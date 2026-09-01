import os
import re
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(font_name_or_path: str, size: int, serif: bool = True):
    """
    加载指定字体，默认优先宋体/衬线体
    """
    if serif:
        candidates = [
            font_name_or_path,
            "C:/Windows/Fonts/simsun.ttc",   # 中易宋体
            "C:/Windows/Fonts/STSONG.TTF",   # 华文宋体
            "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
            "simsun.ttc",
        ]
    else:
        candidates = [
            font_name_or_path,
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "msyhbd.ttc",
        ]
    for font_path in candidates:
        if not font_path:
            continue
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_rich_text_line(draw: ImageDraw.ImageDraw, start_xy, segments, default_font, default_color="#2B2B2B", highlight_color="#A82828"):
    """
    绘制单行富文本，支持 **高亮文字** 自动使用强调色
    """
    cur_x, cur_y = start_xy
    for text, is_hl in segments:
        color = highlight_color if is_hl else default_color
        # 绘制极轻微投影增强边缘清晰度
        draw.text((cur_x, cur_y + 1), text, fill=(0, 0, 0, 20), font=default_font)
        draw.text((cur_x, cur_y), text, fill=color, font=default_font)
        bbox = draw.textbbox((cur_x, cur_y), text, font=default_font)
        cur_x += (bbox[2] - bbox[0])
    return cur_x

def parse_highlight_line(line: str):
    """
    解析类似 "她**满脸泪痕**，听着男方..." 为分段标记
    """
    parts = []
    tokens = re.split(r'(\*\*.*?\*\*)', line)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            parts.append((token[2:-2], True))
        else:
            parts.append((token, False))
    return parts

def render_single_story_card(
    bg_image_path: str,
    title: str,
    story_body: str,
    output_path: str = "",
    target_width: int = 1080,
    target_height: int = 1920
):
    """
    渲染单张独立故事贴图（单张磨砂白底卡片 + 宋体大标题 + 关键词高亮）
    """
    if not os.path.exists(bg_image_path):
        raise FileNotFoundError(f"背景图不存在: {bg_image_path}")

    bg = Image.open(bg_image_path).convert("RGBA")
    bg_w, bg_h = bg.size

    scale = max(target_width / bg_w, target_height / bg_h)
    new_w = int(bg_w * scale)
    new_h = int(bg_h * scale)
    bg_resized = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = (new_w - target_width) // 2
    top = (new_h - target_height) // 2
    canvas = bg_resized.crop((left, top, left + target_width, top + target_height))

    # 整体叠加轻微柔光
    overlay = Image.new("RGBA", (target_width, target_height), (255, 255, 255, 20))
    canvas = Image.alpha_composite(canvas, overlay)

    # 字体准备
    font_main_title = get_font("", int(target_width * 0.065), serif=True)
    font_body = get_font("", int(target_width * 0.032), serif=True)

    # 解析故事内容
    story_lines = [l.strip() for l in story_body.strip().split("\n") if l.strip()]
    line_spacing = int(font_body.size * 1.85)

    # 卡片边距与自适应高度
    card_margin_x = int(target_width * 0.07)
    card_w = target_width - card_margin_x * 2

    # 动态计算内容高度，确保留白舒服
    content_height = int(font_main_title.size * 1.5) + len(story_lines) * line_spacing + 160
    card_h = max(int(target_height * 0.56), content_height)
    card_y1 = int(target_height * 0.12) # 偏上方布局，底部留出景深
    card_y2 = card_y1 + card_h

    # 毛玻璃裁切与高斯模糊
    crop = canvas.crop((card_margin_x, card_y1, card_margin_x + card_w, card_y2))
    blur = crop.filter(ImageFilter.GaussianBlur(radius=26))
    tint = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 205)) # 白底高通透质感
    card_composed = Image.alpha_composite(blur, tint)

    # 圆角贴合
    mask = Image.new("L", (card_w, card_h), 0)
    d_m = ImageDraw.Draw(mask)
    d_m.rounded_rectangle([0, 0, card_w, card_h], radius=24, fill=255)
    canvas.paste(card_composed.convert("RGB"), (card_margin_x, card_y1), mask)

    draw = ImageDraw.Draw(canvas)
    # 微光白边
    draw.rounded_rectangle([card_margin_x, card_y1, card_margin_x + card_w, card_y2], radius=24, outline=(255, 255, 255, 230), width=2)

    # 绘制标题
    title_start_x = card_margin_x + int(card_w * 0.08)
    title_start_y = card_y1 + int(card_h * 0.10)
    draw.text((title_start_x, title_start_y), title, fill="#1F1F1F", font=font_main_title)

    # 标题下方精致分割线与圆点
    line_y = title_start_y + int(font_main_title.size * 1.35)
    line_end_x = card_margin_x + card_w - int(card_w * 0.08)
    draw.line([(title_start_x, line_y), (line_end_x, line_y)], fill=(180, 180, 180, 150), width=1)
    draw.ellipse([title_start_x + 75, line_y - 3, title_start_x + 81, line_y + 3], fill=(150, 150, 150, 200))

    # 绘制故事段落
    cur_body_y = line_y + int(card_h * 0.07)
    for line in story_lines:
        parsed_segs = parse_highlight_line(line)
        draw_rich_text_line(draw, (title_start_x, cur_body_y), parsed_segs, font_body, default_color="#333333", highlight_color="#A82828")
        cur_body_y += line_spacing

    # 保存
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    canvas.convert("RGB").save(output_path, quality=96)
    print(f"[OK] 单故事贴图生成成功: {output_path}")

def auto_output_path(title: str, style: str = "story", skill_root: str = "") -> str:
    """自动归档到 <SKILL_DIR>/output/YYYY-MM-DD/标题_风格.jpg"""
    if not skill_root:
        # 脚本位于 <SKILL_DIR>/scripts/ 下，Skill 根目录为往上 1 级
        skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = re.sub(r'[\\/:*?"<>|\n\r]+', '_', title).strip(' ._') or "story_card"
    filename = f"{safe_title}_{style}.jpg"
    out_dir = os.path.join(skill_root, "output", date_str)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    if os.path.exists(out_path):
        base, ext = os.path.splitext(out_path)
        idx = 2
        while os.path.exists(f"{base}_{idx}{ext}"):
            idx += 1
        out_path = f"{base}_{idx}{ext}"
    return out_path

def main():
    parser = argparse.ArgumentParser(description="单故事公众号贴图生成器")
    parser.add_argument("--bg", required=True, help="背景图路径")
    parser.add_argument("--title", default="", help="故事大标题")
    parser.add_argument("--story", required=True, help="故事正文（支持**高亮词**）")
    parser.add_argument("--out", default="", help="输出路径")
    args = parser.parse_args()

    out_path = args.out if args.out else auto_output_path(args.title, "single_story")
    render_single_story_card(
        bg_image_path=args.bg,
        title=args.title,
        story_body=args.story,
        output_path=out_path
    )

if __name__ == "__main__":
    main()
