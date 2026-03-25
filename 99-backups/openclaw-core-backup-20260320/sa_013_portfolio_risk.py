#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-013: Portfolio Risk Analyzer
Multi-stock portfolio risk analysis (correlation, VaR, diversification)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class PortfolioRiskAnalyzer:
    """Analyze risk for multi-stock portfolios"""

    def __init__(self, data_dir: str = "60-DATA/stock_portfolio"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.analysis_log = self._load_analysis_log()

    def _load_analysis_log(self) -> Dict:
        """Load analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "analyses": [],
            "stats": {
                "total_analyses": 0,
                "portfolios_analyzed": 0,
            }
        }

    def _save_analysis_log(self):
        """Save analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_log, f, ensure_ascii=False, indent=2)

    def calculate_correlation_matrix(self, returns_data: Dict[str, List[float]]) -> Dict:
        """
        Calculate correlation matrix for multiple stocks
        
        Args:
            returns_data: Dict of symbol -> list of returns
            
        Returns:
            Dict with correlation matrix
        """
        symbols = list(returns_data.keys())
        n = len(symbols)

        if n < 2:
            return {"error": "Need at least 2 stocks for correlation"}

        # Check data length
        min_len = min(len(data) for data in returns_data.values())
        if min_len < 10:
            return {"error": "Insufficient data (need at least 10 periods)"}

        # Trim to same length
        trimmed_data = {s: data[-min_len:] for s, data in returns_data.items()}

        # Calculate correlations
        correlation_matrix = {}

        for i, sym1 in enumerate(symbols):
            correlation_matrix[sym1] = {}
            for j, sym2 in enumerate(symbols):
                if i == j:
                    correlation_matrix[sym1][sym2] = 1.0
                elif j < i:
                    # Use symmetry
                    correlation_matrix[sym1][sym2] = correlation_matrix[sym2][sym1]
                else:
                    # Calculate correlation
                    corr = self._calculate_correlation(
                        trimmed_data[sym1],
                        trimmed_data[sym2]
                    )
                    correlation_matrix[sym1][sym2] = round(corr, 3)

        return {
            "symbols": symbols,
            "correlation_matrix": correlation_matrix,
            "periods": min_len,
            "calculated_at": datetime.now().isoformat()
        }

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))

        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)

        denominator = math.sqrt(sum_sq_x * sum_sq_y)

        if denominator == 0:
            return 0

        return numerator / denominator

    def calculate_var(self, returns: List[float], confidence: float = 0.95,
                     method: str = "historical") -> Dict:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: List of returns
            confidence: Confidence level (e.g., 0.95 for 95%)
            method: Calculation method (historical/parametric)
            
        Returns:
            Dict with VaR results
        """
        if not returns or len(returns) < 10:
            return {"error": "Insufficient data"}

        sorted_returns = sorted(returns)
        n = len(sorted_returns)

        if method == "historical":
            # Historical VaR
            index = int((1 - confidence) * n)
            var = sorted_returns[max(0, index)]

            return {
                "method": "historical",
                "confidence": confidence,
                "var": round(var, 4),
                "var_pct": round(var * 100, 2),
                "interpretation": f"{confidence *100:.0f}% confident max loss won't exceed {var *100:.2f}%"
            }

        elif method == "parametric":
            # Parametric VaR (assuming normal distribution)
            mean = sum(returns) / n
            variance = sum((r - mean) ** 2 for r in returns) / n
            std = math.sqrt(variance)

            # Z-score for confidence levels
            z_scores = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}
            z = z_scores.get(confidence, 1.645)

            var = mean - z * std

            return {
                "method": "parametric",
                "confidence": confidence,
                "mean": round(mean, 4),
                "std": round(std, 4),
                "var": round(var, 4),
                "var_pct": round(var * 100, 2),
                "interpretation": f"{confidence *100:.0f}% confident max loss won't exceed {var *100:.2f}%"
            }

        return {"error": "Unknown method"}

    def calculate_portfolio_var(self, positions: Dict[str, Dict],
                               returns_data: Dict[str, List[float]],
                               correlation_matrix: Dict,
                               confidence: float = 0.95) -> Dict:
        """
        Calculate portfolio-level VaR
        
        Args:
            positions: Dict of symbol -> {value, weight}
            returns_data: Dict of symbol -> returns
            correlation_matrix: Correlation matrix
            confidence: Confidence level
            
        Returns:
            Dict with portfolio VaR
        """
        symbols = list(positions.keys())

        if len(symbols) < 2:
            return {"error": "Need at least 2 positions"}

        # Calculate portfolio variance
        portfolio_variance = 0

        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                weight1 = positions[sym1].get("weight", 0)
                weight2 = positions[sym2].get("weight", 0)

                # Get individual variances
                returns1 = returns_data.get(sym1, [])
                returns2 = returns_data.get(sym2, [])

                if not returns1 or not returns2:
                    continue

                var1 = self._calculate_variance(returns1)
                var2 = self._calculate_variance(returns2)
                std1 = math.sqrt(var1)
                std2 = math.sqrt(var2)

                # Get correlation
                corr = correlation_matrix.get(sym1, {}).get(sym2, 0)

                # Add to portfolio variance
                portfolio_variance += weight1 * weight2 * std1 * std2 * corr

        portfolio_std = math.sqrt(abs(portfolio_variance))

        # Calculate portfolio VaR (parametric)
        z_scores = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}
        z = z_scores.get(confidence, 1.645)

        total_value = sum(pos.get("value", 0) for pos in positions.values())
        portfolio_var = total_value * z * portfolio_std

        return {
            "confidence": confidence,
            "portfolio_std": round(portfolio_std, 4),
            "portfolio_var": round(portfolio_var, 2),
            "portfolio_var_pct": round(z * portfolio_std * 100, 2),
            "total_value": round(total_value, 2),
            "interpretation": f"{confidence *100:.0f}% confident max 1-day loss won't exceed ${portfolio_var:,.2f}"
        }

    def _calculate_variance(self, returns: List[float]) -> float:
        """Calculate variance of returns"""
        if not returns:
            return 0

        n = len(returns)
        mean = sum(returns) / n
        variance = sum((r - mean) ** 2 for r in returns) / n
        return variance

    def calculate_diversification_score(self, positions: Dict[str, Dict],
                                       correlation_matrix: Dict) -> Dict:
        """
        Calculate portfolio diversification score
        
        Args:
            positions: Dict of symbol -> {value, weight}
            correlation_matrix: Correlation matrix
            
        Returns:
            Dict with diversification analysis
        """
        symbols = list(positions.keys())
        n = len(symbols)

        if n < 2:
            return {"error": "Need at least 2 positions"}

        # Calculate average correlation
        total_corr = 0
        count = 0

        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i < j:
                    corr = correlation_matrix.get(sym1, {}).get(sym2, 0)
                    total_corr += corr
                    count += 1

        avg_correlation = total_corr / count if count > 0 else 0

        # Calculate concentration (Herfindahl index)
        hhi = sum(pos.get("weight", 0) ** 2 for pos in positions.values())

        # Diversification score (0-100)
        # Lower correlation + lower concentration = higher diversification
        corr_score = (1 - avg_correlation) / 2 * 50  # 0-50
        conc_score = (1 - math.sqrt(hhi)) * 50  # 0-50

        diversification_score = corr_score + conc_score

        # Rating
        if diversification_score >= 80:
            rating = "Excellent"
        elif diversification_score >= 60:
            rating = "Good"
        elif diversification_score >= 40:
            rating = "Fair"
        else:
            rating = "Poor"

        return {
            "diversification_score": round(diversification_score, 1),
            "rating": rating,
            "avg_correlation": round(avg_correlation, 3),
            "correlation_score": round(corr_score, 1),
            "concentration_score": round(conc_score, 1),
            "hhi": round(hhi, 4),
            "num_positions": n,
            "interpretation": self._interpret_diversification(diversification_score)
        }

    def _interpret_diversification(self, score: float) -> str:
        """Interpret diversification score"""
        if score >= 80:
            return "Well diversified across uncorrelated assets"
        elif score >= 60:
            return "Good diversification with some concentration"
        elif score >= 40:
            return "Moderate diversification, consider adding uncorrelated assets"
        else:
            return "Poor diversification, high concentration risk"

    def analyze_portfolio(self, portfolio_name: str, positions: Dict[str, Dict],
                         returns_data: Dict[str, List[float]]) -> Dict:
        """
        Comprehensive portfolio risk analysis
        
        Args:
            portfolio_name: Portfolio name
            positions: Dict of symbol -> {value, weight}
            returns_data: Dict of symbol -> returns
            
        Returns:
            Dict with complete analysis
        """
        result = {
            "portfolio_name": portfolio_name,
            "analyzed_at": datetime.now().isoformat(),
            "positions": positions,
            "total_value": sum(pos.get("value", 0) for pos in positions.values()),
            "correlation_analysis": {},
            "var_analysis": {},
            "diversification_analysis": {},
            "risk_concentration": {},
            "recommendations": []
        }

        # Correlation analysis
        result["correlation_analysis"] = self.calculate_correlation_matrix(returns_data)

        # Individual VaR
        individual_vars = {}
        for symbol, returns in returns_data.items():
            var_result = self.calculate_var(returns, confidence=0.95, method="historical")
            if "error" not in var_result:
                individual_vars[symbol] = var_result
        result["var_analysis"]["individual_var"] = individual_vars

        # Correlation matrix for portfolio VaR
        corr_matrix = result["correlation_analysis"].get("correlation_matrix", {})

        # Portfolio VaR
        if corr_matrix:
            portfolio_var = self.calculate_portfolio_var(
                positions, returns_data, corr_matrix, confidence=0.95
            )
            result["var_analysis"]["portfolio_var"] = portfolio_var

        # Diversification analysis
        result["diversification_analysis"] = self.calculate_diversification_score(
            positions, corr_matrix
        )

        # Risk concentration
        result["risk_concentration"] = self._analyze_risk_concentration(positions, returns_data)

        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(result)

        # Save to cache
        cache_file = self.data_dir / f"{portfolio_name}_risk_analysis.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Log analysis
        self._log_analysis(portfolio_name, result["diversification_analysis"].get("rating", ""), success=True)

        return result

    def _analyze_risk_concentration(self, positions: Dict, returns_data: Dict) -> Dict:
        """Analyze risk concentration"""
        # Calculate individual risk contributions
        risk_contributions = {}

        for symbol, pos in positions.items():
            weight = pos.get("weight", 0)
            returns = returns_data.get(symbol, [])

            if returns:
                risk = self._calculate_variance(returns)
                risk_contributions[symbol] = {
                    "weight": round(weight, 3),
                    "risk": round(risk, 6),
                    "contribution": round(weight * math.sqrt(risk), 4) if risk > 0 else 0
                }

        # Find largest contributor
        if risk_contributions:
            max_contributor = max(risk_contributions.items(),
                                 key=lambda x: x[1]["contribution"])

            return {
                "contributions": risk_contributions,
                "largest_contributor": max_contributor[0],
                "largest_contribution": max_contributor[1]["contribution"]
            }

        return {"contributions": {}, "largest_contributor": None}

    def _generate_recommendations(self, result: Dict) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []

        # Check diversification
        div_score = result.get("diversification_analysis", {}).get("diversification_score", 0)
        if div_score < 40:
            recommendations.append("Add uncorrelated assets to improve diversification")

        # Check concentration
        risk_conc = result.get("risk_concentration", {})
        if risk_conc.get("largest_contribution", 0) > 0.5:
            recommendations.append(f"Reduce exposure to {risk_conc.get('largest_contributor', 'largest position')}")

        # Check correlations
        corr_analysis = result.get("correlation_analysis", {})
        if corr_analysis:
            avg_corr = corr_analysis.get("avg_correlation", 0)
            if avg_corr > 0.7:
                recommendations.append("High average correlation - consider adding low-correlation assets")

        # Check VaR
        var_analysis = result.get("var_analysis", {}).get("portfolio_var", {})
        if var_analysis:
            var_pct = var_analysis.get("portfolio_var_pct", 0)
            if var_pct > 5:
                recommendations.append(f"High portfolio VaR ({var_pct:.1f}%) - consider risk reduction")

        if not recommendations:
            recommendations.append("Portfolio risk metrics within acceptable ranges")

        return recommendations

    def _log_analysis(self, portfolio: str, rating: str, success: bool):
        """Log analysis attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "portfolio": portfolio,
            "rating": rating,
            "success": success
        }

        self.analysis_log["analyses"].append(log_entry)
        self.analysis_log["stats"]["total_analyses"] += 1
        self.analysis_log["stats"]["portfolios_analyzed"] += 1

        # Keep only last 100 entries
        self.analysis_log["analyses"] = self.analysis_log["analyses"][-100:]

        self._save_analysis_log()

    def get_stats(self) -> Dict:
        """Get analysis statistics"""
        return self.analysis_log["stats"].copy()

    def display_status(self) -> str:
        """Display analyzer status"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 14 + "Portfolio Risk Analyzer Status")
        output.append("=" * 70)

        output.append(f"\n[Analysis Features]")
        output.append("  - Correlation Matrix")
        output.append("  - Value at Risk (VaR)")
        output.append("  - Diversification Score")
        output.append("  - Risk Concentration")

        output.append(f"\n[Statistics]")
        output.append(f"  Total Analyses:       {stats['total_analyses']}")
        output.append(f"  Portfolios Analyzed:  {stats['portfolios_analyzed']}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 14 + "SA-013: Portfolio Risk Analyzer")
    print("=" * 70)

    analyzer = PortfolioRiskAnalyzer()

    # Test 1: Display status
    print(analyzer.display_status())

    # Test 2: Analyze sample portfolio
    print("\n[Test 1] Analyze Sample Portfolio")
    print("-" * 70)

    import random
    random.seed(42)

    # Generate sample returns data
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
    returns_data = {}

    for symbol in symbols:
        # Generate correlated-ish returns
        base_return = random.uniform(-0.001, 0.002)
        returns = [base_return + random.uniform(-0.02, 0.02) for _ in range(100)]
        returns_data[symbol] = returns

    # Sample positions
    positions = {
        "AAPL": {"value": 40000, "weight": 0.4},
        "GOOGL": {"value": 30000, "weight": 0.3},
        "MSFT": {"value": 20000, "weight": 0.2},
        "AMZN": {"value": 10000, "weight": 0.1}
    }

    result = analyzer.analyze_portfolio("TEST_PORTFOLIO", positions, returns_data)

    print(f"  Portfolio:      {result['portfolio_name']}")
    print(f"  Total Value:    ${result['total_value']:,.0f}")
    print(f"  Positions:      {len(positions)}")

    print(f"\n  Correlation Analysis:")
    corr = result.get("correlation_analysis", {})
    if "correlation_matrix" in corr:
        matrix = corr["correlation_matrix"]
        for sym1 in matrix:
            corrs = [f"{sym2}: {matrix[sym1][sym2]:.3f}" for sym2 in matrix[sym1]]
            print(f"    {sym1}: {', '.join(corrs)}")

    print(f"\n  VaR Analysis:")
    var_data = result.get("var_analysis", {}).get("portfolio_var", {})
    if var_data:
        print(f"    Portfolio VaR (95%): ${var_data.get('portfolio_var', 0):,.2f} ({var_data.get('portfolio_var_pct', 0):.2f}%)")
        print(f"    {var_data.get('interpretation', '')}")

    print(f"\n  Diversification:")
    div = result.get("diversification_analysis", {})
    print(f"    Score: {div.get('diversification_score', 0):.1f}/100 ({div.get('rating', 'N/A')})")
    print(f"    Avg Correlation: {div.get('avg_correlation', 0):.3f}")

    print(f"\n  Recommendations:")
    for i, rec in enumerate(result.get("recommendations", []), 1):
        print(f"    {i}. {rec}")

    # Test 3: Final stats
    print("\n[Test 2] Final Statistics")
    print("-" * 70)
    stats = analyzer.get_stats()
    print(f"  Total Analyses:       {stats['total_analyses']}")
    print(f"  Portfolios Analyzed:  {stats['portfolios_analyzed']}")

    print("\n[OK] SA-013 Portfolio Risk Analyzer test completed")

if __name__ == "__main__":
    main()
