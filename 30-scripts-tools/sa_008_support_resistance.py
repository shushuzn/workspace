#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-008: Support & Resistance
Automatic support and resistance level detection (pivot points, Fibonacci, volume profile)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class SupportResistanceAnalyzer:
    """Detect and analyze support and resistance levels"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_sr_levels"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
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
                "levels_detected": 0,
            }
        }
    
    def _save_analysis_log(self):
        """Save analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_log, f, ensure_ascii=False, indent=2)
    
    def calculate_pivot_points(self, high: float, low: float, close: float) -> Dict:
        """
        Calculate classic pivot points
        
        Args:
            high: Previous period high
            low: Previous period low
            close: Previous period close
            
        Returns:
            Dict with pivot point levels
        """
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            "pivot": round(pivot, 2),
            "resistance_1": round(r1, 2),
            "resistance_2": round(r2, 2),
            "resistance_3": round(r3, 2),
            "support_1": round(s1, 2),
            "support_2": round(s2, 2),
            "support_3": round(s3, 2)
        }
    
    def calculate_fibonacci_retracement(self, high: float, low: float) -> Dict:
        """
        Calculate Fibonacci retracement levels
        
        Args:
            high: Swing high
            low: Swing low
            
        Returns:
            Dict with Fibonacci levels
        """
        diff = high - low
        
        levels = {
            "0.0%": round(high, 2),
            "23.6%": round(high - 0.236 * diff, 2),
            "38.2%": round(high - 0.382 * diff, 2),
            "50.0%": round(high - 0.5 * diff, 2),
            "61.8%": round(high - 0.618 * diff, 2),
            "78.6%": round(high - 0.786 * diff, 2),
            "100.0%": round(low, 2)
        }
        
        # Extension levels
        levels["127.2%"] = round(low - 0.272 * diff, 2)
        levels["161.8%"] = round(low - 0.618 * diff, 2)
        
        return levels
    
    def find_price_clusters(self, candles: List[Dict], window: int = 50, 
                           tolerance: float = 0.02) -> List[Dict]:
        """
        Find price levels where price has reversed multiple times
        
        Args:
            candles: List of candle data
            window: Number of candles to analyze
            tolerance: Price tolerance for clustering (2%)
            
        Returns:
            List of support/resistance clusters
        """
        if len(candles) < window:
            return []
        
        recent_candles = candles[-window:]
        
        # Find local highs and lows
        highs = []
        lows = []
        
        for i in range(2, len(recent_candles) - 2):
            candle = recent_candles[i]
            prev_candle = recent_candles[i-1]
            next_candle = recent_candles[i+1]
            
            # Local high
            if candle["high"] > prev_candle["high"] and candle["high"] > next_candle["high"]:
                if candle["high"] > prev_candle["close"] and candle["high"] > next_candle["close"]:
                    highs.append(candle["high"])
            
            # Local low
            if candle["low"] < prev_candle["low"] and candle["low"] < next_candle["low"]:
                if candle["low"] < prev_candle["close"] and candle["low"] < next_candle["close"]:
                    lows.append(candle["low"])
        
        # Cluster highs (resistance levels)
        resistance_clusters = self._cluster_prices(highs, tolerance)
        
        # Cluster lows (support levels)
        support_clusters = self._cluster_prices(lows, tolerance)
        
        # Format results
        levels = []
        
        for cluster in resistance_clusters:
            if cluster["count"] >= 2:  # At least 2 touches
                levels.append({
                    "type": "resistance",
                    "price": round(cluster["avg"], 2),
                    "touches": cluster["count"],
                    "strength": self._calculate_level_strength(cluster["count"], cluster["recency"]),
                    "last_touch": cluster["last_touch"]
                })
        
        for cluster in support_clusters:
            if cluster["count"] >= 2:
                levels.append({
                    "type": "support",
                    "price": round(cluster["avg"], 2),
                    "touches": cluster["count"],
                    "strength": self._calculate_level_strength(cluster["count"], cluster["recency"]),
                    "last_touch": cluster["last_touch"]
                })
        
        # Sort by strength
        levels.sort(key=lambda x: x["strength"], reverse=True)
        
        return levels
    
    def _cluster_prices(self, prices: List[float], tolerance: float) -> List[Dict]:
        """Cluster similar prices together"""
        if not prices:
            return []
        
        clusters = []
        
        for price in prices:
            found_cluster = False
            
            for cluster in clusters:
                if abs(price - cluster["avg"]) / cluster["avg"] < tolerance:
                    # Add to existing cluster
                    cluster["prices"].append(price)
                    cluster["count"] += 1
                    cluster["avg"] = sum(cluster["prices"]) / len(cluster["prices"])
                    cluster["recency"] = max(cluster["recency"], 1)
                    found_cluster = True
                    break
            
            if not found_cluster:
                # Create new cluster
                clusters.append({
                    "prices": [price],
                    "count": 1,
                    "avg": price,
                    "recency": 10,  # Most recent
                    "last_touch": "recent"
                })
        
        # Update recency
        for cluster in clusters:
            cluster["recency"] = max(1, cluster["recency"])
        
        return clusters
    
    def _calculate_level_strength(self, touches: int, recency: int) -> float:
        """Calculate strength of support/resistance level"""
        # More touches = stronger
        touch_score = min(touches / 5, 1.0) * 0.6
        
        # More recent = stronger
        recency_score = min(recency / 10, 1.0) * 0.4
        
        return touch_score + recency_score
    
    def analyze_volume_profile(self, candles: List[Dict], num_bins: int = 20) -> Dict:
        """
        Analyze volume profile to find high-volume nodes (support/resistance)
        
        Args:
            candles: List of candle data
            num_bins: Number of price bins
            
        Returns:
            Dict with volume profile analysis
        """
        if not candles:
            return {"error": "No data"}
        
        # Find price range
        all_highs = [c["high"] for c in candles]
        all_lows = [c["low"] for c in candles]
        
        price_min = min(all_lows)
        price_max = max(all_highs)
        price_range = price_max - price_min
        
        if price_range == 0:
            return {"error": "Zero price range"}
        
        bin_size = price_range / num_bins
        
        # Initialize bins
        bins = []
        for i in range(num_bins):
            bins.append({
                "price_low": price_min + i * bin_size,
                "price_high": price_min + (i + 1) * bin_size,
                "volume": 0,
                "count": 0
            })
        
        # Fill bins
        for candle in candles:
            avg_price = (candle["high"] + candle["low"]) / 2
            bin_idx = int((avg_price - price_min) / bin_size)
            bin_idx = max(0, min(num_bins - 1, bin_idx))
            
            bins[bin_idx]["volume"] += candle["volume"]
            bins[bin_idx]["count"] += 1
        
        # Find high volume nodes (HVN) and low volume nodes (LVN)
        avg_volume = sum(b["volume"] for b in bins) / num_bins
        
        hvn = []
        lvn = []
        
        for i, bin_data in enumerate(bins):
            center_price = (bin_data["price_low"] + bin_data["price_high"]) / 2
            
            if bin_data["volume"] > avg_volume * 1.5:
                hvn.append({
                    "price": round(center_price, 2),
                    "volume": bin_data["volume"],
                    "volume_ratio": round(bin_data["volume"] / avg_volume, 2),
                    "type": "HVN"
                })
            elif bin_data["volume"] < avg_volume * 0.5:
                lvn.append({
                    "price": round(center_price, 2),
                    "volume": bin_data["volume"],
                    "volume_ratio": round(bin_data["volume"] / avg_volume, 2),
                    "type": "LVN"
                })
        
        # Sort by volume
        hvn.sort(key=lambda x: x["volume"], reverse=True)
        lvn.sort(key=lambda x: x["volume"])
        
        return {
            "high_volume_nodes": hvn[:5],  # Top 5 HVNs
            "low_volume_nodes": lvn[:5],   # Top 5 LVNs
            "avg_volume": round(avg_volume, 0),
            "price_range": round(price_range, 2)
        }
    
    def analyze_all_levels(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        Comprehensive support and resistance analysis
        
        Args:
            symbol: Stock symbol
            candles: List of candle data
            
        Returns:
            Dict with all S&R levels
        """
        if not candles or len(candles) < 30:
            return {"error": "Insufficient data (need at least 30 candles)"}
        
        # Extract recent data
        recent_candles = candles[-60:] if len(candles) >= 60 else candles
        latest = candles[-1]
        prev = candles[-2] if len(candles) >= 2 else candles[-1]
        
        result = {
            "symbol": symbol,
            "candle_count": len(candles),
            "analyzed_at": datetime.now().isoformat(),
            "current_price": latest["close"],
            "pivot_points": {},
            "fibonacci_levels": {},
            "price_clusters": [],
            "volume_profile": {},
            "key_levels": [],
            "recommendation": ""
        }
        
        # Calculate pivot points
        result["pivot_points"] = self.calculate_pivot_points(
            prev["high"], prev["low"], prev["close"]
        )
        
        # Calculate Fibonacci levels
        swing_high = max(c["high"] for c in recent_candles)
        swing_low = min(c["low"] for c in recent_candles)
        result["fibonacci_levels"] = self.calculate_fibonacci_retracement(swing_high, swing_low)
        
        # Find price clusters
        result["price_clusters"] = self.find_price_clusters(candles)
        
        # Analyze volume profile
        result["volume_profile"] = self.analyze_volume_profile(recent_candles)
        
        # Combine all levels into key levels
        result["key_levels"] = self._combine_key_levels(result)
        
        # Generate recommendation
        result["recommendation"] = self._generate_sr_recommendation(result)
        
        # Save to cache
        cache_file = self.data_dir / f"{symbol}_sr_levels.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Log analysis
        self._log_analysis(symbol, len(result["key_levels"]), success=True)
        
        return result
    
    def _combine_key_levels(self, result: Dict) -> List[Dict]:
        """Combine all levels into unified key levels list"""
        key_levels = []
        current_price = result["current_price"]
        
        # Add pivot points
        pivots = result.get("pivot_points", {})
        for name, price in pivots.items():
            distance = (price - current_price) / current_price * 100
            level_type = "resistance" if price > current_price else "support"
            
            key_levels.append({
                "price": price,
                "type": level_type,
                "source": "pivot",
                "name": name.replace("_", " ").title(),
                "distance_pct": round(distance, 2),
                "strength": 0.7
            })
        
        # Add price clusters
        clusters = result.get("price_clusters", [])
        for cluster in clusters:
            distance = (cluster["price"] - current_price) / current_price * 100
            
            key_levels.append({
                "price": cluster["price"],
                "type": cluster["type"],
                "source": "cluster",
                "name": f"{cluster['type'].title()} ({cluster['touches']} touches)",
                "distance_pct": round(distance, 2),
                "strength": cluster["strength"]
            })
        
        # Add HVNs from volume profile
        volume_profile = result.get("volume_profile", {})
        hvns = volume_profile.get("high_volume_nodes", [])
        for hvn in hvns[:3]:
            distance = (hvn["price"] - current_price) / current_price * 100
            
            key_levels.append({
                "price": hvn["price"],
                "type": "support/resistance",
                "source": "volume",
                "name": f"HVN (vol ratio {hvn['volume_ratio']})",
                "distance_pct": round(distance, 2),
                "strength": 0.6 * hvn["volume_ratio"] / 2
            })
        
        # Sort by strength and remove duplicates (within 1%)
        key_levels.sort(key=lambda x: x["strength"], reverse=True)
        
        filtered = []
        for level in key_levels:
            is_duplicate = False
            for existing in filtered:
                if abs(level["price"] - existing["price"]) / existing["price"] < 0.01:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(level)
        
        return filtered[:10]  # Top 10 key levels
    
    def _generate_sr_recommendation(self, result: Dict) -> str:
        """Generate recommendation based on S&R levels"""
        current_price = result["current_price"]
        key_levels = result.get("key_levels", [])
        
        if not key_levels:
            return "NEUTRAL - No clear S&R levels identified"
        
        # Find nearest support and resistance
        supports = [l for l in key_levels if l["type"] in ["support", "support/resistance"] and l["price"] < current_price]
        resistances = [l for l in key_levels if l["type"] in ["resistance", "support/resistance"] and l["price"] > current_price]
        
        if not supports or not resistances:
            return "NEUTRAL - Insufficient S&R data"
        
        nearest_support = max(supports, key=lambda x: x["price"])
        nearest_resistance = min(resistances, key=lambda x: x["price"])
        
        support_distance = (current_price - nearest_support["price"]) / current_price * 100
        resistance_distance = (nearest_resistance["price"] - current_price) / current_price * 100
        
        if support_distance < 3:
            return f"SUPPORT TEST - Price near support at {nearest_support['price']} ({support_distance:.1f}% above)"
        elif resistance_distance < 3:
            return f"RESISTANCE TEST - Price near resistance at {nearest_resistance['price']} ({resistance_distance:.1f}% below)"
        elif support_distance < resistance_distance:
            return f"BIASED BULLISH - Closer to support ({support_distance:.1f}%) than resistance ({resistance_distance:.1f}%)"
        else:
            return f"BIASED BEARISH - Closer to resistance ({resistance_distance:.1f}%) than support ({support_distance:.1f}%)"
    
    def _log_analysis(self, symbol: str, levels: int, success: bool):
        """Log analysis attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "levels_detected": levels,
            "success": success
        }
        
        self.analysis_log["analyses"].append(log_entry)
        self.analysis_log["stats"]["total_analyses"] += 1
        self.analysis_log["stats"]["levels_detected"] += levels
        
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
        output.append(" " * 14 + "Support & Resistance Analyzer Status")
        output.append("=" * 70)
        
        output.append(f"\n[Analysis Methods]")
        output.append("  - Classic Pivot Points")
        output.append("  - Fibonacci Retracement")
        output.append("  - Price Cluster Detection")
        output.append("  - Volume Profile Analysis")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Analyses:    {stats['total_analyses']}")
        output.append(f"  Levels Detected:   {stats['levels_detected']}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 14 + "SA-008: Support & Resistance")
    print("=" * 70)
    
    analyzer = SupportResistanceAnalyzer()
    
    # Test 1: Display status
    print(analyzer.display_status())
    
    # Test 2: Generate test data
    print("\n[Test 1] Generate Test Data")
    print("-" * 70)
    import random
    random.seed(42)
    
    candles = []
    price = 100
    
    # Create price action with clear S&R levels
    for i in range(100):
        # Create range-bound action with occasional breakouts
        if i < 30:
            price = 100 + random.uniform(-5, 5)  # Range 95-105
        elif i < 60:
            price = 115 + random.uniform(-3, 3)  # Range 112-118
        else:
            price = 130 + random.uniform(-8, 8)  # Range 122-138
        
        open_p = price
        close_p = price * (1 + random.uniform(-0.01, 0.01))
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.02))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.02))
        volume = random.randint(5000000, 50000000)
        
        candles.append({
            "date": f"2026-01-{i%30+1:02d}",
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume
        })
    
    print(f"  Generated {len(candles)} candles")
    print(f"  Price range: {min(c['low'] for c in candles):.2f} - {max(c['high'] for c in candles):.2f}")
    
    # Test 3: Analyze S&R levels
    print("\n[Test 2] Analyze Support & Resistance")
    print("-" * 70)
    result = analyzer.analyze_all_levels("TEST", candles)
    
    if "error" not in result:
        print(f"  Symbol:        {result['symbol']}")
        print(f"  Current Price: {result['current_price']}")
        
        print(f"\n  Pivot Points:")
        for name, price in result["pivot_points"].items():
            print(f"    {name.replace('_', ' ').title():15} {price}")
        
        print(f"\n  Key Levels:")
        for i, level in enumerate(result["key_levels"][:8], 1):
            print(f"    [{i}] {level['price']:7.2f} - {level['type']:15} "
                  f"({level['source']:6}) - {level['name']} "
                  f"[Strength: {level['strength']:.2f}, Dist: {level['distance_pct']:+.2f}%]")
        
        print(f"\n  Recommendation: {result['recommendation']}")
    
    # Test 4: Final stats
    print("\n[Test 3] Final Statistics")
    print("-" * 70)
    stats = analyzer.get_stats()
    print(f"  Total Analyses:    {stats['total_analyses']}")
    print(f"  Levels Detected:   {stats['levels_detected']}")
    
    print("\n[OK] SA-008 Support & Resistance test completed")

if __name__ == "__main__":
    main()
