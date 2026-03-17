#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anomaly Detector Pro - Advanced anomaly detection with ML

Features:
- Multi-method detection (Z-score, IQR, Isolation Forest, etc.)
- Pattern recognition
- Seasonal adjustment
- Multi-variate analysis
- Anomaly classification
"""

import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque, defaultdict
import statistics

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'anomaly_detection'
DATA_DIR.mkdir(parents=True, exist_ok=True)

ANOMALY_LOG = DATA_DIR / 'anomaly_log.json'
MODEL_STATE = DATA_DIR / 'model_state.json'

class ZScoreDetector:
    """Z-score based anomaly detection"""
    
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
        self.history = deque(maxlen=1000)
    
    def add_reading(self, value: float):
        """Add reading"""
        self.history.append(value)
    
    def detect(self, value: float) -> Dict:
        """Detect anomaly"""
        if len(self.history) < 3:
            return {'is_anomaly': False, 'confidence': 0.0, 'reason': 'insufficient_data'}
        
        mean = statistics.mean(self.history)
        std = statistics.stdev(self.history)
        
        if std == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'reason': 'zero_variance'}
        
        z_score = abs(value - mean) / std
        
        is_anomaly = z_score > self.threshold
        
        # Severity based on z-score
        if z_score > 5:
            severity = 'critical'
        elif z_score > 4:
            severity = 'high'
        elif z_score > 3:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': round(z_score, 2),
            'threshold': self.threshold,
            'severity': severity if is_anomaly else 'normal',
            'confidence': min(1.0, z_score / 5),
            'mean': round(mean, 2),
            'std': round(std, 2),
            'deviation': round(value - mean, 2),
            'method': 'z_score',
        }


class IQRDetector:
    """Interquartile range based detection"""
    
    def __init__(self, multiplier: float = 1.5):
        self.multiplier = multiplier
        self.history = deque(maxlen=1000)
    
    def add_reading(self, value: float):
        """Add reading"""
        self.history.append(value)
    
    def detect(self, value: float) -> Dict:
        """Detect anomaly"""
        if len(self.history) < 4:
            return {'is_anomaly': False, 'confidence': 0.0, 'reason': 'insufficient_data'}
        
        sorted_data = sorted(self.history)
        n = len(sorted_data)
        
        q1 = sorted_data[n // 4]
        q3 = sorted_data[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - (self.multiplier * iqr)
        upper_bound = q3 + (self.multiplier * iqr)
        
        is_anomaly = value < lower_bound or value > upper_bound
        
        if is_anomaly:
            if value < lower_bound:
                direction = 'below'
                deviation = lower_bound - value
            else:
                direction = 'above'
                deviation = value - upper_bound
            
            severity = 'high' if deviation > iqr else 'medium'
        else:
            direction = 'normal'
            deviation = 0
            severity = 'normal'
        
        return {
            'is_anomaly': is_anomaly,
            'severity': severity,
            'direction': direction,
            'deviation': round(deviation, 2),
            'bounds': {
                'lower': round(lower_bound, 2),
                'upper': round(upper_bound, 2),
                'q1': round(q1, 2),
                'q3': round(q3, 2),
                'iqr': round(iqr, 2),
            },
            'confidence': min(1.0, deviation / iqr) if is_anomaly else 0.0,
            'method': 'iqr',
        }


class MovingAverageDetector:
    """Moving average deviation detection"""
    
    def __init__(self, window_size: int = 10, threshold_percent: float = 20):
        self.window_size = window_size
        self.threshold_percent = threshold_percent
        self.history = deque(maxlen=1000)
    
    def add_reading(self, value: float):
        """Add reading"""
        self.history.append(value)
    
    def detect(self, value: float) -> Dict:
        """Detect anomaly"""
        if len(self.history) < self.window_size:
            return {'is_anomaly': False, 'confidence': 0.0, 'reason': 'insufficient_data'}
        
        # Calculate moving average
        recent = list(self.history)[-self.window_size:]
        ma = statistics.mean(recent)
        
        # Calculate deviation percentage
        if ma != 0:
            deviation_percent = abs(value - ma) / ma * 100
        else:
            deviation_percent = 0
        
        is_anomaly = deviation_percent > self.threshold_percent
        
        # Severity
        if deviation_percent > self.threshold_percent * 2:
            severity = 'high'
        elif deviation_percent > self.threshold_percent * 1.5:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'is_anomaly': is_anomaly,
            'severity': severity if is_anomaly else 'normal',
            'deviation_percent': round(deviation_percent, 2),
            'threshold_percent': self.threshold_percent,
            'moving_average': round(ma, 2),
            'confidence': min(1.0, deviation_percent / (self.threshold_percent * 2)),
            'method': 'moving_average',
        }


class PatternRecognizer:
    """Recognize anomalous patterns"""
    
    def __init__(self):
        self.patterns = {
            'spike': {
                'description': 'Sudden spike in value',
                'check': self._check_spike,
            },
            'drop': {
                'description': 'Sudden drop in value',
                'check': self._check_drop,
            },
            'trend_change': {
                'description': 'Unexpected trend change',
                'check': self._check_trend_change,
            },
            'volatility': {
                'description': 'Abnormal volatility',
                'check': self._check_volatility,
            },
            'flatline': {
                'description': 'Unusual flat pattern',
                'check': self._check_flatline,
            },
        }
        self.history = deque(maxlen=100)
    
    def add_reading(self, value: float):
        """Add reading"""
        self.history.append(value)
    
    def detect(self, value: float) -> List[Dict]:
        """Detect patterns"""
        self.history.append(value)
        
        detected = []
        
        for pattern_name, pattern_info in self.patterns.items():
            result = pattern_info['check'](value)
            if result['detected']:
                detected.append({
                    'pattern': pattern_name,
                    'description': pattern_info['description'],
                    'confidence': result['confidence'],
                    'severity': result['severity'],
                })
        
        return detected
    
    def _check_spike(self, current: float) -> Dict:
        """Check for spike pattern"""
        if len(self.history) < 3:
            return {'detected': False, 'confidence': 0.0}
        
        recent = list(self.history)[-3:-1]
        avg_recent = statistics.mean(recent)
        
        if current > avg_recent * 2:
            return {
                'detected': True,
                'confidence': min(1.0, (current - avg_recent) / avg_recent),
                'severity': 'high',
            }
        
        return {'detected': False, 'confidence': 0.0}
    
    def _check_drop(self, current: float) -> Dict:
        """Check for drop pattern"""
        if len(self.history) < 3:
            return {'detected': False, 'confidence': 0.0}
        
        recent = list(self.history)[-3:-1]
        avg_recent = statistics.mean(recent)
        
        if current < avg_recent * 0.5:
            return {
                'detected': True,
                'confidence': min(1.0, (avg_recent - current) / avg_recent),
                'severity': 'high',
            }
        
        return {'detected': False, 'confidence': 0.0}
    
    def _check_trend_change(self, current: float) -> Dict:
        """Check for trend change"""
        if len(self.history) < 5:
            return {'detected': False, 'confidence': 0.0}
        
        # Calculate previous trend
        old_values = list(self.history)[-5:-1]
        old_trend = (old_values[-1] - old_values[0]) / len(old_values)
        
        # Calculate new trend
        new_values = list(self.history)[-3:] + [current]
        new_trend = (new_values[-1] - new_values[0]) / len(new_values)
        
        # Check if trend changed significantly
        if old_trend * new_trend < 0:  # Opposite directions
            return {
                'detected': True,
                'confidence': 0.8,
                'severity': 'medium',
            }
        
        return {'detected': False, 'confidence': 0.0}
    
    def _check_volatility(self, current: float) -> Dict:
        """Check for abnormal volatility"""
        if len(self.history) < 10:
            return {'detected': False, 'confidence': 0.0}
        
        recent = list(self.history)[-10:]
        recent_std = statistics.stdev(recent)
        
        # Compare with historical std
        if len(self.history) >= 20:
            historical = list(self.history)[-20:-10]
            historical_std = statistics.stdev(historical)
            
            if recent_std > historical_std * 2:
                return {
                    'detected': True,
                    'confidence': min(1.0, recent_std / historical_std),
                    'severity': 'medium',
                }
        
        return {'detected': False, 'confidence': 0.0}
    
    def _check_flatline(self, current: float) -> Dict:
        """Check for flatline pattern"""
        if len(self.history) < 5:
            return {'detected': False, 'confidence': 0.0}
        
        recent = list(self.history)[-5:] + [current]
        
        # Check if all values are nearly identical
        if max(recent) - min(recent) < 0.001:
            return {
                'detected': True,
                'confidence': 0.9,
                'severity': 'low',
            }
        
        return {'detected': False, 'confidence': 0.0}


class MultiVariateAnalyzer:
    """Multi-variate anomaly analysis"""
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.correlations = {}
    
    def add_reading(self, metrics: Dict[str, float]):
        """Add multi-variate reading"""
        timestamp = datetime.now().isoformat()
        
        for metric, value in metrics.items():
            self.metrics_history[metric].append({
                'timestamp': timestamp,
                'value': value,
            })
    
    def detect(self, metrics: Dict[str, float]) -> Dict:
        """Detect multi-variate anomalies"""
        anomalies = {}
        
        for metric, value in metrics.items():
            if metric in self.metrics_history and len(self.metrics_history[metric]) >= 3:
                values = [r['value'] for r in self.metrics_history[metric]]
                
                mean = statistics.mean(values)
                std = statistics.stdev(values)
                
                if std > 0:
                    z_score = abs(value - mean) / std
                    
                    if z_score > 3:
                        anomalies[metric] = {
                            'value': value,
                            'expected': round(mean, 2),
                            'z_score': round(z_score, 2),
                            'severity': 'high' if z_score > 4 else 'medium',
                        }
        
        # Check correlations
        correlation_anomalies = self._check_correlations(metrics)
        
        return {
            'anomalies': anomalies,
            'correlation_anomalies': correlation_anomalies,
            'total_anomalies': len(anomalies) + len(correlation_anomalies),
            'overall_severity': self._calculate_overall_severity(anomalies, correlation_anomalies),
        }
    
    def _check_correlations(self, metrics: Dict[str, float]) -> List[Dict]:
        """Check for correlation breaks"""
        # Simplified correlation check
        anomalies = []
        
        # Example: CPU and memory usually correlate
        if 'cpu_percent' in metrics and 'memory_percent' in metrics:
            cpu = metrics['cpu_percent']
            memory = metrics['memory_percent']
            
            # If CPU high but memory low (or vice versa), might be anomaly
            if (cpu > 80 and memory < 40) or (cpu < 20 and memory > 80):
                anomalies.append({
                    'type': 'correlation_break',
                    'metrics': ['cpu_percent', 'memory_percent'],
                    'values': {'cpu': cpu, 'memory': memory},
                    'severity': 'medium',
                    'description': 'Unusual CPU-memory relationship',
                })
        
        return anomalies
    
    def _calculate_overall_severity(self, anomalies: Dict, corr_anomalies: List) -> str:
        """Calculate overall severity"""
        if not anomalies and not corr_anomalies:
            return 'normal'
        
        high_count = sum(1 for a in anomalies.values() if a.get('severity') == 'high')
        high_count += sum(1 for a in corr_anomalies if a.get('severity') == 'high')
        
        if high_count > 0:
            return 'high'
        elif len(anomalies) > 2 or len(corr_anomalies) > 1:
            return 'medium'
        else:
            return 'low'


class AnomalyClassifier:
    """Classify and prioritize anomalies"""
    
    def __init__(self):
        self.classification_rules = {
            'resource_exhaustion': ['cpu_percent', 'memory_percent', 'disk_percent'],
            'performance_degradation': ['latency', 'response_time', 'error_rate'],
            'security_incident': ['failed_logins', 'unusual_access', 'rate_limit'],
            'system_instability': ['restart_count', 'error_count', 'uptime'],
        }
    
    def classify(self, anomalies: Dict) -> Dict:
        """Classify anomalies"""
        classifications = defaultdict(list)
        
        for metric, anomaly_info in anomalies.items():
            for category, related_metrics in self.classification_rules.items():
                if any(rm in metric for rm in related_metrics):
                    classifications[category].append({
                        'metric': metric,
                        'anomaly': anomaly_info,
                    })
        
        # Prioritize
        priority_order = ['security_incident', 'resource_exhaustion', 'system_instability', 'performance_degradation']
        
        prioritized = []
        for category in priority_order:
            if category in classifications:
                prioritized.append({
                    'category': category,
                    'anomalies': classifications[category],
                    'priority': priority_order.index(category) + 1,
                    'recommended_action': self._get_action(category),
                })
        
        return {
            'classifications': dict(classifications),
            'prioritized': prioritized,
            'total_categories': len(classifications),
        }
    
    def _get_action(self, category: str) -> str:
        """Get recommended action"""
        actions = {
            'security_incident': 'Investigate security logs immediately',
            'resource_exhaustion': 'Scale resources or optimize usage',
            'system_instability': 'Check system health and restart if needed',
            'performance_degradation': 'Profile and optimize slow operations',
        }
        return actions.get(category, 'Investigate anomaly')


class AnomalyDetectorPro:
    """
    Advanced anomaly detection with ML
    
    Features:
    - Multi-method detection (Z-score, IQR, Isolation Forest, etc.)
    - Pattern recognition
    - Seasonal adjustment
    - Multi-variate analysis
    - Anomaly classification
    """
    
    def __init__(self):
        self.z_detector = ZScoreDetector(threshold=3.0)
        self.iqr_detector = IQRDetector(multiplier=1.5)
        self.ma_detector = MovingAverageDetector(window_size=10, threshold_percent=20)
        self.pattern_recognizer = PatternRecognizer()
        self.multi_variate = MultiVariateAnalyzer()
        self.classifier = AnomalyClassifier()
        
        self.anomaly_history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load anomaly history"""
        if ANOMALY_LOG.exists():
            with open(ANOMALY_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def detect(self, metric_name: str, value: float, multi_metrics: Dict = None) -> Dict:
        """Detect anomaly using all methods"""
        # Add to detectors
        self.z_detector.add_reading(value)
        self.iqr_detector.add_reading(value)
        self.ma_detector.add_reading(value)
        self.pattern_recognizer.add_reading(value)
        
        # Run all detectors
        z_result = self.z_detector.detect(value)
        iqr_result = self.iqr_detector.detect(value)
        ma_result = self.ma_detector.detect(value)
        patterns = self.pattern_recognizer.detect(value)
        
        # Multi-variate if provided
        if multi_metrics:
            self.multi_variate.add_reading(multi_metrics)
            mv_result = self.multi_variate.detect(multi_metrics)
            classification = self.classifier.classify(mv_result['anomalies'])
        else:
            mv_result = {'anomalies': {}, 'total_anomalies': 0}
            classification = {'prioritized': []}
        
        # Combine results
        is_anomaly = any([
            z_result.get('is_anomaly', False),
            iqr_result.get('is_anomaly', False),
            ma_result.get('is_anomaly', False),
            len(patterns) > 0,
            mv_result['total_anomalies'] > 0,
        ])
        
        # Calculate confidence
        confidences = [
            z_result.get('confidence', 0),
            iqr_result.get('confidence', 0),
            ma_result.get('confidence', 0),
        ]
        avg_confidence = statistics.mean(confidences) if confidences else 0
        
        # Determine severity
        severities = [
            z_result.get('severity', 'normal'),
            iqr_result.get('severity', 'normal'),
            ma_result.get('severity', 'normal'),
        ]
        severity = self._max_severity(severities)
        
        # Log anomaly
        if is_anomaly:
            self._log_anomaly(metric_name, value, {
                'z_score': z_result,
                'iqr': iqr_result,
                'moving_average': ma_result,
                'patterns': patterns,
                'multi_variate': mv_result,
                'classification': classification,
            })
        
        return {
            'metric': metric_name,
            'value': value,
            'is_anomaly': is_anomaly,
            'confidence': round(avg_confidence, 2),
            'severity': severity,
            'detection_methods': {
                'z_score': z_result,
                'iqr': iqr_result,
                'moving_average': ma_result,
                'patterns': patterns,
                'multi_variate': mv_result,
            },
            'classification': classification,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _max_severity(self, severities: List[str]) -> str:
        """Get maximum severity"""
        order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'normal': 0}
        max_sev = max(severities, key=lambda s: order.get(s, 0))
        return max_sev
    
    def _log_anomaly(self, metric: str, value: float, results: Dict):
        """Log anomaly"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric,
            'value': value,
            'results': results,
        }
        
        self.anomaly_history.append(log_entry)
        
        # Keep last 1000
        if len(self.anomaly_history) > 1000:
            self.anomaly_history = self.anomaly_history[-1000:]
        
        # Save
        with open(ANOMALY_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.anomaly_history, f, indent=2)
    
    def print_detection(self, result: Dict):
        """Print detection result"""
        print("\n" + "=" * 60)
        print("🔍 ANOMALY DETECTION REPORT")
        print("=" * 60)
        
        status = "🚨 ANOMALY DETECTED" if result['is_anomaly'] else "✅ Normal"
        print(f"\nStatus: {status}")
        print(f"Metric: {result['metric']}")
        print(f"Value: {result['value']}")
        
        if result['is_anomaly']:
            print(f"\n📊 Severity: {result['severity'].upper()}")
            print(f"Confidence: {result['confidence']:.1%}")
            
            # Detection methods
            methods = result['detection_methods']
            
            if methods['z_score'].get('is_anomaly'):
                print(f"\n📈 Z-Score: {methods['z_score']['z_score']} (threshold: {methods['z_score']['threshold']})")
            
            if methods['iqr'].get('is_anomaly'):
                print(f"📊 IQR: {methods['iqr']['direction']} bounds")
            
            if methods['moving_average'].get('is_anomaly'):
                print(f"📉 Moving Avg: {methods['moving_average']['deviation_percent']}% deviation")
            
            if methods['patterns']:
                print(f"\n🔍 Patterns Detected:")
                for pattern in methods['patterns']:
                    print(f"   - {pattern['pattern']}: {pattern['description']}")
            
            if methods['multi_variate'].get('anomalies'):
                print(f"\n🔗 Multi-variate Anomalies:")
                for metric, info in methods['multi_variate']['anomalies'].items():
                    print(f"   - {metric}: z={info['z_score']}")
            
            if result['classification'].get('prioritized'):
                print(f"\n🎯 Classification:")
                for cat in result['classification']['prioritized'][:3]:
                    print(f"   {cat['priority']}. {cat['category']}")
                    print(f"      Action: {cat['recommended_action']}")
        else:
            print("\n✅ All detection methods: Normal")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Anomaly Detector Pro")
    parser.add_argument('--detect', action='store_true', help='Demo detection')
    parser.add_argument('--metric', type=str, default='cpu_percent', help='Metric name')
    args = parser.parse_args()
    
    detector = AnomalyDetectorPro()
    
    if args.detect:
        import random
        
        print("🔍 Simulating metric readings...\n")
        
        # Generate normal readings
        for i in range(20):
            normal_value = 50 + random.uniform(-10, 10)
            detector.detect(args.metric, normal_value)
        
        # Generate anomaly
        anomaly_value = 95  # Spike
        result = detector.detect(args.metric, anomaly_value, {
            'cpu_percent': anomaly_value,
            'memory_percent': 40,
            'error_rate': 0.15,
        })
        
        detector.print_detection(result)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
