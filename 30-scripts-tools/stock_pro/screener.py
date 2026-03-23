"""Stock screener - Optimized v12.8"""
from .core import A, F, P, B, E, calc_score, analyze_multiple_parallel

class StockScreener:
    def __init__(self, min_score=60, min_upside=15, max_pe=40):
        self.min_score = min_score
        self.min_upside = min_upside
        self.max_pe = max_pe

    def screen(self, live=True):
        """Screen stocks using parallel analysis"""
        symbols = list(F.keys())

        # Use parallel analysis for speed
        if live:
            results_dict = analyze_multiple_parallel(symbols, max_workers=10)
        else:
            results_dict = {}
            for sym in symbols:
                from .core import analyze
                results_dict[sym] = analyze(sym)

        results = []
        for sym, data in results_dict.items():
            if not data:
                continue
            score = data.get("score", 0)
            upside = data.get("upside", 0)
            pe = data.get("pe", 999)

            if score >= self.min_score and upside >= self.min_upside and pe <= self.max_pe:
                results.append({
                    "symbol": sym,
                    "price": data.get("price", 0),
                    "target": data.get("target", 0),
                    "upside": upside,
                    "score": score,
                    "pe": pe,
                    "peg": data.get("peg", 5),
                    "roe": data.get("roe", 0),
                    "fcf": data.get("fcf", 0),  # Already in %
                    "div": data.get("div", 0),
                    "rating": data.get("rating_int", "HOLD"),
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def show(self, live=False):
        results = self.screen(live)
        if not results:
            return f"[Screener] No stocks (Score>={self.min_score}, Upside>={self.min_upside}%, P/E<={self.max_pe})"
        lines = ["=" * 95, f"Stock Screener (Score>={self.min_score}, Upside>={self.min_upside}%, P/E<={self.max_pe})", "=" * 95, "", f"{'Symbol':<8} {'Score':>6} {'Upside':>8} {'P/E':>6} {'PEG':>6} {'ROE':>6} {'FCF':>6} {'Div':>6}", "-" * 95]
        for r in results:
            emoji = "+" if r['upside'] > 15 else "-"
            lines.append(f"{r['symbol']:<8} {r['score']:>5} {emoji}{r['upside']:>+6.1f}% {r['pe']:>5.1f}x {r['peg']:>5.2f}x {r['roe']:>5.1f}% {r['fcf']:>5.1f}% {r['div']:>5.2f}%")
        lines.append("=" * 95)
        lines.append(f"Found {len(results)} stocks")
        return "\n".join(lines)
