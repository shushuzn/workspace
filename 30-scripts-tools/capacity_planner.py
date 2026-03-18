#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capacity Planner - Resource usage prediction and scaling recommendations

Features:
- Resource usage forecasting
- Scaling recommendations
- Bottleneck prediction
- Cost optimization
- Capacity planning reports
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
import statistics

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'capacity_planning'
DATA_DIR.mkdir(parents=True, exist_ok=True)

USAGE_HISTORY = DATA_DIR / 'usage_history.json'

class ResourceForecaster:
    """Forecast resource usage"""
    
    def __init__(self):
        self.history = deque(maxlen=1000)
    
    def add_reading(self, timestamp: str, resource: str, usage: float):
        """Add usage reading"""
        self.history.append({
            'timestamp': timestamp,
            'resource': resource,
            'usage': usage,
        })
    
    def forecast(self, resource: str, hours_ahead: int = 24) -> Dict:
        """Forecast resource usage"""
        # Get historical data
        readings = [
            r for r in self.history
            if r['resource'] == resource
        ]
        
        if len(readings) < 3:
            return {
                'status': 'insufficient_data',
                'readings': len(readings),
            }
        
        values = [r['usage'] for r in readings]
        
        # Simple forecasting (weighted moving average + trend)
        current = values[-1]
        avg = statistics.mean(values)
        
        # Calculate trend
        if len(values) >= 3:
            trend = (values[-1] - values[-3]) / 2
        else:
            trend = 0
        
        # Forecast
        forecast_value = current + trend * (hours_ahead / 6)  # Assume 6-hour intervals
        
        # Confidence decreases with time
        confidence = max(0.5, 1.0 - (hours_ahead / 100))
        
        # Bounds
        forecast_value = max(0, min(100, forecast_value))
        
        return {
            'status': 'success',
            'resource': resource,
            'current': round(current, 2),
            'average': round(avg, 2),
            'forecast': round(forecast_value, 2),
            'trend': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'confidence': round(confidence, 2),
            'hours_ahead': hours_ahead,
        }


class BottleneckPredictor:
    """Predict resource bottlenecks"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_percent': {'warning': 70, 'critical': 90},
            'memory_percent': {'warning': 75, 'critical': 95},
            'disk_percent': {'warning': 80, 'critical': 95},
            'network_percent': {'warning': 70, 'critical': 90},
        }
    
    def predict(self, forecasts: Dict) -> List[Dict]:
        """Predict bottlenecks"""
        bottlenecks = []
        
        for resource, forecast in forecasts.items():
            if forecast.get('status') != 'success':
                continue
            
            thresholds = self.thresholds.get(resource, {'warning': 70, 'critical': 90})
            
            forecast_value = forecast.get('forecast', 0)
            
            if forecast_value >= thresholds['critical']:
                bottlenecks.append({
                    'resource': resource,
                    'severity': 'critical',
                    'current': forecast.get('current', 0),
                    'forecast': forecast_value,
                    'threshold': thresholds['critical'],
                    'timeframe': f"{forecast.get('hours_ahead', 24)} hours",
                    'action': 'Immediate scaling required',
                })
            elif forecast_value >= thresholds['warning']:
                bottlenecks.append({
                    'resource': resource,
                    'severity': 'warning',
                    'current': forecast.get('current', 0),
                    'forecast': forecast_value,
                    'threshold': thresholds['warning'],
                    'timeframe': f"{forecast.get('hours_ahead', 24)} hours",
                    'action': 'Plan scaling soon',
                })
        
        return bottlenecks


class ScalingRecommender:
    """Generate scaling recommendations"""
    
    def __init__(self):
        self.strategies = {
            'cpu': {
                'scale_up': 'Add more CPU cores or upgrade to faster CPU',
                'optimize': 'Optimize CPU-intensive operations',
                'distribute': 'Distribute load across multiple instances',
            },
            'memory': {
                'scale_up': 'Add more RAM',
                'optimize': 'Fix memory leaks, optimize data structures',
                'cache': 'Implement caching to reduce memory usage',
            },
            'disk': {
                'scale_up': 'Expand storage capacity',
                'cleanup': 'Clean up old files and logs',
                'archive': 'Archive old data to cold storage',
            },
            'network': {
                'scale_up': 'Upgrade network bandwidth',
                'optimize': 'Optimize network calls, implement CDN',
                'compress': 'Enable compression for data transfer',
            },
        }
    
    def recommend(self, bottleneck: Dict) -> Dict:
        """Generate scaling recommendation"""
        resource = bottleneck['resource'].split('_')[0]  # e.g., 'cpu_percent' -> 'cpu'
        
        strategies = self.strategies.get(resource, {})
        
        severity = bottleneck['severity']
        
        if severity == 'critical':
            action = strategies.get('scale_up', 'Scale up immediately')
            urgency = 'immediate'
        elif severity == 'warning':
            action = strategies.get('optimize', 'Optimize usage')
            urgency = 'soon'
        else:
            action = strategies.get('distribute', 'Monitor and plan')
            urgency = 'planned'
        
        # Cost estimate (simplified)
        cost_estimate = self._estimate_cost(resource, bottleneck)
        
        return {
            'resource': bottleneck['resource'],
            'severity': severity,
            'recommended_action': action,
            'urgency': urgency,
            'alternative_actions': list(strategies.values()),
            'cost_estimate': cost_estimate,
            'roi': self._calculate_roi(action, bottleneck),
        }
    
    def _estimate_cost(self, resource: str, bottleneck: Dict) -> Dict:
        """Estimate scaling cost"""
        # Simplified cost estimates (per month)
        costs = {
            'cpu': {'low': 20, 'medium': 50, 'high': 100},
            'memory': {'low': 30, 'medium': 80, 'high': 150},
            'disk': {'low': 10, 'medium': 30, 'high': 100},
            'network': {'low': 15, 'medium': 40, 'high': 80},
        }
        
        resource_type = resource.split('_')[0]
        severity = bottleneck['severity']
        
        cost_tier = 'high' if severity == 'critical' else 'medium' if severity == 'warning' else 'low'
        
        cost_range = costs.get(resource_type, costs['cpu'])
        
        return {
            'estimated_monthly': cost_range.get(cost_tier, 50),
            'currency': 'USD',
            'note': 'Estimated cost for scaling',
        }
    
    def _calculate_roi(self, action: str, bottleneck: Dict) -> Dict:
        """Calculate ROI of scaling"""
        # Simplified ROI calculation
        if bottleneck['severity'] == 'critical':
            # Downtime cost avoided
            downtime_cost_avoided = 500  # per hour
            roi = 5.0  # 5x return
        elif bottleneck['severity'] == 'warning':
            downtime_cost_avoided = 200
            roi = 3.0
        else:
            downtime_cost_avoided = 50
            roi = 1.5
        
        return {
            'downtime_cost_avoided': downtime_cost_avoided,
            'estimated_roi': roi,
            'payback_period': '1-2 months',
        }


class CostOptimizer:
    """Optimize resource costs"""
    
    def analyze(self, usage_data: Dict) -> Dict:
        """Analyze cost optimization opportunities"""
        opportunities = []
        
        # Check for over-provisioning
        for resource, data in usage_data.items():
            if not isinstance(data, dict):
                continue
            
            avg_usage = data.get('average', 0)
            peak_usage = data.get('peak', 0)
            current_capacity = data.get('capacity', 100)
            
            # Over-provisioned if avg < 30% of capacity
            if avg_usage < current_capacity * 0.3:
                opportunities.append({
                    'type': 'over_provisioned',
                    'resource': resource,
                    'current_capacity': current_capacity,
                    'avg_usage': avg_usage,
                    'potential_savings': f"{int((1 - avg_usage/current_capacity) * 100)}%",
                    'recommendation': f'Consider downsizing {resource}',
                    'risk': 'low' if peak_usage < current_capacity * 0.5 else 'medium',
                })
            
            # Under-utilized if peak < 50% of capacity
            elif peak_usage < current_capacity * 0.5:
                opportunities.append({
                    'type': 'under_utilized',
                    'resource': resource,
                    'current_capacity': current_capacity,
                    'peak_usage': peak_usage,
                    'potential_savings': f"{int((1 - peak_usage/current_capacity) * 100)}%",
                    'recommendation': f'Resource {resource} is under-utilized',
                    'risk': 'low',
                })
        
        # Check for reserved instances opportunity
        if usage_data.get('consistent_usage', False):
            opportunities.append({
                'type': 'reserved_instance',
                'recommendation': 'Consider reserved instances for consistent workloads',
                'potential_savings': '30-50%',
                'commitment': '1-3 years',
            })
        
        return {
            'opportunities': opportunities,
            'total_potential_savings': self._calculate_total_savings(opportunities),
            'priority_actions': [o for o in opportunities if o.get('risk') == 'low'][:3],
        }
    
    def _calculate_total_savings(self, opportunities: List[Dict]) -> str:
        """Calculate total potential savings"""
        if not opportunities:
            return '0%'
        
        # Simplified calculation
        avg_savings = statistics.mean([
            int(o.get('potential_savings', '0%').replace('%', ''))
            for o in opportunities
            if 'potential_savings' in o
        ])
        
        return f"{int(avg_savings)}% average"


class CapacityPlanner:
    """
    Resource usage prediction and scaling recommendations
    
    Features:
    - Resource usage forecasting
    - Scaling recommendations
    - Bottleneck prediction
    - Cost optimization
    - Capacity planning reports
    """
    
    def __init__(self):
        self.forecaster = ResourceForecaster()
        self.bottleneck_predictor = BottleneckPredictor()
        self.scaling_recommender = ScalingRecommender()
        self.cost_optimizer = CostOptimizer()
    
    def analyze(self, component: str, metrics: Dict) -> Dict:
        """Analyze capacity"""
        # Add readings
        timestamp = datetime.now().isoformat()
        
        for resource, value in metrics.items():
            if isinstance(value, (int, float)):
                # Normalize to percentage if needed
                if 'percent' in resource:
                    usage = value
                else:
                    usage = min(100, value)
                
                self.forecaster.add_reading(timestamp, resource, usage)
        
        # Forecast for each resource
        forecasts = {}
        for resource in set(r['resource'] for r in self.forecaster.history):
            forecasts[resource] = self.forecaster.forecast(resource, hours_ahead=24)
        
        # Predict bottlenecks
        bottlenecks = self.bottleneck_predictor.predict(forecasts)
        
        # Generate recommendations
        recommendations = []
        for bottleneck in bottlenecks:
            rec = self.scaling_recommender.recommend(bottleneck)
            rec['bottleneck'] = bottleneck
            recommendations.append(rec)
        
        # Cost optimization
        cost_analysis = self.cost_optimizer.analyze(self._prepare_usage_data(forecasts))
        
        # Capacity score
        capacity_score = self._calculate_capacity_score(forecasts, bottlenecks)
        
        return {
            'component': component,
            'timestamp': timestamp,
            'forecasts': forecasts,
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'cost_optimization': cost_analysis,
            'capacity_score': capacity_score,
            'capacity_grade': self._get_capacity_grade(capacity_score),
        }
    
    def _prepare_usage_data(self, forecasts: Dict) -> Dict:
        """Prepare usage data for cost analysis"""
        usage_data = {}
        
        for resource, forecast in forecasts.items():
            if forecast.get('status') == 'success':
                usage_data[resource] = {
                    'average': forecast.get('average', 0),
                    'current': forecast.get('current', 0),
                    'peak': forecast.get('current', 0) * 1.2,  # Estimate
                    'capacity': 100,
                }
        
        return usage_data
    
    def _calculate_capacity_score(self, forecasts: Dict, bottlenecks: List[Dict]) -> float:
        """Calculate capacity health score"""
        score = 1.0
        
        # Penalize for bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck['severity'] == 'critical':
                score -= 0.3
            elif bottleneck['severity'] == 'warning':
                score -= 0.15
        
        # Bonus for good forecasts (low usage)
        for forecast in forecasts.values():
            if forecast.get('status') == 'success':
                if forecast.get('forecast', 0) < 50:
                    score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _get_capacity_grade(self, score: float) -> str:
        """Get capacity grade"""
        if score >= 0.9:
            return 'A (Excellent)'
        elif score >= 0.8:
            return 'B (Good)'
        elif score >= 0.7:
            return 'C (Adequate)'
        elif score >= 0.6:
            return 'D (Needs Improvement)'
        else:
            return 'F (Critical)'
    
    def print_report(self, result: Dict):
        """Print capacity planning report"""
        print("\n" + "=" * 60)
        print("📊 CAPACITY PLANNING REPORT")
        print("=" * 60)
        
        print(f"\n🔧 Component: {result['component']}")
        print(f"Capacity Score: {result['capacity_score']:.1%}")
        print(f"Grade: {result['capacity_grade']}")
        
        # Forecasts
        print(f"\n📈 Resource Forecasts:")
        for resource, forecast in result['forecasts'].items():
            if forecast.get('status') == 'success':
                emoji = "🟢" if forecast['forecast'] < 70 else "🟡" if forecast['forecast'] < 90 else "🔴"
                print(f"   {emoji} {resource}: {forecast['current']:.0f}% → {forecast['forecast']:.0f}% ({forecast['trend']})")
        
        # Bottlenecks
        if result['bottlenecks']:
            print(f"\n⚠️  Predicted Bottlenecks ({len(result['bottlenecks'])}):")
            for bn in result['bottlenecks']:
                print(f"   [{bn['severity'].upper()}] {bn['resource']}: {bn['current']:.0f}% → {bn['forecast']:.0f}%")
                print(f"      Action: {bn['action']}")
        else:
            print(f"\n✅ No bottlenecks predicted")
        
        # Recommendations
        if result['recommendations']:
            print(f"\n💡 Scaling Recommendations:")
            for rec in result['recommendations'][:3]:
                print(f"   [{rec['urgency'].upper()}] {rec['recommended_action']}")
                print(f"      Cost: ${rec['cost_estimate']['estimated_monthly']}/month")
                print(f"      ROI: {rec['roi']['estimated_roi']}x")
        
        # Cost optimization
        if result['cost_optimization']['opportunities']:
            print(f"\n💰 Cost Optimization Opportunities:")
            for opp in result['cost_optimization']['opportunities'][:3]:
                print(f"   {opp['type']}: {opp['recommendation']}")
                print(f"      Savings: {opp['potential_savings']}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Capacity Planner")
    parser.add_argument('--analyze', action='store_true', help='Demo analysis')
    parser.add_argument('--component', type=str, default='system', help='Component name')
    args = parser.parse_args()
    
    planner = CapacityPlanner()
    
    if args.analyze:
        # Demo metrics
        import random
        
        metrics = {
            'cpu_percent': random.uniform(50, 70),
            'memory_percent': random.uniform(60, 80),
            'disk_percent': random.uniform(40, 60),
        }
        
        # Add some historical data
        for i in range(10):
            hist_metrics = {
                'cpu_percent': 50 + i * 2 + random.uniform(-5, 5),
                'memory_percent': 60 + i * 1.5 + random.uniform(-3, 3),
                'disk_percent': 45 + i * 0.5,
            }
            planner.analyze(args.component, hist_metrics)
        
        # Final analysis
        result = planner.analyze(args.component, metrics)
        planner.print_report(result)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
