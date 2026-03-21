import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-006: Pattern Recognition - 形态识别引擎

功能：
1. K 线形态识别（锤子线、十字星、吞没形态等）
2. 趋势形态识别（头肩顶/底、双顶/底、三角形、旗形等）
3. 形态信号生成（买入/卖出/观望）
4. 形态置信度评分
5. 形态历史记录

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


class CandlestickPattern:
    """单 K 线形态识别"""
    
    @staticmethod
    def is_hammer(open_price: float, high: float, low: float, close: float) -> bool:
        """锤子线 - 底部反转信号"""
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        if body <= 0:
            return False
        
        return (lower_shadow >= 2 * body and 
                upper_shadow <= body * 0.5 and
                lower_shadow >= (high - low) * 0.6)
    
    @staticmethod
    def is_shooting_star(open_price: float, high: float, low: float, close: float) -> bool:
        """流星线 - 顶部反转信号"""
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        if body <= 0:
            return False
        
        return (upper_shadow >= 2 * body and 
                lower_shadow <= body * 0.5 and
                upper_shadow >= (high - low) * 0.6)
    
    @staticmethod
    def is_doji(open_price: float, high: float, low: float, close: float, threshold: float = 0.001) -> bool:
        """十字星 - 市场犹豫"""
        body = abs(close - open_price)
        range_size = high - low
        
        if range_size <= 0:
            return False
        
        return body / range_size <= threshold
    
    @staticmethod
    def is_marubozu(open_price: float, high: float, low: float, close: float) -> bool:
        """光头光脚 - 强势信号"""
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        if body <= 0:
            return False
        
        return (upper_shadow <= body * 0.1 and 
                lower_shadow <= body * 0.1)


class PatternRecognition:
    """形态识别引擎"""
    
    def __init__(self):
        self.candlestick = CandlestickPattern()
        self.patterns_found: List[Dict] = []
        self.cache_dir = Path("60-DATA/stock_patterns")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def detect_candlestick_patterns(self, candles: List[Dict]) -> List[Dict]:
        """
        检测 K 线形态
        
        Args:
            candles: K 线数据列表，每个包含 {open, high, low, close, volume, date}
        
        Returns:
            检测到的形态列表
        """
        patterns = []
        
        for i, candle in enumerate(candles):
            o = candle['open']
            h = candle['high']
            l = candle['low']
            c = candle['close']
            
            pattern = {
                'index': i,
                'date': candle.get('date', f'candle_{i}'),
                'type': 'candlestick',
                'signals': []
            }
            
            # 检测各种 K 线形态
            if self.candlestick.is_hammer(o, h, l, c):
                pattern['signals'].append({
                    'name': '锤子线',
                    'signal': 'bullish',
                    'strength': 'medium',
                    'description': '底部反转信号，可能有上涨'
                })
            
            if self.candlestick.is_shooting_star(o, h, l, c):
                pattern['signals'].append({
                    'name': '流星线',
                    'signal': 'bearish',
                    'strength': 'medium',
                    'description': '顶部反转信号，可能下跌'
                })
            
            if self.candlestick.is_doji(o, h, l, c):
                pattern['signals'].append({
                    'name': '十字星',
                    'signal': 'neutral',
                    'strength': 'weak',
                    'description': '市场犹豫，等待方向'
                })
            
            if self.candlestick.is_marubozu(o, h, l, c):
                signal = 'bullish' if c > o else 'bearish'
                pattern['signals'].append({
                    'name': '光头光脚',
                    'signal': signal,
                    'strength': 'strong',
                    'description': f'强势{"上涨" if signal == "bullish" else "下跌"}信号'
                })
            
            if pattern['signals']:
                patterns.append(pattern)
        
        return patterns
    
    def detect_engulfing_pattern(self, candles: List[Dict], index: int) -> Optional[Dict]:
        """
        检测吞没形态（需要至少 2 根 K 线）
        
        Args:
            candles: K 线数据列表
            index: 当前 K 线索引
        
        Returns:
            吞没形态信息或 None
        """
        if index < 1:
            return None
        
        prev = candles[index - 1]
        curr = candles[index]
        
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        
        #  bullish engulfing: 前阴后阳，后包前
        if prev_body < 0 and curr_body > 0:
            if (curr['open'] < prev['close'] and 
                curr['close'] > prev['open']):
                return {
                    'index': index,
                    'date': curr.get('date', f'candle_{index}'),
                    'type': 'candlestick',
                    'name': '看涨吞没',
                    'signal': 'bullish',
                    'strength': 'strong',
                    'description': '强势底部反转信号'
                }
        
        # bearish engulfing: 前阳后阴，后包前
        if prev_body > 0 and curr_body < 0:
            if (curr['open'] > prev['close'] and 
                curr['close'] < prev['open']):
                return {
                    'index': index,
                    'date': curr.get('date', f'candle_{index}'),
                    'type': 'candlestick',
                    'name': '看跌吞没',
                    'signal': 'bearish',
                    'strength': 'strong',
                    'description': '强势顶部反转信号'
                }
        
        return None
    
    def detect_head_and_shoulders(self, candles: List[Dict]) -> Optional[Dict]:
        """
        检测头肩顶/底形态（简化版）
        
        Args:
            candles: K 线数据列表（至少需要 50 根）
        
        Returns:
            头肩形态信息或 None
        """
        if len(candles) < 50:
            return None
        
        # 寻找局部高点/低点
        peaks = []
        troughs = []
        
        for i in range(5, len(candles) - 5):
            window_high = max(c['high'] for c in candles[i-5:i+6])
            window_low = min(c['low'] for c in candles[i-5:i+6])
            
            if candles[i]['high'] == window_high:
                peaks.append((i, candles[i]['high']))
            if candles[i]['low'] == window_low:
                troughs.append((i, candles[i]['low']))
        
        # 检测头肩顶（3 个峰值，中间最高）
        if len(peaks) >= 3:
            for i in range(1, len(peaks) - 1):
                left_shoulder = peaks[i-1][1]
                head = peaks[i][1]
                right_shoulder = peaks[i+1][1]
                
                # 头肩顶条件：中间高，两边低且接近
                if (head > left_shoulder * 1.02 and 
                    head > right_shoulder * 1.02 and
                    abs(left_shoulder - right_shoulder) / head < 0.05):
                    return {
                        'type': 'trend',
                        'name': '头肩顶',
                        'signal': 'bearish',
                        'strength': 'very_strong',
                        'peak_index': peaks[i][0],
                        'description': '经典顶部反转形态，强烈看跌信号',
                        'confidence': 0.85
                    }
        
        # 检测头肩底（3 个谷值，中间最低）
        if len(troughs) >= 3:
            for i in range(1, len(troughs) - 1):
                left_shoulder = troughs[i-1][1]
                head = troughs[i][1]
                right_shoulder = troughs[i+1][1]
                
                if (head < left_shoulder * 0.98 and 
                    head < right_shoulder * 0.98 and
                    abs(left_shoulder - right_shoulder) / head < 0.05):
                    return {
                        'type': 'trend',
                        'name': '头肩底',
                        'signal': 'bullish',
                        'strength': 'very_strong',
                        'trough_index': troughs[i][0],
                        'description': '经典底部反转形态，强烈看涨信号',
                        'confidence': 0.85
                    }
        
        return None
    
    def detect_double_top_bottom(self, candles: List[Dict]) -> Optional[Dict]:
        """
        检测双顶/双底形态
        
        Args:
            candles: K 线数据列表
        
        Returns:
            双顶/底形态信息或 None
        """
        if len(candles) < 30:
            return None
        
        peaks = []
        troughs = []
        
        for i in range(3, len(candles) - 3):
            window_high = max(c['high'] for c in candles[i-3:i+4])
            window_low = min(c['low'] for c in candles[i-3:i+4])
            
            if candles[i]['high'] == window_high:
                peaks.append((i, candles[i]['high']))
            if candles[i]['low'] == window_low:
                troughs.append((i, candles[i]['low']))
        
        # 检测双顶（M 顶）
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                peak1 = peaks[i][1]
                peak2 = peaks[i+1][1]
                
                if abs(peak1 - peak2) / peak1 < 0.03:  # 相差<3%
                    return {
                        'type': 'trend',
                        'name': '双顶 (M 顶)',
                        'signal': 'bearish',
                        'strength': 'strong',
                        'peak_indices': [peaks[i][0], peaks[i+1][0]],
                        'description': '顶部双重阻力，看跌信号',
                        'confidence': 0.75
                    }
        
        # 检测双底（W 底）
        if len(troughs) >= 2:
            for i in range(len(troughs) - 1):
                trough1 = troughs[i][1]
                trough2 = troughs[i+1][1]
                
                if abs(trough1 - trough2) / trough1 < 0.03:
                    return {
                        'type': 'trend',
                        'name': '双底 (W 底)',
                        'signal': 'bullish',
                        'strength': 'strong',
                        'trough_indices': [troughs[i][0], troughs[i+1][0]],
                        'description': '底部双重支撑，看涨信号',
                        'confidence': 0.75
                    }
        
        return None
    
    def detect_triangle(self, candles: List[Dict]) -> Optional[Dict]:
        """
        检测三角形整理形态（对称/上升/下降）
        
        Args:
            candles: K 线数据列表
        
        Returns:
            三角形形态信息或 None
        """
        if len(candles) < 20:
            return None
        
        # 简化检测：波动幅度逐渐收窄
        recent_volatility = []
        window_size = 5
        
        for i in range(window_size, len(candles), window_size):
            window = candles[i-window_size:i]
            high = max(c['high'] for c in window)
            low = min(c['low'] for c in window)
            volatility = (high - low) / low
            recent_volatility.append(volatility)
        
        if len(recent_volatility) >= 3:
            # 检查波动是否递减
            is_decreasing = all(
                recent_volatility[i] > recent_volatility[i+1] * 1.1
                for i in range(len(recent_volatility) - 1)
            )
            
            if is_decreasing:
                return {
                    'type': 'trend',
                    'name': '三角形整理',
                    'signal': 'neutral',
                    'strength': 'medium',
                    'description': '波动收窄，等待突破方向',
                    'confidence': 0.65
                }
        
        return None
    
    def analyze_all_patterns(self, candles: List[Dict]) -> Dict:
        """
        综合分析所有形态
        
        Args:
            candles: K 线数据列表
        
        Returns:
            形态分析报告
        """
        results = {
            'symbol': 'TEST',
            'analysis_date': datetime.now().isoformat(),
            'candle_count': len(candles),
            'candlestick_patterns': [],
            'trend_patterns': [],
            'summary': {
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'dominant_signal': 'neutral',
                'confidence': 0.0
            }
        }
        
        # 1. K 线形态
        candlestick_patterns = self.detect_candlestick_patterns(candles)
        results['candlestick_patterns'] = candlestick_patterns[-10:]  # 最近 10 个
        
        # 检测吞没形态
        for i in range(len(candles)):
            engulfing = self.detect_engulfing_pattern(candles, i)
            if engulfing:
                results['candlestick_patterns'].append(engulfing)
        
        # 2. 趋势形态
        head_shoulders = self.detect_head_and_shoulders(candles)
        if head_shoulders:
            results['trend_patterns'].append(head_shoulders)
        
        double_top_bottom = self.detect_double_top_bottom(candles)
        if double_top_bottom:
            results['trend_patterns'].append(double_top_bottom)
        
        triangle = self.detect_triangle(candles)
        if triangle:
            results['trend_patterns'].append(triangle)
        
        # 3. 统计信号
        all_signals = []
        for p in results['candlestick_patterns']:
            for s in p.get('signals', []):
                all_signals.append(s['signal'])
        for p in results['trend_patterns']:
            all_signals.append(p['signal'])
        
        results['summary']['bullish_count'] = all_signals.count('bullish')
        results['summary']['bearish_count'] = all_signals.count('bearish')
        results['summary']['neutral_count'] = all_signals.count('neutral')
        
        # 确定主导信号
        if results['summary']['bullish_count'] > results['summary']['bearish_count']:
            results['summary']['dominant_signal'] = 'bullish'
        elif results['summary']['bearish_count'] > results['summary']['bullish_count']:
            results['summary']['dominant_signal'] = 'bearish'
        
        # 计算置信度
        total_signals = len(all_signals)
        if total_signals > 0:
            results['summary']['confidence'] = min(1.0, total_signals / 10.0)
        
        return results
    
    def save_report(self, report: Dict, symbol: str = 'TEST'):
        """保存形态分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_pattern_{timestamp}.json"
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath


def generate_test_data(num_candles: int = 100) -> List[Dict]:
    """生成测试 K 线数据"""
    import random
    
    candles = []
    price = 100.0
    
    for i in range(num_candles):
        change = random.uniform(-0.05, 0.05)
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
    print(" " * 20 + "SA-006: Pattern Recognition")
    print("=" * 70)
    
    engine = PatternRecognition()
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        candles = generate_test_data(100)
        print(f"  Generated {len(candles)} candles")
        print(f"  Price range: {min(c['low'] for c in candles):.2f} - {max(c['high'] for c in candles):.2f}")
        
        print("\n[Test 2] Detect Candlestick Patterns")
        print("-" * 70)
        patterns = engine.detect_candlestick_patterns(candles)
        print(f"  Found {len(patterns)} candlestick patterns")
        for p in patterns[:5]:
            print(f"    - {p['date']}: {[s['name'] for s in p['signals']]}")
        
        print("\n[Test 3] Detect Engulfing Patterns")
        print("-" * 70)
        engulfing_count = 0
        for i in range(len(candles)):
            result = engine.detect_engulfing_pattern(candles, i)
            if result:
                print(f"  {result['date']}: {result['name']} ({result['signal']})")
                engulfing_count += 1
        if engulfing_count == 0:
            print("  No engulfing patterns found in test data")
        
        print("\n[Test 4] Detect Trend Patterns")
        print("-" * 70)
        all_patterns = engine.analyze_all_patterns(candles)
        
        print(f"  Trend patterns found: {len(all_patterns['trend_patterns'])}")
        for p in all_patterns['trend_patterns']:
            print(f"    - {p['name']}: {p['signal']} (confidence: {p.get('confidence', 0):.2f})")
        
        print("\n[Test 5] Pattern Summary")
        print("-" * 70)
        summary = all_patterns['summary']
        print(f"  Bullish signals: {summary['bullish_count']}")
        print(f"  Bearish signals: {summary['bearish_count']}")
        print(f"  Neutral signals: {summary['neutral_count']}")
        print(f"  Dominant signal: {summary['dominant_signal']}")
        print(f"  Confidence: {summary['confidence']:.2f}")
        
        print("\n[Test 6] Save Report")
        print("-" * 70)
        report_path = engine.save_report(all_patterns, 'TEST')
        print(f"  Report saved to: {report_path}")
        
        print("\n" + "=" * 70)
        print(" SA-006 Pattern Recognition test completed")
        print("=" * 70)
    
    else:
        # 正常使用模式
        print("\nUsage: py sa_006_pattern_recognition.py --test")
        print("\nFeatures:")
        print("  - Candlestick patterns (Hammer, Shooting Star, Doji, Marubozu)")
        print("  - Engulfing patterns (Bullish/Bearish)")
        print("  - Trend patterns (Head & Shoulders, Double Top/Bottom, Triangle)")
        print("  - Signal summary with confidence score")
        print("  - Auto-save reports to 60-DATA/stock_patterns/")


if __name__ == '__main__':
    main()
