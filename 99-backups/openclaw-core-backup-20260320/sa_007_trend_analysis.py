#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-007: Trend Analysis
Comprehensive trend analysis (short/medium/long term, trend strength, ADX)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class TrendAnalyzer:
    """Analyze price trends across multiple timeframes"""

    def __init__(self, data_dir: str = "60-DATA/stock_trends"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.timeframes = {
            "short": 10,
            "medium": 30,
            "long": 60
        }

        self.analysis_log = self._load_analysis_log()

    def _load_analysis_log(self) -> Dict:
        """Load analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "analyses": [],
            "stats": {
                "total_analyses": 0,
                "trends_identified": 0,
            }
        }

    def _save_analysis_log(self):
        """Save analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_log, f, ensure_ascii=False, indent=2)

    def calculate_moving_averages(self, prices: List[float]) -> Dict[str, float]:
        """
        Calculate multiple moving averages
        
        Args:
            prices: List of closing prices
            
        Returns:
            Dict with MA values
        """
        result = {}

        # Common MA periods
        ma_periods = [5, 10, 20, 30, 50, 60, 120, 200]

        for period in ma_periods:
            if len(prices) >= period:
                ma = sum(prices[-period:]) / period
                result[f"MA{period}"] = round(ma, 2)

        return result

    def calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average
        
        Args:
            prices: List of closing prices
            period: EMA period
            
        Returns:
            EMA value or None if insufficient data
        """
        if len(prices) < period:
            return None

        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period

        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return round(ema, 2)

    def calculate_adx(self, highs: List[float], lows: List[float],
                     closes: List[float], period: int = 14) -> Optional[Dict]:
        """
        Calculate Average Directional Index (ADX)
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ADX period (default 14)
            
        Returns:
            Dict with ADX, +DI, -DI values
        """
        if len(highs) < period + 1:
            return None

        # Calculate True Range (TR) and Directional Movement (DM)
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []

        for i in range(1, len(highs)):
            # True Range
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i -1]),
                abs(lows[i] - closes[i -1])
            )
            tr_list.append(tr)

            # Directional Movement
            plus_dm = max(highs[i] - highs[i -1], 0)
            minus_dm = max(lows[i -1] - lows[i], 0)

            if plus_dm > minus_dm:
                minus_dm_list.append(0)
            else:
                plus_dm_list.append(0)

            plus_dm_list.append(plus_dm if plus_dm > minus_dm else 0)
            minus_dm_list.append(minus_dm if minus_dm > plus_dm else 0)

        # Smooth TR and DM
        tr_smooth = sum(tr_list[:period])
        plus_dm_smooth = sum(plus_dm_list[:period])
        minus_dm_smooth = sum(minus_dm_list[:period])

        for i in range(period, len(tr_list)):
            tr_smooth = tr_smooth - tr_smooth /period + tr_list[i]
            plus_dm_smooth = plus_dm_smooth - plus_dm_smooth /period + plus_dm_list[i]
            minus_dm_smooth = minus_dm_smooth - minus_dm_smooth /period + minus_dm_list[i]

        # Calculate DI
        plus_di = 100 * (plus_dm_smooth / tr_smooth) if tr_smooth != 0 else 0
        minus_di = 100 * (minus_dm_smooth / tr_smooth) if tr_smooth != 0 else 0

        # Calculate DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) != 0 else 0

        # Calculate ADX (average of DX)
        adx = dx  # Simplified - would need more periods for true ADX

        return {
            "adx": round(adx, 2),
            "plus_di": round(plus_di, 2),
            "minus_di": round(minus_di, 2),
            "trend_strength": self._interpret_adx(adx)
        }

    def _interpret_adx(self, adx: float) -> str:
        """Interpret ADX value"""
        if adx < 20:
            return "weak"
        elif adx < 40:
            return "moderate"
        elif adx < 60:
            return "strong"
        else:
            return "very_strong"

    def analyze_trend(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        Comprehensive trend analysis
        
        Args:
            symbol: Stock symbol
            candles: List of candle data
            
        Returns:
            Dict with trend analysis results
        """
        if not candles or len(candles) < 60:
            return {"error": "Insufficient data (need at least 60 candles)"}

        # Extract price arrays
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]

        result = {
            "symbol": symbol,
            "candle_count": len(candles),
            "analyzed_at": datetime.now().isoformat(),
            "current_price": closes[-1],
            "timeframes": {},
            "moving_averages": {},
            "trend_indicators": {},
            "overall_trend": "",
            "trend_strength": "",
            "recommendation": ""
        }

        # Calculate moving averages
        result["moving_averages"] = self.calculate_moving_averages(closes)

        # Analyze each timeframe
        for tf_name, tf_period in self.timeframes.items():
            if len(candles) >= tf_period:
                tf_closes = closes[-tf_period:]
                tf_analysis = self._analyze_timeframe(tf_closes, tf_name)
                result["timeframes"][tf_name] = tf_analysis

        # Calculate ADX
        adx_result = self.calculate_adx(highs, lows, closes)
        if adx_result:
            result["trend_indicators"]["adx"] = adx_result

        # Determine overall trend
        result["overall_trend"] = self._determine_overall_trend(result)
        result["trend_strength"] = self._determine_trend_strength(result)
        result["recommendation"] = self._generate_recommendation(result)

        # Save to cache
        cache_file = self.data_dir / f"{symbol}_trend.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Log analysis
        self._log_analysis(symbol, result["overall_trend"], success=True)

        return result

    def _analyze_timeframe(self, prices: List[float], timeframe: str) -> Dict:
        """Analyze trend for a specific timeframe"""
        if len(prices) < 10:
            return {"error": "Insufficient data"}

        current_price = prices[-1]
        start_price = prices[0]
        price_change = (current_price - start_price) / start_price * 100

        # Calculate trend direction
        if price_change > 5:
            direction = "bullish"
        elif price_change < -5:
            direction = "bearish"
        else:
            direction = "sideways"

        # Calculate trend strength
        volatility = self._calculate_volatility(prices)
        if volatility > 0.05:
            strength = "strong"
        elif volatility > 0.02:
            strength = "moderate"
        else:
            strength = "weak"

        # Calculate linear regression slope
        slope = self._calculate_slope(prices)

        return {
            "direction": direction,
            "strength": strength,
            "price_change_pct": round(price_change, 2),
            "volatility": round(volatility * 100, 2),
            "slope": round(slope, 4),
            "start_price": round(start_price, 2),
            "end_price": round(current_price, 2)
        }

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0

        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std = math.sqrt(variance)

        return std / mean if mean != 0 else 0

    def _calculate_slope(self, prices: List[float]) -> float:
        """Calculate linear regression slope"""
        n = len(prices)
        if n < 2:
            return 0

        sum_x = sum(range(n))
        sum_y = sum(prices)
        sum_xy = sum(i * prices[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope / prices[0] if prices[0] != 0 else 0

    def _determine_overall_trend(self, result: Dict) -> str:
        """Determine overall trend from multiple timeframes"""
        timeframes = result.get("timeframes", {})

        if not timeframes:
            return "unknown"

        # Count trend directions
        bullish_count = sum(1 for tf in timeframes.values() if tf.get("direction") == "bullish")
        bearish_count = sum(1 for tf in timeframes.values() if tf.get("direction") == "bearish")
        total = len(timeframes)

        if bullish_count > total / 2:
            return "bullish"
        elif bearish_count > total / 2:
            return "bearish"
        else:
            return "sideways"

    def _determine_trend_strength(self, result: Dict) -> str:
        """Determine overall trend strength"""
        timeframes = result.get("timeframes", {})
        adx_result = result.get("trend_indicators", {}).get("adx", {})

        # Get ADX strength
        adx_strength = adx_result.get("trend_strength", "unknown")

        # Count strong trends
        strong_count = sum(1 for tf in timeframes.values() if tf.get("strength") == "strong")

        if adx_strength in ["strong", "very_strong"] or strong_count >= 2:
            return "strong"
        elif adx_strength == "moderate" or strong_count >= 1:
            return "moderate"
        else:
            return "weak"

    def _generate_recommendation(self, result: Dict) -> str:
        """Generate trading recommendation based on trend analysis"""
        overall_trend = result.get("overall_trend", "unknown")
        trend_strength = result.get("trend_strength", "weak")
        current_price = result.get("current_price", 0)
        mas = result.get("moving_averages", {})

        # Check price vs MA relationship
        above_ma50 = current_price > mas.get("MA50", current_price)
        above_ma200 = current_price > mas.get("MA200", current_price)

        # Generate recommendation
        if overall_trend == "bullish" and trend_strength == "strong":
            if above_ma50 and above_ma200:
                return "STRONG BUY - Uptrend confirmed across all timeframes"
            else:
                return "BUY - Bullish trend, watch MA support"

        elif overall_trend == "bullish" and trend_strength == "moderate":
            return "HOLD/BUY - Moderate uptrend, consider entry on pullback"

        elif overall_trend == "bearish" and trend_strength == "strong":
            if not above_ma50 and not above_ma200:
                return "STRONG SELL - Downtrend confirmed across all timeframes"
            else:
                return "SELL - Bearish trend, consider exit"

        elif overall_trend == "bearish" and trend_strength == "moderate":
            return "HOLD/SELL - Moderate downtrend, watch resistance"

        else:
            return "NEUTRAL - Sideways market, wait for breakout"

    def _log_analysis(self, symbol: str, trend: str, success: bool):
        """Log analysis attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "trend": trend,
            "success": success
        }

        self.analysis_log["analyses"].append(log_entry)
        self.analysis_log["stats"]["total_analyses"] += 1
        self.analysis_log["stats"]["trends_identified"] += 1

        # Keep only last 500 entries
        self.analysis_log["analyses"] = self.analysis_log["analyses"][-500:]

        self._save_analysis_log()

    def get_stats(self) -> Dict:
        """Get analysis statistics"""
        return self.analysis_log["stats"].copy()

    def display_status(self) -> str:
        """Display analyzer status"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 18 + "Trend Analyzer Status")
        output.append("=" * 70)

        output.append(f"\n[Timeframes]")
        for tf, period in self.timeframes.items():
            output.append(f"  - {tf.title()}: {period} candles")

        output.append(f"\n[Statistics]")
        output.append(f"  Total Analyses:     {stats['total_analyses']}")
        output.append(f"  Trends Identified:  {stats['trends_identified']}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 16 + "SA-007: Trend Analysis")
    print("=" * 70)

    analyzer = TrendAnalyzer()

    # Test 1: Display status
    print(analyzer.display_status())

    # Test 2: Generate test data
    print("\n[Test 1] Generate Test Data")
    print("-" * 70)
    import random
    random.seed(42)

    candles = []
    price = 100

    # Create uptrend with pullbacks
    for i in range(100):
        if i < 30:  # Initial uptrend
            price *= (1 + random.uniform(0.005, 0.02))
        elif i < 50:  # Pullback
            price *= (1 + random.uniform(-0.015, 0.005))
        elif i < 80:  # Second uptrend
            price *= (1 + random.uniform(0.008, 0.025))
        else:  # Consolidation
            price *= (1 + random.uniform(-0.01, 0.01))

        open_p = price
        close_p = price * (1 + random.uniform(-0.01, 0.01))
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.015))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.015))
        volume = random.randint(5000000, 50000000)

        candles.append({
            "date": f"2026-01-{i%30 +1:02d}",
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume
        })

    print(f"  Generated {len(candles)} candles")
    print(f"  Price range: {min(c['low'] for c in candles):.2f} - {max(c['high'] for c in candles):.2f}")

    # Test 3: Analyze trend
    print("\n[Test 2] Analyze Trend")
    print("-" * 70)
    result = analyzer.analyze_trend("TEST", candles)

    if "error" not in result:
        print(f"  Symbol:           {result['symbol']}")
        print(f"  Current Price:    {result['current_price']}")
        print(f"  Overall Trend:    {result['overall_trend'].upper()}")
        print(f"  Trend Strength:   {result['trend_strength'].upper()}")
        print(f"  Recommendation:   {result['recommendation']}")

        print(f"\n  Timeframes:")
        for tf, analysis in result["timeframes"].items():
            print(f"    {tf.title():8} - Direction: {analysis['direction']:8}, "
                  f"Strength: {analysis['strength']:8}, "
                  f"Change: {analysis['price_change_pct']:+.2f}%")

        print(f"\n  Moving Averages:")
        for ma, value in result["moving_averages"].items():
            above_below = "above" if result["current_price"] > value else "below"
            print(f"    {ma:6}: {value:8.2f} (price {above_below})")

        if "adx" in result["trend_indicators"]:
            adx = result["trend_indicators"]["adx"]
            print(f"\n  ADX Indicator:")
            print(f"    ADX:    {adx['adx']} ({adx['trend_strength']})")
            print(f"    +DI:    {adx['plus_di']}")
            print(f"    -DI:    {adx['minus_di']}")

    # Test 4: Final stats
    print("\n[Test 3] Final Statistics")
    print("-" * 70)
    stats = analyzer.get_stats()
    print(f"  Total Analyses:     {stats['total_analyses']}")
    print(f"  Trends Identified:  {stats['trends_identified']}")

    print("\n[OK] SA-007 Trend Analysis test completed")

if __name__ == "__main__":
    main()
