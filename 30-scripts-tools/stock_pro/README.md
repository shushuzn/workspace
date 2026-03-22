# Stock PRO v12.0

Modular stock analysis tool with DCF valuation, portfolio management, screening, automation, and REST API.

**All data includes timestamps** - Every result includes `fetched_at`, `price_source`, and `expires_at` for data tracking.

## Quick Start

```bash
cd D:\OpenClaw\workspace
30-scripts-tools\stock_pro.bat NVDA
```

## Data Tracking

Every analysis result includes:
| Field | Description |
|-------|-------------|
| `fetched_at` | ISO timestamp when data was fetched |
| `price_source` | "live" or "cached" |
| `expires_at` | Unix timestamp when data expires (5 min) |

## Cache & History

```bash
# Cache management
stock_pro.bat --cache-stats    # Show cache stats
stock_pro.bat --cache-clear    # Clear all cache

# History tracking
stock_pro.bat --history 7      # Show 7-day history
stock_pro.bat --trends 7       # Show 7-day trends
```

## Sector Analysis

```bash
# List all sectors
stock_pro.bat --sectors

# Analyze a sector
stock_pro.bat --sector Technology
stock_pro.bat --sector Healthcare
stock_pro.bat --sector Finance
```

## Risk & Picks

```bash
# Risk analysis
stock_pro.bat --risk NVDA META TSLA

# Diversification check
stock_pro.bat --diversify NVDA META JPM JNJ WMT

# Top picks report
stock_pro.bat --picks

# Quick picks
stock_pro.bat --quick-picks
```

## Watchlist

```bash
# List watchlists
stock_pro.bat --watchlist

# Add to watchlist
stock_pro.bat --watchlist-add NVDA tech
stock_pro.bat --watchlist-add META tech

# Remove from watchlist
stock_pro.bat --watchlist-remove NVDA tech
```

## Analytics

```bash
# Performance analysis
stock_pro.bat --performance

# Data quality report
stock_pro.bat --quality

# Full comprehensive report
stock_pro.bat --full-report

# Export all formats
stock_pro.bat --export-all

# Correlation analysis
stock_pro.bat --correlation
```

## Advanced Analytics

```bash
# Stock Screener
stock_pro.bat --screener-advanced     # Multi-factor screener
stock_pro.bat --value                 # Value stocks (low PE, high ROE)
stock_pro.bat --growth                # Growth stocks (low PEG)
stock_pro.bat --dividend              # Dividend stocks (>2% yield)

# Dashboard
stock_pro.bat --dashboard-report       # Text dashboard
stock_pro.bat --dashboard-html        # HTML dashboard

# Benchmark vs index
stock_pro.bat --benchmark NVDA META GOOGL

# Sector benchmark
stock_pro.bat --sector-benchmark

# Score distribution
stock_pro.bat --distribution

# Backtest strategy
stock_pro.bat --backtest NVDA META GOOGL

# Technical analysis
stock_pro.bat NVDA --technical

# Portfolio optimization
stock_pro.bat --optimize
stock_pro.bat NVDA META GOOGL --optimize

# Earnings
stock_pro.bat --earnings
stock_pro.bat --earnings-predict

# Sentiment analysis
stock_pro.bat --sentiment
stock_pro.bat --sector-sentiment

# Data sync
stock_pro.bat --sync NVDA AAPL MSFT
stock_pro.bat --sync-status

# Alerts management
stock_pro.bat --alerts
stock_pro.bat --alert-add NVDA score 80 above
stock_pro.bat --alert-remove NVDA

# PDF export
stock_pro.bat --pdf
stock_pro.bat NVDA META GOOGL --pdf

# Export formats
stock_pro.bat NVDA META --export-json     # JSON
stock_pro.bat NVDA META --export-md       # Markdown
stock_pro.bat NVDA META --export-html     # HTML
stock_pro.bat NVDA META --export-all-formats  # All formats

# Watchlist performance
stock_pro.bat --watchlist-perf default
stock_pro.bat --compare-lists default growth
```

## Commands

### Analysis
| Command | Description |
|---------|-------------|
| `stock_pro.bat NVDA` | Single stock analysis |
| `stock_pro.bat NVDA --cn` | Chinese report |
| `stock_pro.bat NVDA --json` | JSON output |
| `stock_pro.bat NVDA --live` | Live price (yfinance) |

### Multi-Stock
| Command | Description |
|---------|-------------|
| `--compare NVDA META JPM` | Compare stocks |
| `--summary NVDA META JPM` | Summary cards |
| `--screener` | Filter stocks |
| `--alert NVDA META` | Price alerts |

### Export
| Command | Description |
|---------|-------------|
| `--csv NVDA META` | Export to CSV |
| `--xlsx NVDA META` | Export to Excel |
| `--db NVDA` | Save to SQLite |
| `--dashboard NVDA META` | HTML dashboard |
| `--chart NVDA META` | Generate chart |

### Portfolio
| Command | Description |
|---------|-------------|
| `--portfolio` | Show portfolio |
| `--portfolio-add NVDA 100 150` | Add position |
| `--portfolio-remove NVDA` | Remove position |

### Automation
| Command | Description |
|---------|-------------|
| `--cron` | List cron jobs |
| `--cron-add "09:00" alert NVDA META` | Add scheduled job |
| `--webhook` | List webhooks |
| `--webhook-add slack https://... alert` | Add webhook |
| `--api` | Start REST API (port 8765) |

## REST API

```bash
# Start server
stock_pro.bat --api

# Endpoints
GET /                    # API info + timestamp
GET /analyze?symbol=NVDA&live=true
GET /compare?symbols=NVDA,META,JPM
GET /screener?min_score=60
GET /portfolio
POST /portfolio/add
GET /health             # Health check + timestamp
```

## Module Structure

```
stock_pro/
├── __init__.py              # Exports
├── core.py                  # Analysis engine (~92行)
├── config.py                # Config & settings (~50行)
├── reports.py               # Report generation (~180行)
├── portfolio.py             # Portfolio manager (~72行)
├── screener.py              # Stock filter (~44行)
├── screener_v2.py           # Advanced multi-factor screener (~170行)
├── integrations.py          # CSV/Excel/Chart/Dashboard (~260行)
├── cron.py                  # Cron scheduler (~148行)
├── webhook.py               # Webhook notifications (~97行)
├── api.py                   # REST API (~108行)
├── cache.py                 # Cache system (~70行)
├── history.py               # History tracking (~110行)
├── sectors.py               # Sector classification (~70行)
├── risk.py                  # Risk analysis (~120行)
├── watchlist.py             # Watchlist management (~90行)
├── watchlist_v2.py          # Enhanced watchlist (~230行)
├── picks.py                 # Top picks generator (~100行)
├── performance.py           # Performance metrics (~150行)
├── validator.py             # Data validation (~120行)
├── exporter.py              # Report exporter (~100行)
├── exporters.py            # Multi-format exporter (~160行)
├── correlation.py           # Correlation analysis (~130行)
├── benchmark.py             # Benchmarking (~120行)
├── backtest.py              # Backtesting (~110行)
├── alerts.py                # Alert management (~170行)
├── technical.py             # Technical indicators (~170行)
├── sync.py                  # Data sync (~110行)
├── pdf_export.py            # PDF/HTML export (~150行)
├── optimizer.py             # Portfolio optimization (~180行)
├── earnings.py              # Earnings calendar (~170行)
├── sentiment.py             # News sentiment (~190行)
├── dashboard.py             # Real-time dashboard (~230行)
├── yfinance_wrapper.py      # Live data (~48行)
├── main.py                  # CLI entry (~560行)
└── test.py                  # Test suite (~89行)
```

## Data Coverage

- **54 stocks** across 8 sectors
- **Sectors:** Technology (31), Finance (5), Healthcare (6), Consumer (3), Industrial (3), Energy (2), ETF (2), Technology/Auto (2)

## Output

| Type | Location |
|------|----------|
| Reports | `50-reports/stocks/*.md` |
| Charts | `50-reports/stocks/*.png` |
| CSV | `50-reports/stocks/*.csv` |
| Excel | `50-reports/stocks/*.xlsx` |
| Database | `30-scripts-tools/stock_pro.db` |
| Dashboard | `50-reports/stocks/dashboard.html` |
| Portfolio | `30-scripts-tools/stock_pro_portfolio.json` |
| Cron Jobs | `30-scripts-tools/stock_pro_cron.json` |
| Webhooks | `30-scripts-tools/stock_pro_webhooks.json` |

## Testing

```bash
py 30-scripts-tools\stock_pro\test.py
```

## Version

v11.0 - 1380 lines (62% reduction from v10.0's 3640 lines)
