# -*- coding: utf-8 -*-
"""
爆款标题 10 维启发式评分与 A/B 选拔器 (Viral Title Heuristic Evaluator v2.0)
-------------------------------------------------------------------------
核心治理规范：
1. 完整实现 10 个独立评估维度与精确权重计算（满分 100 分）；
2. 严禁无实测依据的 CTR 预测，严格定性为“启发式综合质量评分 (Heuristic Quality Score)”；
3. 输出 10 维细分得分明细、流派分类与合规建议。
"""

import sys, os, json, argparse, re
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 10 维词库与特征规则
CONFLICT_KEYWORDS = ["为什么", "反而", "越", "却", "但是", "真相", "不是", "而是", "死于", "偏偏"]
CURIOSITY_KEYWORDS = ["怎么", "秘密", "这几个", "竟然", "到底", "千万别", "什么样", "背后", "其实"]
LOSS_AVERSION_KEYWORDS = ["陷阱", "吃亏", "后悔", "毁掉", "代价", "买单", "被坑", "避坑", "防骗", "致命"]
EMOTION_KEYWORDS = ["委屈", "心酸", "崩溃", "扎心", "体面", "通透", "清醒", "底气", "孤独", "从容"]
TARGET_AUDIENCE_KEYWORDS = ["女人", "妈妈", "中年", "退休", "职场", "老人", "儿女", "父母", "年轻人", "夫妻"]
VALUE_PROMISE_KEYWORDS = ["指南", "心法", "法则", "方法", "清单", "真相", "建议", "原则", "智慧", "底气"]
COMPLIANCE_RISK_KEYWORDS = ["第一", "最好", "绝对", "首个", "独家", "包治", "稳赚", "必火", "神效", "百分之百"]

def evaluate_single_title(title: str, platform: str = "channels") -> dict:
    t_clean = title.strip().strip("《》\"'“”")
    t_len = len(t_clean)
    breakdown = {}

    # 1. 冲突对立度 (Weight: 15)
    c_count = sum(1 for kw in CONFLICT_KEYWORDS if kw in t_clean)
    score_conflict = min(15.0, c_count * 7.5)
    breakdown["1_冲突对立度"] = round(score_conflict, 1)

    # 2. 悬念好奇心 (Weight: 15)
    cu_count = sum(1 for kw in CURIOSITY_KEYWORDS if kw in t_clean)
    score_curiosity = min(15.0, cu_count * 7.5)
    breakdown["2_悬念好奇心"] = round(score_curiosity, 1)

    # 3. 损失厌恶感 (Weight: 10)
    la_count = sum(1 for kw in LOSS_AVERSION_KEYWORDS if kw in t_clean)
    score_loss = min(10.0, la_count * 5.0)
    breakdown["3_损失厌恶感"] = round(score_loss, 1)

    # 4. 情绪极化值 (Weight: 10)
    em_count = sum(1 for kw in EMOTION_KEYWORDS if kw in t_clean)
    score_emotion = min(10.0, em_count * 5.0)
    breakdown["4_情绪极化值"] = round(score_emotion, 1)

    # 5. 具象人群锚定 (Weight: 10)
    ta_count = sum(1 for kw in TARGET_AUDIENCE_KEYWORDS if kw in t_clean)
    score_audience = min(10.0, ta_count * 5.0)
    breakdown["5_具象人群锚定"] = round(score_audience, 1)

    # 6. 数字化与具象感 (Weight: 10)
    has_digits = bool(re.search(r"\d+", t_clean))
    has_specific_nouns = bool(re.search(r"[房钱车伴病]", t_clean))
    score_digits = (6.0 if has_digits else 2.0) + (4.0 if has_specific_nouns else 1.0)
    score_digits = min(10.0, score_digits)
    breakdown["6_数字化具象感"] = round(score_digits, 1)

    # 7. 平台载体适配 (Weight: 10)
    # channels/video: 适合较完整有深度反差的句子 (16~30字)
    # xiaohongshu: 适合短促大字+叹号
    score_platform = 7.0
    if platform == "channels" and 15 <= t_len <= 32:
        score_platform = 10.0
    elif platform == "xiaohongshu" and (t_len <= 20 or "！" in t_clean or "!" in t_clean):
        score_platform = 10.0
    breakdown["7_平台载体适配"] = round(score_platform, 1)

    # 8. 手机单屏字数控制 (Weight: 10) - 16~28 字呈现 2 行最佳
    if 16 <= t_len <= 28:
        score_length = 10.0
    elif 12 <= t_len < 16 or 28 < t_len <= 34:
        score_length = 7.0
    elif 8 <= t_len < 12 or 34 < t_len <= 40:
        score_length = 4.0
    else:
        score_length = 2.0
    breakdown["8_手机单屏字数控制"] = round(score_length, 1)

    # 9. 承诺价值明确度 (Weight: 5)
    val_count = sum(1 for kw in VALUE_PROMISE_KEYWORDS if kw in t_clean)
    score_value = min(5.0, val_count * 2.5 + (2.0 if "?" in t_clean or "？" in t_clean else 0.0))
    breakdown["9_承诺价值明确度"] = round(score_value, 1)

    # 10. 广告法与合规安全 (Weight: 5)
    viol_count = sum(1 for kw in COMPLIANCE_RISK_KEYWORDS if kw in t_clean)
    score_compliance = max(0.0, 5.0 - viol_count * 5.0)
    breakdown["10_合规安全评分"] = round(score_compliance, 1)

    total_heuristic_score = round(sum(breakdown.values()), 1)

    # 流派分类推断
    genre = "综合叙事型"
    if score_conflict >= 10.0:
        genre = "颠覆常识/冲突型"
    elif score_loss >= 5.0:
        genre = "避坑防损/警示型"
    elif score_emotion >= 5.0 or score_audience >= 5.0:
        genre = "知己温情/共鸣型"
    elif score_curiosity >= 10.0:
        genre = "悬念提问/探索型"

    return {
        "title": t_clean,
        "character_length": t_len,
        "heuristic_total_score": total_heuristic_score,
        "genre": genre,
        "ten_dimensions_breakdown": breakdown,
        "compliance_status": "✅ 合规" if score_compliance >= 5.0 else "⚠️ 包含疑似违禁词",
        "evaluation_recommendation": (
            "🔥 强烈推荐作为主推标题 (启发式评分 ≥ 85)" if total_heuristic_score >= 85
            else ("⚡ 推荐用于 A/B 组对比测试 (启发式评分 70~84)" if total_heuristic_score >= 70
                  else "⚠️ 建议增加冲突或具象人群修饰后重新评估")
        )
    }

def main():
    parser = argparse.ArgumentParser(description="爆款标题 10 维启发式评分与 A/B 选拔器 (v2.0)")
    parser.add_argument("--titles", nargs="+", default=[
        "女人退休后，为什么越勤劳越不讨喜？",
        "给儿女买房前，千万别踩这3个致命的养老陷阱",
        "退休后如何优雅变老",
        "大多数婚姻不是死于无性，而是死于无话"
    ], help="候选标题列表")
    parser.add_argument("--platform", type=str, default="channels", choices=["channels", "xiaohongshu", "douyin"], help="发布平台")

    args = parser.parse_args()
    results = [evaluate_single_title(t, args.platform) for t in args.titles]
    results.sort(key=lambda x: x["heuristic_total_score"], reverse=True)

    print("\n=================================================================")
    print(f"📊 【爆款标题 10 维启发式打分与选拔报告】(平台: {args.platform})")
    print("=================================================================")

    for idx, r in enumerate(results, 1):
        print(f"[{idx}] 启发式总分: {r['heuristic_total_score']} / 100 分 | 字数: {r['character_length']} 字 | 流派: {r['genre']}")
        print(f"    标题: 《{r['title']}》 ({r['compliance_status']})")
        print(f"    评级建议: {r['evaluation_recommendation']}")
        print("    10 维细分得分明细:")
        for dim, sc in r["ten_dimensions_breakdown"].items():
            print(f"      • {dim}: {sc}分")
        print()
    print("=================================================================\n")

if __name__ == "__main__":
    main()
