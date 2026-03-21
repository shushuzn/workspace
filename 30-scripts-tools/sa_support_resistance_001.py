import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-008: Support & Resistance - 支撑阻力分析引擎

功能：
1. 自动识别支撑位和阻力位
2. 心理关口检测（整数位）
3. 前高/前低识别
4. 成交密集区分析
5. 支撑/阻力强度评分
6. 突破信号检测

依赖：
- SA-002: Historical data downloader

作者：Claw (AI Agent)
创建日期：2026-03-20
版本：1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter
import math


class SupportResistanceAnalyzer:
    """支撑阻力分析引擎"""
    
    def __init__(self):
        self.cache_dir = Path("60-DATA/stock_sr")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def identify_pivot_points(self, candles: List[Dict], window: int = 5) -> List[Dict]:
        """
        识别高低点（枢轴点）
        
        Args:
            candles: K 线数据列表
            window: 检测窗口大小
        
        Returns:
            枢轴点列表
        """
        pivots = []
        
        for i in range(window, len(candles) - window):
            # 检测局部高点
            high = candles[i]['high']
            is_high = all(candles[i-j]['high'] < high for j in range(1, window+1)) and \
                      all(candles[i+j]['high'] < high for j in range(1, window+1))
            
            if is_high:
                pivots.append({
                    'index': i,
                    'type': 'high',
                    'price': high,
                    'date': candles[i].get('date', f'candle_{i}')
                })
            
            # 检测局部低点
            low = candles[i]['low']
            is_low = all(candles[i-j]['low'] > low for j in range(1, window+1)) and \
                     all(candles[i+j]['low'] > low for j in range(1, window+1))
            
            if is_low:
                pivots.append({
                    'index': i,
                    'type': 'low',
                    'price': low,
                    'date': candles[i].get('date', f'candle_{i}')
                })
        
        return pivots
    
    def identify_support_resistance(self, candles: List[Dict], 
                                     pivots: List[Dict] = None) -> Dict:
        """
        识别支撑位和阻力位
        
        Args:
            candles: K 线数据列表
            pivots: 枢轴点列表（可选，不提供则自动计算）
        
        Returns:
            支撑阻力分析结果
        """
        if not pivots:
            pivots = self.identify_pivot_points(candles, window=5)
        
        # 分离高低点
        highs = [p for p in pivots if p['type'] == 'high']
        lows = [p for p in pivots if p['type'] == 'low']
        
        # 聚类分析（简化版：价格接近的归为一组）
        def cluster_prices(points: List[Dict], tolerance: float = 0.02) -> List[Dict]:
            if not points:
                return []
            
            clusters = []
            sorted_points = sorted(points, key=lambda x: x['price'])
            
            current_cluster = {
                'price': sorted_points[0]['price'],
                'touches': [sorted_points[0]],
                'strength': 1
            }
            
            for point in sorted_points[1:]:
                price_ratio = point['price'] / current_cluster['price']
                if abs(price_ratio - 1) < tolerance:
                    # 归入当前聚类
                    current_cluster['touches'].append(point)
                    current_cluster['strength'] = len(current_cluster['touches'])
                    # 更新中心价格
                    current_cluster['price'] = sum(t['price'] for t in current_cluster['touches']) / len(current_cluster['touches'])
                else:
                    # 新建聚类
                    clusters.append(current_cluster)
                    current_cluster = {
                        'price': point['price'],
                        'touches': [point],
                        'strength': 1
                    }
            
            clusters.append(current_cluster)
            return clusters
        
        resistance_clusters = cluster_prices(highs)
        support_clusters = cluster_prices(lows)
        
        # 排序
        resistance_clusters.sort(key=lambda x: x['price'], reverse=True)
        support_clusters.sort(key=lambda x: x['price'])
        
        # 转换为标准格式
        resistances = []
        for i, cluster in enumerate(resistance_clusters[:5]):  # 取前 5 个阻力位
            resistances.append({
                'level': round(cluster['price'], 2),
                'strength': cluster['strength'],
                'touches': len(cluster['touches']),
                'type': 'resistance',
                'rank': i + 1
            })
        
        supports = []
        for i, cluster in enumerate(support_clusters[:5]):  # 取前 5 个支撑位
            supports.append({
                'level': round(cluster['price'], 2),
                'strength': cluster['strength'],
                'touches': len(cluster['touches']),
                'type': 'support',
                'rank': i + 1
            })
        
        return {
            'supports': supports,
            'resistances': resistances,
            'current_price': candles[-1]['close'],
            'description': f'识别到 {len(supports)} 个支撑位，{len(resistances)} 个阻力位'
        }
    
    def identify_psychological_levels(self, current_price: float) -> List[Dict]:
        """
        识别心理关口（整数位）
        
        Args:
            current_price: 当前价格
        
        Returns:
            心理关口列表
        """
        levels = []
        
        # 计算不同级别的整数关口
        for precision in [100, 50, 10, 5, 1, 0.5, 0.1]:
            lower = math.floor(current_price / precision) * precision
            upper = math.ceil(current_price / precision) * precision
            
            if lower > 0 and lower != current_price:
                levels.append({
                    'level': round(lower, 2),
                    'type': 'psychological',
                    'rounding': precision,
                    'distance_percent': abs(lower - current_price) / current_price * 100
                })
            
            if upper != current_price:
                levels.append({
                    'level': round(upper, 2),
                    'type': 'psychological',
                    'rounding': precision,
                    'distance_percent': abs(upper - current_price) / current_price * 100
                })
        
        # 去重并排序
        seen = set()
        unique_levels = []
        for level in sorted(levels, key=lambda x: x['distance_percent']):
            if level['level'] not in seen:
                seen.add(level['level'])
                unique_levels.append(level)
        
        return unique_levels[:10]  # 返回最近的 10 个
    
    def identify_previous_highs_lows(self, candles: List[Dict]) -> Dict:
        """
        识别前高/前低
        
        Args:
            candles: K 线数据列表
        
        Returns:
            前高前低分析
        """
        if len(candles) < 20:
            return {
                'previous_high': None,
                'previous_low': None,
                'description': '数据不足'
            }
        
        # 最近 20 根 K 线的前高前低
        recent = candles[-20:]
        
        previous_high = max(c['high'] for c in recent)
        previous_low = min(c['low'] for c in recent)
        
        # 历史前高前低（全部数据）
        all_time_high = max(c['high'] for c in candles)
        all_time_low = min(c['low'] for c in candles)
        
        current_price = candles[-1]['close']
        
        return {
            'previous_high': {
                'price': previous_high,
                'distance_percent': (previous_high - current_price) / current_price * 100
            },
            'previous_low': {
                'price': previous_low,
                'distance_percent': (current_price - previous_low) / current_price * 100
            },
            'all_time_high': {
                'price': all_time_high,
                'distance_percent': (all_time_high - current_price) / current_price * 100
            },
            'all_time_low': {
                'price': all_time_low,
                'distance_percent': (current_price - all_time_low) / current_price * 100
            },
            'description': f'前高：{previous_high:.2f}, 前低：{previous_low:.2f}'
        }
    
    def analyze_volume_profile(self, candles: List[Dict], num_bins: int = 10) -> Dict:
        """
        分析成交密集区（简化版 Volume Profile）
        
        Args:
            candles: K 线数据列表
            num_bins: 价格区间数量
        
        Returns:
            成交密集区分析
        """
        if len(candles) < 20:
            return {
                'poc': None,
                'value_area': [],
                'description': '数据不足'
            }
        
        # 价格范围
        all_highs = [c['high'] for c in candles]
        all_lows = [c['low'] for c in candles]
        price_range = (max(all_highs) - min(all_lows)) / num_bins
        
        # 统计每个价格区间的成交量
        volume_by_price = Counter()
        for candle in candles:
            avg_price = (candle['high'] + candle['low']) / 2
            bin_index = int((avg_price - min(all_lows)) / price_range)
            bin_index = max(0, min(num_bins - 1, bin_index))
            volume_by_price[bin_index] += candle['volume']
        
        # 找到 POC（Point of Control - 成交量最大的价格区间）
        if volume_by_price:
            poc_bin = max(volume_by_price, key=volume_by_price.get)
            poc_price = min(all_lows) + (poc_bin + 0.5) * price_range
            poc_volume = volume_by_price[poc_bin]
        else:
            poc_price = 0
            poc_volume = 0
        
        # 计算价值区域（70% 成交量区域 - 简化版）
        total_volume = sum(volume_by_price.values())
        sorted_bins = sorted(volume_by_price.items(), key=lambda x: -x[1])
        
        cumulative_volume = 0
        value_area_bins = []
        for bin_idx, volume in sorted_bins:
            cumulative_volume += volume
            value_area_bins.append(bin_idx)
            if cumulative_volume >= total_volume * 0.7:
                break
        
        value_area_low = min(all_lows) + min(value_area_bins) * price_range
        value_area_high = min(all_lows) + (max(value_area_bins) + 1) * price_range
        
        return {
            'poc': {
                'price': round(poc_price, 2),
                'volume': poc_volume
            },
            'value_area': {
                'low': round(value_area_low, 2),
                'high': round(value_area_high, 2)
            },
            'description': f'POC: {poc_price:.2f}, 价值区域：{value_area_low:.2f}-{value_area_high:.2f}'
        }
    
    def detect_breakout(self, candles: List[Dict], 
                         support_resistance: Dict) -> Dict:
        """
        检测突破信号
        
        Args:
            candles: K 线数据列表
            support_resistance: 支撑阻力分析结果
        
        Returns:
            突破信号分析
        """
        current_price = candles[-1]['close']
        prev_close = candles[-2]['close'] if len(candles) > 1 else current_price
        
        breakouts = []
        
        # 检查阻力突破
        for resistance in support_resistance.get('resistances', []):
            level = resistance['level']
            strength = resistance['strength']
            
            # 价格上穿阻力
            if prev_close <= level < current_price:
                breakouts.append({
                    'type': 'resistance_breakout',
                    'level': level,
                    'strength': strength,
                    'direction': 'bullish',
                    'significance': 'high' if strength >= 3 else 'medium'
                })
        
        # 检查支撑跌破
        for support in support_resistance.get('supports', []):
            level = support['level']
            strength = support['strength']
            
            # 价格下破支撑
            if prev_close >= level > current_price:
                breakouts.append({
                    'type': 'support_breakdown',
                    'level': level,
                    'strength': strength,
                    'direction': 'bearish',
                    'significance': 'high' if strength >= 3 else 'medium'
                })
        
        return {
            'breakouts': breakouts,
            'current_price': current_price,
            'description': f'检测到 {len(breakouts)} 个突破信号' if breakouts else '无突破信号'
        }
    
    def analyze_all_sr(self, candles: List[Dict]) -> Dict:
        """
        综合分析所有支撑阻力指标
        
        Args:
            candles: K 线数据列表
        
        Returns:
            完整支撑阻力分析报告
        """
        result = {
            'symbol': 'TEST',
            'analysis_date': datetime.now().isoformat(),
            'candle_count': len(candles),
            'current_price': candles[-1]['close'],
            'support_resistance': {},
            'psychological_levels': [],
            'previous_highs_lows': {},
            'volume_profile': {},
            'breakouts': {},
            'summary': {
                'nearest_support': 0,
                'nearest_resistance': 0,
                'support_distance': 0,
                'resistance_distance': 0,
                'trend': 'neutral',
                'description': ''
            }
        }
        
        # 1. 支撑阻力位
        result['support_resistance'] = self.identify_support_resistance(candles)
        
        # 2. 心理关口
        result['psychological_levels'] = self.identify_psychological_levels(
            result['current_price']
        )
        
        # 3. 前高前低
        result['previous_highs_lows'] = self.identify_previous_highs_lows(candles)
        
        # 4. 成交密集区
        result['volume_profile'] = self.analyze_volume_profile(candles, num_bins=10)
        
        # 5. 突破信号
        result['breakouts'] = self.detect_breakout(
            candles, result['support_resistance']
        )
        
        # 6. 综合判断
        result['summary'] = self._synthesize_sr(result)
        
        return result
    
    def save_report(self, report: Dict, symbol: str = 'TEST'):
        """保存支撑阻力分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_sr_{timestamp}.json"
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    # ========== 辅助方法 ==========
    
    def _synthesize_sr(self, result: Dict) -> Dict:
        """综合判断支撑阻力"""
        current_price = result['current_price']
        supports = result['support_resistance'].get('supports', [])
        resistances = result['support_resistance'].get('resistances', [])
        
        # 最近支撑和阻力
        nearest_support = max([s['level'] for s in supports if s['level'] < current_price], default=0)
        nearest_resistance = min([r['level'] for r in resistances if r['level'] > current_price], default=0)
        
        # 距离百分比
        support_distance = (current_price - nearest_support) / current_price * 100 if nearest_support > 0 else 0
        resistance_distance = (nearest_resistance - current_price) / current_price * 100 if nearest_resistance > 0 else 0
        
        # 判断趋势
        if support_distance < 2 and resistance_distance > 10:
            trend = 'near_support'
            description = f'接近支撑位 {nearest_support:.2f}'
        elif resistance_distance < 2 and support_distance > 10:
            trend = 'near_resistance'
            description = f'接近阻力位 {nearest_resistance:.2f}'
        elif support_distance < 5 and resistance_distance < 5:
            trend = 'consolidation'
            description = f'盘整区间 {nearest_support:.2f}-{nearest_resistance:.2f}'
        else:
            trend = 'neutral'
            description = f'支撑：{nearest_support:.2f}, 阻力：{nearest_resistance:.2f}'
        
        return {
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'support_distance': round(support_distance, 2),
            'resistance_distance': round(resistance_distance, 2),
            'trend': trend,
            'description': description
        }

    def analyze(self, symbol: str, candles: List[Dict]) -> Dict:
        """
        Unified analyze wrapper for pipeline compatibility.

        Args:
            symbol: Stock symbol
            candles: List of candle data (open, high, low, close, volume)

        Returns:
            Dict with support/resistance analysis
        """
        result = self.analyze_all_sr(candles)
        result['symbol'] = symbol
        return result


def generate_test_data(num_candles: int = 100) -> List[Dict]:
    """生成测试 K 线数据（带明显支撑阻力）"""
    import random
    
    candles = []
    price = 100.0
    
    # 创建区间震荡
    support = 95.0
    resistance = 105.0
    
    for i in range(num_candles):
        # 均值回归
        if price > resistance:
            drift = -0.02
        elif price < support:
            drift = 0.02
        else:
            drift = 0
        
        change = random.uniform(-0.03, 0.03) + drift
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
    print(" " * 20 + "SA-008: Support & Resistance")
    print("=" * 70)
    
    analyzer = SupportResistanceAnalyzer()
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        candles = generate_test_data(100)
        print(f"  Generated {len(candles)} candles")
        print(f"  Price range: {min(c['low'] for c in candles):.2f} - {max(c['high'] for c in candles):.2f}")
        
        print("\n[Test 2] Identify Pivot Points")
        print("-" * 70)
        pivots = analyzer.identify_pivot_points(candles, window=5)
        print(f"  Found {len(pivots)} pivot points")
        highs = [p for p in pivots if p['type'] == 'high']
        lows = [p for p in pivots if p['type'] == 'low']
        print(f"  Highs: {len(highs)}, Lows: {len(lows)}")
        
        print("\n[Test 3] Identify Support & Resistance Levels")
        print("-" * 70)
        sr = analyzer.identify_support_resistance(candles, pivots)
        print(f"  {sr['description']}")
        print(f"  Supports: {[s['level'] for s in sr['supports']]}")
        print(f"  Resistances: {[r['level'] for r in sr['resistances']]}")
        
        print("\n[Test 4] Psychological Levels")
        print("-" * 70)
        psych = analyzer.identify_psychological_levels(sr['current_price'])
        print(f"  Nearest 5 psychological levels:")
        for level in psych[:5]:
            print(f"    {level['level']:.2f} (rounding: {level['rounding']})")
        
        print("\n[Test 5] Previous Highs & Lows")
        print("-" * 70)
        phl = analyzer.identify_previous_highs_lows(candles)
        print(f"  {phl['description']}")
        if phl.get('previous_high'):
            print(f"  Previous High: {phl['previous_high']['price']:.2f} ({phl['previous_high']['distance_percent']:.1f}%)")
            print(f"  Previous Low: {phl['previous_low']['price']:.2f} ({phl['previous_low']['distance_percent']:.1f}%)")
        
        print("\n[Test 6] Volume Profile")
        print("-" * 70)
        vp = analyzer.analyze_volume_profile(candles, num_bins=10)
        print(f"  {vp['description']}")
        
        print("\n[Test 7] Breakout Detection")
        print("-" * 70)
        breakouts = analyzer.detect_breakout(candles, sr)
        print(f"  {breakouts['description']}")
        for bo in breakouts.get('breakouts', []):
            print(f"    {bo['type']} at {bo['level']:.2f} ({bo['direction']})")
        
        print("\n[Test 8] Comprehensive Analysis")
        print("-" * 70)
        all_sr = analyzer.analyze_all_sr(candles)
        summary = all_sr['summary']
        print(f"  Current Price: {all_sr['current_price']:.2f}")
        print(f"  Nearest Support: {summary['nearest_support']:.2f} ({summary['support_distance']:.1f}%)")
        print(f"  Nearest Resistance: {summary['nearest_resistance']:.2f} ({summary['resistance_distance']:.1f}%)")
        print(f"  Trend: {summary['trend']}")
        print(f"  {summary['description']}")
        
        print("\n[Test 9] Save Report")
        print("-" * 70)
        report_path = analyzer.save_report(all_sr, 'TEST')
        print(f"  Report saved to: {report_path}")
        
        print("\n" + "=" * 70)
        print(" SA-008 Support & Resistance test completed")
        print("=" * 70)
    
    else:
        # 正常使用模式
        print("\nUsage: py sa_008_support_resistance.py --test")
        print("\nFeatures:")
        print("  - Automatic support/resistance identification")
        print("  - Pivot point detection")
        print("  - Psychological level detection")
        print("  - Previous highs/lows analysis")
        print("  - Volume profile (POC, value area)")
        print("  - Breakout signal detection")
        print("  - Auto-save reports to 60-DATA/stock_sr/")


if __name__ == '__main__':
    main()
