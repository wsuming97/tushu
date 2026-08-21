"""
SRT → 逐句配音 → 完整音频
==============================

核心编排脚本：读取 SRT 字幕文件，逐句调用 TTS 引擎生成配音片段，
按 SRT 时间轴将所有片段拼接为一条完整的配音音频。

支持两种运行模式:
  1. audition  —— 试听模式：只用前 N 句，生成多音色试听片段
  2. full      —— 全量模式：逐句合成并按时间轴拼接为完整 voiceover.mp3

用法示例:
  # 试听（多音色对比）
  python srt_to_voice.py --srt 人生由我.srt --engine volcano --mode audition

  # 全量合成
  python srt_to_voice.py --srt 人生由我.srt --engine volcano \
    --voice zh_female_tianmeitaozi_mars_bigtts --speed 0.95
"""

import re
import sys
import time
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────
# 路径设置
# ──────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DIR = _SCRIPT_DIR.parent

# 加载 .env（优先 Skill 目录下的 .env）
try:
    from dotenv import load_dotenv
    load_dotenv(_SKILL_DIR / ".env")
except ImportError:
    pass  # dotenv 未安装时从环境变量读取

import os

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# SRT 解析
# ──────────────────────────────────────────────────────────────

@dataclass
class SrtEntry:
    """SRT 字幕条目"""
    index: int
    start_ms: int       # 起始时间（毫秒）
    end_ms: int         # 结束时间（毫秒）
    text: str           # 字幕文本


def _parse_time(ts: str) -> int:
    """将 SRT 时间戳 '00:01:23,456' 转换为毫秒"""
    # 支持逗号或点号作为毫秒分隔符
    ts = ts.strip().replace(",", ".")
    parts = ts.split(":")
    h, m = int(parts[0]), int(parts[1])
    sec_parts = parts[2].split(".")
    s = int(sec_parts[0])
    ms = int(sec_parts[1]) if len(sec_parts) > 1 else 0
    return ((h * 3600 + m * 60 + s) * 1000) + ms


def parse_srt(srt_path: Path) -> list[SrtEntry]:
    """
    解析 SRT 文件，返回字幕条目列表。

    处理各种编码（UTF-8 / GBK / UTF-8 BOM）和行尾格式。
    """
    # 尝试多种编码
    content = None
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
        try:
            content = srt_path.read_text(encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        raise ValueError(f"无法识别 SRT 文件编码: {srt_path}")

    entries = []
    # 按空行分割为块
    blocks = re.split(r"\n\s*\n", content.strip())

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        # 第 1 行：序号
        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        # 第 2 行：时间轴
        time_match = re.match(
            r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})",
            lines[1].strip()
        )
        if not time_match:
            continue

        start_ms = _parse_time(time_match.group(1))
        end_ms = _parse_time(time_match.group(2))

        # 第 3+ 行：字幕文本
        text = " ".join(line.strip() for line in lines[2:] if line.strip())

        entries.append(SrtEntry(
            index=index,
            start_ms=start_ms,
            end_ms=end_ms,
            text=text,
        ))

    logger.info(f"[SRT] 解析完成: {len(entries)} 条字幕, "
                f"总时长 {entries[-1].end_ms / 1000:.1f}s" if entries else "")
    return entries


# ──────────────────────────────────────────────────────────────
# 音频拼接（按 SRT 时间轴）
# ──────────────────────────────────────────────────────────────

def _concat_by_timeline(
    segments: list[tuple[int, Path]],
    total_duration_ms: int,
    output_path: Path,
) -> Path:
    """
    按 SRT 时间轴将逐句音频片段拼接为完整音频。

    策略：
    - 创建一条 total_duration_ms 长的静音轨道
    - 将每段配音按其 start_ms 叠加到对应位置
    - 如果某段配音时长超过 SRT 时间窗口，不截断（允许略微溢出）

    Args:
        segments:          [(start_ms, audio_file_path), ...]
        total_duration_ms: 总时长（毫秒）
        output_path:       输出文件路径

    Returns:
        输出文件路径
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise RuntimeError("需要安装 pydub: pip install pydub")

    # 创建静音底轨
    # 加 2 秒缓冲，防止最后一句溢出
    canvas = AudioSegment.silent(duration=total_duration_ms + 2000, frame_rate=24000)

    for start_ms, seg_path in segments:
        if not seg_path.exists():
            logger.warning(f"[拼接] 片段文件不存在，跳过: {seg_path}")
            continue
        try:
            seg_audio = AudioSegment.from_file(str(seg_path))
            canvas = canvas.overlay(seg_audio, position=start_ms)
        except Exception as e:
            logger.warning(f"[拼接] 片段加载失败: {seg_path}, {e}")

    # 裁切到实际总时长 + 1 秒尾部留白
    canvas = canvas[:total_duration_ms + 1000]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.export(str(output_path), format="mp3", bitrate="192k")
    logger.info(f"[拼接] 完整配音已保存: {output_path} "
                f"({len(canvas) / 1000:.1f}s)")
    return output_path


# ──────────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────────

def run_audition(
    entries: list[SrtEntry],
    engine: str,
    output_dir: Path,
    audition_count: int = 3,
    speed: float = 1.0,
):
    """
    试听模式：用前 N 句的拼接文本，生成多音色试听片段。
    """
    # 取前 N 句拼接为试听文本
    audition_text = "".join(e.text for e in entries[:audition_count])
    print(f"\n📢 试听文本 ({len(audition_text)} 字):")
    print(f"   {audition_text[:100]}...\n")

    if engine == "volcano":
        from tts_volcano import VolcanoConfig, audition_voices
        config = VolcanoConfig(
            app_id=os.environ.get("VOLCANO_APP_ID", ""),
            api_key=os.environ.get("VOLCANO_API_KEY", ""),
            cluster_id=os.environ.get("VOLCANO_CLUSTER_ID", "volcano_tts"),
            speed_ratio=speed,
        )
        if not config.app_id or not config.api_key:
            print("❌ 错误: 未配置 VOLCANO_APP_ID 或 VOLCANO_API_KEY")
            print("   请在 .env 文件中填入火山引擎凭证")
            sys.exit(1)

        audition_dir = output_dir / "audition"
        results = audition_voices(audition_text, config, audition_dir)
        print(f"\n✅ 试听片段已生成到: {audition_dir}")
        print(f"   共 {len(results)} 个音色，请逐个播放对比后选择")
    else:
        print(f"❌ 暂不支持引擎: {engine}")
        sys.exit(1)


def run_full(
    entries: list[SrtEntry],
    engine: str,
    voice: str,
    speed: float,
    output_dir: Path,
):
    """
    全量模式：逐句合成 → 按时间轴拼接 → 输出完整 voiceover.mp3
    """
    seg_dir = output_dir / "voice_segments"
    seg_dir.mkdir(parents=True, exist_ok=True)

    if engine == "volcano":
        from tts_volcano import VolcanoConfig, synthesize_to_file
        config = VolcanoConfig(
            app_id=os.environ.get("VOLCANO_APP_ID", ""),
            api_key=os.environ.get("VOLCANO_API_KEY", ""),
            cluster_id=os.environ.get("VOLCANO_CLUSTER_ID", "volcano_tts"),
            voice_type=voice,
            speed_ratio=speed,
        )
        if not config.app_id or not config.api_key:
            print("❌ 错误: 未配置 VOLCANO_APP_ID 或 VOLCANO_API_KEY")
            sys.exit(1)
    else:
        print(f"❌ 暂不支持引擎: {engine}")
        sys.exit(1)

    # 逐句合成
    segments: list[tuple[int, Path]] = []
    total = len(entries)

    for i, entry in enumerate(entries, 1):
        seg_file = seg_dir / f"seg_{entry.index:03d}.mp3"

        # 增量支持：如果片段已存在，跳过
        if seg_file.exists() and seg_file.stat().st_size > 100:
            print(f"  [{i}/{total}] 跳过已有: {seg_file.name}")
            segments.append((entry.start_ms, seg_file))
            continue

        print(f"  [{i}/{total}] 合成中: \"{entry.text[:30]}...\"")
        try:
            synthesize_to_file(entry.text, seg_file, config)
            segments.append((entry.start_ms, seg_file))
            # 防止 API 限流，每句间隔 200ms
            time.sleep(0.2)
        except Exception as e:
            print(f"  ❌ 第 {entry.index} 句合成失败: {e}")
            # 失败不中断，继续后续句子
            continue

    if not segments:
        print("❌ 没有成功合成的片段，无法拼接")
        sys.exit(1)

    # 按时间轴拼接
    total_duration_ms = entries[-1].end_ms
    voiceover_path = output_dir / "voiceover.mp3"
    print(f"\n🔗 正在按时间轴拼接 {len(segments)} 个片段...")
    _concat_by_timeline(segments, total_duration_ms, voiceover_path)

    print(f"\n✅ 完整配音已生成: {voiceover_path}")
    print(f"   时长: {total_duration_ms / 1000:.1f}s")
    print(f"   音色: {voice}")
    print(f"   语速: {speed}")
    return voiceover_path


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SRT 字幕 → TTS 配音生成",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--srt", required=True,
        help="SRT 字幕文件路径",
    )
    parser.add_argument(
        "--engine", default="volcano",
        choices=["volcano", "minimax"],
        help="TTS 引擎 (默认: volcano)",
    )
    parser.add_argument(
        "--mode", default="full",
        choices=["audition", "full", "export"],
        help="运行模式:\n"
             "  audition = 多音色试听（前3句）\n"
             "  full     = 全量合成（默认）\n"
             "  export   = 生成剪映导出包（无需 TTS API）",
    )
    parser.add_argument(
        "--voice", default="zh_female_tianmeitaozi_mars_bigtts",
        help="音色 voice_type（全量模式使用）",
    )
    parser.add_argument(
        "--speed", type=float, default=1.0,
        help="语速倍率 (0.5~2.0, 默认 1.0)",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="输出目录（默认: SRT 文件所在目录）",
    )
    parser.add_argument(
        "--video", default=None,
        help="（export 模式）视频文件路径（如 final.mp4）",
    )
    parser.add_argument(
        "--account", default="三花万里朝夕",
        help="账号署名（默认: 三花万里朝夕）",
    )
    parser.add_argument(
        "--project-name", default=None,
        help="项目名称（默认: SRT 文件名）",
    )

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    srt_path = Path(args.srt).resolve()
    if not srt_path.exists():
        print(f"❌ SRT 文件不存在: {srt_path}")
        sys.exit(1)

    # 输出目录：默认与 SRT 同目录
    output_dir = Path(args.output_dir).resolve() if args.output_dir else srt_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解析 SRT
    print(f"📄 解析 SRT: {srt_path.name}")
    entries = parse_srt(srt_path)
    print(f"   {len(entries)} 条字幕, "
          f"总时长 {entries[-1].end_ms / 1000:.1f}s\n")

    if args.mode == "audition":
        run_audition(entries, args.engine, output_dir, speed=args.speed)
    elif args.mode == "export":
        from export_pack import export_pack
        video_path = Path(args.video).resolve() if args.video else None
        project_name = args.project_name or srt_path.stem
        export_pack(srt_path, video_path, output_dir / "export-pack",
                    project_name, args.account)
    else:
        run_full(entries, args.engine, args.voice, args.speed, output_dir)


if __name__ == "__main__":
    main()
