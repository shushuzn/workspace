#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-007: Trend Analysis
趋势分析工具 - 检测短期/中期/长期趋势、ADX趋势强度、线性回归分析

功能：
1. 趋势方向检测（上升/下降/横盘）
2. 多时间框架趋势分析
3. ADX 趋势强度指标
4. 线性回归趋势线
5. 趋势信号生成与评分

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


class TrendDirectionDetector:
    """趋势方向检测器"""
    
    # 趋势周期配置
    TIMEFRAMES = {
        "short": {"name": "短期", "period": 10, "ma_period": 5},
        "medium": {"name": "中期", "period": 30, "ma_period": 20},
        "long": {"name": "长期", "period": 60, "ma_period": 60}
    }
    
    @staticmethod
    def detect_by_ma(prices: List[float], fast_ma: List[float], 
                     slow_ma: List[float]) -> str:
        """
        通过 MA 交叉检测趋势方向
        
        Args:
            prices: 价格列表
            fast_ma: 快线 MA
            slow_ma: 慢线 MA
            
        Returns:
            "up" / "down" / "sideways"
        """
        if len(fast_ma) < 2 or len(slow_ma) < 2:
            return "unknown"
        
        # 使用最近的有效值
        valid_pairs = [(f, s) for f, s in zip(fast_ma, slow_ma) 
                      if f is not None and s is not None]
        
        if len(valid_pairs) < 2:
            return "unknown"
        
        # 计算 MA 斜率
        f1, s1 = valid_pairs[-2]
        f2, s2 = valid_pairs[-1]
        
        ma_slope = (f2 - f1 + s2 - s1) / 2
        
        if ma_slope > 0.1:
            return "up"
        elif ma_slope < -0.1:
            return "down"
        else:
            return "sideways"
    
    @staticmethod
    def detect_by_price_channel(prices: List[float], period: int = 20) -> str:
        """
        通过价格通道检测趋势
        
        Args:
            prices: 价格列表
            period: 检测周期
            
        Returns:
            "up" / "down" / "sideways"
        """
        if len(prices) < period * 2:
            return "unknown"
        
        # 比较最近周期和前一周期的价格变化
        recent = prices[-period:]
        previous = prices[-period*2:-period]
        
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)
        
        change_pct = (recent_avg - previous_avg) / previous_avg * 100
        
        if change_pct > 3:
            return "up"
        elif change_pct < -3:
            return "down"
        else:
            return "sideways"
    
    @staticmethod
    def calculate_slope(prices: List[float]) -> float:
        """
        计算价格序列的线性斜率
        
        Args:
            prices: 价格列表
            
        Returns:
            斜率值（每天变化）
        """
        if len(prices) < 2:
            return 0.0
        
        n = len(prices)
        x_mean = (n - 1) / 2
        y_mean = sum(prices) / n
        
        numerator = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


class ADXCalculator:
    """ADX (Average Directional Index) 趋势强度计算器"""
    
    def __init__(self):
        self.adx_period = 14
        self.di_period = 14
    
    def calculate_true_range(self, highs: List[float], lows: List[float],
                            closes: List[float]) -> List[float]:
        """计算 True Range"""
        tr_list = [0.0]  # 第一个 TR 为 0
        
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
        
        return tr_list
    
    def calculate_directional_movement(self, highs: List[float], 
                                       lows: List[float]) -> Tuple[List[float], List[float]]:
        """计算方向性运动 +DI 和 -DI"""
        plus_dm = [0.0]
        minus_dm = [0.0]
        
        for i in range(1, len(highs)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            # +DM: 上升方向运动
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
            else:
                plus_dm.append(0.0)
            
            # -DM: 下降方向运动
            if low_diff > high_diff and low_diff > 0:
                minus_dm.append(low_diff)
            else:
                minus_dm.append(0.0)
        
        return plus_dm, minus_dm
    
    def calculate_adx(self, highs: List[float], lows: List[float],
                     closes: List[float]) -> Dict[str, List[float]]:
        """
        计算 ADX 系列指标
        
        Returns:
            Dict with ADX, +DI, -DI values
        """
        if len(closes) < self.adx_period * 2:
            return {"adx": [], "plus_di": [], "minus_di": []}
        
        tr = self.calculate_true_range(highs, lows, closes)
        plus_dm, minus_dm = self.calculate_directional_movement(highs, lows)
        
        # 平滑处理
        period = self.di_period
        
        # 初始 ATR
        atr = sum(tr[1:period+1]) / period
        atr_values = [None] * (period + 1)
        atr_values.append(atr)
        
        # 初始 +DM 和 -DM
        plus_dm_smooth = sum(plus_dm[1:period+1])
        minus_dm_smooth = sum(minus_dm[1:period+1])
        
        plus_di = []
        minus_di = []
        dx = []
        
        for i in range(period, len(closes)):
            # ATR 平滑
            atr = (atr * (period - 1) + tr[i]) / period
            atr_values.append(atr)
            
            # +DM 和 -DM 平滑
            plus_dm_smooth = (plus_dm_smooth * (period - 1) + plus_dm[i]) / period
            minus_dm_smooth = (minus_dm_smooth * (period - 1) + minus_dm[i]) / period
            
            # 计算 +DI 和 -DI
            if atr > 0:
                plus_di_val = (plus_dm_smooth / atr) * 100
                minus_di_val = (minus_dm_smooth / atr) * 100
            else:
                plus_di_val = 0
                minus_di_val = 0
            
            plus_di.append(round(plus_di_val, 2))
            minus_di.append(round(minus_di_val, 2))
            
            # 计算 DX
            di_sum = plus_di_val + minus_di_val
            if di_sum > 0:
                dx_val = abs(plus_di_val - minus_di_val) / di_sum * 100
            else:
                dx_val = 0
            dx.append(dx_val)
        
        # 计算 ADX（DX 的平滑移动平均）
        adx_values = [None] * (period + len(dx))
        
        if len(dx) >= self.adx_period:
            adx = sum(dx[:self.adx_period]) / self.adx_period
            adx_values.append(adx)
            
            for i in range(self.adx_period, len(dx)):
                adx = (adx * (self.adx_period - 1) + dx[i]) / self.adx_period
                adx_values.append(adx)
        
        # Pad 前面的值
        plus_di = [None] * (period + 1) + plus_di
        minus_di = [None] * (period + 1) + minus_di
        
        return {
            "adx": adx_values,
            "plus_di": plus_di,
            "minus_di": minus_di
        }
    
    def interpret_adx(self, adx: float, plus_di: float, minus_di: float) -> Dict[str, Any]:
        """
        解释 ADX 指标
        
        Args:
            adx: ADX 值
            plus_di: +DI 值
            minus_di: -DI 值
            
        Returns:
            趋势解释
        """
        result = {
            "trend_strength": "weak",
            "trend_direction": "neutral",
            "signal": "hold",
            "description": ""
        }
        
        # 趋势强度
        if adx < 20:
            result["trend_strength"] = "weak"
            result["description"] = "趋势弱，市场盘整"
        elif adx < 40:
            result["trend_strength"] = "moderate"
            result["description"] = "趋势中等人" if adx < 30 else "趋势较强"
        else:
            result["trend_strength"] = "strong"
            result["description"] = "趋势强劲"
        
        # 趋势方向
        if plus_di > minus_di:
            result["trend_direction"] = "up"
            if adx > 20:
                result["signal"] = "buy"
                result["description"] += "，上升趋势中"
        elif minus_di > plus_di:
            result["trend_direction"] = "down"
            if adx > 20:
                result["signal"] = "sell"
                result["description"] += "，下降趋势中"
        else:
            result["trend_direction"] = "neutral"
            result["description"] += "，方向不明"
        
        return result


class LinearRegressionAnalyzer:
    """线性回归分析器"""
    
    @staticmethod
    def linear_regression(prices: List[float]) -> Dict[str, float]:
        """
        计算线性回归
        
        Returns:
            Dict with slope, intercept, r_squared
        """
        n = len(prices)
        if n < 2:
            return {"slope": 0, "intercept": 0, "r_squared": 0}
        
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(prices) / n
        
        # 计算斜率和截距
        numerator = sum((x[i] - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # 计算 R²
        ss_res = sum((prices[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((prices[i] - y_mean) ** 2 for i in range(n))
        
        if ss_tot == 0:
            r_squared = 0
        else:
            r_squared = 1 - (ss_res / ss_tot)
        
        return {
            "slope": round(slope, 4),
            "intercept": round(intercept, 2),
            "r_squared": round(r_squared, 4)
        }
    
    @staticmethod
    def predict_next(prices: List[float], periods: int = 5) -> List[float]:
        """
        预测未来价格
        
        Args:
            prices: 历史价格
            periods: 预测周期数
            
        Returns:
            预测价格列表
        """
        reg = LinearRegressionAnalyzer.linear_regression(prices)
        
        n = len(prices)
        predictions = []
        
        for i in range(1, periods + 1):
            pred = reg["slope"] * (n + i - 1) + reg["intercept"]
            predictions.append(round(pred, 2))
        
        return predictions
    
    @staticmethod
    def calculate_residuals(prices: List[float]) -> List[float]:
        """计算残差（实际值与回归线的差）"""
        n = len(prices)
        if n < 2:
            return []
        
        reg = LinearRegressionAnalyzer.linear_regression(prices)
        
        residuals = []
        for i in range(n):
            predicted = reg["slope"] * i + reg["intercept"]
            residuals.append(round(prices[i] - predicted, 2))
        
        return residuals


class TrendAnalyzer:
    """趋势分析主类"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_trends"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.detector = TrendDirectionDetector()
        self.adx_calc = ADXCalculator()
        self.lr_analyzer = LinearRegressionAnalyzer()
        
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
    
    def _calculate_ma(self, prices: List[float], period: int) -> List[float]:
        """计算简单移动平均"""
        ma = [None] * (period - 1)
        
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            ma.append(round(avg, 2))
        
        return ma
    
    def analyze_trend(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        综合趋势分析
        
        Args:
            symbol: 股票代码
            candles: K线数据列表
            
        Returns:
            趋势分析报告
        """
        if not candles or len(candles) < 60:
            return {"error": "数据不足，需要至少 60 根 K 线"}
        
        # 提取价格数据
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]
        volumes = [c.get("volume", 0) for c in candles]
        
        result = {
            "symbol": symbol,
            "analysis_date": datetime.now().isoformat(),
            "candle_count": len(candles),
            "timeframes": {},
            "adx": {},
            "linear_regression": {},
            "signals": {},
            "summary": {}
        }
        
        # 1. 多时间框架趋势分析
        for tf_key, tf_config in self.detector.TIMEFRAMES.items():
            period = tf_config["period"]
            ma_period = tf_config["ma_period"]
            
            if len(closes) >= period:
                # 计算 MA
                ma_fast = self._calculate_ma(closes, tf_config["ma_period"])
                ma_slow = self._calculate_ma(closes, period)
                
                # 趋势检测
                trend_by_ma = self.detector.detect_by_ma(
                    closes[-period:], 
                    ma_fast[-period:], 
                    ma_slow[-period:]
                )
                
                trend_by_channel = self.detector.detect_by_price_channel(
                    closes[-period*2:] if len(closes) >= period*2 else closes
                )
                
                # 斜率
                slope = self.detector.calculate_slope(closes[-period:])
                
                result["timeframes"][tf_key] = {
                    "name": tf_config["name"],
                    "period": period,
                    "trend_by_ma": trend_by_ma,
                    "trend_by_channel": trend_by_channel,
                    "slope": round(slope, 4),
                    "detected_trend": trend_by_ma if trend_by_ma != "unknown" else trend_by_channel
                }
        
        # 2. ADX 分析
        adx_result = self.adx_calc.calculate_adx(highs, lows, closes)
        
        if adx_result["adx"]:
            latest_adx = adx_result["adx"][-1]
            latest_plus_di = adx_result["plus_di"][-1] if adx_result["plus_di"] else 0
            latest_minus_di = adx_result["minus_di"][-1] if adx_result["minus_di"] else 0
            
            adx_interpretation = self.adx_calc.interpret_adx(
                latest_adx, latest_plus_di, latest_minus_di
            )
            
            result["adx"] = {
                "current": round(latest_adx, 2) if latest_adx else None,
                "plus_di": round(latest_plus_di, 2) if latest_plus_di else None,
                "minus_di": round(latest_minus_di, 2) if latest_minus_di else None,
                **adx_interpretation
            }
        
        # 3. 线性回归分析
        lr_result = self.lr_analyzer.linear_regression(closes)
        result["linear_regression"] = {
            "slope": lr_result["slope"],
            "intercept": lr_result["intercept"],
            "r_squared": lr_result["r_squared"],
            "trend_interpretation": "上升" if lr_result["slope"] > 0 else "下降"
        }
        
        # 预测未来价格
        predictions = self.lr_analyzer.predict_next(closes, 5)
        result["linear_regression"]["predictions"] = predictions
        
        # 4. 生成综合信号
        result["signals"] = self._generate_signals(result)
        
        # 5. 总结
        result["summary"] = self._generate_summary(result)
        
        # 保存报告
        self._save_report(result, symbol)
        self._log_analysis(symbol, len(candles), success=True)
        
        return result
    
    def _generate_signals(self, analysis: Dict) -> Dict:
        """生成交易信号"""
        signals = {
            "overall": "neutral",
            "confidence": 0,
            "recommendations": []
        }
        
        # 综合判断
        bullish_count = 0
        bearish_count = 0
        
        # 时间框架信号
        for tf_key, tf_data in analysis.get("timeframes", {}).items():
            detected = tf_data.get("detected_trend", "unknown")
            if detected == "up":
                bullish_count += 1
            elif detected == "down":
                bearish_count += 1
        
        # ADX 信号
        adx_data = analysis.get("adx", {})
        if adx_data.get("signal") == "buy":
            bullish_count += 1
        elif adx_data.get("signal") == "sell":
            bearish_count += 1
        
        # 线性回归信号
        lr_data = analysis.get("linear_regression", {})
        if lr_data.get("slope", 0) > 0.1:
            bullish_count += 1
        elif lr_data.get("slope", 0) < -0.1:
            bearish_count += 1
        
        # 综合判断
        total = bullish_count + bearish_count
        if total > 0:
            confidence = max(bullish_count, bearish_count) / total
            
            if bullish_count > bearish_count:
                signals["overall"] = "bullish"
                signals["confidence"] = round(confidence * 100, 1)
                signals["recommendations"].append("短线可能继续上涨")
            elif bearish_count > bullish_count:
                signals["overall"] = "bearish"
                signals["confidence"] = round(confidence * 100, 1)
                signals["recommendations"].append("短线可能继续下跌")
            else:
                signals["overall"] = "neutral"
                signals["confidence"] = 50
                signals["recommendations"].append("市场方向不明，建议观望")
        
        return signals
    
    def _generate_summary(self, analysis: Dict) -> Dict:
        """生成分析总结"""
        summary = {
            "dominant_trend": "unknown",
            "trend_strength": "unknown",
            "outlook": "需要更多数据"
        }
        
        # 确定主导趋势
        trends = []
        for tf_data in analysis.get("timeframes", {}).values():
            trend = tf_data.get("detected_trend", "unknown")
            if trend != "unknown":
                trends.append(trend)
        
        if trends:
            if trends.count("up") > len(trends) / 2:
                summary["dominant_trend"] = "上升"
            elif trends.count("down") > len(trends) / 2:
                summary["dominant_trend"] = "下降"
            else:
                summary["dominant_trend"] = "横盘"
        
        # 趋势强度
        adx_data = analysis.get("adx", {})
        strength = adx_data.get("trend_strength", "unknown")
        summary["trend_strength"] = strength
        
        # 展望
        dominant = summary["dominant_trend"]
        if dominant == "上升":
            summary["outlook"] = "多方占优，关注支撑位"
        elif dominant == "下降":
            summary["outlook"] = "空方占优，关注阻力位"
        else:
            summary["outlook"] = "多空博弈，等待突破方向"
        
        return summary
    
    def _save_report(self, report: Dict, symbol: str):
        """保存分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_trend_{timestamp}.json"
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
        output.append(" " * 18 + "Trend Analyzer Status")
        output.append("=" * 70)
        
        output.append(f"\n[Timeframes]")
        for key, config in self.detector.TIMEFRAMES.items():
            output.append(f"  {config['name']}: {config['period']} 周期")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Analyses: {stats['total_analyses']}")
        output.append(f"  Successful:     {stats['successful']}")
        output.append(f"  Failed:         {stats['failed']}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def generate_test_data(num_candles: int = 100, trend: str = "up") -> List[Dict]:
    """生成测试 K 线数据"""
    import random
    
    candles = []
    price = 100.0
    
    for i in range(num_candles):
        if trend == "up":
            change = random.uniform(-0.02, 0.04)
        elif trend == "down":
            change = random.uniform(-0.04, 0.02)
        else:
            change = random.uniform(-0.02, 0.02)
        
        open_price = price
        close_price = price * (1 + change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.015))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.015))
        
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
    print(" " * 18 + "SA-007: Trend Analysis")
    print("=" * 70)
    
    analyzer = TrendAnalyzer()
    
    # 显示状态
    print(analyzer.display_status())
    
    # 测试趋势分析
    print("\n[Test 1] Uptrend Analysis")
    print("-" * 70)
    up_candles = generate_test_data(100, "up")
    up_result = analyzer.analyze_trend("TEST_UP", up_candles)
    
    print(f"Symbol: {up_result['symbol']}")
    print(f"Candles: {up_result['candle_count']}")
    
    print("\n[Timeframe Trends]")
    for tf, data in up_result['timeframes'].items():
        print(f"  {data['name']}: {data['detected_trend']} (slope: {data['slope']})")
    
    print(f"\n[ADX]")
    adx = up_result.get('adx', {})
    print(f"  ADX: {adx.get('current', 'N/A')}")
    print(f"  +DI: {adx.get('plus_di', 'N/A')}")
    print(f"  -DI: {adx.get('minus_di', 'N/A')}")
    print(f"  Interpretation: {adx.get('description', 'N/A')}")
    
    print(f"\n[Linear Regression]")
    lr = up_result.get('linear_regression', {})
    print(f"  Slope: {lr.get('slope', 0)}")
    print(f"  R²: {lr.get('r_squared', 0)}")
    print(f"  Predictions: {lr.get('predictions', [])}")
    
    print(f"\n[Signals]")
    signals = up_result.get('signals', {})
    print(f"  Overall: {signals.get('overall', 'N/A')}")
    print(f"  Confidence: {signals.get('confidence', 0)}%")
    
    print(f"\n[Summary]")
    summary = up_result.get('summary', {})
    print(f"  Dominant Trend: {summary.get('dominant_trend', 'N/A')}")
    print(f"  Trend Strength: {summary.get('trend_strength', 'N/A')}")
    print(f"  Outlook: {summary.get('outlook', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("\n[Test 2] Downtrend Analysis")
    print("-" * 70)
    down_candles = generate_test_data(100, "down")
    down_result = analyzer.analyze_trend("TEST_DOWN", down_candles)
    
    print(f"Summary: {down_result['summary']}")
    
    print("\n" + "=" * 70)
    print("\n[Test 3] Sideways Analysis")
    print("-" * 70)
    side_candles = generate_test_data(100, "sideways")
    side_result = analyzer.analyze_trend("TEST_SIDE", side_candles)
    
    print(f"Summary: {side_result['summary']}")
    
    print("\n" + "=" * 70)
    print("\nUsage: py sa_007_trend_analysis.py --test")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        main()
    else:
        print("SA-007: Trend Analysis Tool")
        print("Usage: py sa_007_trend_analysis.py --test")
