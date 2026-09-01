# -*- coding: utf-8 -*-
"""
新 5 大核心技能严苛离线质量与行为验证套件 (Strict Behavioral Test Suite v2.4)
-----------------------------------------------------------------------------
测试矩阵（纯离线验证输入差异性、来源真实性、反向门禁阻断与学术四要素全字段）：
[1] SKILL.md 存在性与 YAML 元数据格式断言
[2] dbs-standard-answer:
    - 学术文献全字段精确核查 (author, title, year, identifier 完整字符串匹配)
    - 反向门禁 A: 只有 facts、没有 sources ➔ 非零阻断
    - 反向门禁 B: 只有 sources、没有 facts ➔ 非零阻断
    - 反向门禁 C: sources 为普通字符串“我编造的来源XYZ” ➔ 非零阻断
    - 反向门禁 D: facts 未关联 source_id ➔ 非零阻断
    - 反向门禁 E: 未联网核验时，输出绝对不得出现“已核实事实”
    - 反向门禁 F: 虚构来源+虚构事实尝试，绝对无法获得 verified 状态 (恒定 user_supplied_unverified)
    - 反向门禁 G: 纯文本事实 + 单一结构化来源 ➔ 严格非零阻断 (严禁自动推断绑定)
    - 反向门禁 H: 源码与 CLI 中绝对不得存在可由调用方设置的 --online-verified
    - 完整合法结构化信源传入 ➔ 成功生成分析与原型 (结构完整、关联完整、用户提供但未经联网核验)
[3] competitor-deconstruct:
    - 机械比例分段验证 (说明中明确注明算法边界)
[4] viral-title-ab-tester:
    - 10 维独立打分完整性核验
    - 零无依据 CTR 字段断言 (严格使用 AND 逻辑)
[5] cover-visual-prompt:
    - 主题动态性验证 (商业主题 vs 治愈主题 动态生成完全不同的主体与构图)
[6] smart-comment-booster:
    - 零虚构作者与出版社断言 (未提供作者时不脑补上野千鹤子)
    - 零虚假水军与小号演戏合规断言
[7] xf-router:
    - 已覆盖场景意图分发测试 (明确报告覆盖用例通过率)
[8] mono-color:
    - 离线设计系统自检与 6 组配方/Prompt 场景测试 (明确未生成任何 PNG/JPG 图片)
"""

import sys, os, subprocess, json
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 纯仓库相对路径，禁止依赖工作区外部绝对路径
SKILLS_ROOT = Path(__file__).resolve().parents[1]

print("=================================================================")
print("🧪 [STRICT BEHAVIORAL TEST v2.4] Running In-Repo Offline Suite...")
print("=================================================================")

# [1] SKILL.md 规范与元数据核验
print("\n--> [Assert 1] Verifying SKILL.md structure & YAML metadata...")
new_skills = [
    "dbs-standard-answer",
    "competitor-deconstruct",
    "viral-title-ab-tester",
    "cover-visual-prompt",
    "smart-comment-booster",
    "mono-color"
]

for sk in new_skills:
    sk_md = SKILLS_ROOT / sk / "SKILL.md"
    assert sk_md.exists(), f"缺少 SKILL.md: {sk}"
    content = sk_md.read_text(encoding="utf-8")
    assert content.startswith("---") and f"name: {sk}" in content
    assert "description:" in content
print("  [PASS] Assert 1: 6 大新技能 SKILL.md 规范完备。")

# [2] dbs-standard-answer 真实学术文献与反向门禁测试 (Gate A ~ Gate H)
print("\n--> [Assert 2] Testing dbs-standard-answer academic citations & reverse gates (A~H)...")
script_dbs = SKILLS_ROOT / "dbs-standard-answer" / "scripts" / "isomorphism_engine.py"

valid_sources_json = json.dumps([
    {
        "source_id": "S1",
        "title": "彭博社关于高调竞拍的专题报道",
        "publisher": "Bloomberg News",
        "url": "https://www.bloomberg.com/news/articles/2023-01-01/example",
        "published_at": "2023-01-01",
        "accessed_at": "2023-01-02"
    }
], ensure_ascii=False)

valid_facts_json = json.dumps([
    {
        "fact_id": "F1",
        "statement": "公开通过高调竞拍巴菲特午餐等争议事件获取关注",
        "source_ids": ["S1"]
    }
], ensure_ascii=False)

# Gate A: 只有 facts、没有 sources ➔ 非零阻断
p_only_facts = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--facts-json", valid_facts_json, "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_only_facts.returncode != 0, "Gate A Failed: 只有 facts 缺少 sources 未能阻断"
assert "missing_sources" in (p_only_facts.stdout + p_only_facts.stderr)

# Gate B: 只有 sources、没有 facts ➔ 非零阻断
p_only_sources = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--sources-json", valid_sources_json, "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_only_sources.returncode != 0, "Gate B Failed: 只有 sources 缺少 facts 未能阻断"
assert "missing_verified_facts" in (p_only_sources.stdout + p_only_sources.stderr)

# Gate C: sources 为普通字符串“我编造的来源XYZ” ➔ 非零阻断
p_fake_str_source = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--facts-json", valid_facts_json,
    "--sources-json", "我编造的来源XYZ",
    "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_fake_str_source.returncode != 0, "Gate C Failed: 传入伪造普通字符串信源未能阻断"
assert "invalid_sources_format" in (p_fake_str_source.stdout + p_fake_str_source.stderr)

# Gate D: facts 未关联 source_id ➔ 非零阻断
unlinked_facts_json = json.dumps([
    {
        "fact_id": "F1",
        "statement": "未关联任何信源的事实陈述",
        "source_ids": []
    }
], ensure_ascii=False)

p_unlinked_fact = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--facts-json", unlinked_facts_json,
    "--sources-json", valid_sources_json,
    "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_unlinked_fact.returncode != 0, "Gate D Failed: 未关联 source_id 的事实未能阻断"
assert "facts_link_failure" in (p_unlinked_fact.stdout + p_unlinked_fact.stderr)

# Gate E: 未联网核验时，输出绝对不得出现“已核实事实”
p_valid_unverified = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--facts-json", valid_facts_json,
    "--sources-json", valid_sources_json,
    "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_valid_unverified.returncode == 0
assert "已核实事实" not in p_valid_unverified.stdout, "Gate E Failed: 未联网核验时输出了'已核实事实'"
assert "公开核验报道" not in p_valid_unverified.stdout, "Gate E Failed: 未联网核验时输出了'公开核验报道'"
assert "user_supplied_unverified" in p_valid_unverified.stdout

# Gate F: 虚构来源+虚构事实，必须无法获得 verified 状态 (恒定 user_supplied_unverified)
fake_sources = json.dumps([{
    "source_id": "FAKE_S1",
    "title": "某虚构网站自媒体文章",
    "publisher": "自媒体",
    "url": "https://example.com/fake",
    "published_at": "2024-01-01",
    "accessed_at": "2024-01-02"
}], ensure_ascii=False)
fake_facts = json.dumps([{
    "fact_id": "FAKE_F1",
    "statement": "用户声称的事实",
    "source_ids": ["FAKE_S1"]
}], ensure_ascii=False)

p_fake_attempt = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--facts-json", fake_facts,
    "--sources-json", fake_sources,
    "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_fake_attempt.returncode == 0
assert "verified_live_fetched" not in p_fake_attempt.stdout, "Gate F Failed: 获得了未经授权的 verified 状态"
assert "user_supplied_unverified" in p_fake_attempt.stdout

# Gate G: 纯文本事实 + 单一结构化来源 ➔ 严格非零阻断 (严禁自动推断绑定)
p_plaintext_fact = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "孙宇晨注意力套利", "--domain", "个人IP",
    "--facts-json", "这是一段未结构化的纯文本事实陈述",
    "--sources-json", valid_sources_json,
    "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_plaintext_fact.returncode != 0, "Gate G Failed: 纯文本事实未能被非零阻断"
assert "verified_facts 必须为结构化 JSON 列表" in (p_plaintext_fact.stdout + p_plaintext_fact.stderr)

# Gate H: 源码与 CLI 中绝对不得存在可由调用方设置的 --online-verified
script_code = script_dbs.read_text(encoding="utf-8")
assert "--online-verified" not in script_code, "Gate H Failed: 源码中仍存在 --online-verified 参数"
assert "online_verified" not in script_code, "Gate H Failed: 源码中仍存在 online_verified 变量"

# 学术引用四要素全字段精确核验
assert "Richard A. Lanham (2006) 《The Economics of Attention: Style and Substance in the Age of Information》, ISBN: 978-0226468822" in p_valid_unverified.stdout
assert "Charles Mackay (1841) 《Extraordinary Popular Delusions and the Madness of Crowds》, ISBN: 978-1463740511" in p_valid_unverified.stdout

# 验证 Toffler & Reingold 安达信全字段
brand_sources = json.dumps([{
    "source_id": "S1", "title": "监管通报", "publisher": "市场监管局",
    "url": "https://gov.cn/bulletin/123", "published_at": "2023-01-01", "accessed_at": "2023-01-02"
}], ensure_ascii=False)
brand_facts = json.dumps([{
    "fact_id": "F1", "statement": "通报关于代言合规性问题", "source_ids": ["S1"]
}], ensure_ascii=False)

p_brand = subprocess.run([
    sys.executable, str(script_dbs),
    "--topic", "景甜代言与品牌声誉", "--domain", "品牌公关",
    "--facts-json", brand_facts,
    "--sources-json", brand_sources,
    "--strict-evidence"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_brand.returncode == 0
assert "Barbara Ley Toffler & Jennifer Reingold (2003) 《Final Accounting: Ambition, Greed, and the Fall of Arthur Andersen》, ISBN: 978-0767913836" in p_brand.stdout

print("  [PASS] Assert 2: dbs-standard-answer 8项反向门禁(Gate A~H)与学术四要素全字段匹配 100% 通过！")
print("         状态核验: 结构完整、事实与来源关联完整、用户提供但未经联网核验。")

# [3] competitor-deconstruct 机械比例分段测试
print("\n--> [Assert 3] Testing competitor-deconstruct mechanical segmentation...")
script_comp = SKILLS_ROOT / "competitor-deconstruct" / "scripts" / "deconstruct_hook.py"

text_sample = "女人退休后，为什么越勤劳越不讨喜？很多母亲为儿女操持了一辈子，最后却换来嫌弃。做母亲必须有边界感。学会放手，把爱还给自己，老后才能从容自立。"
p_comp = subprocess.run([sys.executable, str(script_comp), "--text", text_sample], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_comp.returncode == 0
assert "机械比例分段" in p_comp.stdout or "机械分段" in p_comp.stdout
assert "开篇首句" in p_comp.stdout
print("  [PASS] Assert 3: competitor-deconstruct 真实执行机械分段并明确标注算法边界。")

# [4] viral-title-ab-tester 10 维独立打分与 AND 逻辑 CTR 禁词断言
print("\n--> [Assert 4] Testing viral-title-ab-tester 10 independent dimensions & AND logic CTR assertion...")
script_title = SKILLS_ROOT / "viral-title-ab-tester" / "scripts" / "evaluate_titles.py"

p_title = subprocess.run([
    sys.executable, str(script_title),
    "--titles", "女人退休后，为什么越勤劳越不讨喜？", "普通关于生活的文章",
    "--platform", "channels"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_title.returncode == 0

# 检查 10 维指标全量存在
expected_dims = [
    "1_冲突对立度", "2_悬念好奇心", "3_损失厌恶感", "4_情绪极化值", "5_具象人群锚定",
    "6_数字化具象感", "7_平台载体适配", "8_手机单屏字数控制", "9_承诺价值明确度", "10_合规安全评分"
]
for dim in expected_dims:
    assert dim in p_title.stdout, f"缺少评估维度: {dim}"

# 严格使用 AND 逻辑断言绝对不含无实测依据的 CTR 宣称
out_lower = p_title.stdout.lower()
assert ("ctr" not in out_lower) and ("click-through" not in out_lower), "存在无依据的 CTR 预测！"
assert "启发式总分" in p_title.stdout
print("  [PASS] Assert 4: viral-title-ab-tester 10 维打分完备，严格通过 AND 逻辑零 CTR 断言。")

# [5] cover-visual-prompt 主题与风格动态性验证
print("\n--> [Assert 5] Testing cover-visual-prompt dynamic subjects...")
script_cover = SKILLS_ROOT / "cover-visual-prompt" / "scripts" / "generate_cover_prompts.py"

p_biz = subprocess.run([
    sys.executable, str(script_cover), "--theme", "孙宇晨的注意力套利与商业博弈", "--style", "cinematic_business"
], capture_output=True, text=True, encoding="utf-8", errors="replace")

p_heal = subprocess.run([
    sys.executable, str(script_cover), "--theme", "退休母亲的晚年从容生活", "--style", "healing_illustration"
], capture_output=True, text=True, encoding="utf-8", errors="replace")

assert p_biz.returncode == 0 and p_heal.returncode == 0
assert ("国际象棋" in p_biz.stdout) or ("商业" in p_biz.stdout)
assert ("绿植" in p_heal.stdout) or ("从容" in p_heal.stdout)
assert p_biz.stdout != p_heal.stdout
print("  [PASS] Assert 5: cover-visual-prompt 针对商业与治愈主题动态生成完全不同的主体与构图。")

# [6] smart-comment-booster 零事实虚构与零水军断言
print("\n--> [Assert 6] Testing smart-comment-booster zero author hallucination...")
script_comm = SKILLS_ROOT / "smart-comment-booster" / "scripts" / "generate_comments.py"

# 传入任意书名《原则》，未指定作者时，绝不能脑补为“上野千鹤子”
p_comm_generic = subprocess.run([
    sys.executable, str(script_comm), "--theme", "个人成长", "--book", "原则"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_comm_generic.returncode == 0
assert "上野千鹤子" not in p_comm_generic.stdout, "未指定作者时错误脑补了上野千鹤子！"
assert "人民文学出版社" not in p_comm_generic.stdout, "未指定出版社时错误脑补了出版社！"

# 传入指定作者时，正确回显
p_comm_explicit = subprocess.run([
    sys.executable, str(script_comm),
    "--theme", "晚年自立", "--book", "一个人的老后", "--author", "上野千鹤子", "--publisher", "人民文学出版社"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_comm_explicit.returncode == 0
assert "上野千鹤子" in p_comm_explicit.stdout
assert "人民文学出版社" in p_comm_explicit.stdout
print("  [PASS] Assert 6: smart-comment-booster 绝无作者事实虚构，100% 依凭核查输入。")

# [7] xf-router 意图分发测试 (明确报告覆盖用例通过率)
print("\n--> [Assert 7] Testing xf-router triage on covered test suite (6/6)...")
script_xf = SKILLS_ROOT / "xf-router" / "scripts" / "xf_triage.py"

triage_tests = [
    ("我想追孙宇晨和景甜最近的热点立人设", "dbs-standard-answer"),
    ("帮我拆解同行爆款视频的骨架", "competitor-deconstruct"),
    ("帮我给新视频起几个高点击标题并打分", "viral-title-ab-tester"),
    ("帮我生成孔版印刷海报和单色双色Risograph底图", "mono-color"),
    ("帮我生成小红书大字封面和 Midjourney 提示词", "cover-visual-prompt"),
    ("视频发了，帮我写一套作者置顶首评和官方答疑", "smart-comment-booster")
]

passed_count = 0
for prompt_str, exp_skill in triage_tests:
    p_xf = subprocess.run([sys.executable, str(script_xf), prompt_str], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert p_xf.returncode == 0
    assert f"[{exp_skill}]" in p_xf.stdout, f"路由识别不匹配: '{prompt_str}' -> {exp_skill}"
    passed_count += 1

print(f"  [PASS] Assert 7: xf-router 6 组基准用例测试通过率 100% ({passed_count}/{len(triage_tests)} PASS)。")

# [8] mono-color 独立技能设计系统自检与 6 组离线配方/Prompt 场景测试 (明确未生成 PNG/JPG)
print("\n--> [Assert 8] Testing mono-color design system & 6 offline recipe/prompt scenarios (No PNG/JPG claimed)...")
script_mono_test = SKILLS_ROOT / "mono-color" / "scripts" / "test_mono_color_offline.py"
p_mono = subprocess.run([sys.executable, str(script_mono_test)], cwd=SKILLS_ROOT / "mono-color" / "scripts", capture_output=True, text=True, encoding="utf-8", errors="replace")
assert p_mono.returncode == 0, f"mono-color test failed: {p_mono.stderr}"
print("  [PASS] Assert 8: mono-color 上游设计系统、16 组 Evals 与 6 组离线配方/Prompt 场景断言全部 100% 验证通过 (未生成实体图片)！")

print("\n=================================================================")
print("🏆 [STRICT SUITE v2.4 8/8 PASS] 8大断言、反向门禁、全字段学术四要素与mono-color全通！")
print("=================================================================\n")
