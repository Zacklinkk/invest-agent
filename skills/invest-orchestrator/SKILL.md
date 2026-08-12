---
name: invest-orchestrator
description: This skill should be used when the user invokes "/invest", or asks to "投资分析", "股票研究", "深度研究", "个股分析", "估值对比", "选股", "择时", "交易方案", "组合分析", "行业对比", "研究一下", "投研报告", "帮我看看这只股票", "宏观分析", "周期分析", "周期定位", "大类资产配置", "stock analysis", "investment research". Orchestrates multiple financial analysis skills via three-level dispatch (L1 direct, L2 single expert, L3 multi-agent team).
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

### L2 — Single Expert Team (two-agent team)

**Trigger**: single analysis dimension + full workflow needed.

Create a minimal team with the orchestrator (you) as team lead and one analyst teammate.

| Intent | Analyst Name | Analyst Role | Primary Skill | Output File |
|--------|-------------|-------------|---------------|-------------|
| 财报分析 | fundamental-analyst | 基本面分析专家 | 财报分析 | fundamental.md |
| 估值分析 | valuation-analyst | 估值分析专家 | damodaran-valuation | valuation.md |
| 行业研究 | industry-analyst | 行业研究专家 | industry-research | industry.md |
| 技术分析 | technical-analyst | 技术分析专家 | technical-analysis | technical.md |
| 价格行为 | price-action-analyst | 价格行为专家 | al-brooks-price-action | price-action.md |
| 风险评估 | risk-analyst | 风险分析专家 | taleb-risk-philosophy | risk.md |
| 宏观周期 | macro-analyst | 宏观周期分析专家 | macro-cycle-investing | macro.md |

**L2 Team Workflow:**

```
1. TeamCreate(team_name="invest-{target}-{date}")

2. Agent(
     subagent_type="general-purpose",
     mode="bypassPermissions",
     name="{analyst-name}",
     team_name="invest-{target}-{date}",
     prompt="你是{角色}，团队中的分析专家。分析标的：{target}。
       1. 调用 {skill} skill 执行完整分析流程
       2. 所有输出必须使用中文
       3. 将完整分析结果写入 {output_dir}/{filename}.md（不截断）
       4. 结尾必须包含 trading_suggestion YAML 块
       5. 完成后通过 SendMessage 向 team-lead 报告摘要
       重要：分析必须详尽完整，不设长度限制。"
   )

3. Wait for analyst message → present results to user

4. SendMessage(to="{analyst-name}", message={type:"shutdown_request"})

5. TeamDelete()
```

### L3 — Full Agent Team (multi-agent team with wave coordination)

**Trigger**:
- Multiple targets (≥2 stocks to compare)
- Multiple dimensions with cross-dependencies
- Portfolio-level analysis
- User explicitly specifies `full` or `compare`

**Team Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  Team Lead (you - the orchestrator)                     │
│  - Creates team & task list                             │
│  - Spawns teammates per wave                            │
│  - Monitors via automatic message delivery              │
│  - Controls wave transitions via SendMessage            │
│  - Presents results & handles user intervention         │
└────────────────────┬────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────────────┐
     │               │                       │
  Wave 1          Wave 2                  Wave 3
  (parallel)      (sequential)            (sequential)
     │               │                       │
  ┌──┴──┐           │                       │
  │ 7 analysts │     │                       │
  │ each writes│  trade-planner          report-synthesizer
  │ to shared  │  reads all .md →        reads all files →
  │ output dir │  trading-plan.md        report.html
  └─────┘           │                       │
```

**Strict Three-Wave Execution:**

```
Wave 1: Analysts (parallel, 7 teammates)
  → fundamental-analyst    → fundamental.md
  → valuation-analyst      → valuation.md
  → industry-analyst       → industry.md
  → technical-analyst      → technical.md
  → price-action-analyst   → price-action.md
  → risk-analyst           → risk.md
  → macro-analyst          → macro.md

Wave 2: Trading Synthesis (after Wave 1 completes, 1 teammate)
  → trade-planner          → trading-plan.md

Wave 3: Report Generation (after Wave 2 completes, 1 teammate)
  → report-synthesizer     → report.html
```

**Team Setup & Execution Steps:**

```
Step 1: Initialize workspace
  python ~/.claude/plugins/local/invest-agent/scripts/init-workspace.py <target>

Step 2: Create team
  TeamCreate(team_name="invest-{target}-{date}")

Step 3: Spawn Wave 1 — all 7 analysts in parallel
  For each analyst, use a SINGLE Agent() call with:
    - subagent_type: "general-purpose"
    - mode: "bypassPermissions"
    - name: "{analyst-name}"           ← addressable teammate name
    - team_name: "invest-{target}-{date}"
    - prompt: (see Teammate Prompt Template below)

Step 4: Monitor Wave 1
  - Messages arrive automatically from each analyst
  - Track completion: all 7 must report "analysis complete"
  - If any analyst errors → retry or skip with note

Step 5: User checkpoint (between Wave 1 and 2)
  - Present summary of all analyst findings
  - Ask: "7维分析完成，是否继续生成交易方案？需要调整方向吗？"

Step 6: Spawn Wave 2 — trade-planner
  Agent(
    subagent_type="general-purpose",
    mode="bypassPermissions",
    name="trade-planner",
    team_name="invest-{target}-{date}",
    prompt="你是交易方案规划专家。
      1. 读取 {output_dir}/ 下所有分析师 .md 文件
      2. 综合7维分析结论，生成完整交易方案
      3. 写入 {output_dir}/trading-plan.md
      4. 完成后 SendMessage 向 team-lead 报告摘要"
  )

Step 7: User checkpoint (between Wave 2 and 3)
  - Present trading plan summary
  - Ask: "交易方案已生成，是否继续生成最终报告？"

Step 8: Spawn Wave 3 — report-synthesizer
  Agent(
    subagent_type="general-purpose",
    mode="bypassPermissions",
    name="report-synthesizer",
    team_name="invest-{target}-{date}",
    prompt="你是投研报告合成专家。
      1. 读取 {output_dir}/ 下所有文件（含 trading-plan.md）
      2. 调用 echarts skill 生成数据可视化
      3. 调用 pyramid-principle skill 组织报告结构
      4. 生成完整 HTML 报告写入 {output_dir}/report.html
      5. 完成后 SendMessage 向 team-lead 报告"
  )

Step 9: Present final report to user

Step 10: Shutdown all teammates
  SendMessage(to="*", message={type:"shutdown_request", reason:"分析完成"})

Step 11: Clean up
  TeamDelete()
```

**Teammate Prompt Template (Wave 1 Analysts):**

```
你是{角色}，invest-{target}-{date} 团队的分析专家。

## 任务
分析标的：{target}

## 执行步骤
1. 调用 {skill} skill 执行完整分析流程
2. 所有输出必须使用中文
3. 将完整分析结果写入 {output_dir}/{filename}.md
4. 文件结尾必须包含 trading_suggestion YAML 块
5. 完成后通过 SendMessage(to="team-lead") 发送简短摘要（3-5句话）

## 输出要求
- 分析必须详尽完整，不设长度限制
- 所有数据、推理过程、结论都写入文件
- SendMessage 只发摘要，完整内容在文件中

## 协作规则
- 你的分析结果会被 trade-planner 和 report-synthesizer 在后续 wave 读取
- 确保 trading_suggestion YAML 格式正确，便于下游解析
- 如遇数据获取失败，在文件中标注并降低 confidence
```

**Critical: Agent Team Configuration**
- `subagent_type` must be `"general-purpose"` (plugin agents cannot be invoked via subagent_type)
- `mode` must be `"bypassPermissions"` to ensure Bash/Python execution rights
- `name` must be set for each agent (enables SendMessage addressing)
- `team_name` must match the TeamCreate name (joins agents to shared task list)
- Agent prompts must explicitly reference which skill(s) to invoke via the Skill tool

**User Intervention:** Between each wave, present intermediate results and ask if user wants to adjust direction before proceeding. This is a mandatory checkpoint — do not auto-advance waves without user confirmation.

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
  technical-analysis, al-brooks-price-action, taleb-risk-philosophy,
  macro-cycle-investing
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
    ├── macro.md               # 宏观周期分析
    ├── trading-plan.md        # 交易方案
    └── report.html            # 最终汇总报告
```

## Additional Resources

### Reference Files
- **`references/routing-rules.md`** — Detailed routing decision logic and examples
- **`references/output-schema.md`** — Complete output schema for all analyst outputs and trading plan
