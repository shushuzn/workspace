#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource Monitor - Phase 4 Innovation
Monitors system resource usage and optimizes allocation
Features: CPU/Memory/Disk tracking, bottleneck detection, auto-scaling suggestions

Usage:
    python resource_monitor.py --monitor
    python resource_monitor.py --report
    python resource_monitor.py --optimize
    python resource_monitor.py --history
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports" / "resource-monitor"
HISTORY_FILE = DATA_DIR / "resource-history.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ResourceMonitor:
    """Monitor and optimize system resources"""
    
    def __init__(self):
        self.history = self._load_history()
        self.samples = []
    
    def _load_history(self) -> Dict:
        """Load resource usage history"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"samples": [], "alerts": []}
    
    def _save_history(self):
        """Save resource history"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # Fallback: use Windows command
            import subprocess
            try:
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'loadpercentage'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip().isdigit():
                        return float(line.strip())
            except:
                pass
            return 0.0
    
    def get_memory_usage(self) -> Dict:
        """Get memory usage statistics"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                'total_mb': round(mem.total / (1024 * 1024), 2),
                'used_mb': round(mem.used / (1024 * 1024), 2),
                'available_mb': round(mem.available / (1024 * 1024), 2),
                'percent': mem.percent
            }
        except ImportError:
            # Fallback
            return {'total_mb': 0, 'used_mb': 0, 'available_mb': 0, 'percent': 0}
    
    def get_disk_usage(self, path: str = "D:") -> Dict:
        """Get disk usage statistics"""
        try:
            import psutil
            disk = psutil.disk_usage(path)
            return {
                'total_gb': round(disk.total / (1024 * 1024 * 1024), 2),
                'used_gb': round(disk.used / (1024 * 1024 * 1024), 2),
                'free_gb': round(disk.free / (1024 * 1024 * 1024), 2),
                'percent': disk.percent
            }
        except ImportError:
            # Fallback: use Windows command
            import subprocess
            try:
                result = subprocess.run(
                    ['wmic', 'logicaldisk', 'where', f'DeviceID="{path}"', 'get', 'Size,FreeSpace'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 2 and parts[0].isdigit():
                        free = int(parts[0]) / (1024 * 1024 * 1024)
                        total = int(parts[1]) / (1024 * 1024 * 1024)
                        used = total - free
                        return {
                            'total_gb': round(total, 2),
                            'used_gb': round(used, 2),
                            'free_gb': round(free, 2),
                            'percent': round(used / total * 100, 1) if total > 0 else 0
                        }
            except:
                pass
            return {'total_gb': 0, 'used_gb': 0, 'free_gb': 0, 'percent': 0}
    
    def get_process_count(self) -> int:
        """Get number of running Python processes"""
        try:
            import psutil
            python_processes = [p for p in psutil.process_iter(['name']) 
                               if 'python' in p.info['name'].lower()]
            return len(python_processes)
        except:
            return 0
    
    def sample_resources(self) -> Dict:
        """Sample current resource usage"""
        sample = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage("D:"),
            'python_processes': self.get_process_count()
        }
        
        self.samples.append(sample)
        
        # Check for alerts
        self._check_alerts(sample)
        
        return sample
    
    def _check_alerts(self, sample: Dict):
        """Check for resource alerts"""
        alerts = []
        
        # CPU alert
        if sample['cpu_percent'] > 80:
            alerts.append({
                'type': 'high_cpu',
                'severity': 'warning' if sample['cpu_percent'] < 95 else 'critical',
                'value': sample['cpu_percent'],
                'threshold': 80
            })
        
        # Memory alert
        if sample['memory'].get('percent', 0) > 80:
            alerts.append({
                'type': 'high_memory',
                'severity': 'warning' if sample['memory']['percent'] < 95 else 'critical',
                'value': sample['memory']['percent'],
                'threshold': 80
            })
        
        # Disk alert
        if sample['disk'].get('percent', 0) > 90:
            alerts.append({
                'type': 'low_disk',
                'severity': 'critical',
                'value': sample['disk']['percent'],
                'threshold': 90
            })
        
        # Add alerts to history
        for alert in alerts:
            alert['timestamp'] = sample['timestamp']
            self.history['alerts'].append(alert)
        
        # Keep only last 1000 alerts
        self.history['alerts'] = self.history['alerts'][-1000:]
    
    def monitor(self, duration_minutes: int = 5, interval_seconds: int = 10):
        """Monitor resources for specified duration"""
        print(f"[MONITOR] Monitoring for {duration_minutes} minutes...")
        print(f"  Interval: {interval_seconds} seconds")
        print()
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            sample = self.sample_resources()
            
            # Print current status
            print(f"[{sample['timestamp'][11:19]}] "
                  f"CPU: {sample['cpu_percent']:5.1f}% | "
                  f"MEM: {sample['memory']['percent']:5.1f}% | "
                  f"DISK: {sample['disk']['percent']:5.1f}% | "
                  f"PY: {sample['python_processes']}")
            
            # Save to history
            self.history['samples'].append(sample)
            
            # Keep only last 10000 samples
            self.history['samples'] = self.history['samples'][-10000:]
            self._save_history()
            
            time.sleep(interval_seconds)
        
        print(f"\n[OK] Monitoring complete. {len(self.samples)} samples collected.")
    
    def generate_report(self) -> str:
        """Generate resource usage report"""
        print("[REPORT] Generating resource report...")
        
        if not self.history.get('samples'):
            return "No resource data available"
        
        samples = self.history['samples'][-1000:]  # Last 1000 samples
        
        # Calculate statistics
        cpu_values = [s['cpu_percent'] for s in samples]
        mem_values = [s['memory']['percent'] for s in samples]
        disk_values = [s['disk']['percent'] for s in samples]
        
        report = f"""# Resource Usage Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Samples Analyzed:** {len(samples)}

---

## Summary Statistics

| Resource | Average | Min | Max | Current |
|----------|---------|-----|-----|---------|
| CPU | {sum(cpu_values)/len(cpu_values):.1f}% | {min(cpu_values):.1f}% | {max(cpu_values):.1f}% | {cpu_values[-1]:.1f}% |
| Memory | {sum(mem_values)/len(mem_values):.1f}% | {min(mem_values):.1f}% | {max(mem_values):.1f}% | {mem_values[-1]:.1f}% |
| Disk | {sum(disk_values)/len(disk_values):.1f}% | {min(disk_values):.1f}% | {max(disk_values):.1f}% | {disk_values[-1]:.1f}% |

---

## Alerts

"""
        
        # Alert summary
        alerts = self.history.get('alerts', [])[-100:]
        alert_counts = {}
        for alert in alerts:
            atype = alert.get('type', 'unknown')
            alert_counts[atype] = alert_counts.get(atype, 0) + 1
        
        if alert_counts:
            report += "| Alert Type | Count | Severity |\n"
            report += "|------------|-------|----------|\n"
            for atype, count in alert_counts.items():
                severity = alerts[-1].get('severity', 'unknown') if atype in alerts[-1].get('type', '') else 'unknown'
                report += f"| {atype} | {count} | {severity} |\n"
        else:
            report += "No alerts in recent history.\n"
        
        report += f"""
---

## Optimization Suggestions

"""
        
        # Generate suggestions
        suggestions = []
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        if avg_cpu > 70:
            suggestions.append("- **High average CPU usage** - Consider reducing concurrent tasks or optimizing CPU-intensive operations")
        
        avg_mem = sum(mem_values) / len(mem_values)
        if avg_mem > 70:
            suggestions.append("- **High memory usage** - Review memory-intensive processes, consider increasing RAM or optimizing data structures")
        
        avg_disk = sum(disk_values) / len(disk_values)
        if avg_disk > 80:
            suggestions.append("- **Low disk space** - Clean up temporary files, old logs, and unnecessary data")
        
        if not suggestions:
            suggestions.append("- ✅ Resource usage is healthy - no optimization needed")
        
        report += "\n".join(suggestions)
        
        # Save report
        report_path = DATA_DIR / f"resource-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"[OK] Saved to {report_path}")
        
        return report
    
    def show_history(self, hours: int = 24):
        """Show resource usage history"""
        print("\n" + "=" * 60)
        print(f"Resource Usage History (Last {hours}h)")
        print("=" * 60)
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_samples = [
            s for s in self.history.get('samples', [])
            if datetime.fromisoformat(s['timestamp']) > cutoff
        ]
        
        if not recent_samples:
            print("[INFO] No recent data available")
            return
        
        # Sample at hourly intervals
        print(f"\n{'Time':<12} {'CPU':<8} {'Memory':<8} {'Disk':<8} {'Processes'}")
        print("-" * 50)
        
        for i, sample in enumerate(recent_samples):
            if i % max(1, len(recent_samples) // 24) == 0:  # Show ~24 samples
                time_str = sample['timestamp'][11:16]
                cpu = sample['cpu_percent']
                mem = sample['memory']['percent']
                disk = sample['disk']['percent']
                procs = sample.get('python_processes', 0)
                
                print(f"{time_str:<12} {cpu:>6.1f}% {mem:>6.1f}% {disk:>6.1f}% {procs:>8}")
        
        print("=" * 60)
    
    def optimize(self) -> List[str]:
        """Generate optimization suggestions"""
        print("[OPTIMIZE] Analyzing resource usage...")
        
        suggestions = []
        
        # Analyze history
        samples = self.history.get('samples', [])[-100:]
        
        if not samples:
            # Take fresh sample
            sample = self.sample_resources()
            samples = [sample]
        
        # CPU optimization
        avg_cpu = sum(s['cpu_percent'] for s in samples) / len(samples)
        if avg_cpu > 60:
            suggestions.append(f"Reduce concurrent tasks (avg CPU: {avg_cpu:.1f}%)")
            suggestions.append("Consider implementing task queuing")
        
        # Memory optimization
        avg_mem = sum(s['memory']['percent'] for s in samples) / len(samples)
        if avg_mem > 60:
            suggestions.append(f"Optimize memory usage (avg: {avg_mem:.1f}%)")
            suggestions.append("Implement data streaming instead of loading all at once")
            suggestions.append("Add garbage collection calls after large operations")
        
        # Disk optimization
        latest_disk = samples[-1]['disk']['percent']
        if latest_disk > 70:
            suggestions.append(f"Clean up disk space (used: {latest_disk:.1f}%)")
            suggestions.append("Remove old log files and temporary data")
            suggestions.append("Archive old data to external storage")
        
        # Process optimization
        avg_procs = sum(s.get('python_processes', 0) for s in samples) / len(samples)
        if avg_procs > 10:
            suggestions.append(f"Reduce Python processes (avg: {avg_procs:.0f})")
            suggestions.append("Consolidate scripts where possible")
        
        if not suggestions:
            suggestions.append("✅ Resource usage is optimal - no changes needed")
        
        print(f"\nOptimization Suggestions ({len(suggestions)}):")
        for i, sug in enumerate(suggestions, 1):
            print(f"  {i}. {sug}")
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(description='Resource Monitor')
    parser.add_argument('--monitor', action='store_true', help='Monitor resources')
    parser.add_argument('--duration', type=int, default=5, help='Monitor duration (minutes)')
    parser.add_argument('--interval', type=int, default=10, help='Sample interval (seconds)')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--history', type=int, nargs='?', default=24, help='Show history (hours)')
    parser.add_argument('--optimize', action='store_true', help='Show optimization suggestions')
    args = parser.parse_args()
    
    monitor = ResourceMonitor()
    
    if args.monitor:
        monitor.monitor(args.duration, args.interval)
    
    if args.report:
        report = monitor.generate_report()
        print(report[:2000])
    
    if args.history:
        monitor.show_history(args.history)
    
    if args.optimize:
        monitor.optimize()
    
    if not any([args.monitor, args.report, args.history, args.optimize]):
        parser.print_help()


if __name__ == "__main__":
    main()
