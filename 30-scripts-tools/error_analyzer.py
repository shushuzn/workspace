#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Error Log Analyzer - Phase 4 Innovation
Automatically analyzes error logs and suggests fixes
Features: pattern detection, root cause analysis, auto-fix suggestions

Usage:
    python error_analyzer.py --analyze logs/
    python error_analyzer.py --scan
    python error_analyzer.py --report
    python error_analyzer.py --suggest
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter

# Workspace root
WORKSPACE = Path(__file__).parent.parent
LOGS_DIR = WORKSPACE / "20-data-reports" / "logs"
ANALYSIS_DIR = WORKSPACE / "20-data-reports" / "error-analysis"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ErrorLogAnalyzer:
    """Analyze error logs and suggest fixes"""
    
    def __init__(self):
        self.errors = []
        self.patterns = self._load_error_patterns()
    
    def _load_error_patterns(self) -> Dict:
        """Load known error patterns and fixes"""
        return {
            'import_error': {
                'pattern': r'(ImportError|ModuleNotFoundError):\s*(.+)',
                'severity': 'high',
                'fix_suggestions': [
                    'Install missing package: pip install {package}',
                    'Check virtual environment activation',
                    'Verify requirements.txt is up to date'
                ]
            },
            'syntax_error': {
                'pattern': r'SyntaxError:\s*(.+)\s*File\s*"(.+)",\s*line\s*(\d+)',
                'severity': 'critical',
                'fix_suggestions': [
                    'Check syntax at line {line}',
                    'Look for missing colons, parentheses, or quotes',
                    'Use a linter to identify syntax issues'
                ]
            },
            'type_error': {
                'pattern': r'TypeError:\s*(.+)',
                'severity': 'medium',
                'fix_suggestions': [
                    'Check variable types before operation',
                    'Add type conversion if needed',
                    'Review function signatures'
                ]
            },
            'key_error': {
                'pattern': r'KeyError:\s*[\'"](.+)[\'"]',
                'severity': 'medium',
                'fix_suggestions': [
                    'Check if key exists before accessing',
                    'Use dict.get() with default value',
                    'Verify data structure is correct'
                ]
            },
            'attribute_error': {
                'pattern': r'AttributeError:\s*[\'"](.+)[\'"]',
                'severity': 'medium',
                'fix_suggestions': [
                    'Check if object has the attribute',
                    'Verify object is not None',
                    'Review class definition'
                ]
            },
            'file_not_found': {
                'pattern': r'FileNotFoundError:\s*\[Errno\s*2\]\s*(.+)',
                'severity': 'high',
                'fix_suggestions': [
                    'Check if file path is correct',
                    'Verify file exists before opening',
                    'Use absolute paths for reliability'
                ]
            },
            'permission_error': {
                'pattern': r'PermissionError:\s*\[Errno\s*13\]\s*(.+)',
                'severity': 'high',
                'fix_suggestions': [
                    'Run as administrator',
                    'Check file permissions',
                    'Close file handles properly'
                ]
            },
            'timeout_error': {
                'pattern': r'(TimeoutError|socket\.timeout):\s*(.+)',
                'severity': 'medium',
                'fix_suggestions': [
                    'Increase timeout value',
                    'Check network connectivity',
                    'Implement retry logic'
                ]
            },
            'connection_error': {
                'pattern': r'(ConnectionError|requests\.exceptions\.ConnectionError):\s*(.+)',
                'severity': 'high',
                'fix_suggestions': [
                    'Check network connection',
                    'Verify server is running',
                    'Implement connection retry'
                ]
            },
            'memory_error': {
                'pattern': r'MemoryError:\s*(.+)',
                'severity': 'critical',
                'fix_suggestions': [
                    'Reduce data size or batch processing',
                    'Use generators instead of lists',
                    'Increase available memory'
                ]
            },
            'encoding_error': {
                'pattern': r'(UnicodeDecodeError|UnicodeEncodeError):\s*(.+)',
                'severity': 'medium',
                'fix_suggestions': [
                    'Specify encoding explicitly (utf-8)',
                    'Use errors="ignore" or errors="replace"',
                    'Check file encoding before reading'
                ]
            },
            'json_error': {
                'pattern': r'json\.decoder\.JSONDecodeError:\s*(.+)',
                'severity': 'medium',
                'fix_suggestions': [
                    'Validate JSON before parsing',
                    'Check for trailing commas or missing quotes',
                    'Use try-except for JSON parsing'
                ]
            }
        }
    
    def scan_for_errors(self, dir_path: Path = None) -> List[Dict]:
        """Scan directory for error logs"""
        if dir_path is None:
            dir_path = LOGS_DIR
        
        print(f"[SCAN] Scanning {dir_path} for errors...")
        
        errors = []
        
        # Find log files
        log_patterns = ['*.log', '*.txt', '*.json']
        log_files = []
        
        for pattern in log_patterns:
            log_files.extend(dir_path.glob(f"**/{pattern}"))
        
        # Also scan Python files for error patterns
        py_files = list((WORKSPACE / "30-scripts-tools").glob("*.py"))
        
        all_files = log_files + py_files
        print(f"[SCAN] Found {len(all_files)} files to analyze")
        
        for file_path in all_files[:50]:  # Limit to 50 files
            file_errors = self._analyze_file(file_path)
            errors.extend(file_errors)
        
        self.errors = errors
        print(f"[SCAN] Found {len(errors)} errors")
        
        return errors
    
    def _analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a single file for errors"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for error patterns
                for error_type, config in self.patterns.items():
                    match = re.search(config['pattern'], line, re.IGNORECASE)
                    
                    if match:
                        error = {
                            'file': str(file_path),
                            'line': line_num,
                            'type': error_type,
                            'message': match.group(0),
                            'severity': config['severity'],
                            'timestamp': datetime.now().isoformat(),
                            'fix_suggestions': config['fix_suggestions']
                        }
                        
                        # Extract additional context
                        if 'line' in str(match.groups()):
                            error['line_number'] = match.group(3) if len(match.groups()) > 2 else line_num
                        
                        errors.append(error)
        
        except Exception as e:
            # Skip files that can't be read
            pass
        
        return errors
    
    def analyze_trends(self) -> Dict:
        """Analyze error trends"""
        if not self.errors:
            return {'error': 'No errors to analyze'}
        
        # Count by type
        type_counts = Counter(e['type'] for e in self.errors)
        
        # Count by severity
        severity_counts = Counter(e['severity'] for e in self.errors)
        
        # Count by file
        file_counts = Counter(e['file'] for e in self.errors)
        
        # Most common errors
        most_common = type_counts.most_common(10)
        
        # Files with most errors
        problematic_files = file_counts.most_common(5)
        
        return {
            'total_errors': len(self.errors),
            'by_type': dict(type_counts),
            'by_severity': dict(severity_counts),
            'most_common': most_common,
            'problematic_files': problematic_files,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def generate_fix_suggestions(self, error_type: str = None) -> List[Dict]:
        """Generate fix suggestions for errors"""
        suggestions = []
        
        errors_to_fix = self.errors
        if error_type:
            errors_to_fix = [e for e in self.errors if e['type'] == error_type]
        
        for error in errors_to_fix[:20]:  # Limit to 20
            suggestion = {
                'error': error['message'][:100],
                'file': error['file'],
                'line': error.get('line', 'unknown'),
                'type': error['type'],
                'severity': error['severity'],
                'suggestions': error['fix_suggestions']
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def generate_report(self) -> str:
        """Generate comprehensive error analysis report"""
        print("[REPORT] Generating error analysis report...")
        
        if not self.errors:
            self.scan_for_errors()
        
        trends = self.analyze_trends()
        
        report = f"""# Error Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Errors Found:** {trends.get('total_errors', 0)}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Errors | {trends.get('total_errors', 0)} |
| Critical | {trends.get('by_severity', {}).get('critical', 0)} |
| High | {trends.get('by_severity', {}).get('high', 0)} |
| Medium | {trends.get('by_severity', {}).get('medium', 0)} |

---

## Error Distribution by Type

"""
        
        # Error by type
        if trends.get('most_common'):
            report += "| Type | Count | Percentage |\n"
            report += "|------|-------|------------|\n"
            total = trends.get('total_errors', 1)
            for error_type, count in trends['most_common']:
                pct = round(count / total * 100, 1)
                report += f"| {error_type} | {count} | {pct}% |\n"
        
        report += f"""
---

## Problematic Files

"""
        
        if trends.get('problematic_files'):
            report += "| File | Error Count |\n"
            report += "|------|-------------|\n"
            for file_path, count in trends['problematic_files']:
                file_name = Path(file_path).name
                report += f"| {file_name} | {count} |\n"
        
        report += f"""
---

## Top Fix Suggestions

"""
        
        # Generate fix suggestions
        suggestions = self.generate_fix_suggestions()
        
        for i, sug in enumerate(suggestions[:5], 1):
            report += f"\n### {i}. {sug['type'].replace('_', ' ').title()}\n\n"
            report += f"**File:** `{Path(sug['file']).name}` (line {sug['line']})\n\n"
            report += f"**Error:** `{sug['error']}`\n\n"
            report += "**Suggestions:**\n"
            for fix in sug['suggestions']:
                report += f"- {fix}\n"
        
        report += f"""
---

## Recommendations

1. **Address Critical Errors First** - Fix all critical severity errors immediately
2. **Focus on Common Patterns** - Top error types affect multiple files
3. **Implement Error Handling** - Add try-except blocks for common errors
4. **Add Logging** - Improve error tracking and debugging
5. **Regular Scans** - Run this analyzer weekly to catch new errors

---

*Generated by Error Log Analyzer (Phase 4 Innovation)*
"""
        
        # Save report
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = ANALYSIS_DIR / f"error-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"[OK] Saved to {report_path}")
        
        return report
    
    def show_summary(self):
        """Show error summary"""
        print("\n" + "=" * 60)
        print("Error Analysis Summary")
        print("=" * 60)
        
        if not self.errors:
            self.scan_for_errors()
        
        trends = self.analyze_trends()
        
        print(f"\nTotal Errors: {trends.get('total_errors', 0)}")
        print(f"\nBy Severity:")
        for severity, count in trends.get('by_severity', {}).items():
            icon = "🔴" if severity == 'critical' else "🟠" if severity == 'high' else "🟡"
            print(f"  {icon} {severity}: {count}")
        
        print(f"\nTop 5 Error Types:")
        for error_type, count in trends.get('most_common', [])[:5]:
            print(f"  - {error_type.replace('_', ' ').title()}: {count}")
        
        print(f"\nFiles Needing Attention:")
        for file_path, count in trends.get('problematic_files', [])[:3]:
            print(f"  - {Path(file_path).name}: {count} errors")
        
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Error Log Analyzer')
    parser.add_argument('--analyze', type=str, help='Analyze directory for errors')
    parser.add_argument('--scan', action='store_true', help='Scan for errors')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--suggest', action='store_true', help='Show fix suggestions')
    args = parser.parse_args()
    
    analyzer = ErrorLogAnalyzer()
    
    if args.analyze:
        dir_path = Path(args.analyze)
        errors = analyzer.scan_for_errors(dir_path)
        analyzer.show_summary()
    
    if args.scan:
        errors = analyzer.scan_for_errors()
        analyzer.show_summary()
    
    if args.report:
        report = analyzer.generate_report()
        print(report[:2000])
    
    if args.suggest:
        if not analyzer.errors:
            analyzer.scan_for_errors()
        suggestions = analyzer.generate_fix_suggestions()
        print(f"\nFix Suggestions ({len(suggestions)}):")
        for i, sug in enumerate(suggestions[:10], 1):
            print(f"\n{i}. {sug['type'].title()}")
            print(f"   File: {Path(sug['file']).name}:{sug['line']}")
            print(f"   Error: {sug['error'][:80]}")
            print(f"   Fixes:")
            for fix in sug['suggestions'][:2]:
                print(f"     - {fix}")
    
    if not any([args.analyze, args.scan, args.report, args.suggest]):
        parser.print_help()


if __name__ == "__main__":
    main()
