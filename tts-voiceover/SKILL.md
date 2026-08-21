---
name: tts-voiceover
description: >
  TTS 配音 + 成片合成 Skill。读取 SRT 字幕文件 → 调用火山引擎(豆包语音)或 MiniMax
  TTS API 逐句生成配音 → 按时间轴拼接为完整音频 → 与白板动画视频合成为带声画的最终成片。
  支持多音色试听、语速调节和断句优化。兼容 Antigravity / Codex 双平台。
---

# TTS 配音 + 成片合成 Skill

## 概述

将 SRT 字幕文件转化为高质量中文配音，并与视频合成为可发布的成片。
提供 **两条并行路径**，适应不同的制作需求：

| 路径 | 入口模式 | 适用场景 | 是否需要 API |
|:---|:---|:---|:---|
| **路径 A：AI 配音流水线** | `--mode audition` → `--mode full` | 批量化、全自动出片 | ✅ 需要 TTS API Key |
| **路径 B：剪映手动配音** | `--mode export` | 精品打磨、真人配音 | ❌ 完全免费 |

## 支持的 TTS 引擎

| 引擎 | 状态 | 特点 |
|:---|:---|:---|
| **火山引擎（豆包语音）** | ✅ 已接入 | 300+ 音色、情感控制、SSML 支持 |
| **MiniMax** | 🔲 待接入 | speech-2.8-turbo/hd、音色混合 |

## 目录结构

```text
skills/tts-voiceover/
├── SKILL.md              # 本文件
├── .env                  # API 密钥（不入版本控制）
├── .env.example          # 密钥模板
├── scripts/
│   ├── tts_volcano.py    # 火山引擎 TTS 核心
│   ├── tts_minimax.py    # MiniMax TTS 核心（待实现）
│   ├── srt_to_voice.py   # 统一入口：SRT → 配音 / 导出包
│   ├── export_pack.py    # 剪映导出包生成器
│   └── compose_final.py  # 视频 + 音频 → 成片 (ffmpeg)
└── output/               # 项目输出目录
    └── <项目名>/
        ├── voice_segments/    # 逐句音频片段（路径A）
        ├── voiceover.mp3      # 完整配音音频（路径A）
        ├── audition/          # 多音色试听片段（路径A）
        ├── final_voiced.mp4   # 带配音的最终成片（路径A）
        └── export-pack/       # 剪映导出包（路径B）
            ├── final.mp4          # 无声视频
            ├── narration.txt      # 配音稿（标注停顿）
            ├── subtitles.srt      # SRT 字幕
            ├── publish-copy.txt   # 发布文案 + 话题标签
            ├── first-comment.txt  # 作者首评
            └── README.txt         # 剪映操作指南
```

---

## 路径 B：剪映手动配音（无需 API）

> 推荐刚上手时先用这个路径，不花钱就能完成全流程。

### 一键生成导出包

```bash
python scripts/srt_to_voice.py \
  --srt "path/to/人生由我.srt" \
  --video "path/to/final.mp4" \
  --mode export \
  --project-name "人生由我-梅耶马斯克" \
  --account "三花万里朝夕"
```

生成的 `export-pack/` 文件夹可以直接发给剪映用户，README.txt 包含完整操作指南。

---

## 路径 A：AI 配音流水线（需要 TTS API）

### 配置

#### 1. 创建 `.env` 文件

```bash
# === 火山引擎（豆包语音）===
VOLCANO_APP_ID=你的AppID
VOLCANO_API_KEY=你的APIKey
VOLCANO_CLUSTER_ID=volcano_tts

# === MiniMax（待接入）===
MINIMAX_API_KEY=
MINIMAX_GROUP_ID=
```

#### 2. 安装依赖

```bash
pip install requests python-dotenv pydub
```

### Step 1: 多音色试听

```bash
python scripts/srt_to_voice.py \
  --srt "path/to/人生由我.srt" \
  --engine volcano \
  --mode audition \
  --output-dir output/人生由我-梅耶马斯克/
```

会用 SRT 前 3 句生成 7 种音色的试听片段，保存到 `audition/` 目录。

### Step 2: 全量生成配音

```bash
python scripts/srt_to_voice.py \
  --srt "path/to/人生由我.srt" \
  --engine volcano \
  --voice "zh_female_tianmeitaozi_mars_bigtts" \
  --speed 0.95 \
  --output-dir output/人生由我-梅耶马斯克/
```

### Step 3: 合成成片

```bash
python scripts/compose_final.py \
  --video "path/to/final.mp4" \
  --audio output/人生由我-梅耶马斯克/voiceover.mp3 \
  --output output/人生由我-梅耶马斯克/final_voiced.mp4
```

---

## 音色推荐（治愈/故事类）

| 音色名 | voice_type | 风格 |
|:---|:---|:---|
| 甜美桃子 | `zh_female_tianmeitaozi_mars_bigtts` | 温暖甜美、娓娓道来 |
| 柔美女友（多情感） | `zh_female_roumeinvyou_emo_v2_mars_bigtts` | 知性温柔、情感丰富 |
| Vivi 2.0 | `zh_female_vv_uranus_bigtts` | 清澈自然、通用 |
| 小何 2.0 | `zh_female_xiaohe_uranus_bigtts` | 年轻明快 |
| 爽快思思（多情感） | `zh_female_shuangkuaisisi_emo_v2_mars_bigtts` | 干脆有力、节奏感强 |

## 注意事项

- `.env` 文件包含 API 密钥，**绝不可提交到 Git**。
- 火山引擎 TTS 按字符数计费，试听阶段只用前 3 句（约 50 字），不浪费额度。
- 配音生成的逐句音频片段保留在 `voice_segments/`，支持单句重新生成（增量）。
- 成片合成只做 视频+配音，BGM 由用户在剪映中手动添加。
- Windows 环境需设置 `PYTHONIOENCODING=utf-8` 以正确显示中文 emoji。
