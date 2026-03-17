#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insight Generator - Automated insight generation from metrics

Features:
- Pattern recognition
- Trend analysis
- Correlation detection
- Actionable recommendations
- Natural language generation
- Multi-metric synthesis
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
INSIGHTS_DIR = WORKSPACE / 'data' / 'insights'
INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)

class InsightTemplate:
    """Templates for generating insights"""
    
    TEMPLATES = {
        'deployment_increase': {
            'pattern': 'deployment_count_increasing',
            'template': "📈 Deployment frequency increased by {percent}% over the last {days} days",
            'severity': 'info',
        },
        'deployment_decrease': {
            'pattern': 'deployment_count_decreasing',
            'template': "📉 Deployment frequency decreased by {percent}% over the last {days} days",
            'severity': 'warning',
        },
        'high_failure_rate': {
            'pattern': 'failure_rate_high',
            'template': "⚠️  High deployment failure rate detected: {rate}% (threshold: {threshold}%)",
            'severity': 'critical',
        },
        'slow_deployment': {
            'pattern': 'deployment_duration_high',
            'template': "🐌 Average deployment time increased to {duration}s ({change}% from baseline)",
            'severity': 'warning',
        },
        'fast_deployment': {
            'pattern': 'deployment_duration_low',
            'template': "⚡ Deployment time optimized: {duration}s ({improvement}% faster than baseline)",
            'severity': 'success',
        },
        'anomaly_detected': {
            'pattern': 'anomaly_detected',
            'template': "🚨 Anomaly detected: {metric} value {value} is {deviation}σ from mean",
            'severity': 'warning',
        },
        'trend_reversal': {
            'pattern': 'trend_reversal',
            'template': "🔄 Trend reversal detected: {metric} changed from {old_trend} to {new_trend}",
            'severity': 'info',
        },
        'milestone_reached': {
            'pattern': 'milestone_reached',
            'template': "🎯 Milestone reached: {metric} reached {value}",
            'severity': 'success',
        },
        'correlation_detected': {
            'pattern': 'correlation_detected',
            'template': "🔗 Correlation detected: {metric1} and {metric2} (r={correlation:.2f})",
            'severity': 'info',
        },
        'recommendation': {
            'pattern': 'recommendation',
            'template': "💡 Recommendation: {action} to improve {metric}",
            'severity': 'info',
        },
    }
    
    @classmethod
    def generate(cls, insight_type: str, **kwargs) -> Dict:
        """Generate insight from template"""
        template = cls.TEMPLATES.get(insight_type)
        if not template:
            return None
        
        # Format template
        try:
            message = template['template'].format(**kwargs)
        except KeyError as e:
            return {
                'error': f'Missing parameter: {e}',
                'type': insight_type,
            }
        
        return {
            'type': insight_type,
            'pattern': template['pattern'],
            'message': message,
            'severity': template['severity'],
            'timestamp': datetime.now().isoformat(),
            'parameters': kwargs,
        }


class PatternRecognizer:
    """Recognize patterns in metrics"""
    
    def __init__(self, data: List[float], window_size: int = 7):
        self.data = data
        self.window_size = window_size
    
    def detect_trend(self) -> str:
        """Detect trend direction"""
        if len(self.data) < 2:
            return 'unknown'
        
        # Compare recent vs older
        window = min(self.window_size, len(self.data) // 2)
        if window < 1:
            return 'unknown'
        
        recent = self.data[-window:]
        older = self.data[-(window*2):-window] if len(self.data) >= window*2 else self.data[:window]
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        change = (recent_avg - older_avg) / max(0.01, older_avg)
        
        if change > 0.1:
            return 'increasing'
        elif change < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def detect_change_point(self) -> Optional[int]:
        """Detect significant change points"""
        if len(self.data) < 3:
            return None
        
        for i in range(1, len(self.data) - 1):
            before = self.data[max(0, i-3):i]
            after = self.data[i:min(len(self.data), i+3)]
            
            if before and after:
                before_avg = sum(before) / len(before)
                after_avg = sum(after) / len(after)
                
                change = abs(after_avg - before_avg) / max(0.01, before_avg)
                if change > 0.3:  # 30% change
                    return i
        
        return None
    
    def detect_seasonality(self, period: int = 7) -> bool:
        """Detect seasonal patterns"""
        if len(self.data) < period * 2:
            return False
        
        # Compare same positions in different periods
        correlations = []
        for i in range(period):
            values1 = [self.data[j] for j in range(i, len(self.data), period)]
            values2 = [self.data[j+period] for j in range(i, len(self.data)-period, period)]
            
            if len(values1) > 1 and len(values2) > 1:
                # Simple correlation
                mean1 = sum(values1) / len(values1)
                mean2 = sum(values2) / len(values2)
                
                if abs(mean1 - mean2) / max(0.01, mean1) < 0.2:
                    correlations.append(True)
        
        return sum(correlations) / max(1, len(correlations)) > 0.5


class InsightGenerator:
    """
    Automated insight generation
    
    Features:
    - Pattern recognition
    - Trend analysis
    - Correlation detection
    - Actionable recommendations
    - Natural language generation
    """
    
    def __init__(self):
        self.deployments_file = WORKSPACE / 'data' / 'deploy' / 'deployment_history.json'
        self.tool_usage_file = WORKSPACE / 'data' / 'tool_registry' / 'usage_stats.json'
        
        self.insights = []
    
    def load_deployment_data(self) -> List[Dict]:
        """Load deployment history"""
        if not self.deployments_file.exists():
            return []
        
        with open(self.deployments_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_tool_usage_data(self) -> Dict:
        """Load tool usage statistics"""
        if not self.tool_usage_file.exists():
            return {}
        
        with open(self.tool_usage_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_deployments(self) -> List[Dict]:
        """Analyze deployment data and generate insights"""
        deployments = self.load_deployment_data()
        
        if not deployments:
            return []
        
        insights = []
        
        # Extract metrics
        total = len(deployments)
        successful = sum(1 for d in deployments if d.get('status') == 'success')
        failed = total - successful
        
        # Failure rate insight
        if total > 0:
            failure_rate = (failed / total) * 100
            if failure_rate > 20:  # >20% failure rate
                insight = InsightTemplate.generate(
                    'high_failure_rate',
                    rate=round(failure_rate, 1),
                    threshold=20,
                )
                if insight:
                    insights.append(insight)
        
        # Duration analysis
        durations = [
            d.get('duration_seconds', 0)
            for d in deployments
            if d.get('status') == 'success' and d.get('duration_seconds', 0) > 0
        ]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            
            # Compare first half vs second half
            mid = len(durations) // 2
            if mid > 0:
                old_avg = sum(durations[:mid]) / mid
                new_avg = sum(durations[mid:]) / (len(durations) - mid)
                
                change = ((new_avg - old_avg) / max(0.01, old_avg)) * 100
                
                if change > 20:
                    insight = InsightTemplate.generate(
                        'slow_deployment',
                        duration=round(new_avg, 1),
                        change=round(change, 1),
                    )
                    if insight:
                        insights.append(insight)
                elif change < -20:
                    insight = InsightTemplate.generate(
                        'fast_deployment',
                        duration=round(new_avg, 1),
                        improvement=round(abs(change), 1),
                    )
                    if insight:
                        insights.append(insight)
        
        # Trend analysis
        if total >= 7:
            # Group by day
            by_day = defaultdict(int)
            for dep in deployments:
                try:
                    day = datetime.fromisoformat(dep['timestamp']).date()
                    by_day[str(day)] += 1
                except:
                    pass
            
            daily_counts = [count for _, count in sorted(by_day.items())]
            
            if len(daily_counts) >= 2:
                recognizer = PatternRecognizer(daily_counts)
                trend = recognizer.detect_trend()
                
                if trend == 'increasing':
                    old_avg = sum(daily_counts[:len(daily_counts)//2]) / max(1, len(daily_counts)//2)
                    new_avg = sum(daily_counts[len(daily_counts)//2:]) / max(1, len(daily_counts) - len(daily_counts)//2)
                    percent_change = ((new_avg - old_avg) / max(0.01, old_avg)) * 100
                    
                    insight = InsightTemplate.generate(
                        'deployment_increase',
                        percent=round(percent_change, 1),
                        days=len(daily_counts),
                    )
                    if insight:
                        insights.append(insight)
        
        return insights
    
    def analyze_tool_usage(self) -> List[Dict]:
        """Analyze tool usage and generate insights"""
        usage_data = self.load_tool_usage_data()
        
        if not usage_data:
            return []
        
        insights = []
        
        # Find most used tools
        total_runs = sum(u.get('total_runs', 0) for u in usage_data.values())
        
        if total_runs > 0:
            top_tools = sorted(
                usage_data.items(),
                key=lambda x: x[1].get('total_runs', 0),
                reverse=True
            )[:5]
            
            # Milestone insight
            if total_runs >= 1000:
                insight = InsightTemplate.generate(
                    'milestone_reached',
                    metric='Total tool runs',
                    value=total_runs,
                )
                if insight:
                    insights.append(insight)
        
        return insights
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on deployment analysis
        deployments = self.load_deployment_data()
        
        if deployments:
            failed = sum(1 for d in deployments if d.get('status') == 'failed')
            total = len(deployments)
            
            if total > 0 and failed / total > 0.1:
                rec = InsightTemplate.generate(
                    'recommendation',
                    action='Implement automated testing before deployment',
                    metric='deployment success rate',
                )
                if rec:
                    recommendations.append(rec)
        
        # Based on tool usage
        usage_data = self.load_tool_usage_data()
        
        if usage_data:
            # Find unused tools
            unused = [
                name for name, data in usage_data.items()
                if data.get('total_runs', 0) == 0
            ]
            
            if len(unused) > 5:
                rec = InsightTemplate.generate(
                    'recommendation',
                    action=f'Review and potentially remove {len(unused)} unused tools',
                    metric='tool utilization',
                )
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def generate_all_insights(self) -> Dict:
        """Generate comprehensive insights"""
        deployment_insights = self.analyze_deployments()
        usage_insights = self.analyze_tool_usage()
        recommendations = self.generate_recommendations()
        
        all_insights = deployment_insights + usage_insights + recommendations
        
        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'success': 3}
        all_insights.sort(key=lambda x: severity_order.get(x.get('severity', 'info'), 2))
        
        report = {
            'generated': datetime.now().isoformat(),
            'total_insights': len(all_insights),
            'by_severity': {
                'critical': sum(1 for i in all_insights if i.get('severity') == 'critical'),
                'warning': sum(1 for i in all_insights if i.get('severity') == 'warning'),
                'info': sum(1 for i in all_insights if i.get('severity') == 'info'),
                'success': sum(1 for i in all_insights if i.get('severity') == 'success'),
            },
            'insights': all_insights,
            'recommendations': recommendations,
        }
        
        return report
    
    def save_insights(self, output_file: Path = None) -> Path:
        """Save insights to file"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = INSIGHTS_DIR / f'insights_{timestamp}.json'
        
        report = self.generate_all_insights()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Insights saved: {output_file}")
        return output_file
    
    def print_summary(self):
        """Print insights summary"""
        report = self.generate_all_insights()
        
        print("\n💡 INSIGHT GENERATOR SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Total insights: {report['total_insights']}")
        print(f"   Critical: {report['by_severity']['critical']}")
        print(f"   Warning: {report['by_severity']['warning']}")
        print(f"   Info: {report['by_severity']['info']}")
        print(f"   Success: {report['by_severity']['success']}")
        
        print(f"\n🔍 KEY INSIGHTS:")
        for insight in report['insights'][:5]:
            print(f"   [{insight.get('severity', 'info').upper()}] {insight.get('message', 'N/A')}")
        
        if report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations'][:3]:
                print(f"   {rec.get('message', 'N/A')}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Insight Generator")
    parser.add_argument('--analyze', action='store_true', help='Analyze and generate insights')
    parser.add_argument('--recommend', action='store_true', help='Generate recommendations')
    parser.add_argument('--save', action='store_true', help='Save insights to file')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    generator = InsightGenerator()
    
    if args.analyze:
        generator.print_summary()
    
    elif args.recommend:
        recs = generator.generate_recommendations()
        print(json.dumps(recs, indent=2))
    
    elif args.save:
        generator.save_insights()
    
    elif args.demo:
        print("\n💡 Insight Generator Demo")
        print("=" * 60)
        generator.print_summary()
        print("\n✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
