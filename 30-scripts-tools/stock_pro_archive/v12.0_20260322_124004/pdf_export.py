"""PDF export module for Stock PRO"""
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
EXPORT_DIR = WORKSPACE / "30-scripts-tools" / "exports"


def export_pdf(report_content, filename=None):
    """Export report as PDF (using HTML to PDF approach)"""
    from stock_pro.reports import gen_report
    from stock_pro.core import A, analyze_multiple

    if EXPORT_DIR.exists() is False:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    filepath = EXPORT_DIR / filename

    # Convert markdown to HTML
    html_content = _markdown_to_html(report_content)

    # Full HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Stock PRO Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #007bff; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .positive {{ color: green; }}
        .negative {{ color: red; }}
        .header {{ background: #f4f4f4; padding: 20px; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Stock PRO Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    {html_content}
</body>
</html>"""

    # Save as HTML (for now, can be converted to PDF with tools)
    html_path = EXPORT_DIR / filename.replace('.pdf', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    return f"[PDF] Report saved to {html_path}\nNote: HTML file created. Use browser print-to-PDF for actual PDF."


def _markdown_to_html(md_text):
    """Convert markdown to basic HTML"""
    import re

    html = md_text

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Tables (basic)
    lines = html.split('\n')
    in_table = False
    new_lines = []

    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                new_lines.append('<table>')
                in_table = True

            if not line.replace('|', '').replace('-', '').replace(':', '').strip():
                continue  # Skip separator lines

            cells = [c.strip() for c in line.split('|')[1:-1]]

            if in_table and line.startswith('|'):
                tag = 'th' if '<th>' in ''.join(new_lines[-3:]) or not any('</th>' in l for l in new_lines) else 'td'
                new_lines.append(f'<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
        else:
            if in_table:
                new_lines.append('</table>')
                in_table = False
            new_lines.append(line)

    if in_table:
        new_lines.append('</table>')

    html = '\n'.join(new_lines)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Paragraphs
    html = re.sub(r'\n\n', '</p><p>', html)
    html = f'<p>{html}</p>'
    html = html.replace('<p></p>', '')

    return html


def full_pdf_report(symbols):
    """Generate full PDF report for multiple stocks"""
    from stock_pro.reports import gen_report
    from stock_pro.core import analyze_multiple

    report = f"# Stock PRO - Full Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**Stocks:** {', '.join(symbols)}\n\n"

    # Summary table
    results = analyze_multiple(symbols)

    report += "## Summary\n\n"
    report += "| Symbol | Price | Score | Upside | Recommendation |\n"
    report += "|--------|-------|-------|--------|----------------|\n"

    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        rec = r.get("recommendation", {}).get("action", "Hold")
        report += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {rec} |\n"

    # Individual reports
    report += "\n---\n\n"

    for r in results:
        report += gen_report(r["symbol"])
        report += "\n---\n\n"

    return export_pdf(report)
