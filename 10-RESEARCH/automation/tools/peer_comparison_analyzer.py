#!/usr/bin/env python3
"""
Industry Peer Comparison Analyzer
Compare stocks within same industry

Features:
- Automatic industry classification (GICS)
- Peer group identification
- Multi-metric comparison (P/E, P/S, growth, margins)
- Relative valuation scoring
- Industry ranking

Schedule: Weekly Monday 6AM
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class CompanyMetrics:
    """Company fundamental metrics"""
    ticker: str
    name: str
    industry: str
    sector: str
    market_cap: float  # USD
    pe_ratio: float
    ps_ratio: float
    pb_ratio: float
    peg_ratio: float
    revenue_growth: float  # YoY %
    profit_margin: float  # %
    roe: float  # %
    debt_to_equity: float
    current_ratio: float
    
    def to_dict(self):
        return asdict(self)


class IndustryClassifier:
    """GICS industry classification"""
    
    # Simplified GICS mapping
    SECTORS = {
        'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD'],
        'Communication': ['GOOGL', 'META', 'DIS', 'NFLX', 'CMCSA', 'VZ', 'T'],
        'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW'],
        'Healthcare': ['UNH', 'JNJ', 'LLY', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT'],
        'Financials': ['BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS'],
        'Industrials': ['CAT', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'BA'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
        'Consumer Staples': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'PM'],
        'Utilities': ['NEE', 'DUK', 'SO', 'D'],
        'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX'],
        'Materials': ['LIN', 'APD', 'SHW', 'FCX']
    }
    
    @classmethod
    def get_sector(cls, ticker: str) -> str:
        """Get sector for ticker"""
        ticker = ticker.upper().replace('.', '')
        for sector, tickers in cls.SECTORS.items():
            if ticker in [t.replace('.', '') for t in tickers]:
                return sector
        return 'Other'
    
    @classmethod
    def get_peers(cls, ticker: str, include_self: bool = False) -> List[str]:
        """Get peer tickers in same sector"""
        sector = cls.get_sector(ticker)
        peers = cls.SECTORS.get(sector, [])
        
        ticker_clean = ticker.upper().replace('.', '')
        if not include_self:
            peers = [p for p in peers if p.replace('.', '') != ticker_clean]
        
        return peers[:10]  # Top 10 peers


class PeerComparator:
    """Compare companies with peers"""
    
    def __init__(self):
        self.companies: Dict[str, CompanyMetrics] = {}
    
    def add_company(self, metrics: CompanyMetrics):
        """Add company metrics"""
        self.companies[metrics.ticker] = metrics
    
    def load_demo_data(self):
        """Load demo metrics"""
        demo_companies = [
            CompanyMetrics('AAPL', 'Apple Inc.', 'Consumer Electronics', 'Technology', 2800e9, 29.5, 7.8, 45.2, 2.1, 0.02, 0.256, 1.47, 1.8, 2.1),
            CompanyMetrics('MSFT', 'Microsoft Corp.', 'Software', 'Technology', 3100e9, 36.2, 12.5, 12.8, 2.5, 0.15, 0.382, 0.45, 1.9, 2.5),
            CompanyMetrics('GOOGL', 'Alphabet Inc.', 'Internet Content', 'Technology', 1800e9, 25.8, 6.2, 6.5, 1.8, 0.12, 0.245, 0.12, 2.8, 3.2),
            CompanyMetrics('NVDA', 'NVIDIA Corp.', 'Semiconductors', 'Technology', 2200e9, 72.5, 35.2, 52.3, 1.5, 0.58, 0.485, 0.85, 1.5, 3.8),
            CompanyMetrics('META', 'Meta Platforms', 'Internet Content', 'Technology', 1200e9, 28.3, 8.5, 7.2, 1.2, 0.25, 0.298, 0.18, 2.2, 3.5),
            CompanyMetrics('AMZN', 'Amazon.com', 'Internet Retail', 'Consumer Discretionary', 1900e9, 62.5, 3.2, 8.5, 2.8, 0.10, 0.078, 0.22, 1.8, 1.4),
            CompanyMetrics('TSLA', 'Tesla Inc.', 'Automobiles', 'Consumer Discretionary', 800e9, 75.2, 8.5, 15.2, 3.5, 0.35, 0.145, 0.28, 1.2, 1.8),
        ]
        
        for company in demo_companies:
            self.add_company(company)
    
    def compare_metrics(self, ticker: str) -> Dict:
        """Compare single company with peers"""
        if ticker not in self.companies:
            return {}
        
        company = self.companies[ticker]
        sector = company.sector
        
        # Get sector peers
        peers = [c for t, c in self.companies.items() if c.sector == sector and t != ticker]
        
        if not peers:
            return {}
        
        # Calculate sector averages
        avg_metrics = {
            'pe_ratio': sum(p.pe_ratio for p in peers) / len(peers),
            'ps_ratio': sum(p.ps_ratio for p in peers) / len(peers),
            'revenue_growth': sum(p.revenue_growth for p in peers) / len(peers),
            'profit_margin': sum(p.profit_margin for p in peers) / len(peers),
            'roe': sum(p.roe for p in peers) / len(peers)
        }
        
        # Compare
        comparison = {
            'ticker': ticker,
            'sector': sector,
            'peer_count': len(peers),
            'metrics': {},
            'relative_valuation': {}
        }
        
        # P/E comparison
        pe_vs_avg = (company.pe_ratio - avg_metrics['pe_ratio']) / avg_metrics['pe_ratio'] * 100
        comparison['metrics']['pe_ratio'] = {
            'company': company.pe_ratio,
            'peer_avg': avg_metrics['pe_ratio'],
            'vs_avg': f"{pe_vs_avg:+.1f}%",
            'assessment': 'Overvalued' if pe_vs_avg > 20 else 'Undervalued' if pe_vs_avg < -20 else 'Fair'
        }
        
        # P/S comparison
        ps_vs_avg = (company.ps_ratio - avg_metrics['ps_ratio']) / avg_metrics['ps_ratio'] * 100
        comparison['metrics']['ps_ratio'] = {
            'company': company.ps_ratio,
            'peer_avg': avg_metrics['ps_ratio'],
            'vs_avg': f"{ps_vs_avg:+.1f}%",
            'assessment': 'Overvalued' if ps_vs_avg > 20 else 'Undervalued' if ps_vs_avg < -20 else 'Fair'
        }
        
        # Growth comparison
        growth_vs_avg = (company.revenue_growth - avg_metrics['revenue_growth']) / max(abs(avg_metrics['revenue_growth']), 0.01) * 100
        comparison['metrics']['revenue_growth'] = {
            'company': company.revenue_growth * 100,
            'peer_avg': avg_metrics['revenue_growth'] * 100,
            'vs_avg': f"{growth_vs_avg:+.1f}%",
            'assessment': 'Above Avg' if growth_vs_avg > 10 else 'Below Avg' if growth_vs_avg < -10 else 'Average'
        }
        
        # Margin comparison
        margin_vs_avg = (company.profit_margin - avg_metrics['profit_margin']) / max(abs(avg_metrics['profit_margin']), 0.01) * 100
        comparison['metrics']['profit_margin'] = {
            'company': company.profit_margin * 100,
            'peer_avg': avg_metrics['profit_margin'] * 100,
            'vs_avg': f"{margin_vs_avg:+.1f}%",
            'assessment': 'Above Avg' if margin_vs_avg > 10 else 'Below Avg' if margin_vs_avg < -10 else 'Average'
        }
        
        # ROE comparison
        roe_vs_avg = (company.roe - avg_metrics['roe']) / max(abs(avg_metrics['roe']), 0.01) * 100
        comparison['metrics']['roe'] = {
            'company': company.roe * 100,
            'peer_avg': avg_metrics['roe'] * 100,
            'vs_avg': f"{roe_vs_avg:+.1f}%",
            'assessment': 'Above Avg' if roe_vs_avg > 10 else 'Below Avg' if roe_vs_avg < -10 else 'Average'
        }
        
        # Overall relative valuation score (0-100)
        score = 50  # Start at neutral
        
        # Adjust based on metrics
        if pe_vs_avg < 0: score += 10  # Cheaper P/E
        if pe_vs_avg < -20: score += 15  # Much cheaper
        
        if ps_vs_avg < 0: score += 10
        if ps_vs_avg < -20: score += 15
        
        if growth_vs_avg > 0: score += 10  # Higher growth
        if growth_vs_avg > 20: score += 15
        
        if margin_vs_avg > 0: score += 10
        if margin_vs_avg > 20: score += 15
        
        if roe_vs_avg > 0: score += 10
        if roe_vs_avg > 20: score += 15
        
        score = max(0, min(100, score))
        
        comparison['relative_valuation'] = {
            'score': score,
            'rating': 'Strong Buy' if score >= 80 else 'Buy' if score >= 65 else 'Hold' if score >= 45 else 'Sell' if score >= 25 else 'Strong Sell',
            'summary': f"Score {score}/100 vs sector peers"
        }
        
        return comparison
    
    def sector_ranking(self, sector: str = None) -> List[Dict]:
        """Rank all companies in sector"""
        if sector:
            companies = [c for c in self.companies.values() if c.sector == sector]
        else:
            companies = list(self.companies.values())
        
        rankings = []
        for company in companies:
            comparison = self.compare_metrics(company.ticker)
            if comparison:
                rankings.append({
                    'ticker': company.ticker,
                    'name': company.name,
                    'score': comparison['relative_valuation']['score'],
                    'rating': comparison['relative_valuation']['rating']
                })
        
        # Sort by score
        rankings.sort(key=lambda x: -x['score'])
        
        # Add rank
        for i, r in enumerate(rankings, 1):
            r['rank'] = i
        
        return rankings
    
    def generate_report(self) -> str:
        """Generate comparison report"""
        report = []
        report.append("="*70)
        report.append("📊 Industry Peer Comparison Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("="*70)
        
        # Sector summary
        sectors = set(c.sector for c in self.companies.values())
        report.append(f"\n📈 Sectors Covered: {len(sectors)}")
        report.append(f"  Total companies: {len(self.companies)}")
        
        # By sector rankings
        for sector in sorted(sectors):
            report.append(f"\n{'='*70}")
            report.append(f"🏢 {sector} Sector Ranking")
            report.append("="*70)
            
            rankings = self.sector_ranking(sector)
            
            for r in rankings:
                medal = "🥇" if r['rank'] == 1 else "🥈" if r['rank'] == 2 else "🥉" if r['rank'] == 3 else "  "
                report.append(f"  {medal} #{r['rank']} ${r['ticker']} - {r['name'][:30]:30} Score: {r['score']:3.0f}/100 ({r['rating']})")
        
        # Detailed comparison for top companies
        report.append(f"\n{'='*70}")
        report.append("📋 Detailed Metric Comparison")
        report.append("="*70)
        
        for ticker in list(self.companies.keys())[:5]:
            comparison = self.compare_metrics(ticker)
            if comparison:
                report.append(f"\n${ticker} ({comparison['sector']}):")
                for metric, data in comparison['metrics'].items():
                    report.append(f"  {metric:15}: {data['company']:8.2f} (peer avg: {data['peer_avg']:8.2f}) {data['vs_avg']:>8} - {data['assessment']}")
                report.append(f"  → Valuation: {comparison['relative_valuation']['summary']}")
        
        return "\n".join(report)
    
    def save(self, filename: str = None):
        """Save comparison data"""
        if not filename:
            filename = f"peer_comparison_{datetime.now().strftime('%Y%m%d')}.json"
        
        filepath = Path("D:\\OpenClaw\\workspace\\data") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'companies': {t: c.to_dict() for t, c in self.companies.items()},
            'rankings': {
                sector: self.sector_ranking(sector)
                for sector in set(c.sector for c in self.companies.values())
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved peer comparison: {filepath}")
        return filepath


def main():
    """Demo/test peer comparator"""
    print("="*70)
    print("📊 Industry Peer Comparison Analyzer")
    print("="*70)
    
    comparator = PeerComparator()
    comparator.load_demo_data()
    
    # Generate report
    report = comparator.generate_report()
    print("\n" + report)
    
    # Save
    comparator.save()
    
    print("\n✅ Peer comparison complete!")
    print("="*70)


if __name__ == "__main__":
    main()
