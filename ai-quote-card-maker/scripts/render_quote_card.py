import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(font_name_or_path: str, size: int, serif: bool = False):
    """
    加载指定字体，支持衬线/宋体或黑体回退
    """
    if serif:
        candidates = [
            font_name_or_path,
            "C:/Windows/Fonts/simsun.ttc",   # 中易宋体
            "C:/Windows/Fonts/STSONG.TTF",   # 华文宋体
            "C:/Windows/Fonts/msyhbd.ttc",
            "simsun.ttc",
        ]
    else:
        candidates = [
            font_name_or_path,
            "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "msyhbd.ttc",
            "msyh.ttc",
        ]
    for font_path in candidates:
        if not font_path:
            continue
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_soft_shadow_text(draw: ImageDraw.ImageDraw, xy, text, font, fill_color="#FFFFFF", shadow_color=(0, 0, 0, 140), anchor="mm"):
    """
    绘制带有柔和微光投影的文字，避免生硬脏描边
    """
    x, y = xy
    # 柔和的微暗下投影
    for ox, oy, alpha in [(0, 2, 90), (0, 4, 50), (0, 1, 120)]:
        draw.text((x + ox, y + oy), text, fill=(0, 0, 0, alpha), font=font, anchor=anchor)
    # 主文字
    draw.text((x, y), text, fill=fill_color, font=font, anchor=anchor)

def render_styled_card(
    bg_image_path: str,
    title: str,
    content: str,
    output_path: str,
    style: str = "glass", # glass, cinematic, capsule
    author_or_tag: str = "",
    target_width: int = 1080,
    target_height: int = 1920
):
    if not os.path.exists(bg_image_path):
        raise FileNotFoundError(f"背景图片不存在: {bg_image_path}")
        
    bg = Image.open(bg_image_path).convert("RGBA")
    bg_w, bg_h = bg.size
    
    # 缩放并居中裁切背景
    scale = max(target_width / bg_w, target_height / bg_h)
    new_w = int(bg_w * scale)
    new_h = int(bg_h * scale)
    bg_resized = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - target_width) // 2
    top = (new_h - target_height) // 2
    canvas = bg_resized.crop((left, top, left + target_width, top + target_height))
    
    lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

    # -------------------------------------------------------------
    # 风格 1：毛玻璃卡片风格 (Glassmorphism) — 智能自适应高度
    # -------------------------------------------------------------
    if style == "glass":
        # 整体画面轻微柔化暗角
        overlay = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(target_height):
            alpha = int(45 + (y / target_height) * 45)
            draw_ov.line([(0, y), (target_width, y)], fill=(0, 0, 0, alpha))
        canvas = Image.alpha_composite(canvas, overlay)
        
        # 字体尺寸
        font_title = get_font("", int(target_width * 0.050))
        font_body = get_font("", int(target_width * 0.033))
        
        line_spacing = int(font_body.size * 1.75)
        text_total_height = int(font_title.size * 2.2) + len(lines) * line_spacing + 80
        
        # 动态计算卡片尺寸与垂直居中偏上位置
        card_w = int(target_width * 0.90)
        card_h = max(int(target_height * 0.58), text_total_height + 100)
        card_x1 = (target_width - card_w) // 2
        card_y1 = max(int(target_height * 0.10), (target_height - card_h) // 2 - int(target_height * 0.03))
        card_x2 = card_x1 + card_w
        card_y2 = card_y1 + card_h
        
        # 裁剪出卡片对应的背景进行高斯模糊
        cropped_bg = canvas.crop((card_x1, card_y1, card_x2, card_y2))
        blurred_bg = cropped_bg.filter(ImageFilter.GaussianBlur(radius=30))
        
        # 叠加半透明磨砂白
        card_overlay = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 42))
        card_composed = Image.alpha_composite(blurred_bg, card_overlay)
        
        # 绘制卡片圆角蒙版
        mask = Image.new("L", (card_w, card_h), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([0, 0, card_w, card_h], radius=32, fill=255)
        
        # 将毛玻璃卡片贴回画布
        canvas.paste(card_composed.convert("RGB"), (card_x1, card_y1), mask)
        
        # 绘制卡片微光细边框
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=32, outline=(255, 255, 255, 150), width=2)
        
        # 绘制卡片内标题
        title_y = card_y1 + int(card_h * 0.12)
        draw.text((target_width // 2, title_y), title, fill="#FFFFFF", font=font_title, anchor="mm")
        
        # 标题下方装饰细线
        line_w = int(card_w * 0.22)
        draw.line([(target_width // 2 - line_w // 2, title_y + 32), (target_width // 2 + line_w // 2, title_y + 32)], fill=(255, 255, 255, 120), width=2)
        
        # 绘制正文
        body_y = title_y + int(card_h * 0.14)
        for line in lines:
            draw.text((target_width // 2, body_y), line, fill="#F2F2F2", font=font_body, anchor="mm")
            body_y += line_spacing

    # -------------------------------------------------------------
    # 风格 2：电影画报极简风 (Cinematic) — 沉浸感与优雅宋体
    # -------------------------------------------------------------
    elif style == "cinematic":
        # 叠加电影级深邃调光
        overlay = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(target_height):
            if y < target_height * 0.65:
                alpha = int(120 - (y / (target_height * 0.65)) * 40)
            else:
                alpha = int(80 * (1 - (y - target_height * 0.65) / (target_height * 0.35)))
            draw_ov.line([(0, y), (target_width, y)], fill=(8, 12, 20, alpha))
        canvas = Image.alpha_composite(canvas, overlay)
        
        draw = ImageDraw.Draw(canvas)
        font_title = get_font("", int(target_width * 0.052), serif=True)
        font_body = get_font("", int(target_width * 0.034), serif=True)
        
        # 顶部电影标题
        start_y = int(target_height * 0.15)
        draw_soft_shadow_text(draw, (target_width // 2, start_y), f"「 {title} 」", font_title, fill_color="#FFFDF5")
        
        # 正文
        current_y = start_y + int(target_height * 0.08)
        line_spacing = int(font_body.size * 1.85)
        for line in lines:
            draw_soft_shadow_text(draw, (target_width // 2, current_y), line, font_body, fill_color="#EDE9DF")
            current_y += line_spacing

    # 保存
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    canvas.convert("RGB").save(output_path, quality=96)
    print(f"[OK] 生成完成: {output_path} (Style: {style})")

def auto_output_path(title: str, style: str, skill_root: str = "") -> str:
    """
    自动生成按日期归档的输出路径（存放在 Skill 自身目录下）：
      <SKILL_DIR>/output/YYYY-MM-DD/标题_风格.jpg
    """
    import re
    from datetime import datetime
    
    if not skill_root:
        # 脚本位于 <SKILL_DIR>/scripts/ 下，Skill 根目录为往上 1 级
        skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = re.sub(r'[\\/:*?"<>|\n\r]+', '_', title).strip(' ._') or "quote_card"
    filename = f"{safe_title}_{style}.jpg"
    
    out_dir = os.path.join(skill_root, "output", date_str)
    os.makedirs(out_dir, exist_ok=True)
    
    out_path = os.path.join(out_dir, filename)
    
    # 同名文件自动追加序号避免覆盖
    if os.path.exists(out_path):
        base, ext = os.path.splitext(out_path)
        idx = 2
        while os.path.exists(f"{base}_{idx}{ext}"):
            idx += 1
        out_path = f"{base}_{idx}{ext}"
    
    return out_path


def main():
    parser = argparse.ArgumentParser(description="高级意境金句卡片生成器")
    parser.add_argument("--bg", required=True, help="背景图路径")
    parser.add_argument("--title", default="", help="标题")
    parser.add_argument("--content", required=True, help="正文内容")
    parser.add_argument("--out", default="", help="输出路径（留空则自动归档到 output/quote-cards/YYYY-MM-DD/）")
    parser.add_argument("--style", default="glass", choices=["glass", "cinematic", "capsule"], help="排版设计风格")
    args = parser.parse_args()
    
    # 若用户未指定输出路径，自动按日期归档
    output_path = args.out if args.out else auto_output_path(args.title, args.style)
    
    render_styled_card(
        bg_image_path=args.bg,
        title=args.title,
        content=args.content,
        output_path=output_path,
        style=args.style
    )

if __name__ == "__main__":
    main()
