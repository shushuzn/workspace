#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Predictor - System health forecasting and failure prediction

Features:
- Health trend forecasting
- Failure prediction (ML-based)
- Risk scoring (0-1)
- Time-to-failure estimation
- Preventive action recommendations
"""

import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import statistics

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'health_prediction'
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEALTH_HISTORY = DATA_DIR / 'health_history.json'
PREDICTION_MODEL = DATA_DIR / 'prediction_model.json'

class HealthTrendAnalyzer:
    """Analyze health trends"""
    
    def __init__(self):
        self.history = deque(maxlen=1000)
    
    def add_reading(self, timestamp: str, health_score: float, metrics: Dict):
        """Add health reading"""
        self.history.append({
            'timestamp': timestamp,
            'health_score': health_score,
            'metrics': metrics,
        })
    
    def analyze_trend(self, hours: int = 24) -> Dict:
        """Analyze trend over last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        readings = [
            r for r in self.history
            if datetime.fromisoformat(r['timestamp']) >= cutoff
        ]
        
        if len(readings) < 2:
            return {'status': 'insufficient_data', 'readings': len(readings)}
        
        scores = [r['health_score'] for r in readings]
        
        # Calculate trend
        trend = self._calculate_trend(scores)
        
        # Calculate volatility
        volatility = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        # Predict next value
        prediction = self._predict_next(scores)
        
        return {
            'status': 'success',
            'readings': len(readings),
            'time_range': {
                'start': readings[0]['timestamp'],
                'end': readings[-1]['timestamp'],
            },
            'current': scores[-1],
            'average': statistics.mean(scores),
            'min': min(scores),
            'max': max(scores),
            'trend': trend,
            'volatility': round(volatility, 4),
            'prediction': prediction,
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction"""
        if len(scores) < 2:
            return 'stable'
        
        # Simple linear regression
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(scores)
        
        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Normalize
        if y_mean != 0:
            slope_pct = slope / y_mean * 100
        else:
            slope_pct = 0
        
        if slope_pct > 2:
            return 'improving'
        elif slope_pct < -2:
            return 'degrading'
        else:
            return 'stable'
    
    def _predict_next(self, scores: List[float]) -> Optional[float]:
        """Predict next health score"""
        if len(scores) < 3:
            return None
        
        # Use weighted moving average
        weights = [1, 2, 3]
        recent = scores[-3:]
        
        weighted_sum = sum(s * w for s, w in zip(recent, weights))
        weight_total = sum(weights)
        
        return round(weighted_sum / weight_total, 3)


class FailurePredictor:
    """ML-based failure prediction"""
    
    def __init__(self):
        # Failure patterns (simplified rule-based)
        self.patterns = {
            'rapid_degradation': {
                'condition': lambda s: len(s) >= 3 and s[-1] < s[-2] < s[-3] and (s[-3] - s[-1]) > 0.3,
                'probability': 0.85,
                'timeframe': '1-2 hours',
                'description': 'Rapid health degradation detected',
            },
            'critical_threshold': {
                'condition': lambda s: s[-1] < 0.3,
                'probability': 0.95,
                'timeframe': 'immediate',
                'description': 'Health below critical threshold',
            },
            'high_volatility': {
                'condition': lambda s: len(s) >= 5 and statistics.stdev(s) > 0.2,
                'probability': 0.70,
                'timeframe': '2-4 hours',
                'description': 'High volatility indicates instability',
            },
            'steady_decline': {
                'condition': lambda s: len(s) >= 5 and all(s[i] > s[i+1] for i in range(-5, -1)),
                'probability': 0.75,
                'timeframe': '4-6 hours',
                'description': 'Steady decline pattern detected',
            },
        }
    
    def predict(self, health_scores: List[float]) -> Dict:
        """Predict failure probability"""
        if len(health_scores) < 3:
            return {
                'probability': 0.0,
                'confidence': 0.0,
                'pattern': 'insufficient_data',
                'timeframe': 'unknown',
            }
        
        # Check each pattern
        detected_patterns = []
        
        for name, pattern in self.patterns.items():
            try:
                if pattern['condition'](health_scores):
                    detected_patterns.append({
                        'name': name,
                        'probability': pattern['probability'],
                        'timeframe': pattern['timeframe'],
                        'description': pattern['description'],
                    })
            except:
                continue
        
        if not detected_patterns:
            # Calculate baseline probability
            current = health_scores[-1]
            trend = (health_scores[-1] - health_scores[0]) / len(health_scores)
            
            probability = max(0.0, min(1.0, (1.0 - current) * 0.5 + max(0, -trend) * 2))
            
            return {
                'probability': round(probability, 3),
                'confidence': 0.5,
                'pattern': 'baseline',
                'timeframe': '6-12 hours',
                'patterns_detected': [],
            }
        
        # Use highest probability pattern
        detected_patterns.sort(key=lambda x: x['probability'], reverse=True)
        primary = detected_patterns[0]
        
        return {
            'probability': primary['probability'],
            'confidence': 0.8,
            'pattern': primary['name'],
            'timeframe': primary['timeframe'],
            'description': primary['description'],
            'patterns_detected': detected_patterns,
        }


class RiskScorer:
    """Calculate risk score"""
    
    def __init__(self):
        self.weights = {
            'current_health': 0.3,
            'trend': 0.2,
            'volatility': 0.15,
            'failure_probability': 0.25,
            'critical_metrics': 0.1,
        }
    
    def calculate(self, health_data: Dict, prediction: Dict, metrics: Dict) -> Dict:
        """Calculate comprehensive risk score"""
        # Current health risk (inverse)
        health_risk = 1.0 - health_data.get('current', 1.0)
        
        # Trend risk
        trend = health_data.get('trend', 'stable')
        trend_risk = {'improving': 0.2, 'stable': 0.5, 'degrading': 0.8}.get(trend, 0.5)
        
        # Volatility risk
        volatility = health_data.get('volatility', 0.0)
        volatility_risk = min(1.0, volatility * 3)
        
        # Failure probability
        failure_risk = prediction.get('probability', 0.0)
        
        # Critical metrics
        critical_risk = self._assess_critical_metrics(metrics)
        
        # Weighted sum
        risk_score = (
            health_risk * self.weights['current_health'] +
            trend_risk * self.weights['trend'] +
            volatility_risk * self.weights['volatility'] +
            failure_risk * self.weights['failure_probability'] +
            critical_risk * self.weights['critical_metrics']
        )
        
        # Risk level
        if risk_score >= 0.8:
            level = 'critical'
        elif risk_score >= 0.6:
            level = 'high'
        elif risk_score >= 0.4:
            level = 'medium'
        elif risk_score >= 0.2:
            level = 'low'
        else:
            level = 'minimal'
        
        return {
            'score': round(risk_score, 3),
            'level': level,
            'components': {
                'health_risk': round(health_risk, 3),
                'trend_risk': round(trend_risk, 3),
                'volatility_risk': round(volatility_risk, 3),
                'failure_risk': round(failure_risk, 3),
                'critical_risk': round(critical_risk, 3),
            },
            'recommendation': self._get_recommendation(level),
        }
    
    def _assess_critical_metrics(self, metrics: Dict) -> float:
        """Assess critical metrics risk"""
        critical_thresholds = {
            'cpu_percent': 90,
            'memory_percent': 95,
            'disk_percent': 95,
            'error_rate': 0.1,
        }
        
        risk = 0.0
        count = 0
        
        for metric, threshold in critical_thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                if isinstance(value, (int, float)):
                    count += 1
                    if value >= threshold:
                        risk += 1.0
                    elif value >= threshold * 0.8:
                        risk += 0.5
        
        return risk / count if count > 0 else 0.0
    
    def _get_recommendation(self, level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'critical': 'Immediate action required - prepare for failure',
            'high': 'Urgent attention needed - schedule maintenance',
            'medium': 'Monitor closely - plan preventive action',
            'low': 'Normal operation - continue monitoring',
            'minimal': 'System healthy - no action needed',
        }
        return recommendations.get(level, 'Unknown')


class TimeToFailureEstimator:
    """Estimate time to failure"""
    
    def estimate(self, health_scores: List[float], current_risk: float) -> Dict:
        """Estimate time to failure"""
        if len(health_scores) < 2:
            return {
                'estimated_hours': None,
                'confidence': 0.0,
                'status': 'insufficient_data',
            }
        
        # Calculate degradation rate
        degradation_rate = (health_scores[0] - health_scores[-1]) / len(health_scores)
        
        # Current health
        current = health_scores[-1]
        
        # Failure threshold
        failure_threshold = 0.2
        
        if degradation_rate <= 0:
            # Improving or stable
            return {
                'estimated_hours': float('inf'),
                'confidence': 0.7,
                'status': 'stable_or_improving',
                'message': 'System is stable or improving',
            }
        
        # Time to reach failure threshold
        remaining_health = current - failure_threshold
        
        if remaining_health <= 0:
            return {
                'estimated_hours': 0,
                'confidence': 0.9,
                'status': 'already_failed',
                'message': 'System already below failure threshold',
            }
        
        # Estimate hours
        hours_to_failure = remaining_health / degradation_rate
        
        # Adjust confidence based on data quality
        confidence = min(0.9, 0.5 + len(health_scores) * 0.05)
        
        return {
            'estimated_hours': round(hours_to_failure, 1),
            'estimated_time': self._format_time(hours_to_failure),
            'confidence': round(confidence, 2),
            'status': 'estimated',
            'degradation_rate': round(degradation_rate, 4),
            'message': f'Estimated failure in {self._format_time(hours_to_failure)}',
        }
    
    def _format_time(self, hours: float) -> str:
        """Format time"""
        if hours < 1:
            return f"{hours*60:.0f} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            return f"{hours/24:.1f} days"


class HealthPredictor:
    """
    System health forecasting and failure prediction
    
    Features:
    - Health trend forecasting
    - Failure prediction (rule-based ML)
    - Risk scoring (0-1)
    - Time-to-failure estimation
    - Preventive action recommendations
    """
    
    def __init__(self):
        self.trend_analyzer = HealthTrendAnalyzer()
        self.failure_predictor = FailurePredictor()
        self.risk_scorer = RiskScorer()
        self.ttf_estimator = TimeToFailureEstimator()
    
    def analyze(self, component: str, health_score: float, metrics: Dict) -> Dict:
        """Analyze and predict health"""
        # Add reading
        timestamp = datetime.now().isoformat()
        self.trend_analyzer.add_reading(timestamp, health_score, metrics)
        
        # Get trend analysis
        trend_data = self.trend_analyzer.analyze_trend(hours=24)
        
        # Get health scores for prediction
        health_scores = [r['health_score'] for r in self.trend_analyzer.history]
        
        # Predict failure
        failure_prediction = self.failure_predictor.predict(health_scores)
        
        # Calculate risk
        risk_assessment = self.risk_scorer.calculate(trend_data, failure_prediction, metrics)
        
        # Estimate time to failure
        ttf_estimate = self.ttf_estimator.estimate(health_scores, risk_assessment['score'])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            trend_data, failure_prediction, risk_assessment, ttf_estimate
        )
        
        return {
            'component': component,
            'timestamp': timestamp,
            'current_health': health_score,
            'trend': trend_data,
            'failure_prediction': failure_prediction,
            'risk_assessment': risk_assessment,
            'time_to_failure': ttf_estimate,
            'recommendations': recommendations,
        }
    
    def _generate_recommendations(self, trend: Dict, failure: Dict,
                                  risk: Dict, ttf: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on risk level
        if risk['level'] in ['critical', 'high']:
            recommendations.append({
                'priority': 'critical',
                'action': 'Immediate intervention required',
                'reason': f"Risk level: {risk['level']} (score: {risk['score']:.1%})",
                'timeframe': 'now',
            })
        
        # Based on trend
        if trend.get('trend') == 'degrading':
            recommendations.append({
                'priority': 'high',
                'action': 'Investigate degradation cause',
                'reason': f"Health trend: {trend.get('trend', 'unknown')}",
                'timeframe': 'within 1 hour',
            })
        
        # Based on failure prediction
        if failure.get('probability', 0) > 0.7:
            recommendations.append({
                'priority': 'high',
                'action': f"Prepare for potential failure ({failure.get('pattern', 'unknown')})",
                'reason': f"Failure probability: {failure.get('probability', 0):.1%}",
                'timeframe': failure.get('timeframe', 'soon'),
            })
        
        # Based on time to failure
        if ttf.get('status') == 'estimated' and ttf.get('estimated_hours'):
            hours = ttf['estimated_hours']
            if hours < 2:
                recommendations.append({
                    'priority': 'critical',
                    'action': 'Emergency maintenance required',
                    'reason': f"Estimated time to failure: {ttf['estimated_time']}",
                    'timeframe': 'immediate',
                })
            elif hours < 24:
                recommendations.append({
                    'priority': 'high',
                    'action': 'Schedule maintenance',
                    'reason': f"Estimated time to failure: {ttf['estimated_time']}",
                    'timeframe': 'today',
                })
        
        # Default if no issues
        if not recommendations:
            recommendations.append({
                'priority': 'low',
                'action': 'Continue normal monitoring',
                'reason': 'System operating within normal parameters',
                'timeframe': 'ongoing',
            })
        
        return recommendations
    
    def print_prediction(self, result: Dict):
        """Print prediction report"""
        print("\n" + "=" * 60)
        print("🔮 HEALTH PREDICTION REPORT")
        print("=" * 60)
        
        print(f"\n📊 Component: {result['component']}")
        print(f"Current Health: {result['current_health']:.1%}")
        
        # Trend
        trend = result['trend']
        if trend.get('status') == 'success':
            print(f"\n📈 Trend Analysis:")
            print(f"   Direction: {trend.get('trend', 'unknown')}")
            print(f"   Volatility: {trend.get('volatility', 0):.2%}")
            print(f"   Prediction: {trend.get('prediction', 'N/A'):.1%}")
        
        # Failure prediction
        failure = result['failure_prediction']
        print(f"\n⚠️  Failure Prediction:")
        print(f"   Probability: {failure.get('probability', 0):.1%}")
        print(f"   Confidence: {failure.get('confidence', 0):.1%}")
        print(f"   Pattern: {failure.get('pattern', 'none')}")
        print(f"   Timeframe: {failure.get('timeframe', 'unknown')}")
        
        # Risk
        risk = result['risk_assessment']
        emoji = "🔴" if risk['level'] == 'critical' else "🟠" if risk['level'] == 'high' else "🟡" if risk['level'] == 'medium' else "🟢"
        print(f"\n🎯 Risk Assessment:")
        print(f"   {emoji} Level: {risk['level'].upper()}")
        print(f"   Score: {risk['score']:.1%}")
        print(f"   Recommendation: {risk['recommendation']}")
        
        # Time to failure
        ttf = result['time_to_failure']
        if ttf.get('status') == 'estimated':
            print(f"\n⏰ Time to Failure:")
            print(f"   Estimate: {ttf.get('estimated_time', 'unknown')}")
            print(f"   Confidence: {ttf.get('confidence', 0):.1%}")
        
        # Recommendations
        print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
        for rec in result['recommendations'][:3]:
            print(f"   [{rec['priority'].upper()}] {rec['action']}")
            print(f"      Reason: {rec['reason']}")
            print(f"      Timeframe: {rec['timeframe']}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Health Predictor")
    parser.add_argument('--analyze', action='store_true', help='Demo analysis')
    parser.add_argument('--component', type=str, default='system', help='Component name')
    args = parser.parse_args()
    
    predictor = HealthPredictor()
    
    if args.analyze:
        # Simulate health readings
        import random
        
        print("🔍 Simulating health readings...\n")
        
        # Generate some historical data
        base_health = 0.85
        for i in range(10):
            health = base_health - (i * 0.02) + random.uniform(-0.05, 0.05)
            health = max(0.0, min(1.0, health))
            
            metrics = {
                'cpu_percent': random.uniform(40, 70),
                'memory_percent': random.uniform(50, 80),
                'error_rate': random.uniform(0.01, 0.05),
            }
            
            result = predictor.analyze(args.component, health, metrics)
        
        # Print final prediction
        predictor.print_prediction(result)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
