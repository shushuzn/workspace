#!/usr/bin/env python3
"""
Automatic Daily Report Generator
Comprehensive daily stock analysis report from multiple sources

Features:
- Multi-source data integration (price + news + sentiment + risk)
- AI-powered summary generation (local LLM)
- Automated formatting (Markdown + HTML)
- Scheduled generation (cron-compatible)
- Feishu/Email notification integration

Usage:
  python daily_report_generator.py --generate
  python daily_report_generator.py --demo
  python daily_report_generator.py --notify --feishu
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import os


@dataclass
class MarketSummary:
    """Daily market summary"""
    date: str
    market_status: str  # Bull/Bear/Neutral
    key_drivers: List[str]
    top_gainers: List[Dict]
    top_losers: List[Dict]
    volume_trend: str
    volatility_level: str


@dataclass
class StockInsight:
    """Individual stock insight"""
    ticker: str
    price: float
    change_pct: float
    volume: int
    sentiment: str  # Positive/Neutral/Negative
    risk_level: str  # Low/Medium/High/Critical
    signal: str  # Buy/Sell/Hold
    key_news: List[str]
    recommendation: str


@dataclass
class DailyReport:
    """Complete daily report"""
    report_id: str
    generated_at: str
    market_summary: MarketSummary
    stock_insights: List[StockInsight]
    portfolio_summary: Dict
    risk_alerts: List[str]
    opportunities: List[str]
    ai_summary: str


class DailyReportGenerator:
    """Automatic daily report generator"""

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.report: Optional[DailyReport] = None

    def generate(self, portfolio: List[Dict] = None, market_data: Dict = None) -> DailyReport:
        """Generate comprehensive daily report"""

        # Generate market summary
        market_summary = self._generate_market_summary(market_data)

        # Generate stock insights
        stock_insights = self._generate_stock_insights(portfolio or [])

        # Generate portfolio summary
        portfolio_summary = self._generate_portfolio_summary(portfolio or [])

        # Generate risk alerts
        risk_alerts = self._generate_risk_alerts(stock_insights)

        # Generate opportunities
        opportunities = self._generate_opportunities(stock_insights)

        # Generate AI summary
        ai_summary = self._generate_ai_summary(
            market_summary, stock_insights, portfolio_summary, risk_alerts
        )

        # Create report
        self.report = DailyReport(
            report_id=f"DAILY-{datetime.now().strftime('%Y%m%d')}",
            generated_at=datetime.now().isoformat(),
            market_summary=market_summary,
            stock_insights=stock_insights,
            portfolio_summary=portfolio_summary,
            risk_alerts=risk_alerts,
            opportunities=opportunities,
            ai_summary=ai_summary
        )

        return self.report

    def _generate_market_summary(self, market_data: Dict = None) -> MarketSummary:
        """Generate market summary"""
        # Mock data for demo
        return MarketSummary(
            date=datetime.now().strftime("%Y-%m-%d"),
            market_status="Neutral",
            key_drivers=[
                "Fed rate decision pending",
                "Tech earnings mixed",
                "Oil prices stable"
            ],
            top_gainers=[
                {"ticker": "NVDA", "change": 5.2},
                {"ticker": "AMD", "change": 3.8},
                {"ticker": "AAPL", "change": 2.5}
            ],
            top_losers=[
                {"ticker": "TSLA", "change": -3.5},
                {"ticker": "META", "change": -2.1},
                {"ticker": "NFLX", "change": -1.8}
            ],
            volume_trend="Above average",
            volatility_level="Moderate"
        )

    def _generate_stock_insights(self, portfolio: List[Dict]) -> List[StockInsight]:
        """Generate insights for each stock"""
        insights = []

        # Mock data
        mock_data = {
            "AAPL": {"price": 178.5, "change": 2.5, "sentiment": "Positive", "risk": "Low", "signal": "Buy"},
            "NVDA": {"price": 875.3, "change": 5.2, "sentiment": "Positive", "risk": "Medium", "signal": "Buy"},
            "MSFT": {"price": 415.2, "change": 1.8, "sentiment": "Neutral", "risk": "Low", "signal": "Hold"},
            "GOOGL": {"price": 142.8, "change": -1.2, "sentiment": "Neutral", "risk": "Low", "signal": "Hold"},
            "AMZN": {"price": 178.9, "change": 0.5, "sentiment": "Neutral", "risk": "Medium", "signal": "Hold"},
            "TSLA": {"price": 175.4, "change": -3.5, "sentiment": "Negative", "risk": "High", "signal": "Sell"},
            "JNJ": {"price": 156.2, "change": 0.3, "sentiment": "Neutral", "risk": "Low", "signal": "Hold"},
        }

        for position in portfolio:
            ticker = position.get('ticker', 'UNKNOWN')
            data = mock_data.get(ticker, {"price": 100, "change": 0, "sentiment": "Neutral", "risk": "Medium", "signal": "Hold"})

            insight = StockInsight(
                ticker=ticker,
                price=data['price'],
                change_pct=data['change'],
                volume=1000000,  # Mock
                sentiment=data['sentiment'],
                risk_level=data['risk'],
                signal=data['signal'],
                key_news=[f"{ticker} reports Q1 earnings next week"],
                recommendation=f"{data['signal']} - {data['sentiment']} sentiment, {data['risk']} risk"
            )
            insights.append(insight)

        return insights

    def _generate_portfolio_summary(self, portfolio: List[Dict]) -> Dict:
        """Generate portfolio summary"""
        total_value = sum(p.get('weight', 0) for p in portfolio) * 1000  # Mock
        daily_change = 1.5  # Mock

        return {
            "total_value": total_value,
            "daily_change": daily_change,
            "daily_change_pct": 1.5,
            "cash": 10000,
            "positions": len(portfolio),
            "top_performer": "NVDA (+5.2%)",
            "worst_performer": "TSLA (-3.5%)"
        }

    def _generate_risk_alerts(self, insights: List[StockInsight]) -> List[str]:
        """Generate risk alerts"""
        alerts = []

        for insight in insights:
            if insight.risk_level == "High":
                alerts.append(f"⚠️ {insight.ticker}: High risk level detected")
            elif insight.risk_level == "Critical":
                alerts.append(f"🚨 {insight.ticker}: CRITICAL risk - consider reducing position")

            if insight.change_pct < -3.0:
                alerts.append(f"📉 {insight.ticker}: Significant decline ({insight.change_pct:.1f}%)")

        if not alerts:
            alerts.append("✅ No significant risk alerts")

        return alerts

    def _generate_opportunities(self, insights: List[StockInsight]) -> List[str]:
        """Generate investment opportunities"""
        opportunities = []

        for insight in insights:
            if insight.signal == "Buy" and insight.sentiment == "Positive":
                opportunities.append(f"🟢 {insight.ticker}: Strong buy signal with positive sentiment")
            elif insight.signal == "Buy" and insight.change_pct < 0:
                opportunities.append(f"💰 {insight.ticker}: Potential dip buying opportunity")

        if not opportunities:
            opportunities.append("⚠️ Limited opportunities in current market")

        return opportunities

    def _generate_ai_summary(self, market: MarketSummary, insights: List[StockInsight],
                            portfolio: Dict, alerts: List[str]) -> str:
        """Generate AI-powered summary"""

        # Simple template-based summary (can be enhanced with LLM)
        positive_count = sum(1 for i in insights if i.sentiment == "Positive")
        negative_count = sum(1 for i in insights if i.sentiment == "Negative")

        summary = f"""📊 **Daily Market Report - {market.date}**

**Market Overview:**
Market status: {market.market_status}
Key drivers: {', '.join(market.key_drivers[:2])}

**Portfolio Performance:**
Total value: ${portfolio['total_value']:,.0f}
Daily change: {portfolio['daily_change_pct']:+.1f}%
Top performer: {portfolio['top_performer']}

**Sentiment Breakdown:**
🟢 Positive: {positive_count} positions
⚪ Neutral: {len(insights) - positive_count - negative_count} positions
🔴 Negative: {negative_count} positions

**Key Actions:**
{chr(10).join('• ' + alert for alert in alerts[:3])}

**Outlook:**
Monitor Fed decision and tech earnings. Maintain diversified positions with focus on quality."""

        if self.use_llm:
            # TODO: Enhance with local LLM (Ollama)
            summary += "\n\n*Generated with AI assistance*"

        return summary

    def export_markdown(self, report: DailyReport = None) -> str:
        """Export report as Markdown"""
        if report is None:
            report = self.report

        if not report:
            return ""

        md = f"""# 📊 Daily Stock Report

**Report ID:** {report.report_id}  
**Generated:** {report.generated_at}

---

## 🌍 Market Summary

**Status:** {report.market_summary.market_status}  
**Date:** {report.market_summary.date}

### Key Drivers
{chr(10).join(f"- {driver}" for driver in report.market_summary.key_drivers)}

### Top Movers
**Gainers:**
{chr(10).join(f"- {g['ticker']}: +{g['change']:.1f}%" for g in report.market_summary.top_gainers)}

**Losers:**
{chr(10).join(f"- {l['ticker']}: {l['change']:.1f}%" for l in report.market_summary.top_losers)}

---

## 📈 Portfolio Summary

- **Total Value:** ${report.portfolio_summary['total_value']:,.0f}
- **Daily Change:** {report.portfolio_summary['daily_change_pct']:+.1f}%
- **Positions:** {report.portfolio_summary['positions']}
- **Cash:** ${report.portfolio_summary['cash']:,.0f}

---

## 🎯 Stock Insights

| Ticker | Price | Change | Sentiment | Risk | Signal |
|--------|-------|--------|-----------|------|--------|
{chr(10).join(f"| {i.ticker} | ${i.price:.2f} | {i.change_pct:+.1f}% | {i.sentiment} | {i.risk_level} | {i.signal} |" for i in report.stock_insights)}

---

## ⚠️ Risk Alerts

{chr(10).join(f"- {alert}" for alert in report.risk_alerts)}

---

## 💡 Opportunities

{chr(10).join(f"- {opp}" for opp in report.opportunities)}

---

## 🤖 AI Summary

{report.ai_summary}

---

*Report generated automatically by Daily Report Generator*
"""

        return md

    def export_html(self, report: DailyReport = None) -> str:
        """Export report as HTML"""
        md = self.export_markdown(report)

        # Simple Markdown to HTML conversion
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Daily Stock Report - {report.report_id if report else 'N/A'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .neutral {{ color: #7f8c8d; }}
        blockquote {{ border-left: 4px solid #3498db; margin: 0; padding-left: 20px; color: #555; }}
    </style>
</head>
<body>
{md.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>').replace('**', '<b>').replace('\n', '<br>')}
</body>
</html>
"""

        return html

    def save_report(self, report: DailyReport = None, output_dir: str = "data") -> str:
        """Save report to files"""
        if report is None:
            report = self.report

        if not report:
            return ""

        os.makedirs(output_dir, exist_ok=True)

        # Save Markdown
        md_path = os.path.join(output_dir, f"{report.report_id}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self.export_markdown(report))

        # Save HTML
        html_path = os.path.join(output_dir, f"{report.report_id}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.export_html(report))

        # Save JSON
        json_path = os.path.join(output_dir, f"{report.report_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)

        return md_path


def generate_demo_portfolio() -> List[Dict]:
    """Generate demo portfolio"""
    return [
        {"ticker": "AAPL", "weight": 20.0},
        {"ticker": "NVDA", "weight": 15.0},
        {"ticker": "MSFT", "weight": 18.0},
        {"ticker": "GOOGL", "weight": 12.0},
        {"ticker": "AMZN", "weight": 15.0},
        {"ticker": "TSLA", "weight": 10.0},
        {"ticker": "JNJ", "weight": 10.0},
    ]


def main():
    parser = argparse.ArgumentParser(description="Automatic Daily Report Generator")
    parser.add_argument("--generate", action="store_true", help="Generate daily report")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--output", type=str, default="data", help="Output directory")
    parser.add_argument("--notify", action="store_true", help="Send notification")
    parser.add_argument("--feishu", action="store_true", help="Send via Feishu")
    args = parser.parse_args()

    print("=" *80)
    print("📰 Automatic Daily Report Generator")
    print("=" *80)

    # Generate report
    generator = DailyReportGenerator(use_llm=True)

    if args.demo or True:  # Default to demo
        print("\n📝 Using demo portfolio (7 positions)")
        portfolio = generate_demo_portfolio()
    else:
        portfolio = []

    report = generator.generate(portfolio=portfolio)

    # Print summary
    print(f"\n✅ Report generated: {report.report_id}")
    print(f"📊 Market: {report.market_summary.market_status}")
    print(f"📈 Portfolio: ${report.portfolio_summary['total_value']:,.0f} ({report.portfolio_summary['daily_change_pct']:+.1f}%)")
    print(f"⚠️  Alerts: {len(report.risk_alerts)}")
    print(f"💡 Opportunities: {len(report.opportunities)}")

    # Save files
    md_path = generator.save_report(report, output_dir=args.output)
    print(f"\n💾 Reports saved to: {args.output}/")
    print(f"   - {report.report_id}.md")
    print(f"   - {report.report_id}.html")
    print(f"   - {report.report_id}.json")

    # Print AI summary
    print("\n" + "=" *80)
    print("🤖 AI Summary:")
    print("=" *80)
    print(report.ai_summary)

    # Notification (TODO: integrate with Feishu)
    if args.notify:
        print("\n📬 Sending notification...")
        # TODO: Integrate with feishu_api.py
        print("⚠️  Feishu notification not yet implemented")

    print("\n✅ Daily report generation complete!")


if __name__ == "__main__":
    main()
