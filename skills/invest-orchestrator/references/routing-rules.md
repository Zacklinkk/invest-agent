# Routing Decision Rules

This document defines how the invest-orchestrator dispatches user requests across three escalation levels: L1 (direct skill call), L2 (single expert agent), and L3 (multi-agent team).

---

## Routing Decision Matrix

### L1 -- Direct Skill Dispatch

Route to a single skill with no agent overhead. Applicable to quick lookups, concept Q&A, file downloads, and simple visualizations.

| User Intent (example)             | Dispatch Target                  |
| --------------------------------- | -------------------------------- |
| "茅台PE多少"                       | stock-data                       |
| "什么是反脆弱"                     | taleb-risk-philosophy            |
| "下载比亚迪2024年报"               | cninfo-annual-report             |
| "画个茅台K线图"                    | stock-data + echarts             |
| "帮我读这篇论文"                   | read-paper                       |
| "白酒行业是什么阶段"               | industry-research (theory only)  |

Characteristics:

- Single indicator or ratio query (PE, PB, ROE, market cap, price, volume).
- Concept or philosophy Q&A with no company-specific analysis.
- File download or document retrieval.
- Simple chart rendering with no analytical overlay.

### L2 -- Single Expert Agent

Route to exactly one analyst agent when the request targets a single analytical dimension for a single stock or entity.

| User Intent (example)             | Dispatch Target            |
| --------------------------------- | -------------------------- |
| "分析茅台财报"                     | fundamental-analyst        |
| "给茅台做DCF估值"                  | valuation-analyst          |
| "系统研究光伏行业"                 | industry-analyst           |
| "茅台技术面分析"                   | technical-analyst          |
| "茅台价格行为分析"                 | price-action-analyst       |
| "评估茅台的尾部风险"               | risk-analyst               |

Characteristics:

- Single target entity (one stock, one industry, one theme).
- Single analytical dimension clearly identified.
- No cross-dimension dependencies required.

### L3 -- Multi-Agent Team

Assemble a team of agents when the request involves multiple dimensions, multiple targets, or explicitly asks for a comprehensive deliverable.

| User Intent (example)                     | Team Composition                                              |
| ----------------------------------------- | ------------------------------------------------------------- |
| "深度研究贵州茅台"                         | All analysts -> trade-planner -> report                       |
| "对比茅台五粮液洋河估值"                   | Multi-target: valuation-analyst x N -> comparison report      |
| "评估我的白酒+新能源组合"                  | Portfolio: multiple industry + fundamental analysts -> report  |
| "找一个低估的消费股"                       | Screening: stock-data -> valuation-analyst x N -> ranking     |

Characteristics:

- Two or more analytical dimensions with cross-dependencies.
- Two or more target entities requiring parallel analysis then synthesis.
- Request for a comprehensive investment report or trade plan.
- Screening or ranking across a universe of candidates.

---

## Keyword Detection Rules

Map detected keywords in the user query to analytical dimensions. Each dimension corresponds to a specific L2 agent.

| Keywords                                          | Dimension      | L2 Agent               |
| ------------------------------------------------- | -------------- | ---------------------- |
| 财报, 财务, 杜邦, 造假, 利润, 营收, 现金流        | fundamental    | fundamental-analyst    |
| 估值, DCF, PE, PB, 内在价值, 安全边际              | valuation      | valuation-analyst      |
| 行业, 赛道, 竞争格局, 市场空间, 产业链             | industry       | industry-analyst       |
| 技术面, K线, 缠论, 均线, 买卖点, 主力, MACD        | technical      | technical-analyst      |
| 价格行为, price action, 逐bar, 信号, 趋势区间      | price-action   | price-action-analyst   |
| 风险, 黑天鹅, 脆弱性, 对冲, 尾部, 压力测试         | risk           | risk-analyst           |

### L3 Escalation Keywords

The following keywords bypass dimension counting and escalate directly to L3:

| Keywords                                          | L3 Trigger Reason     |
| ------------------------------------------------- | --------------------- |
| 深度研究, 全面分析, 投资报告, 研报                  | All-dimension sweep   |
| 对比, 比较, 筛选, 排名, 优选                       | Multi-target analysis |

---

## Dimension Count Rules

After keyword detection, apply the following escalation logic:

1. **0 detected dimensions + simple query** -> **L1**.
   The query matches no analytical dimension and fits a quick lookup or concept Q&A pattern.

2. **1 detected dimension** -> **L2**.
   Route to the single corresponding analyst agent.

3. **2+ dimensions with cross-dependencies** -> **L3**.
   Assemble analysts for each detected dimension, wire outputs to trade-planner, and generate a consolidated report.

4. **Multi-target (>=2 stocks or entities)** -> **L3 regardless of dimension count**.
   Even a single-dimension comparison across multiple targets requires team coordination for parallel execution and synthesis.

### Precedence

Apply rules in this order:

1. Check for explicit override commands (highest priority).
2. Check for L3 escalation keywords.
3. Count target entities -- if >= 2, escalate to L3.
4. Count detected dimensions and apply the dimension count rules above.
5. Default to L1 if no dimension or escalation signal is detected.

---

## Explicit Override Commands

Allow the user to force a specific routing level, bypassing all detection logic.

| Command            | Behavior                                                        |
| ------------------ | --------------------------------------------------------------- |
| `/invest quick`    | Force L1. Execute as a direct skill call, no agent overhead.    |
| `/invest deep`     | Force L2. Select the most relevant single analyst agent.        |
| `/invest full`     | Force L3. Assemble the full analyst team with report output.    |
| `/invest compare`  | Force L3. Run multi-target parallel analysis with comparison.   |

When an override is present, skip keyword detection and dimension counting entirely. Use the override level as the final routing decision.

---

## Edge Cases

- **Ambiguous single-word queries** (e.g., "茅台"): default to L1, return a summary card with quick stats, and prompt the user to specify a deeper analysis direction.
- **Mixed L1 + L2 signals** (e.g., "茅台PE多少，顺便分析一下财报"): escalate to the higher level (L2 in this case). Never split a single user turn into separate L1 and L2 dispatches.
- **Conflicting overrides** (e.g., `/invest quick` with an obviously L3 query): honor the override. The user's explicit command takes precedence over inferred complexity.
