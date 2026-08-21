import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main(image_path: str, annotation_path: str, output_path: str) -> None:
    image = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font_file = "C:/Windows/Fonts/msyh.ttc"
    font = ImageFont.truetype(font_file, 28)
    small_font = ImageFont.truetype(font_file, 18)
    colors = [(38, 103, 255, 225), (255, 105, 92, 225), (41, 167, 102, 225), (181, 100, 255, 225)]

    data = json.loads(Path(annotation_path).read_text(encoding="utf-8"))
    for index, element in enumerate(data["elements"], start=1):
        region = element["region"]
        x, y = region["x"], region["y"]
        right, bottom = x + region["width"], y + region["height"]
        color = colors[(index - 1) % len(colors)]
        fill = (*color[:3], 24)
        draw.rounded_rectangle((x, y, right, bottom), radius=12, outline=color, width=4, fill=fill)
        draw.ellipse((x + 8, y + 8, x + 44, y + 44), fill=color)
        draw.text((x + 19, y + 8), str(index), anchor="ma", font=small_font, fill="white")
        label = f"{index}. {element['label']}  {element['reveal']['direction']}"
        label_x0 = x + 52
        label_x1 = max(label_x0 + 10, min(right - 8, label_x0 + len(label) * 19))
        if label_x1 > label_x0 + 20:
            draw.rounded_rectangle((label_x0, y + 8, label_x1, y + 46), radius=6, fill=(255, 255, 255, 225))
            draw.text((label_x0 + 8, y + 12), label, font=small_font, fill=color)
        else:
            # 区域太窄时直接在区域外侧或上方绘制
            draw.rounded_rectangle((x, max(0, y - 36), x + len(label) * 18, max(36, y)), radius=6, fill=(255, 255, 255, 225))
            draw.text((x + 6, max(4, y - 32)), label, font=small_font, fill=color)
        # 绘制方向/手势指示线
        hand_path = element.get("handPath")
        if hand_path and "start" in hand_path and "end" in hand_path:
            start = tuple(hand_path["start"])
            end = tuple(hand_path["end"])
        else:
            # 默认从中心指向右/下
            direction = element.get("reveal", {}).get("direction", "left_to_right")
            cx, cy = x + region["width"] // 2, y + region["height"] // 2
            if direction == "top_to_bottom":
                start, end = (cx, y + 20), (cx, y + region["height"] - 20)
            elif direction == "left_to_right":
                start, end = (x + 20, cy), (x + region["width"] - 20, cy)
            else:
                start, end = (x + 20, cy), (x + region["width"] - 20, cy)
                
        draw.line((start, end), fill=color, width=4)
        draw.polygon((end, (end[0] - 10, end[1] - 6), (end[0] - 10, end[1] + 6)), fill=color)

    result = Image.alpha_composite(image, overlay).convert("RGB")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path, quality=95)


if __name__ == "__main__":
    main(*sys.argv[1:4])
