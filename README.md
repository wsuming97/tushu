# 🎨 AI 商业内容创作技能套件 (AI Content Creator Suite)

> 面向 **微信视频号 / 抖音 / 小红书 / 快手 / 微信公众号** 的全流程 AI 视觉、文案与音视频商业内容生产工作流工具包。
> 涵盖 **选题策划 ➔ 逆向拆解 ➔ 历史立论 ➔ 双轨写作 ➔ 质量风控 ➔ 视觉生图 ➔ 白板动画 ➔ 智能配音 ➔ 互动运营** 完整闭环。

---

## 📦 核心技能矩阵 (15 大打包生产技能)

```text
.
├── 🧭 xf-router/                     # 路由中枢：路线规划与 15 大技能意图分发路由器
├── 📚 copywriting-library/          # 技能 1：文案素材库（双轨框架、视觉指南与读者洞察分析）
├── ✍️ copywriting-verify-optimize/   # 技能 2：商业文案 6 维质检评分、事实核验与转化优化
├── 🛡️ publish-precheck/             # 技能 3：国内自媒体发布前风控自审与保意违禁词修复
├── 🎴 ai-quote-card-maker/          # 技能 4：爆款金句卡片 & 贴图故事号全套生成
├── 🎬 srt-whiteboard-animation/     # 技能 5：SRT 字幕驱动的白板流式连续笔迹手绘动画引擎
├── 🎙️ tts-voiceover/                # 技能 6：播客级磁性配音与声画合成工具
├── 🎞️ native-subtitle-quote-image/  # 技能 7：原生字幕截帧与社交长图拼图工具
├── 🔍 competitor-deconstruct/       # 技能 8：同行文案字数机械分段与开篇句型槽位提取
├── 📊 viral-title-ab-tester/        # 技能 9：爆款标题 10 维启发式评分与 A/B 选拔器
├── 🎨 cover-visual-prompt/          # 技能 10：爆款封面动态主体与生图 Prompt 蒸馏器
├── 🏛️ dbs-standard-answer/          # 技能 11：基于已核验事实的历史案例类比与学术立论建议器
├── 💬 smart-comment-booster/        # 技能 12：作者置顶首评与官方答疑助手 (零水军/零虚构)
├── 🖋️ mimeng-style-skill/           # 技能 13：新媒体观点文机制写作与句长统计分析引擎
└── 🖨️ mono-color/                   # 技能 14：出版级单色/双色孔版印刷与 Risograph 视觉底图引擎
```

> **📌 外部可选依赖说明**：
> `weread-skills`（微信读书助手网关规范）作为外部服务接入规范在此登记，需用户在本地自行配置 `WEREAD_API_KEY`，不计入本仓库打包技能源码中（详见 [EXTERNAL_REFERENCES.md](EXTERNAL_REFERENCES.md)）。

---

## 🛠️ 15 大模块核心能力概览

| 序号 | 技能模块 | 核心定位与能力说明 |
| :---: | :--- | :--- |
| **01** | `xf-router` | **创作路由器**：基于用户输入意图分析，智能推荐 15 大技能的最佳主辅组合与执行路线。 |
| **02** | `copywriting-library` | **文案素材库**：双轨带货框架（深度款 12m + 流量款 4m）与读者画像生活细节微雕标准。 |
| **03** | `copywriting-verify-optimize` | **文案质检优化**：事实可信度、共鸣感、转化逻辑与风控 6 维打分（≥85分放行门禁）。 |
| **04** | `publish-precheck` | **发布风控预审**：内置多平台通用违禁词/极限词规则库扫描与同义保意修复。 |
| **05** | `ai-quote-card-maker` | **金句卡片生成**：全屏唯美意境卡片、毛玻璃排版与贴图故事号生成。 |
| **06** | `srt-whiteboard-animation` | **白板手绘动画**：SRT 驱动的流式笔迹（ink 骨架 ➔ color 平涂）与分区遮罩揭示。 |
| **07** | `tts-voiceover` | **TTS 配音合成**：接入主流语音 API，支持断句调优、响度标准化与音视频音画合成。 |
| **08** | `native-subtitle-quote-image` | **原生字幕长图**：按视频内嵌字幕精确帧截取并无缝拼接为小红书/社交长图。 |
| **09** | `competitor-deconstruct` | **同行文案拆解**：基于字数比例机械四段切分（15%/45%/80%/100%），提炼首句特征与槽位。 |
| **10** | `viral-title-ab-tester` | **标题启发式选拔**：内置冲突度、悬念感、损失厌恶等 10 维独立启发式打分（零虚构 CTR 预测）。 |
| **11** | `cover-visual-prompt` | **封面提示词蒸馏**：基于主题与指定风格动态生成三层景深视觉主体与生图 Prompt。 |
| **12** | `dbs-standard-answer` | **历史同构立论**：双重证据门禁，匹配学术四要素文献引用（作者/书名/年份/ISBN），输出 8 段式短视频原型。 |
| **13** | `smart-comment-booster` | **评论区运营**：生成作者置顶首评与透明官方问答草稿（严禁水军小号演戏与虚构作者）。 |
| **14** | `mimeng-style-skill` | **观点文写作**：8 大写作方法论与全量真实语料句长科学实测分布统计。 |
| **15** | `mono-color` | **单色双色海报**：机器可读设计系统（≤2 墨色、25%~55% 留白），产出 Risograph 风格底图 Prompt。 |

---

## 🧪 离线验证与可复现性

本仓库内置完整的纯离线行为测试套件，不依赖外部网络或私有 API Key：

```bash
# 运行 15 大技能综合质量与反向门禁测试套件
python tests/test_new_skills_offline.py
```

---

## 📄 开源许可与第三方致谢 (License & Attribution)

本项目核心代码与技能规范基于 **MIT License** 开源。

各子模块的具体许可与致谢说明如下：
- **核心工程与原创技能**：遵循 MIT License（见根目录 [LICENSE](LICENSE)）；
- **`mono-color` 技能**：代码与设计系统遵循 MIT License（见 `mono-color/LICENSE`），视觉资产声明见 `mono-color/ASSET-LICENSE.md`，上游溯源见 `mono-color/UPSTREAM.json`（原作者示例图片已完全排除）；
- **`dbs-standard-answer` 技能**：独立 clean-room 算法代码遵循 MIT License，方法论概念致谢 `dontbesilent2025/dbskill`（见 `dbs-standard-answer/NOTICE.md`）；
- **`srt-whiteboard-animation` 与 `publish-precheck`**：遵循 MIT License（见各自目录下的 `LICENSE`）；
- **外部依赖登记**：`weread-skills`、`dbs-video-extract` 仅作为外部规范与参考登记（见 [EXTERNAL_REFERENCES.md](EXTERNAL_REFERENCES.md)），不包含上游未授权源码。
