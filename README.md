# 🎨 AI 内容创作技能套件 (AI Content Creator Suite)

> 面向 **微信视频号 / 抖音 / 小红书 / 微信公众号** 的全流程 AI 视觉与音视频内容生产工作流工具包。  
> 包含 **AI 意境金句/故事卡片制作**、**SRT 白板手绘流式动画引擎**、**TTS 播客级配音与成片自动合成**。

---

## 📦 核心技能矩阵 (Modules)

```text
.
├── 🎴 ai-quote-card-maker/          # 技能 1：爆款金句卡片 & 贴图故事号全套生成
├── 🎬 srt-whiteboard-animation/     # 技能 2：SRT 字幕驱动的白板流式手绘动画引擎
├── 🎙️ tts-voiceover/                # 技能 3：火山引擎(豆包语音)播客级配音与声画合成
└── 🎞️ native-subtitle-quote-image/  # 技能 4：原生字幕截帧与社交长图拼图工具
```

---

### 1. 🎴 [AI 金句/故事卡片生成器 (`ai-quote-card-maker`)](./ai-quote-card-maker/)
- **全屏意境金句卡片**：星空/落日/山川唯美背景 + 优雅毛玻璃排版 + 电影台词中英双语设计。
- **贴图故事号矩阵**：单卡片故事贴图 + 深度公众号配套长文 TXT + 流量标签矩阵。
- **设计美学**：多字体排版、自适应字符换行、高质感渐变与噪点质感。

### 2. 🎬 [SRT 白板手绘动画引擎 (`srt-whiteboard-animation`)](./srt-whiteboard-animation/)
- **流式连续笔迹画法**：起笔墨线骨架追踪（`ink`） → 区域平涂上色（`color`），笔迹连贯流动。
- **叙事遮罩编排**：按字幕故事发展依次逐区揭示，支持 `protectedRegions` 重叠保护与持久画布。
- **政史社科全视觉风格库**：内置中国古代史、民国风云、世界近现代、现代社科等 4 大时期自动视觉配方。
- **可视化预览台**：内置 `preview.html` 本地 Web 预览台，支持拖拽标注框、时序微调与声画实时对齐。

### 3. 🎙️ [TTS 播客级配音与成片合成 (`tts-voiceover`)](./tts-voiceover/)
- **多引擎支持**：接入 **火山引擎（豆包语音）Seed-TTS 2.0 / Agent Plan**，支持云舟、小何等高拟真音色。
- **播客级叙事**：整段连贯口播合成，自动消除机械停顿；支持 0.80 深夜电台黄金语速与幕间自然呼吸留白。
- **EBU R128 广播级响度均衡**：内置 `loudnorm` 动态响度标准化，解决多轨音频混音衰减。
- **硬字幕自动压制**：一键烧录高清防遮挡中文字幕，直接导出可发布的成片（`final.mp4`）。

### 4. 🎞️ [原生字幕长图拼接 (`native-subtitle-quote-image`)](./native-subtitle-quote-image/)
- 将内嵌字幕视频按字幕精确帧裁切并拼接为社交平台长图，保留真实原片质感。

---

## 🚀 快速上手 (Quick Start)

### 1. 环境准备
确保已安装 Python 3.10+ 及 ffmpeg：

```bash
# 安装基础依赖
pip install requests pillow numpy opencv-python pydub imageio-ffmpeg python-dotenv
```

### 2. 配置 TTS 密钥 (可选)
复制 `tts-voiceover/.env.example` 为 `.env`，填入你的 API 凭证：

```bash
cp tts-voiceover/.env.example tts-voiceover/.env
# 在 .env 中填入 VOLCANO_API_KEY (或 Agent Plan Key)
```

### 3. 运行示例

#### 运行金句卡片生成：
```bash
python ai-quote-card-maker/scripts/render_quote_card.py --help
```

#### 运行白板动画流式渲染：
```bash
python srt-whiteboard-animation/scripts/render_stream_whiteboard.py --help
```

#### 运行声画字幕一键合成：
```bash
python tts-voiceover/scripts/srt_to_voice.py --help
```

---

## 🔒 开源合规与安全性
- 本仓库已配置严格的 `.gitignore` 机制，**绝不提交任何私有 API 密钥、密码、本地环境绝对路径及未授权生成物**。
- 所有脚本均使用相对路径与动态环境变量设计，开箱即用。

---

## 📄 开源许可证 (License)
本项目基于 [MIT License](./LICENSE) 开源。
