"""Earnings Calendar and Predictions"""
from datetime import datetime, timedelta
from stock_pro.core import A

# Simulated earnings data (in real implementation, fetch from API)
EARNINGS_CALENDAR = {
    "META": {"date": "2026-04-25", "estimate": 4.50, "surprise_rate": 0.72},
    "NVDA": {"date": "2026-05-22", "estimate": 6.80, "surprise_rate": 0.85},
    "AAPL": {"date": "2026-05-01", "estimate": 2.45, "surprise_rate": 0.78},
    "MSFT": {"date": "2026-04-30", "estimate": 2.82, "surprise_rate": 0.82},
    "GOOGL": {"date": "2026-04-29", "estimate": 1.90, "surprise_rate": 0.75},
    "AMZN": {"date": "2026-05-02", "estimate": 1.45, "surprise_rate": 0.68},
    "AMD": {"date": "2026-05-07", "estimate": 0.95, "surprise_rate": 0.65},
    "TSLA": {"date": "2026-04-23", "estimate": 0.72, "surprise_rate": 0.58},
    "NFLX": {"date": "2026-04-18", "estimate": 4.25, "surprise_rate": 0.70},
    "CRM": {"date": "2026-05-30", "estimate": 2.10, "surprise_rate": 0.72},
    "JPM": {"date": "2026-04-15", "estimate": 4.35, "surprise_rate": 0.80},
    "BAC": {"date": "2026-04-15", "estimate": 0.85, "surprise_rate": 0.72},
    "V": {"date": "2026-05-10", "estimate": 2.25, "surprise_rate": 0.78},
    "MA": {"date": "2026-05-10", "estimate": 2.90, "surprise_rate": 0.75},
    "ADBE": {"date": "2026-06-12", "estimate": 4.50, "surprise_rate": 0.80},
    "NOW": {"date": "2026-05-15", "estimate": 2.85, "surprise_rate": 0.82},
    "AVGO": {"date": "2026-03-07", "estimate": 10.50, "surprise_rate": 0.75},
    "ASML": {"date": "2026-04-24", "estimate": 7.20, "surprise_rate": 0.72},
    "SPY": {"date": "2026-04-18", "estimate": None, "surprise_rate": 0.60},
    "QQQ": {"date": "2026-04-18", "estimate": None, "surprise_rate": 0.60},
}


def get_earnings_calendar(symbols=None, days=90):
    """Get earnings calendar"""
    if symbols is None:
        symbols = list(A.keys())

    today = datetime.now()
    cutoff = today + timedelta(days=days)

    calendar = []
    for sym in symbols:
        if sym in EARNINGS_CALENDAR:
            earnings = EARNINGS_CALENDAR[sym]
            date = datetime.strptime(earnings["date"], "%Y-%m-%d")

            if today <= date <= cutoff:
                days_until = (date - today).days
                calendar.append({
                    "symbol": sym,
                    "date": earnings["date"],
                    "days_until": days_until,
                    "estimate": earnings["estimate"],
                    "surprise_rate": earnings["surprise_rate"]
                })

    # Sort by date
    calendar.sort(key=lambda x: x["date"])

    return calendar


def earnings_report(symbols=None, days=90):
    """Generate earnings report"""
    calendar = get_earnings_calendar(symbols, days)

    if not calendar:
        return f"[Earnings] No earnings scheduled in next {days} days"

    report = f"# Earnings Calendar (Next {days} Days)\n\n"
    report += f"**Total Events:** {len(calendar)}\n\n"

    report += "| Symbol | Date | Days Until | Estimate | Surprise Rate |\n"
    report += "|--------|------|------------|----------|---------------|\n"

    high_confidence = []
    for c in calendar:
        estimate = f"${c['estimate']:.2f}" if c['estimate'] else "N/A"
        surprise = "High" if c["surprise_rate"] > 0.75 else "Medium" if c["surprise_rate"] > 0.65 else "Low"

        if c["surprise_rate"] > 0.75:
            high_confidence.append(c["symbol"])

        report += f"| {c['symbol']} | {c['date']} | {c['days_until']} | {estimate} | {surprise} |\n"

    report += f"\n**High Confidence ({len(high_confidence)}):** {', '.join(high_confidence) if high_confidence else 'None'}\n"

    return report


def predict_earnings_beat(symbols=None):
    """Predict earnings beat probability"""
    from stock_pro.core import analyze_multiple

    if symbols is None:
        symbols = list(A.keys())

    predictions = []

    for sym in symbols:
        if sym in EARNINGS_CALENDAR:
            earnings = EARNINGS_CALENDAR[sym]
            results = analyze_multiple([sym])

            if results:
                r = results[0]
                score = r["score"]

                # Simple prediction model
                base_prob = earnings["surprise_rate"]

                # Adjust by score
                if score >= 80:
                    adj_prob = min(0.95, base_prob + 0.10)
                elif score >= 60:
                    adj_prob = min(0.85, base_prob + 0.05)
                elif score >= 40:
                    adj_prob = base_prob
                else:
                    adj_prob = max(0.30, base_prob - 0.15)

                beat = "Beat" if adj_prob > 0.65 else "Miss"

                predictions.append({
                    "symbol": sym,
                    "date": earnings["date"],
                    "estimate": earnings["estimate"],
                    "beat_probability": adj_prob,
                    "prediction": beat,
                    "score": score
                })

    # Sort by probability
    predictions.sort(key=lambda x: x["beat_probability"], reverse=True)

    report = "# Earnings Beat Predictions\n\n"
    report += "| Symbol | Date | Estimate | Beat Prob | Prediction | Score |\n"
    report += "|--------|------|----------|-----------|------------|-------|\n"

    beat_count = 0
    for p in predictions:
        estimate_str = f"${p['estimate']:.2f}" if p['estimate'] else "N/A"
        report += f"| {p['symbol']} | {p['date']} | {estimate_str} | {p['beat_probability']:.0%} | {p['prediction']} | {p['score']} |\n"
        if p["prediction"] == "Beat":
            beat_count += 1

    report += f"\n**Expected Beats:** {beat_count}/{len(predictions)}\n"

    return report
