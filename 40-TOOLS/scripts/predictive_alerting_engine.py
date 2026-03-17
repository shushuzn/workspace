#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 Predictive Alerting Engine - AI-Powered Anomaly Detection

Predicts system failures before they occur using:
- Time-series analysis
- Anomaly detection
- Pattern recognition
- Threshold prediction

Usage:
    python predictive_alerting_engine.py --analyze
    python predictive_alerting_engine.py --predict
    python predictive_alerting_engine.py --status
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
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
class Prediction:
    """Failure prediction"""
    id: str
    system: str
    probability: float  # 0-1
    predicted_time: str
    confidence: float
    indicators: List[str]
    recommended_action: str


@dataclass
class Anomaly:
    """Detected anomaly"""
    id: str
    system: str
    metric: str
    expected: float
    actual: float
    deviation: float
    severity: str
    timestamp: str


class PredictiveAlertingEngine:
    """AI-powered predictive alerting"""
    
    def __init__(self):
        self.history_file = WORKSPACE / "20-data-reports" / "monitor_history.json"
        self.predictions_file = WORKSPACE / "20-data-reports" / "predictions.json"
        
        self.history = {}
        self.predictions = []
        self.anomalies = []
        
        self.thresholds = {
            'cpu_usage': {'warning': 70, 'critical': 90},
            'memory_usage': {'warning': 75, 'critical': 95},
            'disk_usage': {'warning': 80, 'critical': 95},
            'response_time': {'warning': 1000, 'critical': 5000},  # ms
            'error_rate': {'warning': 5, 'critical': 20},  # %
        }
        
        self.load_history()
    
    def load_history(self):
        """Load historical data"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = {}
    
    def save_history(self):
        """Save historical data"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def save_predictions(self):
        """Save predictions"""
        with open(self.predictions_file, 'w', encoding='utf-8') as f:
            json.dump({
                'predictions': [asdict(p) if isinstance(p, Prediction) else p for p in self.predictions],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def add_metric(self, system: str, metric: str, value: float):
        """Add metric to history"""
        if system not in self.history:
            self.history[system] = {}
        
        if metric not in self.history[system]:
            self.history[system][metric] = []
        
        # Add timestamped value
        self.history[system][metric].append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 1000 data points
        if len(self.history[system][metric]) > 1000:
            self.history[system][metric] = self.history[system][metric][-1000:]
        
        self.save_history()
    
    def detect_anomaly(self, system: str, metric: str, value: float) -> Optional[Anomaly]:
        """Detect anomaly using statistical analysis"""
        if system not in self.history or metric not in self.history[system]:
            return None
        
        data = self.history[system][metric]
        if len(data) < 10:
            return None  # Not enough data
        
        values = [d['value'] for d in data[-100:]]  # Last 100 points
        
        # Calculate statistics
        mean = np.mean(values)
        std = np.std(values)
        
        # Calculate deviation (z-score)
        if std > 0:
            z_score = abs(value - mean) / std
        else:
            z_score = 0
        
        # Determine severity
        if z_score > 3:
            severity = 'critical'
        elif z_score > 2:
            severity = 'warning'
        elif z_score > 1.5:
            severity = 'info'
        else:
            return None  # Normal
        
        # Create anomaly
        anomaly = Anomaly(
            id=f"anomaly_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            system=system,
            metric=metric,
            expected=mean,
            actual=value,
            deviation=z_score,
            severity=severity,
            timestamp=datetime.now().isoformat()
        )
        
        self.anomalies.append(anomaly)
        
        # Keep last 100 anomalies
        if len(self.anomalies) > 100:
            self.anomalies = self.anomalies[-100:]
        
        return anomaly
    
    def check_threshold(self, system: str, metric: str, value: float) -> Optional[str]:
        """Check if value exceeds threshold"""
        if metric not in self.thresholds:
            return None
        
        thresholds = self.thresholds[metric]
        
        if value >= thresholds['critical']:
            return 'critical'
        elif value >= thresholds['warning']:
            return 'warning'
        
        return None
    
    def predict_failure(self, system: str, metric: str) -> Optional[Prediction]:
        """Predict system failure using trend analysis"""
        if system not in self.history or metric not in self.history[system]:
            return None
        
        data = self.history[system][metric]
        if len(data) < 50:
            return None  # Not enough data
        
        values = [d['value'] for d in data[-50:]]
        
        # Simple linear regression for trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Get current value and threshold
        current = values[-1]
        threshold = self.thresholds.get(metric, {}).get('critical', 100)
        
        # Predict time to threshold breach
        if slope > 0:
            steps_to_breach = (threshold - current) / slope
            
            if steps_to_breach > 0:
                # Convert steps to time (assuming 1 data point per minute)
                hours_to_breach = steps_to_breach / 60
                
                if hours_to_breach < 24:  # Predict within 24 hours
                    probability = min(1.0, 1.0 / (hours_to_breach + 0.1))
                    
                    prediction = Prediction(
                        id=f"pred_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        system=system,
                        probability=probability,
                        predicted_time=(datetime.now() + timedelta(hours=hours_to_breach)).isoformat(),
                        confidence=min(0.95, len(values) / 100),
                        indicators=[
                            f"Trend: +{slope:.2f}/min",
                            f"Current: {current:.1f}",
                            f"Threshold: {threshold}",
                            f"Time to breach: {hours_to_breach:.1f}h"
                        ],
                        recommended_action=self._get_recommendation(metric, slope)
                    )
                    
                    return prediction
        
        return None
    
    def _get_recommendation(self, metric: str, trend: float) -> str:
        """Get recommended action"""
        recommendations = {
            'cpu_usage': "Scale up resources or optimize CPU-intensive processes",
            'memory_usage': "Increase memory or fix memory leaks",
            'disk_usage': "Clean up disk space or expand storage",
            'response_time': "Optimize database queries or add caching",
            'error_rate': "Investigate error logs and fix root causes"
        }
        
        base = recommendations.get(metric, "Investigate and address the issue")
        
        if trend > 0:
            return f"⚠️ URGENT: {base} (trend: +{trend:.2f}/min)"
        else:
            return f"ℹ️ MONITOR: {base}"
    
    def analyze(self) -> Dict:
        """Run full analysis"""
        results = {
            'anomalies_detected': 0,
            'predictions_made': 0,
            'threshold_violations': 0,
            'systems_analyzed': 0
        }
        
        for system, metrics in self.history.items():
            results['systems_analyzed'] += 1
            
            for metric, data in metrics.items():
                if not data:
                    continue
                
                current_value = data[-1]['value']
                
                # Check threshold
                violation = self.check_threshold(system, metric, current_value)
                if violation:
                    results['threshold_violations'] += 1
                
                # Detect anomaly
                anomaly = self.detect_anomaly(system, metric, current_value)
                if anomaly:
                    results['anomalies_detected'] += 1
                
                # Predict failure
                prediction = self.predict_failure(system, metric)
                if prediction:
                    self.predictions.append(prediction)
                    results['predictions_made'] += 1
        
        # Keep last 50 predictions
        if len(self.predictions) > 50:
            self.predictions = self.predictions[-50:]
        
        self.save_predictions()
        
        return results
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'status': 'operational',
            'systems_monitored': len(self.history),
            'total_predictions': len(self.predictions),
            'total_anomalies': len(self.anomalies),
            'recent_predictions': [asdict(p) if isinstance(p, Prediction) else p 
                                   for p in self.predictions[-5:]],
            'recent_anomalies': [asdict(a) if isinstance(a, Anomaly) else a 
                                 for a in self.anomalies[-5:]]
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Predictive Alerting Engine')
    parser.add_argument('--analyze', action='store_true', help='Run analysis')
    parser.add_argument('--predict', action='store_true', help='Show predictions')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    
    args = parser.parse_args()
    
    engine = PredictiveAlertingEngine()
    
    if args.demo:
        print("=" * 70)
        print("🔮 Predictive Alerting Engine - Demo")
        print("=" * 70)
        
        # Simulate metrics
        print("\n[1] Simulating metrics...")
        for i in range(60):
            # CPU usage trending up
            cpu = 50 + i * 0.5 + np.random.normal(0, 2)
            engine.add_metric('system_1', 'cpu_usage', cpu)
            
            # Memory stable
            mem = 60 + np.random.normal(0, 3)
            engine.add_metric('system_1', 'memory_usage', mem)
            
            # Response time increasing
            resp = 200 + i * 5 + np.random.normal(0, 20)
            engine.add_metric('api_gateway', 'response_time', resp)
        
        print(f"[OK] Added 180 data points (60 time steps × 3 metrics)")
        
        # Analyze
        print("\n[2] Running analysis...")
        results = engine.analyze()
        print(f"[OK] Analysis complete:")
        for key, value in results.items():
            print(f"  - {key}: {value}")
        
        # Show status
        print("\n[3] Engine Status:")
        status = engine.get_status()
        print(f"  - Systems monitored: {status['systems_monitored']}")
        print(f"  - Total predictions: {status['total_predictions']}")
        print(f"  - Total anomalies: {status['total_anomalies']}")
        
        if status['recent_predictions']:
            print("\n[4] Recent Predictions:")
            for pred in status['recent_predictions']:
                print(f"  ⚠️ {pred['system']}: {pred['probability']*100:.1f}% failure probability")
                print(f"     Time: {pred['predicted_time']}")
                print(f"     Action: {pred['recommended_action']}")
        
        print("\n" + "=" * 70)
        print("✅ Demo complete - Predictive Alerting Engine OPERATIONAL")
        print("=" * 70)
    
    elif args.analyze:
        print("Running analysis...")
        results = engine.analyze()
        print(json.dumps(results, indent=2))
    
    elif args.predict:
        print("Predictions:")
        status = engine.get_status()
        print(json.dumps(status['recent_predictions'], indent=2))
    
    elif args.status:
        print("Engine Status:")
        status = engine.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
