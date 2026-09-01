# -*- coding: utf-8 -*-
"""
同行文案字数分段与句型结构提炼器 (Competitor Text Segmenter & Skeleton Extractor v2.1)
---------------------------------------------------------------------------------------
核心算法与定位说明：
1. 算法机制：本工具采用基于标点分句与字数占比（前15%、15~45%、45~80%、80~100%）的【机械比例分段法】；
2. 局限性与定性边界：本工具提炼的是字数分布节奏与首尾句型，【不包含深度语义级叙事心理转折点识别】；
3. 纯净机制骨架：提取输入文本中的字数结构与高频实体槽位，供创作者作为篇幅节奏参考。
"""

import sys, os, json, re, argparse
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def deconstruct_text(raw_text: str, speaking_rate_cpm: int = 220) -> dict:
    cleaned_text = raw_text.strip()
    if not cleaned_text:
        return {
            "status": "error",
            "message": "输入文案为空，无法提炼结构"
        }

    # 1. 真实分句
    raw_sentences = [s.strip() for s in re.split(r"[。！？!?\n]+", cleaned_text) if len(s.strip()) >= 2]
    total_chars = len(cleaned_text)
    total_est_seconds = max(5, int((total_chars / speaking_rate_cpm) * 60))

    first_sentence = raw_sentences[0] if raw_sentences else cleaned_text[:30]

    # 启发式首句特征提取
    hook_characteristics = []
    if any(k in first_sentence for k in ["为什么", "怎么", "到底", "秘密", "如何"]):
        hook_characteristics.append("疑问好奇句式")
    if any(k in first_sentence for k in ["越", "却", "但是", "反倒", "其实不是"]):
        hook_characteristics.append("反常识对立句式")
    if any(k in first_sentence for k in ["千万别", "陷阱", "吃亏", "毁掉", "后悔"]):
        hook_characteristics.append("警示防损句式")
    if any(k in first_sentence for k in ["女人", "妈妈", "职场", "30岁", "50岁", "创业者"]):
        hook_characteristics.append("特定人群称谓")
    if not hook_characteristics:
        hook_characteristics.append("陈述引入句式")

    # 2. 按字数与句子比例进行机械四段切分 (15%, 45%, 80%, 100%)
    cut_1 = max(1, int(len(raw_sentences) * 0.15))
    cut_2 = max(cut_1 + 1, int(len(raw_sentences) * 0.45))
    cut_3 = max(cut_2 + 1, int(len(raw_sentences) * 0.80))

    st1_sents = raw_sentences[:cut_1]
    st2_sents = raw_sentences[cut_1:cut_2]
    st3_sents = raw_sentences[cut_2:cut_3]
    st4_sents = raw_sentences[cut_3:]

    st1_chars = sum(len(s) for s in st1_sents)
    st2_chars = sum(len(s) for s in st2_sents)
    st3_chars = sum(len(s) for s in st3_sents)
    st4_chars = sum(len(s) for s in st4_sents)

    t_sec_1 = max(3, int((st1_chars / speaking_rate_cpm) * 60))
    t_sec_2 = t_sec_1 + max(5, int((st2_chars / speaking_rate_cpm) * 60))
    t_sec_3 = t_sec_2 + max(8, int((st3_chars / speaking_rate_cpm) * 60))
    t_sec_4 = total_est_seconds

    def fmt_time(sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    mechanical_stages = [
        {
            "segment_name": "第 1 段 · 开篇切入区间 (按前15%字数机械切分)",
            "time_range": f"00:00 ~ {fmt_time(t_sec_1)}",
            "char_count": st1_chars,
            "actual_snippets": " / ".join(st1_sents)
        },
        {
            "segment_name": "第 2 段 · 前中段展开区间 (按15%~45%字数机械切分)",
            "time_range": f"{fmt_time(t_sec_1)} ~ {fmt_time(t_sec_2)}",
            "char_count": st2_chars,
            "actual_snippets": " / ".join(st2_sents[:3]) + ("..." if len(st2_sents) > 3 else "")
        },
        {
            "segment_name": "第 3 段 · 后中段主体区间 (按45%~80%字数机械切分)",
            "time_range": f"{fmt_time(t_sec_2)} ~ {fmt_time(t_sec_3)}",
            "char_count": st3_chars,
            "actual_snippets": " / ".join(st3_sents[:3]) + ("..." if len(st3_sents) > 3 else "")
        },
        {
            "segment_name": "第 4 段 · 收尾收拢区间 (按80%~100%字数机械切分)",
            "time_range": f"{fmt_time(t_sec_3)} ~ {fmt_time(t_sec_4)}",
            "char_count": st4_chars,
            "actual_snippets": " / ".join(st4_sents)
        }
    ]

    reusable_blueprint = (
        f"【首段·引入】{first_sentence} ➔ 句型骨架：在{{场景}}里，越是{{习惯性付出}}，为什么越{{意想不到的结果}}？\n"
        f"【二段·展开】(约 {st2_chars} 字) ➔ 铺垫 2~3 个关于{{主题对象}}的生活细节。\n"
        f"【三段·主体】(约 {st3_chars} 字) ➔ 指出传统{{旧观念}}的局限，交付新的{{核心认知}}。\n"
        f"【末段·收尾】(约 {st4_chars} 字) ➔ 行动建议 + 互动收尾。"
    )

    return {
        "status": "success",
        "algorithm_notice": "本分析基于字数与分句比例机械分段，不宣称识别语义级叙事心理转折",
        "total_characters": total_chars,
        "total_sentences": len(raw_sentences),
        "estimated_duration": fmt_time(total_est_seconds),
        "first_sentence_analysis": {
            "sentence": first_sentence,
            "heuristic_patterns": hook_characteristics
        },
        "proportional_segments": mechanical_stages,
        "reusable_blueprint": reusable_blueprint
    }

def main():
    parser = argparse.ArgumentParser(description="同行文案字数分段与句型结构提炼器 (v2.1)")
    parser.add_argument("--text", type=str, default="女人退休后，为什么越勤劳越不讨喜？很多母亲为儿女操持了一辈子，最后却换来嫌弃。做母亲必须有清晰的边界感。学会放手，把爱还给自己，老后才能从容自立。", help="同行文案文本")
    args = parser.parse_args()

    res = deconstruct_text(args.text)
    print("\n=================================================================")
    print("🦴 【同行文案字数分段与句型结构提炼 (机械比例分段)】")
    print("=================================================================")
    print(f"ℹ️ 说明: {res['algorithm_notice']}")
    print(f"· 总字数: {res['total_characters']} 字 | 句子总数: {res['total_sentences']} 句 | 预估时长: {res['estimated_duration']}")
    print(f"· 开篇首句: 《{res['first_sentence_analysis']['sentence']}》")
    print(f"· 句式特征: {', '.join(res['first_sentence_analysis']['heuristic_patterns'])}\n")

    print("⏱️ 【按字数比例机械切分的四段分布】:")
    for seg in res["proportional_segments"]:
        print(f"  • [{seg['segment_name']}] ({seg['time_range']}，{seg['char_count']}字)")
        print(f"       包含片段: {seg['actual_snippets']}")

    print("\n📦 【提炼的句型骨架参考】:")
    print(res["reusable_blueprint"])
    print("=================================================================\n")

if __name__ == "__main__":
    main()
