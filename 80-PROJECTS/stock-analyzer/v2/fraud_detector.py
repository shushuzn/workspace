#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fraud Detector - Financial Statement Fraud Detection

Detects potential financial fraud using 3 classic models:
- Beneish M-Score (earnings manipulation)
- Altman Z-Score (bankruptcy risk)
- Piotroski F-Score (financial health)

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import os
import math
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Workspace root
WORKSPACE = Path(__file__).parent.parent


@dataclass
class FraudDetectionResult:
    """Fraud detection result for a single stock"""
    symbol: str
    company_name: str
    
    # Beneish M-Score
    m_score: float
    m_score_manipulator: bool
    dsri: float  # Days Sales in Receivables Index
    gmi: float   # Gross Margin Index
    aqi: float   # Asset Quality Index
    sgi: float   # Sales Growth Index
    depi: float  # Depreciation Index
    sgai: float  # SG&A Index
    lvgi: float  # Leverage Index
    tati: float  # Total Accruals to Total Assets
    
    # Altman Z-Score
    z_score: float
    z_score_distress: str  # 'Distress'/'Grey'/'Safe'
    wc_ta: float  # Working Capital / Total Assets
    re_ta: float  # Retained Earnings / Total Assets
    ebit_ta: float  # EBIT / Total Assets
    mve_tl: float  # Market Value Equity / Total Liabilities
    s_ta: float  # Sales / Total Assets
    
    # Piotroski F-Score
    f_score: int
    f_score_grade: str  # 'Strong'/'Good'/'Weak'
    roa_positive: int
    cfo_positive: int
    roa_improving: int
    accrual_quality: int
    leverage_decreasing: int
    liquidity_improving: int
    equity_unchanged: int
    gm_improving: int
    turnover_improving: int
    
    # Composite
    composite_risk_score: float  # 0-100 (higher = more risk)
    risk_level: str  # 'Safe'/'Watch'/'Danger'/'High Risk'
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'm_score': self.m_score,
            'm_score_manipulator': self.m_score_manipulator,
            'z_score': self.z_score,
            'z_score_distress': self.z_score_distress,
            'f_score': self.f_score,
            'f_score_grade': self.f_score_grade,
            'composite_risk_score': self.composite_risk_score,
            'risk_level': self.risk_level,
            'recommendations': self.recommendations
        }


class FraudDetector:
    """Financial statement fraud detection engine"""
    
    def __init__(self):
        self.results: List[FraudDetectionResult] = []
        
    def calculate_beneish_m_score(
        self,
        receivables_current: float, receivables_prior: float,
        sales_current: float, sales_prior: float,
        cogs_current: float, cogs_prior: float,
        assets_current: float, assets_prior: float,
        ppe_current: float, ppe_prior: float,
        dep_current: float, dep_prior: float,
        sga_current: float, sga_prior: float,
        debt_current: float, debt_prior: float,
        ta_current: float,
        ni_current: float, cfo_current: float
    ) -> Tuple[float, bool, Dict]:
        """
        Calculate Beneish M-Score for earnings manipulation detection
        
        M-Score < -2.22: Unlikely manipulator
        M-Score > -2.22: Likely manipulator
        
        8 Variables:
        - DSRI: Days Sales in Receivables Index
        - GMI: Gross Margin Index
        - AQI: Asset Quality Index
        - SGI: Sales Growth Index
        - DEPI: Depreciation Index
        - SGAI: SG&A Index
        - LVGI: Leverage Index
        - TATI: Total Accruals to Total Assets
        """
        # DSRI - Days Sales in Receivables Index
        dsri_current = receivables_current / sales_current if sales_current > 0 else 0
        dsri_prior = receivables_prior / sales_prior if sales_prior > 0 else 0
        dsri = dsri_current / dsri_prior if dsri_prior > 0 else 1.0
        
        # GMI - Gross Margin Index
        gross_margin_current = (sales_current - cogs_current) / sales_current if sales_current > 0 else 0
        gross_margin_prior = (sales_prior - cogs_prior) / sales_prior if sales_prior > 0 else 0
        gmi = gross_margin_prior / gross_margin_current if gross_margin_current > 0 else 1.0
        
        # AQI - Asset Quality Index
        nca_current = assets_current - ppe_current - (receivables_current if receivables_current > 0 else 0)
        nca_prior = assets_prior - ppe_prior - (receivables_prior if receivables_prior > 0 else 0)
        aqi_current = nca_current / assets_current if assets_current > 0 else 0
        aqi_prior = nca_prior / assets_prior if assets_prior > 0 else 0
        aqi = aqi_current / aqi_prior if aqi_prior > 0 else 1.0
        
        # SGI - Sales Growth Index
        sgi = sales_current / sales_prior if sales_prior > 0 else 1.0
        
        # DEPI - Depreciation Index
        depi_current = dep_current / ppe_current if ppe_current > 0 else 0
        depi_prior = dep_prior / ppe_prior if ppe_prior > 0 else 0
        depi = depi_prior / depi_current if depi_current > 0 else 1.0
        
        # SGAI - SG&A Index
        sgai_current = sga_current / sales_current if sales_current > 0 else 0
        sgai_prior = sga_prior / sales_prior if sales_prior > 0 else 0
        sgai = sgai_current / sgai_prior if sgai_prior > 0 else 1.0
        
        # LVGI - Leverage Index
        lvgi_current = debt_current / ta_current if ta_current > 0 else 0
        lvgi_prior = debt_prior / assets_prior if assets_prior > 0 else 0
        lvgi = lvgi_current / lvgi_prior if lvgi_prior > 0 else 1.0
        
        # TATI - Total Accruals to Total Assets
        accruals = ni_current - cfo_current
        tati = accruals / ta_current if ta_current > 0 else 0
        
        # M-Score formula (Beneish 1999)
        m_score = (
            -4.84 +
            0.92 * math.log(dsri) +
            0.528 * math.log(gmi) +
            0.404 * math.log(aqi) +
            0.892 * math.log(sgi) +
            0.115 * math.log(depi) -
            0.172 * math.log(sgai) +
            4.679 * tati -
            0.327 * math.log(lvgi)
        )
        
        # Manipulator flag
        manipulator = m_score > -2.22
        
        variables = {
            'dsri': dsri,
            'gmi': gmi,
            'aqi': aqi,
            'sgi': sgi,
            'depi': depi,
            'sgai': sgai,
            'lvgi': lvgi,
            'tati': tati
        }
        
        return m_score, manipulator, variables
    
    def calculate_altman_z_score(
        self,
        working_capital: float,
        retained_earnings: float,
        ebit: float,
        market_value_equity: float,
        total_liabilities: float,
        sales: float,
        total_assets: float
    ) -> Tuple[float, str, Dict]:
        """
        Calculate Altman Z-Score for bankruptcy prediction
        
        Z-Score > 2.99: Safe
        1.81 < Z-Score < 2.99: Grey
        Z-Score < 1.81: Distress
        """
        # Ratios
        wc_ta = working_capital / total_assets if total_assets > 0 else 0
        re_ta = retained_earnings / total_assets if total_assets > 0 else 0
        ebit_ta = ebit / total_assets if total_assets > 0 else 0
        mve_tl = market_value_equity / total_liabilities if total_liabilities > 0 else 0
        s_ta = sales / total_assets if total_assets > 0 else 0
        
        # Z-Score formula (Altman 1968)
        z_score = (
            1.2 * wc_ta +
            1.4 * re_ta +
            3.3 * ebit_ta +
            0.6 * mve_tl +
            0.999 * s_ta
        )
        
        # Distress zone
        if z_score > 2.99:
            distress = 'Safe'
        elif z_score > 1.81:
            distress = 'Grey'
        else:
            distress = 'Distress'
        
        variables = {
            'wc_ta': wc_ta,
            're_ta': re_ta,
            'ebit_ta': ebit_ta,
            'mve_tl': mve_tl,
            's_ta': s_ta
        }
        
        return z_score, distress, variables
    
    def calculate_piotroski_f_score(
        self,
        roa_current: float,
        cfo_current: float,
        roa_prior: float,
        accruals: float,
        leverage_current: float,
        leverage_prior: float,
        liquidity_current: float,
        liquidity_prior: float,
        equity_issued: bool,
        gm_current: float,
        gm_prior: float,
        turnover_current: float,
        turnover_prior: float
    ) -> Tuple[int, str, Dict]:
        """
        Calculate Piotroski F-Score for financial health
        
        F-Score 7-9: Strong
        F-Score 4-6: Good
        F-Score 0-3: Weak
        """
        score = 0
        signals = {}
        
        # 1. ROA positive
        roa_pos = 1 if roa_current > 0 else 0
        score += roa_pos
        signals['roa_positive'] = roa_pos
        
        # 2. CFO positive
        cfo_pos = 1 if cfo_current > 0 else 0
        score += cfo_pos
        signals['cfo_positive'] = cfo_pos
        
        # 3. ROA improving
        roa_imp = 1 if roa_current > roa_prior else 0
        score += roa_imp
        signals['roa_improving'] = roa_imp
        
        # 4. Accrual quality (CFO > NI)
        accrual_qual = 1 if accruals > 0 else 0
        score += accrual_qual
        signals['accrual_quality'] = accrual_qual
        
        # 5. Leverage decreasing
        lev_dec = 1 if leverage_current < leverage_prior else 0
        score += lev_dec
        signals['leverage_decreasing'] = lev_dec
        
        # 6. Liquidity improving
        liq_imp = 1 if liquidity_current > liquidity_prior else 0
        score += liq_imp
        signals['liquidity_improving'] = liq_imp
        
        # 7. Equity unchanged (no dilution)
        eq_unchanged = 0 if equity_issued else 1
        score += eq_unchanged
        signals['equity_unchanged'] = eq_unchanged
        
        # 8. Gross margin improving
        gm_imp = 1 if gm_current > gm_prior else 0
        score += gm_imp
        signals['gm_improving'] = gm_imp
        
        # 9. Asset turnover improving
        turn_imp = 1 if turnover_current > turnover_prior else 0
        score += turn_imp
        signals['turnover_improving'] = turn_imp
        
        # Grade
        if score >= 7:
            grade = 'Strong'
        elif score >= 4:
            grade = 'Good'
        else:
            grade = 'Weak'
        
        return score, grade, signals
    
    def calculate_composite_risk(
        self,
        m_score: float,
        m_manipulator: bool,
        z_score: float,
        z_distress: str,
        f_score: int
    ) -> Tuple[float, str, List[str]]:
        """
        Calculate composite risk score (0-100)
        
        Higher = More risk
        """
        risk_score = 0.0
        recommendations = []
        
        # M-Score component (40%)
        if m_manipulator:
            # Scale: -2.22 = 50, -1.0 = 100
            m_component = min(100, max(50, 50 + (m_score + 2.22) * 40))
            recommendations.append(f"⚠️  Beneish M-Score indicates potential earnings manipulation (M={m_score:.3f})")
        else:
            m_component = max(0, min(40, (m_score + 2.22) * 30))
        
        risk_score += m_component * 0.4
        
        # Z-Score component (35%)
        if z_distress == 'Distress':
            z_component = min(100, max(60, 100 - z_score * 30))
            recommendations.append(f"🚨 Altman Z-Score in distress zone (Z={z_score:.3f})")
        elif z_distress == 'Grey':
            z_component = 40 + (2.99 - z_score) * 30
            recommendations.append(f"⚠️  Altman Z-Score in grey zone (Z={z_score:.3f})")
        else:
            z_component = max(0, min(30, (2.99 - z_score) * 15))
        
        risk_score += z_component * 0.35
        
        # F-Score component (25%)
        if f_score <= 3:
            f_component = 80 + (3 - f_score) * 5
            recommendations.append(f"🚨 Piotroski F-Score weak (F={f_score}/9)")
        elif f_score <= 6:
            f_component = 30 + (6 - f_score) * 15
        else:
            f_component = max(0, 10 - (f_score - 7) * 3)
        
        risk_score += f_component * 0.25
        
        # Risk level
        if risk_score >= 70:
            risk_level = 'High Risk'
        elif risk_score >= 50:
            risk_level = 'Danger'
        elif risk_score >= 30:
            risk_level = 'Watch'
        else:
            risk_level = 'Safe'
            recommendations.append("✅ Financial statements appear healthy")
        
        return risk_score, risk_level, recommendations
    
    def detect_fraud(
        self,
        symbol: str,
        company_name: str,
        financial_data: Dict
    ) -> FraudDetectionResult:
        """
        Run complete fraud detection analysis
        
        Args:
            symbol: Stock symbol
            company_name: Company name
            financial_data: Dict with all required financial data
        
        Returns:
            FraudDetectionResult
        """
        # Extract data with defaults
        def get(data, key, default=0.0):
            return data.get(key, default) if data.get(key) is not None else default
        
        # Beneish M-Score
        m_score, m_manipulator, m_vars = self.calculate_beneish_m_score(
            receivables_current=get(financial_data, 'receivables_current'),
            receivables_prior=get(financial_data, 'receivables_prior'),
            sales_current=get(financial_data, 'sales_current'),
            sales_prior=get(financial_data, 'sales_prior'),
            cogs_current=get(financial_data, 'cogs_current'),
            cogs_prior=get(financial_data, 'cogs_prior'),
            assets_current=get(financial_data, 'assets_current'),
            assets_prior=get(financial_data, 'assets_prior'),
            ppe_current=get(financial_data, 'ppe_current'),
            ppe_prior=get(financial_data, 'ppe_prior'),
            dep_current=get(financial_data, 'dep_current'),
            dep_prior=get(financial_data, 'dep_prior'),
            sga_current=get(financial_data, 'sga_current'),
            sga_prior=get(financial_data, 'sga_prior'),
            debt_current=get(financial_data, 'debt_current'),
            debt_prior=get(financial_data, 'debt_prior'),
            ta_current=get(financial_data, 'ta_current'),
            ni_current=get(financial_data, 'ni_current'),
            cfo_current=get(financial_data, 'cfo_current')
        )
        
        # Altman Z-Score
        z_score, z_distress, z_vars = self.calculate_altman_z_score(
            working_capital=get(financial_data, 'working_capital'),
            retained_earnings=get(financial_data, 'retained_earnings'),
            ebit=get(financial_data, 'ebit'),
            market_value_equity=get(financial_data, 'market_value_equity'),
            total_liabilities=get(financial_data, 'total_liabilities'),
            sales=get(financial_data, 'sales'),
            total_assets=get(financial_data, 'total_assets')
        )
        
        # Piotroski F-Score
        f_score, f_grade, f_signals = self.calculate_piotroski_f_score(
            roa_current=get(financial_data, 'roa_current'),
            cfo_current=get(financial_data, 'cfo_current'),
            roa_prior=get(financial_data, 'roa_prior'),
            accruals=get(financial_data, 'accruals'),
            leverage_current=get(financial_data, 'leverage_current'),
            leverage_prior=get(financial_data, 'leverage_prior'),
            liquidity_current=get(financial_data, 'liquidity_current'),
            liquidity_prior=get(financial_data, 'liquidity_prior'),
            equity_issued=financial_data.get('equity_issued', False),
            gm_current=get(financial_data, 'gm_current'),
            gm_prior=get(financial_data, 'gm_prior'),
            turnover_current=get(financial_data, 'turnover_current'),
            turnover_prior=get(financial_data, 'turnover_prior')
        )
        
        # Composite risk
        risk_score, risk_level, recommendations = self.calculate_composite_risk(
            m_score=m_score,
            m_manipulator=m_manipulator,
            z_score=z_score,
            z_distress=z_distress,
            f_score=f_score
        )
        
        result = FraudDetectionResult(
            symbol=symbol,
            company_name=company_name,
            m_score=round(m_score, 4),
            m_score_manipulator=m_manipulator,
            z_score=round(z_score, 4),
            z_score_distress=z_distress,
            f_score=f_score,
            f_score_grade=f_grade,
            composite_risk_score=round(risk_score, 2),
            risk_level=risk_level,
            recommendations=recommendations,
            dsri=round(m_vars['dsri'], 4),
            gmi=round(m_vars['gmi'], 4),
            aqi=round(m_vars['aqi'], 4),
            sgi=round(m_vars['sgi'], 4),
            depi=round(m_vars['depi'], 4),
            sgai=round(m_vars['sgai'], 4),
            lvgi=round(m_vars['lvgi'], 4),
            tati=round(m_vars['tati'], 4),
            wc_ta=round(z_vars['wc_ta'], 4),
            re_ta=round(z_vars['re_ta'], 4),
            ebit_ta=round(z_vars['ebit_ta'], 4),
            mve_tl=round(z_vars['mve_tl'], 4),
            s_ta=round(z_vars['s_ta'], 4),
            roa_positive=f_signals['roa_positive'],
            cfo_positive=f_signals['cfo_positive'],
            roa_improving=f_signals['roa_improving'],
            accrual_quality=f_signals['accrual_quality'],
            leverage_decreasing=f_signals['leverage_decreasing'],
            liquidity_improving=f_signals['liquidity_improving'],
            equity_unchanged=f_signals['equity_unchanged'],
            gm_improving=f_signals['gm_improving'],
            turnover_improving=f_signals['turnover_improving']
        )
        
        self.results.append(result)
        return result
    
    def print_result(self, result: FraudDetectionResult):
        """Print detailed fraud detection result"""
        print(f"\n{'='*70}")
        print(f"🔍 FRAUD DETECTION REPORT: {result.symbol} - {result.company_name}")
        print(f"{'='*70}")
        
        # Composite Risk
        risk_emoji = "🚨" if result.risk_level == 'High Risk' else "⚠️" if result.risk_level == 'Danger' else "⚡" if result.risk_level == 'Watch' else "✅"
        print(f"\n{risk_emoji} COMPOSITE RISK SCORE: {result.composite_risk_score:.1f}/100")
        print(f"   Risk Level: {result.risk_level}")
        
        # Beneish M-Score
        m_emoji = "🚨" if result.m_score_manipulator else "✅"
        print(f"\n📊 BENEISH M-SCORE (Earnings Manipulation)")
        print(f"   {m_emoji} M-Score: {result.m_score:.4f} {'(Likely Manipulator)' if result.m_score_manipulator else '(Unlikely Manipulator)'}")
        print(f"   Threshold: -2.22")
        print(f"   Components:")
        print(f"     - DSRI (Receivables): {result.dsri:.3f}")
        print(f"     - GMI (Gross Margin): {result.gmi:.3f}")
        print(f"     - AQI (Asset Quality): {result.aqi:.3f}")
        print(f"     - SGI (Sales Growth): {result.sgi:.3f}")
        print(f"     - DEPI (Depreciation): {result.depi:.3f}")
        print(f"     - SGAI (SG&A): {result.sgai:.3f}")
        print(f"     - LVGI (Leverage): {result.lvgi:.3f}")
        print(f"     - TATI (Accruals): {result.tati:.3f}")
        
        # Altman Z-Score
        z_emoji = "🚨" if result.z_score_distress == 'Distress' else "⚠️" if result.z_score_distress == 'Grey' else "✅"
        print(f"\n📈 ALTMAN Z-SCORE (Bankruptcy Risk)")
        print(f"   {z_emoji} Z-Score: {result.z_score:.4f} ({result.z_score_distress} Zone)")
        print(f"   Zones: Safe (>2.99) | Grey (1.81-2.99) | Distress (<1.81)")
        print(f"   Components:")
        print(f"     - WC/TA (Working Capital): {result.wc_ta:.3f}")
        print(f"     - RE/TA (Retained Earnings): {result.re_ta:.3f}")
        print(f"     - EBIT/TA (Operating Profit): {result.ebit_ta:.3f}")
        print(f"     - MVE/TL (Market Value): {result.mve_tl:.3f}")
        print(f"     - S/TA (Asset Turnover): {result.s_ta:.3f}")
        
        # Piotroski F-Score
        f_emoji = "✅" if result.f_score_grade == 'Strong' else "⚠️" if result.f_score_grade == 'Good' else "🚨"
        print(f"\n🎯 PIOTROSKI F-SCORE (Financial Health)")
        print(f"   {f_emoji} F-Score: {result.f_score}/9 ({result.f_score_grade})")
        print(f"   Grades: Strong (7-9) | Good (4-6) | Weak (0-3)")
        print(f"   Signals:")
        print(f"     {'✅' if result.roa_positive else '❌'} ROA Positive")
        print(f"     {'✅' if result.cfo_positive else '❌'} CFO Positive")
        print(f"     {'✅' if result.roa_improving else '❌'} ROA Improving")
        print(f"     {'✅' if result.accrual_quality else '❌'} Accrual Quality")
        print(f"     {'✅' if result.leverage_decreasing else '❌'} Leverage Decreasing")
        print(f"     {'✅' if result.liquidity_improving else '❌'} Liquidity Improving")
        print(f"     {'✅' if result.equity_unchanged else '❌'} No Equity Dilution")
        print(f"     {'✅' if result.gm_improving else '❌'} Gross Margin Improving")
        print(f"     {'✅' if result.turnover_improving else '❌'} Asset Turnover Improving")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        for rec in result.recommendations:
            print(f"   {rec}")
        
        print(f"\n{'='*70}\n")
    
    def get_high_risk_stocks(self) -> List[FraudDetectionResult]:
        """Get all high risk stocks"""
        return [r for r in self.results if r.risk_level in ['High Risk', 'Danger']]
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        if not self.results:
            return {}
        
        return {
            'total_analyzed': len(self.results),
            'high_risk': len([r for r in self.results if r.risk_level == 'High Risk']),
            'danger': len([r for r in self.results if r.risk_level == 'Danger']),
            'watch': len([r for r in self.results if r.risk_level == 'Watch']),
            'safe': len([r for r in self.results if r.risk_level == 'Safe']),
            'manipulators': len([r for r in self.results if r.m_score_manipulator]),
            'distress': len([r for r in self.results if r.z_score_distress == 'Distress']),
            'weak_f_score': len([r for r in self.results if r.f_score <= 3]),
            'avg_risk_score': sum(r.composite_risk_score for r in self.results) / len(self.results)
        }


def demo():
    """Run fraud detection demo"""
    print("\n🔍 Fraud Detector Demo\n")
    
    detector = FraudDetector()
    
    # Demo 1: Healthy company (Apple-like)
    print("="*70)
    print("Demo 1: Healthy Company (Apple-like)")
    print("="*70)
    
    healthy_data = {
        'receivables_current': 30000, 'receivables_prior': 28000,
        'sales_current': 380000, 'sales_prior': 365000,
        'cogs_current': 220000, 'cogs_prior': 210000,
        'assets_current': 350000, 'assets_prior': 330000,
        'ppe_current': 45000, 'ppe_prior': 43000,
        'dep_current': 11000, 'dep_prior': 10500,
        'sga_current': 25000, 'sga_prior': 24000,
        'debt_current': 120000, 'debt_prior': 115000,
        'ta_current': 350000,
        'ni_current': 95000, 'cfo_current': 100000,
        'working_capital': 50000,
        'retained_earnings': 180000,
        'ebit': 110000,
        'market_value_equity': 2800000,
        'total_liabilities': 120000,
        'sales': 380000,
        'total_assets': 350000,
        'roa_current': 0.27, 'cfo_current': 100000, 'roa_prior': 0.25,
        'accruals': -5000,
        'leverage_current': 0.34, 'leverage_prior': 0.35,
        'liquidity_current': 1.5, 'liquidity_prior': 1.4,
        'equity_issued': False,
        'gm_current': 0.42, 'gm_prior': 0.41,
        'turnover_current': 1.09, 'turnover_prior': 1.05
    }
    
    result1 = detector.detect_fraud('AAPL', 'Apple Inc.', healthy_data)
    detector.print_result(result1)
    
    # Demo 2: Distressed company
    print("="*70)
    print("Demo 2: Distressed Company")
    print("="*70)
    
    distressed_data = {
        'receivables_current': 15000, 'receivables_prior': 8000,
        'sales_current': 50000, 'sales_prior': 65000,
        'cogs_current': 45000, 'cogs_prior': 50000,
        'assets_current': 80000, 'assets_prior': 90000,
        'ppe_current': 20000, 'ppe_prior': 25000,
        'dep_current': 3000, 'dep_prior': 4000,
        'sga_current': 8000, 'sga_prior': 7000,
        'debt_current': 60000, 'debt_prior': 50000,
        'ta_current': 80000,
        'ni_current': -10000, 'cfo_current': -5000,
        'working_capital': -15000,
        'retained_earnings': -30000,
        'ebit': -8000,
        'market_value_equity': 20000,
        'total_liabilities': 60000,
        'sales': 50000,
        'total_assets': 80000,
        'roa_current': -0.125, 'cfo_current': -5000, 'roa_prior': -0.08,
        'accruals': -5000,
        'leverage_current': 0.75, 'leverage_prior': 0.65,
        'liquidity_current': 0.8, 'liquidity_prior': 0.9,
        'equity_issued': True,
        'gm_current': 0.10, 'gm_prior': 0.23,
        'turnover_current': 0.625, 'turnover_prior': 0.72
    }
    
    result2 = detector.detect_fraud('RISK', 'Distressed Corp', distressed_data)
    detector.print_result(result2)
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    stats = detector.get_statistics()
    print(f"Total Analyzed: {stats['total_analyzed']}")
    print(f"High Risk: {stats['high_risk']}")
    print(f"Danger: {stats['danger']}")
    print(f"Watch: {stats['watch']}")
    print(f"Safe: {stats['safe']}")
    print(f"Potential Manipulators: {stats['manipulators']}")
    print(f"Bankruptcy Distress: {stats['distress']}")
    print(f"Weak F-Score: {stats['weak_f_score']}")
    print(f"Average Risk Score: {stats['avg_risk_score']:.1f}/100")
    print("="*70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Financial Fraud Detector')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--symbol', type=str, help='Stock symbol to analyze')
    args = parser.parse_args()
    
    if args.demo or not args.symbol:
        demo()
    else:
        print(f"Analysis for {args.symbol} requires financial data input")
        print("Use --demo to see example")


if __name__ == "__main__":
    main()
