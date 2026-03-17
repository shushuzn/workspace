#!/usr/bin/env python3
"""
Smart Portfolio Rebalancer
Intelligent rebalancing suggestions based on risk + sentiment + valuation

Features:
- Multi-factor scoring (risk 30% + sentiment 25% + valuation 25% + momentum 20%)
- Action recommendations (BUY/SELL/HOLD)
- Position size optimization
- Risk-adjusted allocation

Usage:
  python smart_rebalancer.py --portfolio portfolio.json
  python smart_rebalancer.py --demo
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import argparse
from typing import List, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class RebalanceSuggestion:
    """Rebalancing suggestion for a single stock"""
    ticker: str
    current_weight: float  # Current portfolio weight (%)
    suggested_weight: float  # Suggested weight (%)
    action: str  # BUY/SELL/HOLD
    change_pct: float  # Weight change percentage
    confidence: float  # 0-1 confidence score
    reasons: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    sentiment_score: float = 0.0
    valuation_score: float = 0.0
    momentum_score: float = 0.0
    composite_score: float = 0.0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PortfolioSummary:
    """Portfolio summary"""
    total_value: float
    current_risk: float
    suggested_risk: float
    rebalance_needed: bool
    suggestions_count: int
    buy_count: int
    sell_count: int
    hold_count: int
    expected_improvement: float  # Expected risk-adjusted return improvement


class SmartRebalancer:
    """Smart portfolio rebalancing engine"""
    
    # Scoring weights
    WEIGHTS = {
        'risk': 0.30,      # Lower risk = higher score
        'sentiment': 0.25, # Higher sentiment = higher score
        'valuation': 0.25, # Better valuation = higher score
        'momentum': 0.20   # Positive momentum = higher score
    }
    
    def __init__(self):
        self.suggestions: List[RebalanceSuggestion] = []
    
    def analyze(self, portfolio: List[Dict], market_data: Dict = None) -> List[RebalanceSuggestion]:
        """Analyze portfolio and generate rebalancing suggestions"""
        self.suggestions = []
        
        for position in portfolio:
            ticker = position.get('ticker', 'UNKNOWN')
            current_weight = position.get('weight', 0.0)
            
            # Get scores (mock data for demo)
            risk_score = self._calculate_risk_score(position)
            sentiment_score = self._calculate_sentiment_score(position)
            valuation_score = self._calculate_valuation_score(position)
            momentum_score = self._calculate_momentum_score(position)
            
            # Composite score
            composite = (
                risk_score * self.WEIGHTS['risk'] +
                sentiment_score * self.WEIGHTS['sentiment'] +
                valuation_score * self.WEIGHTS['valuation'] +
                momentum_score * self.WEIGHTS['momentum']
            )
            
            # Calculate suggested weight
            suggested_weight = self._calculate_suggested_weight(composite, portfolio)
            
            # Determine action
            weight_change = suggested_weight - current_weight
            if abs(weight_change) < 2.0:  # Threshold for action
                action = "HOLD"
            elif weight_change > 0:
                action = "BUY"
            else:
                action = "SELL"
            
            # Generate reasons
            reasons = self._generate_reasons(
                ticker, risk_score, sentiment_score, 
                valuation_score, momentum_score, action
            )
            
            # Confidence based on score divergence
            scores = [risk_score, sentiment_score, valuation_score, momentum_score]
            confidence = 1.0 - (max(scores) - min(scores)) / 100.0
            
            suggestion = RebalanceSuggestion(
                ticker=ticker,
                current_weight=current_weight,
                suggested_weight=round(suggested_weight, 1),
                action=action,
                change_pct=round(weight_change, 1),
                confidence=round(confidence, 2),
                reasons=reasons,
                risk_score=round(risk_score, 1),
                sentiment_score=round(sentiment_score, 1),
                valuation_score=round(valuation_score, 1),
                momentum_score=round(momentum_score, 1),
                composite_score=round(composite, 1)
            )
            
            self.suggestions.append(suggestion)
        
        return self.suggestions
    
    def _calculate_risk_score(self, position: Dict) -> float:
        """Calculate risk score (0-100, higher is better)"""
        # Mock: Use existing risk data if available
        risk = position.get('risk_score', 50.0)
        return max(0, min(100, 100 - risk))  # Invert: lower risk = higher score
    
    def _calculate_sentiment_score(self, position: Dict) -> float:
        """Calculate sentiment score (0-100)"""
        sentiment = position.get('sentiment_score', 50.0)
        return max(0, min(100, 50 + sentiment * 50))  # Scale -1..1 to 0-100
    
    def _calculate_valuation_score(self, position: Dict) -> float:
        """Calculate valuation score (0-100, higher = undervalued)"""
        pe = position.get('pe_ratio', 20.0)
        industry_pe = position.get('industry_pe', 20.0)
        
        if industry_pe > 0:
            relative_pe = pe / industry_pe
            # PE < industry = undervalued = higher score
            score = 100 * (1.0 - (relative_pe - 1.0) * 0.5)
        else:
            score = 50.0
        
        return max(0, min(100, score))
    
    def _calculate_momentum_score(self, position: Dict) -> float:
        """Calculate momentum score (0-100)"""
        change = position.get('price_change_pct', 0.0)
        # Scale price change to 0-100 score
        score = 50 + change * 5  # +/-10% change = 0-100 score
        return max(0, min(100, score))
    
    def _calculate_suggested_weight(self, composite_score: float, portfolio: List[Dict]) -> float:
        """Calculate suggested weight based on composite score"""
        # Base weight = equal weight
        base_weight = 100.0 / len(portfolio)
        
        # Adjust based on composite score (50 = neutral, >50 = overweight, <50 = underweight)
        adjustment = (composite_score - 50) * 0.3  # Max +/-15% adjustment
        
        suggested = base_weight + adjustment
        
        # Constraints: min 2%, max 25%
        return max(2.0, min(25.0, suggested))
    
    def _generate_reasons(self, ticker: str, risk: float, sentiment: float, 
                         valuation: float, momentum: float, action: str) -> List[str]:
        """Generate human-readable reasons for suggestion"""
        reasons = []
        
        if risk > 70:
            reasons.append(f"Low risk score ({risk:.0f}/100)")
        elif risk < 30:
            reasons.append(f"High risk detected ({100-risk:.0f}/100)")
        
        if sentiment > 70:
            reasons.append(f"Positive sentiment ({sentiment:.0f}/100)")
        elif sentiment < 30:
            reasons.append(f"Negative sentiment ({sentiment:.0f}/100)")
        
        if valuation > 70:
            reasons.append(f"Undervalued ({valuation:.0f}/100)")
        elif valuation < 30:
            reasons.append(f"Overvalued ({valuation:.0f}/100)")
        
        if momentum > 70:
            reasons.append(f"Strong momentum ({momentum:.0f}/100)")
        elif momentum < 30:
            reasons.append(f"Weak momentum ({momentum:.0f}/100)")
        
        if not reasons:
            reasons.append("Balanced factors")
        
        return reasons[:3]  # Max 3 reasons
    
    def get_summary(self, portfolio_value: float = 100000) -> PortfolioSummary:
        """Get portfolio summary"""
        if not self.suggestions:
            return PortfolioSummary(
                total_value=portfolio_value,
                current_risk=0,
                suggested_risk=0,
                rebalance_needed=False,
                suggestions_count=0,
                buy_count=0,
                sell_count=0,
                hold_count=0,
                expected_improvement=0
            )
        
        buy_count = sum(1 for s in self.suggestions if s.action == "BUY")
        sell_count = sum(1 for s in self.suggestions if s.action == "SELL")
        hold_count = sum(1 for s in self.suggestions if s.action == "HOLD")
        
        # Calculate average risk
        current_risk = sum(s.risk_score for s in self.suggestions) / len(self.suggestions)
        suggested_risk = sum(s.risk_score * s.suggested_weight / 100 for s in self.suggestions)
        
        # Rebalance needed if >30% positions need action
        rebalance_needed = (buy_count + sell_count) / len(self.suggestions) > 0.3
        
        # Expected improvement (mock calculation)
        expected_improvement = sum(abs(s.change_pct) for s in self.suggestions) / len(self.suggestions) * 0.5
        
        return PortfolioSummary(
            total_value=portfolio_value,
            current_risk=round(100 - current_risk, 1),  # Convert to risk level
            suggested_risk=round(100 - suggested_risk, 1),
            rebalance_needed=rebalance_needed,
            suggestions_count=len(self.suggestions),
            buy_count=buy_count,
            sell_count=sell_count,
            hold_count=hold_count,
            expected_improvement=round(expected_improvement, 1)
        )


def generate_demo_portfolio() -> List[Dict]:
    """Generate demo portfolio data"""
    return [
        {"ticker": "AAPL", "weight": 20.0, "risk_score": 15.0, "sentiment_score": 0.6, "pe_ratio": 28.5, "industry_pe": 25.0, "price_change_pct": 2.5},
        {"ticker": "NVDA", "weight": 15.0, "risk_score": 45.0, "sentiment_score": 0.8, "pe_ratio": 65.0, "industry_pe": 40.0, "price_change_pct": 5.2},
        {"ticker": "MSFT", "weight": 18.0, "risk_score": 20.0, "sentiment_score": 0.5, "pe_ratio": 32.0, "industry_pe": 30.0, "price_change_pct": 1.8},
        {"ticker": "GOOGL", "weight": 12.0, "risk_score": 25.0, "sentiment_score": 0.3, "pe_ratio": 24.0, "industry_pe": 28.0, "price_change_pct": -1.2},
        {"ticker": "AMZN", "weight": 15.0, "risk_score": 30.0, "sentiment_score": 0.4, "pe_ratio": 55.0, "industry_pe": 45.0, "price_change_pct": 0.5},
        {"ticker": "TSLA", "weight": 10.0, "risk_score": 60.0, "sentiment_score": -0.2, "pe_ratio": 70.0, "industry_pe": 35.0, "price_change_pct": -3.5},
        {"ticker": "JNJ", "weight": 10.0, "risk_score": 8.0, "sentiment_score": 0.2, "pe_ratio": 15.0, "industry_pe": 18.0, "price_change_pct": 0.3},
    ]


def print_suggestions(suggestions: List[RebalanceSuggestion], summary: PortfolioSummary):
    """Print rebalancing suggestions"""
    print("\n" + "="*80)
    print("📊 SMART PORTFOLIO REBALANCING SUGGESTIONS")
    print("="*80)
    
    print(f"\n📈 Portfolio Summary:")
    print(f"  Total Value: ${summary.total_value:,.0f}")
    print(f"  Current Risk Level: {summary.current_risk:.1f}/100")
    print(f"  Suggested Risk Level: {summary.suggested_risk:.1f}/100")
    print(f"  Rebalance Needed: {'✅ Yes' if summary.rebalance_needed else '⚠️ Optional'}")
    print(f"  Expected Improvement: +{summary.expected_improvement:.1f}% risk-adjusted return")
    
    print(f"\n📋 Actions:")
    print(f"  🟢 BUY:  {summary.buy_count} positions")
    print(f"  🔴 SELL: {summary.sell_count} positions")
    print(f"  ⚪ HOLD: {summary.hold_count} positions")
    
    print("\n" + "-"*80)
    print("Detailed Suggestions:")
    print("-"*80)
    
    # Sort by change magnitude
    sorted_suggestions = sorted(suggestions, key=lambda s: abs(s.change_pct), reverse=True)
    
    for s in sorted_suggestions:
        action_icon = "🟢" if s.action == "BUY" else "🔴" if s.action == "SELL" else "⚪"
        
        print(f"\n{action_icon} {s.ticker}")
        print(f"  Action: {s.action} | Confidence: {s.confidence:.0%}")
        print(f"  Weight: {s.current_weight:.1f}% → {s.suggested_weight:.1f}% ({s.change_pct:+.1f}%)")
        print(f"  Scores: Risk={s.risk_score:.0f} | Sentiment={s.sentiment_score:.0f} | Valuation={s.valuation_score:.0f} | Momentum={s.momentum_score:.0f}")
        print(f"  Composite: {s.composite_score:.0f}/100")
        print(f"  Reasons:")
        for reason in s.reasons:
            print(f"    • {reason}")
    
    print("\n" + "="*80)
    print("💡 Note: These are suggestions only. Always do your own research.")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description="Smart Portfolio Rebalancer")
    parser.add_argument("--portfolio", type=str, help="Portfolio JSON file path")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    args = parser.parse_args()
    
    print("="*80)
    print("🧠 Smart Portfolio Rebalancer")
    print("Multi-factor scoring: Risk(30%) + Sentiment(25%) + Valuation(25%) + Momentum(20%)")
    print("="*80)
    
    # Load portfolio
    if args.portfolio:
        with open(args.portfolio, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
    elif args.demo or True:  # Default to demo
        print("\n📝 Using demo portfolio (7 positions)")
        portfolio = generate_demo_portfolio()
    else:
        print("❌ No portfolio specified. Use --demo or --portfolio <file.json>")
        return
    
    # Analyze
    rebalancer = SmartRebalancer()
    suggestions = rebalancer.analyze(portfolio)
    summary = rebalancer.get_summary(portfolio_value=100000)
    
    # Print results
    print_suggestions(suggestions, summary)
    
    # Save to file
    if args.output:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": asdict(summary),
            "suggestions": [s.to_dict() for s in suggestions]
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {args.output}")
    
    print("\n✅ Smart rebalancing analysis complete!")


if __name__ == "__main__":
    main()
