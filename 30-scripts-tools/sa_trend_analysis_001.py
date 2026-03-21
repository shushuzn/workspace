import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-007: Trend Analysis - 趋势分析引擎

功能：
1. 移动平均线趋势分析（MA 方向、斜率）
2. MACD 趋势分析（金叉/死叉、背离）
3. 趋势强度指标（ADX）
4. 趋势阶段识别（上涨/下跌/盘整）
5. 趋势延续概率

依赖：
- SA-002: Historical data downloader
- SA-005: Technical indicator calculator

作者：Claw (AI Agent)
创建日期：2026-03-20
版本：1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math


class TrendAnalyzer:
    """趋势分析引擎"""
    
    def __init__(self):
        self.cache_dir = Path("60-DATA/stock_trends")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_ma_trend(self, ma_values: List[float], period: int = 5) -> Dict:
        """
        移动平均线趋势分析
        
        Args:
            ma_values: MA 值列表
            period: 分析周期
        
        Returns:
            趋势分析结果
        """
        if len(ma_values) < period * 2:
            return {
                'direction': 'unknown',
                'strength': 0,
                'slope': 0,
                'description': '数据不足'
            }
        
        # 计算斜率（最近 period 个值）
        recent = ma_values[-period:]
        slope = (recent[-1] - recent[0]) / period
        
        # 计算斜率百分比
        avg_ma = sum(recent) / len(recent)
        slope_percent = (slope / avg_ma) * 100 if avg_ma > 0 else 0
        
        # 判断方向
        if slope_percent > 0.5:
            direction = 'upward'
        elif slope_percent < -0.5:
            direction = 'downward'
        else:
            direction = 'flat'
        
        # 计算强度（R 方值简化版）
        r_squared = self._calculate_trend_strength(recent)
        
        return {
            'direction': direction,
            'strength': r_squared,
            'slope': slope,
            'slope_percent': slope_percent,
            'description': f'MA 趋势：{self._direction_cn(direction)} (斜率：{slope_percent:.2f}%)'
        }
    
    def calculate_macd_trend(self, macd_data: List[Dict]) -> Dict:
        """
        MACD 趋势分析
        
        Args:
            macd_data: MACD 数据列表，每个包含 {macd, signal, histogram}
        
        Returns:
            趋势分析结果
        """
        if len(macd_data) < 2:
            return {
                'signal': 'unknown',
                'crossover': None,
                'divergence': 'none',
                'description': '数据不足'
            }
        
        latest = macd_data[-1]
        prev = macd_data[-2]
        
        result = {
            'current_macd': latest['macd'],
            'current_signal': latest['signal'],
            'current_histogram': latest['histogram'],
            'crossover': None,
            'divergence': 'none'
        }
        
        # 检测金叉/死叉
        if prev['macd'] < prev['signal'] and latest['macd'] > latest['signal']:
            result['crossover'] = 'golden_cross'  # 金叉
            result['signal'] = 'bullish'
        elif prev['macd'] > prev['signal'] and latest['macd'] < latest['signal']:
            result['crossover'] = 'death_cross'  # 死叉
            result['signal'] = 'bearish'
        else:
            # 根据 MACD 在信号线上方/下方判断
            if latest['macd'] > latest['signal']:
                result['signal'] = 'bullish'
            else:
                result['signal'] = 'bearish'
        
        # 检测背离（简化版）
        if len(macd_data) >= 5:
            price_trend = self._detect_price_trend(macd_data[-5:])
            macd_trend = self._detect_macd_trend(macd_data[-5:])
            
            if price_trend != macd_trend and price_trend != 'flat':
                result['divergence'] = 'bullish' if price_trend == 'down' else 'bearish'
        
        result['description'] = f'MACD: {self._signal_cn(result["signal"])}'
        if result['crossover']:
            result['description'] += f' - {self._crossover_cn(result["crossover"])}'
        
        return result
    
    def calculate_adx(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict:
        """
        计算 ADX（平均趋向指数）- 趋势强度指标
        
        Args:
            highs: 最高价列表
            lows: 最低价列表
            closes: 收盘价列表
            period: ADX 周期（默认 14）
        
        Returns:
            ADX 分析结果
        """
        if len(highs) < period + 1:
            return {
                'adx': 0,
                'plus_di': 0,
                'minus_di': 0,
                'trend_strength': 'weak',
                'description': '数据不足'
            }
        
        # 计算 TR, +DM, -DM
        tr_list = []
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(highs)):
            # True Range
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
            
            # +DM and -DM
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            
            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
                minus_dm.append(0)
            else:
                plus_dm.append(0)
                minus_dm.append(down_move if down_move > 0 else 0)
        
        # 计算 smoothed values (简化版，用 SMA 代替 Wilder's smoothing)
        def smooth(values, period):
            if len(values) < period:
                return sum(values) / len(values) if values else 0
            return sum(values[-period:]) / period
        
        tr_smooth = smooth(tr_list, period)
        plus_dm_smooth = smooth(plus_dm, period)
        minus_dm_smooth = smooth(minus_dm, period)
        
        # 计算 DI
        plus_di = (plus_dm_smooth / tr_smooth * 100) if tr_smooth > 0 else 0
        minus_di = (minus_dm_smooth / tr_smooth * 100) if tr_smooth > 0 else 0
        
        # 计算 DX and ADX
        if (plus_di + minus_di) > 0:
            dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100
        else:
            dx = 0
        
        # 简化版 ADX（实际应该用更多历史数据）
        adx = dx
        
        # 判断趋势强度
        if adx > 50:
            trend_strength = 'very_strong'
        elif adx > 25:
            trend_strength = 'strong'
        elif adx > 20:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        # 判断趋势方向
        if plus_di > minus_di:
            trend_direction = 'upward'
        else:
            trend_direction = 'downward'
        
        return {
            'adx': round(adx, 2),
            'plus_di': round(plus_di, 2),
            'minus_di': round(minus_di, 2),
            'trend_strength': trend_strength,
            'trend_direction': trend_direction,
            'description': f'ADX: {adx:.2f} ({self._strength_cn(trend_strength)}) - {self._direction_cn(trend_direction)}'
        }
    
    def identify_trend_stage(self, prices: List[float], ma_short: List[float], ma_long: List[float]) -> Dict:
        """
        识别趋势阶段
        
        Args:
            prices: 价格列表
            ma_short: 短期 MA（如 MA10）
            ma_long: 长期 MA（如 MA50）
        
        Returns:
            趋势阶段分析
        """
        if len(prices) < 50 or len(ma_short) < 50 or len(ma_long) < 50:
            return {
                'stage': 'unknown',
                'confidence': 0,
                'description': '数据不足'
            }
        
        latest_price = prices[-1]
        latest_ma_short = ma_short[-1]
        latest_ma_long = ma_long[-1]
        
        # 判断阶段
        if latest_ma_short > latest_ma_long * 1.05:
            if latest_price > latest_ma_short:
                stage = 'strong_uptrend'  # 强势上涨
            else:
                stage = 'uptrend_pullback'  # 上涨回调
        elif latest_ma_short < latest_ma_long * 0.95:
            if latest_price < latest_ma_short:
                stage = 'strong_downtrend'  # 强势下跌
            else:
                stage = 'downtrend_bounce'  # 下跌反弹
        else:
            # MA 粘合，判断盘整
            volatility = (max(prices[-20:]) - min(prices[-20:])) / min(prices[-20:])
            if volatility < 0.15:
                stage = 'consolidation'  # 盘整
            else:
                stage = 'transition'  # 过渡期
        
        # 计算置信度
        confidence = min(1.0, abs(latest_ma_short - latest_ma_long) / latest_ma_long * 20)
        
        return {
            'stage': stage,
            'confidence': round(confidence, 2),
            'price': latest_price,
            'ma_short': latest_ma_short,
            'ma_long': latest_ma_long,
            'description': f'趋势阶段：{self._stage_cn(stage)} (置信度：{confidence:.0%})'
        }
    
    def calculate_trend_continuation_probability(self, prices: List[float], 
                                                  ma_values: List[float], 
                                                  volume: List[float]) -> Dict:
        """
        计算趋势延续概率
        
        Args:
            prices: 价格列表
            ma_values: MA 值列表
            volume: 成交量列表
        
        Returns:
            延续概率分析
        """
        if len(prices) < 20:
            return {
                'continuation_probability': 0.5,
                'factors': [],
                'description': '数据不足'
            }
        
        factors = []
        probability = 0.5  # 基础概率 50%
        
        # 因子 1: 价格在 MA 上方/下方
        if prices[-1] > ma_values[-1]:
            factors.append({'name': 'price_above_ma', 'impact': 0.1, 'direction': 'bullish'})
            probability += 0.1
        else:
            factors.append({'name': 'price_below_ma', 'impact': -0.1, 'direction': 'bearish'})
            probability -= 0.1
        
        # 因子 2: MA 斜率
        ma_slope = (ma_values[-1] - ma_values[-5]) / ma_values[-5] if ma_values[-5] > 0 else 0
        if ma_slope > 0.01:
            factors.append({'name': 'ma_upward', 'impact': 0.15, 'direction': 'bullish'})
            probability += 0.15
        elif ma_slope < -0.01:
            factors.append({'name': 'ma_downward', 'impact': -0.15, 'direction': 'bearish'})
            probability -= 0.15
        
        # 因子 3: 成交量确认
        avg_volume = sum(volume[-20:]) / 20
        recent_volume = sum(volume[-5:]) / 5
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.2:
            factors.append({'name': 'volume_increase', 'impact': 0.1, 'direction': 'confirm'})
            probability += 0.1
        elif volume_ratio < 0.8:
            factors.append({'name': 'volume_decrease', 'impact': -0.1, 'direction': 'weak'})
            probability -= 0.1
        
        # 限制概率在 0-1 范围
        probability = max(0, min(1, probability))
        
        # 判断延续方向
        if probability > 0.6:
            continuation_direction = 'upward'
        elif probability < 0.4:
            continuation_direction = 'downward'
        else:
            continuation_direction = 'uncertain'
        
        return {
            'continuation_probability': round(probability, 2),
            'continuation_direction': continuation_direction,
            'factors': factors,
            'description': f'趋势延续概率：{probability:.0%} ({self._direction_cn(continuation_direction)})'
        }
    
    def analyze_all_trends(self, candles: List[Dict]) -> Dict:
        """
        综合分析所有趋势指标
        
        Args:
            candles: K 线数据列表
        
        Returns:
            完整趋势分析报告
        """
        result = {
            'symbol': 'TEST',
            'analysis_date': datetime.now().isoformat(),
            'candle_count': len(candles),
            'ma_trend': {},
            'macd_trend': {},
            'adx': {},
            'trend_stage': {},
            'continuation_probability': {},
            'summary': {
                'overall_trend': 'neutral',
                'confidence': 0,
                'recommendation': 'hold'
            }
        }
        
        # 提取数据
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        volumes = [c['volume'] for c in candles]
        
        # 计算 MA（简化版，实际应该从 SA-005 获取）
        ma5 = self._calculate_ma(closes, 5)
        ma10 = self._calculate_ma(closes, 10)
        ma20 = self._calculate_ma(closes, 20)
        ma50 = self._calculate_ma(closes, 50)
        
        # 1. MA 趋势分析
        result['ma_trend'] = {
            'ma5': self.calculate_ma_trend(ma5, 5),
            'ma10': self.calculate_ma_trend(ma10, 5),
            'ma20': self.calculate_ma_trend(ma20, 5),
        }
        
        # 2. MACD 趋势分析（简化版）
        macd_data = self._calculate_macd_series(closes)
        result['macd_trend'] = self.calculate_macd_trend(macd_data)
        
        # 3. ADX 趋势强度
        result['adx'] = self.calculate_adx(highs, lows, closes, 14)
        
        # 4. 趋势阶段
        result['trend_stage'] = self.identify_trend_stage(closes, ma10, ma50)
        
        # 5. 延续概率
        result['continuation_probability'] = self.calculate_trend_continuation_probability(
            closes, ma20, volumes
        )
        
        # 6. 综合判断
        result['summary'] = self._synthesize_trend(result)
        
        return result
    
    def save_report(self, report: Dict, symbol: str = 'TEST'):
        """保存趋势分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_trend_{timestamp}.json"
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    # ========== 辅助方法 ==========
    
    def _calculate_ma(self, prices: List[float], period: int) -> List[float]:
        """计算移动平均线"""
        ma = []
        for i in range(len(prices)):
            if i < period - 1:
                ma.append(None)
            else:
                avg = sum(prices[i-period+1:i+1]) / period
                ma.append(avg)
        return ma
    
    def _calculate_macd_series(self, closes: List[float]) -> List[Dict]:
        """计算 MACD 序列（简化版）"""
        ema12 = self._calculate_ema(closes, 12)
        ema26 = self._calculate_ema(closes, 26)
        
        macd_data = []
        for i in range(len(closes)):
            if ema12[i] is not None and ema26[i] is not None:
                macd = ema12[i] - ema26[i]
                signal = macd * 0.9 if i == 0 else macd_data[-1]['signal'] * 0.9 + macd * 0.1
                histogram = macd - signal
                macd_data.append({
                    'macd': macd,
                    'signal': signal,
                    'histogram': histogram
                })
            else:
                macd_data.append({'macd': 0, 'signal': 0, 'histogram': 0})
        
        return macd_data
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """计算指数移动平均"""
        ema = []
        multiplier = 2 / (period + 1)
        
        for i in range(len(prices)):
            if i < period - 1:
                ema.append(None)
            elif i == period - 1:
                avg = sum(prices[:period]) / period
                ema.append(avg)
            else:
                ema.append((prices[i] - ema[i-1]) * multiplier + ema[i-1])
        
        return ema
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """计算趋势强度（R 方简化版）"""
        if len(values) < 2:
            return 0
        
        # 线性回归简化版
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        
        # R 方计算
        y_pred = [y_mean + slope * (i - x_mean) for i in range(n)]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return max(0, min(1, r_squared))
    
    def _detect_price_trend(self, macd_data: List[Dict]) -> str:
        """检测价格趋势（通过 MACD 推断）"""
        if len(macd_data) < 2:
            return 'flat'
        
        trend = macd_data[-1]['macd'] - macd_data[-2]['macd']
        if trend > 0.1:
            return 'up'
        elif trend < -0.1:
            return 'down'
        return 'flat'
    
    def _detect_macd_trend(self, macd_data: List[Dict]) -> str:
        """检测 MACD 趋势"""
        return self._detect_price_trend(macd_data)
    
    def _synthesize_trend(self, result: Dict) -> Dict:
        """综合判断趋势"""
        bullish_count = 0
        bearish_count = 0
        
        # MA 趋势
        for ma_key in ['ma5', 'ma10', 'ma20']:
            direction = result['ma_trend'].get(ma_key, {}).get('direction', 'flat')
            if direction == 'upward':
                bullish_count += 1
            elif direction == 'downward':
                bearish_count += 1
        
        # MACD 趋势
        macd_signal = result['macd_trend'].get('signal', 'neutral')
        if macd_signal == 'bullish':
            bullish_count += 2
        elif macd_signal == 'bearish':
            bearish_count += 2
        
        # ADX 趋势方向
        adx_direction = result['adx'].get('trend_direction', 'flat')
        if adx_direction == 'upward':
            bullish_count += 1
        elif adx_direction == 'downward':
            bearish_count += 1
        
        # 综合判断
        if bullish_count > bearish_count + 2:
            overall_trend = 'bullish'
            recommendation = 'buy'
        elif bearish_count > bullish_count + 2:
            overall_trend = 'bearish'
            recommendation = 'sell'
        else:
            overall_trend = 'neutral'
            recommendation = 'hold'
        
        # 置信度
        total_signals = bullish_count + bearish_count
        confidence = max(bullish_count, bearish_count) / total_signals if total_signals > 0 else 0.5
        
        return {
            'overall_trend': overall_trend,
            'confidence': round(confidence, 2),
            'recommendation': recommendation,
            'bullish_signals': bullish_count,
            'bearish_signals': bearish_count,
            'description': f'综合趋势：{self._trend_cn(overall_trend)} - 建议：{self._recommendation_cn(recommendation)}'
        }
    
    # ========== 中文翻译 ==========
    
    def _direction_cn(self, direction: str) -> str:
        mapping = {
            'upward': '上涨',
            'downward': '下跌',
            'flat': '盘整',
            'unknown': '未知'
        }
        return mapping.get(direction, direction)
    
    def _signal_cn(self, signal: str) -> str:
        mapping = {
            'bullish': '看涨',
            'bearish': '看跌',
            'neutral': '中性',
            'unknown': '未知'
        }
        return mapping.get(signal, signal)
    
    def _crossover_cn(self, crossover: str) -> str:
        mapping = {
            'golden_cross': '金叉',
            'death_cross': '死叉'
        }
        return mapping.get(crossover, crossover)
    
    def _strength_cn(self, strength: str) -> str:
        mapping = {
            'very_strong': '极强',
            'strong': '强',
            'moderate': '中等',
            'weak': '弱'
        }
        return mapping.get(strength, strength)
    
    def _stage_cn(self, stage: str) -> str:
        mapping = {
            'strong_uptrend': '强势上涨',
            'uptrend_pullback': '上涨回调',
            'strong_downtrend': '强势下跌',
            'downtrend_bounce': '下跌反弹',
            'consolidation': '盘整',
            'transition': '过渡期',
            'unknown': '未知'
        }
        return mapping.get(stage, stage)
    
    def _trend_cn(self, trend: str) -> str:
        mapping = {
            'bullish': '看涨',
            'bearish': '看跌',
            'neutral': '中性'
        }
        return mapping.get(trend, trend)
    
    def _recommendation_cn(self, rec: str) -> str:
        mapping = {
            'buy': '买入',
            'sell': '卖出',
            'hold': '持有'
        }
        return mapping.get(rec, rec)

    def analyze(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        Unified analyze wrapper for pipeline compatibility.

        Args:
            symbol: Stock symbol
            candles: List of candle data (open, high, low, close, volume)

        Returns:
            Dict with trend analysis results
        """
        result = self.analyze_all_trends(candles)
        result['symbol'] = symbol
        return result


def generate_test_data(num_candles: int = 100) -> List[Dict]:
    """生成测试 K 线数据"""
    import random
    
    candles = []
    price = 100.0
    
    for i in range(num_candles):
        # 创建上涨趋势
        trend = 0.002 * i
        change = random.uniform(-0.03, 0.03) + trend
        open_price = price
        close_price = price * (1 + change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
        
        candles.append({
            'date': f'2026-01-{i+1:02d}',
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(1000000, 10000000)
        })
        
        price = close_price
    
    return candles


logging.basicConfig(level=logging.INFO)
def main():
    """主函数"""
    print("=" * 70)
    print(" " * 25 + "SA-007: Trend Analysis")
    print("=" * 70)
    
    analyzer = TrendAnalyzer()
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        candles = generate_test_data(100)
        print(f"  Generated {len(candles)} candles")
        print(f"  Price range: {min(c['low'] for c in candles):.2f} - {max(c['high'] for c in candles):.2f}")
        
        print("\n[Test 2] MA Trend Analysis")
        print("-" * 70)
        closes = [c['close'] for c in candles]
        ma20 = analyzer._calculate_ma(closes, 20)
        ma20_valid = [m for m in ma20 if m is not None]
        ma_trend = analyzer.calculate_ma_trend(ma20_valid, 5)
        print(f"  {ma_trend['description']}")
        
        print("\n[Test 3] MACD Trend Analysis")
        print("-" * 70)
        macd_data = analyzer._calculate_macd_series(closes)
        macd_trend = analyzer.calculate_macd_trend(macd_data)
        print(f"  {macd_trend['description']}")
        if macd_trend.get('crossover'):
            print(f"  Crossover: {macd_trend['crossover']}")
        
        print("\n[Test 4] ADX Trend Strength")
        print("-" * 70)
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        adx = analyzer.calculate_adx(highs, lows, closes, 14)
        print(f"  {adx['description']}")
        
        print("\n[Test 5] Trend Stage Identification")
        print("-" * 70)
        ma10 = analyzer._calculate_ma(closes, 10)
        ma50 = analyzer._calculate_ma(closes, 50)
        ma10_valid = [m for m in ma10 if m is not None]
        ma50_valid = [m for m in ma50 if m is not None]
        stage = analyzer.identify_trend_stage(closes, ma10_valid, ma50_valid)
        print(f"  {stage['description']}")
        
        print("\n[Test 6] Trend Continuation Probability")
        print("-" * 70)
        volumes = [c['volume'] for c in candles]
        continuation = analyzer.calculate_trend_continuation_probability(closes, ma20_valid, volumes)
        print(f"  {continuation['description']}")
        print(f"  Factors: {len(continuation['factors'])}")
        
        print("\n[Test 7] Comprehensive Trend Analysis")
        print("-" * 70)
        all_trends = analyzer.analyze_all_trends(candles)
        summary = all_trends['summary']
        print(f"  Overall Trend: {summary['overall_trend']}")
        print(f"  Confidence: {summary['confidence']:.0%}")
        print(f"  Recommendation: {summary['recommendation']}")
        print(f"  {summary['description']}")
        
        print("\n[Test 8] Save Report")
        print("-" * 70)
        report_path = analyzer.save_report(all_trends, 'TEST')
        print(f"  Report saved to: {report_path}")
        
        print("\n" + "=" * 70)
        print(" SA-007 Trend Analysis test completed")
        print("=" * 70)
    
    else:
        # 正常使用模式
        print("\nUsage: py sa_007_trend_analysis.py --test")
        print("\nFeatures:")
        print("  - MA trend analysis (direction, slope, strength)")
        print("  - MACD trend analysis (golden/death cross, divergence)")
        print("  - ADX trend strength indicator")
        print("  - Trend stage identification")
        print("  - Trend continuation probability")
        print("  - Comprehensive trend summary with recommendation")
        print("  - Auto-save reports to 60-DATA/stock_trends/")


if __name__ == '__main__':
    main()
