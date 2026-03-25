#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-005: Technical Indicator Calculator
Calculate common technical indicators (MA, MACD, RSI, KDJ, BOLL, ATR, etc.)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import math

class TechnicalIndicatorCalculator:
    """Calculate technical indicators from price data"""

    def __init__(self, data_dir: str = "60-DATA/stock_indicators"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.supported_indicators = [
            "MA", "EMA", "MACD", "RSI", "KDJ", "BOLL", "ATR",
            "CCI", "WR", "ROC", "OBV"
        ]

        self.calculation_log = self._load_calculation_log()

    def _load_calculation_log(self) -> Dict:
        """Load calculation log"""
        log_file = self.data_dir / "calculation_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "calculations": [],
            "stats": {
                "total_calculations": 0,
                "successful": 0,
                "failed": 0,
            }
        }

    def _save_calculation_log(self):
        """Save calculation log"""
        log_file = self.data_dir / "calculation_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.calculation_log, f, ensure_ascii=False, indent=2)

    def calculate_ma(self, closes: List[float], periods: List[int] = [5, 10, 20, 60]) -> Dict[str, List[float]]:
        """
        Calculate Moving Average
        
        Args:
            closes: List of closing prices
            periods: MA periods to calculate
            
        Returns:
            Dict with MA values for each period
        """
        result = {}

        for period in periods:
            ma_values = []
            for i in range(len(closes)):
                if i < period - 1:
                    ma_values.append(None)
                else:
                    avg = sum(closes[i -period +1:i +1]) / period
                    ma_values.append(round(avg, 2))

            result[f"MA{period}"] = ma_values

        return result

    def calculate_ema(self, closes: List[float], period: int = 12) -> List[float]:
        """
        Calculate Exponential Moving Average
        
        Args:
            closes: List of closing prices
            period: EMA period
            
        Returns:
            List of EMA values
        """
        ema_values = []
        multiplier = 2 / (period + 1)

        # First EMA is SMA
        if len(closes) < period:
            return [None] * len(closes)

        ema = sum(closes[:period]) / period
        ema_values.extend([None] * (period - 1))
        ema_values.append(round(ema, 2))

        for i in range(period, len(closes)):
            ema = (closes[i] - ema) * multiplier + ema
            ema_values.append(round(ema, 2))

        return ema_values

    def calculate_macd(self, closes: List[float],
                      fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            closes: List of closing prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Dict with MACD line, signal line, and histogram
        """
        ema_fast = self.calculate_ema(closes, fast)
        ema_slow = self.calculate_ema(closes, slow)

        # MACD line = Fast EMA - Slow EMA
        macd_line = []
        for i in range(len(closes)):
            if ema_fast[i] is None or ema_slow[i] is None:
                macd_line.append(None)
            else:
                macd_line.append(round(ema_fast[i] - ema_slow[i], 4))

        # Signal line = EMA of MACD line
        macd_valid = [v for v in macd_line if v is not None]
        signal_line_values = self.calculate_ema(macd_valid, signal)

        # Pad signal line
        signal_line = [None] * (len(macd_line) - len(signal_line_values))
        signal_line.extend(signal_line_values)

        # Histogram = MACD - Signal
        histogram = []
        for i in range(len(closes)):
            if macd_line[i] is None or signal_line[i] is None:
                histogram.append(None)
            else:
                histogram.append(round(macd_line[i] - signal_line[i], 4))

        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram
        }

    def calculate_rsi(self, closes: List[float], period: int = 14) -> List[float]:
        """
        Calculate RSI (Relative Strength Index)
        
        Args:
            closes: List of closing prices
            period: RSI period
            
        Returns:
            List of RSI values (0-100)
        """
        rsi_values = [None] * period

        for i in range(period, len(closes)):
            gains = []
            losses = []

            for j in range(i - period + 1, i + 1):
                change = closes[j] - closes[j -1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(round(rsi, 2))

        return rsi_values

    def calculate_kdj(self, highs: List[float], lows: List[float],
                     closes: List[float], n: int = 9) -> Dict:
        """
        Calculate KDJ (Stochastic Oscillator)
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            n: Period for RSV calculation
            
        Returns:
            Dict with K, D, J values
        """
        k_values = [None] * n
        d_values = [None] * n
        j_values = [None] * n

        prev_k = 50  # Initial K
        prev_d = 50  # Initial D

        for i in range(n, len(closes)):
            # RSV = (Close - Lowest Low) / (Highest High - Lowest Low) * 100
            lowest_low = min(lows[i -n +1:i +1])
            highest_high = max(highs[i -n +1:i +1])

            if highest_high == lowest_low:
                rsv = 0
            else:
                rsv = (closes[i] - lowest_low) / (highest_high - lowest_low) * 100

            # K = 2/3 * Prev_K + 1/3 * RSV
            k = round(2 /3 * prev_k + 1 /3 * rsv, 2)
            # D = 2/3 * Prev_D + 1/3 * K
            d = round(2 /3 * prev_d + 1 /3 * k, 2)
            # J = 3*K - 2*D
            j = round(3 * k - 2 * d, 2)

            k_values.append(k)
            d_values.append(d)
            j_values.append(j)

            prev_k = k
            prev_d = d

        return {"K": k_values, "D": d_values, "J": j_values}

    def calculate_boll(self, closes: List[float], period: int = 20,
                      std_dev: float = 2.0) -> Dict:
        """
        Calculate Bollinger Bands
        
        Args:
            closes: List of closing prices
            period: MA period for middle band
            std_dev: Number of standard deviations
            
        Returns:
            Dict with upper, middle, and lower bands
        """
        upper_band = []
        middle_band = []
        lower_band = []

        for i in range(len(closes)):
            if i < period - 1:
                upper_band.append(None)
                middle_band.append(None)
                lower_band.append(None)
            else:
                # Middle = SMA
                sma = sum(closes[i -period +1:i +1]) / period
                middle_band.append(round(sma, 2))

                # Standard deviation
                variance = sum((closes[j] - sma) ** 2 for j in range(i -period +1, i +1)) / period
                std = math.sqrt(variance)

                upper_band.append(round(sma + std_dev * std, 2))
                lower_band.append(round(sma - std_dev * std, 2))

        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }

    def calculate_atr(self, highs: List[float], lows: List[float],
                     closes: List[float], period: int = 14) -> List[float]:
        """
        Calculate ATR (Average True Range)
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ATR period
            
        Returns:
            List of ATR values
        """
        atr_values = [None] * period

        true_ranges = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i -1]),
                abs(lows[i] - closes[i -1])
            )
            true_ranges.append(tr)

        # First ATR is simple average
        if len(true_ranges) >= period:
            atr = sum(true_ranges[:period]) / period
            atr_values.append(round(atr, 2))

            # Subsequent ATRs use smoothed method
            for i in range(period, len(true_ranges)):
                atr = (atr * (period - 1) + true_ranges[i]) / period
                atr_values.append(round(atr, 2))

        return atr_values

    def calculate_all(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        Calculate all technical indicators for a stock
        
        Args:
            symbol: Stock symbol
            candles: List of candle data (open, high, low, close, volume)
            
        Returns:
            Dict with all indicator values
        """
        if not candles or len(candles) < 60:
            return {"error": "Insufficient data (need at least 60 candles)"}

        # Extract price arrays
        opens = [c["open"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]
        volumes = [c["volume"] for c in candles]

        # Calculate indicators
        result = {
            "symbol": symbol,
            "candle_count": len(candles),
            "calculated_at": datetime.now().isoformat(),
            "indicators": {}
        }

        # MA
        result["indicators"]["MA"] = self.calculate_ma(closes)

        # MACD
        result["indicators"]["MACD"] = self.calculate_macd(closes)

        # RSI
        result["indicators"]["RSI"] = self.calculate_rsi(closes)

        # KDJ
        result["indicators"]["KDJ"] = self.calculate_kdj(highs, lows, closes)

        # BOLL
        result["indicators"]["BOLL"] = self.calculate_boll(closes)

        # ATR
        result["indicators"]["ATR"] = self.calculate_atr(highs, lows, closes)

        # Save to cache
        cache_file = self.data_dir / f"{symbol}_indicators.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Log calculation
        self._log_calculation(symbol, len(candles), success=True)

        return result

    def get_latest_signals(self, indicators: Dict) -> Dict:
        """
        Get trading signals from latest indicator values
        
        Args:
            indicators: Dict with calculated indicators
            
        Returns:
            Dict with trading signals
        """
        signals = {
            "symbol": indicators.get("symbol", "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "signals": {}
        }

        # Get latest values
        ma = indicators["indicators"]["MA"]
        macd = indicators["indicators"]["MACD"]
        rsi = indicators["indicators"]["RSI"]
        kdj = indicators["indicators"]["KDJ"]
        boll = indicators["indicators"]["BOLL"]

        # MA signal
        if ma["MA5"][-1] and ma["MA20"][-1]:
            if ma["MA5"][-1] > ma["MA20"][-1]:
                signals["signals"]["MA"] = "BULLISH"
            else:
                signals["signals"]["MA"] = "BEARISH"

        # MACD signal
        if macd["histogram"][-1] is not None:
            if macd["histogram"][-1] > 0:
                signals["signals"]["MACD"] = "BULLISH"
            else:
                signals["signals"]["MACD"] = "BEARISH"

        # RSI signal
        if rsi[-1] is not None:
            if rsi[-1] > 70:
                signals["signals"]["RSI"] = "OVERBOUGHT"
            elif rsi[-1] < 30:
                signals["signals"]["RSI"] = "OVERSOLD"
            else:
                signals["signals"]["RSI"] = "NEUTRAL"

        # KDJ signal
        if kdj["K"][-1] and kdj["D"][-1]:
            if kdj["K"][-1] > kdj["D"][-1]:
                signals["signals"]["KDJ"] = "BULLISH"
            else:
                signals["signals"]["KDJ"] = "BEARISH"

        # BOLL signal
        if boll["upper"][-1] and boll["lower"][-1]:
            # Would need current price to determine
            signals["signals"]["BOLL"] = "NEUTRAL"

        return signals

    def _log_calculation(self, symbol: str, candles: int, success: bool):
        """Log calculation attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "candles": candles,
            "success": success
        }

        self.calculation_log["calculations"].append(log_entry)
        self.calculation_log["stats"]["total_calculations"] += 1

        if success:
            self.calculation_log["stats"]["successful"] += 1
        else:
            self.calculation_log["stats"]["failed"] += 1

        # Keep only last 500 entries
        self.calculation_log["calculations"] = self.calculation_log["calculations"][-500:]

        self._save_calculation_log()

    def get_stats(self) -> Dict:
        """Get calculation statistics"""
        return self.calculation_log["stats"].copy()

    def display_status(self) -> str:
        """Display calculator status"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 14 + "Technical Indicator Calculator Status")
        output.append("=" * 70)

        output.append(f"\n[Supported Indicators]")
        output.append(f"  {', '.join(self.supported_indicators)}")

        output.append(f"\n[Statistics]")
        output.append(f"  Total Calculations: {stats['total_calculations']}")
        output.append(f"  Successful:         {stats['successful']}")
        output.append(f"  Failed:             {stats['failed']}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 12 + "SA-005: Technical Indicator Calculator")
    print("=" * 70)

    calculator = TechnicalIndicatorCalculator()

    # Test 1: Display status
    print(calculator.display_status())

    # Test 2: Generate test data
    print("\n[Test 1] Generate Test Data")
    print("-" * 70)
    import random
    candles = []
    price = 100
    for i in range(100):
        change = random.uniform(-0.03, 0.03)
        open_p = price
        close_p = price * (1 + change)
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.02))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.02))
        volume = random.randint(5000000, 50000000)

        candles.append({
            "date": f"2026-01-{i%30 +1:02d}",
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume
        })
        price = close_p

    print(f"  Generated {len(candles)} candles")
    print(f"  Price range: {min(c['close'] for c in candles):.2f} - {max(c['close'] for c in candles):.2f}")

    # Test 3: Calculate all indicators
    print("\n[Test 2] Calculate All Indicators")
    print("-" * 70)
    result = calculator.calculate_all("TEST", candles)

    if "error" not in result:
        print(f"  Symbol:       {result['symbol']}")
        print(f"  Candles:      {result['candle_count']}")

        ma = result["indicators"]["MA"]
        print(f"\n  MA (Latest):")
        print(f"    MA5:  {ma['MA5'][-1]}")
        print(f"    MA10: {ma['MA10'][-1]}")
        print(f"    MA20: {ma['MA20'][-1]}")
        print(f"    MA60: {ma['MA60'][-1]}")

        macd = result["indicators"]["MACD"]
        print(f"\n  MACD (Latest):")
        print(f"    MACD:     {macd['macd_line'][-1]}")
        print(f"    Signal:   {macd['signal_line'][-1]}")
        print(f"    Histogram: {macd['histogram'][-1]}")

        rsi = result["indicators"]["RSI"]
        print(f"\n  RSI (Latest): {rsi[-1]}")

        kdj = result["indicators"]["KDJ"]
        print(f"\n  KDJ (Latest):")
        print(f"    K: {kdj['K'][-1]}")
        print(f"    D: {kdj['D'][-1]}")
        print(f"    J: {kdj['J'][-1]}")

        boll = result["indicators"]["BOLL"]
        print(f"\n  BOLL (Latest):")
        print(f"    Upper:  {boll['upper'][-1]}")
        print(f"    Middle: {boll['middle'][-1]}")
        print(f"    Lower:  {boll['lower'][-1]}")

        atr = result["indicators"]["ATR"]
        print(f"\n  ATR (Latest): {atr[-1]}")

    # Test 4: Get trading signals
    print("\n[Test 3] Get Trading Signals")
    print("-" * 70)
    if "error" not in result:
        signals = calculator.get_latest_signals(result)
        print(f"  Symbol: {signals['symbol']}")
        print(f"\n  Signals:")
        for indicator, signal in signals["signals"].items():
            print(f"    {indicator:6} {signal}")

    # Test 5: Final stats
    print("\n[Test 4] Final Statistics")
    print("-" * 70)
    stats = calculator.get_stats()
    print(f"  Total Calculations: {stats['total_calculations']}")
    print(f"  Successful:         {stats['successful']}")
    print(f"  Failed:             {stats['failed']}")

    print("\n[OK] SA-005 Technical Indicator Calculator test completed")

if __name__ == "__main__":
    main()
