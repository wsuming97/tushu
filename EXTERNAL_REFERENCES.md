# 外部技能与方法论参考登记表 (External References Registry)

本文档用于登记经评估后仅作为外部参考、暂不直接将其上游文档/代码纳入 Git 源码版本库的外部项目与规范。

---

## 1. weread-skills (微信读书助手)

- **项目名称**：weread-skills (WeRead Agent Gateway Specification)
- **协议版本**：1.0.4
- **官方网关**：`https://i.weread.qq.com/api/agent/gateway`
- **认证机制**：`Authorization: Bearer $WEREAD_API_KEY` (Key 格式: `wrk-xxxxxxxx`)
- **来源性质**：微信读书 Agent 开放接口调用规范说明
- **许可证状态**：未附带独立开源许可证 (Proprietary / Tencent WeRead)
- **排除策略**：
  - 上游 9 个规范 Markdown 文件（`SKILL.md`, `book.md`, `discover.md`, `notes.md`, `profile.md`, `readdata.md`, `review.md`, `search.md`, `shelf.md`）**不作为开源代码提交到 Public 仓库**；
  - 仅作为外部服务接口调用说明在此备案。
- **本地使用指引**：
  - 需使用微信读书能力时，在本地环境配置环境变量：`export WEREAD_API_KEY=<你的apikey>`；
  - 直接按微信读书官方网关协议 POST 发送 JSON 请求。
- **登记日期**：2026-09-01

---

## 2. dbs-video-extract / dbs-wanshu-content-router

- **项目名称**：dbs-video-extract（DBS 视频提取与内容路由）
- **来源仓库**：
  - [dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill)
  - [zhenxishuai/dbs-wanshu-content-router](https://github.com/zhenxishuai/dbs-wanshu-content-router)
- **作者与许可**：dontbesilent2025 / 上游核心方法论遵循 CC BY-NC 4.0
- **评估定级**：`REJECTED_FOR_INTEGRATION`（停止集成，仅作外部备查参考）
- **决议原因**：
  1. 核心数据抓取与音视频转录强依赖 TikHub、轻抖等第三方聚合付费 SaaS 接口，并非平台官方 API；
  2. 暂不具备开箱即用的历史时序增长曲线、时间轴 SRT 深度解析或 Hook 因果归因等不可替代的核心壁垒；
  3. 引入外部付费商业 Token 会增加系统运维与费用不确定性。
- **执行边界与纪律**：
  - **不安装、不复制、不修改** 现有技能矩阵；
  - **不配置** TikHub / 轻抖 Key，严禁产生外部付费 API 调用；
  - **不加入** `xf-router` 意图分发，**不同步** 至 `.newmax` 与 `.codex` 全局目录；
  - **现有业务基准**：所有文案分析与拆解流程，继续基于用户显式提供的文案、字幕文件或平台官方后台导出数据进行。
- **登记日期**：2026-09-01
