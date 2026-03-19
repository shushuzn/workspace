#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-015: Market Regime Detector
Identify market conditions (bull/bear/sideways/volatile)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import math

class MarketRegimeDetector:
    """Detect market regime conditions"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_regimes"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_log = self._load_analysis_log()
    
    def _load_analysis_log(self) -> Dict:
        log_file = self.data_dir / "analysis_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0", "analyses": [], "stats": {"total_analyses": 0}}
    
    def _save_analysis_log(self):
        log_file = self.data_dir / "analysis_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_log, f, ensure_ascii=False, indent=2)
    
    def detect_regime(self, symbol: str, candles: List[Dict], lookback: int = 60) -> Dict:
        """Detect market regime from price data"""
        if not candles or len(candles) < lookback:
            return {"error": "Insufficient data"}
        
        recent = candles[-lookback:]
        closes = [c["close"] for c in recent]
        highs = [c["high"] for c in recent]
        lows = [c["low"] for c in recent]
        
        # Calculate metrics
        trend = self._calculate_trend(closes)
        volatility = self._calculate_volatility(closes)
        momentum = self._calculate_momentum(closes)
        
        # Classify regime
        regime = self._classify_regime(trend, volatility, momentum)
        
        result = {
            "symbol": symbol,
            "detected_at": datetime.now().isoformat(),
            "lookback": lookback,
            "current_price": closes[-1],
            "metrics": {
                "trend": round(trend, 4),
                "volatility": round(volatility, 4),
                "momentum": round(momentum, 4)
            },
            "regime": regime,
            "confidence": self._calculate_confidence(trend, volatility, momentum)
        }
        
        cache_file = self.data_dir / f"{symbol}_regime.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self._log_analysis(symbol, regime["type"], success=True)
        return result
    
    def _calculate_trend(self, prices: List[float]) -> float:
        n = len(prices)
        if n < 2: return 0
        return (prices[-1] - prices[0]) / prices[0]
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        if len(prices) < 2: return 0
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        return math.sqrt(variance) / mean
    
    def _calculate_momentum(self, prices: List[float]) -> float:
        if len(prices) < 10: return 0
        return (prices[-1] - prices[-10]) / prices[-10]
    
    def _classify_regime(self, trend: float, volatility: float, momentum: float) -> Dict:
        trend_threshold = 0.05
        vol_threshold = 0.03
        
        if volatility > vol_threshold * 1.5:
            regime_type = "highly_volatile"
            description = "High volatility regime - expect large price swings"
        elif trend > trend_threshold and momentum > 0:
            regime_type = "bull"
            description = "Bull market - sustained uptrend"
        elif trend < -trend_threshold and momentum < 0:
            regime_type = "bear"
            description = "Bear market - sustained downtrend"
        elif abs(trend) < trend_threshold * 0.5:
            regime_type = "sideways"
            description = "Sideways/consolidation - range-bound market"
        else:
            regime_type = "transition"
            description = "Transition regime - unclear direction"
        
        return {"type": regime_type, "description": description}
    
    def _calculate_confidence(self, trend: float, volatility: float, momentum: float) -> float:
        return min(1.0, abs(trend) * 5 + abs(momentum) * 3 + (1 - volatility * 10))
    
    def _log_analysis(self, symbol: str, regime: str, success: bool):
        log_entry = {"timestamp": datetime.now().isoformat(), "symbol": symbol, "regime": regime, "success": success}
        self.analysis_log["analyses"].append(log_entry)
        self.analysis_log["stats"]["total_analyses"] += 1
        self.analysis_log["analyses"] = self.analysis_log["analyses"][-100:]
        self._save_analysis_log()
    
    def get_stats(self) -> Dict:
        return self.analysis_log["stats"].copy()
    
    def display_status(self) -> str:
        stats = self.get_stats()
        return f"\n{'='*70}\n{' '*18}Market Regime Detector\n{'='*70}\n\n[Regime Types]\n  - Bull/Bear/Sideways/Volatile/Transition\n\n[Statistics]\n  Total Analyses: {stats['total_analyses']}\n\n{'='*70}\n"

def main():
    print("=" * 70)
    print(" " * 18 + "SA-015: Market Regime Detector")
    print("=" * 70)
    
    detector = MarketRegimeDetector()
    print(detector.display_status())
    
    import random
    random.seed(42)
    candles = []
    price = 100
    for i in range(100):
        price *= (1 + random.uniform(-0.015, 0.025))
        candles.append({"close": price, "high": price*1.01, "low": price*0.99})
    
    print(f"\n[Test] Detect Market Regime")
    print("-" * 70)
    result = detector.detect_regime("TEST", candles)
    
    if "error" not in result:
        print(f"  Symbol:        {result['symbol']}")
        print(f"  Regime:        {result['regime']['type'].upper()}")
        print(f"  Description:   {result['regime']['description']}")
        print(f"  Confidence:    {result['confidence']*100:.0f}%")
        print(f"  Trend:         {result['metrics']['trend']*100:.2f}%")
        print(f"  Volatility:    {result['metrics']['volatility']*100:.2f}%")
        print(f"  Momentum:      {result['metrics']['momentum']*100:.2f}%")
    
    print(f"\n[OK] SA-015 Market Regime Detector test completed")

if __name__ == "__main__":
    main()
