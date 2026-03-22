# Stock PRO Changelog

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
