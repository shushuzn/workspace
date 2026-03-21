#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-008: Support and Resistance Analysis
支撑阻力分析工具 - 枢轴点、斐波那契回撤、成交量分布分析

功能：
1. 枢轴点计算（标准型、Woodie、费波纳奇）
2. 斐波那契回撤位计算
3. 支撑阻力位自动检测
4. 水平位强度评分
5. 突破/支撑信号生成

依赖：
- SA-005: Technical Indicator Calculator

作者：Claw (AI Agent)
创建日期：2026-03-21
版本：1.0.0
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class PivotPointCalculator:
    """枢轴点计算器"""
    
    @staticmethod
    def calculate_standard(high: float, low: float, close: float) -> Dict[str, float]:
        """
        标准枢轴点计算
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
            
        Returns:
            枢轴点及支撑阻力位
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
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "r3": round(r3, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(s3, 2)
        }
    
    @staticmethod
    def calculate_woodie(high: float, low: float, close: float) -> Dict[str, float]:
        """
        Woodie 枢轴点
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
            
        Returns:
            Woodie 枢轴点及支撑阻力位
        """
        pivot = (high + low + 2 * close) / 4
        
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        return {
            "pivot": round(pivot, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "r3": round(high + 2 * (pivot - low), 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(low - 2 * (high - pivot), 2)
        }
    
    @staticmethod
    def calculate_fibonacci(high: float, low: float, close: float) -> Dict[str, float]:
        """
        斐波纳奇枢轴点
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
            
        Returns:
            斐波纳奇枢轴点及支撑阻力位
        """
        pivot = (high + low + close) / 3
        
        # 阻力位
        r1 = pivot + (high - low) * 0.382
        r2 = pivot + (high - low) * 0.618
        r3 = pivot + (high - low) * 1.0
        
        # 支撑位
        s1 = pivot - (high - low) * 0.382
        s2 = pivot - (high - low) * 0.618
        s3 = pivot - (high - low) * 1.0
        
        return {
            "pivot": round(pivot, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "r3": round(r3, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(s3, 2)
        }


class FibonacciCalculator:
    """斐波那契计算器"""
    
    # 斐波那契回撤水平
    FIB_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    FIB_LEVELS_EXTENDED = [1.272, 1.414, 1.618, 2.0, 2.618]
    
    @staticmethod
    def calculate_retracement(high: float, low: float) -> Dict[str, float]:
        """
        计算斐波那契回撤位
        
        Args:
            high: 高点
            low: 低点
            
        Returns:
            各回撤位价格
        """
        diff = high - low
        
        levels = {}
        for fib in FibonacciCalculator.FIB_LEVELS:
            level_name = f"fib_{int(fib * 1000)}" if fib < 1 else "fib_1000"
            levels[level_name] = round(high - diff * fib, 2)
        
        levels["range"] = round(diff, 2)
        levels["high"] = round(high, 2)
        levels["low"] = round(low, 2)
        
        return levels
    
    @staticmethod
    def calculate_extension(high: float, low: float, start: float) -> Dict[str, float]:
        """
        计算斐波那契扩展位
        
        Args:
            high: 高点
            low: 低点
            start: 起始点（用于计算扩展）
            
        Returns:
            各扩展位价格
        """
        diff = high - low
        
        extensions = {}
        for fib in FibonacciCalculator.FIB_LEVELS_EXTENDED:
            level_name = f"ext_{str(fib).replace('.', '')}"
            extensions[level_name] = round(low + diff * fib, 2)
        
        return extensions
    
    @staticmethod
    def get_current_position(price: float, high: float, low: float) -> Dict[str, Any]:
        """
        获取价格在斐波那契回撤位中的位置
        
        Args:
            price: 当前价格
            high: 高点
            low: 低点
            
        Returns:
            位置信息
        """
        diff = high - low
        
        if diff == 0:
            return {"position": "unknown", "percentage": 0}
        
        # 计算当前价格在高-低区间的位置
        percentage = (price - low) / diff * 100
        
        # 确定位置
        if percentage < 23.6:
            position = "deep_pullback"
        elif percentage < 38.2:
            position = "shallow_pullback"
        elif percentage < 50:
            position = "golden_zone_1"
        elif percentage < 61.8:
            position = "golden_zone_2"
        elif percentage < 78.6:
            position = "above_golden"
        else:
            position = "near_high"
        
        return {
            "position": position,
            "percentage": round(percentage, 2),
            "retracement": round(100 - percentage, 2)
        }


class VolumePriceAnalyzer:
    """成交量价格分布分析器"""
    
    def __init__(self, bin_count: int = 20):
        self.bin_count = bin_count
    
    def analyze_volume_profile(self, candles: List[Dict]) -> Dict[str, Any]:
        """
        分析成交量分布
        
        Args:
            candles: K线数据列表
            
        Returns:
            成交量分布分析结果
        """
        if not candles:
            return {"error": "无数据"}
        
        # 提取价格和成交量
        prices = [(c["high"] + c["low"]) / 2 for c in candles]
        volumes = [c.get("volume", 0) for c in candles]
        
        # 确定价格范围
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return {"error": "价格范围为0"}
        
        # 创建价格区间
        bin_size = price_range / self.bin_count
        
        # 统计每个区间的成交量
        bins = [0] * self.bin_count
        bin_prices = []
        
        for i in range(self.bin_count):
            bin_prices.append(round(min_price + bin_size * (i + 0.5), 2))
        
        for i, price in enumerate(prices):
            bin_index = min(int((price - min_price) / bin_size), self.bin_count - 1)
            bins[bin_index] += volumes[i]
        
        # 找出高成交量区域
        avg_volume = sum(bins) / len(bins)
        
        high_volume_bins = []
        for i, vol in enumerate(bins):
            if vol > avg_volume * 1.5:
                high_volume_bins.append({
                    "price": bin_prices[i],
                    "volume": vol,
                    "strength": round(vol / avg_volume, 2)
                })
        
        return {
            "price_range": {
                "min": round(min_price, 2),
                "max": round(max_price, 2)
            },
            "high_volume_levels": high_volume_bins,
            "avg_volume": round(avg_volume, 0),
            "bins": bins,
            "bin_prices": bin_prices
        }


class SupportResistanceDetector:
    """支撑阻力位检测器"""
    
    def __init__(self, touch_threshold: int = 2):
        """
        Args:
            touch_threshold: 价格触及次数阈值
        """
        self.touch_threshold = touch_threshold
    
    def detect_swing_points(self, candles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        检测摆动高点和低点
        
        Args:
            candles: K线数据列表
            
        Returns:
            (swing_highs, swing_lows)
        """
        if len(candles) < 5:
            return [], []
        
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        swing_highs = []
        swing_lows = []
        
        # 检测摆动高点（局部最高点）
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append({
                    "index": i,
                    "price": round(highs[i], 2),
                    "date": candles[i].get("date", f"candle_{i}")
                })
        
        # 检测摆动低点（局部最低点）
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append({
                    "index": i,
                    "price": round(lows[i], 2),
                    "date": candles[i].get("date", f"candle_{i}")
                })
        
        return swing_highs, swing_lows
    
    def group_nearby_levels(self, points: List[Dict], tolerance: float = 0.02) -> List[Dict]:
        """
        将相近的价格点位分组
        
        Args:
            points: 价格点列表
            tolerance: 容差比例（默认2%）
            
        Returns:
            分组后的水平位
        """
        if not points:
            return []
        
        # 按价格排序
        sorted_points = sorted(points, key=lambda x: x["price"])
        
        groups = []
        current_group = [sorted_points[0]]
        
        for i in range(1, len(sorted_points)):
            prev_price = current_group[-1]["price"]
            curr_price = sorted_points[i]["price"]
            
            # 如果价格相近，合并
            if abs(curr_price - prev_price) / prev_price <= tolerance:
                current_group.append(sorted_points[i])
            else:
                groups.append(current_group)
                current_group = [sorted_points[i]]
        
        groups.append(current_group)
        
        # 计算每组的统计信息
        levels = []
        for group in groups:
            avg_price = sum(p["price"] for p in group) / len(group)
            levels.append({
                "price": round(avg_price, 2),
                "touch_count": len(group),
                "points": group
            })
        
        return levels
    
    def calculate_level_strength(self, price: float, touch_count: int, 
                                 recent_touches: int = 0) -> Dict[str, Any]:
        """
        计算水平位强度
        
        Args:
            price: 价位
            touch_count: 触及次数
            recent_touches: 最近触及次数
            
        Returns:
            强度信息
        """
        # 基础强度分数
        base_score = min(touch_count * 10, 50)
        
        # 最近触及加分
        recent_bonus = min(recent_touches * 15, 30)
        
        # 综合强度
        total_score = base_score + recent_bonus
        
        # 强度等级
        if total_score >= 70:
            strength = "very_strong"
            label = "非常强"
        elif total_score >= 50:
            strength = "strong"
            label = "强"
        elif total_score >= 30:
            strength = "moderate"
            label = "中等"
        else:
            strength = "weak"
            label = "弱"
        
        return {
            "score": total_score,
            "strength": strength,
            "label": label,
            "description": f"{label}支撑/阻力位"
        }
    
    def detect_support_resistance(self, candles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        综合检测支撑阻力位
        
        Args:
            candles: K线数据列表
            
        Returns:
            支撑位和阻力位列表
        """
        swing_highs, swing_lows = self.detect_swing_points(candles)
        
        # 分组相近点位
        resistance_levels = self.group_nearby_levels(swing_highs)
        support_levels = self.group_nearby_levels(swing_lows)
        
        # 计算强度
        for level in resistance_levels:
            strength_info = self.calculate_level_strength(
                level["price"], 
                level["touch_count"]
            )
            level.update(strength_info)
        
        for level in support_levels:
            strength_info = self.calculate_level_strength(
                level["price"], 
                level["touch_count"]
            )
            level.update(strength_info)
        
        # 按强度排序
        resistance_levels.sort(key=lambda x: x["score"], reverse=True)
        support_levels.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "resistance": resistance_levels,
            "support": support_levels
        }


class SRAnalyzer:
    """支撑阻力分析主类"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_sr_levels"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.pivot_calc = PivotPointCalculator()
        self.fib_calc = FibonacciCalculator()
        self.vp_analyzer = VolumePriceAnalyzer()
        self.sr_detector = SupportResistanceDetector()
        
        self.analysis_log = self._load_analysis_log()
    
    def _load_analysis_log(self) -> Dict:
        """加载分析日志"""
        log_file = self.data_dir / "analysis_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "analyses": [],
            "stats": {
                "total_analyses": 0,
                "successful": 0,
                "failed": 0
            }
        }
    
    def _save_analysis_log(self):
        """保存分析日志"""
        log_file = self.data_dir / "analysis_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_log, f, ensure_ascii=False, indent=2)
    
    def analyze(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        综合支撑阻力分析
        
        Args:
            symbol: 股票代码
            candles: K线数据列表
            
        Returns:
            分析报告
        """
        if not candles or len(candles) < 20:
            return {"error": "数据不足，需要至少 20 根 K 线"}
        
        # 提取最新价格数据
        latest = candles[-1]
        high = latest["high"]
        low = latest["low"]
        close = latest["close"]
        current_price = close
        
        result = {
            "symbol": symbol,
            "analysis_date": datetime.now().isoformat(),
            "candle_count": len(candles),
            "current_price": round(current_price, 2),
            "pivot_points": {},
            "fibonacci": {},
            "volume_profile": {},
            "levels": {},
            "signals": {},
            "summary": {}
        }
        
        # 1. 枢轴点计算
        result["pivot_points"] = {
            "standard": self.pivot_calc.calculate_standard(high, low, close),
            "woodie": self.pivot_calc.calculate_woodie(high, low, close),
            "fibonacci": self.pivot_calc.calculate_fibonacci(high, low, close)
        }
        
        # 2. 斐波那契回撤
        # 使用近期高点低点
        recent_highs = [c["high"] for c in candles[-30:]]
        recent_lows = [c["low"] for c in candles[-30:]]
        
        fib_high = max(recent_highs)
        fib_low = min(recent_lows)
        
        result["fibonacci"] = {
            "retracement": self.fib_calc.calculate_retracement(fib_high, fib_low),
            "position": self.fib_calc.get_current_position(current_price, fib_high, fib_low)
        }
        
        # 3. 成交量分布
        result["volume_profile"] = self.vp_analyzer.analyze_volume_profile(candles)
        
        # 4. 支撑阻力位检测
        sr_levels = self.sr_detector.detect_support_resistance(candles)
        result["levels"] = sr_levels
        
        # 5. 信号生成
        result["signals"] = self._generate_signals(result, current_price)
        
        # 6. 总结
        result["summary"] = self._generate_summary(result, current_price)
        
        # 保存报告
        self._save_report(result, symbol)
        self._log_analysis(symbol, len(candles), success=True)
        
        return result
    
    def _generate_signals(self, analysis: Dict, current_price: float) -> Dict:
        """生成交易信号"""
        signals = {
            "type": "neutral",
            "confidence": 50,
            "nearest_support": None,
            "nearest_resistance": None,
            "stop_loss": None,
            "take_profit": [],
            "description": ""
        }
        
        support_levels = analysis.get("levels", {}).get("support", [])
        resistance_levels = analysis.get("levels", {}).get("resistance", [])
        
        # 找最近的支撑和阻力
        if support_levels:
            # 找当前价下方的支撑
            valid_supports = [s for s in support_levels if s["price"] < current_price]
            if valid_supports:
                nearest_support = min(valid_supports, key=lambda x: current_price - x["price"])
                signals["nearest_support"] = nearest_support["price"]
                
                # 止损位在支撑下方
                signals["stop_loss"] = round(nearest_support["price"] * 0.98, 2)
        
        if resistance_levels:
            # 找当前价上方的阻力
            valid_resistances = [r for r in resistance_levels if r["price"] > current_price]
            if valid_resistances:
                nearest_resistance = min(valid_resistances, key=lambda x: x["price"] - current_price)
                signals["nearest_resistance"] = nearest_resistance["price"]
                
                # 止盈位在阻力位
                signals["take_profit"].append(nearest_resistance["price"])
        
        # 判断信号类型
        pivot = analysis.get("pivot_points", {}).get("standard", {}).get("pivot", current_price)
        fib_position = analysis.get("fibonacci", {}).get("position", {}).get("position", "unknown")
        
        if current_price > pivot and fib_position in ["above_golden", "near_high"]:
            signals["type"] = "bearish"
            signals["description"] = "价格处于斐波那契高位，关注回落风险"
        elif current_price < pivot and fib_position in ["deep_pullback", "shallow_pullback"]:
            signals["type"] = "bullish"
            signals["description"] = "价格处于斐波那契支撑区域，关注反弹机会"
        else:
            signals["type"] = "neutral"
            signals["description"] = "价格处于中性区域，等待方向确认"
        
        # 计算置信度
        confidence = 50
        if signals["nearest_support"] and signals["nearest_resistance"]:
            distance_to_support = (current_price - signals["nearest_support"]) / current_price * 100
            distance_to_resistance = (signals["nearest_resistance"] - current_price) / current_price * 100
            
            if distance_to_support < 3:
                confidence += 10
            if distance_to_resistance < 5:
                confidence += 10
            
            signals["confidence"] = min(confidence, 90)
        
        return signals
    
    def _generate_summary(self, analysis: Dict, current_price: float) -> Dict:
        """生成分析总结"""
        summary = {
            "current_price": round(current_price, 2),
            "key_levels": {
                "strong_support": None,
                "strong_resistance": None
            },
            "market_position": "neutral",
            "outlook": ""
        }
        
        support_levels = analysis.get("levels", {}).get("support", [])
        resistance_levels = analysis.get("levels", {}).get("resistance", {})
        
        # 最强支撑
        if support_levels:
            strong_support = support_levels[0]
            summary["key_levels"]["strong_support"] = {
                "price": strong_support["price"],
                "strength": strong_support["strength"]
            }
        
        # 最强阻力
        if resistance_levels:
            strong_resistance = resistance_levels[0]
            summary["key_levels"]["strong_resistance"] = {
                "price": strong_resistance["price"],
                "strength": strong_resistance["strength"]
            }
        
        # 市场位置判断
        if summary["key_levels"]["strong_support"] and summary["key_levels"]["strong_resistance"]:
            support_price = summary["key_levels"]["strong_support"]["price"]
            resistance_price = summary["key_levels"]["strong_resistance"]["price"]
            
            range_size = resistance_price - support_price
            position_in_range = (current_price - support_price) / range_size * 100
            
            if position_in_range < 30:
                summary["market_position"] = "near_support"
                summary["outlook"] = "价格接近支撑位，关注反弹机会"
            elif position_in_range > 70:
                summary["market_position"] = "near_resistance"
                summary["outlook"] = "价格接近阻力位，关注回落风险"
            else:
                summary["market_position"] = "mid_range"
                summary["outlook"] = "价格在中部区间，等待突破方向"
        else:
            summary["market_position"] = "no_clear_levels"
            summary["outlook"] = "缺乏明确的支撑阻力位"
        
        return summary
    
    def _save_report(self, report: Dict, symbol: str):
        """保存分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_sr_{timestamp}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def _log_analysis(self, symbol: str, candles: int, success: bool):
        """记录分析日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "candles": candles,
            "success": success
        }
        
        self.analysis_log["analyses"].append(log_entry)
        self.analysis_log["stats"]["total_analyses"] += 1
        
        if success:
            self.analysis_log["stats"]["successful"] += 1
        else:
            self.analysis_log["stats"]["failed"] += 1
        
        # 保留最近 500 条
        self.analysis_log["analyses"] = self.analysis_log["analyses"][-500:]
        
        self._save_analysis_log()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.analysis_log["stats"].copy()
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 18 + "Support/Resistance Analyzer Status")
        output.append("=" * 70)
        
        output.append(f"\n[Calculators]")
        output.append("  - Pivot Points (Standard/Woodie/Fibonacci)")
        output.append("  - Fibonacci Retracement")
        output.append("  - Volume Profile")
        output.append("  - Swing Point Detection")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Analyses: {stats['total_analyses']}")
        output.append(f"  Successful:     {stats['successful']}")
        output.append(f"  Failed:         {stats['failed']}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def generate_test_data(num_candles: int = 100, volatility: float = 0.03) -> List[Dict]:
    """生成测试 K 线数据"""
    import random
    
    candles = []
    price = 100.0
    
    for i in range(num_candles):
        change = random.uniform(-volatility, volatility)
        
        open_price = price
        close_price = price * (1 + change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility / 2))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility / 2))
        
        candles.append({
            'date': f'2026-01-{(i % 28) + 1:02d}',
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(1000000, 10000000)
        })
        
        price = close_price
    
    return candles


def main():
    """主函数"""
    print("=" * 70)
    print(" " * 14 + "SA-008: Support and Resistance Analysis")
    print("=" * 70)
    
    analyzer = SRAnalyzer()
    
    # 显示状态
    print(analyzer.display_status())
    
    # 生成测试数据
    print("\n[Test 1] Support/Resistance Analysis")
    print("-" * 70)
    candles = generate_test_data(100)
    
    result = analyzer.analyze("TEST_SR", candles)
    
    print(f"Symbol: {result['symbol']}")
    print(f"Candles: {result['candle_count']}")
    print(f"Current Price: {result['current_price']}")
    
    print("\n[Pivot Points - Standard]")
    pivot = result['pivot_points']['standard']
    print(f"  Pivot: {pivot['pivot']}")
    print(f"  R1: {pivot['r1']}, R2: {pivot['r2']}, R3: {pivot['r3']}")
    print(f"  S1: {pivot['s1']}, S2: {pivot['s2']}, S3: {pivot['s3']}")
    
    print("\n[Fibonacci Retracement]")
    fib = result['fibonacci']['retracement']
    print(f"  High: {fib['high']}, Low: {fib['low']}, Range: {fib['range']}")
    print(f"  23.6%: {fib['fib_236']}, 38.2%: {fib['fib_382']}")
    print(f"  50.0%: {fib['fib_500']}, 61.8%: {fib['fib_618']}")
    
    print("\n[Fibonacci Position]")
    fib_pos = result['fibonacci']['position']
    print(f"  Position: {fib_pos['position']}")
    print(f"  Percentage: {fib_pos['percentage']}%")
    
    print("\n[Support Levels (Top 3)]")
    for i, level in enumerate(result['levels']['support'][:3]):
        print(f"  {i+1}. Price: {level['price']}, Touches: {level['touch_count']}, Strength: {level['strength']}")
    
    print("\n[Resistance Levels (Top 3)]")
    for i, level in enumerate(result['levels']['resistance'][:3]):
        print(f"  {i+1}. Price: {level['price']}, Touches: {level['touch_count']}, Strength: {level['strength']}")
    
    print("\n[Signals]")
    signals = result['signals']
    print(f"  Type: {signals['type']}")
    print(f"  Confidence: {signals['confidence']}%")
    print(f"  Nearest Support: {signals['nearest_support']}")
    print(f"  Nearest Resistance: {signals['nearest_resistance']}")
    print(f"  Stop Loss: {signals['stop_loss']}")
    print(f"  Take Profit: {signals['take_profit']}")
    print(f"  Description: {signals['description']}")
    
    print("\n[Summary]")
    summary = result['summary']
    print(f"  Market Position: {summary['market_position']}")
    print(f"  Outlook: {summary['outlook']}")
    
    if summary['key_levels']['strong_support']:
        ss = summary['key_levels']['strong_support']
        print(f"  Strong Support: {ss['price']} ({ss['strength']})")
    
    if summary['key_levels']['strong_resistance']:
        sr = summary['key_levels']['strong_resistance']
        print(f"  Strong Resistance: {sr['price']} ({sr['strength']})")
    
    print("\n" + "=" * 70)
    print("\nUsage: py sa_008_support_resistance.py --test")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        main()
    else:
        print("SA-008: Support and Resistance Analysis Tool")
        print("Usage: py sa_008_support_resistance.py --test")
