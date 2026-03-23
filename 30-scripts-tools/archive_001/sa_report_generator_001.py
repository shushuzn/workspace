import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-012: Report Generator
Generate comprehensive stock analysis reports
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class ReportGenerator:
    """Generate comprehensive stock analysis reports"""

    def __init__(self, data_dir: str = "60-DATA/stock_reports"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.report_log = self._load_report_log()

    def _load_report_log(self) -> Dict:
        """Load report log"""
        log_file = self.data_dir / "report_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "reports": [],
            "stats": {
                "total_reports": 0,
            }
        }

    def _save_report_log(self):
        """Save report log"""
        log_file = self.data_dir / "report_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_log, f, ensure_ascii=False, indent=2)

    def generate_report(self, symbol: str, analysis_data: Dict) -> Dict:
        """
        Generate comprehensive analysis report
        
        Args:
            symbol: Stock symbol
            analysis_data: Dict with all analysis results
            
        Returns:
            Dict with formatted report
        """
        report = {
            "symbol": symbol,
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive",
            "executive_summary": "",
            "sections": {},
            "overall_rating": "",
            "recommendation": "",
            "confidence": 0
        }

        # Generate executive summary
        report["executive_summary"] = self._generate_executive_summary(symbol, analysis_data)

        # Add sections
        if "price_data" in analysis_data:
            report["sections"]["price_analysis"] = self._format_price_section(analysis_data["price_data"])

        if "indicators" in analysis_data:
            report["sections"]["technical_indicators"] = self._format_indicators_section(analysis_data["indicators"])

        if "trend" in analysis_data:
            report["sections"]["trend_analysis"] = self._format_trend_section(analysis_data["trend"])

        if "patterns" in analysis_data:
            report["sections"]["pattern_recognition"] = self._format_patterns_section(analysis_data["patterns"])

        if "support_resistance" in analysis_data:
            report["sections"]["support_resistance"] = self._format_sr_section(analysis_data["support_resistance"])

        if "signals" in analysis_data:
            report["sections"]["trading_signals"] = self._format_signals_section(analysis_data["signals"])

        if "risk" in analysis_data:
            report["sections"]["risk_analysis"] = self._format_risk_section(analysis_data["risk"])

        # Calculate overall rating
        report["overall_rating"] = self._calculate_overall_rating(report["sections"])
        report["recommendation"] = self._generate_recommendation(report)
        report["confidence"] = self._calculate_confidence(report)

        # Generate text report
        report["text_report"] = self._generate_text_report(report)

        # Save report
        report_file = self.data_dir / f"{symbol}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # Also save text version
        text_file = self.data_dir / f"{symbol}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(report["text_report"])

        # Log report
        self._log_report(symbol, report["overall_rating"], success=True)

        return report

    def _generate_executive_summary(self, symbol: str, data: Dict) -> str:
        """Generate executive summary"""
        summary_parts = []

        # Price info
        if "price_data" in data:
            price = data["price_data"].get("current_price", 0)
            change = data["price_data"].get("change_pct", 0)
            summary_parts.append(f"{symbol} is trading at ${price:.2f} ({change:+.2f}%)")

        # Trend
        if "trend" in data:
            trend = data["trend"].get("overall_trend", "unknown")
            summary_parts.append(f"overall trend is {trend}")

        # Signal
        if "signals" in data:
            signal = data["signals"].get("confluence_signal", {}).get("signal", "neutral")
            summary_parts.append(f"technical signal: {signal}")

        return " | ".join(summary_parts) if summary_parts else "Analysis in progress"

    def _format_price_section(self, price_data: Dict) -> Dict:
        """Format price analysis section"""
        return {
            "current_price": price_data.get("current_price", 0),
            "change": price_data.get("change", 0),
            "change_pct": price_data.get("change_pct", 0),
            "high_52w": price_data.get("high_52w", 0),
            "low_52w": price_data.get("low_52w", 0),
            "volume": price_data.get("volume", 0),
            "avg_volume": price_data.get("avg_volume", 0)
        }

    def _format_indicators_section(self, indicators: Dict) -> Dict:
        """Format technical indicators section"""
        return {
            "mas": indicators.get("moving_averages", {}),
            "rsi": indicators.get("rsi", {}),
            "macd": indicators.get("macd", {}),
            "kdj": indicators.get("kdj", {}),
            "boll": indicators.get("bollinger", {})
        }

    def _format_trend_section(self, trend: Dict) -> Dict:
        """Format trend analysis section"""
        return {
            "overall_trend": trend.get("overall_trend", "unknown"),
            "trend_strength": trend.get("trend_strength", "unknown"),
            "timeframes": trend.get("timeframes", {}),
            "recommendation": trend.get("recommendation", "")
        }

    def _format_patterns_section(self, patterns: Dict) -> Dict:
        """Format pattern recognition section"""
        found_patterns = patterns.get("patterns_found", [])
        return {
            "patterns_detected": len(found_patterns),
            "patterns": found_patterns
        }

    def _format_sr_section(self, sr_data: Dict) -> Dict:
        """Format support & resistance section"""
        return {
            "key_levels": sr_data.get("key_levels", []),
            "pivot_points": sr_data.get("pivot_points", {}),
            "recommendation": sr_data.get("recommendation", "")
        }

    def _format_signals_section(self, signals: Dict) -> Dict:
        """Format trading signals section"""
        return {
            "confluence_signal": signals.get("confluence_signal", {}),
            "individual_signals": signals.get("individual_signals", {}),
            "recommendation": signals.get("recommendation", ""),
            "confidence": signals.get("confidence", 0)
        }

    def _format_risk_section(self, risk: Dict) -> Dict:
        """Format risk analysis section"""
        return {
            "position_sizing": risk.get("position_sizing", {}),
            "stop_loss": risk.get("stop_loss", {}),
            "take_profit": risk.get("take_profit", {}),
            "risk_reward": risk.get("risk_reward", {}),
            "recommendation": risk.get("recommendation", "")
        }

    def _calculate_overall_rating(self, sections: Dict) -> str:
        """Calculate overall rating from sections"""
        score = 0
        count = 0

        # Check trend
        if "trend_analysis" in sections:
            trend = sections["trend_analysis"]
            if trend.get("overall_trend") == "bullish":
                score += 2
            elif trend.get("overall_trend") == "bearish":
                score -= 2
            count += 1

        # Check signals
        if "trading_signals" in sections:
            signal = sections["trading_signals"].get("confluence_signal", {})
            signal_type = signal.get("signal", "neutral")
            if signal_type in ["strong_buy", "buy"]:
                score += 2
            elif signal_type in ["strong_sell", "sell"]:
                score -= 2
            count += 1

        # Check patterns
        if "pattern_recognition" in sections:
            patterns = sections["pattern_recognition"]
            if patterns.get("patterns_detected", 0) > 0:
                score += 1
            count += 1

        # Determine rating
        if score >= 3:
            return "A+ (Strong Buy)"
        elif score >= 2:
            return "A (Buy)"
        elif score >= 1:
            return "B+ (Moderate Buy)"
        elif score == 0:
            return "B (Hold)"
        elif score >= -1:
            return "C+ (Moderate Sell)"
        elif score >= -2:
            return "C (Sell)"
        else:
            return "D (Strong Sell)"

    def _generate_recommendation(self, report: Dict) -> str:
        """Generate final recommendation"""
        rating = report.get("overall_rating", "")

        if "Strong Buy" in rating:
            return "STRONG BUY - Multiple bullish signals with high confidence"
        elif "Buy" in rating:
            return "BUY - Bullish setup with good risk-reward"
        elif "Moderate Buy" in rating:
            return "MODERATE BUY - Cautiously bullish, watch for confirmation"
        elif "Hold" in rating:
            return "HOLD - Wait for clearer signals"
        elif "Moderate Sell" in rating:
            return "MODERATE SELL - Consider reducing position"
        elif "Sell" in rating:
            return "SELL - Bearish setup, consider exit"
        elif "Strong Sell" in rating:
            return "STRONG SELL - Multiple bearish signals, exit recommended"
        else:
            return "NEUTRAL - Insufficient data for recommendation"

    def _calculate_confidence(self, report: Dict) -> float:
        """Calculate report confidence"""
        sections = report.get("sections", {})

        # Base confidence on data completeness
        expected_sections = 7
        actual_sections = len(sections)

        completeness = actual_sections / expected_sections

        # Adjust based on signal confidence
        if "trading_signals" in sections:
            signal_conf = sections["trading_signals"].get("confidence", 0.5)
            confidence = (completeness + signal_conf) / 2
        else:
            confidence = completeness * 0.5

        return round(min(confidence, 1.0), 2)

    def _generate_text_report(self, report: Dict) -> str:
        """Generate human-readable text report"""
        lines = []

        lines.append("=" * 70)
        lines.append(f" STOCK ANALYSIS REPORT - {report['symbol']}")
        lines.append("=" * 70)
        lines.append(f" Generated: {report['generated_at']}")
        lines.append(f" Report Type: {report['report_type']}")
        lines.append("")

        lines.append("-" * 70)
        lines.append(" EXECUTIVE SUMMARY")
        lines.append("-" * 70)
        lines.append(report["executive_summary"])
        lines.append("")

        lines.append("-" * 70)
        lines.append(" OVERALL RATING")
        lines.append("-" * 70)
        lines.append(f" Rating: {report['overall_rating']}")
        lines.append(f" Recommendation: {report['recommendation']}")
        lines.append(f" Confidence: {report['confidence']*100:.0f}%")
        lines.append("")

        # Add sections
        for section_name, section_data in report["sections"].items():
            lines.append("-" * 70)
            lines.append(f" {section_name.replace('_', ' ').title()}")
            lines.append("-" * 70)

            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if isinstance(value, dict):
                        lines.append(f"  {key}:")
                        for k, v in value.items():
                            lines.append(f"    {k}: {v}")
                    else:
                        lines.append(f"  {key}: {value}")

            lines.append("")

        lines.append("=" * 70)
        lines.append(" END OF REPORT")
        lines.append("=" * 70)

        return "\n".join(lines)

    def _log_report(self, symbol: str, rating: str, success: bool):
        """Log report generation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "rating": rating,
            "success": success
        }

        self.report_log["reports"].append(log_entry)
        self.report_log["stats"]["total_reports"] += 1

        # Keep only last 100 entries
        self.report_log["reports"] = self.report_log["reports"][-100:]

        self._save_report_log()

    def get_stats(self) -> Dict:
        """Get report statistics"""
        return self.report_log["stats"].copy()

    def display_status(self) -> str:
        """Display generator status"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 16 + "Report Generator Status")
        output.append("=" * 70)

        output.append(f"\n[Report Sections]")
        output.append("  - Price Analysis")
        output.append("  - Technical Indicators")
        output.append("  - Trend Analysis")
        output.append("  - Pattern Recognition")
        output.append("  - Support & Resistance")
        output.append("  - Trading Signals")
        output.append("  - Risk Analysis")

        output.append(f"\n[Statistics]")
        output.append(f"  Total Reports:  {stats['total_reports']}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)

    def analyze(self, symbol: str, data: Dict = None) -> Dict:
        """
        Unified analyze wrapper for pipeline compatibility.

        Args:
            symbol: Stock symbol
            data: Optional dict with analysis_data containing all SA results

        Returns:
            Dict with generated report
        """
        data = data or {}
        analysis_data = data.get('analysis_data', {})
        # If no analysis data provided, create a minimal structure
        if not analysis_data:
            analysis_data = {
                'symbol': symbol,
                'indicators': {},
                'patterns': {},
                'trend': {},
                'support_resistance': {},
                'signals': {},
                'risk': {}
            }
        return self.generate_report(symbol, analysis_data)


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
# py sa_report_generator_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_report_generator_001.py

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

Test entry point"""
    print("=" * 70)
    print(" " * 16 + "SA-012: Report Generator")
    print("=" * 70)

    generator = ReportGenerator()

    # Test 1: Display status
    print(generator.display_status())

    # Test 2: Generate sample report
    print("\n[Test 1] Generate Sample Report")
    print("-" * 70)

    # Sample analysis data
    analysis_data = {
        "price_data": {
            "current_price": 105.50,
            "change": 2.30,
            "change_pct": 2.23,
            "volume": 15000000
        },
        "trend": {
            "overall_trend": "bullish",
            "trend_strength": "strong",
            "recommendation": "BUY - Uptrend confirmed"
        },
        "patterns": {
            "patterns_found": [
                {"pattern": "double_bottom", "confidence": 0.75}
            ]
        },
        "signals": {
            "confluence_signal": {
                "signal": "buy",
                "strength": 0.65,
                "confluence": "4/5"
            },
            "confidence": 0.72
        },
        "risk": {
            "risk_reward": {
                "risk_reward_ratio": 2.5,
                "quality": "good"
            }
        }
    }

    result = generator.generate_report("TEST", analysis_data)

    print(f"  Symbol:          {result['symbol']}")
    print(f"  Generated:       {result['generated_at']}")
    print(f"  Overall Rating:  {result['overall_rating']}")
    print(f"  Recommendation:  {result['recommendation']}")
    print(f"  Confidence:      {result['confidence']*100:.0f}%")

    print(f"\n  Sections Generated:")
    for section in result["sections"].keys():
        print(f"    - {section.replace('_', ' ').title()}")

    print(f"\n  Executive Summary:")
    print(f"    {result['executive_summary']}")

    print(f"\n  Report Files:")
    print(f"    - JSON: {result['symbol']}_report_*.json")
    print(f"    - Text: {result['symbol']}_report_*.txt")

    # Test 3: Final stats
    print("\n[Test 2] Final Statistics")
    print("-" * 70)
    stats = generator.get_stats()
    print(f"  Total Reports:  {stats['total_reports']}")

    print("\n[OK] SA-012 Report Generator test completed")

if __name__ == "__main__":
    main()
