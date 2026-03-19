#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-006: Pattern Recognition
Automatic K-line pattern recognition (Head & Shoulders, Double Top/Bottom, Triangles, etc.)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class PatternRecognizer:
    """Recognize candlestick patterns from price data"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_patterns"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.pattern_types = [
            "head_shoulders", "double_top", "double_bottom",
            "triangle", "flag", "wedge", "cup_handle"
        ]
        
        self.recognition_log = self._load_recognition_log()
    
    def _load_recognition_log(self) -> Dict:
        """Load recognition log"""
        log_file = self.data_dir / "recognition_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "recognitions": [],
            "stats": {
                "total_recognitions": 0,
                "patterns_found": 0,
            }
        }
    
    def _save_recognition_log(self):
        """Save recognition log"""
        log_file = self.data_dir / "recognition_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.recognition_log, f, ensure_ascii=False, indent=2)
    
    def detect_head_shoulders(self, highs: List[float], lows: List[float], 
                             closes: List[float]) -> Optional[Dict]:
        """
        Detect Head and Shoulders pattern
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            
        Returns:
            Dict with pattern details or None if not found
        """
        if len(highs) < 50:
            return None
        
        # Find three peaks (left shoulder, head, right shoulder)
        peaks = self._find_peaks(highs, window=10)
        
        if len(peaks) < 3:
            return None
        
        # Look for head and shoulders configuration
        for i in range(len(peaks) - 2):
            left_shoulder = peaks[i]
            head = peaks[i + 1]
            right_shoulder = peaks[i + 2]
            
            # Head should be highest
            if highs[head] > highs[left_shoulder] and highs[head] > highs[right_shoulder]:
                # Shoulders should be roughly equal (within 5%)
                shoulder_diff = abs(highs[left_shoulder] - highs[right_shoulder]) / highs[left_shoulder]
                
                if shoulder_diff < 0.05:
                    # Find neckline (trough between peaks)
                    left_trough = self._find_trough(lows, left_shoulder, head)
                    right_trough = self._find_trough(lows, head, right_shoulder)
                    
                    if left_trough and right_trough:
                        neckline = (lows[left_trough] + lows[right_trough]) / 2
                        
                        # Calculate confidence
                        confidence = self._calculate_hs_confidence(
                            highs[left_shoulder], highs[head], highs[right_shoulder],
                            lows[left_trough], lows[right_trough]
                        )
                        
                        if confidence > 0.6:
                            return {
                                "pattern": "head_shoulders",
                                "type": "reversal",
                                "direction": "bearish",
                                "left_shoulder": {"index": left_shoulder, "price": highs[left_shoulder]},
                                "head": {"index": head, "price": highs[head]},
                                "right_shoulder": {"index": right_shoulder, "price": highs[right_shoulder]},
                                "neckline": round(neckline, 2),
                                "confidence": round(confidence, 2),
                                "target": round(neckline - (highs[head] - neckline), 2),
                                "detected_at": datetime.now().isoformat()
                            }
        
        return None
    
    def detect_double_top(self, highs: List[float], lows: List[float]) -> Optional[Dict]:
        """
        Detect Double Top pattern
        
        Returns:
            Dict with pattern details or None if not found
        """
        if len(highs) < 40:
            return None
        
        peaks = self._find_peaks(highs, window=8)
        
        if len(peaks) < 2:
            return None
        
        for i in range(len(peaks) - 1):
            peak1 = peaks[i]
            peak2 = peaks[i + 1]
            
            # Peaks should be roughly equal (within 3%)
            peak_diff = abs(highs[peak1] - highs[peak2]) / highs[peak1]
            
            if peak_diff < 0.03:
                # Find trough between peaks
                trough = self._find_trough(lows, peak1, peak2)
                
                if trough:
                    neckline = lows[trough]
                    confidence = self._calculate_double_top_confidence(
                        highs[peak1], highs[peak2], lows[trough]
                    )
                    
                    if confidence > 0.6:
                        return {
                            "pattern": "double_top",
                            "type": "reversal",
                            "direction": "bearish",
                            "peak1": {"index": peak1, "price": highs[peak1]},
                            "peak2": {"index": peak2, "price": highs[peak2]},
                            "neckline": round(neckline, 2),
                            "confidence": round(confidence, 2),
                            "target": round(neckline - (highs[peak1] - neckline), 2),
                            "detected_at": datetime.now().isoformat()
                        }
        
        return None
    
    def detect_double_bottom(self, lows: List[float], highs: List[float]) -> Optional[Dict]:
        """
        Detect Double Bottom pattern
        
        Returns:
            Dict with pattern details or None if not found
        """
        if len(lows) < 40:
            return None
        
        troughs = self._find_troughs(lows, window=8)
        
        if len(troughs) < 2:
            return None
        
        for i in range(len(troughs) - 1):
            trough1 = troughs[i]
            trough2 = troughs[i + 1]
            
            # Troughs should be roughly equal (within 3%)
            trough_diff = abs(lows[trough1] - lows[trough2]) / lows[trough1]
            
            if trough_diff < 0.03:
                # Find peak between troughs
                peak = self._find_peak_between(highs, trough1, trough2)
                
                if peak:
                    neckline = highs[peak]
                    confidence = self._calculate_double_bottom_confidence(
                        lows[trough1], lows[trough2], highs[peak]
                    )
                    
                    if confidence > 0.6:
                        return {
                            "pattern": "double_bottom",
                            "type": "reversal",
                            "direction": "bullish",
                            "trough1": {"index": trough1, "price": lows[trough1]},
                            "trough2": {"index": trough2, "price": lows[trough2]},
                            "neckline": round(neckline, 2),
                            "confidence": round(confidence, 2),
                            "target": round(neckline + (neckline - lows[trough1]), 2),
                            "detected_at": datetime.now().isoformat()
                        }
        
        return None
    
    def detect_triangle(self, highs: List[float], lows: List[float], 
                       closes: List[float]) -> Optional[Dict]:
        """
        Detect Triangle pattern (ascending, descending, or symmetrical)
        
        Returns:
            Dict with pattern details or None if not found
        """
        if len(highs) < 30:
            return None
        
        # Find recent highs and lows (last 20-30 candles)
        window = min(30, len(highs))
        recent_highs = highs[-window:]
        recent_lows = lows[-window:]
        
        # Calculate trendlines
        high_trend = self._calculate_trend(recent_highs)
        low_trend = self._calculate_trend(recent_lows)
        
        # Determine triangle type
        if high_trend < -0.001 and abs(low_trend) < 0.001:
            triangle_type = "descending"
            direction = "bearish"
        elif low_trend > 0.001 and abs(high_trend) < 0.001:
            triangle_type = "ascending"
            direction = "bullish"
        elif high_trend < -0.001 and low_trend > 0.001:
            triangle_type = "symmetrical"
            direction = "neutral"
        else:
            return None
        
        # Calculate confidence based on how well prices fit the trendlines
        confidence = self._calculate_triangle_confidence(recent_highs, recent_lows, high_trend, low_trend)
        
        if confidence > 0.5:
            return {
                "pattern": "triangle",
                "triangle_type": triangle_type,
                "type": "continuation",
                "direction": direction,
                "high_trend": round(high_trend, 4),
                "low_trend": round(low_trend, 4),
                "confidence": round(confidence, 2),
                "breakout_level": round(recent_highs[0] if triangle_type == "ascending" else recent_lows[0], 2),
                "detected_at": datetime.now().isoformat()
            }
        
        return None
    
    def detect_flag(self, highs: List[float], lows: List[float], 
                   closes: List[float]) -> Optional[Dict]:
        """
        Detect Flag pattern (bullish or bearish flag)
        
        Returns:
            Dict with pattern details or None if not found
        """
        if len(closes) < 40:
            return None
        
        # Look for strong move (flagpole) followed by consolidation
        window = 20
        recent_closes = closes[-window:]
        
        # Calculate price change in first half (flagpole)
        first_half_change = (recent_closes[window//2] - recent_closes[0]) / recent_closes[0]
        
        # Calculate consolidation in second half (flag)
        second_half_volatility = self._calculate_volatility(recent_closes[window//2:])
        
        # Bullish flag: strong up move + low volatility consolidation
        if first_half_change > 0.05 and second_half_volatility < 0.02:
            return {
                "pattern": "flag",
                "flag_type": "bullish",
                "type": "continuation",
                "direction": "bullish",
                "flagpole_change": round(first_half_change * 100, 2),
                "consolidation_volatility": round(second_half_volatility * 100, 2),
                "confidence": round(min(0.9, 0.5 + first_half_change * 5), 2),
                "target": round(recent_closes[-1] * (1 + first_half_change), 2),
                "detected_at": datetime.now().isoformat()
            }
        
        # Bearish flag: strong down move + low volatility consolidation
        elif first_half_change < -0.05 and second_half_volatility < 0.02:
            return {
                "pattern": "flag",
                "flag_type": "bearish",
                "type": "continuation",
                "direction": "bearish",
                "flagpole_change": round(first_half_change * 100, 2),
                "consolidation_volatility": round(second_half_volatility * 100, 2),
                "confidence": round(min(0.9, 0.5 + abs(first_half_change) * 5), 2),
                "target": round(recent_closes[-1] * (1 + first_half_change), 2),
                "detected_at": datetime.now().isoformat()
            }
        
        return None
    
    def scan_all_patterns(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        Scan for all patterns in price data
        
        Args:
            symbol: Stock symbol
            candles: List of candle data
            
        Returns:
            Dict with all detected patterns
        """
        if not candles or len(candles) < 30:
            return {"error": "Insufficient data (need at least 30 candles)"}
        
        # Extract price arrays
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]
        
        result = {
            "symbol": symbol,
            "candle_count": len(candles),
            "scanned_at": datetime.now().isoformat(),
            "patterns_found": []
        }
        
        # Detect each pattern type
        detectors = [
            ("head_shoulders", lambda: self.detect_head_shoulders(highs, lows, closes)),
            ("double_top", lambda: self.detect_double_top(highs, lows)),
            ("double_bottom", lambda: self.detect_double_bottom(lows, highs)),
            ("triangle", lambda: self.detect_triangle(highs, lows, closes)),
            ("flag", lambda: self.detect_flag(highs, lows, closes))
        ]
        
        for pattern_name, detector in detectors:
            try:
                pattern = detector()
                if pattern:
                    result["patterns_found"].append(pattern)
            except Exception as e:
                print(f"[WARN] Error detecting {pattern_name}: {e}")
        
        # Save to cache
        cache_file = self.data_dir / f"{symbol}_patterns.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Log recognition
        self._log_recognition(symbol, len(result["patterns_found"]), success=True)
        
        return result
    
    # Helper methods
    def _find_peaks(self, prices: List[float], window: int = 10) -> List[int]:
        """Find peak indices in price series"""
        peaks = []
        for i in range(window, len(prices) - window):
            is_peak = True
            for j in range(i - window, i + window + 1):
                if j != i and prices[j] >= prices[i]:
                    is_peak = False
                    break
            if is_peak:
                peaks.append(i)
        return peaks
    
    def _find_troughs(self, prices: List[float], window: int = 10) -> List[int]:
        """Find trough indices in price series"""
        troughs = []
        for i in range(window, len(prices) - window):
            is_trough = True
            for j in range(i - window, i + window + 1):
                if j != i and prices[j] <= prices[i]:
                    is_trough = False
                    break
            if is_trough:
                troughs.append(i)
        return troughs
    
    def _find_trough(self, prices: List[float], start: int, end: int) -> Optional[int]:
        """Find lowest point between two indices"""
        if start >= end or end >= len(prices):
            return None
        trough_idx = start
        for i in range(start, end + 1):
            if prices[i] < prices[trough_idx]:
                trough_idx = i
        return trough_idx
    
    def _find_peak_between(self, prices: List[float], start: int, end: int) -> Optional[int]:
        """Find highest point between two indices"""
        if start >= end or end >= len(prices):
            return None
        peak_idx = start
        for i in range(start, end + 1):
            if prices[i] > prices[peak_idx]:
                peak_idx = i
        return peak_idx
    
    def _calculate_trend(self, prices: List[float]) -> float:
        """Calculate linear trend (slope) of prices"""
        if len(prices) < 2:
            return 0
        
        n = len(prices)
        sum_x = sum(range(n))
        sum_y = sum(prices)
        sum_xy = sum(i * prices[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope / prices[0] if prices[0] != 0 else 0
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility (standard deviation / mean)"""
        if len(prices) < 2:
            return 0
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std = math.sqrt(variance)
        
        return std / mean if mean != 0 else 0
    
    def _calculate_hs_confidence(self, ls: float, head: float, rs: float, 
                                lt: float, rt: float) -> float:
        """Calculate head and shoulders pattern confidence"""
        # Shoulder symmetry
        shoulder_sym = 1 - abs(ls - rs) / ls
        
        # Head prominence
        head_prom = (head - max(ls, rs)) / ls
        
        # Neckline flatness
        neckline_flat = 1 - abs(lt - rt) / lt
        
        confidence = (shoulder_sym * 0.4 + min(head_prom, 0.3) * 0.4 + neckline_flat * 0.2)
        return min(confidence, 1.0)
    
    def _calculate_double_top_confidence(self, peak1: float, peak2: float, 
                                        trough: float) -> float:
        """Calculate double top pattern confidence"""
        peak_sym = 1 - abs(peak1 - peak2) / peak1
        depth = (peak1 - trough) / peak1
        
        return min((peak_sym * 0.6 + depth * 0.4), 1.0)
    
    def _calculate_double_bottom_confidence(self, trough1: float, trough2: float, 
                                           peak: float) -> float:
        """Calculate double bottom pattern confidence"""
        trough_sym = 1 - abs(trough1 - trough2) / trough1
        depth = (peak - trough1) / trough1
        
        return min((trough_sym * 0.6 + depth * 0.4), 1.0)
    
    def _calculate_triangle_confidence(self, highs: List[float], lows: List[float],
                                      high_trend: float, low_trend: float) -> float:
        """Calculate triangle pattern confidence"""
        # Check convergence
        price_range = highs[0] - lows[0]
        convergence = 1 - (highs[-1] - lows[-1]) / price_range if price_range > 0 else 0
        
        # Check trendline fit
        high_fit = 1 - abs(high_trend) * 10
        low_fit = 1 - abs(low_trend) * 10
        
        return min((convergence * 0.5 + max(high_fit, 0) * 0.25 + max(low_fit, 0) * 0.25), 1.0)
    
    def _log_recognition(self, symbol: str, patterns: int, success: bool):
        """Log recognition attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "patterns_found": patterns,
            "success": success
        }
        
        self.recognition_log["recognitions"].append(log_entry)
        self.recognition_log["stats"]["total_recognitions"] += 1
        self.recognition_log["stats"]["patterns_found"] += patterns
        
        # Keep only last 500 entries
        self.recognition_log["recognitions"] = self.recognition_log["recognitions"][-500:]
        
        self._save_recognition_log()
    
    def get_stats(self) -> Dict:
        """Get recognition statistics"""
        return self.recognition_log["stats"].copy()
    
    def display_status(self) -> str:
        """Display recognizer status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 16 + "Pattern Recognizer Status")
        output.append("=" * 70)
        
        output.append(f"\n[Pattern Types]")
        for pt in self.pattern_types:
            output.append(f"  - {pt.replace('_', ' ').title()}")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Recognitions: {stats['total_recognitions']}")
        output.append(f"  Patterns Found:     {stats['patterns_found']}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 14 + "SA-006: Pattern Recognition")
    print("=" * 70)
    
    recognizer = PatternRecognizer()
    
    # Test 1: Display status
    print(recognizer.display_status())
    
    # Test 2: Generate test data with patterns
    print("\n[Test 1] Generate Test Data")
    print("-" * 70)
    import random
    random.seed(42)
    
    candles = []
    price = 100
    
    # Create head and shoulders pattern
    for i in range(100):
        if i < 20:  # Left shoulder
            price *= (1 + random.uniform(-0.01, 0.02))
        elif i < 40:  # Head
            price *= (1 + random.uniform(0.01, 0.03))
        elif i < 60:  # Right shoulder
            price *= (1 + random.uniform(-0.02, 0.01))
        else:  # Random walk
            price *= (1 + random.uniform(-0.02, 0.02))
        
        open_p = price
        close_p = price * (1 + random.uniform(-0.01, 0.01))
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.015))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.015))
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
    
    # Test 3: Scan for patterns
    print("\n[Test 2] Scan for Patterns")
    print("-" * 70)
    result = recognizer.scan_all_patterns("TEST", candles)
    
    if "error" not in result:
        print(f"  Symbol:       {result['symbol']}")
        print(f"  Candles:      {result['candle_count']}")
        print(f"  Patterns:     {len(result['patterns_found'])}")
        
        if result["patterns_found"]:
            print(f"\n  Detected Patterns:")
            for i, pattern in enumerate(result["patterns_found"], 1):
                print(f"\n  [{i}] {pattern['pattern'].replace('_', ' ').title()}")
                print(f"      Type:       {pattern['type']}")
                print(f"      Direction:  {pattern['direction']}")
                print(f"      Confidence: {pattern['confidence']*100:.0f}%")
                if "target" in pattern:
                    print(f"      Target:     {pattern['target']}")
        else:
            print("  No patterns detected")
    
    # Test 4: Final stats
    print("\n[Test 3] Final Statistics")
    print("-" * 70)
    stats = recognizer.get_stats()
    print(f"  Total Recognitions: {stats['total_recognitions']}")
    print(f"  Patterns Found:     {stats['patterns_found']}")
    
    print("\n[OK] SA-006 Pattern Recognition test completed")

if __name__ == "__main__":
    main()
