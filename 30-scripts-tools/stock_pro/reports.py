"""Report generation"""
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
OUTPUT = WORKSPACE / "50-reports" / "stocks"
OUTPUT.mkdir(parents=True, exist_ok=True)

def gen_report(data, lang="en"):
    """Generate analysis report from symbol or analyze() result"""
    # Support both symbol string and analyze() dict
    if isinstance(data, str):
        from stock_pro.core import analyze
        data = analyze(data)
    sym = data["symbol"]
    cn = lang == "cn"
    f = lambda t, e: t if cn else e
    title = f"{sym} 分析报告" if cn else f"# {sym} Analysis"
    fetched = data.get('fetched_at', datetime.now().isoformat())
    src = data.get('price_source', 'cached')

    lines = [title, f"**时间:** {fetched} | **来源:** {src}\n",
             "## 估值摘要" if cn else "## Valuation",
             f"| 指标 | 数值 | 评估 |" if cn else "| Metric | Value | Assessment |",
             f"|------|------|------|" + ("-" * 20),
             f"| {'价格' if cn else 'Price'} | ${data['price']:.2f} | - |",
             f"| {'目标价' if cn else 'Target'} | ${data['target']:.2f} | - |",
             f"| {'上涨空间' if cn else 'Upside'} | {data['upside']:+.1f}% | {data['rating']} |",
             f"| {'评分' if cn else 'Score'} | {data['score']}/100 | {'优秀' if data['score'] >= 75 else '良好' if data['score'] >= 60 else '一般'} |",
             f"| P/E | {data['pe']:.1f}x | {data['recommend']} |",
             "",
             "## DCF估值" if cn else "## DCF Valuation",
             f"| {'情景' if cn else 'Scenario'} | {'估值' if cn else 'Value'} | vs Price |",
             f"| {'------|------|----------' if cn else '|-----------|-------|----------'}",
             f"| {'牛市' if cn else 'Bull'} | ${data['dcf_bull']:.2f} | {(data['dcf_bull'] /data['price'] -1) *100:+.1f}% |",
             f"| {'基准' if cn else 'Base'} | ${data['dcf_base']:.2f} | {(data['dcf_base'] /data['price'] -1) *100:+.1f}% |",
             f"| {'熊市' if cn else 'Bear'} | ${data['dcf_bear']:.2f} | {(data['dcf_bear'] /data['price'] -1) *100:+.1f}% |",
             "",
             "## 财务指标" if cn else "## Financial Metrics",
             f"| {'指标' if cn else 'Metric'} | {'数值' if cn else 'Value'} |",
             f"|------|------|",
             f"| ROE | {data['roe']:.1f}% |",
             f"| {'净利率' if cn else 'Net Margin'} | {data['pm']:.1f}% |",
             f"| {'毛利率' if cn else 'Gross Margin'} | {data['gm']:.1f}% |",
             f"| ROIC | {data['roic']:.1f}% |",
             f"| {'营收增长' if cn else 'Rev Growth'} | {data['rev_g']:.1f}% |",
             "",
             "## 风险指标" if cn else "## Risk Metrics",
             f"| Beta | {data['beta']:.2f} |",
             f"| {'股息率' if cn else 'Dividend'} | {data['div']:.2f}% |",
             f"| {'分析师评级' if cn else 'Analyst'} | {data['analyst_rating']} ({data['num_analysts']}) |",
             "",
             f"**{'建议' if cn else 'Recommendation'}:** {data['rating']} - {data['recommend']}",
             f"\n*Stock PRO v12.0*"]
    return "\n".join(lines)

def gen_compare_table(results, lang="en"):
    cn = lang == "cn"
    header = "| Symbol | Price | Target | Upside | Score | P/E | ROE |"
    sep = "|-------|-------|--------|--------|-------|-----|-----|"
    rows = []
    for r in results:
        rows.append(f"| {r['symbol']} | ${r['price']:.2f} | ${r['target']:.2f} | {r['upside']:+.1f}% | {r['score']} | {r['pe']:.0f}x | {r['roe']:.0f}% |")
    return f"{'# 对比分析\n' if cn else '# Comparison\n'}\n{header}\n{sep}\n" + "\n".join(rows)

def gen_summary_card(results, lang="en"):
    cn = lang == "cn"
    total = len(results)
    avg_score = sum(r['score'] for r in results) / total if results else 0
    avg_upside = sum(r['upside'] for r in results) / total if results else 0
    strong = len([r for r in results if r['score'] >= 75])
    buys = len([r for r in results if r['score'] >= 60])
    return f"{'# 摘要卡片\n' if cn else '# Summary Card\n'}\n" + \
           (f"**股票数量:** {total}\n" if cn else f"**Stocks:** {total}\n") + \
           f"{'**平均评分:**' if cn else '**Avg Score:**'} {avg_score:.0f}\n" + \
           f"{'**平均上涨空间:**' if cn else '**Avg Upside:**'} {avg_upside:+.1f}%\n" + \
           f"{'**强烈买入:**' if cn else '**Strong Buy:**'} {strong} | {'**买入:**' if cn else '**Buy:**'} {buys}"
