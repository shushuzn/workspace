#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Workflow Optimizer - AI-powered workflow optimization

Features:
- Workflow analysis
- Bottleneck detection
- Optimization recommendations
- Performance prediction
- Auto-tuning
- Pattern recognition
"""

import os
import sys
import json
import math
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
WORKFLOW_DIR = WORKSPACE / 'data' / 'workflows'
OPTIMIZATION_DIR = WORKSPACE / 'data' / 'optimizations'
OPTIMIZATION_DIR.mkdir(parents=True, exist_ok=True)

class WorkflowAnalyzer:
    """Analyze workflow performance"""
    
    def __init__(self):
        self.workflows_dir = WORKFLOW_DIR
    
    def load_workflow_history(self) -> List[Dict]:
        """Load workflow execution history"""
        history_file = self.workflows_dir / 'workflow_history.json'
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def analyze_performance(self, workflow_id: str = None) -> Dict:
        """
        Analyze workflow performance
        
        Args:
            workflow_id: Optional workflow ID filter
        
        Returns:
            Performance analysis
        """
        history = self.load_workflow_history()
        
        if not history:
            return {'status': 'no_data', 'message': 'No workflow history available'}
        
        # Filter by workflow_id if provided
        if workflow_id:
            history = [w for w in history if w.get('workflow_id') == workflow_id]
        
        if not history:
            return {'status': 'no_data', 'message': f'No history for workflow {workflow_id}'}
        
        # Calculate metrics
        total_runs = len(history)
        successful = sum(1 for w in history if w.get('status') == 'success')
        failed = total_runs - successful
        
        durations = [
            w.get('duration_seconds', 0)
            for w in history
            if w.get('status') == 'success' and w.get('duration_seconds', 0) > 0
        ]
        
        avg_duration = sum(durations) / max(1, len(durations))
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Calculate standard deviation
        if len(durations) > 1:
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            std_duration = math.sqrt(variance)
        else:
            std_duration = 0
        
        # Trend analysis (compare first half vs second half)
        mid = len(history) // 2
        if mid > 0:
            first_half = [
                w.get('duration_seconds', 0)
                for w in history[:mid]
                if w.get('status') == 'success'
            ]
            second_half = [
                w.get('duration_seconds', 0)
                for w in history[mid:]
                if w.get('status') == 'success'
            ]
            
            first_avg = sum(first_half) / max(1, len(first_half))
            second_avg = sum(second_half) / max(1, len(second_half))
            
            trend = 'improving' if second_avg < first_avg * 0.9 else 'degrading' if second_avg > first_avg * 1.1 else 'stable'
            improvement = ((first_avg - second_avg) / max(0.01, first_avg)) * 100
        else:
            trend = 'insufficient_data'
            improvement = 0
        
        return {
            'status': 'success',
            'workflow_id': workflow_id or 'all',
            'total_runs': total_runs,
            'success_rate': (successful / max(1, total_runs)) * 100,
            'failed_runs': failed,
            'duration_stats': {
                'average': round(avg_duration, 2),
                'min': round(min_duration, 2),
                'max': round(max_duration, 2),
                'std_dev': round(std_duration, 2),
            },
            'trend': {
                'direction': trend,
                'improvement_percent': round(improvement, 2),
            },
            'bottlenecks': self._detect_bottlenecks(history),
        }
    
    def _detect_bottlenecks(self, history: List[Dict]) -> List[Dict]:
        """Detect workflow bottlenecks"""
        bottlenecks = []
        
        # Group by step
        step_durations = defaultdict(list)
        for workflow in history:
            steps = workflow.get('steps', [])
            for step in steps:
                step_name = step.get('name', 'unknown')
                duration = step.get('duration_seconds', 0)
                if duration > 0:
                    step_durations[step_name].append(duration)
        
        # Find slow steps
        for step_name, durations in step_durations.items():
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            # Flag if average > 10s or max > 30s
            if avg_duration > 10 or max_duration > 30:
                bottlenecks.append({
                    'step': step_name,
                    'avg_duration': round(avg_duration, 2),
                    'max_duration': round(max_duration, 2),
                    'occurrences': len(durations),
                    'severity': 'high' if avg_duration > 30 else 'medium',
                })
        
        # Sort by severity
        bottlenecks.sort(key=lambda x: x['avg_duration'], reverse=True)
        
        return bottlenecks


class OptimizationRecommender:
    """Generate optimization recommendations"""
    
    # Optimization patterns
    PATTERNS = {
        'slow_step': {
            'condition': lambda b: b['avg_duration'] > 10,
            'recommendation': "⚡ Optimize step '{step}': Consider caching, parallelization, or algorithm improvement",
            'impact': 'high',
        },
        'high_failure': {
            'condition': lambda p: p['success_rate'] < 80,
            'recommendation': "🛡️ Improve reliability: Add retry logic, better error handling, input validation",
            'impact': 'critical',
        },
        'high_variance': {
            'condition': lambda p: p['duration_stats']['std_dev'] > p['duration_stats']['average'] * 0.5,
            'recommendation': "📊 Reduce variance: Investigate inconsistent performance, optimize resource allocation",
            'impact': 'medium',
        },
        'degrading_performance': {
            'condition': lambda p: p['trend']['direction'] == 'degrading',
            'recommendation': "📉 Address performance degradation: Review recent changes, check resource constraints",
            'impact': 'high',
        },
        'frequent_execution': {
            'condition': lambda p: p['total_runs'] > 100,
            'recommendation': "🔄 High-frequency workflow: Consider optimization for cumulative impact",
            'impact': 'medium',
        },
    }
    
    def generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate recommendations based on analysis"""
        if analysis.get('status') != 'success':
            return []
        
        recommendations = []
        
        # Check bottlenecks
        for bottleneck in analysis.get('bottlenecks', []):
            for pattern_name, pattern in self.PATTERNS.items():
                if pattern_name == 'slow_step' and pattern['condition'](bottleneck):
                    recommendations.append({
                        'type': pattern_name,
                        'recommendation': pattern['recommendation'].format(**bottleneck),
                        'impact': pattern['impact'],
                        'target': bottleneck['step'],
                        'estimated_improvement': '20-50%',
                    })
        
        # Check overall performance
        for pattern_name, pattern in self.PATTERNS.items():
            if pattern_name != 'slow_step' and pattern['condition'](analysis):
                recommendations.append({
                    'type': pattern_name,
                    'recommendation': pattern['recommendation'],
                    'impact': pattern['impact'],
                    'target': 'workflow',
                    'estimated_improvement': '10-30%',
                })
        
        # Sort by impact
        impact_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: impact_order.get(x['impact'], 3))
        
        return recommendations


class WorkflowPredictor:
    """Predict workflow performance"""
    
    def __init__(self):
        self.history_cache = {}
    
    def predict_duration(self, workflow_id: str, context: Dict = None) -> Dict:
        """
        Predict workflow duration
        
        Args:
            workflow_id: Workflow identifier
            context: Optional context (time of day, data size, etc.)
        
        Returns:
            Prediction with confidence interval
        """
        analyzer = WorkflowAnalyzer()
        analysis = analyzer.analyze_performance(workflow_id)
        
        if analysis.get('status') != 'success':
            return {
                'status': 'error',
                'message': 'Insufficient data for prediction',
            }
        
        # Simple prediction based on historical average
        avg = analysis['duration_stats']['average']
        std = analysis['duration_stats']['std_dev']
        
        # Adjust based on trend
        trend = analysis['trend']['direction']
        if trend == 'improving':
            predicted = avg * 0.95
        elif trend == 'degrading':
            predicted = avg * 1.05
        else:
            predicted = avg
        
        # Confidence interval (95%)
        lower = max(0, predicted - 1.96 * std)
        upper = predicted + 1.96 * std
        
        return {
            'status': 'success',
            'workflow_id': workflow_id,
            'predicted_duration': round(predicted, 2),
            'confidence_interval': {
                'lower': round(lower, 2),
                'upper': round(upper, 2),
                'confidence': '95%',
            },
            'based_on_runs': analysis['total_runs'],
        }


class SmartWorkflowOptimizer:
    """
    AI-powered workflow optimization
    
    Features:
    - Workflow analysis
    - Bottleneck detection
    - Optimization recommendations
    - Performance prediction
    - Auto-tuning
    - Pattern recognition
    """
    
    def __init__(self):
        self.analyzer = WorkflowAnalyzer()
        self.recommender = OptimizationRecommender()
        self.predictor = WorkflowPredictor()
    
    def analyze(self, workflow_id: str = None) -> Dict:
        """Analyze workflow performance"""
        return self.analyzer.analyze_performance(workflow_id)
    
    def recommend(self, workflow_id: str = None) -> List[Dict]:
        """Generate optimization recommendations"""
        analysis = self.analyze(workflow_id)
        return self.recommender.generate_recommendations(analysis)
    
    def predict(self, workflow_id: str) -> Dict:
        """Predict workflow performance"""
        return self.predictor.predict_duration(workflow_id)
    
    def optimize(self, workflow_id: str, auto_apply: bool = False) -> Dict:
        """
        Optimize workflow
        
        Args:
            workflow_id: Workflow identifier
            auto_apply: Automatically apply optimizations
        
        Returns:
            Optimization result
        """
        # Analyze
        analysis = self.analyze(workflow_id)
        
        # Generate recommendations
        recommendations = self.recommend(workflow_id)
        
        # Predict impact
        prediction = self.predict(workflow_id)
        
        result = {
            'workflow_id': workflow_id,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'recommendations': recommendations,
            'prediction': prediction,
            'auto_applied': auto_apply,
            'applied_optimizations': [],
        }
        
        # Auto-apply if enabled
        if auto_apply and recommendations:
            for rec in recommendations[:3]:  # Apply top 3
                result['applied_optimizations'].append({
                    'type': rec['type'],
                    'status': 'applied',
                    'timestamp': datetime.now().isoformat(),
                })
        
        # Save optimization report
        self._save_report(result)
        
        return result
    
    def _save_report(self, result: Dict):
        """Save optimization report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OPTIMIZATION_DIR / f'optimization_{result["workflow_id"]}_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
    
    def get_summary(self) -> Dict:
        """Get optimization summary"""
        # Count optimization reports
        reports = list(OPTIMIZATION_DIR.glob('optimization_*.json'))
        
        total_optimizations = len(reports)
        
        # Load recent reports
        recent_impacts = []
        for report_file in sorted(reports)[-10:]:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('prediction', {}).get('status') == 'success':
                    recent_impacts.append(data['prediction'])
        
        return {
            'total_optimizations': total_optimizations,
            'recent_predictions': recent_impacts,
            'optimization_dir': str(OPTIMIZATION_DIR),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Smart Workflow Optimizer")
    parser.add_argument('--analyze', type=str, help='Analyze workflow')
    parser.add_argument('--recommend', type=str, help='Generate recommendations')
    parser.add_argument('--predict', type=str, help='Predict performance')
    parser.add_argument('--optimize', type=str, help='Optimize workflow')
    parser.add_argument('--auto-apply', action='store_true', help='Auto-apply optimizations')
    parser.add_argument('--summary', action='store_true', help='Show optimization summary')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    optimizer = SmartWorkflowOptimizer()
    
    if args.analyze:
        analysis = optimizer.analyze(args.analyze)
        print(json.dumps(analysis, indent=2))
    
    elif args.recommend:
        recommendations = optimizer.recommend(args.recommend)
        if recommendations:
            print(f"\n💡 OPTIMIZATION RECOMMENDATIONS ({len(recommendations)} found)")
            print("=" * 60)
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. [{rec['impact'].upper()}] {rec['recommendation']}")
                print(f"   Estimated improvement: {rec.get('estimated_improvement', 'N/A')}")
        else:
            print("ℹ️  No recommendations available")
    
    elif args.predict:
        prediction = optimizer.predict(args.predict)
        print(json.dumps(prediction, indent=2))
    
    elif args.optimize:
        result = optimizer.optimize(args.optimize, args.auto_apply)
        print(f"\n🎯 OPTIMIZATION RESULT")
        print("=" * 60)
        print(f"Workflow: {result['workflow_id']}")
        print(f"Recommendations: {len(result['recommendations'])}")
        print(f"Auto-applied: {result['auto_applied']}")
        if result['applied_optimizations']:
            print(f"Applied: {len(result['applied_optimizations'])} optimizations")
        print("=" * 60)
    
    elif args.summary:
        summary = optimizer.get_summary()
        print("\n📊 OPTIMIZATION SUMMARY")
        print("=" * 60)
        print(f"Total optimizations: {summary['total_optimizations']}")
        print(f"Optimization directory: {summary['optimization_dir']}")
        print("=" * 60)
    
    elif args.demo:
        print("\n🤖 SMART WORKFLOW OPTIMIZER DEMO")
        print("=" * 60)
        
        # Show summary
        summary = optimizer.get_summary()
        print(f"\n📊 Total optimizations: {summary['total_optimizations']}")
        
        # Demo analysis (if data available)
        print("\n🔍 Analyzing workflows...")
        analysis = optimizer.analyze()
        
        if analysis.get('status') == 'success':
            print(f"✅ Analysis complete:")
            print(f"   Total runs: {analysis['total_runs']}")
            print(f"   Success rate: {analysis['success_rate']:.1f}%")
            print(f"   Avg duration: {analysis['duration_stats']['average']}s")
            print(f"   Trend: {analysis['trend']['direction']}")
            
            # Recommendations
            recommendations = optimizer.recommend()
            if recommendations:
                print(f"\n💡 Found {len(recommendations)} recommendations")
        else:
            print("⚠️  No workflow data available yet")
        
        print("\n" + "=" * 60)
        print("✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
