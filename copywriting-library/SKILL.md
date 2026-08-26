---
name: copywriting-library
description: 爆款图书带货文案素材库与智能创作引擎。从微信读书读者书评采样出发，按 1.5.4.3.2.6 标准业务流水线（调研➔飞书建档➔合规预审➔6维质检➔终稿分镜➔视听出片）全自动生产双轨口播文案（深度带货款12m+爆款流量款4m）、动作级分镜与对标头部大号（老渔吖/豆包读书）的四平台发布文案，并实时双向同步至飞书多维表格看板。
---

# 📚 图书带货文案素材库与智能创作引擎

从微信读书读者深度洞察出发，实现**“1.微信读书调研 ➔ 5.飞书看板建档 ➔ 4.合规风控预审 ➔ 3.6维质检打分 ➔ 2.终稿文案分镜 ➔ 6.声画合成出片”**的完整全自动商业生产流水线。

---

## 🔄 标准生产流水线 (1.5.4.3.2.6 闭环)

```mermaid
graph TD
    S1["1. 微信读书 6 维读者洞察 (weread_fetcher.py)<br/>• 采样 20~40 条真实长评，提取 pain/scene/belief"] --> S5["5. 飞书多维表格建档 (lark_base_sync.py)<br/>• 第一时间建档入看板，团队可视化追踪"]
    S5 --> S4["4. 平台合规风控预审 (publish-precheck/scan.py)<br/>• 扫描广告法极值词/敏感词，自动保意修复"]
    S4 --> S3["3. 6 维商业文案质检 (copywriting-verify-optimize)<br/>• 事实/共鸣/转化/留存/匹配/风控打分 (≥85分放行)"]
    S3 --> S2["2. 定稿双轨文案与动作分镜 (visual_action_storyboard)<br/>• 深度带货款 12m + 爆款流量款 4m + 老渔吖同款四平台文案"]
    S2 --> S6["6. 声画合成与白板手绘成片 (tts-voiceover & srt-whiteboard)<br/>• 剪映磁性男声 0.90x + 60fps 暖米黄底流式手绘成片"]
```

---

## 🛠️ 核心方法论与脚本

1. **微信读书读者洞察方法论**：`frameworks/weread_reader_insights.md`
   - 提取 6 大核心维度：`pain`（真实困境）、`scene`（具象场景）、`belief`（认知转变）、`language`（读者大白话）、`objection`（疑虑）、`outcome`（读后获得）。
2. **动作级视觉分镜标准**：`frameworks/visual_action_storyboard.md`
   - 拒绝抽象词，强制画面必须包含可被画出来的“具体动作与生活道具”。
3. **前置书评提取工具**：`scripts/weread_fetcher.py`
   - 运行：`python scripts/weread_fetcher.py --book "书名" --output "./topics/书名/"`
4. **飞书多维表格同步工具**：`scripts/lark_base_sync.py`
   - 运行：`python scripts/lark_base_sync.py --topic_dir "./topics/书名/"`

---

## 📦 双轨文案交付规范

每个主题产出标准 4 件套：
- `xx_深度带货口播稿.md`：11~13分钟，五阶递进，最后一幕手捧正版原著强促单；
- `xx_流量口播稿.md`：3~5分钟，10句清醒大实话密集金句，极高完播率；
- `xx_带货发布文案.md`：对标“我是老渔吖/豆包读书”同款 120~180 字真诚书评；
- `xx_流量发布文案.md`：短平快爆款文案，引导评论区互动与转发。
