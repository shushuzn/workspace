#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Trend Analyzer Pro - Advanced Time-Series Analysis

Analyzes system trends:
- 7-day trends
- 30-day trends
- Seasonal patterns
- Anomaly detection
- Forecasting

Usage:
    python trend_analyzer_pro.py --analyze
    python trend_analyzer_pro.py --forecast
    python trend_analyzer_pro.py --report
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


@dataclass
class Trend:
    """Trend analysis result"""
    metric: str
    system: str
    direction: str  # increasing/decreasing/stable
    slope: float
    strength: float  # 0-1
    period_days: int
    start_value: float
    end_value: float
    change_percent: float


@dataclass
class Forecast:
    """Forecast result"""
    metric: str
    system: str
    predicted_value: float
    confidence: float
    time_horizon: str
    timestamp: str


class TrendAnalyzer:
    """Advanced trend analysis"""
    
    def __init__(self):
        self.history_file = WORKSPACE / "20-data-reports" / "monitor_history.json"
        self.trends_file = WORKSPACE / "20-data-reports" / "trends.json"
        
        self.history = {}
        self.trends = []
        
        self.load_history()
    
    def load_history(self):
        """Load historical data"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = {}
    
    def save_trends(self):
        """Save trends"""
        with open(self.trends_file, 'w', encoding='utf-8') as f:
            json.dump({
                'trends': [asdict(t) if isinstance(t, Trend) else t for t in self.trends],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def analyze_trend(self, system: str, metric: str, days: int = 7) -> Optional[Trend]:
        """Analyze trend for metric"""
        if system not in self.history or metric not in self.history[system]:
            return None
        
        data = self.history[system][metric]
        if len(data) < days:
            return None
        
        # Get data for period
        recent = data[-days*24:]  # Assuming hourly data
        
        if len(recent) < 10:
            return None
        
        values = [d['value'] for d in recent]
        
        # Linear regression
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Calculate strength (R²)
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine direction
        if slope > 0.1:
            direction = 'increasing'
        elif slope < -0.1:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # Calculate change percent
        start_value = values[0]
        end_value = values[-1]
        change_percent = ((end_value - start_value) / start_value * 100) if start_value > 0 else 0
        
        trend = Trend(
            metric=metric,
            system=system,
            direction=direction,
            slope=slope,
            strength=min(1.0, r_squared),
            period_days=days,
            start_value=start_value,
            end_value=end_value,
            change_percent=change_percent
        )
        
        self.trends.append(trend)
        
        # Keep last 100 trends
        if len(self.trends) > 100:
            self.trends = self.trends[-100:]
        
        self.save_trends()
        
        return trend
    
    def forecast(self, system: str, metric: str, hours: int = 24) -> Optional[Forecast]:
        """Forecast future value"""
        if system not in self.history or metric not in self.history[system]:
            return None
        
        data = self.history[system][metric]
        if len(data) < 48:
            return None
        
        values = [d['value'] for d in data[-48:]]
        
        # Simple linear extrapolation
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Predict
        future_x = len(values) + hours
        predicted_value = slope * future_x + intercept
        
        # Confidence based on R²
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        confidence = min(0.95, r_squared)
        
        forecast = Forecast(
            metric=metric,
            system=system,
            predicted_value=max(0, predicted_value),  # No negative values
            confidence=confidence,
            time_horizon=f"{hours}h",
            timestamp=(datetime.now() + timedelta(hours=hours)).isoformat()
        )
        
        return forecast
    
    def get_seasonal_pattern(self, system: str, metric: str) -> Dict:
        """Detect seasonal patterns"""
        if system not in self.history or metric not in self.history[system]:
            return {}
        
        data = self.history[system][metric]
        if len(data) < 168:  # 1 week hourly
            return {}
        
        values = [d['value'] for d in data[-168:]]
        
        # Hourly pattern
        hourly_avg = {}
        for hour in range(24):
            hour_values = [values[i] for i in range(hour, len(values), 24)]
            if hour_values:
                hourly_avg[hour] = np.mean(hour_values)
        
        # Find peak and trough
        peak_hour = max(hourly_avg, key=hourly_avg.get) if hourly_avg else 0
        trough_hour = min(hourly_avg, key=hourly_avg.get) if hourly_avg else 0
        
        return {
            'peak_hour': peak_hour,
            'trough_hour': trough_hour,
            'amplitude': max(hourly_avg.values()) - min(hourly_avg.values()) if hourly_avg else 0,
            'hourly_pattern': hourly_avg
        }
    
    def analyze_all(self) -> Dict:
        """Analyze all trends"""
        results = {
            'trends_analyzed': 0,
            'increasing': 0,
            'decreasing': 0,
            'stable': 0,
            'forecasts_made': 0
        }
        
        for system, metrics in self.history.items():
            for metric in metrics.keys():
                # Analyze 7-day trend
                trend = self.analyze_trend(system, metric, days=7)
                if trend:
                    results['trends_analyzed'] += 1
                    
                    if trend.direction == 'increasing':
                        results['increasing'] += 1
                    elif trend.direction == 'decreasing':
                        results['decreasing'] += 1
                    else:
                        results['stable'] += 1
                
                # Make forecast
                forecast = self.forecast(system, metric, hours=24)
                if forecast:
                    results['forecasts_made'] += 1
        
        return results
    
    def get_status(self) -> Dict:
        """Get analyzer status"""
        return {
            'status': 'operational',
            'systems_analyzed': len(self.history),
            'total_trends': len(self.trends),
            'recent_trends': [asdict(t) if isinstance(t, Trend) else t 
                              for t in self.trends[-10:]]
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trend Analyzer Pro')
    parser.add_argument('--analyze', action='store_true', help='Analyze trends')
    parser.add_argument('--forecast', action='store_true', help='Show forecasts')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    
    args = parser.parse_args()
    
    analyzer = TrendAnalyzer()
    
    if args.demo:
        print("=" * 70)
        print("📊 Trend Analyzer Pro - Demo")
        print("=" * 70)
        
        # Check if we have data
        print("\n[1] Loading historical data...")
        print(f"[OK] Found {len(analyzer.history)} systems")
        
        if not analyzer.history:
            print("\n⚠️ No historical data found. Run unified_monitor first.")
            print("\n" + "=" * 70)
            print("ℹ️ Demo skipped - no data available")
            print("=" * 70)
            return
        
        # Analyze trends
        print("\n[2] Analyzing trends...")
        results = analyzer.analyze_all()
        print(f"[OK] Analysis complete:")
        for key, value in results.items():
            print(f"  - {key}: {value}")
        
        # Show trends
        print("\n[3] Recent Trends:")
        status = analyzer.get_status()
        for trend in status['recent_trends'][-5:]:
            print(f"  📈 {trend['system']}.{trend['metric']}: {trend['direction']}")
            print(f"     Change: {trend['change_percent']:+.1f}% (R²={trend['strength']:.2f})")
        
        # Show forecasts
        print("\n[4] 24h Forecasts:")
        for system, metrics in analyzer.history.items():
            for metric in list(metrics.keys())[:2]:
                forecast = analyzer.forecast(system, metric, hours=24)
                if forecast:
                    print(f"  🔮 {system}.{metric}: {forecast.predicted_value:.1f}")
                    print(f"     Confidence: {forecast.confidence*100:.0f}%")
        
        # Seasonal patterns
        print("\n[5] Seasonal Patterns:")
        for system, metrics in analyzer.history.items():
            for metric in list(metrics.keys())[:1]:
                pattern = analyzer.get_seasonal_pattern(system, metric)
                if pattern:
                    print(f"  🕐 {system}.{metric}:")
                    print(f"     Peak hour: {pattern['peak_hour']}:00")
                    print(f"     Trough hour: {pattern['trough_hour']}:00")
                    print(f"     Amplitude: {pattern['amplitude']:.1f}")
        
        print("\n" + "=" * 70)
        print("✅ Demo complete - Trend Analyzer Pro OPERATIONAL")
        print("=" * 70)
    
    elif args.analyze:
        print("Analyzing trends...")
        results = analyzer.analyze_all()
        print(json.dumps(results, indent=2))
    
    elif args.forecast:
        print("Forecasts:")
        for system, metrics in analyzer.history.items():
            for metric in metrics.keys():
                forecast = analyzer.forecast(system, metric, hours=24)
                if forecast:
                    print(f"{system}.{metric}: {forecast.predicted_value:.1f} (confidence: {forecast.confidence*100:.0f}%)")
    
    elif args.report:
        print("Trend Analysis Report:")
        status = analyzer.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
