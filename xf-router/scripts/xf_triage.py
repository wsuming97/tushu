# -*- coding: utf-8 -*-
"""
商业全案意图分发路由器 (/xf Triage Recommender) v2.0
---------------------------------------------------
支持 15 大技能全链路智能调度：
1. dbs-standard-answer (热点立论/历史同构)
2. competitor-deconstruct (同行爆款拆解)
3. viral-title-ab-tester (爆款标题 10 维选拔)
4. cover-visual-prompt (封面生图 Prompt 蒸馏)
5. smart-comment-booster (评论区神评与私域冷启动)
6. weread-skills (微信读书官方数据)
7. copywriting-library (图书带货素材库)
8. copywriting-verify-optimize (商业质检)
9. mimeng-style-skill (观点文机制)
10. publish-precheck (平台风控)
11. srt-whiteboard-animation (白板手绘动画)
12. tts-voiceover (情感配音成片)
13. ai-quote-card-maker (意境金句卡片)
14. native-subtitle-quote-image (原生字幕长图)
15. lark_base_sync (飞书多维看板)
"""

import sys, os, json, re, argparse
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def triage_intent(user_prompt: str) -> dict:
    prompt_lower = user_prompt.lower()

    # 1. 历史同构与热点立论
    if any(k in prompt_lower for k in ["热点", "孙宇晨", "景甜", "争议", "立论", "吃瓜", "名人", "标准答案", "八卦"]):
        return {
            "primary_skill": "dbs-standard-answer",
            "secondary_skills": ["viral-title-ab-tester", "cover-visual-prompt", "smart-comment-booster"],
            "reason": "检测到热点立论与专业 IP 塑造诉求，启用历史同构模型与 8 段式短视频原型流水线。",
            "workflow": [
                "1. 调用 dbs-standard-answer 执行三层信息剥离与历史同构匹配",
                "2. 调用 viral-title-ab-tester 输出 10 维优选爆款标题",
                "3. 调用 cover-visual-prompt 生成 Midjourney/即梦生图 Prompt 与大字排版方案",
                "4. 调用 smart-comment-booster 预制评论区置顶首评与引流神评"
            ]
        }

    # 2. 同行爆款拆解
    if any(k in prompt_lower for k in ["对标", "同行", "拆解", "反编译", "抄骨架", "逐字稿"]):
        return {
            "primary_skill": "competitor-deconstruct",
            "secondary_skills": ["mimeng-style-skill", "copywriting-library"],
            "reason": "检测到对标账号或爆款文案拆解诉求，秒级反编译黄金时间轴与槽位模板。",
            "workflow": [
                "1. 调用 competitor-deconstruct 剥离表层文字，提炼纯净机制骨架",
                "2. 调用 mimeng-style-skill 灌入高保真语料二次重写",
                "3. 调用 publish-precheck 确保合规无违禁词"
            ]
        }

    # 3. 标题选拔
    if any(k in prompt_lower for k in ["起标题", "标题", "评估标题", "打分", "ctr", "a/b测试"]):
        return {
            "primary_skill": "viral-title-ab-tester",
            "secondary_skills": ["publish-precheck"],
            "reason": "检测到标题起草或选拔诉求，启用 10 维量化打分模型与 4 大流派优选。",
            "workflow": [
                "1. 调用 viral-title-ab-tester 对候选标题进行量化打分",
                "2. 调用 publish-precheck 检查广告法合规"
            ]
        }

    # 4. 单色/双色印刷与孔版海报 (mono-color)
    if any(k in prompt_lower for k in ["单色", "双色", "孔版", "risograph", "riso", "网点", "zine", "二色", "印刷海报", "单色调", "mono-color"]):
        return {
            "primary_skill": "mono-color",
            "secondary_skills": ["ai-quote-card-maker", "cover-visual-prompt"],
            "reason": "检测到单色/双色出版级印刷海报、孔版印刷 (Risograph) 或网点海报诉求，启用单色/双色墨水限制与大面积留白视觉流水线。",
            "workflow": [
                "1. 调用 mono-color 解析配方 Manifest 并生成高精度 AI 绘画底图 Prompt",
                "2. 获得具有 25%~55% 留白与网点质感的单/双色底图",
                "3. 调用 ai-quote-card-maker 覆盖精确中文字符与作者排版，避免 AI 文字乱码"
            ]
        }

    # 5. 封面与首图
    if any(k in prompt_lower for k in ["封面", "首图", "midjourney", "即梦", "生图", "prompt", "大字排版"]):
        return {
            "primary_skill": "cover-visual-prompt",
            "secondary_skills": ["ai-quote-card-maker"],
            "reason": "检测到视觉封面制作诉求，输出三层景深构图与精准中英文生图 Prompt。",
            "workflow": [
                "1. 调用 cover-visual-prompt 输出 Midjourney / 即梦提示词与大字布局",
                "2. 可选调用 ai-quote-card-maker 渲染毛玻璃金句卡片"
            ]
        }

    # 5. 评论区运营
    if any(k in prompt_lower for k in ["评论区", "神评", "置顶", "冷启动", "互动", "点火"]):
        return {
            "primary_skill": "smart-comment-booster",
            "secondary_skills": ["copywriting-verify-optimize"],
            "reason": "检测到评论区冷启动与完播互动诉求，预制争议点火与私域转化神回复。",
            "workflow": [
                "1. 调用 smart-comment-booster 输出作者置顶首评与正反神评",
                "2. 植入高情商挂车与私域转化钩子"
            ]
        }

    # 6. 图书带货
    if any(k in prompt_lower for k in ["带货", "图书", "书单", "上野千鹤子", "一个人的老后", "被讨厌的勇气"]):
        return {
            "primary_skill": "copywriting-library",
            "secondary_skills": ["weread-skills", "publish-precheck", "tts-voiceover", "cover-visual-prompt"],
            "reason": "检测到图书商业带货全案诉求，启动 1.5.4.3.2.6 全案生产流水线。",
            "workflow": [
                "1. 提取微信读书 6 维真实读者书评",
                "2. 生成双轨口播文案与动作分镜头",
                "3. 合规风控与 6 维质检",
                "4. 配套封面 Prompt 与播客级配音成片"
            ]
        }

    # 7. 观点文机制
    if any(k in prompt_lower for k in ["观点文", "咪蒙", "情绪", "金句", "爆款文章"]):
        return {
            "primary_skill": "mimeng-style-skill",
            "secondary_skills": ["publish-precheck", "viral-title-ab-tester"],
            "reason": "检测到新媒体观点文或情绪机制写作诉求，基于 Phase B 956 篇高保真语料库提供黄金开篇与修辞节奏。",
            "workflow": [
                "1. 提取原子库黄金 Hook",
                "2. 运用多故事网状结构拟定大纲与正文",
                "3. 标题选拔与合规预审"
            ]
        }

    # 默认综合推荐
    return {
        "primary_skill": "dbs-standard-answer",
        "secondary_skills": ["copywriting-library", "mimeng-style-skill"],
        "reason": "输入较为宽泛，建议先使用历史同构模型确立核心立意，再选择具体载体展开创作。",
        "workflow": [
            "1. 明确商业立意与目标受众",
            "2. 选择观点长文或短视频双轨文案",
            "3. 视觉出片与评论区冷启动"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="/xf 商业创作全案意图分发路由器")
    parser.add_argument("intent", nargs="?", default="我想追孙宇晨和景甜最近的热点，立商业IP", help="用户的创作诉求")
    args = parser.parse_args()

    triage = triage_intent(args.intent)

    print("\n=================================================================")
    print(f"🧭 【/xf 全案路线智能规划结果】 (用户输入: \"{args.intent}\")")
    print("=================================================================")
    print(f"🎯 推荐主技能 (Primary):    [{triage['primary_skill']}]")
    print(f"🧩 推荐辅助技能 (Secondary): {triage['secondary_skills']}")
    print(f"💡 推荐决策逻辑:            {triage['reason']}\n")
    print("📋 【全链路标准执行计划】:")
    for step in triage["workflow"]:
        print(f"   {step}")
    print("=================================================================\n")

if __name__ == "__main__":
    main()
