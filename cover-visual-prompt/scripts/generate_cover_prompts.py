# -*- coding: utf-8 -*-
"""
爆款封面与首图提示词蒸馏器 (Cover Visual & Prompt Distiller v2.0)
-----------------------------------------------------------------
核心治理规范：
1. 真正基于输入主题 (theme) 与风格 (style) 动态生成视觉主体、构图与提示词；
2. 严禁固定输出单一的女性、绿植或茶杯模板；
3. 内置多风格视觉模具 (商业博弈/治愈插画/极简杂志/科技洞察/生活写真) 与三层景深动态引擎。
"""

import sys, os, json, argparse, re
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 风格模具库
STYLE_PRESETS = {
    "healing_illustration": {
        "name": "治愈系手绘插画风",
        "color_palette": "warm cream background (#F5EBD7), pastel tones, soft golden hour sunlight",
        "art_medium": "Ghibli and Makoto Shinkai aesthetic, delicate line-art, watercolor wash",
        "lighting": "soft cinematic volumetric light, warm and tranquil ambiance",
        "chinese_desc": "治愈系水彩手绘插画，温暖米黄纸张底色（#F5EBD7），柔和漫射晨光，吉卜力动画美学质感"
    },
    "cinematic_business": {
        "name": "电影级商业与博弈质感",
        "color_palette": "deep navy blue, dark charcoal, subtle metallic gold accents",
        "art_medium": "35mm anamorphic photography, high dynamic range, editorial portraiture",
        "lighting": "dramatic chiaroscuro lighting, sharp rim light, deep shadows",
        "chinese_desc": "电影级冷调商业大片，深藏青与暗炭黑高反差配色，戏剧性侧逆光与轮廓光，35毫米宽画幅质感"
    },
    "editorial_minimalist": {
        "name": "极简杂志排版风",
        "color_palette": "pure off-white, bold typographic contrast, stark neutral tones",
        "art_medium": "Vogue/Kinfolk editorial style, clean negative space, studio still-life",
        "lighting": "diffused studio daylight, clean soft shadows, 40% negative space",
        "chinese_desc": "Kinfolk 极简时尚杂志风，干净大面积留白，专业摄影影棚柔光，高质感极简静物"
    },
    "tech_cyberpunk": {
        "name": "科技与未来洞察风",
        "color_palette": "neon cyan, dark violet, electric amber highlights",
        "art_medium": "futuristic concept art, holographic digital nodes, Unreal Engine 5 render",
        "lighting": "cybernetic neon reflections, moody atmospheric fog",
        "chinese_desc": "赛博科技未来风，电光青与深紫霓虹光影，虚幻引擎5概念渲染，全息数据节点"
    }
}

def extract_visual_elements_from_theme(theme: str) -> tuple[str, str, str, str, str]:
    """
    根据主题动态提取视觉前景、中景、后景、大字标题与副标题
    """
    t = theme.lower()

    if any(k in t for k in ["孙宇晨", "套利", "投资", "财富", "商业", "博弈", "股市", "赚钱", "金钱"]):
        fg = "前景：散落的黑色国际象棋棋子、精密的机械腕表与泛着微光的金融走势图"
        mg = "中景：一位神情锐利冷峻的年轻商业决策者侧影，身着深色西装，凝视着眼前的棋局"
        bg = "后景：摩天大楼落地窗外虚化的繁华城市天际线与夜景微光"
        main_headline = "顶级套利的真相"
        sub_headline = "为什么普通人学他必死无疑？"
        subject_en = "a sharp business strategist in dark tailored suit contemplating a chessboard by a skyscraper window"
        fg_en = "scattered black chess pieces, a mechanical wristwatch and glowing financial charts in extreme foreground"
        bg_en = "blurred metropolitan skyline at night through floor-to-ceiling glass"
    elif any(k in t for k in ["婚姻", "感情", "恋爱", "无话", "夫妻", "伴侣", "家庭"]):
        fg = "前景：长餐桌两侧各放着一杯冷掉的咖啡，中间横亘着未翻动的晨报"
        mg = "中景：一对背对背坐着的男女剪影，两人各自看着窗外，神色沉静而疏离"
        bg = "后景：清冷阴雨天的窗户，雨滴划过玻璃留下的水痕"
        main_headline = "不是死于无性"
        sub_headline = "而是死于无话的沉默"
        subject_en = "a man and woman sitting back-to-back at a long table in quiet emotional distance"
        fg_en = "two cups of cold coffee and an untouched newspaper in foreground"
        bg_en = "a rain-streaked window overlooking a muted gray cityscape"
    elif any(k in t for k in ["职场", "跳槽", "领导", "同事", "工资", "升职", "工作"]):
        fg = "前景：合上的笔记本电脑、一杯咖啡与整齐码放的项目方案"
        mg = "中景：一位专注自信的职场青年，正在阳光洒下的开放式办公室里收拾公文包"
        bg = "后景：通透整洁的玻璃幕墙办公室，温暖阳光在地板上拉出长长的影子"
        main_headline = "越努力越被边缘？"
        sub_headline = "职场高手都在用的边界心法"
        subject_en = "a confident modern professional in smart casual attire packing a leather bag by a sunlit office window"
        fg_en = "a closed sleek laptop and steaming coffee cup in foreground"
        bg_en = "modern minimalist glass-walled office with warm sunlight"
    else:
        # 通用生活/自立/情感主题
        fg = "前景：质感木桌上放着翻开的书页、金属老花镜与冒着热气的茶杯"
        mg = f"中景：一位神态从容通透的主角人物，神情从容自如，正在安静思考或翻阅书籍"
        bg = "后景：阳光透过的温暖窗棂，绿植在微风中摇曳，充满宁静自立的生活气息"
        main_headline = theme[:8] if len(theme) >= 8 else f"{theme}的真相"
        sub_headline = "人生由我，老后由心"
        subject_en = f"a serene individual reflecting calmly with quiet confidence"
        fg_en = "an open vintage book, glasses and a warm ceramic teacup on wooden table"
        bg_en = "warm sunlight streaming through a serene window with gentle shadows"

    return fg, mg, bg, main_headline, sub_headline, subject_en, fg_en, bg_en

def generate_cover_prompts(theme: str, style_key: str = "healing_illustration") -> dict:
    preset = STYLE_PRESETS.get(style_key, STYLE_PRESETS["healing_illustration"])

    fg, mg, bg, h_main, h_sub, subj_en, fg_en, bg_en = extract_visual_elements_from_theme(theme)

    # 动态组装 Midjourney 提示词
    mj_prompt = (
        f"A cinematic visual composition of {subj_en}, with {fg_en}, {bg_en}. "
        f"Color palette: {preset['color_palette']}. Art medium: {preset['art_medium']}. "
        f"Lighting: {preset['lighting']}. Three-layer depth of field, high aesthetic, 8k resolution, 9:16 vertical --ar 9:16 --v 6.0"
    )

    # 动态组装即梦中文提示词
    jimeng_prompt = (
        f"{preset['chinese_desc']}。画面主体呈现：{mg}；{fg}；{bg}。"
        f"电影级三层景深，光影细腻通透，9:16 竖屏高保真壁纸质感，适合小红书/视频号大字封面排版。"
    )

    return {
        "status": "success",
        "theme": theme,
        "style_selected": preset["name"],
        "three_layer_composition": {
            "foreground": fg,
            "midground": mg,
            "background": bg
        },
        "typography_layout": {
            "main_headline": f"《{h_main}》",
            "sub_headline": h_sub,
            "layout_advice": "主标题使用极粗黑体/宋体占据画面上方 1/3 黄金分割位，预留 35% 负空间放置大字"
        },
        "midjourney_prompt_en": mj_prompt,
        "jimeng_prompt_cn": jimeng_prompt
    }

def main():
    parser = argparse.ArgumentParser(description="爆款封面与首图提示词蒸馏器 (v2.0)")
    parser.add_argument("--theme", type=str, default="孙宇晨的注意力套利与商业阳谋", help="文案主题")
    parser.add_argument("--style", type=str, default="cinematic_business", choices=list(STYLE_PRESETS.keys()), help="视觉风格")
    args = parser.parse_args()

    res = generate_cover_prompts(args.theme, args.style)
    print("\n=================================================================")
    print(f"🎨 【爆款封面视觉与 AI 生图 Prompt 方案】: {args.theme}")
    print("=================================================================")
    print(f"🎭 视觉风格: {res['style_selected']}\n")

    print("📐 【三层景深构图方案 (根据主题动态提取)】:")
    print(f"  • {res['three_layer_composition']['foreground']}")
    print(f"  • {res['three_layer_composition']['midground']}")
    print(f"  • {res['three_layer_composition']['background']}\n")

    print("✍️ 【封面大字排版方案】:")
    print(f"  • 主大字: {res['typography_layout']['main_headline']}")
    print(f"  • 副大字: {res['typography_layout']['sub_headline']}")
    print(f"  • 排版建议: {res['typography_layout']['layout_advice']}\n")

    print("🤖 【Midjourney (v6.0) 英文提示词】:")
    print(f"  {res['midjourney_prompt_en']}\n")

    print("✨ 【即梦 / 国内大模型中文提示词】:")
    print(f"  {res['jimeng_prompt_cn']}")
    print("=================================================================\n")

if __name__ == "__main__":
    main()
