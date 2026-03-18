#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
System Health Checker - Phase 4 Iteration
Comprehensive system health monitoring
Features: tool health, resource status, error detection, recommendations

Usage:
    python system_health_checker.py --check
    python system_health_checker.py --report
    python system_health_checker.py --quick
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "30-scripts-tools"
REPORTS_DIR = WORKSPACE / "20-data-reports" / "health"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SystemHealthChecker:
    """Comprehensive system health monitoring"""
    
    def __init__(self):
        self.health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {}
        }
    
    def check_tools(self) -> Dict:
        """Check tool health"""
        print("[CHECK] Scanning tools...")
        
        py_files = list(TOOLS_DIR.glob("*.py"))
        
        results = {
            'total': len(py_files),
            'healthy': 0,
            'warnings': 0,
            'errors': 0,
            'details': []
        }
        
        for py_file in py_files[:30]:  # Check first 30
            tool_result = self._check_single_tool(py_file)
            results['details'].append(tool_result)
            
            if tool_result['status'] == 'ok':
                results['healthy'] += 1
            elif tool_result['status'] == 'warning':
                results['warnings'] += 1
            else:
                results['errors'] += 1
        
        return results
    
    def _check_single_tool(self, tool_path: Path) -> Dict:
        """Check a single tool"""
        result = {
            'name': tool_path.name,
            'status': 'unknown',
            'response_time_ms': 0
        }
        
        try:
            start = datetime.now()
            
            # Try --help
            process = subprocess.run(
                ['python', str(tool_path), '--help'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(WORKSPACE)
            )
            
            end = datetime.now()
            result['response_time_ms'] = (end - start).total_seconds() * 1000
            
            if process.returncode in [0, 1]:
                result['status'] = 'ok'
            else:
                result['status'] = 'warning'
                result['message'] = process.stderr[:100]
        
        except subprocess.TimeoutExpired:
            result['status'] = 'error'
            result['message'] = 'Timeout'
        
        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)[:100]
        
        return result
    
    def check_git(self) -> Dict:
        """Check Git status"""
        print("[CHECK] Checking Git...")
        
        result = {
            'status': 'unknown',
            'branch': 'unknown',
            'commits_behind': 0,
            'uncommitted_changes': 0
        }
        
        try:
            # Get current branch
            process = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(WORKSPACE)
            )
            result['branch'] = process.stdout.strip()
            
            # Get uncommitted changes
            process = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(WORKSPACE)
            )
            
            changes = [line for line in process.stdout.strip().split('\n') if line]
            result['uncommitted_changes'] = len(changes)
            
            if result['uncommitted_changes'] == 0:
                result['status'] = 'ok'
            else:
                result['status'] = 'warning'
        
        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)[:100]
        
        return result
    
    def check_disk(self) -> Dict:
        """Check disk space"""
        print("[CHECK] Checking disk...")
        
        result = {
            'status': 'unknown',
            'total_gb': 0,
            'used_gb': 0,
            'free_gb': 0,
            'percent_used': 0
        }
        
        try:
            import psutil
            disk = psutil.disk_usage(str(WORKSPACE))
            
            result['total_gb'] = round(disk.total / (1024**3), 2)
            result['used_gb'] = round(disk.used / (1024**3), 2)
            result['free_gb'] = round(disk.free / (1024**3), 2)
            result['percent_used'] = round(disk.percent, 1)
            
            if disk.percent < 70:
                result['status'] = 'ok'
            elif disk.percent < 90:
                result['status'] = 'warning'
            else:
                result['status'] = 'critical'
        
        except ImportError:
            result['status'] = 'warning'
            result['message'] = 'psutil not installed'
        
        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)[:100]
        
        return result
    
    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        print("\n" + "=" * 60)
        print("System Health Check")
        print("=" * 60)
        
        # Run checks
        self.health['checks']['tools'] = self.check_tools()
        self.health['checks']['git'] = self.check_git()
        self.health['checks']['disk'] = self.check_disk()
        self.health['timestamp'] = datetime.now().isoformat()
        
        # Calculate overall status
        self._calculate_overall_status()
        
        # Print summary
        self._print_summary()
        
        # Save report
        self._save_report()
        
        return self.health
    
    def _calculate_overall_status(self):
        """Calculate overall health status"""
        statuses = []
        
        for check_name, check_result in self.health['checks'].items():
            status = check_result.get('status', 'unknown')
            statuses.append(status)
        
        if 'critical' in statuses:
            self.health['overall_status'] = 'critical'
        elif 'error' in statuses:
            self.health['overall_status'] = 'error'
        elif 'warning' in statuses:
            self.health['overall_status'] = 'warning'
        else:
            self.health['overall_status'] = 'ok'
    
    def _print_summary(self):
        """Print health summary"""
        print("\n" + "=" * 60)
        print("Health Summary")
        print("=" * 60)
        
        # Overall status
        status = self.health['overall_status']
        icon = "✅" if status == 'ok' else "⚠️" if status == 'warning' else "❌"
        print(f"\nOverall Status: {icon} {status.upper()}")
        
        # Tool health
        tools = self.health['checks'].get('tools', {})
        print(f"\nTools:")
        print(f"  Total:   {tools.get('total', 0)}")
        print(f"  Healthy: {tools.get('healthy', 0)}")
        print(f"  Warnings:{tools.get('warnings', 0)}")
        print(f"  Errors:  {tools.get('errors', 0)}")
        
        # Git status
        git = self.health['checks'].get('git', {})
        print(f"\nGit:")
        print(f"  Branch:  {git.get('branch', 'unknown')}")
        print(f"  Changes: {git.get('uncommitted_changes', 0)} uncommitted")
        
        # Disk status
        disk = self.health['checks'].get('disk', {})
        print(f"\nDisk:")
        print(f"  Used:    {disk.get('percent_used', 0)}%")
        print(f"  Free:    {disk.get('free_gb', 0)} GB")
        
        print("\n" + "=" * 60)
    
    def _save_report(self):
        """Save health report"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        report_file = REPORTS_DIR / f"health-report-{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.health, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Report saved to {report_file}")
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on health check"""
        recommendations = []
        
        # Tool recommendations
        tools = self.health['checks'].get('tools', {})
        if tools.get('errors', 0) > 0:
            recommendations.append(f"Fix {tools['errors']} tool(s) with errors")
        if tools.get('warnings', 0) > 5:
            recommendations.append(f"Review {tools['warnings']} tool(s) with warnings")
        
        # Git recommendations
        git = self.health['checks'].get('git', {})
        if git.get('uncommitted_changes', 0) > 0:
            recommendations.append(f"Commit {git['uncommitted_changes']} uncommitted change(s)")
        
        # Disk recommendations
        disk = self.health['checks'].get('disk', {})
        if disk.get('percent_used', 0) > 80:
            recommendations.append("Clean up disk space - usage above 80%")
        if disk.get('percent_used', 0) > 90:
            recommendations.append("URGENT: Disk space critical - free up space now")
        
        if not recommendations:
            recommendations.append("✅ System healthy - no action needed")
        
        return recommendations


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='System Health Checker')
    parser.add_argument('--check', action='store_true', help='Run all checks')
    parser.add_argument('--quick', action='store_true', help='Quick health check')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()
    
    checker = SystemHealthChecker()
    
    if args.check or args.quick:
        checker.run_all_checks()
        
        # Show recommendations
        recs = checker.generate_recommendations()
        print(f"\nRecommendations ({len(recs)}):")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec}")
    
    if args.report:
        print("[REPORT] Report generation not yet implemented")
        print("  Use --check instead")
    
    if not any([args.check, args.quick, args.report]):
        parser.print_help()


if __name__ == "__main__":
    main()
