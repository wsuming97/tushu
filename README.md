# 🎨 AI 内容创作技能套件 (AI Content Creator Suite)

> 面向 **微信视频号 / 快手 / 抖音 / 小红书 / 微信公众号** 的全流程 AI 视觉与音视频商业内容生产工作流工具包。  
> 严格践行 **1.微信读书调研 ➔ 5.飞书看板建档 ➔ 4.合规风控预审 ➔ 3.6维质检打分 ➔ 2.终稿文案分镜 ➔ 6.视听声画出片** 标准商业流水线。

---

## 📦 核心技能矩阵 (Modules)

```text
.
├── 📚 copywriting-library/          # 技能 1：文案素材库（双轨框架、视觉指南、分主题口播文案库、飞书同步）
├── ✍️ copywriting-verify-optimize/   # 技能 2：商业文案 6 维质检评分、事实核验与转化优化
├── 🛡️ publish-precheck/             # 技能 3：国内自媒体发布前风控自审与保意违禁词修复
├── 🎴 ai-quote-card-maker/          # 技能 4：爆款金句卡片 & 贴图故事号全套生成
├── 🎬 srt-whiteboard-animation/     # 技能 5：SRT 字幕驱动的 60fps 白板流式手绘动画引擎
├── 🎙️ tts-voiceover/                # 技能 6：剪映/火山引擎 VIP 播客级磁性配音与声画合成 (0.95x 黄金速)
└── 🎞️ native-subtitle-quote-image/  # 技能 7：原生字幕截帧与社交长图拼图工具
```

---

## 🔄 标准生产流水线 (1.5.4.3.2.6 闭环)

```mermaid
graph TD
    S1["1. 微信读书 6 维读者洞察 (weread_fetcher.py)<br/>• 采样 20~40 条真实长评，提取 pain/scene/belief"] --> S5["5. 飞书多维表格建档 (lark_base_sync.py)<br/>• 第一时间建档入看板，团队可视化追踪"]
    S5 --> S4["4. 平台合规风控预审 (publish-precheck/scan.py)<br/>• 扫描广告法极值词/敏感词，自动保意修复"]
    S4 --> S3["3. 6 维商业文案质检 (copywriting-verify-optimize)<br/>• 事实/共鸣/转化/留存/匹配/风控打分 (≥85分放行)"]
    S3 --> S2["2. 定稿双轨文案与动作分镜 (four_tier_conversion & storyboard)<br/>• 深度带货款 12m + 爆款流量款 4m + 老渔吖同款四平台文案"]
    S2 --> S6["6. 声画合成与白板手绘成片 (tts-voiceover & srt-whiteboard)<br/>• 剪映磁性男声 0.95x 黄金速 + 60fps 暖米黄底流式手绘成片"]
```

---

## 🛠️ 模块详解 (Module Details)

### 1. 📚 [文案素材库与创作引擎 (`copywriting-library`)](./copywriting-library/)
- **微信读书 6 维读者洞察**：采样 20~40 条读者真实书评，提炼真实困境(`pain`)、生活场景(`scene`)与认知觉醒(`belief`)。
- **四层递进带货法**：严格按照 **共情 ➔ 亏欠 ➔ 痛点 ➔ 出口** 四层转化逻辑，注入生活毛刺细节，拒绝空洞排比句。
- **飞书多维表格实时同步**：支持全自动双向同步看板，带货/流量双轨分离。

### 2. ✍️ [文案审核与优化 (`copywriting-verify-optimize`)](./copywriting-verify-optimize/)
- **6 维商业质检体系**：事实可信度(25分)、共鸣与懂感(20分)、转化与逻辑(20分)、留存与互动(15分)、产品匹配(10分)、风控合规(10分)。
- 严格执行 ≥85 分放行门槛，杜绝虚假恐吓营销与编造家庭矛盾。

### 3. 🛡️ [发布风控预审 (`publish-precheck`)](./publish-precheck/)
- **多平台自审引擎**：覆盖微信视频号、抖音、快手、小红书最新违规限流规则。
- **保意精准替换**：对医疗绝对化用语、夸大宣传词、违禁词进行智能降级与同义保意修复。

### 4. 🎴 [AI 金句/故事卡片生成器 (`ai-quote-card-maker`)](./ai-quote-card-maker/)
- **全屏意境金句卡片**：星空/落日/山川唯美背景 + 优雅毛玻璃排版 + 电影台词中英双语设计。
- **贴图故事号矩阵**：单卡片故事贴图 + 深度公众号配套长文 TXT + 流量标签矩阵。

### 5. 🎬 [SRT 白板手绘动画引擎 (`srt-whiteboard-animation`)](./srt-whiteboard-animation/)
- **流式连续笔迹画法**：起笔墨线骨架追踪（`ink`） → 区域平涂上色（`color`），真实还原画手笔触。
- **叙事遮罩编排**：按叙事语义依次逐区揭示，支持 `protectedRegions` 重叠保护与持久画布。
- **可视化预览台**：内置 `preview.html` 本地 Web 预览台，支持拖拽标注框、时序微调与声画实时对齐。

### 6. 🎙️ [TTS 播客级配音与成片合成 (`tts-voiceover`)](./tts-voiceover/)
- **多引擎支持**：接入 **火山引擎（豆包语音）Seed-TTS 2.0 / Agent Plan**，全面支持剪映 VIP 官方同款【磁性男声】（`zh_male_m191_uranus_bigtts`）。
- **微沉浸调优**：内置 **0.95x 黄金微沉浸语速** 与 0.4s 开场静谧入场垫音，彻底告别急促与拖沓。
- **广播级响度**：内置 EBU R128 (`loudnorm=I=-16:TP=-1.5:LRA=11`) 动态响度标准化。

### 7. 🎞️ [原生字幕长图拼接 (`native-subtitle-quote-image`)](./native-subtitle-quote-image/)
- 将内嵌字幕视频按字幕精确帧裁切并拼接为社交平台长图，保留真实原片质感。

---

## 🚀 快速上手 (Quick Start)

### 1. 环境准备
确保已安装 Python 3.10+ 及 ffmpeg：

```bash
pip install requests pillow numpy opencv-python pydub imageio-ffmpeg python-dotenv
```

### 2. 运行一键飞书同步测试
```bash
python copywriting-library/scripts/lark_base_sync.py --topic_dir "./copywriting-library/topics/一个人的老后/"
```

---

## 📄 开源许可证 (License)
本项目基于 [MIT License](./LICENSE) 开源。
