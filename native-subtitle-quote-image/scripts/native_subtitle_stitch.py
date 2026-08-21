#!/usr/bin/env python3
"""把带内嵌字幕的视频精确取帧并拼成原生字幕长图。"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = shutil.which("ffmpeg")
    if not FFMPEG:
        sys.exit("找不到 ffmpeg；请安装 ffmpeg 或 imageio-ffmpeg")


def ffmpeg(args):
    return subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args],
        check=True,
        capture_output=True,
    )


def video_size(path):
    proc = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
    )
    match = re.search(r"(\d{2,5})x(\d{2,5})[,\s]", proc.stderr)
    if not match:
        raise SystemExit(f"无法读取视频尺寸: {path}")
    return int(match.group(1)), int(match.group(2))


def grab_frame(path, seconds):
    """先快速跳转，再精确解码 3 秒，避免长 GOP 视频错帧。"""
    preseek = max(0.0, float(seconds) - 3.0)
    offset = float(seconds) - preseek
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        ffmpeg([
            "-ss", f"{preseek:.3f}", "-i", str(path),
            "-ss", f"{offset:.3f}", "-frames:v", "1", tmp,
        ])
        if not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
            raise SystemExit(f"取帧失败 @ {seconds:.2f}s")
        image = Image.open(tmp).convert("RGB")
        image.load()
        return image
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def parse_aspect(value):
    try:
        width, height = (float(x) for x in value.split(":"))
    except Exception as exc:
        raise argparse.ArgumentTypeError("比例必须写成 3:4 这样的格式") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("比例必须为正数")
    return width, height


def safe_title(value):
    cleaned = re.sub(r"[\\/:*?\"<>|\n\r]+", "_", str(value)).strip(" ._")
    return cleaned or "未命名"


def crop_band(frame, top, bottom):
    y0, y1 = int(frame.height * top), int(frame.height * bottom)
    if y1 <= y0:
        raise SystemExit("--band-bottom 必须大于 --band-top")
    return frame.crop((0, y0, frame.width, y1)), y0, y1


def fit_lower(image, size, vertical=0.72):
    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, vertical),
    )


def render_one(video, times, out_path, aspect, out_width, top, bottom,
               hero_fraction):
    if len(times) < 2:
        raise SystemExit("每张图至少需要 2 个时间点")
    if any(float(b) <= float(a) for a, b in zip(times, times[1:])):
        raise SystemExit(f"时间点必须严格递增: {times}")

    aw, ah = aspect
    out_height = round(out_width * ah / aw)
    hero_height = round(out_height * hero_fraction)
    remaining = out_height - hero_height
    strip_count = len(times) - 1
    base_strip = remaining // strip_count
    strip_heights = [base_strip] * strip_count
    strip_heights[-1] += remaining - sum(strip_heights)

    first = grab_frame(video, times[0])
    _, _, subtitle_bottom = crop_band(first, top, bottom)
    wanted_hero_source_h = min(
        subtitle_bottom,
        max(1, round(first.width * hero_height / out_width)),
    )
    hero_source = first.crop(
        (0, subtitle_bottom - wanted_hero_source_h, first.width, subtitle_bottom)
    )
    hero = fit_lower(hero_source, (out_width, hero_height), vertical=0.75)

    strips = []
    for seconds, height in zip(times[1:], strip_heights):
        frame = grab_frame(video, seconds)
        band, _, _ = crop_band(frame, top, bottom)
        strips.append(fit_lower(band, (out_width, height), vertical=0.72))

    canvas = Image.new("RGB", (out_width, out_height), "black")
    canvas.paste(hero, (0, 0))
    y = hero_height
    for strip in strips:
        canvas.paste(strip, (0, y))
        y += strip.height
    canvas.save(out_path, quality=93, subsampling=0)
    print(f"完成: {out_path} ({out_width}x{out_height})")


def contact_sheet(paths, out_path, columns=4):
    if not paths:
        return
    columns = min(columns, len(paths))
    thumb_w, thumb_h = 360, 480
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * thumb_h), "#111111")
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        thumb = ImageOps.fit(image, (thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % columns) * thumb_w, (index // columns) * thumb_h))
    sheet.save(out_path, quality=92, subsampling=0)


def command_band(args):
    frame = grab_frame(args.video, args.time)
    _, y0, y1 = crop_band(frame, args.band_top, args.band_bottom)
    draw = ImageDraw.Draw(frame)
    line_width = max(3, frame.height // 300)
    draw.line((0, y0, frame.width, y0), fill="red", width=line_width)
    draw.line((0, y1, frame.width, y1), fill="red", width=line_width)
    frame.save(args.out, quality=93)
    print(f"字幕区域预览: {args.out} (y={y0}-{y1})")


def command_render(args):
    manifest_path = Path(args.manifest).resolve()
    with manifest_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    items = data.get("images")
    if not isinstance(items, list) or not items:
        raise SystemExit("manifest 必须包含非空 images 数组")

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for index, item in enumerate(items, 1):
        title = safe_title(item.get("title", f"图片{index}"))
        times = item.get("times")
        if not isinstance(times, list):
            raise SystemExit(f"第 {index} 项缺少 times 数组")
        out_path = out_dir / f"{index:02d}_{title}.jpg"
        render_one(
            args.video, times, out_path, args.aspect, args.width,
            args.band_top, args.band_bottom, args.hero_fraction,
        )
        outputs.append(out_path)

    shutil.copyfile(manifest_path, out_dir / "原生字幕时间点.json")
    contact_sheet(outputs, out_dir / "final_contact_sheet.jpg")
    print(f"总览图: {out_dir / 'final_contact_sheet.jpg'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    band = sub.add_parser("band", help="预览字幕裁切区域")
    band.add_argument("video")
    band.add_argument("-t", "--time", type=float, required=True)
    band.add_argument("--band-top", type=float, default=0.68)
    band.add_argument("--band-bottom", type=float, default=0.96)
    band.add_argument("--out", default="band-preview.jpg")
    band.set_defaults(func=command_band)

    render = sub.add_parser("render", help="按 manifest 渲染整套拼图")
    render.add_argument("video")
    render.add_argument("--manifest", required=True)
    render.add_argument("--out-dir", required=True)
    render.add_argument("--aspect", type=parse_aspect, default=parse_aspect("3:4"))
    render.add_argument("--width", type=int, default=1440)
    render.add_argument("--band-top", type=float, default=0.68)
    render.add_argument("--band-bottom", type=float, default=0.96)
    render.add_argument("--hero-fraction", type=float, default=0.42)
    render.set_defaults(func=command_render)

    args = parser.parse_args()
    if not 0 <= args.band_top < args.band_bottom <= 1:
        raise SystemExit("字幕区域必须满足 0 <= top < bottom <= 1")
    if getattr(args, "width", 1) <= 0:
        raise SystemExit("--width 必须为正数")
    if hasattr(args, "hero_fraction") and not 0.25 <= args.hero_fraction <= 0.75:
        raise SystemExit("--hero-fraction 必须在 0.25–0.75 之间")
    args.func(args)


if __name__ == "__main__":
    main()
