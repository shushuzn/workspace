#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Profiler - System performance analysis

Features:
- Execution time profiling
- Memory usage tracking
- CPU utilization monitoring
- I/O performance analysis
- Bottleneck identification
- Optimization recommendations
"""

import os
import sys
import json
import time
import psutil
import functools
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import defaultdict
import threading

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
PROFILER_DIR = WORKSPACE / 'data' / 'profiler'
PROFILER_DIR.mkdir(parents=True, exist_ok=True)

class ExecutionProfiler:
    """Profile execution time"""
    
    def __init__(self):
        self.profiles = defaultdict(list)
    
    def profile(self, func: Callable) -> Callable:
        """Decorator to profile function execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            
            duration = end - start
            self.profiles[func.__name__].append({
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'args': str(args)[:100],
                'kwargs': str(kwargs)[:100],
            })
            
            return result
        return wrapper
    
    def get_stats(self, func_name: str = None) -> Dict:
        """Get profiling statistics"""
        if func_name:
            profiles = self.profiles.get(func_name, [])
        else:
            profiles = []
            for p in self.profiles.values():
                profiles.extend(p)
        
        if not profiles:
            return {'status': 'no_data'}
        
        durations = [p['duration'] for p in profiles]
        
        return {
            'status': 'success',
            'calls': len(profiles),
            'total_time': sum(durations),
            'avg_time': sum(durations) / len(durations),
            'min_time': min(durations),
            'max_time': max(durations),
            'std_dev': (sum((d - sum(durations)/len(durations))**2 for d in durations) / max(1, len(durations)-1)) ** 0.5 if len(durations) > 1 else 0,
        }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get stats for all profiled functions"""
        return {
            name: self.get_stats(name)
            for name in self.profiles.keys()
        }


class MemoryTracker:
    """Track memory usage"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.snapshots = []
    
    def snapshot(self) -> Dict:
        """Take memory snapshot"""
        mem_info = self.process.memory_info()
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'rss_mb': mem_info.rss / 1024 / 1024,
            'vms_mb': mem_info.vms / 1024 / 1024,
            'percent': self.process.memory_percent(),
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        if not self.snapshots:
            self.snapshot()
        
        rss_values = [s['rss_mb'] for s in self.snapshots]
        
        return {
            'current': self.snapshot(),
            'avg_rss_mb': sum(rss_values) / len(rss_values),
            'max_rss_mb': max(rss_values),
            'min_rss_mb': min(rss_values),
            'snapshots': len(self.snapshots),
        }
    
    def clear(self):
        """Clear snapshots"""
        self.snapshots.clear()


class CPUMonitor:
    """Monitor CPU utilization"""
    
    def __init__(self):
        self.samples = []
        self._monitoring = False
        self._thread = None
    
    def sample(self) -> float:
        """Take CPU sample"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        self.samples.append({
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
        })
        
        return cpu_percent
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous monitoring"""
        self._monitoring = True
        
        def monitor():
            while self._monitoring:
                self.sample()
                time.sleep(interval)
        
        self._thread = threading.Thread(target=monitor, daemon=True)
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def get_stats(self) -> Dict:
        """Get CPU statistics"""
        if not self.samples:
            self.sample()
        
        cpu_values = [s['cpu_percent'] for s in self.samples]
        
        return {
            'current': cpu_values[-1] if cpu_values else 0,
            'avg': sum(cpu_values) / len(cpu_values),
            'max': max(cpu_values),
            'min': min(cpu_values),
            'samples': len(self.samples),
        }


class IOAnalyzer:
    """Analyze I/O performance"""
    
    def __init__(self):
        self.operations = []
    
    def log_operation(self, operation: str, path: str, duration: float, bytes_transferred: int = 0):
        """Log I/O operation"""
        self.operations.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'path': path,
            'duration': duration,
            'bytes': bytes_transferred,
            'throughput_mbps': (bytes_transferred / duration / 1024 / 1024) if duration > 0 else 0,
        })
    
    def get_stats(self) -> Dict:
        """Get I/O statistics"""
        if not self.operations:
            return {'status': 'no_data'}
        
        # Group by operation type
        by_type = defaultdict(list)
        for op in self.operations:
            by_type[op['operation']].append(op)
        
        stats = {
            'status': 'success',
            'total_operations': len(self.operations),
            'by_type': {},
        }
        
        for op_type, ops in by_type.items():
            durations = [o['duration'] for o in ops]
            bytes_total = sum(o['bytes'] for o in ops)
            
            stats['by_type'][op_type] = {
                'count': len(ops),
                'avg_duration': sum(durations) / len(durations),
                'total_bytes': bytes_total,
                'avg_throughput_mbps': sum(o['throughput_mbps'] for o in ops) / len(ops),
            }
        
        return stats


class PerformanceProfiler:
    """
    System performance analysis
    
    Features:
    - Execution time profiling
    - Memory usage tracking
    - CPU utilization monitoring
    - I/O performance analysis
    - Bottleneck identification
    - Optimization recommendations
    """
    
    def __init__(self):
        self.execution_profiler = ExecutionProfiler()
        self.memory_tracker = MemoryTracker()
        self.cpu_monitor = CPUMonitor()
        self.io_analyzer = IOAnalyzer()
        
        self.bottlenecks = []
    
    def profile_execution(self, func: Callable) -> Callable:
        """Profile function execution"""
        return self.execution_profiler.profile(func)
    
    def track_memory(self) -> Dict:
        """Track memory usage"""
        return self.memory_tracker.snapshot()
    
    def monitor_cpu(self, interval: float = 1.0):
        """Start CPU monitoring"""
        self.cpu_monitor.start_monitoring(interval)
    
    def log_io(self, operation: str, path: str, duration: float, bytes_transferred: int = 0):
        """Log I/O operation"""
        self.io_analyzer.log_operation(operation, path, duration, bytes_transferred)
    
    def identify_bottlenecks(self) -> List[Dict]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Check execution time
        exec_stats = self.execution_profiler.get_all_stats()
        for func_name, stats in exec_stats.items():
            if stats.get('status') == 'success':
                if stats['avg_time'] > 1.0:  # >1 second average
                    bottlenecks.append({
                        'type': 'slow_function',
                        'name': func_name,
                        'avg_time': stats['avg_time'],
                        'severity': 'high' if stats['avg_time'] > 5.0 else 'medium',
                        'recommendation': 'Optimize algorithm or add caching',
                    })
        
        # Check memory
        mem_stats = self.memory_tracker.get_stats()
        if mem_stats['current']['percent'] > 80:
            bottlenecks.append({
                'type': 'high_memory',
                'current_percent': mem_stats['current']['percent'],
                'severity': 'critical' if mem_stats['current']['percent'] > 90 else 'high',
                'recommendation': 'Reduce memory footprint or add pagination',
            })
        
        # Check CPU
        cpu_stats = self.cpu_monitor.get_stats()
        if cpu_stats['avg'] > 80:
            bottlenecks.append({
                'type': 'high_cpu',
                'avg_percent': cpu_stats['avg'],
                'severity': 'high',
                'recommendation': 'Optimize CPU-intensive operations or add parallelization',
            })
        
        # Check I/O
        io_stats = self.io_analyzer.get_stats()
        if io_stats.get('status') == 'success':
            for op_type, op_data in io_stats['by_type'].items():
                if op_data['avg_duration'] > 0.5:  # >500ms
                    bottlenecks.append({
                        'type': 'slow_io',
                        'operation': op_type,
                        'avg_duration': op_data['avg_duration'],
                        'severity': 'medium',
                        'recommendation': 'Add buffering or async I/O',
                    })
        
        self.bottlenecks = bottlenecks
        return bottlenecks
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate optimization recommendations"""
        if not self.bottlenecks:
            self.identify_bottlenecks()
        
        recommendations = []
        
        for bottleneck in self.bottlenecks:
            rec = {
                'issue': bottleneck['type'],
                'severity': bottleneck['severity'],
                'recommendation': bottleneck['recommendation'],
                'expected_improvement': '20-50%',
                'effort': 'medium',
            }
            recommendations.append(rec)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return recommendations
    
    def get_full_report(self) -> Dict:
        """Get full performance report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'execution': self.execution_profiler.get_all_stats(),
            'memory': self.memory_tracker.get_stats(),
            'cpu': self.cpu_monitor.get_stats(),
            'io': self.io_analyzer.get_stats(),
            'bottlenecks': self.bottlenecks,
            'recommendations': self.generate_recommendations(),
        }
    
    def save_report(self, report: Dict = None):
        """Save report to file"""
        if report is None:
            report = self.get_full_report()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = PROFILER_DIR / f'performance_report_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 Report saved: {report_file}")
    
    def print_summary(self):
        """Print summary to console"""
        report = self.get_full_report()
        
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE PROFILER REPORT")
        print("=" * 60)
        
        # Execution
        print(f"\n⚡ EXECUTION:")
        for func_name, stats in report['execution'].items():
            if stats.get('status') == 'success':
                print(f"   {func_name}: {stats['avg_time']*1000:.2f}ms avg ({stats['calls']} calls)")
        
        # Memory
        print(f"\n💾 MEMORY:")
        mem = report['memory']
        if mem.get('current'):
            print(f"   Current: {mem['current']['rss_mb']:.1f} MB ({mem['current']['percent']:.1f}%)")
            print(f"   Avg: {mem['avg_rss_mb']:.1f} MB")
        
        # CPU
        print(f"\n🔥 CPU:")
        cpu = report['cpu']
        print(f"   Current: {cpu['current']:.1f}%")
        print(f"   Avg: {cpu['avg']:.1f}% | Max: {cpu['max']:.1f}%")
        
        # Bottlenecks
        print(f"\n⚠️  BOTTLENECKS: {len(report['bottlenecks'])}")
        for bn in report['bottlenecks'][:5]:
            print(f"   [{bn['severity'].upper()}] {bn['type']}: {bn['recommendation']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS: {len(report['recommendations'])}")
        for rec in report['recommendations'][:3]:
            print(f"   [{rec['severity'].upper()}] {rec['recommendation']}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Performance Profiler")
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--profile', type=str, help='Profile a script')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--summary', action='store_true', help='Print summary')
    args = parser.parse_args()
    
    profiler = PerformanceProfiler()
    
    if args.demo:
        print("\n🔍 PERFORMANCE PROFILER DEMO")
        print("=" * 60)
        
        # Simulate some work
        @profiler.profile_execution
        def sample_work():
            time.sleep(0.5)
            return sum(range(1000000))
        
        print("\n⚡ Running sample work...")
        for i in range(3):
            sample_work()
        
        # Memory snapshot
        print("\n💾 Taking memory snapshots...")
        for i in range(3):
            profiler.track_memory()
            time.sleep(0.1)
        
        # CPU sample
        print("\n🔥 Sampling CPU...")
        profiler.cpu_monitor.sample()
        
        # Identify bottlenecks
        print("\n🔍 Identifying bottlenecks...")
        bottlenecks = profiler.identify_bottlenecks()
        
        # Print summary
        profiler.print_summary()
        
        print("\n✅ Demo complete!")
    
    elif args.report:
        report = profiler.get_full_report()
        profiler.save_report(report)
        print("✅ Report generated and saved")
    
    elif args.summary:
        profiler.print_summary()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
