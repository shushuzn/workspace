"""
Stock PRO - Modular Stock Analysis Tool v12.0
"""
__version__ = "12.4"

# Core
from .core import analyze, analyze_multiple, fetch, fetch_live, calc_score, calc_dcf

# Data & Config
from .config import load_config, save_config
from .data_target import A
from .data_financial import F
from .data_price import P, B, E

# Reports
from .reports import gen_report, gen_compare_table, gen_summary_card

# Portfolio & Screener
from .portfolio import PortfolioManager
from .screener import StockScreener

# Integrations
from .integrations import export_csv, export_xlsx, save_db, gen_dashboard, check_alerts, gen_chart

# Automation
from .cron import CronScheduler
from .webhook import WebhookManager

# Cache & History
from .cache import get_cached, cache_stats, clear_cache
from .history import track, get_history, get_trends, history_stats

# Sectors
from .sectors import get_sector, get_symbols_by_sector, get_all_sectors, sector_report

# Risk
from .risk import risk_profile, risk_report, diversification_check

# Watchlist
from .watchlist import add_to_watchlist, remove_from_watchlist, get_watchlist, list_watchlists, create_watchlist, delete_watchlist

# Picks
from .picks import get_top_picks, get_top_picks_report, quick_picks

# Performance
from .performance import performance_report, performance_metrics, risk_adjusted_report

# Validator
from .validator import validate_stock_data, data_quality_report, check_data_freshness

# Exporter
from .exporter import full_report, export_all

# Correlation
from .correlation import correlation_report, diversification_by_correlation

# Benchmark
from .benchmark import benchmark_vs_index, sector_benchmark, score_distribution

# Alerts
from .alerts import add_alert, remove_alert, check_alerts, list_alerts

# Sync
from .sync import sync_yfinance, sync_all, get_sync_status

# PDF
from .pdf_export import export_pdf, full_pdf_report

# Optimizer
from .optimizer import optimize_report, PortfolioOptimizer

# Earnings
from .earnings import earnings_report, predict_earnings_beat, get_earnings_calendar

# Sentiment
from .sentiment import sentiment_report, sector_sentiment, calculate_sentiment

# Advanced Screener
from .screener_v2 import AdvancedScreener, advanced_screener_report, value_picks, growth_picks, dividend_picks

# Dashboard
from .dashboard import Dashboard, dashboard_report

# Watchlist v2
from .watchlist_v2 import WatchlistManager, watchlist_performance, compare_watchlists

# Exporters
from .exporters import export_json, export_markdown, export_html, export_all as export_all_formats

# Report Builder
from .report_builder import ReportBuilder, quick_report, investment_summary

# Market
from .market import get_market_overview, market_report, sector_rotation_report, market_breadth_indicator

# ADVANCED ANALYSIS (NEW)
from .advanced_metrics import get_advanced_metrics, get_all_advanced_metrics, quality_report, risk_return_report, value_vs_growth_report
from .compare import compare_stocks, compare_sectors, compare_risk, find_winners
from .scoring_v2 import get_all_scores, compare_models, get_consensus_top
from .technical import technical_summary, technical_report
from .sector_rotation import get_sector_rotation, recommend_sectors
from .backtest import backtest_report, backtest_all
from .earnings_analysis import predict_earnings_beat, earnings_report
from .dividend_analysis import calc_dividend_score, dividend_report
from .fscore import calc_fscore, fscore_report

__all__ = [
    # Core
    'analyze', 'analyze_multiple', 'fetch', 'fetch_live', 'calc_score', 'calc_dcf',
    # Data
    'A', 'F', 'P', 'B', 'E',
    # Advanced Analysis
    'quality_report', 'risk_return_report', 'value_vs_growth_report',
    'compare_stocks', 'compare_sectors', 'compare_risk', 'find_winners',
    'get_all_scores', 'compare_models', 'get_consensus_top',
    'technical_summary', 'technical_report',
    'get_sector_rotation', 'recommend_sectors',
    'backtest_report', 'backtest_all',
]
