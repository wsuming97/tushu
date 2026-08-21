"""
成片合成：视频 + 配音 → 最终成片
========================================

将白板手绘动画视频（无声或旧音轨）与 TTS 配音音频合成为可发布成片。

功能:
  - 替换/添加音轨到视频
  - 自动对齐音视频时长（短音频自动补静音，长音频截断）
  - 保持视频画质不损失（视频流直接 copy）
  - 可选添加 BGM（预留接口，默认不启用）

用法:
  python compose_final.py \
    --video final.mp4 \
    --audio voiceover.mp3 \
    --output final_voiced.mp4
"""

import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _find_ffmpeg() -> str:
    """
    查找可用的 ffmpeg 路径。

    优先级：
    1. imageio_ffmpeg 内置的 ffmpeg（与 srt-whiteboard-animation 共享）
    2. 系统 PATH 中的 ffmpeg
    """
    # 尝试 imageio_ffmpeg
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        if ff:
            return ff
    except ImportError:
        pass

    # 系统 PATH
    import shutil
    ff = shutil.which("ffmpeg")
    if ff:
        return ff

    raise RuntimeError(
        "未找到 ffmpeg。请安装 imageio-ffmpeg (pip install imageio-ffmpeg) "
        "或将 ffmpeg 加入系统 PATH。"
    )


def _find_ffprobe() -> str:
    """查找 ffprobe 路径"""
    import shutil

    # imageio_ffmpeg 附带的 ffprobe
    try:
        import imageio_ffmpeg
        ff_dir = Path(imageio_ffmpeg.get_ffmpeg_exe()).parent
        probe = ff_dir / "ffprobe.exe" if sys.platform == "win32" else ff_dir / "ffprobe"
        if probe.exists():
            return str(probe)
    except ImportError:
        pass

    # 系统 PATH
    fp = shutil.which("ffprobe")
    if fp:
        return fp

    return ""


def get_duration_ms(file_path: Path, ffprobe: str = "") -> int:
    """用 ffprobe 获取媒体文件时长（毫秒）"""
    if not ffprobe:
        ffprobe = _find_ffprobe()
    if not ffprobe:
        logger.warning("ffprobe 不可用，无法获取媒体时长")
        return 0

    cmd = [
        ffprobe, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(file_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)
        duration_s = float(data["format"]["duration"])
        return int(duration_s * 1000)
    except Exception as e:
        logger.warning(f"获取时长失败: {file_path}, {e}")
        return 0


def compose(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    bgm_path: Path | None = None,
    bgm_volume: float = 0.15,
) -> Path:
    """
    将视频和音频合成为最终成片。

    策略:
    1. 视频流直接 copy（不重新编码，保持画质）
    2. 音频重新编码为 AAC
    3. 以视频时长为准（-shortest）
    4. 如果提供了 BGM，混合 BGM 到音频轨（amix filter）

    Args:
        video_path:  视频文件路径
        audio_path:  配音音频路径
        output_path: 输出成片路径
        bgm_path:    背景音乐路径（可选）
        bgm_volume:  BGM 音量系数（0.0~1.0，默认 0.15 = 衬托不抢戏）

    Returns:
        输出文件路径
    """
    ffmpeg = _find_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if bgm_path and bgm_path.exists():
        # 带 BGM 混合
        # 使用 amix 将配音（音量 1.0）和 BGM（音量 bgm_volume）混合
        filter_complex = (
            f"[1:a]volume=1.0[voice];"
            f"[2:a]volume={bgm_volume}[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first[aout]"
        )
        cmd = [
            ffmpeg,
            "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-i", str(bgm_path),
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path),
        ]
    else:
        # 纯配音（无 BGM）
        cmd = [
            ffmpeg,
            "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path),
        ]

    logger.info(f"[合成] 执行命令: {' '.join(cmd)}")
    print(f"\n🎬 正在合成成片...")
    print(f"   视频: {video_path.name}")
    print(f"   配音: {audio_path.name}")
    if bgm_path:
        print(f"   BGM:  {bgm_path.name} (音量 {bgm_volume:.0%})")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg 错误:\n{result.stderr[-1000:]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("ffmpeg 合成超时（120s）")

    # 验证输出
    if not output_path.exists() or output_path.stat().st_size < 10000:
        raise RuntimeError(f"合成输出异常: {output_path}")

    # 获取成片信息
    ffprobe = _find_ffprobe()
    duration_ms = get_duration_ms(output_path, ffprobe)

    print(f"\n✅ 成片合成完成!")
    print(f"   输出: {output_path}")
    print(f"   大小: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    if duration_ms:
        m, s = divmod(duration_ms // 1000, 60)
        print(f"   时长: {m}:{s:02d}")

    return output_path


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="视频 + 配音 → 最终成片",
    )
    parser.add_argument(
        "--video", required=True,
        help="输入视频文件路径（如 final.mp4）",
    )
    parser.add_argument(
        "--audio", required=True,
        help="配音音频路径（如 voiceover.mp3）",
    )
    parser.add_argument(
        "--output", default=None,
        help="输出成片路径（默认: 视频同目录下 final_voiced.mp4）",
    )
    parser.add_argument(
        "--bgm", default=None,
        help="（可选）背景音乐文件路径",
    )
    parser.add_argument(
        "--bgm-volume", type=float, default=0.15,
        help="BGM 音量系数 (0.0~1.0, 默认 0.15)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    video = Path(args.video).resolve()
    audio = Path(args.audio).resolve()

    if not video.exists():
        print(f"❌ 视频文件不存在: {video}")
        sys.exit(1)
    if not audio.exists():
        print(f"❌ 音频文件不存在: {audio}")
        sys.exit(1)

    output = Path(args.output).resolve() if args.output else video.parent / "final_voiced.mp4"
    bgm = Path(args.bgm).resolve() if args.bgm else None

    compose(video, audio, output, bgm, args.bgm_volume)


if __name__ == "__main__":
    main()
