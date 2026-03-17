#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Monitor AI - AI-powered health monitoring

Features:
- Real-time health metrics
- Anomaly detection
- Predictive alerts
- Component health tracking
- Trend analysis
- Auto-scaling suggestions
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import statistics

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'health_monitor'
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEALTH_LOG = DATA_DIR / 'health_log.json'
HEALTH_CONFIG = DATA_DIR / 'health_config.json'

class HealthMetrics:
    """Collect health metrics"""
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
    
    def collect(self, component: str, metrics: Dict) -> None:
        """Collect metrics for component"""
        timestamp = datetime.now().isoformat()
        
        metrics_entry = {
            'timestamp': timestamp,
            'component': component,
            'metrics': metrics,
        }
        
        self.metrics_history[component].append(metrics_entry)
    
    def get_current(self, component: str) -> Optional[Dict]:
        """Get current metrics"""
        if component in self.metrics_history and self.metrics_history[component]:
            return self.metrics_history[component][-1]['metrics']
        return None
    
    def get_history(self, component: str, minutes: int = 60) -> List[Dict]:
        """Get historical metrics"""
        if component not in self.metrics_history:
            return []
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        return [
            entry for entry in self.metrics_history[component]
            if datetime.fromisoformat(entry['timestamp']) >= cutoff
        ]
    
    def get_all_components(self) -> List[str]:
        """Get all monitored components"""
        return list(self.metrics_history.keys())


class AnomalyDetector:
    """Detect anomalies in metrics"""
    
    def __init__(self):
        self.baseline = {}
    
    def set_baseline(self, component: str, metrics: Dict) -> None:
        """Set baseline for component"""
        self.baseline[component] = {
            'mean': {},
            'std': {},
            'updated_at': datetime.now().isoformat(),
        }
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                self.baseline[component]['mean'][key] = value
                self.baseline[component]['std'][key] = value * 0.1  # 10% default
    
    def detect(self, component: str, metrics: Dict) -> List[Dict]:
        """Detect anomalies"""
        anomalies = []
        
        if component not in self.baseline:
            return anomalies
        
        baseline = self.baseline[component]
        
        for key, value in metrics.items():
            if not isinstance(value, (int, float)):
                continue
            
            if key not in baseline['mean']:
                continue
            
            mean = baseline['mean'][key]
            std = baseline['std'][key]
            
            if std == 0:
                std = mean * 0.1
            
            # Calculate z-score
            z_score = abs(value - mean) / std
            
            if z_score > 3:  # 3 sigma
                anomalies.append({
                    'metric': key,
                    'value': value,
                    'baseline': mean,
                    'z_score': round(z_score, 2),
                    'severity': 'critical' if z_score > 5 else 'high',
                    'direction': 'increase' if value > mean else 'decrease',
                })
            elif z_score > 2:
                anomalies.append({
                    'metric': key,
                    'value': value,
                    'baseline': mean,
                    'z_score': round(z_score, 2),
                    'severity': 'medium',
                    'direction': 'increase' if value > mean else 'decrease',
                })
        
        return anomalies
    
    def update_baseline(self, component: str, metrics: Dict) -> None:
        """Update baseline with new metrics"""
        if component not in self.baseline:
            self.set_baseline(component, metrics)
            return
        
        # Exponential moving average
        alpha = 0.1  # Smoothing factor
        
        baseline = self.baseline[component]
        
        for key, value in metrics.items():
            if not isinstance(value, (int, float)):
                continue
            
            old_mean = baseline['mean'].get(key, value)
            baseline['mean'][key] = alpha * value + (1 - alpha) * old_mean
            
            # Update std (simplified)
            old_std = baseline['std'].get(key, old_mean * 0.1)
            baseline['std'][key] = alpha * abs(value - old_mean) + (1 - alpha) * old_std
        
        baseline['updated_at'] = datetime.now().isoformat()


class AlertGenerator:
    """Generate alerts from anomalies"""
    
    def __init__(self):
        self.alert_history = []
        self.suppression = {}  # Suppress duplicate alerts
    
    def generate(self, component: str, anomalies: List[Dict], metrics: Dict) -> List[Dict]:
        """Generate alerts"""
        alerts = []
        
        for anomaly in anomalies:
            # Check suppression
            alert_key = f"{component}_{anomaly['metric']}_{anomaly['severity']}"
            
            if alert_key in self.suppression:
                last_alert = self.suppression[alert_key]
                time_since = (datetime.now() - datetime.fromisoformat(last_alert)).total_seconds()
                
                if time_since < 300:  # Suppress for 5 minutes
                    continue
            
            # Generate alert
            alert = {
                'timestamp': datetime.now().isoformat(),
                'component': component,
                'metric': anomaly['metric'],
                'value': anomaly['value'],
                'baseline': anomaly['baseline'],
                'severity': anomaly['severity'],
                'message': self._generate_message(component, anomaly),
                'suggested_action': self._generate_action(anomaly),
            }
            
            alerts.append(alert)
            self.suppression[alert_key] = alert['timestamp']
            self.alert_history.append(alert)
        
        return alerts
    
    def _generate_message(self, component: str, anomaly: Dict) -> str:
        """Generate alert message"""
        direction = anomaly['direction']
        metric = anomaly['metric']
        value = anomaly['value']
        baseline = anomaly['baseline']
        
        change_pct = ((value - baseline) / baseline * 100) if baseline else 0
        
        return (
            f"{component}: {metric} {direction}d by {abs(change_pct):.1f}% "
            f"({value:.2f} vs baseline {baseline:.2f})"
        )
    
    def _generate_action(self, anomaly: Dict) -> str:
        """Generate suggested action"""
        metric = anomaly['metric'].lower()
        severity = anomaly['severity']
        
        if 'cpu' in metric or 'memory' in metric:
            if anomaly['direction'] == 'increase':
                return 'Consider scaling up or optimizing resource usage'
            else:
                return 'Resources underutilized - consider scaling down'
        
        elif 'error' in metric or 'failure' in metric:
            return 'Investigate error logs and implement fixes'
        
        elif 'latency' in metric or 'response_time' in metric:
            return 'Check network and database performance'
        
        elif 'disk' in metric:
            if anomaly['direction'] == 'increase':
                return 'Clean up disk space or expand storage'
            else:
                return 'Disk usage normal'
        
        else:
            return f'Investigate {anomaly["metric"]} anomaly'


class TrendAnalyzer:
    """Analyze trends in metrics"""
    
    def analyze(self, component: str, history: List[Dict]) -> Dict:
        """Analyze trends"""
        if len(history) < 2:
            return {'status': 'insufficient_data'}
        
        # Extract time series for each metric
        metrics_data = defaultdict(list)
        
        for entry in history:
            for key, value in entry.get('metrics', {}).items():
                if isinstance(value, (int, float)):
                    metrics_data[key].append((entry['timestamp'], value))
        
        # Analyze each metric
        trends = {}
        
        for metric, data in metrics_data.items():
            if len(data) < 2:
                continue
            
            values = [d[1] for d in data]
            
            # Calculate trend
            trend = self._calculate_trend(values)
            
            # Calculate volatility
            volatility = self._calculate_volatility(values)
            
            # Predict next value
            prediction = self._predict_next(values)
            
            trends[metric] = {
                'trend': trend,
                'volatility': volatility,
                'current': values[-1],
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'prediction': prediction,
            }
        
        return {
            'status': 'success',
            'component': component,
            'data_points': len(history),
            'time_range': {
                'start': history[0]['timestamp'],
                'end': history[-1]['timestamp'],
            },
            'trends': trends,
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Normalize by mean
        if y_mean != 0:
            slope_pct = slope / y_mean * 100
        else:
            slope_pct = 0
        
        if slope_pct > 5:
            return 'increasing'
        elif slope_pct < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (coefficient of variation)"""
        if len(values) < 2 or statistics.mean(values) == 0:
            return 0.0
        
        std = statistics.stdev(values)
        mean = statistics.mean(values)
        
        return std / mean
    
    def _predict_next(self, values: List[float]) -> Optional[float]:
        """Predict next value using simple moving average"""
        if len(values) < 3:
            return None
        
        # Use last 3 values for prediction
        window = values[-3:]
        return statistics.mean(window)


class HealthMonitorAI:
    """
    AI-powered health monitoring
    
    Features:
    - Real-time health metrics
    - Anomaly detection
    - Predictive alerts
    - Component health tracking
    - Trend analysis
    - Auto-scaling suggestions
    """
    
    def __init__(self):
        self.metrics = HealthMetrics()
        self.anomaly_detector = AnomalyDetector()
        self.alert_generator = AlertGenerator()
        self.trend_analyzer = TrendAnalyzer()
        
        # Default thresholds
        self.thresholds = {
            'cpu_percent': {'warning': 70, 'critical': 90},
            'memory_percent': {'warning': 75, 'critical': 95},
            'disk_percent': {'warning': 80, 'critical': 95},
            'error_rate': {'warning': 0.05, 'critical': 0.1},
            'latency_ms': {'warning': 500, 'critical': 1000},
        }
    
    def report(self, component: str, metrics: Dict) -> Dict:
        """Report health metrics"""
        # Collect metrics
        self.metrics.collect(component, metrics)
        
        # Update baseline
        self.anomaly_detector.update_baseline(component, metrics)
        
        # Detect anomalies
        anomalies = self.anomaly_detector.detect(component, metrics)
        
        # Generate alerts
        alerts = self.alert_generator.generate(component, anomalies, metrics)
        
        # Check thresholds
        threshold_alerts = self._check_thresholds(component, metrics)
        alerts.extend(threshold_alerts)
        
        # Calculate health score
        health_score = self._calculate_health_score(metrics, anomalies)
        
        return {
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'health_score': health_score,
            'health_status': self._get_health_status(health_score),
            'anomalies': anomalies,
            'alerts': alerts,
            'anomaly_count': len(anomalies),
            'alert_count': len(alerts),
        }
    
    def get_status(self, component: str = None) -> Dict:
        """Get health status"""
        if component:
            current = self.metrics.get_current(component)
            history = self.metrics.get_history(component)
            trends = self.trend_analyzer.analyze(component, history)
            
            return {
                'component': component,
                'current': current,
                'trends': trends,
                'baseline': self.anomaly_detector.baseline.get(component),
            }
        else:
            # All components
            components = self.metrics.get_all_components()
            statuses = {}
            
            for comp in components:
                current = self.metrics.get_current(comp)
                if current:
                    health = self._calculate_health_score(current, [])
                    statuses[comp] = {
                        'current': current,
                        'health_score': health,
                        'status': self._get_health_status(health),
                    }
            
            return {
                'components': statuses,
                'total_components': len(components),
                'healthy': sum(1 for s in statuses.values() if s['status'] == 'healthy'),
                'warning': sum(1 for s in statuses.values() if s['status'] == 'warning'),
                'critical': sum(1 for s in statuses.values() if s['status'] == 'critical'),
            }
    
    def _check_thresholds(self, component: str, metrics: Dict) -> List[Dict]:
        """Check metric thresholds"""
        alerts = []
        
        for metric, value in metrics.items():
            if metric not in self.thresholds:
                continue
            
            if not isinstance(value, (int, float)):
                continue
            
            thresholds = self.thresholds[metric]
            
            if value >= thresholds['critical']:
                alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'component': component,
                    'metric': metric,
                    'value': value,
                    'threshold': thresholds['critical'],
                    'severity': 'critical',
                    'message': f'{metric} critical: {value} >= {thresholds["critical"]}',
                    'action': 'Immediate action required',
                })
            elif value >= thresholds['warning']:
                alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'component': component,
                    'metric': metric,
                    'value': value,
                    'threshold': thresholds['warning'],
                    'severity': 'warning',
                    'message': f'{metric} warning: {value} >= {thresholds["warning"]}',
                    'action': 'Monitor closely',
                })
        
        return alerts
    
    def _calculate_health_score(self, metrics: Dict, anomalies: List[Dict]) -> float:
        """Calculate health score (0-1)"""
        score = 1.0
        
        # Penalize for anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'critical':
                score -= 0.3
            elif anomaly['severity'] == 'high':
                score -= 0.2
            elif anomaly['severity'] == 'medium':
                score -= 0.1
        
        # Penalize for threshold violations
        for metric, value in metrics.items():
            if metric in self.thresholds:
                if value >= self.thresholds[metric]['critical']:
                    score -= 0.4
                elif value >= self.thresholds[metric]['warning']:
                    score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _get_health_status(self, score: float) -> str:
        """Get health status from score"""
        if score >= 0.9:
            return 'healthy'
        elif score >= 0.7:
            return 'warning'
        elif score >= 0.5:
            return 'degraded'
        else:
            return 'critical'
    
    def print_status(self, status: Dict):
        """Print health status"""
        print("\n" + "=" * 60)
        print("🏥 HEALTH MONITOR")
        print("=" * 60)
        
        if 'components' in status:
            # Multiple components
            print(f"\n📊 Overview:")
            print(f"   Total: {status['total_components']}")
            print(f"   ✅ Healthy: {status['healthy']}")
            print(f"   ⚠️  Warning: {status['warning']}")
            print(f"   🚨 Critical: {status['critical']}")
            
            print(f"\n📋 Components:")
            for comp, info in status['components'].items():
                emoji = "✅" if info['status'] == 'healthy' else "⚠️" if info['status'] == 'warning' else "🚨"
                print(f"   {emoji} {comp}: {info['health_score']:.1%} ({info['status']})")
        else:
            # Single component
            print(f"\n🔧 Component: {status.get('component', 'unknown')}")
            
            if status.get('current'):
                print(f"\n📊 Current Metrics:")
                for key, value in status['current'].items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    else:
                        print(f"   {key}: {value}")
            
            if status.get('trends') and status['trends'].get('status') == 'success':
                print(f"\n📈 Trends:")
                for metric, trend_info in status['trends'].get('trends', {}).items():
                    print(f"   {metric}: {trend_info['trend']} (volatility: {trend_info['volatility']:.2f})")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Health Monitor AI")
    parser.add_argument('--report', action='store_true', help='Demo report')
    report_group = parser.add_mutually_exclusive_group()
    report_group.add_argument('--status', action='store_true', help='Show status')
    report_group.add_argument('--monitor', action='store_true', help='Monitor mode')
    parser.add_argument('--component', type=str, default='system', help='Component name')
    args = parser.parse_args()
    
    monitor = HealthMonitorAI()
    
    if args.report:
        # Demo health report
        test_metrics = [
            {'cpu_percent': 45, 'memory_percent': 60, 'disk_percent': 55, 'error_rate': 0.02},
            {'cpu_percent': 85, 'memory_percent': 78, 'disk_percent': 60, 'error_rate': 0.08},
            {'cpu_percent': 95, 'memory_percent': 92, 'disk_percent': 88, 'error_rate': 0.15},
        ]
        
        for i, metrics in enumerate(test_metrics):
            print(f"\n📊 Test Case {i+1}:")
            result = monitor.report(args.component, metrics)
            print(f"   Health Score: {result['health_score']:.1%}")
            print(f"   Status: {result['health_status']}")
            if result['alerts']:
                print(f"   Alerts: {len(result['alerts'])}")
                for alert in result['alerts'][:2]:
                    print(f"     - [{alert['severity']}] {alert['message']}")
    
    elif args.status:
        status = monitor.get_status()
        monitor.print_status(status)
    
    elif args.monitor:
        print("🔍 Monitoring mode - simulating metrics...\n")
        
        import random
        
        for i in range(5):
            metrics = {
                'cpu_percent': random.uniform(40, 70),
                'memory_percent': random.uniform(50, 80),
                'disk_percent': random.uniform(55, 65),
                'error_rate': random.uniform(0.01, 0.05),
            }
            
            result = monitor.report(args.component, metrics)
            
            emoji = "✅" if result['health_status'] == 'healthy' else "⚠️"
            print(f"{emoji} [{datetime.now().strftime('%H:%M:%S')}] "
                  f"{args.component}: {result['health_score']:.1%} "
                  f"({result['health_status']})")
            
            time.sleep(0.5)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    import time
    main()
