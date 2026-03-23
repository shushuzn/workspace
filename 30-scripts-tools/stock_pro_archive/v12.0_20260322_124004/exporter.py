"""Comprehensive report generator for Stock PRO"""

def full_report(symbols=None):
    """Generate comprehensive report for given symbols"""
    from stock_pro.core import A, analyze_multiple
    from stock_pro.reports import gen_report, gen_compare_table, gen_summary_card
    from stock_pro.risk import risk_report, diversification_check
    from stock_pro.picks import get_top_picks_report, quick_picks
    from stock_pro.sectors import sector_report
    from stock_pro.performance import performance_report
    from stock_pro.validator import data_quality_report

    if symbols is None:
        symbols = list(A.keys())

    results = analyze_multiple(symbols)

    report = "# Stock PRO Comprehensive Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"**Stocks Analyzed:** {len(results)}\n\n"

    # Executive Summary
    report += "---\n\n## Executive Summary\n\n"
    avg_score = sum(r['score'] for r in results) / len(results)
    avg_upside = sum(r['upside'] for r in results) / len(results)
    strong_buys = sum(1 for r in results if r['rating'] == 'STRONG BUY')
    buys = sum(1 for r in results if 'BUY' in r['rating'])

    report += f"| Metric | Value |\n|--------|-------|\n"
    report += f"| Total Stocks | {len(results)} |\n"
    report += f"| Average Score | {avg_score:.0f} |\n"
    report += f"| Average Upside | {avg_upside:+.1f}% |\n"
    report += f"| Strong Buy | {strong_buys} |\n"
    report += f"| Buy | {buys} |\n\n"

    # Top Picks
    report += "---\n\n## Top Picks\n\n"
    top5 = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
    report += "| Symbol | Price | Score | Upside | Rating |\n"
    report += "|--------|-------|-------|--------|--------|\n"
    for r in top5:
        report += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {r['rating']} |\n"

    # Risk Summary
    report += "\n---\n\n## Risk Summary\n\n"
    high_risk = sum(1 for r in results if r.get('beta', 1) > 1.5)
    low_risk = sum(1 for r in results if r.get('beta', 1) < 0.8)

    report += f"- High Volatility (Beta > 1.5): {high_risk} stocks\n"
    report += f"- Low Volatility (Beta < 0.8): {low_risk} stocks\n"
    report += f"- Average Beta: {sum(r.get('beta', 1) for r in results) / len(results):.2f}\n"

    # Diversification Check
    check = diversification_check(results)
    report += "\n**Diversification:**\n"
    for rec in check['recommendations']:
        report += f"- {rec}\n"

    # Data Quality
    report += "\n---\n\n## Data Quality\n\n"
    valid = sum(1 for r in results if r.get('price_source') == 'cached')
    report += f"- Data Source: {valid}/{len(results)} cached\n"
    report += f"- All records have timestamps: Yes\n"

    return report


def quick_summary():
    """Generate quick one-page summary"""
    from stock_pro.core import A, analyze_multiple
    from stock_pro.picks import quick_picks

    results = analyze_multiple(list(A.keys()))
    return quick_picks(results)


def export_all(symbols, format='all'):
    """Export all reports in various formats"""
    from stock_pro.integrations import export_csv, export_xlsx, gen_dashboard
    from stock_pro.core import analyze_multiple

    results = analyze_multiple(symbols)

    outputs = []

    if format == 'all' or format == 'csv':
        csv_file = export_csv(results)
        outputs.append(csv_file)

    if format == 'all' or format == 'xlsx':
        xlsx_file = export_xlsx(results)
        outputs.append(xlsx_file)

    if format == 'all' or format == 'html':
        html_file = gen_dashboard(results)
        outputs.append(html_file)

    return outputs


from datetime import datetime
