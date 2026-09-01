---
name: xf-router
description: 中文商业内容与全案创作路线规划路由器（Triage Recommender v2.0）。面向新媒体创作者、知识博主与图书带货团队，把真实创作需求、热点选题或卡点交给 /xf，分析意图并给出 15 大专业 Skills 的最佳主辅推荐组合与分步执行计划（本技能只负责路线推荐与指令编排，不代替用户静默执行外部写库或付费操作）。
---

# 商业内容与全案创作路线规划路由器 (/xf Router v2.0)

## 🎯 核心使命 (Mission)
创作者无需记住 15 个底层工具名称。只需输入你的**一句话真实创作诉求、选题或困境**，中枢路由器即可秒级识别创作意图，精准编排主辅技能组合与全流程实施路线。

---

## 🗺️ 15 大专业技能全链路矩阵 (Full Production Matrix)

```
                               ┌────────────────────────────────────────────────────────┐
                               │        总控分发中枢: /xf (商业全案意图路由器)          │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
   ┌───────────────────────┬──────────────────────┬────────┴──────────────┬──────────────────────┬──────────────────────┐
   ▼                       ▼                      ▼                       ▼                      ▼                      ▼
【1. 选题与反编译】       【2. 深度立论与洞察】  【3. 爆款文案创作】     【4. 视觉与封面出片】   【5. 质检与发布风控】  【6. 评论与商业转化】
· competitor-deconstruct  · dbs-standard-answer  · weread-skills         · cover-visual-prompt   · copywriting-verify    · smart-comment-booster
  (拆同行爆款骨架)          (历史同构降维立论)     · copywriting-library   (爆款大字封面Prompt)    · publish-precheck      (预埋神评促完播)
                          · viral-title-ab-tester· mimeng-style-skill    · srt-whiteboard          (100% 平台合规)      · lark_base_sync
                            (10维爆款标题选拔)                             · tts-voiceover                                 (多维表格看板)
                                                                         · ai-quote-card-maker
                                                                         · native-subtitle-quote
```

---

## 💡 典型意图与推荐组合 (Triage Table)

| 用户的真实输入 (User Intent) | 推荐主技能 (Primary) | 推荐辅助技能 (Secondary) | 推荐理由与执行路线 (Workflow) |
| :--- | :--- | :--- | :--- |
| **“我想追名人/商业热点（如孙宇晨/景甜），不想低俗吃瓜，想立专业人设”** | `dbs-standard-answer` | `viral-title-ab-tester` + `cover-visual-prompt` | 历史同构模型 ➔ 三层信息剥离 ➔ 8段式短视频脚本 ➔ 封面与大字方案。 |
| **“看到同行爆款视频，帮我拆解它的底层抓人骨架”** | `competitor-deconstruct` | `mimeng-style-skill` | 秒级剥离表层文字 ➔ 提炼黄金时间轴与槽位模板 ➔ 灌入高保真语料二次创作。 |
| **“帮我评估这 4 个标题哪个点击率更高，或者帮我起 5 个爆款标题”** | `viral-title-ab-tester` | `publish-precheck` | 10 维打分模型优选 ➔ 4 大流派候选 ➔ 平台合规自审。 |
| **“帮我生成孔版印刷海报、双色Risograph插画或单色出版级大字封面”** | `mono-color` | `ai-quote-card-maker` + `cover-visual-prompt` | 严格限制1~2种油墨与25%~55%留白 ➔ 生成Midjourney/即梦底图Prompt ➔ ai-quote-card-maker 精确中文文字覆盖。 |
| **“文案写好了，帮我生成普通封面图提示词和小红书大字排版方案”** | `cover-visual-prompt` | `ai-quote-card-maker` | 三层景深构图 ➔ Midjourney/即梦生图 Prompt ➔ 大字吸睛排版布局。 |
| **“视频刚发出去，帮我做一套评论区置顶神评与带货转化话术”** | `smart-comment-booster` | `copywriting-verify-optimize` | 作者置顶首评 ➔ 正反争议点火神评 ➔ 挂车高情商转化神回复。 |
| **“我想做一本书（如《一个人的老后》）的短视频带货全案”** | `copywriting-library` | `weread-skills` + `publish-precheck` + `tts-voiceover` | 读者书评洞察 ➔ 双轨文案与分镜 ➔ 合规自审 ➔ 播客级配音成片。 |
| **“我想写一篇关于女性自立的爆款观点文”** | `mimeng-style-skill` | `publish-precheck` | 基于 Phase B 956 篇语料库提炼黄金开篇 Hook 与修辞节奏 ➔ 过审合规检查。 |

---

## 💻 命令行调用 (CLI Usage)

```bash
# 智能分析用户诉求并给出推荐路线
python scripts/xf_triage.py "我想做《被讨厌的勇气》带货全案"
```
