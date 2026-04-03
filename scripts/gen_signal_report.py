#!/usr/bin/env python3
"""生成交易信号 HTML 报告"""
from analyze.stock_linker import SignalLinker
from datetime import datetime
import sqlite3

linker = SignalLinker()
all_signals = linker.get_trading_signals(min_confidence=0.6)
buys = [s for s in all_signals if s['signal'] == 'BUY']
sells = [s for s in all_signals if s['signal'] == 'SELL']

conn = sqlite3.connect('news_history.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM news')
news_count = cur.fetchone()[0]
conn.close()

now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>NewsHub 信号 {now_str[:10]}</title>
<style>
body{{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px}}
h1{{color:#222}}
.buy{{color:#16a34a}} .sell{{color:#dc2626}}
table{{width:100%;border-collapse:collapse;margin:16px 0}}
th{{text-align:left;padding:8px;border-bottom:2px solid #ddd}}
td{{padding:8px;border-bottom:1px solid #eee}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px}}
.b-buy{{background:#dcfce7;color:#16a34a}}
.b-sell{{background:#fee2e2;color:#dc2626}}
.high{{font-weight:bold}}
</style></head><body>
<h1>📊 NewsHub 信号日报</h1>
<p>{now_str} | 新闻库:{news_count}条 | 信号源:新闻情感分析</p>

<h2 style="color:#16a34a">🟢 买入信号 ({len(buys)}条)</h2>
<table><tr><th>股票</th><th>公司</th><th>置信度</th><th>新闻</th></tr>
'''

for s in buys[:15]:
    badge_class = 'b-buy high' if s['confidence'] >= 0.8 else 'b-buy'
    html += f'<tr><td class="high">{s["ticker"]}</td><td>{s.get("company","")}</td><td><span class="badge {badge_class}">{s["confidence"]:.0%}</span></td><td>{s["news_title"]}</td></tr>'

html += '</table>'

html += f'''
<h2 style="color:#dc2626">🔴 卖出信号 ({len(sells)}条)</h2>
<table><tr><th>股票</th><th>公司</th><th>置信度</th><th>新闻</th></tr>
'''

for s in sells[:15]:
    badge_class = 'b-sell high' if s['confidence'] >= 0.8 else 'b-sell'
    html += f'<tr><td class="high">{s["ticker"]}</td><td>{s.get("company","")}</td><td><span class="badge {badge_class}">{s["confidence"]:.0%}</span></td><td>{s["news_title"]}</td></tr>'

html += '</table><hr><p style="color:#888;font-size:12px">NewsHub 自动生成 | 技术分析数据暂停(网络问题)</p></body></html>'

with open('trading_signals.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'报告已生成: trading_signals.html ({len(buys)}买入/{len(sells)}卖出)')
