# invest-agent

投资分析编排插件 — 通过三级调度（L1 直答 / L2 单专家团队 / L3 多 Agent 团队）协调 20+ 个金融分析 skill，完成选股、择时、宏观周期判断与交易方案设计。

## 功能概览

| 级别 | 触发条件 | 执行方式 | 典型场景 |
|------|----------|----------|----------|
| L1 | 单 skill + 无需深度分析 | 主 agent 直接调用 skill | 查行情、查指标、概念问答 |
| L2 | 单维度 + 完整工作流 | 主 Agent + 1 位专家组成最小团队 | "分析茅台财报"、"DCF 估值比亚迪" |
| L3 | 多标的/多维度/组合分析 | TeamCreate 多 agent 团队 | "全面分析贵州茅台"、"对比茅台和五粮液" |

## 架构

```
用户请求
  │
  ├─ L1: 主 agent 直接调用 skill
  │
  ├─ L2: TeamCreate + 1 位 general-purpose 专家
  │     └─ 主 Agent 编排，单分析师执行完整流程
  │
  └─ L3: TeamCreate 三波执行
        ├─ Wave 1: 7 个分析师并行
        │   ├─ 基本面分析师 (财报分析 skill)
        │   ├─ 估值分析师 (damodaran-valuation skill)
        │   ├─ 行业分析师 (industry-research skill)
        │   ├─ 技术分析师 (technical-analysis skill)
        │   ├─ 价格行为分析师 (al-brooks-price-action skill)
        │   ├─ 风险分析师 (taleb-risk-philosophy skill)
        │   └─ 宏观周期分析师 (macro-cycle-investing skill)
        │
        ├─ Wave 2: 交易方案综合
        │   └─ 交易策划师 (读取所有分析师输出，综合判定)
        │
        └─ Wave 3: 报告生成
            └─ 报告合成师 (生成交互式 HTML 研报)
```

## 分析维度

### 选股（Should I buy?）
- **基本面**: 杜邦分解、现金流画像、造假红旗检测、四力评估
- **估值**: DCF、相对估值、叙事估值（Damodaran 10 种模式）
- **行业**: 市场空间、竞争格局、供应链、政策环境、技术趋势

### 择时（When to buy/sell?）
- **技术面**: 缠论结构分解（分型→笔→线段→中枢→走势类型）+ K 线形态
- **价格行为**: Al Brooks 框架（H1-H4/L1-L4、信号 bar 质量、市场状态识别）
- **风险**: Taleb 脆弱性光谱、肥尾分布评估、黑天鹅情景分析

### 宏观周期（Where are we in the cycle?）
- **周期定位**: 康波、房地产、中周期、库存周期与美元周期
- **环境诊断**: 债务周期、市场温度及数据端/情绪端双验证
- **资产配置**: 股票、债券、商品、现金与黄金的攻守配置建议

### 交易方案（How to execute?）
- 7 位分析师各出 trading_suggestion → 交易策划师综合判定
- 工具选择：股票/ETF/期权/组合（基于信心-不确定性矩阵）
- 完整执行计划：入场条件、仓位管理、止损止盈、风险预案

## 使用方式

```text
/invest-agent:invest-orchestrator quick 茅台PE          # L1: 快速查询
/invest-agent:invest-orchestrator deep 茅台财报          # L2: 单维度深度分析
/invest-agent:invest-orchestrator full 贵州茅台          # L3: 全维度分析 + 报告
/invest-agent:invest-orchestrator compare 茅台 五粮液    # L3: 多标的对比
```

也可以自然语言触发：
- "分析茅台" / "帮我看看比亚迪" / "研究一下宁德时代"
- "投研报告 贵州茅台"
- "对比茅台和五粮液的估值"

## 输出

所有分析结果持久化到 `./invest-reports/{YYYYMMDD}-{target}/`：

```
./invest-reports/20260426-moutai/
├── metadata.json          # 会话配置
├── fundamental.md         # 基本面分析
├── valuation.md           # 估值分析
├── industry.md            # 行业分析
├── technical.md           # 技术分析
├── price-action.md        # 价格行为分析
├── risk.md                # 风险分析
├── macro.md               # 宏观周期分析
├── trading-plan.md        # 交易方案
└── report.html            # 最终汇总报告（交互式 HTML）
```

## 依赖的 Skills

插件本身不包含分析逻辑，而是编排以下已安装的 skills：

**核心分析层**: 财报分析, damodaran-valuation, industry-research, technical-analysis, al-brooks-price-action, taleb-risk-philosophy, macro-cycle-investing

**数据补充层**: stock-data, tushare, cninfo-annual-report, paddle-ocr

**信息采集层**: web-scraper, playwright-cli, slider-captcha-solver

**输出层**: echarts, svg-craft, pyramid-principle

**思维工具**: thinkers-guide-library, systems-thinking

## 关键设计决策

1. **分析驱动架构**: 核心分析 skill 自带数据获取，数据层仅作 fallback
2. **Plugin Agent 不可直接调用**: Agent tool 的 `subagent_type` 不支持 plugin agent，L2/L3 均使用 `general-purpose` + `bypassPermissions` 组建团队
3. **所有输出使用中文**: 9 个 agent 系统提示均包含中文输出要求
4. **三波严格顺序**: Wave 1 全部完成 → Wave 2 → Wave 3，波间可人工介入

## 插件结构

```
invest-agent/
├── .claude-plugin/
│   └── plugin.json              # 插件清单
├── agents/                      # 9 个 agent 定义（供 Claude 自动匹配）
│   ├── fundamental-analyst.md
│   ├── valuation-analyst.md
│   ├── industry-analyst.md
│   ├── technical-analyst.md
│   ├── price-action-analyst.md
│   ├── risk-analyst.md
│   ├── macro-analyst.md
│   ├── trade-planner.md
│   └── report-synthesizer.md
├── hooks/
│   └── hooks.json               # SubagentStop 输出验证 hook
├── scripts/
│   └── init-workspace.py        # 工作区初始化脚本
├── skills/
│   └── invest-orchestrator/
│       ├── SKILL.md             # 编排技能主文件
│       └── references/
│           ├── routing-rules.md # 路由决策详细规则
│           └── output-schema.md # 输出格式完整 schema
├── .gitignore
└── README.md
```
