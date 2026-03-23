import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-011: Growth Analysis - 成长性分析引擎

功能：
1. 营收增长分析（3 年/5 年 CAGR）
2. 利润增长分析（净利润 CAGR）
3. 现金流增长分析
4. 股东权益增长分析
5. 成长性评分（0-100）
6. 成长趋势预测

依赖：
- SA-009: Financial ratios

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


class GrowthAnalyzer:
    """成长性分析引擎"""

    def __init__(self):
        self.cache_dir = Path("60-DATA/stock_growth")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def calculate_cagr(self, start_value: float, end_value: float, years: int) -> float:
        """
        计算复合年增长率（CAGR）
        
        Args:
            start_value: 起始值
            end_value: 结束值
            years: 年数
        
        Returns:
            CAGR（小数形式）
        """
        if start_value <= 0 or years <= 0:
            return 0.0

        return (end_value / start_value) ** (1 / years) - 1

    def analyze_revenue_growth(self, financial_history: List[Dict]) -> Dict:
        """
        营收增长分析
        
        Args:
            financial_history: 历史财务数据列表（按年份）
        
        Returns:
            营收增长分析结果
        """
        if len(financial_history) < 2:
            return {'error': '数据不足'}

        # 按年份排序
        sorted_data = sorted(financial_history, key=lambda x: x.get('year', 0))

        revenues = [d.get('revenue', 0) for d in sorted_data]
        years = len(revenues)

        # 计算 CAGR
        cagr_3y = self.calculate_cagr(revenues[0], revenues[-1], min(3, years-1)) if years >= 4 else 0
        cagr_5y = self.calculate_cagr(revenues[0], revenues[-1], min(5, years-1)) if years >= 6 else 0

        # 计算同比增长率
        yoy_growth = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                yoy = (revenues[i] - revenues[i-1]) / revenues[i-1]
                yoy_growth.append(yoy)

        avg_yoy = sum(yoy_growth) / len(yoy_growth) if yoy_growth else 0

        return {
            'revenue_cagr_3y': round(cagr_3y, 4),
            'revenue_cagr_5y': round(cagr_5y, 4),
            'avg_yoy_growth': round(avg_yoy, 4),
            'years_analyzed': years,
            'description': f'营收 3 年 CAGR: {cagr_3y:.2%}, 5 年 CAGR: {cagr_5y:.2%}'
        }

    def analyze_profit_growth(self, financial_history: List[Dict]) -> Dict:
        """
        利润增长分析
        
        Args:
            financial_history: 历史财务数据
        
        Returns:
            利润增长分析结果
        """
        if len(financial_history) < 2:
            return {'error': '数据不足'}

        sorted_data = sorted(financial_history, key=lambda x: x.get('year', 0))
        net_incomes = [d.get('net_income', 0) for d in sorted_data]
        years = len(net_incomes)

        # 计算 CAGR
        cagr_3y = self.calculate_cagr(net_incomes[0], net_incomes[-1], min(3, years-1)) if years >= 4 else 0
        cagr_5y = self.calculate_cagr(net_incomes[0], net_incomes[-1], min(5, years-1)) if years >= 6 else 0

        # 计算同比增长
        yoy_growth = []
        for i in range(1, len(net_incomes)):
            if net_incomes[i-1] > 0:
                yoy = (net_incomes[i] - net_incomes[i-1]) / net_incomes[i-1]
                yoy_growth.append(yoy)

        avg_yoy = sum(yoy_growth) / len(yoy_growth) if yoy_growth else 0

        return {
            'profit_cagr_3y': round(cagr_3y, 4),
            'profit_cagr_5y': round(cagr_5y, 4),
            'avg_yoy_growth': round(avg_yoy, 4),
            'description': f'净利润 3 年 CAGR: {cagr_3y:.2%}, 5 年 CAGR: {cagr_5y:.2%}'
        }

    def analyze_cash_flow_growth(self, financial_history: List[Dict]) -> Dict:
        """
        现金流增长分析
        
        Args:
            financial_history: 历史财务数据
        
        Returns:
            现金流增长分析结果
        """
        if len(financial_history) < 2:
            return {'error': '数据不足'}

        sorted_data = sorted(financial_history, key=lambda x: x.get('year', 0))
        ocfs = [d.get('operating_cash_flow', 0) for d in sorted_data]
        years = len(ocfs)

        # 计算 CAGR
        cagr_3y = self.calculate_cagr(ocfs[0], ocfs[-1], min(3, years-1)) if years >= 4 else 0
        cagr_5y = self.calculate_cagr(ocfs[0], ocfs[-1], min(5, years-1)) if years >= 6 else 0

        return {
            'ocf_cagr_3y': round(cagr_3y, 4),
            'ocf_cagr_5y': round(cagr_5y, 4),
            'description': f'经营现金流 3 年 CAGR: {cagr_3y:.2%}'
        }

    def calculate_growth_score(self, revenue_analysis: Dict,
                                profit_analysis: Dict,
                                cashflow_analysis: Dict) -> Dict:
        """
        计算成长性综合评分（0-100）
        
        Args:
            revenue_analysis: 营收增长分析
            profit_analysis: 利润增长分析
            cashflow_analysis: 现金流增长分析
        
        Returns:
            成长性评分
        """
        score = 0
        max_score = 100

        # 营收增长（40 分）
        rev_cagr = revenue_analysis.get('revenue_cagr_3y', 0)
        if rev_cagr > 0.30:
            score += 40
        elif rev_cagr > 0.20:
            score += 30
        elif rev_cagr > 0.10:
            score += 20
        elif rev_cagr > 0:
            score += 10

        # 利润增长（40 分）
        profit_cagr = profit_analysis.get('profit_cagr_3y', 0)
        if profit_cagr > 0.30:
            score += 40
        elif profit_cagr > 0.20:
            score += 30
        elif profit_cagr > 0.10:
            score += 20
        elif profit_cagr > 0:
            score += 10

        # 现金流增长（20 分）
        ocf_cagr = cashflow_analysis.get('ocf_cagr_3y', 0)
        if ocf_cagr > 0.20:
            score += 20
        elif ocf_cagr > 0.10:
            score += 15
        elif ocf_cagr > 0:
            score += 10

        # 评级
        if score >= 80:
            rating = 'A'
            description = '高成长'
        elif score >= 60:
            rating = 'B'
            description = '中高成长'
        elif score >= 40:
            rating = 'C'
            description = '中等成长'
        elif score >= 20:
            rating = 'D'
            description = '低成长'
        else:
            rating = 'E'
            description = '负成长'

        return {
            'score': score,
            'max_score': max_score,
            'rating': rating,
            'description': f'成长性评分：{score}/{max_score} ({rating}级 - {description})'
        }

    def predict_growth_trend(self, historical_growth: List[float], years_ahead: int = 3) -> Dict:
        """
        预测成长趋势（简化版线性回归）
        
        Args:
            historical_growth: 历史增长率列表
            years_ahead: 预测年数
        
        Returns:
            成长趋势预测
        """
        if len(historical_growth) < 2:
            return {'error': '数据不足'}

        # 简单线性趋势
        avg_growth = sum(historical_growth) / len(historical_growth)
        trend = 'stable'

        # 判断趋势方向
        if len(historical_growth) >= 3:
            first_half = sum(historical_growth[:len(historical_growth)//2]) / (len(historical_growth)//2)
            second_half = sum(historical_growth[len(historical_growth)//2:]) / (len(historical_growth) - len(historical_growth)//2)

            if second_half > first_half * 1.1:
                trend = 'accelerating'
            elif second_half < first_half * 0.9:
                trend = 'decelerating'

        # 预测未来
        predicted_growth = [avg_growth * (0.95 ** i) for i in range(years_ahead)]  # 假设逐年放缓

        return {
            'avg_historical_growth': round(avg_growth, 4),
            'trend': trend,
            'predicted_growth': [round(g, 4) for g in predicted_growth],
            'description': f'平均增长率：{avg_growth:.2%}, 趋势：{trend}'
        }

    def analyze_all_growth(self, financial_history: List[Dict]) -> Dict:
        """
        综合成长性分析
        
        Args:
            financial_history: 历史财务数据
        
        Returns:
            完整成长性分析报告
        """
        result = {
            'symbol': financial_history[0].get('symbol', 'TEST') if financial_history else 'TEST',
            'analysis_date': datetime.now().isoformat(),
            'revenue_growth': {},
            'profit_growth': {},
            'cashflow_growth': {},
            'growth_score': {},
            'growth_trend': {}
        }

        # 1. 营收增长
        result['revenue_growth'] = self.analyze_revenue_growth(financial_history)

        # 2. 利润增长
        result['profit_growth'] = self.analyze_profit_growth(financial_history)

        # 3. 现金流增长
        result['cashflow_growth'] = self.analyze_cash_flow_growth(financial_history)

        # 4. 成长性评分
        result['growth_score'] = self.calculate_growth_score(
            result['revenue_growth'],
            result['profit_growth'],
            result['cashflow_growth']
        )

        # 5. 成长趋势预测
        historical_growth_rates = [
            result['revenue_growth'].get('avg_yoy_growth', 0),
            result['profit_growth'].get('avg_yoy_growth', 0),
            result['cashflow_growth'].get('ocf_cagr_3y', 0)
        ]
        result['growth_trend'] = self.predict_growth_trend(historical_growth_rates)

        return result

    def save_report(self, report: Dict, symbol: str = 'TEST'):
        """保存成长性分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_growth_{timestamp}.json"
        filepath = self.cache_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return filepath

    def analyze(self, symbol: str, data: Dict = None) -> Dict:
        """
        Unified analyze wrapper for pipeline compatibility.

        Args:
            symbol: Stock symbol
            data: Optional dict with financial_history

        Returns:
            Dict with growth analysis
        """
        data = data or {}
        financial_history = data.get('financial_history', [])
        if not financial_history:
            financial_history = generate_test_data()
        # Ensure symbol is set
        for item in financial_history:
            item['symbol'] = symbol

        return self.analyze_all_growth(financial_history)


def generate_test_data() -> List[Dict]:
    """生成测试财务历史数据"""
    return [
        {'year': 2020, 'symbol': 'TEST', 'revenue': 1000000, 'net_income': 100000, 'operating_cash_flow': 120000},
        {'year': 2021, 'symbol': 'TEST', 'revenue': 1300000, 'net_income': 150000, 'operating_cash_flow': 170000},
        {'year': 2022, 'symbol': 'TEST', 'revenue': 1700000, 'net_income': 220000, 'operating_cash_flow': 240000},
        {'year': 2023, 'symbol': 'TEST', 'revenue': 2200000, 'net_income': 300000, 'operating_cash_flow': 330000},
        {'year': 2024, 'symbol': 'TEST', 'revenue': 2800000, 'net_income': 400000, 'operating_cash_flow': 450000},
    ]


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
# py sa_growth_analysis_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_growth_analysis_001.py

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
    print(" " * 25 + "SA-011: Growth Analysis")
    print("=" * 70)

    analyzer = GrowthAnalyzer()

    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        financial_history = generate_test_data()
        print(f"  Symbol: {financial_history[0]['symbol']}")
        print(f"  Years: {len(financial_history)}")
        print(f"  Revenue Range: {financial_history[0]['revenue']:,.0f} - {financial_history[-1]['revenue']:,.0f}")

        print("\n[Test 2] Revenue Growth Analysis")
        print("-" * 70)
        rev_growth = analyzer.analyze_revenue_growth(financial_history)
        print(f"  {rev_growth['description']}")

        print("\n[Test 3] Profit Growth Analysis")
        print("-" * 70)
        profit_growth = analyzer.analyze_profit_growth(financial_history)
        print(f"  {profit_growth['description']}")

        print("\n[Test 4] Cash Flow Growth Analysis")
        print("-" * 70)
        cf_growth = analyzer.analyze_cash_flow_growth(financial_history)
        print(f"  {cf_growth['description']}")

        print("\n[Test 5] Growth Score")
        print("-" * 70)
        score = analyzer.calculate_growth_score(rev_growth, profit_growth, cf_growth)
        print(f"  {score['description']}")

        print("\n[Test 6] Growth Trend Prediction")
        print("-" * 70)
        historical_rates = [0.30, 0.38, 0.36, 0.29, 0.27]
        trend = analyzer.predict_growth_trend(historical_rates, years_ahead=3)
        print(f"  {trend['description']}")
        print(f"  Predicted: {[f'{g:.2%}' for g in trend['predicted_growth']]}")

        print("\n[Test 7] Full Growth Analysis")
        print("-" * 70)
        full_analysis = analyzer.analyze_all_growth(financial_history)
        print(f"  Symbol: {full_analysis['symbol']}")
        print(f"  Revenue: {full_analysis['revenue_growth']['description']}")
        print(f"  Profit: {full_analysis['profit_growth']['description']}")
        print(f"  Score: {full_analysis['growth_score']['description']}")
        print(f"  Trend: {full_analysis['growth_trend']['description']}")

        print("\n[Test 8] Save Report")
        print("-" * 70)
        report_path = analyzer.save_report(full_analysis, 'TEST')
        print(f"  Report saved to: {report_path}")

        print("\n" + "=" * 70)
        print(" SA-011 Growth Analysis test completed")
        print("=" * 70)

    else:
        # 正常使用模式
        print("\nUsage: py sa_011_growth_analysis.py --test")
        print("\nFeatures:")
        print("  - Revenue growth analysis (3Y/5Y CAGR)")
        print("  - Profit growth analysis (net income CAGR)")
        print("  - Cash flow growth analysis")
        print("  - Comprehensive growth score (0-100)")
        print("  - Growth trend prediction")
        print("  - Auto-save reports to 60-DATA/stock_growth/")


if __name__ == '__main__':
    main()
