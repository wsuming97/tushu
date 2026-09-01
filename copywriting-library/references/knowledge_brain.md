# 🔗 知识大脑连接配置

> 本文件告诉 Agent（Antigravity / Codex）去哪里读取知识积累，以及如何双向同步数据。

## Obsidian 知识大脑位置

- **Vault 路径**：`${VAULT_ROOT}`
- **Git 仓库**：已初始化（Codex 可直接打开）
- **规约文件**：`${VAULT_ROOT}/AGENTS.md`

---

## 数据流向（技能库 ↔ 知识大脑）

```text
技能库 (skills/)                          知识大脑 (${VAULT_ROOT}/)
──────────────────                       ──────────────────────
weread_fetcher.py 采样书评  ──同步──→   raw/weread-reviews/
topics/书名/成品文案(≥85分) ──归档──→   raw/our-productions/
                                         raw/books/书名.pdf  ──提取──→ wiki/entities/books/书名.md
写新文案前              ←──参考──   wiki/concepts/ + wiki/entities/
```

## 协作规则

### 1. 微信读书书评同步（A → 知识大脑）
- `weread_fetcher.py` 输出保存到技能库 `topics/` 后
- **同步一份到** `${VAULT_ROOT}/raw/weread-reviews/书名_书评采样.md`

### 2. 成品文案归档（B → 知识大脑供自我学习）
- 技能库中质检 ≥85 分的最佳成品文案
- **归档到** `${VAULT_ROOT}/raw/our-productions/书名_篇号_类型.md`
- Agent 从这些成品中学习风格演变与迭代轨迹

### 3. 书籍原文导入与提取（C）
- PDF/EPUB/TXT 手动放入 `${VAULT_ROOT}/raw/books/书名/`
- Agent 读取后提取：书籍信息、全书地图、核心概念、关键观点、金句摘录
- 提取结果写入 `${VAULT_ROOT}/wiki/entities/books/书名.md`

### 4. 写新文案前（必做）
1. 读取 `${VAULT_ROOT}/wiki/entities/books/书名.md`（全书地图与核心概念）
2. 读取 `${VAULT_ROOT}/wiki/concepts/`（四层递进带货法、生活毛刺细节等方法论）
3. 读取 `${VAULT_ROOT}/wiki/entities/benchmark-accounts/`（对标账号风格档案）
4. 将知识融入文案生成过程

### 5. 项目复盘后
- 经验沉淀写入 `${VAULT_ROOT}/wiki/playbooks/`
- 在 `${VAULT_ROOT}/wiki/changelog.md` 追加变更记录
