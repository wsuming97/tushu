---
name: dbs-standard-answer
description: 基于已核验事实的历史案例类比与专业立论建议器（Historical Analogy & Standard Answer Advisor v2.3）。面向知识博主、商业咨询师与专业 IP 创作者，在已提供可靠事实与信源的前提下，通过三层信息剥离与历史学术文献同构模型，输出带四要素学术引用（作者/书名/年份/ISBN/DOI）、适用边界的立论建议与 8 段式短视频原型。内置双重证据门禁（Dual Evidence Gate），缺失当前事件信源或无同构历史事实时严格阻断。
---

# 基于已核验事实的历史案例类比建议器 (v2.3)

## 🎯 核心定位与定性 (Core Purpose & Definition)
本技能定位为 **“基于已核验事实的历史案例类比与专业立论建议器”**。
解决专业创作者“追热点像营销号、讲理论没人看”的矛盾。通过将用户提供的结构化事实与经过历史验证的商业/学术模型进行同构类比，输出具有学术严谨度与商业边界的 8 段式短视频原型。

---

## 🛡️ 双重证据门禁纪律 (Dual Evidence Gate)
1. **当前事件信源门禁 (Current Sources & Facts Gate)**：
   - 必须同时传入结构化事实（`verified_facts`）与结构化信源（`sources`）；
   - **facts 为空 OR sources 为空均必须阻断**；
   - 每个信源必须包含 6 项结构化字段：`source_id`, `title`, `publisher`, `url`, `published_at`, `accessed_at`；传入普通文本（如“我编造的来源XYZ”）严格阻断；
   - 每条事实必须为包含 `fact_id`, `statement`, `source_ids` 的字典，严禁将纯文本事实自动绑定；
   - 所有外部输入统一标定为 `source_status="user_supplied_unverified"`（用户提供事实与信源，未经联网核验），严禁宣称“已核实事实”或“公开核验报道”；
2. **学术四要素门禁 (4-Element Academic Citations)**：
   - 所有引用的理论与历史正反案例，必须具备【作者、书名/篇名、年份、唯一标识符(ISBN/DOI/HBS Case)】四要素（如：Barbara Ley Toffler & Jennifer Reingold, 2003, ISBN: 978-0767913836）；
   - 严禁出现残缺、拼错或伪造的学术文献引用。

---

## 🎬 八段式短视频原型骨架 (8-Stage Video Archetype)

1. **问题标题**：反常识/高反差的问题化标题；
2. **开头钩子**：3秒内抛出事件核心反差与同构本质；
3. **事件铺垫**：仅陈述提供的已核验事实，标明信源；
4. **底层理论解释**：引入带四要素文献引用的学术模型；
5. **历史案例对比**：调取真实经核实的历史正例与反例；
6. **最小行动建议**：给出带适用前提与失效边界的操作铁律；
7. **结果验证指标**：中长期可量化的衡量标准；
8. **结尾业务回扣**：自然扣回博主自身的专业领域与产品服务。

---

## 💻 命令行工具 (CLI Usage)

```bash
# 提供结构化信源与事实执行分析
python scripts/isomorphism_engine.py \
  --topic "孙宇晨注意力套利现象" \
  --domain "个人IP与商业增长" \
  --facts-json '[{"fact_id":"F1", "statement":"孙宇晨公开通过高调竞拍巴菲特午餐等争议事件获取全网关注", "source_ids":["S1"]}]' \
  --sources-json '[{"source_id":"S1", "title":"彭博社专题报道", "publisher":"Bloomberg", "url":"https://bloomberg.com/news/123", "published_at":"2023-01-01", "accessed_at":"2023-01-02"}]' \
  --strict-evidence
```
