# -*- coding: utf-8 -*-
"""
单色与双色出版级印刷海报生成引擎 (Monocolor Editorial Print Engine v1.0)
-----------------------------------------------------------------------
严格遵循设计系统规范：
- 基底 (Substrate): 极简冷白 (#FAFAF7), 现代冷灰 (#E9E9E5), 暖米白纸 (#F5F1E8)
- 墨色 (Inks): 严格限制 <=2 种油墨 (纯单色 8 大色系 / 双色 9 套经典配方)
- 留白 (Space): 强制保留 25%~55% 纯净纸张留白，非对称编辑栅格
- 质感 (Texture): 半色调网点 (Halftone), 孔版印刷 (Risograph), 蓝晒 (Cyanotype)
- 协同 (Pipeline): 生成底图提示词，供 ai-quote-card-maker 进行高精度中文文字排版覆盖
"""

import sys, os, json, argparse, hashlib
from pathlib import Path

# Force UTF-8 stdout & stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_DIR = ROOT / "design-system"

def load_catalog(name: str) -> dict:
    p = SYSTEM_DIR / name
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

COLORS_CATALOG = load_catalog("colors.json")
TYPOGRAPHY_CATALOG = load_catalog("typography.json")
COMPOSITIONS_CATALOG = load_catalog("compositions.json")
CARRIERS_CATALOG = load_catalog("carriers.json")
IMPERFECTIONS_CATALOG = load_catalog("imperfections.json")
RHYTHM_CATALOG = load_catalog("rhythm.json")

# 经典色板与墨水映射表
PALETTE_MAP = {
    "cobalt": {"id": "palette_cobalt", "mode": "pure one-ink", "inks": ["Cobalt / Ultramarine (#2148B8)"], "substrate": "#FAFAF7"},
    "terracotta": {"id": "palette_terracotta", "mode": "pure one-ink", "inks": ["Terracotta Orange (#C65F38)"], "substrate": "#F5F1E8"},
    "signal_red": {"id": "palette_signal_red", "mode": "pure one-ink", "inks": ["Signal Red (#C83232)"], "substrate": "#FAFAF7"},
    "aubergine": {"id": "palette_aubergine", "mode": "pure one-ink", "inks": ["Aubergine (#63365F)"], "substrate": "#FAFAF7"},
    "cobalt_terracotta": {"id": "palette_cobalt_terracotta", "mode": "controlled two-ink", "inks": ["Cobalt (#2148B8)", "Terracotta (#C65F38)"], "substrate": "#FAFAF7"},
    "charcoal_signal_red": {"id": "palette_charcoal_signal_red", "mode": "controlled two-ink", "inks": ["Charcoal (#30343A)", "Signal Red (#C83232)"], "substrate": "#E9E9E5"},
    "botanical_oxblood": {"id": "palette_botanical_oxblood", "mode": "controlled two-ink", "inks": ["Botanical Green (#008A4B)", "Oxblood (#8F3434)"], "substrate": "#F5F1E8"},
    "mint_charcoal": {"id": "palette_mint_charcoal", "mode": "controlled two-ink", "inks": ["Mint Green (#5EB783)", "Charcoal (#302D2E)"], "substrate": "#FAFAF7"},
    "cyan_brick_red": {"id": "palette_cyan_brick_red", "mode": "controlled two-ink", "inks": ["Cyan (#159DDA)", "Brick Red (#B64032)"], "substrate": "#FAFAF7"},
    "ultramarine_safety_orange": {"id": "palette_ultramarine_safety_orange", "mode": "controlled two-ink", "inks": ["Ultramarine (#263E99)", "Safety Orange (#E55D2B)"], "substrate": "#FAFAF7"}
}

def resolve_recipe_manifest(
    subject: str,
    intent: str = "cultural_poster",
    exact_text: str = "",
    mode: str = "controlled two-ink",
    palette_key: str = "cobalt_terracotta",
    ratio: str = "3:4",
    carrier_id: str = "carrier_editorial_poster",
    substrate_hex: str = "#FAFAF7",
    representation: str = "faithful reproduction"
) -> dict:
    # 自动匹配色板
    pal_info = PALETTE_MAP.get(palette_key, PALETTE_MAP["cobalt_terracotta"])
    if mode == "pure one-ink" and pal_info["mode"] != "pure one-ink":
        pal_info = PALETTE_MAP["cobalt"]

    # 确定排版角色与留白
    if "book" in intent or "literature" in intent or "书籍" in intent:
        type_role = "role_literary_serif"
        layout_id = "comp_hero_photograph"
        empty_paper = 40
        tension = "relaxed"
    elif "portrait" in intent or "人像" in intent:
        type_role = "role_cultural_grotesk"
        layout_id = "comp_isolated_specimen"
        empty_paper = 35
        tension = "balanced"
    elif "quote" in intent or "金句" in intent or "declaration" in intent:
        type_role = "role_typographic_object"
        layout_id = "comp_declaration"
        empty_paper = 50
        tension = "assertive"
    elif "xhs" in carrier_id or "小红书" in intent:
        type_role = "role_rotated_display"
        layout_id = "comp_journal_entry"
        empty_paper = 30
        tension = "balanced"
    else:
        type_role = "role_condensed_civic"
        layout_id = "comp_hero_photograph"
        empty_paper = 35
        tension = "balanced"

    # 构造确定性 Manifest
    manifest = {
        "subject": subject,
        "intent": intent,
        "exact_text": exact_text,
        "representation": representation,
        "ratio": ratio,
        "carrier": carrier_id,
        "substrate": substrate_hex,
        "mode": pal_info["mode"],
        "palette": pal_info["id"],
        "inks": pal_info["inks"],
        "plate_roles": {
            "dominant_plate (70-85%)": pal_info["inks"][0],
            "accent_plate (15-30%)": pal_info["inks"][1] if len(pal_info["inks"]) > 1 else "None (Single Ink Only)"
        },
        "layout": layout_id,
        "empty_paper_percent": empty_paper,
        "visual_tension": tension,
        "focal_event": "one off-center high-contrast subject crop",
        "release_zone": f"generous {empty_paper}% visible paper field with zero clutter",
        "image_treatment": "fine halftone screening, risograph spot color print, physical screen texture",
        "type_hierarchy": type_role
    }
    return manifest

def build_production_prompt(manifest: dict) -> str:
    """生成 Midjourney / 即梦 / SD 高精度提示词"""
    subject = manifest["subject"]
    substrate = manifest["substrate"]
    inks = ", ".join(manifest["inks"])
    ratio = manifest["ratio"]
    empty_paper = manifest["empty_paper_percent"]

    # 构造英文高质感 Prompt
    ar_tag = f"--ar {ratio.replace(':', ':')}" if ":" in ratio else "--ar 3:4"

    prompt = (
        f"Editorial print poster design, featuring {subject}. "
        f"Strict printing process: authentic two-tone Risograph print, spot ink on neutral paper substrate ({substrate}). "
        f"Limited color palette strictly restricted to: {inks}. "
        f"Fine halftone screen pattern, visible mechanical print grain, ink absorption texture, clean edge bleed. "
        f"Composition: generous {empty_paper}% active negative space, asymmetric Swiss editorial grid layout, "
        f"minimalist and restrained typography placement, elegant whitespace. "
        f"Front-facing flat scan, no mockup, no frame, no camera angle, pure graphic print artifact. {ar_tag} --style raw --v 6.1"
    )
    return prompt

def generate_mono_artifact(
    subject: str,
    intent: str = "cultural_poster",
    exact_text: str = "",
    mode: str = "controlled two-ink",
    palette: str = "cobalt_terracotta",
    ratio: str = "3:4",
    carrier_id: str = "carrier_editorial_poster"
) -> dict:
    manifest = resolve_recipe_manifest(
        subject=subject,
        intent=intent,
        exact_text=exact_text,
        mode=mode,
        palette_key=palette,
        ratio=ratio,
        carrier_id=carrier_id
    )
    prompt = build_production_prompt(manifest)

    recipe_note = (
        f"• 色板模式: {manifest['mode']} ({', '.join(manifest['inks'])})\n"
        f"• 纸张底色: {manifest['substrate']}\n"
        f"• 构图留白: {manifest['empty_paper_percent']}%\n"
        f"• 版式角色: {manifest['type_hierarchy']}\n"
        f"• 后期建议: 底图生成后由 ai-quote-card-maker 叠加精确中文字符: 「{exact_text}」"
    )

    return {
        "status": "success",
        "recipe_manifest": manifest,
        "production_prompt": prompt,
        "recipe_note": recipe_note
    }

def main():
    parser = argparse.ArgumentParser(description="单色与双色出版级印刷海报生成引擎 (mono-color v1.0)")
    parser.add_argument("--subject", type=str, required=True, help="视觉核心主体或主题隐喻")
    parser.add_argument("--intent", type=str, default="cultural_poster", help="创作意图 (poster/book/portrait/quote/xhs)")
    parser.add_argument("--text", type=str, default="", help="待排版的文本或金句")
    parser.add_argument("--mode", type=str, default="controlled two-ink", choices=["pure one-ink", "controlled two-ink"], help="油墨模式")
    parser.add_argument("--palette", type=str, default="cobalt_terracotta", help="预设色板 ID")
    parser.add_argument("--ratio", type=str, default="3:4", help="画面比例")
    parser.add_argument("--carrier", type=str, default="carrier_editorial_poster", help="载体类型")

    args = parser.parse_args()

    res = generate_mono_artifact(
        subject=args.subject,
        intent=args.intent,
        exact_text=args.text,
        mode=args.mode,
        palette=args.palette,
        ratio=args.ratio,
        carrier_id=args.carrier
    )

    print("\n=================================================================")
    print(f"🖨️ 【单色/双色出版级印刷海报配方 (Monocolor Recipe)】: {args.subject}")
    print("=================================================================")
    print(f"🎨 墨色系统: {res['recipe_manifest']['mode']}")
    print(f"   • 油墨清单: {', '.join(res['recipe_manifest']['inks'])}")
    print(f"   • 纸张基底: {res['recipe_manifest']['substrate']}")
    print(f"   • 画面留白: {res['recipe_manifest']['empty_paper_percent']}%")
    print(f"   • 栅格排版: {res['recipe_manifest']['layout']} / {res['recipe_manifest']['type_hierarchy']}\n")

    print("📜 【AI 绘画精准生产 Prompt (Midjourney / 即梦)】:")
    print(f"  {res['production_prompt']}\n")

    print("🛠️ 【后期排版协同指引 (ai-quote-card-maker)】:")
    print(f"  {res['recipe_note']}")
    print("=================================================================\n")

if __name__ == "__main__":
    main()
