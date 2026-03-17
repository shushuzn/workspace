#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resilience Analyzer - System resilience analysis

Features:
- Resilience scoring
- Failure mode analysis
- Recovery time estimation
- Redundancy checking
- Stress test simulation
- Improvement recommendations
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'resilience'
DATA_DIR.mkdir(parents=True, exist_ok=True)

RESILIENCE_LOG = DATA_DIR / 'resilience_log.json'

class FailureModeAnalyzer:
    """Analyze failure modes"""
    
    def __init__(self):
        self.failure_modes = {
            'single_point_of_failure': {
                'description': 'Component with no redundancy',
                'indicators': ['no_backup', 'single_instance', 'no_failover'],
                'severity': 'critical',
                'mitigation': [
                    'Add redundancy',
                    'Implement failover',
                    'Create backup',
                ],
            },
            'cascading_failure': {
                'description': 'Failure propagates to other components',
                'indicators': ['tight_coupling', 'no_circuit_breaker', 'synchronous_calls'],
                'severity': 'high',
                'mitigation': [
                    'Add circuit breakers',
                    'Implement async communication',
                    'Add bulkheads',
                ],
            },
            'resource_exhaustion': {
                'description': 'Resources depleted under load',
                'indicators': ['no_rate_limit', 'unbounded_queue', 'no_backpressure'],
                'severity': 'high',
                'mitigation': [
                    'Add rate limiting',
                    'Implement backpressure',
                    'Set resource limits',
                ],
            },
            'dependency_failure': {
                'description': 'External dependency failure',
                'indicators': ['external_api', 'no_fallback', 'hard_dependency'],
                'severity': 'medium',
                'mitigation': [
                    'Add fallbacks',
                    'Cache responses',
                    'Implement retry logic',
                ],
            },
            'configuration_error': {
                'description': 'Misconfiguration causes failure',
                'indicators': ['manual_config', 'no_validation', 'environment_specific'],
                'severity': 'medium',
                'mitigation': [
                    'Automate configuration',
                    'Add validation',
                    'Use configuration management',
                ],
            },
        }
    
    def analyze(self, system_config: Dict) -> List[Dict]:
        """Analyze system for failure modes"""
        identified_modes = []
        
        # Check for single points of failure
        components = system_config.get('components', [])
        for component in components:
            if not component.get('redundant', False):
                identified_modes.append({
                    'mode': 'single_point_of_failure',
                    'component': component.get('name', 'unknown'),
                    'severity': 'critical',
                    'description': self.failure_modes['single_point_of_failure']['description'],
                    'mitigation': self.failure_modes['single_point_of_failure']['mitigation'],
                })
        
        # Check for tight coupling
        dependencies = system_config.get('dependencies', [])
        sync_calls = sum(1 for d in dependencies if d.get('type') == 'synchronous')
        
        if sync_calls > len(dependencies) * 0.7:
            identified_modes.append({
                'mode': 'cascading_failure',
                'severity': 'high',
                'description': f'{sync_calls}/{len(dependencies)} synchronous dependencies',
                'mitigation': self.failure_modes['cascading_failure']['mitigation'],
            })
        
        # Check for missing rate limiting
        if not system_config.get('rate_limiting', False):
            identified_modes.append({
                'mode': 'resource_exhaustion',
                'severity': 'high',
                'description': 'No rate limiting configured',
                'mitigation': self.failure_modes['resource_exhaustion']['mitigation'],
            })
        
        # Check for external dependencies without fallbacks
        external_deps = [d for d in dependencies if d.get('external', False)]
        no_fallback = sum(1 for d in external_deps if not d.get('fallback', False))
        
        if no_fallback > 0:
            identified_modes.append({
                'mode': 'dependency_failure',
                'severity': 'medium',
                'description': f'{no_fallback} external dependencies without fallback',
                'mitigation': self.failure_modes['dependency_failure']['mitigation'],
            })
        
        return identified_modes


class RecoveryTimeEstimator:
    """Estimate recovery time"""
    
    def __init__(self):
        # Base recovery times (seconds)
        self.base_times = {
            'restart_service': 30,
            'failover': 60,
            'restore_backup': 300,
            'scale_up': 120,
            'rollback': 60,
            'manual_intervention': 900,
        }
    
    def estimate(self, failure_scenario: Dict) -> Dict:
        """Estimate recovery time for scenario"""
        failure_type = failure_scenario.get('type', 'unknown')
        complexity = failure_scenario.get('complexity', 'medium')
        automation = failure_scenario.get('automation_level', 'manual')
        
        # Base time
        base_time = self._get_base_time(failure_type)
        
        # Complexity multiplier
        complexity_mult = {'low': 0.5, 'medium': 1.0, 'high': 2.0, 'critical': 3.0}
        
        # Automation multiplier
        automation_mult = {'automatic': 0.2, 'semi_automatic': 0.5, 'manual': 1.0}
        
        estimated_time = base_time * complexity_mult.get(complexity, 1.0) * automation_mult.get(automation, 1.0)
        
        # Add variance
        optimistic = estimated_time * 0.7
        pessimistic = estimated_time * 1.5
        
        return {
            'estimated_time': round(estimated_time, 0),
            'optimistic': round(optimistic, 0),
            'pessimistic': round(pessimistic, 0),
            'formatted': self._format_time(estimated_time),
            'factors': {
                'base_time': base_time,
                'complexity': complexity,
                'automation': automation,
            },
        }
    
    def _get_base_time(self, failure_type: str) -> float:
        """Get base recovery time"""
        type_mapping = {
            'service_crash': 'restart_service',
            'hardware_failure': 'failover',
            'data_corruption': 'restore_backup',
            'overload': 'scale_up',
            'bad_deployment': 'rollback',
            'unknown': 'manual_intervention',
        }
        
        recovery_type = type_mapping.get(failure_type, 'manual_intervention')
        return self.base_times.get(recovery_type, 300)
    
    def _format_time(self, seconds: float) -> str:
        """Format time"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.2f}h"


class RedundancyChecker:
    """Check system redundancy"""
    
    def check(self, system_config: Dict) -> Dict:
        """Check redundancy levels"""
        components = system_config.get('components', [])
        
        redundancy_scores = {}
        
        for component in components:
            name = component.get('name', 'unknown')
            
            # Check redundancy factors
            instances = component.get('instances', 1)
            has_backup = component.get('backup', False)
            has_failover = component.get('failover', False)
            geographic_distribution = component.get('geo_dist', False)
            
            # Calculate score
            score = 0.0
            
            if instances >= 3:
                score += 0.4
            elif instances >= 2:
                score += 0.25
            
            if has_backup:
                score += 0.2
            if has_failover:
                score += 0.2
            if geographic_distribution:
                score += 0.2
            
            redundancy_scores[name] = {
                'score': min(1.0, score),
                'level': self._get_redundancy_level(score),
                'instances': instances,
                'backup': has_backup,
                'failover': has_failover,
                'geo_dist': geographic_distribution,
            }
        
        # Overall score
        if redundancy_scores:
            overall = statistics.mean([r['score'] for r in redundancy_scores.values()])
        else:
            overall = 0.0
        
        return {
            'components': redundancy_scores,
            'overall_score': overall,
            'overall_level': self._get_redundancy_level(overall),
            'total_components': len(components),
            'redundant_count': sum(1 for r in redundancy_scores.values() if r['score'] > 0.5),
        }
    
    def _get_redundancy_level(self, score: float) -> str:
        """Get redundancy level"""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'adequate'
        elif score >= 0.2:
            return 'poor'
        else:
            return 'critical'


class StressTestSimulator:
    """Simulate stress tests"""
    
    def simulate(self, system_config: Dict, stress_level: str = 'high') -> Dict:
        """Simulate stress test"""
        # Define stress scenarios
        scenarios = {
            'load_spike': {
                'description': 'Sudden 10x traffic increase',
                'impact': self._simulate_load_spike(system_config),
            },
            'dependency_failure': {
                'description': 'Critical dependency fails',
                'impact': self._simulate_dependency_failure(system_config),
            },
            'resource_exhaustion': {
                'description': 'Memory/CPU exhaustion',
                'impact': self._simulate_resource_exhaustion(system_config),
            },
            'network_partition': {
                'description': 'Network split',
                'impact': self._simulate_network_partition(system_config),
            },
        }
        
        # Calculate resilience score
        total_impact = sum(s['impact']['survival_rate'] for s in scenarios.values())
        avg_survival = total_impact / len(scenarios)
        
        return {
            'stress_level': stress_level,
            'scenarios': scenarios,
            'overall_resilience': avg_survival,
            'resilience_grade': self._get_grade(avg_survival),
            'weakest_link': self._find_weakest_link(scenarios),
        }
    
    def _simulate_load_spike(self, system_config: Dict) -> Dict:
        """Simulate load spike"""
        has_autoscaling = system_config.get('autoscaling', False)
        has_rate_limiting = system_config.get('rate_limiting', False)
        capacity_headroom = system_config.get('capacity_headroom', 0.2)
        
        survival_rate = 0.5  # Base
        
        if has_autoscaling:
            survival_rate += 0.3
        if has_rate_limiting:
            survival_rate += 0.1
        survival_rate += capacity_headroom * 0.2
        
        return {
            'survival_rate': min(1.0, survival_rate),
            'degradation': 'graceful' if has_rate_limiting else 'catastrophic',
            'recovery_time': 'fast' if has_autoscaling else 'slow',
        }
    
    def _simulate_dependency_failure(self, system_config: Dict) -> Dict:
        """Simulate dependency failure"""
        dependencies = system_config.get('dependencies', [])
        
        has_fallback = sum(1 for d in dependencies if d.get('fallback', False))
        has_circuit_breaker = system_config.get('circuit_breaker', False)
        
        survival_rate = 0.6
        
        if has_fallback > 0:
            survival_rate += 0.2
        if has_circuit_breaker:
            survival_rate += 0.15
        
        return {
            'survival_rate': min(1.0, survival_rate),
            'fallback_available': has_fallback > 0,
            'circuit_breaker': has_circuit_breaker,
        }
    
    def _simulate_resource_exhaustion(self, system_config: Dict) -> Dict:
        """Simulate resource exhaustion"""
        has_monitoring = system_config.get('monitoring', False)
        has_autoscaling = system_config.get('autoscaling', False)
        has_resource_limits = system_config.get('resource_limits', False)
        
        survival_rate = 0.5
        
        if has_monitoring:
            survival_rate += 0.15
        if has_autoscaling:
            survival_rate += 0.25
        if has_resource_limits:
            survival_rate += 0.1
        
        return {
            'survival_rate': min(1.0, survival_rate),
            'detection': 'automatic' if has_monitoring else 'manual',
            'mitigation': 'automatic' if has_autoscaling else 'manual',
        }
    
    def _simulate_network_partition(self, system_config: Dict) -> Dict:
        """Simulate network partition"""
        has_multi_region = system_config.get('multi_region', False)
        has_consensus = system_config.get('consensus_mechanism', False)
        
        survival_rate = 0.4
        
        if has_multi_region:
            survival_rate += 0.4
        if has_consensus:
            survival_rate += 0.15
        
        return {
            'survival_rate': min(1.0, survival_rate),
            'multi_region': has_multi_region,
            'data_consistency': 'maintained' if has_consensus else 'at_risk',
        }
    
    def _get_grade(self, score: float) -> str:
        """Get resilience grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.6:
            return 'C'
        elif score >= 0.5:
            return 'D'
        else:
            return 'F'
    
    def _find_weakest_link(self, scenarios: Dict) -> str:
        """Find weakest scenario"""
        min_survival = 1.0
        weakest = None
        
        for name, scenario in scenarios.items():
            if scenario['impact']['survival_rate'] < min_survival:
                min_survival = scenario['impact']['survival_rate']
                weakest = name
        
        return weakest


class ResilienceAnalyzer:
    """
    System resilience analysis
    
    Features:
    - Resilience scoring
    - Failure mode analysis
    - Recovery time estimation
    - Redundancy checking
    - Stress test simulation
    - Improvement recommendations
    """
    
    def __init__(self):
        self.failure_analyzer = FailureModeAnalyzer()
        self.recovery_estimator = RecoveryTimeEstimator()
        self.redundancy_checker = RedundancyChecker()
        self.stress_simulator = StressTestSimulator()
    
    def analyze(self, system_config: Dict) -> Dict:
        """Full resilience analysis"""
        # Failure modes
        failure_modes = self.failure_analyzer.analyze(system_config)
        
        # Redundancy
        redundancy = self.redundancy_checker.check(system_config)
        
        # Stress test
        stress_test = self.stress_simulator.simulate(system_config)
        
        # Recovery times
        recovery_estimates = self._estimate_recovery_times(failure_modes)
        
        # Overall resilience score
        resilience_score = self._calculate_resilience_score(
            failure_modes, redundancy, stress_test
        )
        
        # Recommendations
        recommendations = self._generate_recommendations(
            failure_modes, redundancy, stress_test
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'resilience_score': resilience_score,
            'resilience_grade': self._get_grade(resilience_score),
            'failure_modes': failure_modes,
            'redundancy': redundancy,
            'stress_test': stress_test,
            'recovery_estimates': recovery_estimates,
            'recommendations': recommendations,
        }
    
    def _estimate_recovery_times(self, failure_modes: List[Dict]) -> List[Dict]:
        """Estimate recovery times for failure modes"""
        estimates = []
        
        for mode in failure_modes:
            scenario = {
                'type': mode['mode'],
                'complexity': 'high' if mode['severity'] == 'critical' else 'medium',
                'automation_level': 'manual',  # Assume manual by default
            }
            
            estimate = self.recovery_estimator.estimate(scenario)
            estimate['failure_mode'] = mode['mode']
            estimate['severity'] = mode['severity']
            
            estimates.append(estimate)
        
        return estimates
    
    def _calculate_resilience_score(self, failure_modes: List[Dict],
                                    redundancy: Dict, stress_test: Dict) -> float:
        """Calculate overall resilience score"""
        score = 1.0
        
        # Penalize for failure modes
        for mode in failure_modes:
            if mode['severity'] == 'critical':
                score -= 0.2
            elif mode['severity'] == 'high':
                score -= 0.15
            elif mode['severity'] == 'medium':
                score -= 0.1
        
        # Bonus for redundancy
        score += redundancy['overall_score'] * 0.3
        
        # Add stress test resilience
        score += stress_test['overall_resilience'] * 0.4
        
        return max(0.0, min(1.0, score))
    
    def _get_grade(self, score: float) -> str:
        """Get grade"""
        if score >= 0.9:
            return 'A+ (Excellent)'
        elif score >= 0.8:
            return 'A (Very Good)'
        elif score >= 0.7:
            return 'B (Good)'
        elif score >= 0.6:
            return 'C (Adequate)'
        elif score >= 0.5:
            return 'D (Poor)'
        else:
            return 'F (Critical)'
    
    def _generate_recommendations(self, failure_modes: List[Dict],
                                  redundancy: Dict, stress_test: Dict) -> List[Dict]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # From failure modes
        for mode in failure_modes[:3]:
            recommendations.append({
                'priority': 'high' if mode['severity'] in ['critical', 'high'] else 'medium',
                'category': 'failure_prevention',
                'issue': mode['description'],
                'action': mode['mitigation'][0],
                'impact': f"Reduce {mode['mode']} risk",
            })
        
        # From redundancy
        if redundancy['overall_level'] in ['poor', 'critical']:
            recommendations.append({
                'priority': 'high',
                'category': 'redundancy',
                'issue': f"Overall redundancy: {redundancy['overall_level']}",
                'action': 'Add redundancy to critical components',
                'impact': 'Improve fault tolerance',
            })
        
        # From stress test
        weakest = stress_test['weakest_link']
        if weakest:
            recommendations.append({
                'priority': 'high',
                'category': 'stress_resilience',
                'issue': f"Weakest scenario: {weakest}",
                'action': f"Improve resilience against {weakest}",
                'impact': f"Improve {stress_test['resilience_grade']} grade",
            })
        
        return recommendations
    
    def print_report(self, result: Dict):
        """Print resilience report"""
        print("\n" + "=" * 60)
        print("🛡️  RESILIENCE ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n📊 RESILIENCE SCORE: {result['resilience_score']:.1%}")
        print(f"Grade: {result['resilience_grade']}")
        
        # Failure modes
        print(f"\n⚠️  FAILURE MODES ({len(result['failure_modes'])}):")
        for mode in result['failure_modes'][:3]:
            print(f"   [{mode['severity'].upper()}] {mode['mode']}")
            print(f"      {mode['description']}")
        
        # Redundancy
        redundancy = result['redundancy']
        print(f"\n🔄 REDUNDANCY: {redundancy['overall_level']} ({redundancy['overall_score']:.1%})")
        print(f"   Redundant components: {redundancy['redundant_count']}/{redundancy['total_components']}")
        
        # Stress test
        stress = result['stress_test']
        print(f"\n💥 STRESS TEST: Grade {stress['resilience_grade']}")
        print(f"   Weakest link: {stress['weakest_link']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS ({len(result['recommendations'])}):")
        for rec in result['recommendations'][:3]:
            print(f"   [{rec['priority'].upper()}] {rec['action']}")
            print(f"      Impact: {rec['impact']}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Resilience Analyzer")
    parser.add_argument('--analyze', action='store_true', help='Demo analysis')
    parser.add_argument('--config', type=str, help='System config file')
    args = parser.parse_args()
    
    analyzer = ResilienceAnalyzer()
    
    if args.analyze:
        # Demo system config
        demo_config = {
            'components': [
                {'name': 'web_server', 'instances': 2, 'backup': True, 'failover': True},
                {'name': 'database', 'instances': 1, 'backup': True, 'failover': False},
                {'name': 'cache', 'instances': 3, 'backup': False, 'failover': True},
            ],
            'dependencies': [
                {'name': 'payment_api', 'external': True, 'fallback': False},
                {'name': 'email_service', 'external': True, 'fallback': True},
            ],
            'autoscaling': True,
            'rate_limiting': False,
            'monitoring': True,
            'circuit_breaker': False,
        }
        
        result = analyzer.analyze(demo_config)
        analyzer.print_report(result)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
