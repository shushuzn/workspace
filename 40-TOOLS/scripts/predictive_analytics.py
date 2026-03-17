#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Predictive Analytics Engine - Forecasting and trend prediction

Features:
- Time series forecasting
- Trend analysis
- Anomaly detection
- Pattern recognition
- Confidence intervals
- Multi-metric prediction
"""

import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
ANALYTICS_DIR = WORKSPACE / 'data' / 'analytics'
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

class TimeSeriesModel:
    """Simple time series forecasting model"""
    
    def __init__(self, data: List[Tuple[datetime, float]]):
        self.data = sorted(data, key=lambda x: x[0])
        self.timestamps = [d[0] for d in self.data]
        self.values = [d[1] for d in self.data]
        
        # Model parameters
        self.mean = 0
        self.trend = 0
        self.seasonality = []
        self.residuals = []
        
        # Fit model
        self._fit()
    
    def _fit(self):
        """Fit time series decomposition model"""
        if len(self.values) < 3:
            self.mean = sum(self.values) / max(1, len(self.values))
            return
        
        # Calculate mean
        self.mean = sum(self.values) / len(self.values)
        
        # Calculate trend (linear regression)
        n = len(self.values)
        x_mean = (n - 1) / 2
        y_mean = self.mean
        
        numerator = sum((i - x_mean) * (self.values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        self.trend = numerator / max(1, denominator)
        
        # Calculate residuals
        for i, value in enumerate(self.values):
            predicted = self.mean + self.trend * (i - x_mean)
            residual = value - predicted
            self.residuals.append(residual)
        
        # Calculate seasonality (if enough data)
        if len(self.values) >= 7:
            # Weekly seasonality
            self.seasonality = []
            for i in range(min(7, len(self.values))):
                day_values = [
                    self.values[j] for j in range(i, len(self.values), 7)
                ]
                if day_values:
                    day_mean = sum(day_values) / len(day_values)
                    self.seasonality.append(day_mean - self.mean)
    
    def forecast(self, steps: int = 7) -> List[Tuple[datetime, float, float, float]]:
        """
        Forecast future values
        
        Args:
            steps: Number of steps to forecast
        
        Returns:
            List of (timestamp, predicted_value, lower_bound, upper_bound)
        """
        if not self.data:
            return []
        
        forecasts = []
        last_timestamp = self.timestamps[-1]
        n = len(self.values)
        
        # Calculate residual standard deviation
        if self.residuals:
            residual_std = math.sqrt(
                sum(r ** 2 for r in self.residuals) / max(1, len(self.residuals))
            )
        else:
            residual_std = 0
        
        for i in range(steps):
            # Future timestamp
            future_timestamp = last_timestamp + timedelta(days=i+1)
            
            # Predicted value
            future_index = n + i
            predicted = self.mean + self.trend * (future_index - (n-1)/2)
            
            # Add seasonality if available
            if self.seasonality and i < len(self.seasonality):
                predicted += self.seasonality[i % len(self.seasonality)]
            
            # Confidence interval (95%)
            margin = 1.96 * residual_std * math.sqrt(1 + 1/max(1, n) + (future_index - (n-1)/2)**2 / max(1, sum((j - (n-1)/2)**2 for j in range(n))))
            lower_bound = predicted - margin
            upper_bound = predicted + margin
            
            forecasts.append((future_timestamp, predicted, lower_bound, upper_bound))
        
        return forecasts
    
    def get_trend(self) -> str:
        """Get trend direction"""
        if abs(self.trend) < 0.01:
            return 'stable'
        elif self.trend > 0:
            return 'increasing'
        else:
            return 'decreasing'
    
    def get_stats(self) -> Dict:
        """Get model statistics"""
        return {
            'mean': self.mean,
            'trend': self.trend,
            'trend_direction': self.get_trend(),
            'data_points': len(self.data),
            'residual_std': math.sqrt(sum(r**2 for r in self.residuals) / max(1, len(self.residuals))) if self.residuals else 0,
        }


class AnomalyDetector:
    """Anomaly detection for time series"""
    
    def __init__(self, data: List[float], sensitivity: float = 2.0):
        self.data = data
        self.sensitivity = sensitivity  # Standard deviations
        
        # Calculate statistics
        if data:
            self.mean = sum(data) / len(data)
            self.std = math.sqrt(sum((x - self.mean)**2 for x in data) / max(1, len(data)))
        else:
            self.mean = 0
            self.std = 0
        
        # Detect anomalies
        self.anomalies = self._detect()
    
    def _detect(self) -> List[int]:
        """Detect anomalies in data"""
        anomalies = []
        
        for i, value in enumerate(self.data):
            if self.std > 0:
                z_score = abs(value - self.mean) / self.std
                if z_score > self.sensitivity:
                    anomalies.append(i)
        
        return anomalies
    
    def is_anomaly(self, value: float) -> bool:
        """Check if a value is anomalous"""
        if self.std == 0:
            return False
        
        z_score = abs(value - self.mean) / self.std
        return z_score > self.sensitivity
    
    def get_anomaly_report(self) -> Dict:
        """Get anomaly detection report"""
        return {
            'total_points': len(self.data),
            'anomalies_detected': len(self.anomalies),
            'anomaly_rate': len(self.anomalies) / max(1, len(self.data)),
            'anomaly_indices': self.anomalies,
            'threshold': f'±{self.sensitivity}σ',
        }


class PredictiveAnalytics:
    """
    Predictive analytics engine
    
    Features:
    - Time series forecasting
    - Trend analysis
    - Anomaly detection
    - Pattern recognition
    - Confidence intervals
    """
    
    def __init__(self):
        self.metrics_dir = ANALYTICS_DIR / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Load historical metrics
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, List[Tuple[datetime, float]]]:
        """Load historical metrics"""
        metrics = {}
        
        # Load deployment metrics
        deployment_history_file = WORKSPACE / 'data' / 'deploy' / 'deployment_history.json'
        if deployment_history_file.exists():
            with open(deployment_history_file, 'r', encoding='utf-8') as f:
                deployments = json.load(f)
            
            # Group by date
            by_date = defaultdict(list)
            for dep in deployments:
                try:
                    date = datetime.fromisoformat(dep['timestamp']).date()
                    by_date[str(date)].append(1)
                except:
                    pass
            
            metrics['deployments_per_day'] = [
                (datetime.strptime(d, '%Y-%m-%d'), len(counts))
                for d, counts in sorted(by_date.items())
            ]
        
        # Load tool usage metrics
        usage_file = WORKSPACE / 'data' / 'tool_registry' / 'usage_stats.json'
        if usage_file.exists():
            with open(usage_file, 'r', encoding='utf-8') as f:
                usage = json.load(f)
            
            total_runs = sum(u.get('total_runs', 0) for u in usage.values())
            metrics['total_tool_runs'] = [(datetime.now(), total_runs)]
        
        return metrics
    
    def analyze_deployments(self) -> Dict:
        """Analyze and forecast deployment metrics"""
        if 'deployments_per_day' not in self.metrics or not self.metrics['deployments_per_day']:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough deployment history for analysis',
            }
        
        data = self.metrics['deployments_per_day']
        
        # Create time series model
        model = TimeSeriesModel(data)
        
        # Forecast next 7 days
        forecast = model.forecast(steps=7)
        
        # Anomaly detection
        values = [d[1] for d in data]
        anomaly_detector = AnomalyDetector(values)
        
        # Build report
        report = {
            'status': 'success',
            'current_stats': {
                'mean_deployments_per_day': model.mean,
                'trend': model.get_trend(),
                'trend_slope': model.trend,
                'total_days': len(data),
            },
            'forecast': [
                {
                    'date': f.timestamp().strftime('%Y-%m-%d'),
                    'predicted': round(f[1], 2),
                    'lower_bound': round(f[2], 2),
                    'upper_bound': round(f[3], 2),
                }
                for f in forecast
            ],
            'anomalies': anomaly_detector.get_anomaly_report(),
            'insights': self._generate_insights(model, forecast, anomaly_detector),
        }
        
        return report
    
    def _generate_insights(self, model: TimeSeriesModel,
                          forecast: List[Tuple],
                          anomalies: AnomalyDetector) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # Trend insight
        trend = model.get_trend()
        if trend == 'increasing':
            insights.append(f"📈 Deployment frequency is increasing ({model.trend:.2f}/day)")
        elif trend == 'decreasing':
            insights.append(f"📉 Deployment frequency is decreasing ({model.trend:.2f}/day)")
        else:
            insights.append(f"➡️ Deployment frequency is stable")
        
        # Forecast insight
        if forecast:
            avg_forecast = sum(f[1] for f in forecast) / len(forecast)
            if avg_forecast > model.mean * 1.2:
                insights.append(f"⚠️  Expected deployment increase: {avg_forecast:.1f}/day (vs {model.mean:.1f} historical)")
            elif avg_forecast < model.mean * 0.8:
                insights.append(f"💡 Expected deployment decrease: {avg_forecast:.1f}/day (vs {model.mean:.1f} historical)")
        
        # Anomaly insight
        if anomalies.anomalies:
            insights.append(f"⚠️  {len(anomalies.anomalies)} anomalous days detected in history")
        
        return insights
    
    def predict_tool_usage(self) -> Dict:
        """Predict tool usage trends"""
        if 'total_tool_runs' not in self.metrics or not self.metrics['total_tool_runs']:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough tool usage data for analysis',
            }
        
        # For now, return current stats
        total_runs = self.metrics['total_tool_runs'][0][1]
        
        return {
            'status': 'success',
            'current_usage': {
                'total_runs': total_runs,
            },
            'prediction': {
                'message': 'More data needed for accurate prediction',
            },
        }
    
    def generate_report(self, output_file: Path = None) -> Path:
        """Generate comprehensive predictive analytics report"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = ANALYTICS_DIR / f'predictive_report_{timestamp}.json'
        
        report = {
            'generated': datetime.now().isoformat(),
            'deployment_analysis': self.analyze_deployments(),
            'tool_usage_prediction': self.predict_tool_usage(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Predictive report generated: {output_file}")
        return output_file
    
    def print_summary(self):
        """Print analytics summary"""
        print("\n🔮 PREDICTIVE ANALYTICS SUMMARY")
        print("=" * 60)
        
        # Deployment analysis
        deployment_analysis = self.analyze_deployments()
        
        if deployment_analysis.get('status') == 'success':
            stats = deployment_analysis['current_stats']
            print(f"\n📊 DEPLOYMENT TRENDS:")
            print(f"   Mean deployments/day: {stats['mean_deployments_per_day']:.2f}")
            print(f"   Trend: {stats['trend'].upper()}")
            print(f"   Data points: {stats['total_days']} days")
            
            print(f"\n📈 7-DAY FORECAST:")
            for f in deployment_analysis['forecast'][:7]:
                print(f"   {f['date']}: {f['predicted']:.1f} ({f['lower_bound']:.1f}-{f['upper_bound']:.1f})")
            
            print(f"\n💡 INSIGHTS:")
            for insight in deployment_analysis.get('insights', []):
                print(f"   {insight}")
        else:
            print(f"\n⚠️  {deployment_analysis.get('message', 'No deployment data')}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Predictive Analytics Engine")
    parser.add_argument('--analyze', action='store_true', help='Run analysis')
    parser.add_argument('--forecast', action='store_true', help='Generate forecast')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    analytics = PredictiveAnalytics()
    
    if args.analyze:
        analytics.print_summary()
    
    elif args.forecast:
        deployment_forecast = analytics.analyze_deployments()
        print(json.dumps(deployment_forecast, indent=2))
    
    elif args.report:
        analytics.generate_report()
    
    elif args.demo:
        print("\n🔮 Predictive Analytics Demo")
        print("=" * 60)
        analytics.print_summary()
        print("\n✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
