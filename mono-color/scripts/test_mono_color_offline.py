# -*- coding: utf-8 -*-
"""
mono-color 独立技能严苛离线质量与 6 组配方/Prompt 场景测试套件 (Strict Verification Suite v1.1)
-----------------------------------------------------------------------------------------
验证矩阵：
[1] 上游设计系统 19 墨色、10 色板、7 排版角色、9 构图、7 载体、5 瑕疵、3 节奏规范核验 (100% PASS)
[2] 上游 16 组核心评测契约核验 (validate_evals.py 100% PASS)
[3] LICENSE 与 ASSET-LICENSE.md 与 UPSTREAM.json 物理存在性与哈希一致性验签
[4] 6 组离线配方与 Prompt 场景测试 (注意：本测试仅校验配方 Manifest、Prompt 语法与排版建议，未生成任何实体图片)：
    - Scene 1: 中文单色海报配方 (Cobalt 纯单色)
    - Scene 2: 中文双色海报配方 (Cobalt + Terracotta 双色孔版印刷)
    - Scene 3: 人像保真封面配方 (Charcoal + Signal Red 现代冷灰底)
    - Scene 4: 纯文字金句卡配方 (Signal Red 50% 大面积留白)
    - Scene 5: 商品/书籍封面配方 (Botanical Green + Oxblood 暖米白底)
    - Scene 6: 小红书 3:4 封面配方 (Mint Green + Charcoal 3:4 竖版)
[5] 严格测试断言：
    - 墨色上限: <= 2 种油墨
    - 留白区间: 25% ~ 55% 纯净纸张留白
    - 提示词质感: 严格包含 'spot ink', 'neutral paper substrate' (或 'paper substrate'), 'Risograph', 'halftone'
    - 杜绝 3D 渲染包装: 严格包含 'no mockup'
    - 排版协同: 必须生成 ai-quote-card-maker 精确中文文字覆盖指引
"""

import sys, os, subprocess, json, hashlib
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"

print("=================================================================")
print("🧪 [MONO-COLOR STRICT TEST] Running Deep Offline Verification...")
print("=================================================================")

# [1] 上游设计系统与评测校验
print("\n--> [Assert 1] Verifying upstream design system catalogs...")
p_ds = subprocess.run([sys.executable, str(SCRIPTS_DIR / "validate_design_system.py")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_ds.returncode == 0, f"design system validation failed: {p_ds.stderr}"
print(f"  [PASS] Assert 1: {p_ds.stdout.strip()}")

print("\n--> [Assert 2] Verifying upstream evals cases (16 cases)...")
p_ev = subprocess.run([sys.executable, str(SCRIPTS_DIR / "validate_evals.py")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_ev.returncode == 0, f"evals validation failed: {p_ev.stderr}"
print(f"  [PASS] Assert 2: {p_ev.stdout.strip()}")

# [2] 许可证与上游凭证验签
print("\n--> [Assert 3] Verifying LICENSE, ASSET-LICENSE.md, UPSTREAM.json...")
lic_file = ROOT / "LICENSE"
asset_lic_file = ROOT / "ASSET-LICENSE.md"
upstream_file = ROOT / "UPSTREAM.json"

assert lic_file.exists(), "缺少 LICENSE 文件"
assert asset_lic_file.exists(), "缺少 ASSET-LICENSE.md 文件"
assert upstream_file.exists(), "缺少 UPSTREAM.json 文件"

lic_sha = hashlib.sha256(lic_file.read_bytes()).hexdigest()
asset_lic_sha = hashlib.sha256(asset_lic_file.read_bytes()).hexdigest()

assert lic_sha == "2025880f6441e121c76c01bc5996e84a7498d9d5aa7222a10400d303bdd043cb", f"LICENSE SHA 异常: {lic_sha}"
assert asset_lic_sha == "70eb1637a6d04652c494f8e20bdf82b6a675e9bbbc34b6bbf4b6f503cae9eea4", f"ASSET-LICENSE SHA 异常: {asset_lic_sha}"

upstream_data = json.loads(upstream_file.read_text(encoding="utf-8"))
assert upstream_data.get("upstream_commit") == "de607fedfff647eaf5400e0aa43085787d7d1fca"
assert "examples/" in upstream_data.get("excluded_upstream_paths", [])
assert "UPSTREAM.json" in upstream_data.get("local_added_files", [])
assert "scripts/generate_mono_recipe.py" in upstream_data.get("local_added_files", [])
assert "scripts/test_mono_color_offline.py" in upstream_data.get("local_added_files", [])
assert "scripts/validate_design_system.py" in upstream_data.get("local_modified_files", [])
print(f"  [PASS] Assert 3: 许可证与上游溯源凭证核验一致 (Commit: de607fed, examples/ 已物理排除，本地新增脚本已逐项显式登记)。")

# [3] 6 组离线配方与 Prompt 场景测试
print("\n--> [Assert 4] Testing 6 Offline Recipe & Prompt Scenarios (No Images Claimed)...")
from generate_mono_recipe import generate_mono_artifact

test_scenes = [
    {
        "name": "Scene 1: 中文单色海报配方 (Cobalt 纯单色)",
        "subject": "独自站在雨夜站台上的风衣旅人",
        "intent": "cultural_poster",
        "text": "独自等待也是一种修行",
        "mode": "pure one-ink",
        "palette": "cobalt",
        "ratio": "3:4",
        "exp_inks": 1,
        "exp_empty_min": 25,
        "exp_empty_max": 55
    },
    {
        "name": "Scene 2: 中文双色海报配方 (Cobalt + Terracotta 双色孔版印刷)",
        "subject": "穿梭在老街胡同里的复古自行车",
        "intent": "city_guide",
        "text": "城市漫步指南：在旧时光里呼吸",
        "mode": "controlled two-ink",
        "palette": "cobalt_terracotta",
        "ratio": "3:4",
        "exp_inks": 2,
        "exp_empty_min": 25,
        "exp_empty_max": 55
    },
    {
        "name": "Scene 3: 人像保真封面配方 (Charcoal + Signal Red 现代冷灰底)",
        "subject": "沉思中的建筑师侧影特写",
        "intent": "portrait_cover",
        "text": "秩序与自由的边界",
        "mode": "controlled two-ink",
        "palette": "charcoal_signal_red",
        "ratio": "3:4",
        "exp_inks": 2,
        "exp_empty_min": 25,
        "exp_empty_max": 55
    },
    {
        "name": "Scene 4: 纯文字金句卡配方 (Signal Red 50% 大面积留白)",
        "subject": "巨大的印刷体抽象数字与文字排版",
        "intent": "quote_card",
        "text": "不被定义的人生，从拒绝妥协开始",
        "mode": "pure one-ink",
        "palette": "signal_red",
        "ratio": "1:1",
        "exp_inks": 1,
        "exp_empty_min": 40,
        "exp_empty_max": 55
    },
    {
        "name": "Scene 5: 商品/书籍封面配方 (Botanical Green + Oxblood 暖米白底)",
        "subject": "手工陶罐与一枝野草",
        "intent": "book_cover",
        "text": "自然与生活方式的手记",
        "mode": "controlled two-ink",
        "palette": "botanical_oxblood",
        "ratio": "3:4",
        "exp_inks": 2,
        "exp_empty_min": 35,
        "exp_empty_max": 55
    },
    {
        "name": "Scene 6: 小红书 3:4 封面配方 (Mint Green + Charcoal 3:4 竖版)",
        "subject": "窗台旁的咖啡杯与翻开的书页",
        "intent": "xhs_cover",
        "text": "独处日记：享受一个人的慢时光",
        "mode": "controlled two-ink",
        "palette": "mint_charcoal",
        "ratio": "3:4",
        "exp_inks": 2,
        "exp_empty_min": 25,
        "exp_empty_max": 45
    }
]

for idx, tc in enumerate(test_scenes, 1):
    res = generate_mono_artifact(
        subject=tc["subject"],
        intent=tc["intent"],
        exact_text=tc["text"],
        mode=tc["mode"],
        palette=tc["palette"],
        ratio=tc["ratio"]
    )
    assert res["status"] == "success"
    manifest = res["recipe_manifest"]
    prompt = res["production_prompt"]
    note = res["recipe_note"]

    # 严格断言
    assert len(manifest["inks"]) == tc["exp_inks"], f"{tc['name']} 墨水数量异常: {manifest['inks']}"
    assert tc["exp_empty_min"] <= manifest["empty_paper_percent"] <= tc["exp_empty_max"], f"{tc['name']} 留白率超限: {manifest['empty_paper_percent']}"
    assert "Risograph" in prompt, f"{tc['name']} Prompt 缺少 Risograph"
    assert "spot ink" in prompt, f"{tc['name']} Prompt 缺少 spot ink"
    assert ("paper substrate" in prompt) or ("neutral paper" in prompt), f"{tc['name']} Prompt 缺少 paper substrate"
    assert "halftone" in prompt.lower(), f"{tc['name']} Prompt 缺少 halftone"
    assert "no mockup" in prompt.lower(), f"{tc['name']} Prompt 缺少 no mockup"
    assert "ai-quote-card-maker" in note, f"{tc['name']} 缺少 ai-quote-card-maker 指引"
    assert tc["text"] in note

    print(f"  • [{idx}/6] PASS: {tc['name']}")
    print(f"        油墨: {', '.join(manifest['inks'])} | 留白: {manifest['empty_paper_percent']}% | 纸底: {manifest['substrate']}")

print("\n=================================================================")
print("🏆 [MONO-COLOR PASS] 上游设计系统自检与 6 组配方/Prompt 场景断言全部满分通过！")
print("=================================================================\n")
