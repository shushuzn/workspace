import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SA-018: Performance Attribution - Analyze sources of trading returns"""

import json
from datetime import datetime
from pathlib import Path

class PerformanceAttribution:
    def __init__(self, data_dir="60-DATA/stock_performance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def attribute_returns(self, portfolio_return: float, benchmark_return: float,
                         factors: dict) -> dict:
        """Decompose returns into factors"""
        excess_return = portfolio_return - benchmark_return
        
        factor_contributions = {}
        total_factor = 0
        
        for factor_name, factor_value in factors.items():
            contribution = factor_value * 0.1
            factor_contributions[factor_name] = round(contribution, 4)
            total_factor += contribution
        
        residual = excess_return - total_factor
        
        return {
            "analyzed_at": datetime.now().isoformat(),
            "portfolio_return": round(portfolio_return, 4),
            "benchmark_return": round(benchmark_return, 4),
            "excess_return": round(excess_return, 4),
            "factor_contributions": factor_contributions,
            "total_factor_contribution": round(total_factor, 4),
            "residual": round(residual, 4),
            "skill_vs_luck": "skill" if abs(total_factor) > abs(residual) else "luck"
        }
    
    def compare_benchmark(self, portfolio_returns: list, benchmark_returns: list) -> dict:
        """Compare portfolio vs benchmark"""
        if len(portfolio_returns) != len(benchmark_returns):
            return {"error": "Return series must have same length"}
        
        total_portfolio = sum(portfolio_returns)
        total_benchmark = sum(benchmark_returns)
        
        outperformance = total_portfolio - total_benchmark
        win_rate = sum(1 for p, b in zip(portfolio_returns, benchmark_returns) if p > b) / len(portfolio_returns)
        
        return {
            "compared_at": datetime.now().isoformat(),
            "periods": len(portfolio_returns),
            "total_portfolio": round(total_portfolio, 4),
            "total_benchmark": round(total_benchmark, 4),
            "outperformance": round(outperformance, 4),
            "win_rate": round(win_rate, 2),
            "outperformed": outperformance > 0
        }

logging.basicConfig(level=logging.INFO)
def main():
    print("=" * 70)
    print(" " * 16 + "SA-018: Performance Attribution")
    print("=" * 70)
    
    attr = PerformanceAttribution()
    
    result = attr.attribute_returns(
        portfolio_return=0.15,
        benchmark_return=0.10,
        factors={"market": 0.8, "size": 0.3, "momentum": 0.5, "value": -0.2}
    )
    
    print(f"\n  Portfolio Return:  {result['portfolio_return']*100:.2f}%")
    print(f"  Benchmark Return:  {result['benchmark_return']*100:.2f}%")
    print(f"  Excess Return:     {result['excess_return']*100:.2f}%")
    print(f"\n  Factor Contributions:")
    for factor, contrib in result["factor_contributions"].items():
        print(f"    {factor}: {contrib*100:.2f}%")
    print(f"\n  Skill vs Luck:     {result['skill_vs_luck'].upper()}")
    
    print(f"\n[OK] SA-018 Performance Attribution test completed")

if __name__ == "__main__":
    main()
