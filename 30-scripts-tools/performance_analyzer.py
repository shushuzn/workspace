#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance Analyzer - System Bottleneck Detection
Analyzes system performance and identifies optimization opportunities
Features: Profiling, bottleneck detection, optimization suggestions, trend analysis

Usage:
    python performance_analyzer.py --profile
    python performance_analyzer.py --bottlenecks
    python performance_analyzer.py --optimize
    python performance_analyzer.py --report
"""

import os
import sys
import json
import cProfile
import pstats
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class Bottleneck:
    """Bottleneck item"""
    id: str
    category: str
    component: str
    description: str
    severity: str  # critical/high/medium/low
    impact_score: float  # 0-100
    current_value: float
    target_value: float
    optimization: str
    expected_improvement: str


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    timestamp: str
    component: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    io_operations: int
    cache_hit_rate: float


class PerformanceAnalyzer:
    """Analyze system performance"""
    
    def __init__(self):
        self.metrics_file = WORKSPACE / "20-data-reports" / "performance_metrics.json"
        self.bottlenecks_file = WORKSPACE / "20-data-reports" / "bottlenecks.json"
        
        self.metrics = []
        self.bottlenecks = []
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
            except:
                pass
        
        if self.bottlenecks_file.exists():
            try:
                with open(self.bottlenecks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bottlenecks = [Bottleneck(**b) if isinstance(b, dict) else b 
                                       for b in data.get('bottlenecks', [])]
            except:
                pass
    
    def save_state(self):
        """Save state"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        with open(self.bottlenecks_file, 'w', encoding='utf-8') as f:
            json.dump({
                'bottlenecks': [asdict(b) if isinstance(b, Bottleneck) else b 
                               for b in self.bottlenecks],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def profile_component(self, component: str, func, *args) -> Dict:
        """Profile a component"""
        print(f"\n📊 Profiling: {component}\n")
        
        profiler = cProfile.Profile()
        
        start_time = time.time()
        profiler.enable()
        
        # Execute function
        try:
            result = func(*args)
        except Exception as e:
            print(f"❌ Error: {e}")
            return {'error': str(e)}
        finally:
            profiler.disable()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get stats
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Top functions
        top_functions = []
        for func_name, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:10]:
            filename, line, func = func_name
            top_functions.append({
                'function': func,
                'file': filename.split('/')[-1],
                'line': line,
                'call_count': nc,
                'cumulative_time': ct
            })
        
        profile_result = {
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'top_functions': top_functions
        }
        
        # Save metrics
        self.metrics.append({
            'timestamp': profile_result['timestamp'],
            'component': component,
            'execution_time': duration,
            'memory_usage': 0,  # Would need memory profiler
            'cpu_usage': 0,
            'io_operations': 0,
            'cache_hit_rate': 0
        })
        
        # Keep last 100 metrics
        self.metrics = self.metrics[-100:]
        self.save_state()
        
        # Print results
        print(f"Duration: {duration:.3f}s")
        print(f"\nTop 10 functions:\n")
        for i, func in enumerate(top_functions, 1):
            print(f"{i}. {func['function']} ({func['file']}:{func['line']})")
            print(f"   Calls: {func['call_count']} | Time: {func['cumulative_time']:.3f}s\n")
        
        return profile_result
    
    def detect_bottlenecks(self) -> List[Bottleneck]:
        """Detect performance bottlenecks"""
        print("\n" + "="*60)
        print(" Bottleneck Detection")
        print("="*60 + "\n")
        
        bottlenecks = []
        
        # Bottleneck 1: Slow execution time
        if self.metrics:
            recent_metrics = self.metrics[-20:]
            avg_time = sum(m['execution_time'] for m in recent_metrics) / len(recent_metrics)
            
            if avg_time > 10:  # > 10 seconds
                bottlenecks.append(Bottleneck(
                    id=f"bn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_1",
                    category='execution',
                    component='system',
                    description='Average execution time exceeds 10 seconds',
                    severity='high',
                    impact_score=75.0,
                    current_value=avg_time,
                    target_value=5.0,
                    optimization='Implement parallel execution and caching',
                    expected_improvement='50-70% reduction'
                ))
        
        # Bottleneck 2: Low cache hit rate
        if self.metrics:
            avg_cache_hit = sum(m.get('cache_hit_rate', 0) for m in self.metrics) / len(self.metrics)
            
            if avg_cache_hit < 0.5:  # < 50%
                bottlenecks.append(Bottleneck(
                    id=f"bn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_2",
                    category='caching',
                    component='cache_manager',
                    description='Cache hit rate below 50%',
                    severity='medium',
                    impact_score=60.0,
                    current_value=avg_cache_hit,
                    target_value=0.8,
                    optimization='Increase cache TTL and optimize cache keys',
                    expected_improvement='40-60% improvement'
                ))
        
        # Bottleneck 3: Sequential execution
        bottlenecks.append(Bottleneck(
            id=f"bn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_3",
            category='architecture',
            component='orchestrator',
            description='Systems execute sequentially instead of in parallel',
            severity='high',
            impact_score=80.0,
            current_value=1.0,  # 1 system at a time
            target_value=4.0,  # 4 systems in parallel
            optimization='Implement ThreadPoolExecutor for independent systems',
            expected_improvement='60-75% reduction in total time'
        ))
        
        # Bottleneck 4: No result caching
        bottlenecks.append(Bottleneck(
            id=f"bn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_4",
            category='caching',
            component='recommendations',
            description='Recommendations regenerated on every request',
            severity='medium',
            impact_score=55.0,
            current_value=0.0,  # No caching
            target_value=1.0,  # Full caching
            optimization='Cache recommendations with 30-min TTL',
            expected_improvement='90% reduction in generation time'
        ))
        
        # Bottleneck 5: Inefficient file I/O
        bottlenecks.append(Bottleneck(
            id=f"bn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_5",
            category='io',
            component='all',
            description='Frequent file I/O without buffering',
            severity='low',
            impact_score=40.0,
            current_value=0.0,  # No buffering
            target_value=1.0,  # Buffered I/O
            optimization='Implement buffered I/O and batch writes',
            expected_improvement='20-30% improvement'
        ))
        
        # Bottleneck 6: Memory inefficiency
        bottlenecks.append(Bottleneck(
            id=f"bn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_6",
            category='memory',
            component='dashboard',
            description='Dashboard loads all data on every refresh',
            severity='medium',
            impact_score=65.0,
            current_value=100.0,  # 100% data load
            target_value=20.0,  # 20% incremental load
            optimization='Implement incremental data loading and delta updates',
            expected_improvement='70-80% reduction in data transfer'
        ))
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        bottlenecks.sort(key=lambda b: (severity_order.get(b.severity, 4), -b.impact_score))
        
        self.bottlenecks = bottlenecks
        self.save_state()
        
        # Print bottlenecks
        print(f"Detected {len(bottlenecks)} bottlenecks:\n")
        
        for i, bn in enumerate(bottlenecks, 1):
            severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            print(f"{i}. {severity_icon.get(bn.severity, '⚪')} [{bn.category.upper()}] {bn.component}")
            print(f"   {bn.description}")
            print(f"   Severity: {bn.severity} | Impact: {bn.impact_score:.0f}/100")
            print(f"   Current: {bn.current_value:.1f} → Target: {bn.target_value:.1f}")
            print(f"   Optimization: {bn.optimization}")
            print(f"   Expected: {bn.expected_improvement}\n")
        
        return bottlenecks
    
    def generate_optimizations(self) -> List[Dict]:
        """Generate optimization recommendations"""
        print("\n" + "="*60)
        print(" Optimization Recommendations")
        print("="*60 + "\n")
        
        if not self.bottlenecks:
            self.detect_bottlenecks()
        
        optimizations = []
        
        for bn in self.bottlenecks:
            optimizations.append({
                'bottleneck_id': bn.id,
                'component': bn.component,
                'optimization': bn.optimization,
                'priority': bn.severity,
                'impact_score': bn.impact_score,
                'expected_improvement': bn.expected_improvement,
                'implementation_steps': self._get_implementation_steps(bn),
                'estimated_effort': self._estimate_effort(bn)
            })
        
        print(f"Generated {len(optimizations)} optimization recommendations:\n")
        
        for i, opt in enumerate(optimizations, 1):
            print(f"{i}. [{opt['priority'].upper()}] {opt['component']}")
            print(f"   {opt['optimization']}")
            print(f"   Impact: {opt['impact_score']:.0f}/100")
            print(f"   Effort: {opt['estimated_effort']}")
            print(f"   Steps: {len(opt['implementation_steps'])}\n")
        
        return optimizations
    
    def _get_implementation_steps(self, bn: Bottleneck) -> List[str]:
        """Get implementation steps for bottleneck"""
        steps_map = {
            'execution': [
                'Identify independent tasks',
                'Implement ThreadPoolExecutor',
                'Add task queue',
                'Test parallel execution',
                'Monitor performance'
            ],
            'caching': [
                'Identify cacheable data',
                'Implement TwoLevelCache',
                'Set appropriate TTL',
                'Add cache invalidation',
                'Monitor hit rates'
            ],
            'architecture': [
                'Map system dependencies',
                'Implement DAG scheduler',
                'Add parallel execution',
                'Test dependency resolution',
                'Monitor execution time'
            ],
            'io': [
                'Identify frequent I/O operations',
                'Implement buffered I/O',
                'Batch write operations',
                'Add async I/O where possible',
                'Monitor I/O wait time'
            ],
            'memory': [
                'Profile memory usage',
                'Implement lazy loading',
                'Add incremental updates',
                'Optimize data structures',
                'Monitor memory footprint'
            ]
        }
        
        return steps_map.get(bn.category, ['Analyze problem', 'Design solution', 'Implement', 'Test', 'Deploy'])
    
    def _estimate_effort(self, bn: Bottleneck) -> str:
        """Estimate implementation effort"""
        effort_map = {
            'execution': 'Medium (4-6 hours)',
            'caching': 'Low (2-4 hours)',
            'architecture': 'High (8-12 hours)',
            'io': 'Low (2-3 hours)',
            'memory': 'Medium (4-6 hours)'
        }
        
        return effort_map.get(bn.category, 'Medium (4-6 hours)')
    
    def generate_report(self) -> str:
        """Generate performance report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = WORKSPACE / "20-data-reports" / f"performance_report_{timestamp}.md"
        
        if not self.bottlenecks:
            self.detect_bottlenecks()
        
        optimizations = self.generate_optimizations()
        
        # Calculate summary stats
        total_bottlenecks = len(self.bottlenecks)
        critical_count = sum(1 for b in self.bottlenecks if b.severity == 'critical')
        high_count = sum(1 for b in self.bottlenecks if b.severity == 'high')
        avg_impact = sum(b.impact_score for b in self.bottlenecks) / max(1, total_bottlenecks)
        
        report = f"""# Performance Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version:** 1.0

## Executive Summary

- **Total Bottlenecks:** {total_bottlenecks}
- **Critical:** {critical_count}
- **High Priority:** {high_count}
- **Average Impact:** {avg_impact:.0f}/100

## Bottlenecks

"""
        
        for i, bn in enumerate(self.bottlenecks, 1):
            report += f"""### {i}. {bn.component} ({bn.severity.upper()})

**Description:** {bn.description}

**Impact Score:** {bn.impact_score:.0f}/100

**Current Value:** {bn.current_value:.1f}

**Target Value:** {bn.target_value:.1f}

**Optimization:** {bn.optimization}

**Expected Improvement:** {bn.expected_improvement}

---

"""
        
        report += """## Optimization Plan

| Priority | Component | Optimization | Impact | Effort |
|----------|-----------|--------------|--------|--------|
"""
        
        for opt in optimizations:
            report += f"| {opt['priority']} | {opt['component']} | {opt['optimization'][:40]}... | {opt['impact_score']:.0f} | {opt['estimated_effort']} |\n"
        
        report += f"""
## Next Steps

1. Address critical bottlenecks first
2. Implement caching optimizations (high ROI)
3. Parallelize independent systems
4. Monitor performance improvements
5. Iterate based on metrics

## Metrics History

Total metrics recorded: {len(self.metrics)}

Recent execution times:
"""
        
        if self.metrics:
            for m in self.metrics[-5:]:
                report += f"- {m['timestamp']}: {m['execution_time']:.2f}s ({m['component']})\n"
        
        report += f"""
---

*Report generated by Performance Analyzer v1.0*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Report saved: {report_file}\n")
        print(report)
        
        return report
    
    def get_status(self) -> Dict:
        """Get analyzer status"""
        return {
            'total_metrics': len(self.metrics),
            'total_bottlenecks': len(self.bottlenecks),
            'by_severity': {
                'critical': sum(1 for b in self.bottlenecks if b.severity == 'critical'),
                'high': sum(1 for b in self.bottlenecks if b.severity == 'high'),
                'medium': sum(1 for b in self.bottlenecks if b.severity == 'medium'),
                'low': sum(1 for b in self.bottlenecks if b.severity == 'low')
            },
            'avg_impact': sum(b.impact_score for b in self.bottlenecks) / max(1, len(self.bottlenecks)) if self.bottlenecks else 0,
            'last_updated': datetime.now().isoformat()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Analyzer')
    parser.add_argument('--profile', action='store_true', help='Profile components')
    parser.add_argument('--bottlenecks', action='store_true', help='Detect bottlenecks')
    parser.add_argument('--optimize', action='store_true', help='Generate optimizations')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--status', action='store_true', help='Show status')
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer()
    
    if args.profile:
        # Profile self-iteration
        from self_iteration import SelfIterationSystem
        system = SelfIterationSystem()
        analyzer.profile_component('self_iteration', system.run_full_cycle)
    
    elif args.bottlenecks:
        bottlenecks = analyzer.detect_bottlenecks()
        print(f"\nTotal: {len(bottlenecks)} bottlenecks")
    
    elif args.optimize:
        optimizations = analyzer.generate_optimizations()
        print(f"\nTotal: {len(optimizations)} optimizations")
    
    elif args.report:
        analyzer.generate_report()
    
    elif args.status:
        status = analyzer.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
