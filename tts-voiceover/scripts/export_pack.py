"""
剪映导出包生成器
========================================

从 SRT 字幕 + 白板动画视频，生成一个「开箱即用」的剪映编辑素材包。
用户拿到这个文件夹后，打开剪映直接就能开工——
不需要 TTS API，不需要写代码，不需要额外配置。

导出包内容:
  export-pack/
  ├── final.mp4              视频成片（无声/原始音轨）
  ├── narration.txt          配音稿（按自然呼吸断句，标注停顿位置）
  ├── subtitles.srt          SRT 字幕（可直接拖入剪映字幕轨）
  ├── publish-copy.txt       发布文案（标题 + 正文 + 话题标签）
  ├── first-comment.txt      作者首评文案
  └── README.txt             操作指南

用法:
  python export_pack.py \
    --srt 人生由我.srt \
    --video final.mp4 \
    --project-name "人生由我-梅耶马斯克" \
    --account "三花万里朝夕" \
    --output-dir export-pack/
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# 复用 srt_to_voice 的 SRT 解析器
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from srt_to_voice import parse_srt, SrtEntry


# ──────────────────────────────────────────────────────────────
# 配音稿生成
# ──────────────────────────────────────────────────────────────

def _estimate_pause(gap_ms: int) -> str:
    """根据相邻字幕间隔推算自然停顿标注"""
    if gap_ms <= 0:
        return ""
    elif gap_ms < 500:
        return ""  # 极短间隔，不需要特别标注
    elif gap_ms < 1500:
        return "（停顿0.5秒）"
    elif gap_ms < 3000:
        return "（停顿1秒）"
    elif gap_ms < 5000:
        return "（停顿2秒）"
    else:
        return f"（停顿{gap_ms / 1000:.0f}秒）"


def _split_long_sentence(text: str, max_chars: int = 25) -> list[str]:
    """
    将长句按中文标点或语义边界拆分为多行，便于朗读换气。

    拆分点优先级：
    1. 句号、问号、叹号、分号
    2. 逗号、顿号
    3. 破折号、省略号
    """
    if len(text) <= max_chars:
        return [text]

    # 按标点拆分，保留标点
    # 先按强断句拆
    parts = re.split(r"(。|！|？|；)", text)
    lines = []
    current = ""

    for part in parts:
        if not part:
            continue
        current += part
        # 如果是句末标点，输出当前行
        if part in "。！？；":
            lines.append(current.strip())
            current = ""
        # 如果当前行已经够长，按逗号再拆
        elif len(current) > max_chars:
            sub_parts = re.split(r"(，|、|——|……)", current)
            sub_line = ""
            for sp in sub_parts:
                if not sp:
                    continue
                sub_line += sp
                if sp in ("，", "、", "——", "……") and len(sub_line) > 10:
                    lines.append(sub_line.strip())
                    sub_line = ""
            if sub_line.strip():
                current = sub_line
            else:
                current = ""

    if current.strip():
        lines.append(current.strip())

    return lines if lines else [text]


def generate_narration(
    entries: list[SrtEntry],
    project_name: str = "",
    account_name: str = "三花万里朝夕",
) -> str:
    """
    从 SRT 条目生成带停顿标记的配音稿。

    配音稿特点：
    - 按自然呼吸和语义边界断行
    - 标注停顿位置和时长
    - 头部标注总字数、建议语速和预计时长
    """
    # 统计总字数
    total_chars = sum(len(e.text) for e in entries)
    total_duration_s = entries[-1].end_ms / 1000 if entries else 0
    minutes = int(total_duration_s // 60)
    seconds = int(total_duration_s % 60)
    # 实际语速
    actual_speed = total_chars / (total_duration_s / 60) if total_duration_s > 0 else 200

    lines = []
    lines.append(f"【配音稿 · {project_name}】")
    lines.append(f"账号：{account_name}")
    lines.append(f"总字数：{total_chars}字 | 建议语速：每分钟{int(actual_speed)}字 | 预计时长：{minutes}分{seconds:02d}秒")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("=" * 50)
    lines.append("")

    for i, entry in enumerate(entries):
        # 拆分长句为多行
        sub_lines = _split_long_sentence(entry.text)
        for sl in sub_lines:
            lines.append(sl)

        # 计算与下一句的间隔，添加停顿标注
        if i < len(entries) - 1:
            gap_ms = entries[i + 1].start_ms - entry.end_ms
            pause = _estimate_pause(gap_ms)
            if pause:
                lines.append(pause)
            lines.append("")  # 空行分隔

    lines.append("")
    lines.append("=" * 50)
    lines.append("【配音提示】")
    lines.append("- 整体语调：温暖、从容、娓娓道来，不要急")
    lines.append("- 问句处稍微上扬语调，制造互动感")
    lines.append("- 转折处（如「然而」「但是」）略微放慢、加重")
    lines.append("- 引用和金句处可以降低音量，制造沉浸感")
    lines.append(f"- 总时长控制在 {minutes}分{seconds:02d}秒 左右")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 发布文案生成
# ──────────────────────────────────────────────────────────────

def generate_publish_copy(
    entries: list[SrtEntry],
    project_name: str = "",
    account_name: str = "三花万里朝夕",
) -> str:
    """
    从字幕内容生成微信视频号/小红书发布文案。

    包含：标题、正文摘要、话题标签。
    """
    # 提取前几句作为钩子
    hook = entries[0].text if entries else ""
    # 提取核心金句（通常在中后段）
    mid_idx = len(entries) // 2
    core_quote = entries[mid_idx].text if len(entries) > mid_idx else ""
    # 提取结尾行动号召
    cta = entries[-1].text if entries else ""

    lines = []
    lines.append(f"【发布文案 · {project_name}】")
    lines.append(f"账号：{account_name}")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("=" * 40)
    lines.append("")
    lines.append("📌 标题（二选一）：")
    lines.append(f"  A. {hook}")
    if len(entries) > 3:
        lines.append(f"  B. {entries[3].text[:30]}...")
    lines.append("")
    lines.append("📝 正文：")
    lines.append(f"{hook}")
    lines.append(f"{core_quote}")
    lines.append("")
    lines.append(f"关注 @{account_name}，愿你原力觉醒。")
    lines.append("")
    lines.append("🏷️ 话题标签：")
    lines.append(f"#{project_name.split('-')[0] if '-' in project_name else project_name} "
                 f"#治愈 #成长 #女性力量 #{account_name} "
                 f"#人生感悟 #正能量 #好书推荐")
    lines.append("")
    lines.append("=" * 40)

    return "\n".join(lines)


def generate_first_comment(
    entries: list[SrtEntry],
    project_name: str = "",
    account_name: str = "三花万里朝夕",
) -> str:
    """生成作者首评文案"""
    # 从字幕中提取一句最有力的金句作为首评
    # 通常在后半段，找带「告诉」「如果」「每一个」等关键词的句子
    best_quote = ""
    for e in entries[len(entries) // 2:]:
        if any(kw in e.text for kw in ("告诉", "如果", "每一个", "千万", "一定")):
            best_quote = e.text
            break
    if not best_quote and entries:
        best_quote = entries[-2].text if len(entries) > 1 else entries[-1].text

    lines = []
    lines.append(f"【作者首评 · {project_name}】")
    lines.append("")
    lines.append(f"「{best_quote}」")
    lines.append("")
    lines.append(f"你在什么年纪做过最勇敢的决定？评论区聊聊👇")
    lines.append("")
    lines.append(f"—— {account_name}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 操作指南
# ──────────────────────────────────────────────────────────────

def generate_readme(project_name: str, account_name: str) -> str:
    """生成剪映操作指南"""
    return f"""【剪映编辑指南 · {project_name}】
账号：{account_name}

=============================================
📂 文件说明
=============================================

1. final.mp4          → 白板手绘动画成片（无声版）
2. narration.txt      → 配音稿（标注了停顿位置，朗读用）
3. subtitles.srt      → SRT 字幕文件（可直接导入剪映）
4. publish-copy.txt   → 发布文案 + 话题标签
5. first-comment.txt  → 作者首评文案

=============================================
🎬 剪映操作步骤
=============================================

【方法一：剪映文本朗读（最快）】
1. 打开剪映，新建项目
2. 导入 final.mp4 到时间线
3. 点击「文本」→「导入字幕」→ 选择 subtitles.srt
4. 选中字幕轨道 → 点击「文本朗读」
5. 选择你喜欢的音色（推荐：治愈女声 / 故事解说）
6. 调整语速到 0.9x ~ 1.0x
7. 添加背景音乐（推荐：轻钢琴 / 大提琴，音量 10%~15%）
8. 导出发布

【方法二：真人录音】
1. 打开剪映，导入 final.mp4
2. 打开 narration.txt，按标注的停顿朗读
3. 用手机/麦克风录音，导入剪映音频轨
4. 微调音频与画面的对齐
5. 添加字幕（导入 subtitles.srt）
6. 添加 BGM → 导出发布

=============================================
📱 发布清单
=============================================
☐ 复制 publish-copy.txt 中的标题和正文
☐ 粘贴话题标签
☐ 发布后立即粘贴 first-comment.txt 作为首评
☐ 置顶首评

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


# ──────────────────────────────────────────────────────────────
# 主流程：打包导出
# ──────────────────────────────────────────────────────────────

def export_pack(
    srt_path: Path,
    video_path: Path | None,
    output_dir: Path,
    project_name: str = "",
    account_name: str = "三花万里朝夕",
) -> Path:
    """
    生成剪映导出包。

    Args:
        srt_path:      SRT 字幕文件路径
        video_path:    视频文件路径（可选，会复制到导出包）
        output_dir:    导出包输出目录
        project_name:  项目名称
        account_name:  账号署名

    Returns:
        导出包目录路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解析 SRT
    entries = parse_srt(srt_path)
    print(f"📄 解析 SRT: {len(entries)} 条字幕, "
          f"总时长 {entries[-1].end_ms // 60000}:{(entries[-1].end_ms % 60000) // 1000:02d}")

    # 1. 复制视频
    if video_path and video_path.exists():
        dst_video = output_dir / "final.mp4"
        if dst_video.resolve() != video_path.resolve():
            shutil.copy2(video_path, dst_video)
            print(f"  ✅ 视频 → {dst_video.name}")
        else:
            print(f"  ✅ 视频已在目标目录")
    else:
        print(f"  ⚠️ 未提供视频文件，跳过视频复制")

    # 2. 复制 SRT 字幕
    dst_srt = output_dir / "subtitles.srt"
    if dst_srt.resolve() != srt_path.resolve():
        shutil.copy2(srt_path, dst_srt)
    print(f"  ✅ 字幕 → {dst_srt.name}")

    # 3. 生成配音稿
    narration = generate_narration(entries, project_name, account_name)
    narration_path = output_dir / "narration.txt"
    narration_path.write_text(narration, encoding="utf-8")
    print(f"  ✅ 配音稿 → {narration_path.name}")

    # 4. 生成发布文案
    publish = generate_publish_copy(entries, project_name, account_name)
    publish_path = output_dir / "publish-copy.txt"
    publish_path.write_text(publish, encoding="utf-8")
    print(f"  ✅ 发布文案 → {publish_path.name}")

    # 5. 生成首评
    comment = generate_first_comment(entries, project_name, account_name)
    comment_path = output_dir / "first-comment.txt"
    comment_path.write_text(comment, encoding="utf-8")
    print(f"  ✅ 首评 → {comment_path.name}")

    # 6. 生成操作指南
    readme = generate_readme(project_name, account_name)
    readme_path = output_dir / "README.txt"
    readme_path.write_text(readme, encoding="utf-8")
    print(f"  ✅ 操作指南 → {readme_path.name}")

    print(f"\n🎉 剪映导出包已就绪: {output_dir}")
    print(f"   共 {len(list(output_dir.iterdir()))} 个文件，可直接打开剪映使用")

    return output_dir


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="生成剪映编辑导出包（视频 + 配音稿 + 字幕 + 发布物料）",
    )
    parser.add_argument(
        "--srt", required=True,
        help="SRT 字幕文件路径",
    )
    parser.add_argument(
        "--video", default=None,
        help="视频文件路径（如 final.mp4）",
    )
    parser.add_argument(
        "--project-name", default="",
        help="项目名称（用于文案标题）",
    )
    parser.add_argument(
        "--account", default="三花万里朝夕",
        help="账号署名（默认: 三花万里朝夕）",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="导出包输出目录（默认: SRT 同目录下 export-pack/）",
    )

    args = parser.parse_args()

    srt_path = Path(args.srt).resolve()
    if not srt_path.exists():
        print(f"❌ SRT 文件不存在: {srt_path}")
        sys.exit(1)

    video_path = Path(args.video).resolve() if args.video else None
    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else srt_path.parent / "export-pack"
    )
    project_name = args.project_name or srt_path.stem

    export_pack(srt_path, video_path, output_dir, project_name, args.account)


if __name__ == "__main__":
    main()
