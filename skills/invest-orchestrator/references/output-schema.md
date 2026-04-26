# Output Schema Reference

Define the complete output schema for all analyst agents and the trading plan synthesis. Every analyst writes a structured markdown file to the session workspace. The trade-planner and report-synthesizer consume these files downstream.

---

## Analyst Output Schema

Each analyst agent MUST produce a markdown file conforming to the schema below. Use H2/H3 headers as section delimiters. Embed structured data in fenced YAML blocks.

---

### fundamental.md (基本面分析师)

#### 分析结论

```yaml
summary: <one-paragraph verdict>
health_score: <1-10 integer>
key_findings:
  - <finding 1>
  - <finding 2>
  - ...
```

#### 详细分析

```yaml
balance_sheet:
  total_assets: <number>
  total_liabilities: <number>
  equity: <number>
  asset_liability_ratio: <percentage>
  current_ratio: <number>
  quick_ratio: <number>
  commentary: <string>

income_statement:
  revenue: <number>
  revenue_growth_yoy: <percentage>
  gross_margin: <percentage>
  operating_margin: <percentage>
  net_margin: <percentage>
  eps: <number>
  commentary: <string>

cash_flow:
  archetype: <string>  # e.g. "奶牛型", "投资型", "衰退型"
  operating_cf: <number>
  investing_cf: <number>
  financing_cf: <number>
  free_cash_flow: <number>
  commentary: <string>

dupont_decomposition:
  roe: <percentage>
  net_profit_margin: <percentage>
  asset_turnover: <number>
  equity_multiplier: <number>
  trend: <improving|stable|deteriorating>

red_flags:
  - flag: <description>
    severity: <low|medium|high>
  - ...
```

#### trading_suggestion

```yaml
direction: 做多|做空|观望
instrument: <stock_code or description>
position_rationale: <string>
confidence: <1-10 integer>
```

---

### valuation.md (估值分析师)

#### 分析结论

```yaml
valuation_summary: <one-paragraph verdict>
fair_value_range:
  low: <number>
  mid: <number>
  high: <number>
current_price: <number>
current_vs_fair: <premium or discount percentage>
```

#### 详细分析

```yaml
dcf:
  method: fcff|fcfe|ddm
  wacc: <percentage>
  cost_of_equity: <percentage>
  terminal_growth_rate: <percentage>
  terminal_value: <number>
  enterprise_value: <number>
  equity_value_per_share: <number>
  sensitivity_matrix:
    rows_label: "WACC"
    cols_label: "Terminal Growth"
    row_values: [<wacc_1>, <wacc_2>, ...]
    col_values: [<g_1>, <g_2>, ...]
    values:
      - [<v11>, <v12>, ...]
      - [<v21>, <v22>, ...]

relative:
  pe:
    current: <number>
    peer_median: <number>
    percentile_5y: <percentage>
  pb:
    current: <number>
    peer_median: <number>
    percentile_5y: <percentage>
  ev_ebitda:
    current: <number>
    peer_median: <number>
    percentile_5y: <percentage>
  peers:
    - code: <string>
      name: <string>
      pe: <number>
      pb: <number>
      ev_ebitda: <number>

narrative_valuation:
  story: <string>
  narrative_fair_value: <number>
  key_assumptions:
    - <assumption 1>
    - <assumption 2>
```

#### trading_suggestion

```yaml
direction: 做多|做空|观望
instrument: <stock_code or description>
price_range:
  entry_low: <number>
  entry_high: <number>
confidence: <1-10 integer>
```

---

### industry.md (行业分析师)

#### 分析结论

```yaml
industry_stage: introduction|growth|maturity|decline
outlook: <one-paragraph outlook>
key_drivers:
  - <driver 1>
  - <driver 2>
  - ...
```

#### 详细分析

```yaml
market_size:
  value: <number>
  unit: <亿元|billion_usd|...>
  year: <YYYY>

growth_rate:
  historical_cagr_5y: <percentage>
  forecast_cagr_3y: <percentage>
  source: <string>

competitive_landscape:
  concentration: <CR5 percentage>
  top_players:
    - name: <string>
      market_share: <percentage>
  moat_type: <economies_of_scale|network_effect|brand|regulation|none>

pest_analysis:
  political: <string>
  economic: <string>
  social: <string>
  technological: <string>

value_chain:
  upstream: <string>
  midstream: <string>
  downstream: <string>
  target_position: <string>
```

#### trading_suggestion

```yaml
direction: 做多|做空|观望
instrument_preference: individual_stock|etf|index
confidence: <1-10 integer>
```

---

### technical.md (技术分析师)

#### 分析结论

```yaml
trend_structure:
  description: <Chan Theory structural summary>
  current_level: <5m|15m|30m|60m|daily|weekly>
  trend_type: 上涨|下跌|盘整

pattern_signals:
  - pattern: <K-line Golden Laws pattern name>
    signal: 买入|卖出|中性
    reliability: <1-10 integer>

buy_sell_points:
  - type: 一买|二买|三买|一卖|二卖|三卖
    price: <number>
    confirmed: <true|false>
```

#### 详细分析

```yaml
chan_analysis:
  level: <analysis timeframe level>
  trend_type: 上涨|下跌|盘整
  pivot_zone:
    high: <number>
    low: <number>
  divergence:
    type: 顶背驰|底背驰|none
    strength: <weak|moderate|strong>

kline_patterns:
  - name: <string>
    timeframe: <string>
    location: <string>
    implication: 看多|看空|中性

ma_state:
  ma5: <number>
  ma10: <number>
  ma20: <number>
  ma60: <number>
  alignment: 多头排列|空头排列|交织

volume_price:
  volume_trend: 放量|缩量|平量
  price_volume_relationship: <string>

main_force_behavior:
  accumulation_distribution: 吸筹|派发|洗盘|无明显迹象
  evidence: <string>
```

#### trading_suggestion

```yaml
direction: 做多|做空|观望
entry_zone:
  low: <number>
  high: <number>
stop_loss: <number>
target: <number>
signal_strength: <weak|moderate|strong>
confidence: <1-10 integer>
```

---

### price-action.md (价格行为分析师)

#### 分析结论

```yaml
market_state:
  type: trend|trading_range
  subtype: <strong_trend|weak_trend|tight_range|wide_range|...>
direction_probability:
  up: <percentage>
  down: <percentage>
  sideways: <percentage>
```

#### 详细分析

```yaml
key_structures:
  trend_lines:
    - type: <support|resistance>
      slope: <ascending|descending|horizontal>
      price_at_current_bar: <number>
      touches: <integer>
  channel_lines:
    - type: <bull_channel|bear_channel|horizontal_channel>
      upper: <number>
      lower: <number>
  ema_relationship:
    ema20: <number>
    ema50: <number>
    ema200: <number>
    price_vs_ema20: <above|below|at>
    gap_width: <wide|narrow|crossing>

setups:
  - name: <string>  # e.g. "H2", "L2", "wedge_bull_flag", "double_bottom"
    status: triggered|pending|failed
    entry_bar: <string>
    probability: <percentage>

signal_bar_quality:
  bar_type: <bull_reversal|bear_reversal|doji|inside_bar|outside_bar|...>
  body_ratio: <percentage>
  tail_ratio: <percentage>
  close_position: <upper_third|middle|lower_third>
  quality: <strong|moderate|weak>
```

#### trading_suggestion

```yaml
direction: 做多|做空|观望
entry_method: stop|limit
entry_price: <number>
stop: <number>
scalp_target: <number>
swing_target: <number>
confidence: <1-10 integer>
```

---

### risk.md (风险分析师)

#### 分析结论

```yaml
fragility_assessment: fragile|robust|antifragile
risk_level: <low|medium|high|extreme>
tail_risk_probability: <percentage>
```

#### 详细分析

```yaml
fragility_spectrum:
  score: <-10 to +10>  # negative = fragile, 0 = robust, positive = antifragile
  factors:
    - factor: <string>
      contribution: <fragile|robust|antifragile>
      weight: <number>

extremistan_vs_mediocristan:
  classification: extremistan|mediocristan
  reasoning: <string>
  fat_tail_indicators:
    - <indicator 1>
    - <indicator 2>

black_swan_scenarios:
  - scenario: <string>
    probability: <very_low|low|medium>
    impact: <catastrophic|severe|moderate>
    exposure: <string>

current_volatility_regime:
  regime: <low_vol|normal|high_vol|crisis>
  historical_vol_30d: <percentage>
  implied_vol: <percentage>
  vol_of_vol: <number>
  regime_change_signal: <true|false>
```

#### trading_suggestion

```yaml
hedge_needed: yes|no
hedge_instrument: <string>  # e.g. "put options on index", "VIX calls"
hedge_rationale: <string>
confidence: <1-10 integer>
```

---

## Trading Plan Schema (trading-plan.md)

trade-planner MUST synthesize all analyst suggestions into a single actionable plan with the following sections.

### 综合判定

```yaml
direction: 做多|做空|观望
confidence_score: <1-10 integer>
consensus_analysis:
  agree:
    - analyst: <name>
      direction: <string>
      confidence: <integer>
  disagree:
    - analyst: <name>
      direction: <string>
      confidence: <integer>
  reasoning: <string>
dissent_points:
  - point: <string>
    raised_by: <analyst name>
    interpretation: <string>
```

### 交易工具选择

```yaml
recommended_instrument: stock|etf|options|combination
selection_rationale: <string>

# Include the following block only when recommended_instrument includes "options"
options_detail:
  strategy_type: protective_put|covered_call|straddle|barbell|custom
  legs:
    - contract: <string>
      strike: <number>
      expiry: <YYYY-MM-DD>
      quantity: <integer>
      direction: buy|sell
  greeks:
    delta: <number>
    gamma: <number>
    vega: <number>
    theta: <number>
  max_loss: <number>
  max_profit: <number or "unlimited">
  breakeven:
    - <price>
```

### 执行计划

```yaml
entry_conditions:
  price_triggers:
    - condition: <string>
      price: <number>
  event_triggers:
    - condition: <string>
  time_triggers:
    - condition: <string>

entry_price_range:
  low: <number>
  high: <number>

position_size:
  percentage_of_portfolio: <percentage>
  absolute_amount: <number>  # optional

scaling_strategy:
  method: all_at_once|scale_in
  tranches:  # only when method = scale_in
    - percentage: <percentage>
      trigger: <string>
    - percentage: <percentage>
      trigger: <string>

stop_loss:
  price: <number>
  type: hard|trailing
  rationale: <string>

take_profit:
  targets:
    - price: <number>
      percentage_to_close: <percentage>
      rationale: <string>
    - price: <number>
      percentage_to_close: <percentage>
      rationale: <string>

exit_conditions:
  thesis_invalidation:
    - condition: <string>
      action: <string>
```

### 风险预案

```yaml
if_wrong_plan:
  stop_hit_action: <string>
  reassessment_trigger: <string>
  max_reentry_attempts: <integer>

black_swan_response:
  scenario: <string>
  immediate_action: <string>
  recovery_plan: <string>

max_acceptable_loss:
  absolute: <number>
  percentage: <percentage>

hedge_overlay:
  needed: <true|false>
  instrument: <string>
  size: <string>
  trigger: <string>
```

---

## Report Schema (report.html)

report-synthesizer MUST compile all analyst outputs and the trading plan into a single HTML report. Structure the report as follows:

1. **Executive Summary** -- Include 选股结论, 择时结论, and 交易方案 in a concise overview block at the top.
2. **Per-Dimension Analysis Sections** -- One section per analyst dimension. Embed ECharts charts for quantitative data (sensitivity matrices, price charts, volatility regimes, etc.).
3. **Trading Plan Detail** -- Render the full trading plan with entry/exit visualization.
4. **Risk Dashboard** -- Consolidate risk analyst output into a visual dashboard (fragility gauge, scenario table, volatility regime indicator).
5. **Data Sources and Methodology Notes** -- List all data sources, timestamps, and methodology descriptions used by each analyst.

Use responsive layout. Inline all CSS and JS (ECharts via CDN). Produce a single self-contained HTML file.

---

## metadata.json Schema

Write a `metadata.json` file at the session workspace root to track orchestration state.

```json
{
  "session_id": "YYYYMMDD-target",
  "created_at": "ISO 8601 timestamp",
  "target": "stock_code or industry name",
  "dispatch_level": "L1|L2|L3",
  "dimensions_analyzed": ["fundamental", "valuation", "industry", "technical", "price_action", "risk"],
  "analysts_used": ["fundamental-analyst", "valuation-analyst", "industry-analyst", "technical-analyst", "price-action-analyst", "risk-analyst"],
  "status": "in_progress|completed|partial",
  "duration_seconds": 0,
  "errors": []
}
```

| Field                 | Type     | Description                                        |
|-----------------------|----------|----------------------------------------------------|
| `session_id`          | string   | Unique session identifier, format YYYYMMDD-target  |
| `created_at`          | string   | ISO 8601 timestamp of session creation             |
| `target`              | string   | Analysis target (stock code or industry name)      |
| `dispatch_level`      | string   | Dispatch complexity level: L1, L2, or L3           |
| `dimensions_analyzed` | string[] | List of dimensions that were actually analyzed      |
| `analysts_used`       | string[] | List of analyst agent names that were dispatched    |
| `status`              | string   | Current session status                             |
| `duration_seconds`    | number   | Total elapsed time in seconds                      |
| `errors`              | string[] | Any errors encountered during the session          |
