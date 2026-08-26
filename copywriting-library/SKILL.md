---
name: copywriting-library
description: 爆款图书带货文案素材库与智能创作引擎。从微信读书读者书评采样出发，提取真实痛点(pain)、具象场景(scene)与认知觉醒(belief)，输出双轨口播文案（深度带货款12m+爆款流量款4m）、动作级分镜与对标头部大号（老渔吖/豆包读书）的四平台发布文案，并支持同步至飞书多维表格看板。
---

# 📚 图书带货文案素材库与智能创作引擎

从微信读书读者深度洞察出发，实现**“前置真实数据支撑 ➔ 双轨口播创作 ➔ 动作级分镜 ➔ 四平台矩阵文案 ➔ 飞书多维表格沉淀”**的完整创作流水线。

---

## 🔄 标准创作流水线

```mermaid
graph TD
    A["📖 输入书名 / 飞书选题"] --> B["🔍 weread_fetcher.py<br/>(微信读书书评采样 6 维提取)"]
    B --> C["📝 撰写双轨口播稿<br/>(深度带货款 12m + 爆款流量款 4m)"]
    C --> D["🎨 visual_action_storyboard<br/>(生成动作级三景深手绘分镜)"]
    D --> E["📱 生成对标头部大号四平台文案<br/>(微信视频号 + 快手 + 抖音 + 小红书)"]
    E --> F["📊 lark_base_sync.py<br/>(自动打包同步至飞书多维表格看板)"]
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
