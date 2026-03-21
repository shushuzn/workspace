import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-010: Valuation Model - 估值模型引擎

功能：
1. DCF 估值（现金流折现模型）
2. 相对估值（PE/PB/PS 对比）
3. PEG 估值（成长性调整）
4. 股息贴现模型（DDM）
5. 综合估值评分
6. 目标价计算

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


class ValuationModel:
    """估值模型引擎"""
    
    def __init__(self):
        self.cache_dir = Path("60-DATA/stock_valuation")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def dcf_valuation(self, financial_data: Dict, assumptions: Dict = None) -> Dict:
        """
        DCF 估值（现金流折现模型）
        
        Args:
            financial_data: 财务数据
            assumptions: 假设参数
        
        Returns:
            DCF 估值结果
        """
        if assumptions is None:
            assumptions = {
                'growth_rate': 0.15,  # 增长率 15%
                'discount_rate': 0.10,  # 折现率 10%
                'terminal_growth': 0.03,  # 永续增长率 3%
                'years': 5  # 预测 5 年
            }
        
        free_cash_flow = financial_data.get('free_cash_flow', 100000)
        shares_outstanding = financial_data.get('shares_outstanding', 10000)
        
        # 预测未来现金流
        projected_fcf = []
        for year in range(assumptions['years']):
            fcf = free_cash_flow * (1 + assumptions['growth_rate']) ** year
            projected_fcf.append(fcf)
        
        # 计算现值
        pv_fcf = sum(
            fcf / (1 + assumptions['discount_rate']) ** (year + 1)
            for year, fcf in enumerate(projected_fcf)
        )
        
        # 计算终值
        terminal_fcf = projected_fcf[-1] * (1 + assumptions['terminal_growth'])
        terminal_value = terminal_fcf / (assumptions['discount_rate'] - assumptions['terminal_growth'])
        pv_terminal = terminal_value / (1 + assumptions['discount_rate']) ** assumptions['years']
        
        # 计算企业价值和每股价值
        enterprise_value = pv_fcf + pv_terminal
        equity_value = enterprise_value - financial_data.get('total_debt', 0)
        value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        return {
            'method': 'DCF',
            'enterprise_value': round(enterprise_value, 2),
            'equity_value': round(equity_value, 2),
            'value_per_share': round(value_per_share, 2),
            'assumptions': assumptions,
            'description': f'DCF 估值：{value_per_share:.2f}元/股'
        }
    
    def relative_valuation(self, company_data: Dict, peer_data: List[Dict]) -> Dict:
        """
        相对估值（与同行业对比）
        
        Args:
            company_data: 公司数据
            peer_data: 同行数据列表
        
        Returns:
            相对估值结果
        """
        company_pe = company_data.get('pe_ratio', 0)
        company_pb = company_data.get('pb_ratio', 0)
        company_ps = company_data.get('ps_ratio', 0)
        
        # 计算行业平均
        peer_pes = [p.get('pe_ratio', 0) for p in peer_data if p.get('pe_ratio', 0) > 0]
        peer_pbs = [p.get('pb_ratio', 0) for p in peer_data if p.get('pb_ratio', 0) > 0]
        peer_pss = [p.get('ps_ratio', 0) for p in peer_data if p.get('ps_ratio', 0) > 0]
        
        industry_pe = sum(peer_pes) / len(peer_pes) if peer_pes else 0
        industry_pb = sum(peer_pbs) / len(peer_pbs) if peer_pbs else 0
        industry_ps = sum(peer_pss) / len(peer_pss) if peer_pss else 0
        
        # 计算相对估值
        pe_premium = (company_pe - industry_pe) / industry_pe if industry_pe > 0 else 0
        pb_premium = (company_pb - industry_pb) / industry_pb if industry_pb > 0 else 0
        ps_premium = (company_ps - industry_ps) / industry_ps if industry_ps > 0 else 0
        
        # 判断高估/低估
        avg_premium = (pe_premium + pb_premium + ps_premium) / 3
        
        if avg_premium > 0.2:
            valuation = 'overvalued'
            description = '高估'
        elif avg_premium < -0.2:
            valuation = 'undervalued'
            description = '低估'
        else:
            valuation = 'fair'
            description = '合理'
        
        return {
            'method': 'Relative Valuation',
            'company_pe': company_pe,
            'industry_pe': round(industry_pe, 2),
            'company_pb': company_pb,
            'industry_pb': round(industry_pb, 2),
            'company_ps': company_ps,
            'industry_ps': round(industry_ps, 2),
            'pe_premium': round(pe_premium, 4),
            'pb_premium': round(pb_premium, 4),
            'ps_premium': round(ps_premium, 4),
            'valuation': valuation,
            'description': f'相对估值：{description} (行业平均 PE: {industry_pe:.2f})'
        }
    
    def peg_valuation(self, pe_ratio: float, growth_rate: float) -> Dict:
        """
        PEG 估值（成长性调整）
        
        Args:
            pe_ratio: PE 比率
            growth_rate: 净利润增长率
        
        Returns:
            PEG 估值结果
        """
        peg_ratio = pe_ratio / (growth_rate * 100) if growth_rate > 0 else 0
        
        # PEG 判断标准
        if peg_ratio < 1:
            valuation = 'undervalued'
            description = '低估（成长性未被充分定价）'
        elif peg_ratio < 1.5:
            valuation = 'fair'
            description = '合理'
        else:
            valuation = 'overvalued'
            description = '高估'
        
        return {
            'method': 'PEG',
            'pe_ratio': pe_ratio,
            'growth_rate': growth_rate,
            'peg_ratio': round(peg_ratio, 2),
            'valuation': valuation,
            'description': f'PEG: {peg_ratio:.2f} - {description}'
        }
    
    def ddm_valuation(self, dividend_data: Dict, assumptions: Dict = None) -> Dict:
        """
        股息贴现模型（DDM）
        
        Args:
            dividend_data: 股息数据
            assumptions: 假设参数
        
        Returns:
            DDM 估值结果
        """
        if assumptions is None:
            assumptions = {
                'growth_rate': 0.05,  # 股息增长率 5%
                'required_return': 0.10  # 要求回报率 10%
            }
        
        current_dividend = dividend_data.get('annual_dividend', 0)
        
        # Gordon Growth Model: P = D1 / (r - g)
        next_dividend = current_dividend * (1 + assumptions['growth_rate'])
        value_per_share = next_dividend / (assumptions['required_return'] - assumptions['growth_rate'])
        
        return {
            'method': 'DDM',
            'current_dividend': current_dividend,
            'next_dividend': round(next_dividend, 2),
            'value_per_share': round(value_per_share, 2),
            'assumptions': assumptions,
            'description': f'DDM 估值：{value_per_share:.2f}元/股'
        }
    
    def comprehensive_valuation(self, financial_data: Dict, 
                                 market_data: Dict,
                                 peer_data: List[Dict] = None) -> Dict:
        """
        综合估值
        
        Args:
            financial_data: 财务数据
            market_data: 市场数据
            peer_data: 同行数据（可选）
        
        Returns:
            综合估值结果
        """
        result = {
            'symbol': financial_data.get('symbol', 'TEST'),
            'analysis_date': datetime.now().isoformat(),
            'current_price': market_data.get('price', 0),
            'valuations': {},
            'target_price': 0,
            'upside_potential': 0,
            'recommendation': 'hold'
        }
        
        # 1. DCF 估值
        result['valuations']['dcf'] = self.dcf_valuation(financial_data)
        
        # 2. 相对估值（如果有同行数据）
        if peer_data:
            result['valuations']['relative'] = self.relative_valuation(
                {
                    'pe_ratio': market_data.get('pe_ratio', 0),
                    'pb_ratio': market_data.get('pb_ratio', 0),
                    'ps_ratio': market_data.get('ps_ratio', 0)
                },
                peer_data
            )
        
        # 3. PEG 估值
        pe_ratio = market_data.get('pe_ratio', 0)
        growth_rate = financial_data.get('net_income_growth', 0.15)
        result['valuations']['peg'] = self.peg_valuation(pe_ratio, growth_rate)
        
        # 4. DDM 估值（如果有股息数据）
        if financial_data.get('annual_dividend', 0) > 0:
            result['valuations']['ddm'] = self.ddm_valuation(financial_data)
        
        # 5. 计算目标价（多种方法平均）
        target_prices = [
            result['valuations']['dcf']['value_per_share']
        ]
        
        if 'ddm' in result['valuations']:
            target_prices.append(result['valuations']['ddm']['value_per_share'])
        
        if target_prices:
            result['target_price'] = sum(target_prices) / len(target_prices)
        
        # 6. 计算上涨空间
        current_price = market_data.get('price', 0)
        if current_price > 0 and result['target_price'] > 0:
            result['upside_potential'] = (result['target_price'] - current_price) / current_price
        
        # 7. 投资建议
        if result['upside_potential'] > 0.2:
            result['recommendation'] = 'buy'
        elif result['upside_potential'] < -0.2:
            result['recommendation'] = 'sell'
        else:
            result['recommendation'] = 'hold'
        
        return result
    
    def save_report(self, report: Dict, symbol: str = 'TEST'):
        """保存估值报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_valuation_{timestamp}.json"
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath


def generate_test_data() -> Dict:
    """生成测试财务数据"""
    return {
        'symbol': 'TEST',
        'free_cash_flow': 100000,
        'shares_outstanding': 10000,
        'total_debt': 200000,
        'net_income_growth': 0.20,
        'annual_dividend': 2.0
    }


def generate_market_data() -> Dict:
    """生成测试市场数据"""
    return {
        'price': 50.0,
        'pe_ratio': 25.0,
        'pb_ratio': 3.0,
        'ps_ratio': 5.0
    }


def generate_peer_data() -> List[Dict]:
    """生成同行数据"""
    return [
        {'pe_ratio': 20.0, 'pb_ratio': 2.5, 'ps_ratio': 4.0},
        {'pe_ratio': 30.0, 'pb_ratio': 3.5, 'ps_ratio': 6.0},
        {'pe_ratio': 25.0, 'pb_ratio': 3.0, 'ps_ratio': 5.0},
        {'pe_ratio': 22.0, 'pb_ratio': 2.8, 'ps_ratio': 4.5},
    ]


logging.basicConfig(level=logging.INFO)
def main():
    """主函数"""
    print("=" * 70)
    print(" " * 25 + "SA-010: Valuation Model")
    print("=" * 70)
    
    model = ValuationModel()
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Generate Test Data")
        print("-" * 70)
        financial_data = generate_test_data()
        market_data = generate_market_data()
        peer_data = generate_peer_data()
        print(f"  Symbol: {financial_data['symbol']}")
        print(f"  Current Price: {market_data['price']:.2f}")
        print(f"  PE Ratio: {market_data['pe_ratio']:.2f}")
        
        print("\n[Test 2] DCF Valuation")
        print("-" * 70)
        dcf = model.dcf_valuation(financial_data)
        print(f"  {dcf['description']}")
        
        print("\n[Test 3] Relative Valuation")
        print("-" * 70)
        relative = model.relative_valuation(
            {
                'pe_ratio': market_data['pe_ratio'],
                'pb_ratio': market_data['pb_ratio'],
                'ps_ratio': market_data['ps_ratio']
            },
            peer_data
        )
        print(f"  {relative['description']}")
        
        print("\n[Test 4] PEG Valuation")
        print("-" * 70)
        peg = model.peg_valuation(market_data['pe_ratio'], financial_data['net_income_growth'])
        print(f"  {peg['description']}")
        
        print("\n[Test 5] DDM Valuation")
        print("-" * 70)
        ddm = model.ddm_valuation(financial_data)
        print(f"  {ddm['description']}")
        
        print("\n[Test 6] Comprehensive Valuation")
        print("-" * 70)
        comprehensive = model.comprehensive_valuation(financial_data, market_data, peer_data)
        print(f"  Current Price: {comprehensive['current_price']:.2f}")
        print(f"  Target Price: {comprehensive['target_price']:.2f}")
        print(f"  Upside Potential: {comprehensive['upside_potential']:.2%}")
        print(f"  Recommendation: {comprehensive['recommendation']}")
        
        print("\n[Test 7] Save Report")
        print("-" * 70)
        report_path = model.save_report(comprehensive, 'TEST')
        print(f"  Report saved to: {report_path}")
        
        print("\n" + "=" * 70)
        print(" SA-010 Valuation Model test completed")
        print("=" * 70)
    
    else:
        # 正常使用模式
        print("\nUsage: py sa_010_valuation_model.py --test")
        print("\nFeatures:")
        print("  - DCF valuation (discounted cash flow)")
        print("  - Relative valuation (PE/PB/PS vs peers)")
        print("  - PEG valuation (growth-adjusted)")
        print("  - DDM valuation (dividend discount model)")
        print("  - Comprehensive valuation with target price")
        print("  - Investment recommendation (buy/hold/sell)")
        print("  - Auto-save reports to 60-DATA/stock_valuation/")


if __name__ == '__main__':
    main()
