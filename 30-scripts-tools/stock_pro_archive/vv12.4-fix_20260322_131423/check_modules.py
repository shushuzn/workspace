import os
modules = [
    'watchlist', 'exporter', 'earnings',
    'reports', 'integrations', 'cron', 'webhook',
    'cache', 'history', 'sectors', 'risk', 'picks',
    'performance', 'validator', 'correlation', 'benchmark',
    'backtest', 'alerts', 'technical', 'sync', 'pdf_export',
    'optimizer', 'sentiment', 'screener_v2', 'dashboard',
    'watchlist_v2', 'exporters', 'insights', 'report_builder',
    'market', 'advanced_metrics', 'compare', 'earnings_analysis',
    'dividend_analysis', 'fscore', 'core', 'api'
]

for m in modules:
    f = f'{m}.py'
    exists = os.path.exists(f)
    print(f'{"OK" if exists else "MISSING"}: {f}')
