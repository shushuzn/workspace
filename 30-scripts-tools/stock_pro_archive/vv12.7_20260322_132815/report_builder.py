"""Report Builder - Create custom reports with templates"""
from datetime import datetime
from stock_pro.core import A, analyze_multiple
from stock_pro.sectors import get_sector, get_all_sectors


class ReportBuilder:
    """Build custom reports with templates"""

    def __init__(self, title="Stock Report"):
        self.title = title
        self.sections = []
        self.timestamp = datetime.now()

    def add_header(self, text, level=1):
        self.sections.append({"type": "header", "text": text, "level": level})
        return self

    def add_paragraph(self, text):
        self.sections.append({"type": "paragraph", "text": text})
        return self

    def add_table(self, headers, rows):
        self.sections.append({"type": "table", "headers": headers, "rows": rows})
        return self

    def add_list(self, items):
        self.sections.append({"type": "list", "items": items})
        return self

    def add_summary(self, results):
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0
        avg_upside = sum(r["upside"] for r in results) / len(results) if results else 0
        self.add_header("Summary")
        self.add_list([
            f"Stocks: {len(results)}",
            f"Average Score: {avg_score:.0f}",
            f"Average Upside: {avg_upside:+.1f}%",
            f"Strong Buys: {len([r for r in results if r['score'] >= 75])}"
        ])
        return self

    def add_top_picks(self, results, n=5):
        top = sorted(results, key=lambda x: x["score"], reverse=True)[:n]
        headers = ["Symbol", "Score", "Upside", "Sector"]
        rows = [[r["symbol"], r["score"], f"{r['upside']:+.1f}%", get_sector(r["symbol"])] for r in top]
        self.add_header("Top Picks", 2)
        self.add_table(headers, rows)
        return self

    def render_markdown(self):
        output = f"# {self.title}\n\n**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
        for s in self.sections:
            if s["type"] == "header":
                output += f"{'#' * s['level']} {s['text']}\n\n"
            elif s["type"] == "paragraph":
                output += f"{s['text']}\n\n"
            elif s["type"] == "table":
                output += "| " + " | ".join(s["headers"]) + " |\n"
                output += "| " + " | ".join(["---"] * len(s["headers"])) + " |\n"
                for row in s["rows"]:
                    output += "| " + " | ".join(str(c) for c in row) + " |\n"
                output += "\n"
            elif s["type"] == "list":
                for item in s["items"]:
                    output += f"- {item}\n"
                output += "\n"
        return output

    def render_html(self):
        output = f"""<!DOCTYPE html>
<html><head><title>{self.title}</title><meta charset="UTF-8">
<style>
body{{font-family:Arial;margin:40px;line-height:1.6}}
h1{{color:#1a1a2e;border-bottom:2px solid #00d4ff;padding-bottom:10px}}
h2{{color:#333;margin-top:25px}}
table{{border-collapse:collapse;width:100%;margin:15px 0}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#1a1a2e;color:#fff}}
</style></head><body>
<h1>{self.title}</h1><p style="color:#666">Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
"""
        for s in self.sections:
            if s["type"] == "header":
                output += f"<h{s['level']}>{s['text']}</h{s['level']}>\n"
            elif s["type"] == "paragraph":
                output += f"<p>{s['text']}</p>\n"
            elif s["type"] == "table":
                output += "<table><tr>"
                for h in s["headers"]:
                    output += f"<th>{h}</th>"
                output += "</tr>"
                for row in s["rows"]:
                    output += "<tr>"
                    for c in row:
                        output += f"<td>{c}</td>"
                    output += "</tr>"
                output += "</table>\n"
            elif s["type"] == "list":
                output += "<ul>"
                for item in s["items"]:
                    output += f"<li>{item}</li>"
                output += "</ul>\n"
        output += "</body></html>"
        return output


def quick_report(symbols=None, style="markdown"):
    if symbols is None:
        symbols = list(A.keys())[:20]
    results = analyze_multiple(symbols)
    builder = ReportBuilder("Stock Analysis Report")
    builder.add_summary(results)
    builder.add_top_picks(results, n=10)
    if style == "html":
        return builder.render_html()
    return builder.render_markdown()


def investment_summary(symbols=None):
    if symbols is None:
        symbols = list(A.keys())
    results = analyze_multiple(symbols)
    builder = ReportBuilder("Investment Summary")

    total_value = sum(r["price"] for r in results)
    total_target = sum(r["target"] for r in results)
    potential_gain = total_target - total_value

    builder.add_header("Investment Overview")
    builder.add_list([
        f"Total Stocks: {len(results)}",
        f"Current Value: ${total_value:,.2f}",
        f"Target Value: ${total_target:,.2f}",
        f"Potential Gain: ${potential_gain:,.2f} ({(potential_gain/total_value*100):+.1f}%)"
    ])

    top10 = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    total_target10 = sum(r["target"] for r in top10)
    headers = ["Symbol", "Target", "Weight", "Score", "Upside"]
    rows = []
    for r in top10:
        weight = r["target"] / total_target10 * 100
        rows.append([r["symbol"], f"${r['target']:.2f}", f"{weight:.1f}%", r["score"], f"{r['upside']:+.1f}%"])

    builder.add_header("Top 10 Allocation")
    builder.add_table(headers, rows)

    return builder.render_markdown()
