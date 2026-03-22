"""Stock screener"""
from .core import A, F, P, B, E, calc_score, fetch_live

class StockScreener:
    def __init__(self, min_score=60, min_upside=15, max_pe=40):
        self.min_score = min_score
        self.min_upside = min_upside
        self.max_pe = max_pe
    
    def screen(self, live=False):
        results = []
        for sym in F.keys():
            price = P.get(sym, 100)
            if live:
                p = fetch_live(sym)
                if p > 0: price = p
            fin = F[sym]
            eps = E.get(sym, 3)
            beta = B.get(sym, 1)
            analyst = A.get(sym, A["META"])
            pe = price / eps if eps > 0 else 50
            upside = (analyst[0] - price) / price * 100
            score = calc_score(sym, price, A.get(sym, A["META"]))
            rev_g = fin[5]
            if score >= self.min_score and upside >= self.min_upside and pe <= self.max_pe:
                results.append({
                    "symbol": sym, "price": price, "target": analyst[0], "upside": upside,
                    "score": score, "pe": pe, "peg": pe / (rev_g * 100) if rev_g > 0 else 5,
                    "roe": fin[2] * 100, "fcf": fin[6] * 100, "div": fin[7] * 100,
                    "rating": "BUY" if score >= 65 else "HOLD" if score >= 55 else "SELL",
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
