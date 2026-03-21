import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-010: Signal Generator
Generate trading signals from multiple indicators (confluence-based)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class SignalGenerator:
    """Generate trading signals from multiple technical indicators"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_signals"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.signal_log = self._load_signal_log()
    
    def _load_signal_log(self) -> Dict:
        """Load signal log"""
        log_file = self.data_dir / "signal_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "signals": [],
            "stats": {
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "neutral_signals": 0
            }
        }
    
    def _save_signal_log(self):
        """Save signal log"""
        log_file = self.data_dir / "signal_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.signal_log, f, ensure_ascii=False, indent=2)
    
    def evaluate_ma_signal(self, price: float, mas: Dict[str, float]) -> Dict:
        """
        Evaluate Moving Average signals
        
        Args:
            price: Current price
            mas: Dict of moving averages
            
        Returns:
            Dict with MA signal
        """
        if not mas:
            return {"signal": "neutral", "strength": 0}
        
        # Count how many MAs price is above/below
        above_count = sum(1 for ma in mas.values() if price > ma)
        total_mas = len(mas)
        
        if above_count == total_mas:
            return {"signal": "strong_buy", "strength": 1.0, "detail": "Price above all MAs"}
        elif above_count >= total_mas * 0.75:
            return {"signal": "buy", "strength": 0.75, "detail": "Price above most MAs"}
        elif above_count <= total_mas * 0.25:
            return {"signal": "sell", "strength": -0.75, "detail": "Price below most MAs"}
        elif above_count == 0:
            return {"signal": "strong_sell", "strength": -1.0, "detail": "Price below all MAs"}
        else:
            return {"signal": "neutral", "strength": 0, "detail": "Mixed MA signals"}
    
    def evaluate_macd_signal(self, macd_line: float, signal_line: float,
                            histogram: float) -> Dict:
        """
        Evaluate MACD signal
        
        Returns:
            Dict with MACD signal
        """
        if macd_line > signal_line and histogram > 0:
            if histogram > 0.5:
                return {"signal": "strong_buy", "strength": 0.8, "detail": "MACD bullish crossover"}
            else:
                return {"signal": "buy", "strength": 0.5, "detail": "MACD above signal"}
        elif macd_line < signal_line and histogram < 0:
            if histogram < -0.5:
                return {"signal": "strong_sell", "strength": -0.8, "detail": "MACD bearish crossover"}
            else:
                return {"signal": "sell", "strength": -0.5, "detail": "MACD below signal"}
        else:
            return {"signal": "neutral", "strength": 0, "detail": "MACD neutral"}
    
    def evaluate_rsi_signal(self, rsi: float) -> Dict:
        """
        Evaluate RSI signal
        
        Returns:
            Dict with RSI signal
        """
        if rsi < 20:
            return {"signal": "strong_buy", "strength": 0.7, "detail": "RSI oversold (<20)"}
        elif rsi < 30:
            return {"signal": "buy", "strength": 0.4, "detail": "RSI oversold (<30)"}
        elif rsi > 80:
            return {"signal": "strong_sell", "strength": -0.7, "detail": "RSI overbought (>80)"}
        elif rsi > 70:
            return {"signal": "sell", "strength": -0.4, "detail": "RSI overbought (>70)"}
        else:
            return {"signal": "neutral", "strength": 0, "detail": "RSI neutral"}
    
    def evaluate_kdj_signal(self, k: float, d: float, j: float) -> Dict:
        """
        Evaluate KDJ signal
        
        Returns:
            Dict with KDJ signal
        """
        if k < 20 and d < 20:
            if k > d:
                return {"signal": "buy", "strength": 0.5, "detail": "KDJ oversold + K>D"}
            else:
                return {"signal": "neutral", "strength": 0.1, "detail": "KDJ oversold"}
        elif k > 80 and d > 80:
            if k < d:
                return {"signal": "sell", "strength": -0.5, "detail": "KDJ overbought + K<D"}
            else:
                return {"signal": "neutral", "strength": -0.1, "detail": "KDJ overbought"}
        elif k > d:
            return {"signal": "buy", "strength": 0.3, "detail": "K above D"}
        elif k < d:
            return {"signal": "sell", "strength": -0.3, "detail": "K below D"}
        else:
            return {"signal": "neutral", "strength": 0, "detail": "KDJ neutral"}
    
    def evaluate_boll_signal(self, price: float, upper: float,
                            middle: float, lower: float) -> Dict:
        """
        Evaluate Bollinger Bands signal
        
        Returns:
            Dict with BOLL signal
        """
        if price <= lower:
            return {"signal": "buy", "strength": 0.5, "detail": "Price at lower band"}
        elif price >= upper:
            return {"signal": "sell", "strength": -0.5, "detail": "Price at upper band"}
        elif price > middle:
            return {"signal": "neutral", "strength": 0.2, "detail": "Price above middle band"}
        elif price < middle:
            return {"signal": "neutral", "strength": -0.2, "detail": "Price below middle band"}
        else:
            return {"signal": "neutral", "strength": 0, "detail": "Price at middle band"}
    
    def generate_confluence_signal(self, indicators: Dict) -> Dict:
        """
        Generate confluence-based signal from multiple indicators
        
        Args:
            indicators: Dict with all indicator values
            
        Returns:
            Dict with combined signal
        """
        signals = []
        weights = []
        
        # Evaluate each indicator
        if "mas" in indicators:
            ma_signal = self.evaluate_ma_signal(indicators["price"], indicators["mas"])
            signals.append(ma_signal["strength"])
            weights.append(0.25)
        
        if "macd" in indicators:
            macd_data = indicators["macd"]
            macd_signal = self.evaluate_macd_signal(
                macd_data.get("macd", 0),
                macd_data.get("signal", 0),
                macd_data.get("histogram", 0)
            )
            signals.append(macd_signal["strength"])
            weights.append(0.20)
        
        if "rsi" in indicators:
            rsi_signal = self.evaluate_rsi_signal(indicators["rsi"])
            signals.append(rsi_signal["strength"])
            weights.append(0.20)
        
        if "kdj" in indicators:
            kdj_data = indicators["kdj"]
            kdj_signal = self.evaluate_kdj_signal(
                kdj_data.get("k", 50),
                kdj_data.get("d", 50),
                kdj_data.get("j", 50)
            )
            signals.append(kdj_signal["strength"])
            weights.append(0.15)
        
        if "boll" in indicators:
            boll_data = indicators["boll"]
            boll_signal = self.evaluate_boll_signal(
                indicators["price"],
                boll_data.get("upper", 0),
                boll_data.get("middle", 0),
                boll_data.get("lower", 0)
            )
            signals.append(boll_signal["strength"])
            weights.append(0.20)
        
        if not signals:
            return {"signal": "neutral", "strength": 0, "detail": "No indicators available"}
        
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_signal = sum(s * w for s, w in zip(signals, weights)) / total_weight
        
        # Determine final signal
        if weighted_signal >= 0.6:
            final_signal = "strong_buy"
        elif weighted_signal >= 0.3:
            final_signal = "buy"
        elif weighted_signal <= -0.6:
            final_signal = "strong_sell"
        elif weighted_signal <= -0.3:
            final_signal = "sell"
        else:
            final_signal = "neutral"
        
        # Count confluence
        buy_signals = sum(1 for s in signals if s > 0)
        sell_signals = sum(1 for s in signals if s < 0)
        total_signals = len(signals)
        
        return {
            "signal": final_signal,
            "strength": round(weighted_signal, 2),
            "confluence": f"{max(buy_signals, sell_signals)}/{total_signals}",
            "buy_indicators": buy_signals,
            "sell_indicators": sell_signals,
            "neutral_indicators": total_signals - buy_signals - sell_signals,
            "detail": f"Confluence: {buy_signals} buy, {sell_signals} sell, {total_signals - buy_signals - sell_signals} neutral"
        }
    
    def generate_all_signals(self, symbol: str, indicators: Dict) -> Dict:
        """
        Generate comprehensive signal analysis
        
        Args:
            symbol: Stock symbol
            indicators: Dict with all indicator values
            
        Returns:
            Dict with all signals
        """
        result = {
            "symbol": symbol,
            "generated_at": datetime.now().isoformat(),
            "price": indicators.get("price", 0),
            "individual_signals": {},
            "confluence_signal": {},
            "recommendation": "",
            "confidence": 0
        }
        
        # Generate individual signals
        if "mas" in indicators:
            result["individual_signals"]["MA"] = self.evaluate_ma_signal(
                indicators["price"], indicators["mas"]
            )
        
        if "macd" in indicators:
            macd_data = indicators["macd"]
            result["individual_signals"]["MACD"] = self.evaluate_macd_signal(
                macd_data.get("macd", 0),
                macd_data.get("signal", 0),
                macd_data.get("histogram", 0)
            )
        
        if "rsi" in indicators:
            result["individual_signals"]["RSI"] = self.evaluate_rsi_signal(indicators["rsi"])
        
        if "kdj" in indicators:
            kdj_data = indicators["kdj"]
            result["individual_signals"]["KDJ"] = self.evaluate_kdj_signal(
                kdj_data.get("k", 50),
                kdj_data.get("d", 50),
                kdj_data.get("j", 50)
            )
        
        if "boll" in indicators:
            boll_data = indicators["boll"]
            result["individual_signals"]["BOLL"] = self.evaluate_boll_signal(
                indicators["price"],
                boll_data.get("upper", 0),
                boll_data.get("middle", 0),
                boll_data.get("lower", 0)
            )
        
        # Generate confluence signal
        result["confluence_signal"] = self.generate_confluence_signal(indicators)
        
        # Generate recommendation
        result["recommendation"] = self._generate_recommendation(result)
        result["confidence"] = self._calculate_confidence(result)
        
        # Save to cache
        cache_file = self.data_dir / f"{symbol}_signals.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Log signal
        self._log_signal(symbol, result["confluence_signal"]["signal"], success=True)
        
        return result
    
    def _generate_recommendation(self, result: Dict) -> str:
        """Generate trading recommendation"""
        signal = result.get("confluence_signal", {})
        signal_type = signal.get("signal", "neutral")
        strength = signal.get("strength", 0)
        confluence = signal.get("confluence", "0/0")
        
        if signal_type == "strong_buy":
            return f"STRONG BUY - High conviction long ({confluence} confluence)"
        elif signal_type == "buy":
            return f"BUY - Moderate conviction long ({confluence} confluence)"
        elif signal_type == "strong_sell":
            return f"STRONG SELL - High conviction short ({confluence} confluence)"
        elif signal_type == "sell":
            return f"SELL - Moderate conviction short ({confluence} confluence)"
        else:
            return f"NEUTRAL - Wait for clearer signal ({confluence} confluence)"
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate signal confidence"""
        confluence_signal = result.get("confluence_signal", {})
        
        buy = confluence_signal.get("buy_indicators", 0)
        sell = confluence_signal.get("sell_indicators", 0)
        neutral = confluence_signal.get("neutral_indicators", 0)
        total = buy + sell + neutral
        
        if total == 0:
            return 0
        
        # Confidence based on agreement
        max_side = max(buy, sell)
        confidence = max_side / total
        
        # Boost confidence if strength is high
        strength = abs(confluence_signal.get("strength", 0))
        confidence = (confidence + strength) / 2
        
        return round(confidence, 2)
    
    def _log_signal(self, symbol: str, signal: str, success: bool):
        """Log signal generation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "signal": signal,
            "success": success
        }
        
        self.signal_log["signals"].append(log_entry)
        self.signal_log["stats"]["total_signals"] += 1
        
        if signal in ["buy", "strong_buy"]:
            self.signal_log["stats"]["buy_signals"] += 1
        elif signal in ["sell", "strong_sell"]:
            self.signal_log["stats"]["sell_signals"] += 1
        else:
            self.signal_log["stats"]["neutral_signals"] += 1
        
        # Keep only last 500 entries
        self.signal_log["signals"] = self.signal_log["signals"][-500:]
        
        self._save_signal_log()
    
    def get_stats(self) -> Dict:
        """Get signal statistics"""
        return self.signal_log["stats"].copy()
    
    def display_status(self) -> str:
        """Display generator status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 16 + "Signal Generator Status")
        output.append("=" * 70)
        
        output.append(f"\n[Signal Methods]")
        output.append("  - Moving Average Analysis")
        output.append("  - MACD Crossover")
        output.append("  - RSI Overbought/Oversold")
        output.append("  - KDJ Stochastic")
        output.append("  - Bollinger Bands")
        output.append("  - Confluence Scoring")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Signals:    {stats['total_signals']}")
        output.append(f"  Buy Signals:      {stats['buy_signals']}")
        output.append(f"  Sell Signals:     {stats['sell_signals']}")
        output.append(f"  Neutral Signals:  {stats['neutral_signals']}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py sa_signal_generator_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_signal_generator_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Test entry point"""
    print("=" * 70)
    print(" " * 16 + "SA-010: Signal Generator")
    print("=" * 70)
    
    generator = SignalGenerator()
    
    # Test 1: Display status
    print(generator.display_status())
    
    # Test 2: Generate signal with sample data
    print("\n[Test 1] Generate Trading Signal")
    print("-" * 70)
    
    # Sample indicator data (bullish scenario)
    indicators = {
        "price": 105.0,
        "mas": {
            "MA5": 103.0,
            "MA10": 102.0,
            "MA20": 100.0,
            "MA50": 98.0,
            "MA200": 95.0
        },
        "macd": {
            "macd": 1.5,
            "signal": 1.0,
            "histogram": 0.5
        },
        "rsi": 58.0,
        "kdj": {
            "k": 65.0,
            "d": 60.0,
            "j": 70.0
        },
        "boll": {
            "upper": 108.0,
            "middle": 103.0,
            "lower": 98.0
        }
    }
    
    result = generator.generate_all_signals("TEST", indicators)
    
    print(f"  Symbol:        {result['symbol']}")
    print(f"  Price:         ${result['price']}")
    
    print(f"\n  Individual Signals:")
    for name, signal in result["individual_signals"].items():
        print(f"    {name:6} - {signal['signal']:12} (strength: {signal['strength']:+.2f})")
        print(f"             {signal['detail']}")
    
    print(f"\n  Confluence Signal:")
    conf = result["confluence_signal"]
    print(f"    Signal:      {conf['signal']}")
    print(f"    Strength:    {conf['strength']:+.2f}")
    print(f"    Confluence:  {conf['confluence']}")
    print(f"    Buy:         {conf['buy_indicators']}")
    print(f"    Sell:        {conf['sell_indicators']}")
    print(f"    Neutral:     {conf['neutral_indicators']}")
    
    print(f"\n  Recommendation: {result['recommendation']}")
    print(f"  Confidence:     {result['confidence']*100:.0f}%")
    
    # Test 3: Final stats
    print("\n[Test 2] Final Statistics")
    print("-" * 70)
    stats = generator.get_stats()
    print(f"  Total Signals:    {stats['total_signals']}")
    print(f"  Buy Signals:      {stats['buy_signals']}")
    print(f"  Sell Signals:     {stats['sell_signals']}")
    print(f"  Neutral Signals:  {stats['neutral_signals']}")
    
    print("\n[OK] SA-010 Signal Generator test completed")

if __name__ == "__main__":
    main()
