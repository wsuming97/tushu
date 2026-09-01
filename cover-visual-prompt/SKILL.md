---
name: cover-visual-prompt
description: 爆款封面与首图提示词蒸馏器（Cover Visual & Prompt Distiller v2.0）。真正基于文案主题（theme）与指定美学风格（style，支持电影商业/治愈插画/极简杂志/赛博科技等），动态提取三层景深视觉主体，生成高质感 Midjourney / 即梦中英文生图 Prompt 与大字排版方案。严禁使用固定单一的静态模具。
---

# 爆款封面与首图提示词蒸馏器 (v2.0)

## 🎯 核心定位 (Core Purpose)
解决新媒体创作者 **“文案极佳但封面没有点击欲、生图提示词缺乏故事性与主体动态性”** 的痛点。
本技能通过语义分析，动态提取与文案主题高度契合的视觉主体、情绪物件与光影环境，输出结构化的三层景深生图 Prompt。

---

## 🎨 支持的 4 大专业美学风格模具 (Style Presets)
1. `cinematic_business`：电影级商业与博弈质感（深藏青/暗炭黑，戏剧性侧逆光）；
2. `healing_illustration`：治愈系手绘水彩插画（温暖米黄底 `#F5EBD7`，柔和漫射光）；
3. `editorial_minimalist`：Kinfolk 极简杂志摄影风（大面积干净留白，柔和影棚光）；
4. `tech_cyberpunk`：赛博科技与未来洞察风（电光青/深紫，虚幻引擎概念渲染）。

---

## 💻 命令行工具 (CLI Usage)

```bash
# 生成商业主题封面提示词
python scripts/generate_cover_prompts.py --theme "商业博弈与投资" --style "cinematic_business"

# 生成治愈系情感主题封面提示词
python scripts/generate_cover_prompts.py --theme "女性从容自立" --style "healing_illustration"
```
