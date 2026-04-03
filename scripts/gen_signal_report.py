#!/usr/bin/env python3
"""生成交易信号 HTML 报告（按股票聚合）"""
from analyze.stock_linker import SignalLinker
from datetime import datetime
import sqlite3
from collections import defaultdict

linker = SignalLinker()
all_signals = linker.get_trading_signals(min_confidence=0.6)
buys = [s for s in all_signals if s['signal'] == 'BUY']
sells = [s for s in all_signals if s['signal'] == 'SELL']

conn = sqlite3.connect('news_history.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM news')
news_count = cur.fetchone()[0]
conn.close()

# 按 ticker 聚合
def aggregate(signals):
    grouped = defaultdict(lambda: {'confidence': 0, 'news': [], 'company': ''})
    for s in signals:
        t = s['ticker']
        grouped[t]['confidence'] = max(grouped[t]['confidence'], s['confidence'])
        grouped[t]['company'] = s.get('company', '')
        grouped[t]['news'].append(s['news_title'])
    result = []
    for ticker, data in grouped.items():
        result.append({
            'ticker': ticker,
            'company': data['company'],
            'confidence': data['confidence'],
            'news_count': len(data['news']),
            'top_news': data['news'][0],
        })
    result.sort(key=lambda x: (-x['confidence'], -x['news_count']))
    return result

buys_agg = aggregate(buys)
sells_agg = aggregate(sells)

now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>NewsHub 信号 {now_str[:10]}</title>
<style>
body{{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px}}
h1{{color:#222}}
table{{width:100%;border-collapse:collapse;margin:16px 0}}
th{{text-align:left;padding:8px;border-bottom:2px solid #ddd;background:#fafafa}}
td{{padding:8px;border-bottom:1px solid #eee}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px}}
.b-buy{{background:#dcfce7;color:#16a34a}}
.b-sell{{background:#fee2e2;color:#dc2626}}
.high{{font-weight:bold}}
.count{{color:#888;font-size:12px}}
.trend-up{{color:#16a34a}} .trend-down{{color:#dc2626}}
</style></head><body>
<h1>📊 NewsHub 信号日报</h1>
<p>{now_str} | 新闻库:{news_count}条 | 信号:新闻情感分析(无技术指标)</p>

<h2 style="color:#16a34a">🟢 买入信号 ({len(buys_agg)}只股票)</h2>
<table><tr><th>股票</th><th>公司</th><th>置信度</th><th>新闻数</th><th>最新新闻</th></tr>
'''
for s in buys_agg[:15]:
    badge_class = 'b-buy high' if s['confidence'] >= 0.8 else 'b-buy'
    count_str = f'<span class="count">×{s["news_count"]}条</span>' if s['news_count'] > 1 else ''
    html += f'<tr><td class="high">{s["ticker"]}</td><td>{s["company"]}</td><td><span class="badge {badge_class}">{s["confidence"]:.0%}</span>{count_str}</td><td>{s["news_count"]}</td><td>{s["top_news"][:50]}</td></tr>'

html += '</table>'

html += f'''
<h2 style="color:#dc2626">🔴 卖出信号 ({len(sells_agg)}只股票)</h2>
<table><tr><th>股票</th><th>公司</th><th>置信度</th><th>新闻数</th><th>最新新闻</th></tr>
'''
for s in sells_agg[:15]:
    badge_class = 'b-sell high' if s['confidence'] >= 0.8 else 'b-sell'
    count_str = f'<span class="count">×{s["news_count"]}条</span>' if s['news_count'] > 1 else ''
    html += f'<tr><td class="high">{s["ticker"]}</td><td>{s["company"]}</td><td><span class="badge {badge_class}">{s["confidence"]:.0%}</span>{count_str}</td><td>{s["news_count"]}</td><td>{s["top_news"][:50]}</td></tr>'

html += '</table><hr><p style="color:#888;font-size:12px">NewsHub 自动生成 | 技术分析暂停(网络问题) | 信号按股票去重聚合</p></body></html>'

import json

# 导出 JSON
report_data = {
    'generated_at': now_str,
    'news_count': news_count,
    'source': 'news_sentiment_only',
    'buy_signals': buys_agg,
    'sell_signals': sells_agg,
}

with open('trading_signals.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

with open('trading_signals.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'报告已生成: trading_signals.html ({len(buys_agg)}只买入/{len(sells_agg)}只卖出)')
print(f'数据已导出: trading_signals.json')
