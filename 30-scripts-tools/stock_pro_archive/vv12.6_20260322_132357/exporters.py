"""Enhanced Export Module - Multiple format exporters"""
import json
import csv
from pathlib import Path
from datetime import datetime
from stock_pro.core import A, analyze_multiple

WORKSPACE = Path("D:/OpenClaw/workspace")
EXPORT_DIR = WORKSPACE / "30-scripts-tools" / "exports"


def ensure_export_dir():
    """Ensure export directory exists"""
    if not EXPORT_DIR.exists():
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_json(symbols, filename=None):
    """Export to JSON format"""
    ensure_export_dir()

    if filename is None:
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    results = analyze_multiple(symbols)
    filepath = EXPORT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            "generated": datetime.now().isoformat(),
            "count": len(results),
            "stocks": results
        }, f, indent=2)

    return f"[Export] JSON saved to: {filepath}"


def export_csv(symbols, filename=None):
    """Export to CSV format"""
    ensure_export_dir()

    if filename is None:
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    results = analyze_multiple(symbols)
    filepath = EXPORT_DIR / filename

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol", "Price", "Target", "Upside", "Score", "P/E", "PEG", "ROE", "Sector"])

        from stock_pro.sectors import get_sector
        for r in results:
            writer.writerow([
                r["symbol"], r["price"], r["target"], r["upside"], r["score"],
                r.get("pe", ""), r.get("peg", ""), r.get("roe", ""),
                get_sector(r["symbol"])
            ])

    return f"[Export] CSV saved to: {filepath}"


def export_markdown(symbols, filename=None):
    """Export to Markdown format"""
    ensure_export_dir()

    if filename is None:
        filename = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    results = analyze_multiple(symbols)
    from stock_pro.sectors import get_sector

    report = f"# Stock Report\n\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**Stocks:** {len(results)}\n\n"
    report += "| Symbol | Price | Score | Upside | Sector |\n|--------|-------|-------|--------|--------|\n"

    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        report += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {get_sector(r['symbol'])} |\n"

    filepath = EXPORT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    return f"[Export] Markdown saved to: {filepath}"


def export_html(symbols, filename=None):
    """Export to HTML format"""
    ensure_export_dir()

    if filename is None:
        filename = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    results = analyze_multiple(symbols)
    from stock_pro.sectors import get_sector

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Stock Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; }}
        th {{ background-color: #1a1a2e; color: white; }}
        .positive {{ color: #00aa00; }}
    </style>
</head>
<body>
    <h1>Stock Report - {datetime.now().strftime('%Y-%m-%d')}</h1>
    <table>
        <tr><th>Symbol</th><th>Price</th><th>Target</th><th>Upside</th><th>Score</th><th>Sector</th></tr>
"""

    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        html += f"<tr><td><strong>{r['symbol']}</strong></td><td>${r['price']:.2f}</td>"
        html += f"<td>${r['target']:.2f}</td><td class='positive'>{r['upside']:+.1f}%</td>"
        html += f"<td>{r['score']}</td><td>{get_sector(r['symbol'])}</td></tr>\n"

    html += "</table></body></html>"

    filepath = EXPORT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return f"[Export] HTML saved to: {filepath}"


def export_all(symbols):
    """Export to all formats"""
    ensure_export_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    outputs = []
    outputs.append(export_json(symbols, f"stocks_{timestamp}.json"))
    outputs.append(export_csv(symbols, f"stocks_{timestamp}.csv"))
    outputs.append(export_markdown(symbols, f"report_{timestamp}.md"))
    outputs.append(export_html(symbols, f"report_{timestamp}.html"))

    return outputs


def batch_export(symbols_list, prefix="batch"):
    """Batch export multiple symbol groups"""
    ensure_export_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    outputs = []
    for i, symbols in enumerate(symbols_list):
        outputs.append(export_csv(symbols, f"{prefix}_{i}_{timestamp}.csv"))

    return outputs
