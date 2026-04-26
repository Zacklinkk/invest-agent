---
name: invest-orchestrator
description: This skill should be used when the user invokes "/invest", or asks to "投资分析", "股票研究", "深度研究", "个股分析", "估值对比", "选股", "择时", "交易方案", "组合分析", "行业对比", "研究一下", "投研报告", "帮我看看这只股票", "stock analysis", "investment research". Orchestrates multiple financial analysis skills via three-level dispatch (L1 direct, L2 single expert, L3 multi-agent team).
argument-hint: "[quick|deep|full|compare] [标的代码或名称] [更多标的...]"
---

# Invest Orchestrator

Investment analysis orchestrator that routes tasks across financial skills via three-level dispatch. Coordinates data acquisition, multi-dimensional analysis, trading plan synthesis, and report generation.

## Entry Modes

Two invocation patterns:

**With arguments** — auto-route based on intent:
- `/invest quick 茅台PE` → L1 direct
- `/invest deep 茅台财报` → L2 single expert
- `/invest full 贵州茅台` → L3 team
- `/invest compare 茅台 五粮液 洋河` → L3 team (multi-target)

**Without arguments** — interactive guidance:
1. Ask what to analyze (stock code, industry, portfolio)
2. Confirm analysis dimensions (基本面/估值/行业/技术面/价格行为/风险)
3. Determine dispatch level
4. Execute

## Three-Level Dispatch

### L1 — Direct (main agent handles inline)

**Trigger**: single skill + no deep analysis required.

Examples: quote lookup, simple indicator query, concept Q&A, report download.

Directly invoke the appropriate skill: stock-data, tushare, cninfo-annual-report, book-downloader, wechat-article-to-markdown, read-paper, or any single skill for a quick answer.

### L2 — Single Expert (spawn one subagent)

**Trigger**: single analysis dimension + full workflow needed.

Spawn via `Agent` tool with `subagent_type: "general-purpose"` and `mode: "bypassPermissions"`. The agent prompt must include the analyst role, skill to invoke, target, and output directory.

| Intent | Analyst Role | Primary Skill |
|--------|-------------|---------------|
| 财报分析 | 基本面分析专家 | 财报分析 |
| 估值分析 | 估值分析专家 | damodaran-valuation |
| 行业研究 | 行业研究专家 | industry-research |
| 技术分析 | 技术分析专家 | technical-analysis |
| 价格行为 | 价格行为专家 | al-brooks-price-action |
| 风险评估 | 风险分析专家 | taleb-risk-philosophy |

**L2 Spawn Template:**
```
Agent(
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="你是{角色}。分析标的：{target}。
    1. 调用 {skill} skill 执行完整分析流程
    2. 所有输出必须使用中文
    3. 将分析结果写入 {output_dir}/{filename}.md
    4. 结尾必须包含 trading_suggestion YAML 块"
)
```

Pass the target stock/industry and output directory in the prompt. Wait for result, present to user.

For background execution, set `run_in_background: true` so user can continue chatting.

### L3 — Agent Team (TeamCreate for complex tasks)

**Trigger**:
- Multiple targets (≥2 stocks to compare)
- Multiple dimensions with cross-dependencies
- Portfolio-level analysis
- User explicitly specifies `full` or `compare`

**Strict Three-Wave Execution:**

```
Wave 1: Analysts (parallel)
  → fundamental-analyst
  → valuation-analyst
  → industry-analyst
  → technical-analyst
  → price-action-analyst
  → risk-analyst
  (each writes results to ./invest-reports/{session}/)

Wave 2: Trading Synthesis (after Wave 1 completes)
  → trade-planner
  (reads all analyst outputs, synthesizes trading plan)

Wave 3: Report Generation (after Wave 2 completes)
  → report-synthesizer
  (compiles everything into final HTML report)
```

**Team Setup Steps:**
1. Run `python ~/.claude/plugins/local/invest-agent/scripts/init-workspace.py <target>` to create output directory
2. `TeamCreate` with team name `invest-{target}-{date}`
3. Spawn Wave 1 analysts in parallel — each as `Agent(subagent_type="general-purpose", mode="bypassPermissions")`. In each agent's prompt, specify:
   - Analyst role and primary skill to invoke (see L2 table above)
   - Target stock and output directory path
   - **"所有输出必须使用中文"**
   - Output filename (e.g., `fundamental.md`, `valuation.md`)
   - Must end with `trading_suggestion` YAML block
4. Monitor — when all Wave 1 agents complete, present intermediate results to user
5. Spawn Wave 2: `trade-planner` role — prompt must instruct agent to read all Wave 1 `.md` files from output dir, synthesize trading plan, write `trading-plan.md`
6. Spawn Wave 3: `report-synthesizer` role — prompt must instruct agent to read all files including `trading-plan.md`, invoke echarts/pyramid-principle/svg-craft skills, write `report.html`
7. Present final report to user
8. Clean up team with `TeamDelete`

**Critical: Subagent Spawn Configuration**
- `subagent_type` must be `"general-purpose"` (plugin agents cannot be invoked via subagent_type)
- `mode` must be `"bypassPermissions"` to ensure Bash/Python execution rights
- Agent prompts must explicitly reference which skill(s) to invoke via the Skill tool

**User Intervention:** Between waves, present intermediate results and ask if user wants to adjust direction before proceeding.

## Routing Decision Tree

```
Parse user input
  │
  ├─ Explicit level? (quick/deep/full/compare)
  │   ├─ quick → L1
  │   ├─ deep  → L2
  │   ├─ full  → L3
  │   └─ compare → L3
  │
  └─ Auto-detect
      ├─ Single skill sufficient?     → L1
      ├─ Single dimension, deep?      → L2
      ├─ Multiple targets (≥2)?       → L3
      ├─ Multiple dimensions + deps?  → L3
      └─ Portfolio/cross-analysis?    → L3
```

See `references/routing-rules.md` for detailed routing logic.

## Analysis-Driven Architecture

Core analysis skills drive the process. Data acquisition happens inside analysis skills, with fallback layers activated only on failure:

```
Layer 1: Core Analysis Skills (primary drivers)
  财报分析, damodaran-valuation, industry-research,
  technical-analysis, al-brooks-price-action, taleb-risk-philosophy
  → Each skill has built-in data fetching

Layer 2: Data Supplement (on-demand fallback)
  stock-data → tushare → cninfo-annual-report → paddle-ocr

Layer 3: Information Gathering (deep fallback)
  web-scraper → playwright-cli → slider-captcha-solver / Client-Side Logic Bypass

Layer 4: Output (after analysis completes)
  echarts, svg-craft, frontend-design, pyramid-principle
```

## Output Framework

All analysis converges on three investment decisions. See `references/output-schema.md` for full schema.

**1. Stock Selection (选股)** — Should I buy?
- Fundamental health score + valuation assessment + industry trend

**2. Timing (择时)** — When to buy/sell?
- Chan Theory structure + Price Action signals + risk environment

**3. Trading Plan (交易方案)** — How to execute?
- Instrument choice (stock/ETF/options/combination)
- Entry/exit conditions, position sizing, stop-loss rules

## Result Persistence

All outputs saved to `./invest-reports/{session-id}/`:

```
./invest-reports/
└── {YYYYMMDD}-{target}/
    ├── metadata.json          # session config
    ├── fundamental.md         # 基本面分析
    ├── valuation.md           # 估值分析
    ├── industry.md            # 行业分析
    ├── technical.md           # 技术分析
    ├── price-action.md        # 价格行为分析
    ├── risk.md                # 风险分析
    ├── trading-plan.md        # 交易方案
    └── report.html            # 最终汇总报告
```

## Additional Resources

### Reference Files
- **`references/routing-rules.md`** — Detailed routing decision logic and examples
- **`references/output-schema.md`** — Complete output schema for all analyst outputs and trading plan
