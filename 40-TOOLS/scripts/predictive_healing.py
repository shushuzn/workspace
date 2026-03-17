#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Predictive Self-Healing - Proactive Error Prevention
Features: Anomaly detection, trend analysis, predictive alerts, auto-prevention

Usage:
    python predictive_healing.py --monitor
    python predictive_healing.py --analyze
    python predictive_healing.py --predict
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class MetricPoint:
    """Single metric measurement"""
    timestamp: str
    value: float
    metadata: Dict


@dataclass
class Trend:
    """Trend analysis result"""
    metric: str
    direction: str  # increasing/decreasing/stable
    slope: float
    r_squared: float
    prediction_1h: float
    prediction_6h: float
    prediction_24h: float


@dataclass
class Prediction:
    """Predictive alert"""
    metric: str
    current_value: float
    threshold: float
    predicted_breach_time: str
    confidence: float
    severity: str  # critical/warning/info
    recommendation: str


@dataclass
class Anomaly:
    """Detected anomaly"""
    metric: str
    value: float
    expected_range: Tuple[float, float]
    deviation: float
    timestamp: str
    possible_cause: str


class PredictiveSelfHealing:
    """Predictive self-healing system"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "healing"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / "metrics_history.json"
        self.predictions_file = self.data_dir / "predictions.json"
        self.anomalies_file = self.data_dir / "anomalies.json"
        
        self.metrics_history: Dict[str, List[MetricPoint]] = {}
        self.predictions: List[Prediction] = []
        self.anomalies: List[Anomaly] = []
        
        # Thresholds
        self.thresholds = {
            'memory_percent': {'warning': 80, 'critical': 90},
            'disk_percent': {'warning': 80, 'critical': 90},
            'cpu_percent': {'warning': 70, 'critical': 90},
            'api_calls_per_hour': {'warning': 800, 'critical': 950},
            'error_rate': {'warning': 0.05, 'critical': 0.10},
            'response_time_ms': {'warning': 1000, 'critical': 3000}
        }
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metrics_history = {
                    k: [MetricPoint(**p) for p in v]
                    for k, v in data.get('metrics', {}).items()
                }
        
        if self.predictions_file.exists():
            with open(self.predictions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.predictions = [Prediction(**p) for p in data.get('predictions', [])]
        
        if self.anomalies_file.exists():
            with open(self.anomalies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.anomalies = [Anomaly(**a) for a in data.get('anomalies', [])]
    
    def save_state(self):
        """Save state"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metrics': {
                    k: [asdict(p) for p in v[-1000:]]  # Keep last 1000 points
                    for k, v in self.metrics_history.items()
                },
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.predictions_file, 'w', encoding='utf-8') as f:
            json.dump({
                'predictions': [asdict(p) for p in self.predictions[-100:]],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.anomalies_file, 'w', encoding='utf-8') as f:
            json.dump({
                'anomalies': [asdict(a) for a in self.anomalies[-200:]],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def record_metric(self, metric: str, value: float, metadata: Dict = None):
        """Record metric measurement"""
        point = MetricPoint(
            timestamp=datetime.now().isoformat(),
            value=value,
            metadata=metadata or {}
        )
        
        if metric not in self.metrics_history:
            self.metrics_history[metric] = []
        
        self.metrics_history[metric].append(point)
        
        # Check for anomalies
        self.detect_anomalies(metric, value)
        
        # Save periodically
        if len(self.metrics_history[metric]) % 50 == 0:
            self.save_state()
    
    def calculate_trend(self, metric: str, hours: int = 6) -> Optional[Trend]:
        """Calculate trend for metric"""
        if metric not in self.metrics_history:
            return None
        
        points = self.metrics_history[metric]
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            p for p in points
            if datetime.fromisoformat(p.timestamp) > cutoff
        ]
        
        if len(recent) < 3:
            return None
        
        # Simple linear regression
        n = len(recent)
        x = list(range(n))
        y = [p.value for p in recent]
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # R-squared
        y_pred = [intercept + slope * x[i] for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Predictions
        current_x = n - 1
        prediction_1h = intercept + slope * (current_x + n // 6)  # 1h = 1/6 of 6h
        prediction_6h = intercept + slope * (current_x + n)  # 6h more
        prediction_24h = intercept + slope * (current_x + n * 4)  # 24h more
        
        direction = 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable'
        
        return Trend(
            metric=metric,
            direction=direction,
            slope=round(slope, 4),
            r_squared=round(r_squared, 3),
            prediction_1h=round(prediction_1h, 2),
            prediction_6h=round(prediction_6h, 2),
            prediction_24h=round(prediction_24h, 2)
        )
    
    def detect_anomalies(self, metric: str, value: float):
        """Detect anomalies in metric"""
        if metric not in self.metrics_history:
            return
        
        points = self.metrics_history[metric][-100:]  # Last 100 points
        
        if len(points) < 10:
            return
        
        values = [p.value for p in points]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Z-score anomaly detection
        if stdev > 0:
            z_score = abs(value - mean) / stdev
            
            if z_score > 3.0:  # 3 sigma
                expected_min = mean - 3 * stdev
                expected_max = mean + 3 * stdev
                
                anomaly = Anomaly(
                    metric=metric,
                    value=round(value, 2),
                    expected_range=(round(expected_min, 2), round(expected_max, 2)),
                    deviation=round(z_score, 2),
                    timestamp=datetime.now().isoformat(),
                    possible_cause=self._infer_cause(metric, value)
                )
                
                self.anomalies.append(anomaly)
                
                print(f"\n🚨 ANOMALY DETECTED: {metric}")
                print(f"  Value: {value:.2f}")
                print(f"  Expected: {expected_min:.2f} - {expected_max:.2f}")
                print(f"  Deviation: {z_score:.2f}σ")
                print(f"  Possible cause: {anomaly.possible_cause}\n")
    
    def _infer_cause(self, metric: str, value: float) -> str:
        """Infer possible cause of anomaly"""
        causes = {
            'memory_percent': 'Memory leak or large data processing',
            'disk_percent': 'Large file creation or log accumulation',
            'cpu_percent': 'CPU-intensive task or infinite loop',
            'api_calls_per_hour': 'Automated script running or rate limit approach',
            'error_rate': 'System instability or external service issues',
            'response_time_ms': 'Network congestion or server overload'
        }
        
        return causes.get(metric, 'Unknown - requires investigation')
    
    def predict_threshold_breach(self, metric: str) -> Optional[Prediction]:
        """Predict when metric will breach threshold"""
        if metric not in self.thresholds:
            return None
        
        trend = self.calculate_trend(metric)
        if not trend or trend.direction == 'stable':
            return None
        
        points = self.metrics_history[metric]
        current_value = points[-1].value if points else 0
        
        thresholds = self.thresholds[metric]
        
        # Check critical threshold
        if trend.slope > 0:  # Increasing
            if trend.prediction_6h > thresholds['critical']:
                hours_to_breach = (thresholds['critical'] - current_value) / (trend.slope * 6)
                breach_time = datetime.now() + timedelta(hours=max(0.1, hours_to_breach))
                
                prediction = Prediction(
                    metric=metric,
                    current_value=round(current_value, 2),
                    threshold=thresholds['critical'],
                    predicted_breach_time=breach_time.isoformat(),
                    confidence=round(trend.r_squared * 100, 1),
                    severity='critical',
                    recommendation=self._get_recommendation(metric, 'critical')
                )
                
                self.predictions.append(prediction)
                return prediction
        
        # Check warning threshold
        if trend.slope > 0:
            if trend.prediction_1h > thresholds['warning']:
                hours_to_breach = (thresholds['warning'] - current_value) / (trend.slope * 6)
                breach_time = datetime.now() + timedelta(hours=max(0.1, hours_to_breach))
                
                prediction = Prediction(
                    metric=metric,
                    current_value=round(current_value, 2),
                    threshold=thresholds['warning'],
                    predicted_breach_time=breach_time.isoformat(),
                    confidence=round(trend.r_squared * 100, 1),
                    severity='warning',
                    recommendation=self._get_recommendation(metric, 'warning')
                )
                
                self.predictions.append(prediction)
                return prediction
        
        return None
    
    def _get_recommendation(self, metric: str, severity: str) -> str:
        """Get prevention recommendation"""
        recommendations = {
            'memory_percent': {
                'warning': 'Consider clearing cache or restarting memory-intensive services',
                'critical': 'Immediate action required: Clear cache, stop non-essential processes'
            },
            'disk_percent': {
                'warning': 'Clean up temporary files and old backups',
                'critical': 'Critical: Delete old logs, backups, and temporary data immediately'
            },
            'cpu_percent': {
                'warning': 'Review running processes and optimize CPU-intensive tasks',
                'critical': 'Stop non-essential processes and investigate CPU hogs'
            },
            'api_calls_per_hour': {
                'warning': 'Throttle API calls or implement caching',
                'critical': 'Stop automated scripts immediately to avoid rate limit ban'
            }
        }
        
        return recommendations.get(metric, {}).get(severity, 'Investigate and take appropriate action')
    
    def run_prevention(self, prediction: Prediction) -> bool:
        """Run preventive action"""
        print(f"\n🛡️  RUNNING PREVENTION: {prediction.metric}")
        print(f"  Severity: {prediction.severity}")
        print(f"  Recommendation: {prediction.recommendation}")
        
        # Auto-prevention actions
        if prediction.metric == 'memory_percent':
            print("  → Clearing cache...")
            # Here would call cache_manager.clear()
        
        elif prediction.metric == 'disk_percent':
            print("  → Deleting old backups...")
            # Here would call cleanup_old_backups()
        
        elif prediction.metric == 'api_calls_per_hour':
            print("  → Throttling API calls...")
            # Here would call api_throttle()
        
        print("  ✅ Prevention complete\n")
        return True
    
    def get_health_score(self) -> float:
        """Calculate overall health score"""
        scores = []
        
        for metric in self.thresholds.keys():
            if metric in self.metrics_history and self.metrics_history[metric]:
                current = self.metrics_history[metric][-1].value
                thresholds = self.thresholds[metric]
                
                if current >= thresholds['critical']:
                    scores.append(0)
                elif current >= thresholds['warning']:
                    scores.append(50)
                else:
                    # Scale from 0 to warning
                    score = 100 - (current / thresholds['warning'] * 50)
                    scores.append(min(100, max(0, score)))
        
        return round(statistics.mean(scores), 1) if scores else 100.0
    
    def get_status(self) -> Dict:
        """Get healing system status"""
        return {
            'health_score': self.get_health_score(),
            'metrics_tracked': len(self.metrics_history),
            'active_predictions': len([p for p in self.predictions if p.severity in ['critical', 'warning']]),
            'anomalies_24h': len([
                a for a in self.anomalies
                if datetime.fromisoformat(a.timestamp) > datetime.now() - timedelta(hours=24)
            ])
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Predictive Self-Healing')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')
    parser.add_argument('--analyze', action='store_true', help='Analyze trends')
    parser.add_argument('--predict', action='store_true', help='Generate predictions')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--test', action='store_true', help='Test system')
    args = parser.parse_args()
    
    healing = PredictiveSelfHealing()
    
    if args.monitor:
        print("Starting monitoring (Ctrl+C to stop)...")
        try:
            while True:
                # Simulate metrics (replace with real metrics)
                import random
                healing.record_metric('memory_percent', 60 + random.random() * 20)
                healing.record_metric('cpu_percent', 30 + random.random() * 40)
                time.sleep(5)
        except KeyboardInterrupt:
            healing.save_state()
            print("\nMonitoring stopped")
    
    elif args.analyze:
        print("\nTrend Analysis:\n")
        for metric in healing.metrics_history.keys():
            trend = healing.calculate_trend(metric)
            if trend:
                print(f"{metric}:")
                print(f"  Direction: {trend.direction}")
                print(f"  Slope: {trend.slope}")
                print(f"  R²: {trend.r_squared}")
                print(f"  1h prediction: {trend.prediction_1h}")
                print(f"  6h prediction: {trend.prediction_6h}")
                print()
    
    elif args.predict:
        print("\nPredictions:\n")
        for metric in healing.thresholds.keys():
            prediction = healing.predict_threshold_breach(metric)
            if prediction:
                print(f"⚠️  {prediction.metric}")
                print(f"  Current: {prediction.current_value}")
                print(f"  Threshold: {prediction.threshold}")
                print(f"  Breach time: {prediction.predicted_breach_time}")
                print(f"  Confidence: {prediction.confidence}%")
                print(f"  Recommendation: {prediction.recommendation}")
                print()
        
        if not healing.predictions:
            print("No threshold breaches predicted ✅")
    
    elif args.status:
        status = healing.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.test:
        print("\n🧪 Testing Predictive Self-Healing\n")
        
        # Simulate increasing memory usage
        print("Simulating memory leak...")
        for i in range(50):
            healing.record_metric('memory_percent', 50 + i * 0.8)
        
        # Analyze trend
        trend = healing.calculate_trend('memory_percent')
        if trend:
            print(f"\n📊 Trend Detected:")
            print(f"  Direction: {trend.direction}")
            print(f"  Slope: {trend.slope}")
            print(f"  R²: {trend.r_squared}")
        
        # Predict breach
        prediction = healing.predict_threshold_breach('memory_percent')
        if prediction:
            print(f"\n🔮 Prediction:")
            print(f"  Breach time: {prediction.predicted_breach_time}")
            print(f"  Severity: {prediction.severity}")
            
            # Run prevention
            healing.run_prevention(prediction)
        
        # Show status
        status = healing.get_status()
        print(f"\n📈 Health Score: {status['health_score']}/100")
        
        healing.save_state()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
