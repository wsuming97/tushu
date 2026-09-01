# -*- coding: utf-8 -*-
"""
基于已核验事实的历史案例类比与专业立论建议器 (Historical Analogy & Standard Answer Advisor v2.3)
-----------------------------------------------------------------------------------------
核心治理规范：
1. 真实来源与严格状态标定：
   - 严禁调用方通过任何布尔参数声明已联网核验；
   - 本工具当前无真实外部网络抓取引擎，所有输入统一恒定标定为：
     source_status="user_supplied_unverified"
     source_status_description="用户提供事实与信源（未经联网核验）"；
2. 严禁纯文本事实自动绑定：
   - verified_facts 必须严格为结构化字典列表；
   - 每一条事实必须显式包含 fact_id, statement, source_ids，即使单来源也严禁自动绑定纯文本；
3. 学术文献四要素完整性：
   - 必须提供【作者、书名/篇名、年份、唯一标识符(ISBN/DOI/HBS Case)】。
"""

import sys, os, json, argparse, re
from pathlib import Path

# Force UTF-8 stdout & stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 经核实的历史学术文献与案例库 (带唯一标识符 ISBN/DOI/HBS Case 四要素)
VERIFIED_HISTORICAL_ACADEMIC_BASE = [
    {
        "domain_id": "attention_capital_arbitrage",
        "keywords": ["注意力", "流量", "黑红", "炒作", "名人", "争议", "孙宇晨", "网红", "博眼球"],
        "theory_name": "注意力套利与声誉资本理论 (Attention Arbitrage & Reputation Capital)",
        "academic_citation": {
            "author": "Richard A. Lanham",
            "title": "The Economics of Attention: Style and Substance in the Age of Information",
            "year": 2006,
            "publisher": "University of Chicago Press",
            "identifier": "ISBN: 978-0226468822"
        },
        "secondary_citation": {
            "author": "Pierre Bourdieu",
            "title": "The Forms of Capital",
            "year": 1986,
            "identifier": "DOI: 10.1002/9780470755679.ch15"
        },
        "archetype_name": "注意力极化套利 vs 长期声誉资本防御",
        "positive_historical_case": {
            "entity": "理查德·布兰森 (Richard Branson) 与维珍集团 (Virgin Group)",
            "fact_summary": "布兰森通过高调个人冒险吸引公众注意力，但他将眼球效应严格注入实体航空与零售的交付品质中，守住商业闭环。",
            "citation": {
                "author": "Richard Branson",
                "title": "Losing My Virginity: How I Survial, Had Fun, and Made a Fortune Doing Business My Way",
                "year": 1998,
                "identifier": "ISBN: 978-0307720740"
            }
        },
        "negative_historical_case": {
            "entity": "约翰·布朗特 (John Blunt) 与英国南海公司 (South Sea Company, 1720)",
            "fact_summary": "通过制造虚假繁荣与极端争议炒作股价，但底层无真实业务支撑，最终导致英国南海泡沫破裂、个人信用彻底破产并引发法律清算。",
            "citation": {
                "author": "Charles Mackay",
                "title": "Extraordinary Popular Delusions and the Madness of Crowds",
                "year": 1841,
                "identifier": "ISBN: 978-1463740511"
            }
        },
        "boundary_conditions": "黑红与注意力套利仅适用于有强对冲资产与短期退出渠道的极端投机者；对于依靠信任复利的知识博主与专业 IP，透支信用的边际成本远高于短期流量收益。"
    },
    {
        "domain_id": "brand_reputation_crisis",
        "keywords": ["景甜", "代言", "品牌", "翻车", "声誉", "明星", "违规", "公关", "信任危机"],
        "theory_name": "信号传递理论与品牌背书风险模型 (Signaling Theory in Brand Endorsement)",
        "academic_citation": {
            "author": "Michael Spence",
            "title": "Job Market Signaling",
            "year": 1973,
            "publisher": "The Quarterly Journal of Economics",
            "identifier": "DOI: 10.2307/1882010"
        },
        "secondary_citation": {
            "author": "David A. Aaker",
            "title": "Building Strong Brands",
            "year": 1996,
            "publisher": "Free Press",
            "identifier": "ISBN: 978-0029001516"
        },
        "archetype_name": "品牌溢价透支 vs 声誉防火墙隔离",
        "positive_historical_case": {
            "entity": "强生公司 (Johnson & Johnson) 1982年泰诺胶囊危机处理",
            "fact_summary": "在遭遇恶意投毒后主动全国召回并研发防篡改包装，以极高的短期经济代价换取了长期无法撼动的公众信任资产。",
            "citation": {
                "author": "Stephen Greyser & Norman Klein",
                "title": "Johnson & Johnson: The Tylenol Tragedy",
                "year": 1982,
                "publisher": "Harvard Business School Case Study",
                "identifier": "HBS Case 9-583-043"
            }
        },
        "negative_historical_case": {
            "entity": "安达信会计师事务所 (Arthur Andersen) 与安然事件 (2001)",
            "fact_summary": "为了短期咨询高额利润放弃审计独立性底线，为客户造假背书，最终直接导致拥有89年历史的全球五大审计巨头解体。",
            "citation": {
                "author": "Barbara Ley Toffler & Jennifer Reingold",
                "title": "Final Accounting: Ambition, Greed, and the Fall of Arthur Andersen",
                "year": 2003,
                "publisher": "Broadway Business",
                "identifier": "ISBN: 978-0767913836"
            }
        },
        "boundary_conditions": "声誉资产具有严重的非对称性（建立需数十年，摧毁仅需数日）；个人 IP 在承接外部商业合作时必须设立严格的风控防火墙。"
    },
    {
        "domain_id": "service_to_product_transition",
        "keywords": ["转型", "定制", "标准化", "产品化", "交付", "外包", "商业模式", "saas"],
        "theory_name": "创新者的窘境与定制服务规模化悖论 (Service Standardization Dilemma)",
        "academic_citation": {
            "author": "Clayton M. Christensen",
            "title": "The Innovator's Dilemma: When New Technologies Cause Great Firms to Fail",
            "year": 1997,
            "publisher": "Harvard Business Review Press",
            "identifier": "ISBN: 978-1633691780"
        },
        "secondary_citation": {
            "author": "Geoffrey A. Moore",
            "title": "Crossing the Chasm",
            "year": 1991,
            "publisher": "HarperBusiness",
            "identifier": "ISBN: 978-0060511982"
        },
        "archetype_name": "定制项目现金流陷阱 vs 核心产品化突破",
        "positive_historical_case": {
            "entity": "IBM 在 1990 年代郭士纳 (Lou Gerstner) 主导的软硬件与服务整合转型",
            "fact_summary": "将分散的定制服务能力沉淀为模块化行业解决方案，成功摆脱单一硬件衰退危机。",
            "citation": {
                "author": "Louis V. Gerstner Jr.",
                "title": "Who Says Elephants Can't Dance? Inside IBM's Historic Turnaround",
                "year": 2002,
                "publisher": "HarperBusiness",
                "identifier": "ISBN: 978-0060523794"
            }
        },
        "negative_historical_case": {
            "entity": "早期 IT 软件外包行业转型 SaaS 的普遍困境",
            "fact_summary": "无法忍受产品研发前期的无现金流期，反复将核心研发人员抽调回去救火做定制交付，最终导致产品研发无限延期、两头落空。",
            "citation": {
                "author": "Michael A. Cusumano",
                "title": "The Business of Software",
                "year": 2004,
                "publisher": "Free Press",
                "identifier": "ISBN: 978-0743215800"
            }
        },
        "boundary_conditions": "从定制服务走向产品化，必须在组织架构与财务考核上建立物理隔离，否则定制项目的紧急性必然吞噬产品研发的战略重要性。"
    }
]

def find_isomorphism_match(topic: str, domain: str) -> dict:
    search_text = f"{topic} {domain}".lower()
    best_match = None
    max_score = 0

    for item in VERIFIED_HISTORICAL_ACADEMIC_BASE:
        score = 0
        for kw in item["keywords"]:
            if kw.lower() in search_text:
                score += 1
        if score > max_score:
            max_score = score
            best_match = item

    return best_match if max_score > 0 else None

def parse_and_validate_sources(sources_input) -> tuple[bool, list, str]:
    """
    验证信源必须为包含 6 项结构化字段的列表:
    source_id, title, publisher, url, published_at, accessed_at
    """
    if not sources_input:
        return False, [], "sources 列表为空"

    if isinstance(sources_input, str):
        try:
            sources_input = json.loads(sources_input)
        except Exception:
            return False, [], f"sources 格式错误，无法解析为 JSON: {sources_input}"

    if not isinstance(sources_input, list) or len(sources_input) == 0:
        return False, [], "sources 必须为非空结构化列表"

    required_keys = ["source_id", "title", "publisher", "url", "published_at", "accessed_at"]
    validated = []

    for idx, s in enumerate(sources_input, 1):
        if not isinstance(s, dict):
            return False, [], f"sources[{idx}] 必须为结构化字典，不能为普通字符串 (如 '{s}')"
        for k in required_keys:
            val = str(s.get(k, "")).strip()
            if not val:
                return False, [], f"sources[{idx}] 缺失必要字段: '{k}'"
        if not (s["url"].startswith("http://") or s["url"].startswith("https://")):
            return False, [], f"sources[{idx}] url 必须以 http:// 或 https:// 开头: {s['url']}"
        validated.append(s)

    return True, validated, ""

def parse_and_validate_facts(facts_input, valid_source_ids: set) -> tuple[bool, list, str]:
    """
    严格验证事实：必须为显式包含 fact_id, statement, source_ids 的结构化列表。
    严禁将纯文本自动绑定到单一 source_id！
    """
    if not facts_input:
        return False, [], "verified_facts 为空"

    if isinstance(facts_input, str):
        facts_input_str = facts_input.strip()
        # 尝试解析为 JSON
        if facts_input_str.startswith("[") or facts_input_str.startswith("{"):
            try:
                facts_input = json.loads(facts_input_str)
            except Exception as e:
                return False, [], f"verified_facts JSON 解析失败: {e}"
        else:
            # 纯文本传入 ➔ 严禁自动绑定，必须严格阻断
            return False, [], f"verified_facts 必须为结构化 JSON 列表，禁止传入纯文本字符串 (输入为: '{facts_input_str[:40]}...')"

    if isinstance(facts_input, dict):
        facts_input = [facts_input]

    if not isinstance(facts_input, list) or len(facts_input) == 0:
        return False, [], "verified_facts 必须为非空结构化列表"

    validated = []
    for idx, f in enumerate(facts_input, 1):
        if not isinstance(f, dict):
            return False, [], f"facts[{idx}] 必须为结构化字典包含 fact_id, statement, source_ids"
        stmt = str(f.get("statement", "")).strip()
        if not stmt:
            return False, [], f"facts[{idx}] 缺少 statement"
        sids = f.get("source_ids", [])
        if not isinstance(sids, list) or len(sids) == 0:
            return False, [], f"facts[{idx}] (statement: '{stmt[:20]}...') 未关联任何 source_id (source_ids 为空)"
        for sid in sids:
            if sid not in valid_source_ids:
                return False, [], f"facts[{idx}] 关联的 source_id '{sid}' 在 sources 中不存在"
        validated.append({
            "fact_id": f.get("fact_id", f"F{idx}"),
            "statement": stmt,
            "source_ids": sids
        })

    return True, validated, ""

def generate_standard_answer(
    topic: str,
    domain: str = "商业增长与个人IP",
    audience: str = "创作者与商业决策者",
    verified_facts=None,
    sources=None,
    strict_evidence: bool = False
) -> dict:
    """
    执行带严密双重证据门禁与来源结构化校验的历史同构分析
    （注：无外部真实抓取证据对象前，统一标定 source_status="user_supplied_unverified"）
    """
    # 门禁 A: 历史同构匹配检查
    match = find_isomorphism_match(topic, domain)
    if match is None:
        err_msg = f"未能在已核实学术案例库中找到关于「{topic}」的同构历史模型（严禁凭空捏造历史）。"
        if strict_evidence:
            print(f"⛔ [EVIDENCE GATE BLOCKED: historical_isomorphism_missing] {err_msg}", file=sys.stderr)
            sys.exit(1)
        return {
            "status": "insufficient_evidence",
            "evidence_gate": "blocked",
            "gate_failure_reason": "historical_isomorphism_missing",
            "message": err_msg
        }

    # 门禁 B: 当前事件来源门禁检查 (facts 为空 OR sources 为空均必须阻断)
    if not verified_facts:
        err_msg = f"当前事件事实 (verified_facts) 为空。必须同时提供结构化事实与可靠信源。"
        if strict_evidence:
            print(f"⛔ [EVIDENCE GATE BLOCKED: missing_verified_facts] {err_msg}", file=sys.stderr)
            sys.exit(1)
        return {
            "status": "insufficient_evidence",
            "evidence_gate": "blocked",
            "gate_failure_reason": "missing_verified_facts",
            "message": err_msg
        }

    if not sources:
        err_msg = f"当前事件信源 (sources) 为空。必须同时提供结构化事实与可靠信源。"
        if strict_evidence:
            print(f"⛔ [EVIDENCE GATE BLOCKED: missing_sources] {err_msg}", file=sys.stderr)
            sys.exit(1)
        return {
            "status": "insufficient_evidence",
            "evidence_gate": "blocked",
            "gate_failure_reason": "missing_sources",
            "message": err_msg
        }

    # 结构化校验 sources
    s_ok, valid_sources, s_err = parse_and_validate_sources(sources)
    if not s_ok:
        err_msg = f"信源结构化校验失败: {s_err}"
        if strict_evidence:
            print(f"⛔ [EVIDENCE GATE BLOCKED: invalid_sources_format] {err_msg}", file=sys.stderr)
            sys.exit(1)
        return {
            "status": "insufficient_evidence",
            "evidence_gate": "blocked",
            "gate_failure_reason": "invalid_sources_format",
            "message": err_msg
        }

    valid_sids = {s["source_id"] for s in valid_sources}

    # 结构化校验 facts
    f_ok, valid_facts, f_err = parse_and_validate_facts(verified_facts, valid_sids)
    if not f_ok:
        err_msg = f"事实关联校验失败: {f_err}"
        if strict_evidence:
            print(f"⛔ [EVIDENCE GATE BLOCKED: facts_link_failure] {err_msg}", file=sys.stderr)
            sys.exit(1)
        return {
            "status": "insufficient_evidence",
            "evidence_gate": "blocked",
            "gate_failure_reason": "facts_link_failure",
            "message": err_msg
        }

    # 真实核验状态标定：当前无独立抓取证据对象，恒定标定为用户提供未核验
    source_status = "user_supplied_unverified"
    source_status_desc = "用户提供事实与信源（未经联网核验）"

    # 构建输出
    acad = match["academic_citation"]
    pos = match["positive_historical_case"]
    neg = match["negative_historical_case"]

    facts_summary = "；".join([f"[{f['fact_id']}] {f['statement']} (关联信源: {', '.join(f['source_ids'])})" for f in valid_facts])

    result = {
        "status": "success",
        "evidence_gate": "passed",
        "topic": topic,
        "domain": domain,
        "target_audience": audience,
        "evidence_audit": {
            "source_status": source_status,
            "source_status_description": source_status_desc,
            "structure_integrity": "complete_and_verified",
            "facts_and_sources_linkage": "complete_and_verified",
            "validated_sources_count": len(valid_sources),
            "validated_facts_count": len(valid_facts),
            "sources": valid_sources,
            "facts": valid_facts
        },
        "isomorphism_match": {
            "archetype_name": match["archetype_name"],
            "underlying_theory": match["theory_name"],
            "primary_academic_citation": {
                "author": acad["author"],
                "title": acad["title"],
                "year": acad["year"],
                "publisher": acad.get("publisher", ""),
                "identifier": acad["identifier"],
                "full_citation": f"{acad['author']} ({acad['year']}) 《{acad['title']}》, {acad['identifier']}"
            },
            "positive_case": {
                "entity": pos["entity"],
                "summary": pos["fact_summary"],
                "citation": f"{pos['citation']['author']} ({pos['citation']['year']}) 《{pos['citation']['title']}》, {pos['citation']['identifier']}"
            },
            "negative_case": {
                "entity": neg["entity"],
                "summary": neg["fact_summary"],
                "citation": f"{neg['citation']['author']} ({neg['citation']['year']}) 《{neg['citation']['title']}》, {neg['citation']['identifier']}"
            },
            "boundary_conditions": match["boundary_conditions"]
        },
        "three_layer_breakdown": {
            "layer_1_discarded_gossip": f"关于「{topic}」的道听途说与未经结构化信源印证的八卦动机（已物理剔除，仅采信提供的 {len(valid_sources)} 个结构化信源）",
            "layer_2_public_core_anxiety": f"公众在【{domain}】层面的核心困惑：在巨大诱惑与争议面前，如何权衡短期流量与长期声誉资本？",
            "layer_3_professional_increment": f"基于【{match['theory_name']}】，阐明「{match['boundary_conditions']}」"
        },
        "video_archetype_8_stages": {
            "stage_1_question_title": f"《谈谈【{topic}】：为什么顶级套利者的路，普通创作者千万不能走？》",
            "stage_2_hook_3s": f"“很多人看【{topic}】都在看热闹，但在商业逻辑里，这本质上是一场关于‘{match['archetype_name']}’的经典博弈。”",
            "stage_3_fact_premise": f"基于{source_status_desc}：{facts_summary[:120]}...",
            "stage_4_theory_explanation": f"引入【{match['theory_name']}】({acad['author']}, {acad['year']})：解释为什么不同商业模式承受声誉风险的能力完全不同。",
            "stage_5_case_comparison": f"对比真实历史案例：正例【{pos['entity']}】 vs 反例【{neg['entity']}】({neg['citation']['identifier']})。",
            "stage_6_actionable_advice": f"普通创作者与决策者的最小行动铁律：{match['boundary_conditions']}",
            "stage_7_verification_metric": "设定检验标准：衡量未来 3~6 个月内在无公关造势情况下，目标客群的自发复购与转介绍率。",
            "stage_8_business_anchor": f"“商业的终局拼的是资产复利。关注我，用经得起检验的底层规律拆解商业现象。”"
        }
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="基于已核验事实的历史案例类比建议器 (dbs-standard-answer v2.3)")
    parser.add_argument("--topic", type=str, default="孙宇晨的注意力经济与争议", help="热点事件主题")
    parser.add_argument("--domain", type=str, default="个人IP与商业增长", help="博主专业领域")
    parser.add_argument("--audience", type=str, default="创作者与商业决策者", help="目标受众")
    parser.add_argument("--facts-json", type=str, default="", help="结构化事实 JSON 列表")
    parser.add_argument("--sources-json", type=str, default="", help="结构化信源 JSON 列表")
    parser.add_argument("--strict-evidence", action="store_true", help="启用严格证据门禁")

    args = parser.parse_args()

    res = generate_standard_answer(
        args.topic,
        args.domain,
        args.audience,
        verified_facts=args.facts_json,
        sources=args.sources_json,
        strict_evidence=args.strict_evidence
    )

    if res["status"] == "insufficient_evidence":
        print(f"\n⛔ [EVIDENCE GATE BLOCKED] {res['message']}")
        sys.exit(1)

    print("\n=================================================================")
    print(f"🏛️ 【历史案例类比与专业立论建议报告】: {args.topic}")
    print("=================================================================")
    print(f"🔒 信源核验状态: {res['evidence_audit']['source_status']} ({res['evidence_audit']['source_status_description']})")
    print(f"🎯 理论模型: {res['isomorphism_match']['underlying_theory']}")
    print(f"📚 核心文献引用: {res['isomorphism_match']['primary_academic_citation']['full_citation']}")
    print(f"⚖️ 结构原型: {res['isomorphism_match']['archetype_name']}\n")

    pos = res["isomorphism_match"]["positive_case"]
    neg = res["isomorphism_match"]["negative_case"]
    print("📖 【历史经核实案例对比 (带四要素出处)】:")
    print(f"  • ✅ 历史正例: {pos['entity']}")
    print(f"       实证总结: {pos['summary']}")
    print(f"       权威出处: {pos['citation']}")
    print(f"  • ❌ 历史反例: {neg['entity']}")
    print(f"       实证总结: {neg['summary']}")
    print(f"       权威出处: {neg['citation']}\n")

    print("🎬 【八段式短视频原型脚本】:")
    for k, v in res["video_archetype_8_stages"].items():
        print(f"  [{k}] {v}")
    print("=================================================================\n")

if __name__ == "__main__":
    main()
