# Stock PRO Skill v12.2

## Description
Modular stock analysis tool with DCF valuation, portfolio management, screening, automation, and REST API.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| v12.2 | 2026-03-22 | Added git auto-push to archive workflow |
| v12.1 | 2026-03-22 | Added scoring_v2, technical, sector_rotation, backtest, compare |
| v12.0 | 2026-03-22 | Modular refactor with 39+ modules |

## Archive + Git Workflow
```bash
# 1. 开发完成 → 归档并自动推送
python archive_stock_pro.py archive <version> [notes]

# 2. 查看归档列表
python archive_stock_pro.py list

# 3. 恢复旧版本
python archive_stock_pro.py restore <name>

# 4. Git 状态
python archive_stock_pro.py status
python git_stock_pro.py status    # 详细状态
python git_stock_pro.py log 10   # 最近10次提交

# 5. 手动 Git 操作
python git_stock_pro.py commit "message"
python git_stock_pro.py push
```

### 工作流
```
开发新功能 → 测试通过 → archive 归档 → 自动 git commit → 自动 git push
```

## Usage
```
stock-pro <symbol> [--cn] [--json] [--live]
stock-pro --compare <symbols...>
stock-pro --summary <symbols...>
stock-pro --screener
stock-pro --portfolio [--add <sym> <shares> <cost>] [--remove <sym>]
stock-pro --alert <symbols...>
stock-pro --chart <symbols...>
stock-pro --csv <symbols...>
stock-pro --xlsx <symbols...>
stock-pro --db <symbols...>
stock-pro --dashboard <symbols...>
stock-pro --cron [--add <schedule> <cmd> <symbols>]
stock-pro --webhook [--add <name> <url> <events>]
stock-pro --api
stock-pro --market
stock-pro --sector-rotation
stock-pro --market-breadth
stock-pro --quick-report
stock-pro --investment-summary
stock-pro --insights
stock-pro --themes
```

## Examples
```bash
# Analysis
stock-pro NVDA              # English report
stock-pro NVDA --cn         # Chinese report
stock-pro NVDA --json       # JSON output
stock-pro NVDA --live       # Live price

# Multi-stock
stock-pro --compare NVDA META JPM
stock-pro --summary NVDA META JPM

# Market Analysis
stock-pro --market
stock-pro --sector-rotation
stock-pro --market-breadth
stock-pro --quick-report
stock-pro --investment-summary

# Insights
stock-pro --insights
stock-pro --themes

# Quality & Advanced
stock-pro --quality-report NVDA META
stock-pro --risk-return NVDA META AAPL
stock-pro --value-growth
stock-pro --metrics NVDA

# Comparison
stock-pro --compare-all NVDA META AAPL
stock-pro --compare-risk NVDA META AAPL KO
stock-pro --winners score
stock-pro --winners upside

# Tools
stock-pro --screener
stock-pro --portfolio
stock-pro --portfolio-add NVDA 100 150
stock-pro --alert NVDA META JPM
stock-pro --chart NVDA META JPM

# Automation
stock-pro --cron-add "09:00" alert NVDA META
stock-pro --webhook-add slack https://hooks.slack.com/... alert
stock-pro --api
```

## REST API
```bash
GET  /analyze?symbol=NVDA
GET  /compare?symbols=NVDA,META
GET  /screener?min_score=60
GET  /portfolio
POST /portfolio/add {"symbol": "NVDA", "shares": 100, "cost": 150}
```

## Output
| Type | Location |
|------|----------|
| Reports | `50-reports/stocks/*.md` |
| Charts | `50-reports/stocks/*.png` |
| CSV | `50-reports/stocks/*.csv` |
| Database | `30-scripts-tools/stock_pro.db` |
| Dashboard | `50-reports/stocks/dashboard.html` |

## CoPaw Triggers
- "analyze NVDA"
- "stock comparison NVDA META"
- "screen stocks"
- "show portfolio"
- "NVDA chart"
- "NVDA alert"
- "start stock api"
