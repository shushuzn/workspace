#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-009: Financial Ratios - 财务比率分析引擎

功能：
1. 偿债能力比率（流动比率、速动比率、资产负债率）
2. 盈利能力比率（毛利率、净利率、ROE、ROA）
3. 运营能力比率（存货周转率、应收账款周转率）
4. 成长能力比率（营收增长率、净利润增长率）
5. 估值比率（PE、PB、PS）
6. 综合财务评分

依赖：
- SA-003: Financial collector

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


class FinancialRatioAnalyzer:
    """财务比率分析引擎"""
    
    def __init__(self):
        self.cache_dir = Path("60-DATA/stock_financials")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_liquidity_ratios(self, financial_data: Dict) -> Dict:
        """
        计算偿债能力比率
        
        Args:
            financial_data: 财务数据
        
        Returns:
            偿债能力比率
        """
        current_assets = financial_data.get('current_assets', 0)
        current_liabilities = financial_data.get('current_liabilities', 0)
        inventory = financial_data.get('inventory', 0)
        total_assets = financial_data.get('total_assets', 0)
        total_liabilities = financial_data.get('total_liabilities', 0)
        
        # 流动比率 = 流动资产 / 流动负债
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
        
        # 速动比率 = (流动资产 - 存货) / 流动负债
        quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
        
        # 资产负债率 = 总负债 / 总资产
        debt_to_asset = total_liabilities / total_assets if total_assets > 0 else 0
        
        return {
            'current_ratio': round(current_ratio, 2),
            'quick_ratio': round(quick_ratio, 2),
            'debt_to_asset': round(debt_to_asset, 4),
            'description': f'流动比率：{current_ratio:.2f}, 速动比率：{quick_ratio:.2f}, 资产负债率：{debt_to_asset:.2%}'
        }
    
    def calculate_profitability_ratios(self, financial_data: Dict) -> Dict:
        """
        计算盈利能力比率
        
        Args:
            financial_data: 财务数据
        
        Returns:
            盈利能力比率
        """
        revenue = financial_data.get('revenue', 0)
        gross_profit = financial_data.get('gross_profit', 0)
        net_income = financial_data.get('net_income', 0)
        total_assets = financial_data.get('total_assets', 0)
        shareholders_equity = financial_data.get('shareholders_equity', 0)
        
        # 毛利率 = 毛利润 / 营业收入
        gross_margin = gross_profit / revenue if revenue > 0 else 0
        
        # 净利率 = 净利润 / 营业收入
        net_margin = net_income / revenue if revenue > 0 else 0
        
        # ROA = 净利润 / 总资产
        roa = net_income / total_assets if total_assets > 0 else 0
        
        # ROE = 净利润 / 股东权益
        roe = net_income / shareholders_equity if shareholders_equity > 0 else 0
        
        return {
            'gross_margin': round(gross_margin, 4),
            'net_margin': round(net_margin, 4),
            'roa': round(roa, 4),
            'roe': round(roe, 4),
            'description': f'毛利率：{gross_margin:.2%}, 净利率：{net_margin:.2%}, ROA: {roa:.2%}, ROE: {roe:.2%}'
        }
    
    def calculate_efficiency_ratios(self, financial_data: Dict) -> Dict:
        """
        计算运营能力比率
        
        Args:
            financial_data: 财务数据
        
        Returns:
            运营能力比率
        """
        revenue = financial_data.get('revenue', 0)
        inventory = financial_data.get('inventory', 0)
        accounts_receivable = financial_data.get('accounts_receivable', 0)
        
        # 存货周转率 = 营业收入 / 存货
        inventory_turnover = revenue / inventory if inventory > 0 else 0
        
        # 应收账款周转率 = 营业收入 / 应收账款
        receivables_turnover = revenue / accounts_receivable if accounts_receivable > 0 else 0
        
        return {
            'inventory_turnover': round(inventory_turnover, 2),
            'receivables_turnover': round(receivables_turnover, 2),
            'description': f'存货周转率：{inventory_turnover:.2f}, 应收账款周转率：{receivables_turnover:.2f}'
        }
    
    def calculate_growth_ratios(self, current_data: Dict, previous_data: Dict) -> Dict:
        """
        计算成长能力比率
        
        Args:
            current_data: 当期财务数据
            previous_data: 上期财务数据
        
        Returns:
            成长能力比率
        """
        current_revenue = current_data.get('revenue', 0)
        previous_revenue = previous_data.get('revenue', 0)
        current_net_income = current_data.get('net_income', 0)
        previous_net_income = previous_data.get('net_income', 0)
        
        # 营收增长率 = (本期营收 - 上期营收) / 上期营收
        revenue_growth = (current_revenue - previous_revenue) / previous_revenue if previous_revenue > 0 else 0
        
        # 净利润增长率 = (本期净利润 - 上期净利润) / 上期净利润
        net_income_growth = (current_net_income - previous_net_income) / previous_net_income if previous_net_income > 0 else 0
        
        return {
            'revenue_growth': round(revenue_growth, 4),
            'net_income_growth': round(net_income_growth, 4),
            'description': f'营收增长率：{revenue_growth:.2%}, 净利润增长率：{net_income_growth:.2%}'
        }
    
    def calculate_valuation_ratios(self, market_data: Dict, financial_data: Dict) -> Dict:
        """
        计算估值比率
        
        Args:
            market_data: 市场数据（股价、市值等）
            financial_data: 财务数据
        
        Returns:
            估值比率
        """
        price = market_data.get('price', 0)
        market_cap = market_data.get('market_cap', 0)
        eps = financial_data.get('eps', 0)
        bvps = financial_data.get('bvps', 0)
        revenue = financial_data.get('revenue', 0)
        
        # PE = 股价 / 每股收益
        pe_ratio = price / eps if eps > 0 else 0
        
        # PB = 市值 / 股东权益
        pb_ratio = market_cap / (bvps * (market_cap / price)) if bvps > 0 and price > 0 else 0
        
        # PS = 市值 / 营业收入
        ps_ratio = market_cap / revenue if revenue > 0 else 0
        
        return {
            'pe_ratio': round(pe_ratio, 2),
            'pb_ratio': round(pb_ratio, 2),
            'ps_ratio': round(ps_ratio, 2),
            'description': f'PE: {pe_ratio:.2f}, PB: {pb_ratio:.2f}, PS: {ps_ratio:.2f}'
        }
    
    def calculate_comprehensive_score(self, ratios: Dict) -> Dict:
        """
        计算综合财务评分
        
        Args:
            ratios: 所有比率数据
        
        Returns:
            综合评分
        """
        score = 0
        max_score = 100
        
        # 偿债能力 (20 分)
        if ratios.get('current_ratio', 0) > 1.5:
            score += 10
        if ratios.get('debt_to_asset', 1) < 0.6:
            score += 10
        
        # 盈利能力 (30 分)
        if ratios.get('gross_margin', 0) > 0.3:
            score += 10
        if ratios.get('net_margin', 0) > 0.15:
            score += 10
        if ratios.get('roe', 0) > 0.15:
            score += 10
        
        # 成长能力 (30 分)
        if ratios.get('revenue_growth', 0) > 0.2:
            score += 15
        if ratios.get('net_income_growth', 0) > 0.2:
            score += 15
        
        # 估值合理性 (20 分)
        if 10 < ratios.get('pe_ratio', 0) < 30:
            score += 10
        if 1 < ratios.get('pb_ratio', 0) < 5:
            score += 10
        
        # 评级
        if score >= 80:
            rating = 'A'
            description = '优秀'
        elif score >= 60:
            rating = 'B'
            description = '良好'
        elif score >= 40:
            rating = 'C'
            description = '中等'
        else:
            rating = 'D'
            description = '较差'
        
        return {
            'score': score,
            'max_score': max_score,
            'rating': rating,
            'description': f'综合评分：{score}/{max_score} ({rating}级 - {description})'
        }
    
    def analyze_all_ratios(self, financial_data: Dict, 
                           previous_data: Dict = None,
                           market_data: Dict = None) -> Dict:
        """
        综合分析所有财务比率
        
        Args:
            financial_data: 财务数据
            previous_data: 上期财务数据（可选）
            market_data: 市场数据（可选）
        
        Returns:
            完整财务比率分析报告
        """
        result = {
            'symbol': financial_data.get('symbol', 'TEST'),
            'analysis_date': datetime.now().isoformat(),
            'liquidity_ratios': {},
            'profitability_ratios': {},
            'efficiency_ratios': {},
            'growth_ratios': {},
            'valuation_ratios': {},
            'comprehensive_score': {}
        }
        
        # 1. 偿债能力
        result['liquidity_ratios'] = self.calculate_liquidity_ratios(financial_data)
        
        # 2. 盈利能力
        result['profitability_ratios'] = self.calculate_profitability_ratios(financial_data)
        
        # 3. 运营能力
        result['efficiency_ratios'] = self.calculate_efficiency_ratios(financial_data)
        
        # 4. 成长能力（需要上期数据）
        if previous_data:
            result['growth_ratios'] = self.calculate_growth_ratios(financial_data, previous_data)
        else:
            result['growth_ratios'] = {'description': '缺少上期数据，无法计算成长比率'}
        
        # 5. 估值比率（需要市场数据）
        if market_data:
            result['valuation_ratios'] = self.calculate_valuation_ratios(market_data, financial_data)
        else:
            result['valuation_ratios'] = {'description': '缺少市场数据，无法计算估值比率'}
        
        # 6. 综合评分
        all_ratios = {
            **result['liquidity_ratios'],
            **result['profitability_ratios'],
            **result['growth_ratios'],
            **result['valuation_ratios']
        }
        result['comprehensive_score'] = self.calculate_comprehensive_score(all_ratios)
        
        return result
    
    def save_report(self, report: Dict, symbol: str = 'TEST'):
        """保存财务比率分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_financial_{timestamp}.json"
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath


def generate_test_data() -> Dict:
    """生成测试财务数据"""
    return {
        'symbol': 'TEST',
        'current_assets': 1000000,
        'current_liabilities': 600000,
        'inventory': 200000,
        'total_assets': 2000000,
        'total_liabilities': 1000000,
        'revenue': 1500000,
        'gross_profit': 600000,
        'net_income': 200000,
        'shareholders_equity': 1000000,
        'accounts_receivable': 300000,
        'eps': 2.0,
        'bvps': 10.0
    }


def generate_previous_data() -> Dict:
    """生成上期测试数据"""
    return {
        'revenue': 1200000,
        'net_income': 150000
    }


def generate_market_data() -> Dict:
    """生成测试市场数据"""
    return {
        'price': 40.0,
        'market_cap': 2000000
    }


def main():
    """主函数"""
    print("=" * 70)
    print(" " * 25 + "SA-009: Financial Ratios")
    print("=" * 70)
    
    analyzer = FinancialRatioAnalyzer()
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        financial_data = generate_test_data()
        previous_data = generate_previous_data()
        market_data = generate_market_data()
        print(f"  Symbol: {financial_data['symbol']}")
        print(f"  Revenue: {financial_data['revenue']:,.0f}")
        print(f"  Net Income: {financial_data['net_income']:,.0f}")
        
        print("\n[Test 2] Liquidity Ratios")
        print("-" * 70)
        liquidity = analyzer.calculate_liquidity_ratios(financial_data)
        print(f"  {liquidity['description']}")
        
        print("\n[Test 3] Profitability Ratios")
        print("-" * 70)
        profitability = analyzer.calculate_profitability_ratios(financial_data)
        print(f"  {profitability['description']}")
        
        print("\n[Test 4] Efficiency Ratios")
        print("-" * 70)
        efficiency = analyzer.calculate_efficiency_ratios(financial_data)
        print(f"  {efficiency['description']}")
        
        print("\n[Test 5] Growth Ratios")
        print("-" * 70)
        growth = analyzer.calculate_growth_ratios(financial_data, previous_data)
        print(f"  {growth['description']}")
        
        print("\n[Test 6] Valuation Ratios")
        print("-" * 70)
        valuation = analyzer.calculate_valuation_ratios(market_data, financial_data)
        print(f"  {valuation['description']}")
        
        print("\n[Test 7] Comprehensive Score")
        print("-" * 70)
        all_ratios = {**liquidity, **profitability, **growth, **valuation}
        score = analyzer.calculate_comprehensive_score(all_ratios)
        print(f"  {score['description']}")
        
        print("\n[Test 8] Full Analysis")
        print("-" * 70)
        full_analysis = analyzer.analyze_all_ratios(financial_data, previous_data, market_data)
        print(f"  Symbol: {full_analysis['symbol']}")
        print(f"  Liquidity: {full_analysis['liquidity_ratios']['description']}")
        print(f"  Profitability: {full_analysis['profitability_ratios']['description']}")
        print(f"  Growth: {full_analysis['growth_ratios']['description']}")
        print(f"  Valuation: {full_analysis['valuation_ratios']['description']}")
        print(f"  Score: {full_analysis['comprehensive_score']['description']}")
        
        print("\n[Test 9] Save Report")
        print("-" * 70)
        report_path = analyzer.save_report(full_analysis, 'TEST')
        print(f"  Report saved to: {report_path}")
        
        print("\n" + "=" * 70)
        print(" SA-009 Financial Ratios test completed")
        print("=" * 70)
    
    else:
        # 正常使用模式
        print("\nUsage: py sa_009_financial_ratios.py --test")
        print("\nFeatures:")
        print("  - Liquidity ratios (current, quick, debt-to-asset)")
        print("  - Profitability ratios (gross margin, net margin, ROA, ROE)")
        print("  - Efficiency ratios (inventory turnover, receivables turnover)")
        print("  - Growth ratios (revenue growth, net income growth)")
        print("  - Valuation ratios (PE, PB, PS)")
        print("  - Comprehensive financial score (0-100)")
        print("  - Auto-save reports to 60-DATA/stock_financials/")


if __name__ == '__main__':
    main()
