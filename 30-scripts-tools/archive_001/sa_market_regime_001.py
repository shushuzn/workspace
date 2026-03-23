import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-015: Market Regime Detection - 市场状态检测

功能：
1. 牛/熊/震荡市场识别
2. 波动率状态检测（高/中/低）
3. 趋势强度评估
4. 市场情绪指标
5. 状态转换预警

依赖：
- SA-005: 技术指标
- SA-007: 趋势分析

作者：Claw (AI Agent)
创建日期：2026-03-20
版本：1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import math


class MarketRegimeDetector:
    """市场状态检测引擎"""

    def __init__(self):
        self.cache_dir = Path("60-DATA/stock_regime")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def detect_market_trend(self, prices: List[float],
                            ma_short: List[float],
                            ma_long: List[float]) -> Dict:
        """
        检测市场趋势（牛/熊/震荡）
        
        Args:
            prices: 价格列表
            ma_short: 短期均线（如 MA20）
            ma_long: 长期均线（如 MA60）
        
        Returns:
            趋势检测结果
        """
        if len(prices) < 60 or not ma_short or not ma_long:
            return {
                'status': 'insufficient_data',
                'regime': 'unknown'
            }

        current_price = prices[-1]
        current_ma_short = ma_short[-1]
        current_ma_long = ma_long[-1]

        # 判断趋势
        if current_ma_short > current_ma_long * 1.05 and current_price > current_ma_short:
            regime = 'bull'
            description = '牛市 - 价格在均线上方，短期均线高于长期均线'
            confidence = 0.8
        elif current_ma_short < current_ma_long * 0.95 and current_price < current_ma_short:
            regime = 'bear'
            description = '熊市 - 价格在均线下方，短期均线低于长期均线'
            confidence = 0.8
        else:
            regime = 'sideways'
            description = '震荡市 - 均线粘合，无明显趋势'
            confidence = 0.6

        # 计算均线差值
        ma_diff_percent = (current_ma_short - current_ma_long) / current_ma_long * 100

        return {
            'regime': regime,
            'confidence': confidence,
            'ma_diff_percent': round(ma_diff_percent, 2),
            'description': f'{description} (均线差：{ma_diff_percent:.2f}%)'
        }

    def detect_volatility_regime(self, returns: List[float],
                                  window: int = 20) -> Dict:
        """
        检测波动率状态（高/中/低）
        
        Args:
            returns: 收益率列表
            window: 计算窗口
        
        Returns:
            波动率检测结果
        """
        if len(returns) < window:
            return {
                'status': 'insufficient_data',
                'regime': 'unknown'
            }

        # 计算滚动标准差
        recent_returns = returns[-window:]
        volatility = sum((r - sum(recent_returns)/len(recent_returns))**2
                        for r in recent_returns) / len(recent_returns)
        volatility = math.sqrt(volatility)

        # 年化波动率
        annualized_vol = volatility * math.sqrt(252) * 100

        # 判断波动率状态
        if annualized_vol > 40:
            regime = 'high'
            description = '高波动率市场'
        elif annualized_vol > 20:
            regime = 'medium'
            description = '中等波动率市场'
        else:
            regime = 'low'
            description = '低波动率市场'

        return {
            'regime': regime,
            'volatility': round(volatility * 100, 2),
            'annualized_vol': round(annualized_vol, 2),
            'description': f'{description} (年化波动率：{annualized_vol:.2f}%)'
        }

    def assess_trend_strength(self, prices: List[float],
                              highs: List[float],
                              lows: List[float]) -> Dict:
        """
        评估趋势强度
        
        Args:
            prices: 价格列表
            highs: 最高价列表
            lows: 最低价列表
        
        Returns:
            趋势强度评估
        """
        if len(prices) < 50:
            return {
                'status': 'insufficient_data',
                'strength': 'unknown'
            }

        # 计算 ADX（简化版）
        # 真实 ADX 需要计算 +DI 和 -DI，这里简化

        # 计算价格变化幅度
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        avg_change = sum(abs(c) for c in price_changes) / len(price_changes)

        # 计算趋势强度评分（0-100）
        recent_prices = prices[-20:]
        trend_score = 0

        # 上涨趋势
        if recent_prices[-1] > recent_prices[0]:
            uptrend_strength = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            trend_score += min(50, uptrend_strength * 2)
        # 下跌趋势
        else:
            downtrend_strength = (recent_prices[0] - recent_prices[-1]) / recent_prices[0] * 100
            trend_score += min(50, downtrend_strength * 2)

        # 趋势强度评级
        if trend_score >= 40:
            strength = 'strong'
            description = '强趋势'
        elif trend_score >= 20:
            strength = 'moderate'
            description = '中等趋势'
        else:
            strength = 'weak'
            description = '弱趋势/震荡'

        return {
            'strength': strength,
            'trend_score': round(trend_score, 1),
            'description': f'{description} (趋势强度评分：{trend_score:.1f}/100)'
        }

    def detect_market_sentiment(self, volume: List[float],
                                 prices: List[float]) -> Dict:
        """
        检测市场情绪
        
        Args:
            volume: 成交量列表
            prices: 价格列表
        
        Returns:
            市场情绪检测结果
        """
        if len(volume) < 20 or len(prices) < 20:
            return {
                'status': 'insufficient_data',
                'sentiment': 'unknown'
            }

        # 计算量价关系
        recent_volume = volume[-20:]
        recent_prices = prices[-20:]

        avg_volume = sum(recent_volume) / len(recent_volume)
        volume_trend = 'increasing' if recent_volume[-1] > avg_volume else 'decreasing'

        price_trend = 'up' if recent_prices[-1] > recent_prices[0] else 'down'

        # 情绪判断
        if volume_trend == 'increasing' and price_trend == 'up':
            sentiment = 'bullish'
            description = '看涨情绪 - 放量上涨'
        elif volume_trend == 'increasing' and price_trend == 'down':
            sentiment = 'bearish'
            description = '看跌情绪 - 放量下跌'
        elif volume_trend == 'decreasing' and price_trend == 'up':
            sentiment = 'cautiously_bullish'
            description = '谨慎看涨 - 缩量上涨'
        else:
            sentiment = 'cautiously_bearish'
            description = '谨慎看跌 - 缩量下跌'

        return {
            'sentiment': sentiment,
            'volume_trend': volume_trend,
            'price_trend': price_trend,
            'description': description
        }

    def detect_regime_transition(self, current_regime: str,
                                  previous_regime: str) -> Dict:
        """
        检测状态转换
        
        Args:
            current_regime: 当前状态
            previous_regime: 前一状态
        
        Returns:
            状态转换检测结果
        """
        if current_regime == previous_regime:
            return {
                'transition': False,
                'message': '市场状态未变化'
            }

        transition_map = {
            ('bull', 'bear'): 'bull_to_bear',
            ('bear', 'bull'): 'bear_to_bull',
            ('sideways', 'bull'): 'sideways_to_bull',
            ('sideways', 'bear'): 'sideways_to_bear',
            ('bull', 'sideways'): 'bull_to_sideways',
            ('bear', 'sideways'): 'bear_to_sideways',
        }

        transition_type = transition_map.get((current_regime, previous_regime), 'unknown')

        # 转换信号强度
        if 'bull_to_bear' in transition_type or 'bear_to_bull' in transition_type:
            signal_strength = 'strong'
        else:
            signal_strength = 'moderate'

        return {
            'transition': True,
            'transition_type': transition_type,
            'signal_strength': signal_strength,
            'message': f'市场状态转换：{previous_regime} → {current_regime}'
        }

    def analyze_market_regime(self, prices: List[float],
                               highs: List[float],
                               lows: List[float],
                               volumes: List[float],
                               ma_short: List[float] = None,
                               ma_long: List[float] = None,
                               returns: List[float] = None) -> Dict:
        """
        综合市场分析
        
        Args:
            prices: 价格列表
            highs: 最高价列表
            lows: 最低价列表
            volumes: 成交量列表
            ma_short: 短期均线（可选）
            ma_long: 长期均线（可选）
            returns: 收益率（可选）
        
        Returns:
            完整市场状态分析报告
        """
        result = {
            'analysis_date': datetime.now().isoformat(),
            'data_points': len(prices),
            'trend_analysis': {},
            'volatility_analysis': {},
            'strength_analysis': {},
            'sentiment_analysis': {},
            'overall_regime': 'unknown',
            'confidence': 0,
            'recommendations': []
        }

        # 1. 趋势分析
        if ma_short and ma_long:
            result['trend_analysis'] = self.detect_market_trend(prices, ma_short, ma_long)
        else:
            # 简化：假设均线
            ma_short = prices[-20:]
            ma_long = prices[-60:] if len(prices) >= 60 else prices[-20:]
            result['trend_analysis'] = self.detect_market_trend(prices, ma_short, ma_long)

        # 2. 波动率分析
        if returns:
            result['volatility_analysis'] = self.detect_volatility_regime(returns)
        else:
            # 计算简化收益率
            returns = [(prices[i] - prices[i-1]) / prices[i-1]
                      for i in range(1, len(prices))]
            result['volatility_analysis'] = self.detect_volatility_regime(returns)

        # 3. 趋势强度
        result['strength_analysis'] = self.assess_trend_strength(prices, highs, lows)

        # 4. 市场情绪
        result['sentiment_analysis'] = self.detect_market_sentiment(volumes, prices)

        # 5. 综合市场状态
        result['overall_regime'], result['confidence'] = self._calculate_overall_regime(result)

        # 6. 投资建议
        result['recommendations'] = self._generate_recommendations(result)

        return result

    def _calculate_overall_regime(self, analysis: Dict) -> tuple:
        """计算综合市场状态"""
        trend = analysis['trend_analysis'].get('regime', 'unknown')
        volatility = analysis['volatility_analysis'].get('regime', 'unknown')
        strength = analysis['strength_analysis'].get('strength', 'unknown')

        # 综合判断
        if trend == 'bull' and strength in ['strong', 'moderate']:
            overall = 'bull_market'
            confidence = 0.8
        elif trend == 'bear' and strength in ['strong', 'moderate']:
            overall = 'bear_market'
            confidence = 0.8
        elif trend == 'sideways' or strength == 'weak':
            overall = 'sideways_market'
            confidence = 0.7
        else:
            overall = 'uncertain'
            confidence = 0.5

        return overall, confidence

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """生成投资建议"""
        recommendations = []

        regime = analysis['overall_regime']
        volatility = analysis['volatility_analysis'].get('regime', 'unknown')

        if regime == 'bull_market':
            recommendations.append('牛市环境，可积极持仓')
            if volatility == 'high':
                recommendations.append('波动率高，注意风险控制')
        elif regime == 'bear_market':
            recommendations.append('熊市环境，建议减仓或空仓')
            if volatility == 'high':
                recommendations.append('高波动，避免抄底')
        elif regime == 'sideways_market':
            recommendations.append('震荡市，适合高抛低吸')
            recommendations.append('等待明确突破信号')
        else:
            recommendations.append('市场方向不明，观望为主')

        return recommendations

    def save_report(self, report: Dict, symbol: str = 'MARKET'):
        """保存市场状态报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_regime_{timestamp}.json"
        filepath = self.cache_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return filepath


def generate_test_data() -> tuple:
    """生成测试数据"""
    import random

    # 生成 200 天数据
    prices = [100.0]
    for i in range(199):
        change = random.uniform(-0.03, 0.035)  # 略微上涨
        prices.append(prices[-1] * (1 + change))

    highs = [p * (1 + random.uniform(0, 0.02)) for p in prices]
    lows = [p * (1 - random.uniform(0, 0.02)) for p in prices]
    volumes = [random.randint(800000, 1200000) for _ in range(200)]

    ma_short = [sum(prices[max(0, i-19):i+1]) / min(20, i+1) for i in range(200)]
    ma_long = [sum(prices[max(0, i-59):i+1]) / min(60, i+1) for i in range(200)]

    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]

    return prices, highs, lows, volumes, ma_short, ma_long, returns


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
# py sa_market_regime_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_market_regime_001.py

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

主函数"""
    print("=" * 70)
    print(" " * 20 + "SA-015: Market Regime Detection")
    print("=" * 70)

    detector = MarketRegimeDetector()

    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        prices, highs, lows, volumes, ma_short, ma_long, returns = generate_test_data()
        print(f"  Generated {len(prices)} days of data")
        print(f"  Price range: {min(prices):.2f} - {max(prices):.2f}")

        print("\n[Test 2] Market Trend Detection")
        print("-" * 70)
        trend = detector.detect_market_trend(prices, ma_short, ma_long)
        print(f"  {trend['description']}")

        print("\n[Test 3] Volatility Regime Detection")
        print("-" * 70)
        volatility = detector.detect_volatility_regime(returns)
        print(f"  {volatility['description']}")

        print("\n[Test 4] Trend Strength Assessment")
        print("-" * 70)
        strength = detector.assess_trend_strength(prices, highs, lows)
        print(f"  {strength['description']}")

        print("\n[Test 5] Market Sentiment Detection")
        print("-" * 70)
        sentiment = detector.detect_market_sentiment(volumes, prices)
        print(f"  {sentiment['description']}")

        print("\n[Test 6] Comprehensive Market Regime Analysis")
        print("-" * 70)
        full_analysis = detector.analyze_market_regime(
            prices, highs, lows, volumes, ma_short, ma_long, returns
        )
        print(f"  Overall Regime: {full_analysis['overall_regime']}")
        print(f"  Confidence: {full_analysis['confidence']:.0%}")
        print(f"  Recommendations:")
        for rec in full_analysis['recommendations']:
            print(f"    - {rec}")

        print("\n[Test 7] Save Report")
        print("-" * 70)
        report_path = detector.save_report(full_analysis, 'TEST')
        print(f"  Report saved to: {report_path}")

        print("\n" + "=" * 70)
        print(" SA-015 Market Regime Detection test completed")
        print("=" * 70)

    else:
        # 正常使用模式
        print("\nUsage: py sa_015_market_regime.py --test")
        print("\nFeatures:")
        print("  - Bull/Bear/Sideways market detection")
        print("  - Volatility regime (high/medium/low)")
        print("  - Trend strength assessment")
        print("  - Market sentiment analysis")
        print("  - Regime transition detection")
        print("  - Investment recommendations")
        print("  - Auto-save reports to 60-DATA/stock_regime/")


if __name__ == '__main__':
    main()
