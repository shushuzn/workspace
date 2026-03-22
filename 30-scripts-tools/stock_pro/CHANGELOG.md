# Stock PRO Changelog

## [13.0] - 2026-03-22
### New Features
- `picks.py`: New module with quick stock screening
  - `top_picks(n)` - Top N overall picks
  - `value_picks()` - Best value stocks
  - `growth_picks()` - Fastest growing stocks
  - `dividend_picks()` - Best dividend stocks
  - `momentum_picks()` - Best momentum stocks

### UI
- `simple_ui.py`: Simple HTML UI (no install required)
- `dash_app.py`: Full Dash UI with charts
- `install_dash.py`: Dash installation helper

### Performance
- All pick functions use parallel analysis

## [12.9] - 2026-03-22
### Performance Optimizations
- `core.py`: Added `fetch_batch()` for batch API calls
- `core.py`: Optimized `analyze_multiple_parallel()` with batch fetch
- `screener.py`: Replaced sequential loop with parallel analysis
- New `prewarm_cache()` function for cache warming

### Compatibility Fixes
- Added `dcf_base`, `dcf_bull`, `dcf_bear` fields to analyze()
- Added `recommend`, `rev_g`, `analyst_rating` fields to analyze()
- Fixed report generation compatibility

## [12.3] - 2026-03-22
### Enhanced
- Archive workflow v2: auto versioning, checksum verification, commit types
- New modules: scoring_v2, technical, sector_rotation, backtest, compare

### Archive Tool Features
- Auto-detect version from `__init__.py`
- Auto-detect commit type (feat/fix/refactor/docs)
- Auto-generate change summary
- MD5 checksum verification
- Auto backup before restore
- Standardized commit messages

## [12.2] - 2026-03-22
### Added
- Git auto-push on archive workflow

## [12.1] - 2026-03-22
### Added
- `scoring_v2.py` - Multi-model scoring system
- `technical.py` - Technical analysis (RSI/MACD/MA)
- `sector_rotation.py` - Sector rotation analysis
- `backtest.py` - Strategy backtesting
- `compare.py` - Stock comparison tools

## [12.0] - 2026-03-22
### Refactored
- Modular refactor: 39+ Python modules
- Split monolithic `stock_pro_v4.py` into separate modules
- New write_helper.py for files >8KB
