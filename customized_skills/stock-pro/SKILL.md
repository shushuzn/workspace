# Stock PRO Skill v12.4

## Description
Modular stock analysis tool with DCF valuation, portfolio management, screening, automation, and REST API.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| **12.4** | 2026-03-22 | +earnings_analysis, dividend_analysis, fscore modules |
| **12.3** | 2026-03-22 | Enhanced archive workflow v2, release workflow |
| 12.2 | 2026-03-22 | Git auto-push on archive workflow |
| 12.1 | 2026-03-22 | scoring_v2, technical, sector_rotation, backtest, compare |
| 12.0 | 2026-03-22 | Modular refactor with 39+ modules |

---

## Quick Start

### Analysis
```bash
python -m stock_pro NVDA          # Single stock
python -m stock_pro NVDA META     # Multiple stocks
python -m stock_pro --cn NVDA      # Chinese report
python -m stock_pro --json NVDA    # JSON output
```

### Comparison
```bash
python -m stock_pro --compare NVDA META AAPL
python -m stock_pro --compare-all NVDA META
python -m stock_pro --compare-risk NVDA META
python -m stock_pro --winners score
python -m stock_pro --winners upside
```

### Advanced Analysis
```bash
python -m stock_pro --quality-report NVDA META
python -m stock_pro --risk-return NVDA META
python -m stock_pro --value-growth
python -m stock_pro --metrics NVDA
python -m stock_pro --earnings
python -m stock_pro --dividend
python -m stock_pro --fscore
```

### Module Usage
```python
from stock_pro import *

analyze('NVDA')              # Full analysis
compare_stocks(['NVDA','AAPL'])  # Compare
quality_report(['NVDA'])     # Quality analysis
technical_summary('NVDA')    # Technical analysis
get_sector_rotation()        # Sector analysis
backtest_report(['NVDA'])    # Backtest
earnings_report(['NVDA'])    # Earnings forecast
dividend_report(['JNJ'])     # Dividend analysis
fscore_report(['NVDA'])     # Piotroski F-Score
```

---

## Archive + Release Workflow

### Release Workflow (Recommended)
```bash
# One command to rule them all
python release_stock_pro.py "description of changes"

# Steps:
# 1. Run tests (analyze, quality, compare, technical)
# 2. Archive current version + git commit + push
# 3. Update CHANGELOG.md and SKILL.md
# 4. Verify archive integrity
```

### Archive Commands
```bash
# Archive version
python archive_stock_pro.py archive [version] [notes]

# List archives
python archive_stock_pro.py list

# Verify integrity
python archive_stock_pro.py verify <name>

# Restore (auto backup)
python archive_stock_pro.py restore <name>

# Delete archive
python archive_stock_pro.py delete <name>

# Status
python archive_stock_pro.py status
python archive_stock_pro.py test <name>
```

### Archive Features
| Feature | Description |
|---------|-------------|
| Auto version | Reads from `__init__.py` |
| Auto detect | Analyzes git diff for changes |
| Commit types | feat/fix/refactor/docs/revert |
| Checksum | MD5 verification |
| Backup | Auto `pre_restore_TIMESTAMP` |

### Commit Format
```
{type}(stock-pro): {notes} | v{version} [{date}]
```

---

## Modules Overview

| Module | Function |
|--------|----------|
| `core.py` | Analysis engine, DCF, scoring |
| `advanced_metrics.py` | Quality, risk-return, value-growth |
| `compare.py` | Stock comparison |
| `scoring_v2.py` | Multi-model scoring |
| `technical.py` | RSI, MACD, MA, patterns |
| `sector_rotation.py` | Sector analysis |
| `backtest.py` | Strategy backtesting |
| `portfolio.py` | Portfolio management |
| `screener.py` | Stock screening |
| `watchlist.py` | Watchlist management |

---

## Data Workflow
```
collect -> review -> iterate -> archive -> consume
```

---

## Files Location
```
D:\OpenClaw\workspace\30-scripts-tools\
├── stock_pro\              # Main modules
│   ├── __init__.py        # Version 12.3
│   ├── core.py            # Analysis engine
│   ├── advanced_metrics.py
│   ├── compare.py
│   ├── scoring_v2.py
│   ├── technical.py
│   └── ... (47 modules)
├── stock_pro_archive\      # Version archives
├── archive_stock_pro.py    # Archive tool
├── git_stock_pro.py        # Git helper
└── release_stock_pro.py    # Release workflow
```
