#!/usr/bin/env py
# Stock PRO v3.0 - Professional Stock Analysis Report Generator
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("D:/OpenClaw/workspace")
OUTPUT = WORKSPACE / "50-reports" / "stocks"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Financial Database
FD = {
    "AAPL": {"rev": 416e9, "gm": 0.47, "om": 0.30, "nm": 0.24, "roe": 0.45, "roa": 0.22, "roic": 0.35, "de": 1.8, "cr": 1.05, "pe_avg": 28, "eg": 0.10, "sector": "Technology", "business": "Consumer Electronics & Software Services"},
    "MSFT": {"rev": 237e9, "gm": 0.70, "om": 0.43, "nm": 0.35, "roe": 0.38, "roa": 0.18, "roic": 0.28, "de": 0.5, "cr": 1.3, "pe_avg": 32, "eg": 0.12, "sector": "Technology", "business": "Cloud Computing & Enterprise Software"},
    "NVDA": {"rev": 80e9, "gm": 0.73, "om": 0.53, "nm": 0.49, "roe": 0.58, "roa": 0.35, "roic": 0.45, "de": 0.4, "cr": 4.2, "pe_avg": 55, "eg": 0.50, "sector": "Technology", "business": "Semiconductor & AI Accelerators"},
    "META": {"rev": 135e9, "gm": 0.81, "om": 0.38, "nm": 0.32, "roe": 0.28, "roa": 0.15, "roic": 0.22, "de": 0.3, "cr": 2.7, "pe_avg": 28, "eg": 0.25, "sector": "Technology", "business": "Social Media & Digital Advertising"},
    "GOOGL": {"rev": 307e9, "gm": 0.57, "om": 0.28, "nm": 0.24, "roe": 0.30, "roa": 0.14, "roic": 0.20, "de": 0.1, "cr": 2.1, "pe_avg": 26, "eg": 0.15, "sector": "Technology", "business": "Search, Cloud & AI Services"},
    "AMZN": {"rev": 620e9, "gm": 0.48, "om": 0.11, "nm": 0.09, "roe": 0.18, "roa": 0.08, "roic": 0.15, "de": 0.6, "cr": 1.2, "pe_avg": 50, "eg": 0.18, "sector": "Consumer Discretionary", "business": "E-commerce & Cloud Infrastructure"},
    "JPM": {"rev": 160e9, "gm": 0.0, "om": 0.40, "nm": 0.30, "roe": 0.17, "roa": 0.01, "roic": 0.18, "de": 1.5, "cr": 0, "pe_avg": 12, "eg": 0.08, "sector": "Financial Services", "business": "Global Banking & Financial Services"},
    "JNJ": {"rev": 88e9, "gm": 0.68, "om": 0.28, "nm": 0.20, "roe": 0.23, "roa": 0.10, "roic": 0.20, "de": 0.5, "cr": 1.2, "pe_avg": 18, "eg": 0.06, "sector": "Healthcare", "business": "Pharmaceuticals & Medical Devices"},
}
SHARES = {"AAPL": 15.3e9, "MSFT": 7.43e9, "NVDA": 24.5e9, "META": 2.5e9, "GOOGL": 12.8e9, "AMZN": 10.5e9, "JPM": 2.9e9, "JNJ": 2.4e9}
COMP = {"AAPL": ["MSFT", "GOOGL", "AMZN", "META"], "NVDA": ["AMD", "INTC"], "META": ["GOOGL", "SNAP"], "AMZN": ["WMT", "TGT"], "JPM": ["BAC", "WFC"], "JNJ": ["PFE", "UNH"]}

def get_quote(sym):
    try:
        import urllib.request
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode())
        m = d["chart"]["result"][0]["meta"]
        p = m.get("regularMarketPrice", 0) or 0
        sh = SHARES.get(sym.upper(), 1e9)
        pe = m.get("trailingPE", 0) or 0
        eps = m.get("trailingEps", 0) or 0
        if eps == 0:
            fd = FD.get(sym.upper(), {})
            eps = (fd.get("rev", 1e10) * fd.get("nm", 0.20)) / sh
        fd_data = FD.get(sym.upper(), {})
        return {"symbol": sym.upper(), "price": p, "mc": m.get("marketCap", 0) or p *sh,
                "pe": pe or fd_data.get("pe_avg", 25), "eps": eps, "eg": fd_data.get("eg", 0.10),
                "beta": m.get("beta", 1.0) or 1.0,
                "w52h": m.get("fiftyTwoWeekHigh", p *1.2) or p *1.2,
                "w52l": m.get("fiftyTwoWeekLow", p *0.8) or p *0.8}
    except Exception as e:
        print(f"Error: {e}"); return None

def get_fin(sym, q):
    fd = FD.get(sym.upper(), {})
    rev = fd.get("rev", q["mc"] /10)
    ni = rev * fd.get("nm", 0.15)
    eq = ni / fd["roe"] if fd.get("roe", 0) > 0 else rev * 2
    return {"rev": rev, "ni": ni, "eq": eq, "ta": eq *2, "debt": eq *fd.get("de", 0.5), "sh": SHARES.get(sym.upper(), 1e9),
            "gm": fd.get("gm", 0.40), "om": fd.get("om", 0.20), "nm": fd.get("nm", 0.15),
            "roe": fd.get("roe", 0.15), "roa": fd.get("roa", 0.08), "roic": fd.get("roic", 0.12),
            "cr": fd.get("cr", 1.5), "de": fd.get("de", 0.5),
            "sector": fd.get("sector", "Unknown"), "business": fd.get("business", "")}

def calc_target(eps, gr, pe_avg):
    if gr < 0.05: base_pe = 18
    elif gr < 0.10: base_pe = 22
    elif gr < 0.15: base_pe = 28
    elif gr < 0.25: base_pe = 35
    else: base_pe = 45
    return eps * (1 + gr) * base_pe, base_pe

def gen_report(sym):
    q = get_quote(sym)
    if not q: return None
    fin = get_fin(sym, q)
    pe = q["pe"]
    ps = q["mc"] /fin["rev"] if fin["rev"] > 0 else 0
    pb = q["mc"] /fin["eq"] if fin["eq"] > 0 else 0
    target, target_pe = calc_target(q["eps"], q["eg"], fin.get("pe_avg", 25))
    upside = (target - q["price"]) / q["price"] * 100
    rating = "STRONG_BUY" if upside > 30 else "BUY" if upside > 15 else "HOLD" if upside > 0 else "SELL"
    var_95 = q["price"] * q["beta"] * 1.65 * 0.05
    max_dd = (q["price"] - q["w52l"]) / q["price"] * 100
    risk_score = min(q["beta"] *15 + var_95 /q["price"] *100 + fin["de"] *8, 100)
    risk_level = "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 50 else "HIGH"
    score = 50
    score += 15 if q["eg"] > 0.30 else 10 if q["eg"] > 0.15 else 5 if q["eg"] > 0.08 else 0
    score += 10 if fin["roe"] > 0.30 else 5 if fin["roe"] > 0.20 else 0
    score += 5 if fin["gm"] > 0.60 else 0
    score += 15 if upside > 30 else 10 if upside > 15 else 5 if upside > 0 else -10
    score += 10 if risk_score < 30 else -10 if risk_score > 50 else 0
    score = min(max(score, 0), 100)
    comps = COMP.get(sym.upper(), [])
    comp_data = []
    for c in comps[:4]:
        cq = get_quote(c)
        if cq: comp_data.append({"s": c, "p": cq["price"], "pe": cq["pe"]})
    today = datetime.now().strftime("%Y-%m-%d")
    pos = (q["price"] -q["w52l"]) /(q["w52h"] -q["w52l"]) *100 if q["w52h"] > q["w52l"] else 50

    # Build Markdown report
    md = []
    md.append(f"# Stock Analysis Report: {sym}")
    md.append("")
    md.append(f"**Report Date:** {today}")
    md.append(f"**Analyst:** Stock PRO v3.0")
    md.append(f"**Sector:** {fin['sector']}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary")
    md.append("")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(f"| Current Price | ${q['price']:.2f} |")
    md.append(f"| Market Cap | ${q['mc'] /1e12:.2f}T |")
    md.append(f"| Target Price | ${target:.2f} |")
    md.append(f"| Upside Potential | {upside:+.1f}% |")
    md.append(f"| Rating | **{rating}** |")
    md.append(f"| Overall Score | {score}/100 |")
    md.append("")
    md.append(f"**Recommendation:** {rating}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Business Overview")
    md.append("")
    md.append(f"**{sym}** operates in the **{fin['sector']}** sector:")
    md.append("")
    md.append(f"> {fin['business']}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. Valuation Analysis")
    md.append("")
    md.append("### 3.1 Price Multiples")
    md.append("")
    md.append("| Metric | Current | Industry Avg | Assessment |")
    md.append("|--------|---------|--------------|------------|")
    pe_assess = "Overvalued" if pe > fin.get("pe_avg", 25) else "Undervalued" if pe < fin.get("pe_avg", 25) * 0.8 else "Fair Value"
    md.append(f"| P/E Ratio | {pe:.1f}x | {fin.get('pe_avg', 25):.0f}x | {pe_assess} |")
    ps_assess = "High" if ps > 10 else "Moderate" if ps > 5 else "Low"
    md.append(f"| P/S Ratio | {ps:.1f}x | - | {ps_assess} |")
    pb_assess = "High" if pb > 10 else "Moderate" if pb > 3 else "Low"
    md.append(f"| P/B Ratio | {pb:.1f}x | - | {pb_assess} |")
    md.append("")
    md.append("### 3.2 Target Price Calculation")
    md.append("")
    md.append("| Component | Value |")
    md.append("|-----------|-------|")
    md.append(f"| Current EPS | ${q['eps']:.2f} |")
    md.append(f"| Expected Growth | {q['eg'] *100:.0f}% |")
    md.append(f"| Forward EPS | ${q['eps'] *(1 +q['eg']):.2f} |")
    md.append(f"| Target P/E | {target_pe}x |")
    md.append(f"| **Target Price** | **${target:.2f}** |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 4. Financial Health")
    md.append("")
    md.append("### 4.1 Profitability")
    md.append("")
    md.append("| Metric | Value | Assessment |")
    md.append("|--------|-------|------------|")
    gm_assess = "Excellent" if fin["gm"] > 0.60 else "Good" if fin["gm"] > 0.40 else "Average"
    md.append(f"| Gross Margin | {fin['gm'] *100:.1f}% | {gm_assess} |")
    om_assess = "Excellent" if fin["om"] > 0.25 else "Good" if fin["om"] > 0.15 else "Average"
    md.append(f"| Operating Margin | {fin['om'] *100:.1f}% | {om_assess} |")
    nm_assess = "Excellent" if fin["nm"] > 0.20 else "Good" if fin["nm"] > 0.10 else "Average"
    md.append(f"| Net Margin | {fin['nm'] *100:.1f}% | {nm_assess} |")
    md.append("")
    md.append("### 4.2 Returns")
    md.append("")
    md.append("| Metric | Value | Assessment |")
    md.append("|--------|-------|------------|")
    roe_assess = "Exceptional" if fin["roe"] > 0.30 else "Strong" if fin["roe"] > 0.20 else "Average"
    md.append(f"| ROE | {fin['roe'] *100:.1f}% | {roe_assess} |")
    roic_assess = "Excellent" if fin["roic"] > 0.25 else "Good" if fin["roic"] > 0.15 else "Needs Improvement"
    md.append(f"| ROIC | {fin['roic'] *100:.1f}% | {roic_assess} |")
    roa_assess = "Strong" if fin["roa"] > 0.15 else "Adequate" if fin["roa"] > 0.05 else "Weak"
    md.append(f"| ROA | {fin['roa'] *100:.1f}% | {roa_assess} |")
    md.append("")
    md.append("### 4.3 Balance Sheet")
    md.append("")
    md.append("| Metric | Value | Assessment |")
    md.append("|--------|-------|------------|")
    de_assess = "Conservative" if fin["de"] < 0.5 else "Moderate" if fin["de"] < 1.5 else "Aggressive"
    md.append(f"| Debt/Equity | {fin['de']:.1f}x | {de_assess} |")
    cr_assess = "Strong" if fin["cr"] > 1.5 else "Adequate" if fin["cr"] > 1.0 else "Weak"
    md.append(f"| Current Ratio | {fin['cr']:.1f}x | {cr_assess} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 5. Risk Assessment")
    md.append("")
    md.append("| Metric | Value | Interpretation |")
    md.append("|--------|-------|----------------|")
    beta_assess = "Defensive" if q["beta"] < 0.8 else "Neutral" if q["beta"] < 1.2 else "Aggressive"
    md.append(f"| Beta | {q['beta']:.2f} | {beta_assess} |")
    md.append(f"| VaR (95%) | ${var_95:.2f} | Max 1-day loss with 95% confidence |")
    md.append(f"| Max Drawdown Risk | {max_dd:.1f}% | Potential decline from current price |")
    md.append(f"| Risk Score | {risk_score:.0f}/100 | {risk_level} |")
    md.append(f"| 52-Week Position | {pos:.0f}% | {'Near high' if pos > 75 else 'Near low' if pos < 25 else 'Mid-range'} |")
    md.append("")
    md.append(f"**Overall Risk Level: {risk_level}**")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 6. Competitive Analysis")
    md.append("")
    md.append("| Ticker | Price | P/E | vs " + sym + " |")
    md.append("|--------|-------|-----|----------|")
    md.append(f"| **{sym}** | **${q['price']:.2f}** | **{pe:.1f}x** | - |")
    for c in comp_data:
        diff = c["pe"] - pe
        sign = "+" if diff > 0 else ""
        md.append(f"| {c['s']} | ${c['p']:.2f} | {c['pe']:.1f}x | {sign}{diff:.1f} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 7. Investment Thesis")
    md.append("")
    md.append("### Strengths")
    if fin["gm"] > 0.50: md.append(f"- **High Gross Margins ({fin['gm'] *100:.0f}%)** - Strong pricing power")
    if fin["roe"] > 0.25: md.append(f"- **Exceptional ROE ({fin['roe'] *100:.0f}%)** - Efficient capital deployment")
    if fin["nm"] > 0.20: md.append(f"- **Strong Net Margins ({fin['nm'] *100:.0f}%)** - Operational excellence")
    if q["eg"] > 0.15: md.append(f"- **High Growth Rate ({q['eg'] *100:.0f}%)** - Strong momentum")
    if fin["cr"] > 2.0: md.append(f"- **Strong Liquidity (CR: {fin['cr']:.1f}x)** - Financial flexibility")
    md.append("")
    md.append("### Concerns")
    if pe > fin.get("pe_avg", 25): md.append(f"- **Elevated P/E ({pe:.0f}x vs avg {fin.get('pe_avg', 25):.0f}x)** - Premium valuation")
    if fin["de"] > 1.0: md.append(f"- **High Leverage (D/E: {fin['de']:.1f}x)** - Debt servicing risk")
    if upside < 0: md.append(f"- **Negative Upside ({upside:.1f}%)** - Limited near-term appreciation")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 8. Conclusion")
    md.append("")
    md.append(f"**Rating: {rating}**")
    md.append("")
    md.append("| Factor | Assessment |")
    md.append("|--------|------------|")
    val_assess = "Attractive" if upside > 15 else "Fair" if upside > 0 else "Expensive"
    md.append(f"| Valuation | {val_assess} |")
    fund_assess = "Strong" if score > 70 else "Good" if score > 50 else "Weak"
    md.append(f"| Fundamentals | {fund_assess} |")
    md.append(f"| Risk Profile | {risk_level} |")
    md.append(f"| Technical | At {pos:.0f}% of 52-week range |")
    md.append("")
    summary = f"{sym} is currently trading at ${q['price']:.2f} with a target of ${target:.2f}, representing {upside:+.1f}% upside/downside. "
    if rating in ["BUY", "STRONG_BUY"]: summary += "The stock deserves attention for long-term investors."
    elif rating == "HOLD": summary += "The stock may require patience for value to materialize."
    else: summary += "The stock appears fully valued at current levels."
    md.append(summary)
    md.append("")
    md.append("---")
    md.append("")
    md.append(f"*Report generated by Stock PRO v3.0 on {today}*")

    # Save report
    content = "\n".join(md)
    fname = OUTPUT / f"{sym}_{today}.md"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n{'=' *60}")
    print(f"  Stock PRO v3.0 - {sym} Report Generated")
    print(f"{'=' *60}")
    print(f"  Rating: {rating}")
    print(f"  Target: ${target:.2f} ({upside:+.1f}%)")
    print(f"  Score: {score}/100")
    print(f"  Risk: {risk_level}")
    print(f"\n  Report: {fname}")
    print(f"{'=' *60}\n")
    return fname

def main():
    import argparse
    p = argparse.ArgumentParser(description="Stock PRO v3.0")
    p.add_argument("symbol", nargs="?", default="AAPL")
    args = p.parse_args()
    gen_report(args.symbol.upper())

if __name__ == "__main__": main()