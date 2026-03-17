#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration Analyzer
Analyze collaboration patterns, identify bottlenecks, suggest optimizations
Features: pattern mining, bottleneck detection, optimization recommendations

Usage:
    python persona_analyzer.py --analyze
    python persona_analyzer.py --report
    python persona_analyzer.py --optimize
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class PersonaAnalyzer:
    """Analyze persona collaboration patterns"""
    
    def __init__(self):
        self.state_file = WORKSPACE / "20-data-reports" / "persona_state.json"
        self.orchestrator_stats = WORKSPACE / "20-data-reports" / "persona_orchestrator_stats.json"
        self.reports_dir = WORKSPACE / "20-data-reports"
    
    def load_state(self) -> Dict:
        """Load persona state"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_stats(self) -> Dict:
        """Load orchestrator stats"""
        if self.orchestrator_stats.exists():
            with open(self.orchestrator_stats, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def analyze_patterns(self) -> Dict:
        """Analyze collaboration patterns"""
        state = self.load_state()
        personas = state.get('personas', {})
        
        patterns = {
            'workload_distribution': self._analyze_workload(personas),
            'communication_patterns': self._analyze_communication(personas),
            'conflict_patterns': self._analyze_conflicts(state),
            'performance_trends': self._analyze_performance()
        }
        
        return patterns
    
    def _analyze_workload(self, personas: Dict) -> Dict:
        """Analyze workload distribution"""
        if not personas:
            return {'balance': 0, 'overloaded': [], 'underloaded': []}
        
        workloads = {name: data.get('workload', 0) for name, data in personas.items()}
        avg_workload = sum(workloads.values()) / len(workloads)
        variance = sum((w - avg_workload) ** 2 for w in workloads.values()) / len(workloads)
        
        overloaded = [name for name, w in workloads.items() if w > avg_workload + 20]
        underloaded = [name for name, w in workloads.items() if w < avg_workload - 20]
        
        return {
            'average': avg_workload,
            'variance': variance,
            'balance': 100 - min(variance / 100, 100),
            'overloaded': overloaded,
            'underloaded': underloaded
        }
    
    def _analyze_communication(self, personas: Dict) -> Dict:
        """Analyze communication patterns"""
        if not personas:
            return {'total_messages': 0, 'active': [], 'silent': []}
        
        total = sum(p.get('messages_sent', 0) + p.get('messages_received', 0) 
                   for p in personas.values())
        
        active = [name for name, p in personas.items() 
                 if p.get('messages_sent', 0) > 10]
        silent = [name for name, p in personas.items() 
                 if p.get('messages_sent', 0) < 5]
        
        return {
            'total_messages': total,
            'active_personas': active,
            'silent_personas': silent,
            'avg_per_persona': total / max(1, len(personas))
        }
    
    def _analyze_conflicts(self, state: Dict) -> Dict:
        """Analyze conflict patterns"""
        conflicts = state.get('conflicts', [])
        
        if not conflicts:
            return {'total': 0, 'resolved': 0, 'rate': 0}
        
        resolved = sum(1 for c in conflicts if c.get('status') == 'resolved')
        
        by_severity = defaultdict(int)
        for c in conflicts:
            by_severity[c.get('severity', 'unknown')] += 1
        
        return {
            'total': len(conflicts),
            'resolved': resolved,
            'pending': len(conflicts) - resolved,
            'resolution_rate': resolved / len(conflicts) * 100,
            'by_severity': dict(by_severity)
        }
    
    def _analyze_performance(self) -> Dict:
        """Analyze performance trends"""
        stats = self.load_stats()
        
        return {
            'total_tasks': stats.get('total_tasks', 0),
            'success_rate': stats.get('success_rate', 0),
            'avg_execution_time': stats.get('avg_execution_time', 0),
            'last_24h': stats.get('last_24h', {})
        }
    
    def detect_bottlenecks(self) -> List[Dict]:
        """Detect collaboration bottlenecks"""
        bottlenecks = []
        patterns = self.analyze_patterns()
        
        # Workload imbalance
        if patterns['workload_distribution']['balance'] < 60:
            bottlenecks.append({
                'type': 'workload_imbalance',
                'severity': 'high',
                'description': 'Significant workload imbalance detected',
                'affected': patterns['workload_distribution']['overloaded'],
                'recommendation': 'Redistribute tasks via Coordinator'
            })
        
        # Communication gaps
        if patterns['communication_patterns']['silent_personas']:
            bottlenecks.append({
                'type': 'communication_gap',
                'severity': 'medium',
                'description': 'Some personas are not communicating enough',
                'affected': patterns['communication_patterns']['silent_personas'],
                'recommendation': 'Encourage inter-persona messaging'
            })
        
        # Low resolution rate
        if patterns['conflict_patterns'].get('resolution_rate', 100) < 70:
            bottlenecks.append({
                'type': 'conflict_resolution',
                'severity': 'high',
                'description': 'Low conflict resolution rate',
                'data': patterns['conflict_patterns'],
                'recommendation': 'Improve arbitration process'
            })
        
        # Low success rate
        if patterns['performance_trends'].get('success_rate', 100) < 85:
            bottlenecks.append({
                'type': 'low_success_rate',
                'severity': 'critical',
                'description': 'Task success rate below threshold',
                'data': patterns['performance_trends'],
                'recommendation': 'Review failure patterns and adjust workflow'
            })
        
        return bottlenecks
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate optimization recommendations"""
        recommendations = []
        bottlenecks = self.detect_bottlenecks()
        patterns = self.analyze_patterns()
        
        for bottleneck in bottlenecks:
            rec = {
                'priority': 'high' if bottleneck['severity'] in ['high', 'critical'] else 'medium',
                'category': bottleneck['type'],
                'action': bottleneck['recommendation'],
                'impact': 'high',
                'effort': 'medium'
            }
            recommendations.append(rec)
        
        # Proactive recommendations
        state = self.load_state()
        personas = state.get('personas', {})
        
        # Check individual persona scores
        for name, data in personas.items():
            collab_score = data.get('collaboration_score', 1)
            if collab_score < 0.75:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'persona_improvement',
                    'action': f'Improve {name} collaboration score (current: {collab_score*100:.0f}%)',
                    'impact': 'medium',
                    'effort': 'low'
                })
        
        return recommendations
    
    def generate_report(self, save: bool = True) -> str:
        """Generate comprehensive analysis report"""
        patterns = self.analyze_patterns()
        bottlenecks = self.detect_bottlenecks()
        recommendations = self.generate_recommendations()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║  Persona Collaboration Analysis Report                   ║
╚══════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
WORKLOAD DISTRIBUTION
{'='*60}
Average Workload: {patterns['workload_distribution']['average']:.1f}%
Balance Score: {patterns['workload_distribution']['balance']:.1f}/100
Variance: {patterns['workload_distribution']['variance']:.1f}

Overloaded: {', '.join(patterns['workload_distribution']['overloaded']) or 'None'}
Underloaded: {', '.join(patterns['workload_distribution']['underloaded']) or 'None'}

{'='*60}
COMMUNICATION PATTERNS
{'='*60}
Total Messages: {patterns['communication_patterns']['total_messages']}
Average per Persona: {patterns['communication_patterns']['avg_per_persona']:.1f}

Active Personas: {', '.join(patterns['communication_patterns']['active_personas']) or 'None'}
Silent Personas: {', '.join(patterns['communication_patterns']['silent_personas']) or 'None'}

{'='*60}
CONFLICT ANALYSIS
{'='*60}
Total Conflicts: {patterns['conflict_patterns']['total']}
Resolved: {patterns['conflict_patterns']['resolved']}
Pending: {patterns['conflict_patterns']['pending']}
Resolution Rate: {patterns['conflict_patterns']['resolution_rate']:.1f}%

By Severity:
{json.dumps(patterns['conflict_patterns'].get('by_severity', {}), indent=2)}

{'='*60}
PERFORMANCE METRICS
{'='*60}
Total Tasks: {patterns['performance_trends']['total_tasks']}
Success Rate: {patterns['performance_trends']['success_rate']:.1f}%
Avg Execution Time: {patterns['performance_trends']['avg_execution_time']:.1f}s

Last 24 Hours:
  Tasks: {patterns['performance_trends'].get('last_24h', {}).get('count', 0)}
  Success Rate: {patterns['performance_trends'].get('last_24h', {}).get('success_rate', 0):.1f}%

{'='*60}
BOTTLENECKS DETECTED: {len(bottlenecks)}
{'='*60}
"""
        
        if bottlenecks:
            for i, b in enumerate(bottlenecks, 1):
                report += f"""
{i}. {b['type'].upper()}
   Severity: {b['severity']}
   Description: {b['description']}
   Recommendation: {b['recommendation']}
"""
        else:
            report += "\nNo critical bottlenecks detected ✅\n"
        
        report += f"""
{'='*60}
RECOMMENDATIONS: {len(recommendations)}
{'='*60}
"""
        
        if recommendations:
            for i, r in enumerate(recommendations, 1):
                report += f"""
{i}. [{r['priority'].upper()}] {r['category']}
   Action: {r['action']}
   Impact: {r['impact']} | Effort: {r['effort']}
"""
        else:
            report += "\nNo immediate recommendations - system operating optimally ✅\n"
        
        report += f"""
{'='*60}
OVERALL HEALTH SCORE
{'='*60}
"""
        
        # Calculate overall health
        health_score = (
            patterns['workload_distribution']['balance'] * 0.25 +
            patterns['performance_trends']['success_rate'] * 0.35 +
            patterns['conflict_patterns'].get('resolution_rate', 100) * 0.25 +
            (100 - len(bottlenecks) * 10) * 0.15
        )
        
        health_score = max(0, min(100, health_score))
        
        if health_score >= 90:
            grade = 'A'
            status = 'Excellent'
        elif health_score >= 80:
            grade = 'B'
            status = 'Good'
        elif health_score >= 70:
            grade = 'C'
            status = 'Fair'
        else:
            grade = 'D'
            status = 'Needs Improvement'
        
        report += f"""
Health Score: {health_score:.1f}/100
Grade: {grade}
Status: {status}

{'='*60}
"""
        
        if save:
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.reports_dir / f"persona_analysis_{timestamp}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"[ANALYZER] Report saved: {report_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Persona Collaboration Analyzer')
    parser.add_argument('--analyze', action='store_true', help='Run pattern analysis')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--optimize', action='store_true', help='Generate recommendations')
    parser.add_argument('--bottlenecks', action='store_true', help='Detect bottlenecks')
    args = parser.parse_args()
    
    analyzer = PersonaAnalyzer()
    
    if args.analyze:
        patterns = analyzer.analyze_patterns()
        print(json.dumps(patterns, indent=2))
    
    elif args.report:
        report = analyzer.generate_report()
        print(report)
    
    elif args.optimize:
        recs = analyzer.generate_recommendations()
        print(f"\nRecommendations: {len(recs)}\n")
        for r in recs:
            print(f"[{r['priority'].upper()}] {r['action']}")
    
    elif args.bottlenecks:
        bottlenecks = analyzer.detect_bottlenecks()
        print(f"\nBottlenecks: {len(bottlenecks)}\n")
        for b in bottlenecks:
            print(f"[{b['severity'].upper()}] {b['type']}: {b['description']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
