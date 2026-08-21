---
name: srt-whiteboard-animation
description: 将 SRT 字幕做成暖米黄纸张底的白板手绘动画：读字幕→输出配图策略→确认后生成统一风格线稿→按叙事语义标注分区→预览台调整→渲染 MP4。编排沿用分区遮罩揭示（annotation.json / sequence / startMs / protectedRegions），但每个区域内的落墨换成 stream 的连续笔迹（骨架/网格 ink→color）。当用户提供 SRT 字幕并要求"字幕做成白板手绘/流式笔迹视频""SRT 生成白板动画""按字幕分镜画手绘"时触发。
---

# SRT 白板动画（mask 编排 + stream 画法）

把 SRT 字幕转成白板手绘动画：**编排**沿用分区遮罩揭示（按叙事顺序逐区域揭示、未开始区域完全隐藏、重叠用 `protectedRegions` 保护）；**画法**换成流式笔迹——每个区域在自己的允许掩码内，笔尖沿骨架/网格连续滑行落墨（起笔 ink → 添彩 color），所有区域共享一张持久画布，已画完的区域保留在画布上。所有面向用户的说明、分镜、配置和界面文字必须使用中文。

与逐格跳变或矩形擦除不同：本 skill 的笔迹是**连贯流动**的；与整图 stream 不同：本 skill 按**字幕叙事分区**依次作画，可控制每个元素的出场顺序与时序。

## 默认实现参数

| 项目 | 默认要求 |
|---|---|
| 纸张背景 | 生成图使用暖米黄旧纸色（建议 `#F5EBD7`）；渲染时从原图距四角内缩取样染底，禁止纯白。 |
| 画法 | 每区域 stream 连续笔迹：起笔 `ink`（铺线稿）→ 添彩 `color`（还原原色）；权重 `ink:color = 2:1`。 |
| 笔迹路径 | `--ink-path grid`（网格，默认，稳）或 `skeleton`（骨架追踪，线稿清晰的插画更贴合）。 |
| 上色风格 | `--color-fill contour-wipe`（轮廓扫描，默认）或 `brush`（沿轨迹刷）。 |
| 未绘制区域 | 区域的允许掩码 = 矩形 `region` 扣除「后续区域 + protectedRegions」；未开始区域完全隐藏。 |
| 时长来源 | 每张图的 `sceneDurationMs` 来自该幕字幕的时间跨度（建议 25–35 秒/幕）。 |
| 编辑框 | 预览台默认显示全部编号编辑框；编辑框不属于动画画面内容。 |

## 政史社科全时期视觉风格库（根据文案自动路由）

政史社科类内容跨越年代长、概念多。Agent 读到字幕/文案后，**自动分析年代与题材关键词，自动匹配对应的时期视觉风格配方**。全系列保持统一暖米黄底色 `#F5EBD7` 与黑色墨水勾线，确保手绘动画连贯统一。

```
                    ┌── 1. 中国古代史（先秦/汉唐/明清/三国演义）
                    ├── 2. 中国近代史与民国风云（1840~1949/长袍/军装/报纸）
[政史社科文案] ──► ├── 3. 世界近现代与国际政经（工业革命/冷战/地缘政治/大选）
                    └── 4. 现代社科与宏观经济制度（社会学/博弈论/经济图表/制度天平）
```

---

### 时期 1：【中国古代史篇】（先秦/秦汉/三国魏晋/隋唐宋元明清）
- **文案触发词：** 皇帝、朝廷、起义、丞相、士大夫、战乱、赋税、科举、封建、诸侯、三国、水浒等。
- **视觉特征：** 3~3.5 头身 Q 版古代人物，传统汉服袍服、冠帽发髻、佩剑战旗、马车宫门。表情夸张生动（威严、怒吼、恐慌、沉思）。
- **色彩与材质：** 暖米黄纸张 `#F5EBD7`，姜黄、赤红、靛蓝、墨绿等传统国风平涂填色（Cel shading），粗黑墨线。
- **Prompt 模板：** `Modern Chinese ancient historical picture book illustration, cute 3.5-head chibi character, [角色身份与服饰动作], clean bold black ink contour lines, smooth flat color fill, traditional Chinese tones, solid warm cream-white paper background #F5EBD7, ample negative space, minimal vector style --ar 16:9`

---

### 时期 2：【中国近代史与民国风云篇】（1840 晚清鸦片战争 ~ 1949 建国前夕）
- **文案触发词：** 洋务运动、辛亥革命、民国、租界、军阀、长衫马褂、中山装、新青年、抗战、上海滩、工厂罢工、法币贬值等。
- **视觉特征：** Q 版近代人物造型（长衫马褂、圆框眼镜、中山装、民国学生装、旧式军官大盖帽）；复古道具（老报纸、留声机、老式黄包车、早期蒸汽机车、旧式步枪）。
- **色彩与材质：** 略带复古怀旧感的平涂色调（藏青、军绿、砖红、卡其灰），配合暖米黄纸张 `#F5EBD7`，木刻版画与近代连环画融合质感。
- **Prompt 模板：** `Early 20th century modern Chinese history picture book illustration, cute 3.5-head chibi character, [如: a May Fourth movement student / a Republican warlord / old newspaper scene], retro vintage comic style, clean bold black ink outlines, flat color wash in navy blue and olive, solid warm cream-white paper background #F5EBD7, ample negative space --ar 16:9`

---

### 时期 3：【世界近现代与国际政经篇】（大航海 / 工业革命 / 冷战 / 地缘博弈 / 全球化）
- **文案触发词：** 殖民扩张、工业革命、蒸汽机、华尔街、冷战、美苏、地缘政治、联合国、石油危机、大选辩论、美元霸权、关税战等。
- **视觉特征：** 欧美历史与现代政经 Q 版角色（头戴高筒礼帽的资本家、戴假发的启蒙思想家、西装政要、工业流水线工人）；标志性地缘政治符号（公文包、油桶、集装箱货轮、国会大厦、握手与博弈谈判桌）。
- **色彩与材质：** 政治讽刺漫画（Political Editorial Cartoon）风格，干净黑墨线，克制的深蓝、绯红、金黄点缀，暖米黄底。
- **Prompt 模板：** `Modern editorial political cartoon illustration, cute chibi stylized world historical character, [如: 19th century industrial capitalist in top hat / diplomats negotiating over a world map], clean black ink line art, bold editorial color palette, solid warm cream-white paper background #F5EBD7, minimal vector layout, ample negative space --ar 16:9`

---

### 时期 4：【现代社科与宏观经济/制度理论篇】（社会学 / 制度经济学 / 博弈论 / 抽象模型）
- **文案触发词：** 基尼系数、通货膨胀、博弈论、社会阶层流动、制度成本、公地悲剧、边际效益、社会契约、选举机制等。
- **视觉特征：** Notion 涂鸦与概念插画融合（简笔小人 + 抽象模型道具：天平秤、齿轮机械、阶梯与金字塔、上升/下降趋势曲线、剪刀差模型）。强调逻辑与概念隐喻。
- **色彩与材质：** 极简双色/三色（深灰线 + 科技蓝 / 警示红），极度干净纯粹。
- **Prompt 模板：** `Minimalist social science concept doodle illustration, Notion aesthetic, cute conceptual stylized figures demonstrating [如: social inequality scale / inflation curve mechanism], clean sharp ink lines, subtle accent color in blue and coral red, solid warm cream-white paper background #F5EBD7, ample negative space --ar 16:9`

---

### 通用绝对禁止项与渲染规范
- **禁止项：** 严禁生成任何文字/数字/水印（由字幕自动驱动）；严禁 3D 渲染、厚涂、噪点或写实复杂背景。
- **渲染推荐参数：** 全部推荐使用 `--ink-path skeleton --color-fill contour-wipe`（骨架流式落墨 + 轮廓平涂上色，出片效果最佳）。

## 确认关卡（强制）

默认工作流的**每一步完成后都必须停止并等待用户明确确认**，才可开始下一步。确认前不得生成下一步的图片、标注、预览、视频或合并文件；不得把“未回复”“此前的笼统授权”“用户没有反对”视为确认。用户要求修改上一步时，只重做该步，并在完成后再次等待确认。

唯一的连带动作是：**标注 JSON 创建完成后，必须立即自动打开预览台并载入该 JSON 所在目录**；这属于第 3 步的交付，不需要为“打开预览台”另行等待确认。若浏览器的 File System Access API 要求用户手势，使用浏览器界面选择这个已确定的目录；不得因此向用户索要额外确认或改为让用户自行打开预览台。

## 工作流程

1. **读字幕、出策略（不生成图片）。** 用 `scripts/parse_srt.py` 把 SRT 解析成字幕条并按 25–35 秒/幕给出建议分镜。据此输出配图策略：每幕的场景编号、核心表达、画面主体、对应字幕区间与 `sceneDurationMs`。每幕只表达一个核心意思。**完成后停止，等待用户确认策略。**
2. **生成线稿并保存到素材库。** 仅在用户确认策略后，按“统一出图视觉规范”逐幕生成 16:9 暖米黄旧纸张底线稿图，背景 `#F5EBD7`，主体之间保留充足留白便于自动拆分；不得生成文字、复杂照片、重叠对象或与规范冲突的元素。**每张生成的线稿必须立即复制保存到素材库 `<SKILL_DIR>/assets/library/<项目名>/` 目录中**，文件名与场景编号对应（如 `scene-01-xxx.png`），以便后续增量复用。**完成后停止，展示线稿并等待用户确认。**
3. **先读字幕再看图，然后标注并打开预览台。** 仅在用户确认线稿后，先阅读该图对应的字幕、再实际查看图片、并获取原图像素宽高；不得只凭字幕臆测画面，也不得只按画面位置机械排序。先提炼字幕叙事事件，再把图中可见主体对应到事件，按“场景铺垫 → 关键人物/物体 → 动作冲突或变化 → 反应/结果”的语义顺序安排绘制。随后创建 `<图片名>.annotation.json`。创建完成后，立即用默认浏览器打开 `assets/preview.html`，并通过预览台的“打开文件夹”载入**该标注文件所在目录**的全部 `<名称>.png` + `<名称>.annotation.json`；不得只给出文件路径或要求用户自行操作。**预览台已带入目录后停止，等待用户确认标注与预览内容。**
4. **生成区域预览图。** 仅在用户确认标注与预览内容后，用 `render_annotation_preview.py` 出编号/方向检查图，核对分区与叙事顺序一致、区域都在画布内、重叠主体用 `protectedRegions` 保护。**完成后停止，等待用户确认预览图。**
5. **在预览台调整并保存。** 仅在用户确认预览图后，在已打开且已载入对应目录的预览台调整：默认（未播放）显示完整图片和区域框；画布是**矩形代理**：拖区域四边四角改 `region`，右侧改名称/方向/**开始(ms)/结束(ms)**（时长= 结束−开始，只读）与**字幕**，拖动模块列表**调整顺序**（自动重排 `sequence`），选中模块自动高亮对应字幕；拖时间轴或按播放看揭示（未开始区域不显示）；`direction` 只影响此代理。改完点“保存本场景/全部保存”写回原 `.annotation.json`（含每区域 `subtitle`，并把 `sceneDurationMs` 对齐到最后区域结束+0.5s）。**保存后停止，等待用户确认最终标注与时序。**
6. **命令行渲染成片。** 仅在用户确认最终标注与时序后，用 `render_stream_whiteboard.py` 逐幕出全清 MP4，抽查开场、任意重叠模块中段、结尾三个时间点。**完成后停止，等待用户确认成片。**
7. **多幕合并（仅适用于多幕）。** 仅在用户确认所有单幕成片后，用 `merge_scenes.py` 按顺序合并成一条。**完成后停止，等待用户确认最终合成视频。**


## 目录约定


### 素材库（永久保存，可增量复用）

所有 AI 生成的线稿原图保存在 `assets/library/` 下，按项目名分目录。这些素材**永久保留**，后续可直接复用或修改，不随项目产出清理：

```text
<SKILL_DIR>/assets/library/<项目名>/
  scene-01-<名称>.png              # AI 生成的线稿原图（永久素材）
  scene-02-<名称>.png
  ...
```

### 成品产出（项目交付物）

标注文件、渲染成片、合并视频保存在 `output/` 下，按项目名分目录：

```text
<SKILL_DIR>/output/<项目名>/
  scene-01-<名称>.png              # 从素材库复制，用于标注与渲染
  scene-01-<名称>.annotation.json  # 与 png 同名
  scene-01-<名称>-whiteboard.mp4   # 成片
  scene-01-<名称>-preview.mp4      # 预览台生成
  final.mp4                        # 多幕合并最终视频
```

图片与配置必须同名：`foo.png` 对应 `foo.annotation.json`。预览台据此自动加载配置。


## 语义排序与像素级标注（必须执行）

1. **阅读依据：** 标注前必须同时具备字幕与已查看的原图。缺任一项先索取，不得生成标注。
2. **顺序依据：** `sequence`、`startMs` 与 `label` 必须反映字幕中的事件先后，而非仅按从左到右、从上到下或视觉显眼程度。
3. **坐标依据：** 每个模块输出原图坐标系的整数像素 `x`、`y`、`width`、`height`；原点左上角，禁止百分比/比例/估算坐标或省略尺寸。`canvas.width`/`canvas.height` 必须等于原图像素尺寸。
4. **模块字段：** 每个元素含 `sequence`、`narrativeRole`、`subtitle`、`region`、`reveal`、`handPath`。`narrativeRole` 用中文说明其在字幕中的叙事作用；`subtitle` 存该区域对应的字幕文本（来自 SRT，供预览台联动与后续用途）；`sequence` 从 1 起连续。
5. **校验：** 生成预览前检查每个区域是否在画布内、是否覆盖对应可见主体、是否与字幕事件相符；重叠主体用 `protectedRegions` 保护后绘制模块。

## 时序模型（stream 画法专用）

- **每幕总时长** `sceneDurationMs` 来自该幕字幕时间跨度（`parse_srt.py` 的 `scenes[].sceneDurationMs`）。
- **区域串行作画：** stream 画法是一支笔在动，同一幕内各区域应**在时间上依次进行**（`startMs` 不重叠）：下一区域从上一区域 `startMs + durationMs`（+ 可选 100–300ms 呼吸）开始。若 `startMs` 重叠，渲染器仍按顺序处理，但视觉上不再是并发。
- **区域内 ink→color：** 每个区域的 `durationMs` 会按 `ink:color = 2:1` 切成起笔段和添彩段。`durationMs` 由预览台的**开始/结束时间**决定（结束−开始），可对齐该区域对应字幕的时长；也可用 150 像素/秒 × 绘制距离作为初始估算。
- **凝视收尾：** 全部区域画完后自动补到 `sceneDurationMs`，并保证结尾至少停留 0.5 秒完整原图。
- `reveal.direction` 在 stream 画法下**不决定真实笔迹**（笔迹由骨架/网格自动生成），仅供预览台的矩形代理演示；保留它是为了预览台可用。

## 遮罩不变量（编排层，必须执行）

- 在时间 `t`，模块仅可显示其 `reveal.startMs ≤ t` 之后、且不超过当前作画进度的像素；未开始模块的任何线条/填充/图像都不得出现。
- 每个区域的**允许掩码** = 矩形 `region` 扣除全部**后续模块的 `region`**，再扣除本模块 `reveal.protectedRegions`。stream 落墨被限制在允许掩码内，因此后续区域不会提前露线。
- `protectedRegions` 采用与 `region` 相同的原图整数像素坐标，用于矩形过大、主体交叠或背景线条可能泄露的情况。
- 渲染器已实现"限制在允许掩码内落墨 → 后续区域与保护区天然不被触碰"的顺序；预览台矩形代理用等价的 `destination-out` 扣除演示同一编排。

## 配置示例

```json
{
  "sceneId": "scene-01",
  "canvas": { "width": 1672, "height": 941 },
  "storyBasis": "该幕字幕的事件摘要",
  "sceneDurationMs": 9000,
  "elements": [
    {
      "id": "rockery",
      "label": "假山场景",
      "sequence": 1,
      "narrativeRole": "故事的场景铺垫",
      "subtitle": "猴子山上，一只小猴子坐在假山顶端，手里拿着香蕉。",
      "type": "structure",
      "region": { "x": 20, "y": 120, "width": 540, "height": 780 },
      "reveal": { "direction": "top_to_bottom", "startMs": 300, "durationMs": 2600, "maskPaddingPx": 22, "protectedRegions": [] },
      "handPath": { "start": [290, 130], "end": [290, 890], "easing": "easeInOut" }
    }
  ]
}
```

> `direction` / `handPath` 仅供预览台矩形代理使用；成片笔迹由 stream 自动生成，无需精调。

## 使用脚本

所有渲染脚本用 skill 内 `.venv` 的解释器运行（依赖隔离）。

1. **准备环境**（首次或缺依赖时）：
   ```bash
   python scripts/prepare_env.py --check   # 探测；成功末行输出 ENV_PY=<路径>，捕获备用
   python scripts/prepare_env.py           # 缺则建 .venv 并装 opencv-python/numpy/av
   ```
2. **解析字幕 + 建议分镜**：
   ```bash
   python scripts/parse_srt.py <字幕.srt> --target-sec 30 --min-sec 25 --max-sec 35
   ```
3. **区域编号预览图**：
   ```bash
   python scripts/render_annotation_preview.py <图片> <标注> <预览图输出>
   ```
4. **预览台（无需服务器）**：直接用 Chrome / Edge 打开 `assets/preview.html`，点"打开文件夹"选目录 → 载入全部图片+同名标注 → 拖拽编辑 → "保存"写回原文件。写回需 File System Access API（Chrome/Edge）；其它浏览器改为下载后手动覆盖。渲染仍走命令行（下面第 5 步）。
5. **渲染单幕成片**：
   ```bash
   <ENV_PY> scripts/render_stream_whiteboard.py <图片> <标注> <输出mp4> assets/drawing-hand.png \
       [--ink-path grid|skeleton] [--color-fill contour-wipe|brush] [--total-ms <毫秒>]
   ```
   `--total-ms` 缺省时用标注里的 `sceneDurationMs`。末行输出 `OUTPUT=<路径>`。
6. **多幕合并**：
   ```bash
   <ENV_PY> scripts/merge_scenes.py --inputs 幕1.mp4 幕2.mp4 幕3.mp4 --output final.mp4
   ```

## 质量检查

渲染前/后确认：

- 首帧为干净的暖米黄旧纸张底，没有提前露出线条。
- 已阅读对应字幕并实际查看原图；`canvas` 与原图像素尺寸一致，所有 `region` 为整数像素坐标且在画布内。
- `sequence`、`startMs` 与字幕事件顺序一致；预览图编号/标签/区域来自同一份标注 JSON。
- 在开场、任意重叠模块中段、所有模块完成后三个时间点检查：未绘制模块均不可见，重叠保护区不漏出，最终帧显示完整原图。
- 笔尖贴近正在推进的笔迹；线稿清晰的插画可用 `--ink-path skeleton` 让笔迹更贴合。
- 所有模块结束后停留至少 0.5 秒完整原图。
- 多幕合并后顺序、时长与字幕分镜一致。

如需修改效果，先在预览台（`assets/preview.html`）调整标注（区域/顺序/时序）并保存，再命令行渲染，不要凭空反复出片。
