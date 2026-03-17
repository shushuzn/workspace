#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Risk Monitor - Multi-Dimensional Stock Risk Monitoring System

Monitors 4 risk dimensions:
- Volatility Risk (price volatility anomalies)
- Correlation Risk (asset correlation breakdown)
- Liquidity Risk (volume/spread anomalies)
- Valuation Risk (valuation bubble detection)

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import os
import math
import statistics
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

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


class AlertLevel(Enum):
    """Alert level enumeration"""
    NORMAL = "Normal"
    WATCH = "Watch"
    WARNING = "Warning"
    CRITICAL = "Critical"


@dataclass
class RiskMetrics:
    """Risk metrics for a single stock"""
    symbol: str
    company_name: str
    timestamp: datetime
    
    # Price data
    current_price: float
    prices_20d: List[float]
    prices_60d: List[float]
    prices_252d: List[float]
    
    # Volume data
    current_volume: float
    volumes_20d: List[float]
    avg_volume_60d: float
    
    # Market data
    market_cap: float
    pe_ratio: float
    pb_ratio: float
    sector_pe_median: float
    historical_pe_percentile: float
    
    # Calculated metrics
    volatility_20d: float  # Annualized
    volatility_60d: float
    volatility_percentile: float
    
    beta: float
    correlation_to_market: float
    
    volume_ratio: float  # Current / Average
    turnover_rate: float
    
    valuation_z_score: float
    valuation_percentile: float
    
    # Risk scores (0-100, higher = more risk)
    volatility_risk: float
    correlation_risk: float
    liquidity_risk: float
    valuation_risk: float
    
    # Composite
    composite_risk_score: float
    alert_level: AlertLevel
    alerts: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'timestamp': self.timestamp.isoformat(),
            'current_price': self.current_price,
            'volatility_20d': self.volatility_20d,
            'volatility_percentile': self.volatility_percentile,
            'beta': self.beta,
            'correlation_to_market': self.correlation_to_market,
            'volume_ratio': self.volume_ratio,
            'turnover_rate': self.turnover_rate,
            'valuation_z_score': self.valuation_z_score,
            'valuation_percentile': self.valuation_percentile,
            'volatility_risk': self.volatility_risk,
            'correlation_risk': self.correlation_risk,
            'liquidity_risk': self.liquidity_risk,
            'valuation_risk': self.valuation_risk,
            'composite_risk_score': self.composite_risk_score,
            'alert_level': self.alert_level.value,
            'alerts': self.alerts
        }


class RiskMonitor:
    """Multi-dimensional risk monitoring engine"""
    
    def __init__(self):
        self.results: List[RiskMetrics] = []
        self.market_returns: List[float] = []  # For correlation calculation
        
    def calculate_volatility(self, prices: List[float], annualize: bool = True) -> float:
        """Calculate annualized volatility"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = [(prices[i] / prices[i-1]) - 1 for i in range(1, len(prices))]
        
        if len(returns) < 2:
            return 0.0
        
        # Standard deviation of returns
        std_dev = statistics.stdev(returns)
        
        # Annualize (252 trading days)
        if annualize:
            std_dev *= math.sqrt(252)
        
        return std_dev
    
    def calculate_beta(self, stock_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta (systematic risk)"""
        if len(stock_returns) < 60 or len(market_returns) < 60:
            return 1.0
        
        # Use last 60 days
        n = min(60, len(stock_returns), len(market_returns))
        stock_ret = stock_returns[-n:]
        market_ret = market_returns[-n:]
        
        # Covariance and variance
        mean_stock = statistics.mean(stock_ret)
        mean_market = statistics.mean(market_ret)
        
        covariance = sum((s - mean_stock) * (m - mean_market) for s, m in zip(stock_ret, market_ret)) / (n - 1)
        variance_market = sum((m - mean_market) ** 2 for m in market_ret) / (n - 1)
        
        beta = covariance / variance_market if variance_market > 0 else 1.0
        return beta
    
    def calculate_correlation(self, stock_returns: List[float], market_returns: List[float]) -> float:
        """Calculate correlation to market"""
        if len(stock_returns) < 60 or len(market_returns) < 60:
            return 0.0
        
        n = min(60, len(stock_returns), len(market_returns))
        stock_ret = stock_returns[-n:]
        market_ret = market_returns[-n:]
        
        try:
            correlation = statistics.correlation(stock_ret, market_ret)
            return correlation
        except (statistics.StatisticsError, AttributeError):
            # Fallback for Python < 3.10
            mean_stock = statistics.mean(stock_ret)
            mean_market = statistics.mean(market_ret)
            
            std_stock = statistics.stdev(stock_ret)
            std_market = statistics.stdev(market_ret)
            
            if std_stock == 0 or std_market == 0:
                return 0.0
            
            covariance = sum((s - mean_stock) * (m - mean_market) for s, m in zip(stock_ret, market_ret)) / (n - 1)
            correlation = covariance / (std_stock * std_market)
            return correlation
    
    def calculate_volatility_risk(
        self,
        current_volatility: float,
        historical_volatilities: List[float],
        beta: float
    ) -> Tuple[float, List[str]]:
        """
        Calculate volatility risk score (0-100)
        
        Higher = More risk
        """
        alerts = []
        risk_score = 0.0
        
        # Current vs historical percentile
        if historical_volatilities:
            sorted_vols = sorted(historical_volatilities)
            n_below = sum(1 for v in sorted_vols if v < current_volatility)
            percentile = n_below / len(sorted_vols) * 100
        else:
            percentile = 50.0
        
        # Score based on percentile
        if percentile > 90:
            risk_score += 40
            alerts.append(f"🔴 Volatility at {percentile:.0f}th percentile (very high)")
        elif percentile > 75:
            risk_score += 25
            alerts.append(f"🟠 Volatility at {percentile:.0f}th percentile (high)")
        elif percentile > 50:
            risk_score += 10
            alerts.append(f"🟡 Volatility at {percentile:.0f}th percentile (elevated)")
        
        # Beta risk
        if beta > 2.0:
            risk_score += 30
            alerts.append(f"🔴 High beta ({beta:.2f}), very sensitive to market")
        elif beta > 1.5:
            risk_score += 20
            alerts.append(f"🟠 Elevated beta ({beta:.2f}), sensitive to market")
        elif beta > 1.2:
            risk_score += 10
            alerts.append(f"🟡 Above-average beta ({beta:.2f})")
        elif beta < 0.5:
            risk_score += 10
            alerts.append(f"🟡 Low beta ({beta:.2f}), may miss market rallies")
        
        # Volatility spike detection
        if historical_volatilities:
            avg_vol = statistics.mean(historical_volatilities)
            vol_ratio = current_volatility / avg_vol if avg_vol > 0 else 1.0
            
            if vol_ratio > 2.0:
                risk_score += 30
                alerts.append(f"🔴 Volatility spike! {vol_ratio:.1f}x average")
            elif vol_ratio > 1.5:
                risk_score += 15
                alerts.append(f"🟠 Volatility increasing ({vol_ratio:.1f}x average)")
        
        return min(100, risk_score), alerts
    
    def calculate_correlation_risk(
        self,
        correlation: float,
        portfolio_correlations: Optional[List[float]] = None
    ) -> Tuple[float, List[str]]:
        """
        Calculate correlation risk score (0-100)
        
        Higher = More risk (diversification breakdown)
        """
        alerts = []
        risk_score = 0.0
        
        # High correlation to market (low diversification)
        if correlation > 0.9:
            risk_score += 40
            alerts.append(f"🔴 Very high correlation to market ({correlation:.2f})")
        elif correlation > 0.7:
            risk_score += 25
            alerts.append(f"🟠 High correlation to market ({correlation:.2f})")
        elif correlation > 0.5:
            risk_score += 10
            alerts.append(f"🟡 Moderate correlation to market ({correlation:.2f})")
        
        # Correlation breakdown (if portfolio data available)
        if portfolio_correlations and len(portfolio_correlations) > 1:
            avg_corr = statistics.mean(portfolio_correlations)
            if avg_corr > 0.8:
                risk_score += 30
                alerts.append(f"🔴 Portfolio correlation breakdown (avg {avg_corr:.2f})")
            elif avg_corr > 0.6:
                risk_score += 15
                alerts.append(f"🟠 Portfolio diversification low (avg {avg_corr:.2f})")
        
        return min(100, risk_score), alerts
    
    def calculate_liquidity_risk(
        self,
        volume_ratio: float,
        turnover_rate: float,
        market_cap: float
    ) -> Tuple[float, List[str]]:
        """
        Calculate liquidity risk score (0-100)
        
        Higher = More risk (liquidity drying up)
        """
        alerts = []
        risk_score = 0.0
        
        # Volume anomaly
        if volume_ratio < 0.3:
            risk_score += 40
            alerts.append(f"🔴 Very low volume ({volume_ratio:.2f}x average)")
        elif volume_ratio < 0.5:
            risk_score += 25
            alerts.append(f"🟠 Low volume ({volume_ratio:.2f}x average)")
        elif volume_ratio > 3.0:
            risk_score += 20
            alerts.append(f"🟠 Unusual volume spike ({volume_ratio:.2f}x average)")
        elif volume_ratio > 2.0:
            risk_score += 10
            alerts.append(f"🟡 Elevated volume ({volume_ratio:.2f}x average)")
        
        # Turnover rate
        if turnover_rate < 0.5:
            risk_score += 20
            alerts.append(f"🟡 Low turnover rate ({turnover_rate:.1f}%)")
        elif turnover_rate > 20:
            risk_score += 15
            alerts.append(f"🟡 Very high turnover ({turnover_rate:.1f}%)")
        
        # Market cap liquidity
        if market_cap < 1e9:  # < 1B
            risk_score += 20
            alerts.append(f"🟡 Small cap, may have liquidity issues")
        
        return min(100, risk_score), alerts
    
    def calculate_valuation_risk(
        self,
        pe_ratio: float,
        sector_pe_median: float,
        historical_pe_percentile: float
    ) -> Tuple[float, List[str]]:
        """
        Calculate valuation risk score (0-100)
        
        Higher = More risk (overvaluation)
        """
        alerts = []
        risk_score = 0.0
        
        # Historical percentile
        if historical_pe_percentile > 90:
            risk_score += 40
            alerts.append(f"🔴 PE at {historical_pe_percentile:.0f}th percentile (very expensive)")
        elif historical_pe_percentile > 75:
            risk_score += 25
            alerts.append(f"🟠 PE at {historical_pe_percentile:.0f}th percentile (expensive)")
        elif historical_pe_percentile > 50:
            risk_score += 10
            alerts.append(f"🟡 PE at {historical_pe_percentile:.0f}th percentile (above average)")
        
        # Sector comparison
        if sector_pe_median > 0:
            pe_ratio_vs_sector = pe_ratio / sector_pe_median
            if pe_ratio_vs_sector > 2.0:
                risk_score += 30
                alerts.append(f"🔴 PE {pe_ratio_vs_sector:.1f}x sector median")
            elif pe_ratio_vs_sector > 1.5:
                risk_score += 15
                alerts.append(f"🟠 PE {pe_ratio_vs_sector:.1f}x sector median")
            elif pe_ratio_vs_sector < 0.5:
                risk_score += 5
                alerts.append(f"🟡 PE below sector ({pe_ratio_vs_sector:.1f}x median)")
        
        # Absolute PE level
        if pe_ratio > 50:
            risk_score += 20
            alerts.append(f"🟠 Very high absolute PE ({pe_ratio:.1f})")
        elif pe_ratio > 30:
            risk_score += 10
            alerts.append(f"🟡 High absolute PE ({pe_ratio:.1f})")
        elif pe_ratio < 0:
            risk_score += 15
            alerts.append(f"🟡 Negative earnings (PE={pe_ratio:.1f})")
        
        return min(100, risk_score), alerts
    
    def determine_alert_level(self, composite_score: float, individual_risks: Dict[str, float]) -> AlertLevel:
        """Determine overall alert level"""
        # Critical if any dimension is critical
        if any(r >= 70 for r in individual_risks.values()) or composite_score >= 70:
            return AlertLevel.CRITICAL
        
        # Warning if composite is high or multiple dimensions elevated
        if composite_score >= 50 or sum(1 for r in individual_risks.values() if r >= 50) >= 2:
            return AlertLevel.WARNING
        
        # Watch if any dimension elevated
        if composite_score >= 30 or any(r >= 30 for r in individual_risks.values()):
            return AlertLevel.WATCH
        
        return AlertLevel.NORMAL
    
    def monitor_stock(
        self,
        symbol: str,
        company_name: str,
        price_data: Dict,
        market_data: Optional[List[float]] = None
    ) -> RiskMetrics:
        """
        Run complete risk monitoring analysis
        
        Args:
            symbol: Stock symbol
            company_name: Company name
            price_data: Dict with price/volume/valuation data
            market_data: Optional market returns for correlation
        
        Returns:
            RiskMetrics
        """
        # Extract data with defaults
        def get(data, key, default=None):
            return data.get(key, default) if data.get(key) is not None else default
        
        current_price = get(price_data, 'current_price', 100.0)
        prices_20d = get(price_data, 'prices_20d', [current_price] * 20)
        prices_60d = get(price_data, 'prices_60d', prices_20d * 3)
        prices_252d = get(price_data, 'prices_252d', prices_60d * 4)
        
        current_volume = get(price_data, 'current_volume', 1000000)
        volumes_20d = get(price_data, 'volumes_20d', [current_volume] * 20)
        avg_volume_60d = get(price_data, 'avg_volume_60d', current_volume)
        
        market_cap = get(price_data, 'market_cap', 100e9)
        pe_ratio = get(price_data, 'pe_ratio', 20.0)
        pb_ratio = get(price_data, 'pb_ratio', 3.0)
        sector_pe_median = get(price_data, 'sector_pe_median', 25.0)
        historical_pe_percentile = get(price_data, 'historical_pe_percentile', 50.0)
        
        # Calculate metrics
        volatility_20d = self.calculate_volatility(prices_20d)
        volatility_60d = self.calculate_volatility(prices_60d)
        
        # Volatility percentile (using 252d rolling)
        rolling_vols = [self.calculate_volatility(prices_252d[i:i+60]) for i in range(0, len(prices_252d)-60, 5)]
        vol_percentile = sum(1 for v in rolling_vols if v < volatility_60d) / len(rolling_vols) * 100 if rolling_vols else 50.0
        
        # Daily returns
        stock_returns = [(prices_20d[i] / prices_20d[i-1]) - 1 for i in range(1, len(prices_20d))]
        
        # Beta and correlation
        if market_data and len(market_data) >= 60:
            market_returns = market_data[-60:]
            beta = self.calculate_beta(stock_returns, market_returns)
            correlation = self.calculate_correlation(stock_returns, market_returns)
        else:
            beta = 1.0
            correlation = 0.7
        
        # Volume metrics
        volume_ratio = current_volume / avg_volume_60d if avg_volume_60d > 0 else 1.0
        turnover_rate = (current_volume * current_price) / market_cap * 100 if market_cap > 0 else 0.0
        
        # Valuation z-score
        valuation_z_score = (pe_ratio - sector_pe_median) / (sector_pe_median * 0.5) if sector_pe_median > 0 else 0.0
        
        # Calculate risk scores
        vol_risk, vol_alerts = self.calculate_volatility_risk(volatility_60d, rolling_vols, beta)
        corr_risk, corr_alerts = self.calculate_correlation_risk(correlation)
        liq_risk, liq_alerts = self.calculate_liquidity_risk(volume_ratio, turnover_rate, market_cap)
        val_risk, val_alerts = self.calculate_valuation_risk(pe_ratio, sector_pe_median, historical_pe_percentile)
        
        # Composite risk score (weighted average)
        composite = (
            vol_risk * 0.30 +
            corr_risk * 0.25 +
            liq_risk * 0.20 +
            val_risk * 0.25
        )
        
        # Determine alert level
        individual_risks = {
            'volatility': vol_risk,
            'correlation': corr_risk,
            'liquidity': liq_risk,
            'valuation': val_risk
        }
        alert_level = self.determine_alert_level(composite, individual_risks)
        
        # Combine all alerts
        all_alerts = vol_alerts + corr_alerts + liq_alerts + val_alerts
        
        result = RiskMetrics(
            symbol=symbol,
            company_name=company_name,
            timestamp=datetime.now(),
            current_price=current_price,
            prices_20d=prices_20d,
            prices_60d=prices_60d,
            prices_252d=prices_252d,
            current_volume=current_volume,
            volumes_20d=volumes_20d,
            avg_volume_60d=avg_volume_60d,
            market_cap=market_cap,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            sector_pe_median=sector_pe_median,
            historical_pe_percentile=historical_pe_percentile,
            volatility_20d=round(volatility_20d, 4),
            volatility_60d=round(volatility_60d, 4),
            volatility_percentile=round(vol_percentile, 1),
            beta=round(beta, 3),
            correlation_to_market=round(correlation, 3),
            volume_ratio=round(volume_ratio, 2),
            turnover_rate=round(turnover_rate, 2),
            valuation_z_score=round(valuation_z_score, 2),
            valuation_percentile=round(historical_pe_percentile, 1),
            volatility_risk=round(vol_risk, 1),
            correlation_risk=round(corr_risk, 1),
            liquidity_risk=round(liq_risk, 1),
            valuation_risk=round(val_risk, 1),
            composite_risk_score=round(composite, 1),
            alert_level=alert_level,
            alerts=all_alerts
        )
        
        self.results.append(result)
        return result
    
    def print_result(self, result: RiskMetrics):
        """Print detailed risk monitoring result"""
        alert_emoji = "🔴" if result.alert_level == AlertLevel.CRITICAL else "🟠" if result.alert_level == AlertLevel.WARNING else "🟡" if result.alert_level == AlertLevel.WATCH else "🟢"
        
        print(f"\n{'='*70}")
        print(f"{alert_emoji} RISK MONITORING REPORT: {result.symbol} - {result.company_name}")
        print(f"{'='*70}")
        print(f"Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"Current Price: ${result.current_price:.2f}")
        
        # Composite Risk
        risk_emoji = "🔴" if result.composite_risk_score >= 70 else "🟠" if result.composite_risk_score >= 50 else "🟡" if result.composite_risk_score >= 30 else "🟢"
        print(f"\n{risk_emoji} COMPOSITE RISK SCORE: {result.composite_risk_score:.1f}/100")
        print(f"   Alert Level: {result.alert_level.value}")
        
        # Volatility Risk
        vol_emoji = "🔴" if result.volatility_risk >= 70 else "🟠" if result.volatility_risk >= 50 else "🟡" if result.volatility_risk >= 30 else "🟢"
        print(f"\n📊 VOLATILITY RISK: {result.volatility_risk:.1f}/100 {vol_emoji}")
        print(f"   20d Volatility: {result.volatility_20d:.1%} (annualized)")
        print(f"   60d Volatility: {result.volatility_60d:.1%} (annualized)")
        print(f"   Volatility Percentile: {result.volatility_percentile:.0f}th")
        print(f"   Beta: {result.beta:.3f}")
        print(f"   Correlation to Market: {result.correlation_to_market:.3f}")
        
        # Correlation Risk
        corr_emoji = "🔴" if result.correlation_risk >= 70 else "🟠" if result.correlation_risk >= 50 else "🟡" if result.correlation_risk >= 30 else "🟢"
        print(f"\n🔗 CORRELATION RISK: {result.correlation_risk:.1f}/100 {corr_emoji}")
        print(f"   Diversification: {'Low' if result.correlation_risk >= 50 else 'Moderate' if result.correlation_risk >= 30 else 'Good'}")
        
        # Liquidity Risk
        liq_emoji = "🔴" if result.liquidity_risk >= 70 else "🟠" if result.liquidity_risk >= 50 else "🟡" if result.liquidity_risk >= 30 else "🟢"
        print(f"\n💧 LIQUIDITY RISK: {result.liquidity_risk:.1f}/100 {liq_emoji}")
        print(f"   Volume Ratio: {result.volume_ratio:.2f}x average")
        print(f"   Turnover Rate: {result.turnover_rate:.2f}%")
        print(f"   Market Cap: ${result.market_cap/1e9:.2f}B")
        
        # Valuation Risk
        val_emoji = "🔴" if result.valuation_risk >= 70 else "🟠" if result.valuation_risk >= 50 else "🟡" if result.valuation_risk >= 30 else "🟢"
        print(f"\n💰 VALUATION RISK: {result.valuation_risk:.1f}/100 {val_emoji}")
        print(f"   P/E Ratio: {result.pe_ratio:.1f}")
        print(f"   P/B Ratio: {result.pb_ratio:.1f}")
        print(f"   vs Sector: {result.pe_ratio/result.sector_pe_median:.1f}x median")
        print(f"   Historical Percentile: {result.valuation_percentile:.0f}th")
        
        # Alerts
        if result.alerts:
            print(f"\n🚨 ALERTS ({len(result.alerts)})")
            for alert in result.alerts:
                print(f"   {alert}")
        else:
            print(f"\n✅ No significant risk alerts")
        
        print(f"\n{'='*70}\n")
    
    def get_high_risk_stocks(self) -> List[RiskMetrics]:
        """Get all high risk stocks"""
        return [r for r in self.results if r.alert_level in [AlertLevel.CRITICAL, AlertLevel.WARNING]]
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        if not self.results:
            return {}
        
        return {
            'total_monitored': len(self.results),
            'critical': len([r for r in self.results if r.alert_level == AlertLevel.CRITICAL]),
            'warning': len([r for r in self.results if r.alert_level == AlertLevel.WARNING]),
            'watch': len([r for r in self.results if r.alert_level == AlertLevel.WATCH]),
            'normal': len([r for r in self.results if r.alert_level == AlertLevel.NORMAL]),
            'avg_composite_risk': sum(r.composite_risk_score for r in self.results) / len(self.results),
            'avg_volatility_risk': sum(r.volatility_risk for r in self.results) / len(self.results),
            'avg_correlation_risk': sum(r.correlation_risk for r in self.results) / len(self.results),
            'avg_liquidity_risk': sum(r.liquidity_risk for r in self.results) / len(self.results),
            'avg_valuation_risk': sum(r.valuation_risk for r in self.results) / len(self.results)
        }


def demo():
    """Run risk monitoring demo"""
    print("\n🔍 Risk Monitor Demo\n")
    
    monitor = RiskMonitor()
    
    # Simulate market data (60 days of returns)
    import random
    random.seed(42)
    market_returns = [random.gauss(0.0005, 0.015) for _ in range(60)]
    
    # Demo 1: Low risk stock (stable blue-chip)
    print("="*70)
    print("Demo 1: Low Risk Stock (Blue-chip)")
    print("="*70)
    
    random.seed(123)
    base_price = 150.0
    prices_20d_low = [base_price * (1 + random.gauss(0.001, 0.01)) ** i for i in range(20)]
    prices_60d_low = [base_price * (1 + random.gauss(0.001, 0.012)) ** i for i in range(60)]
    prices_252d_low = [base_price * (1 + random.gauss(0.001, 0.015)) ** i for i in range(252)]
    
    low_risk_data = {
        'current_price': prices_20d_low[-1],
        'prices_20d': prices_20d_low,
        'prices_60d': prices_60d_low,
        'prices_252d': prices_252d_low,
        'current_volume': 5000000,
        'volumes_20d': [5000000 * (1 + random.gauss(0, 0.2)) for _ in range(20)],
        'avg_volume_60d': 5000000,
        'market_cap': 500e9,
        'pe_ratio': 18.5,
        'pb_ratio': 4.2,
        'sector_pe_median': 22.0,
        'historical_pe_percentile': 35.0
    }
    
    result1 = monitor.monitor_stock('JNJ', 'Johnson & Johnson', low_risk_data, market_returns)
    monitor.print_result(result1)
    
    # Demo 2: High risk stock (volatile growth)
    print("="*70)
    print("Demo 2: High Risk Stock (Volatile Growth)")
    print("="*70)
    
    random.seed(456)
    base_price = 250.0
    prices_20d_high = [base_price * (1 + random.gauss(0.002, 0.04)) ** i for i in range(20)]
    prices_60d_high = [base_price * (1 + random.gauss(0.003, 0.05)) ** i for i in range(60)]
    prices_252d_high = [base_price * (1 + random.gauss(0.004, 0.06)) ** i for i in range(252)]
    
    high_risk_data = {
        'current_price': prices_20d_high[-1],
        'prices_20d': prices_20d_high,
        'prices_60d': prices_60d_high,
        'prices_252d': prices_252d_high,
        'current_volume': 500000,
        'volumes_20d': [500000 * (1 + random.gauss(0, 0.5)) for _ in range(20)],
        'avg_volume_60d': 2000000,
        'market_cap': 50e9,
        'pe_ratio': 85.0,
        'pb_ratio': 15.0,
        'sector_pe_median': 30.0,
        'historical_pe_percentile': 92.0
    }
    
    result2 = monitor.monitor_stock('NVDA', 'NVIDIA Corp', high_risk_data, market_returns)
    monitor.print_result(result2)
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    stats = monitor.get_statistics()
    print(f"Total Monitored: {stats['total_monitored']}")
    print(f"Critical: {stats['critical']}")
    print(f"Warning: {stats['warning']}")
    print(f"Watch: {stats['watch']}")
    print(f"Normal: {stats['normal']}")
    print(f"Average Composite Risk: {stats['avg_composite_risk']:.1f}/100")
    print(f"Average Volatility Risk: {stats['avg_volatility_risk']:.1f}/100")
    print(f"Average Valuation Risk: {stats['avg_valuation_risk']:.1f}/100")
    print("="*70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Risk Monitor')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--symbol', type=str, help='Stock symbol to monitor')
    args = parser.parse_args()
    
    if args.demo or not args.symbol:
        demo()
    else:
        print(f"Monitoring {args.symbol} requires price data input")
        print("Use --demo to see example")


if __name__ == "__main__":
    main()
