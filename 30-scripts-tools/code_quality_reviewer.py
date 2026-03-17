#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code Quality Auto-Reviewer - Phase 4 Innovation
Automated code review with AI-powered analysis
Features: 6-dimension scoring, issue detection, fix suggestions, trend tracking

Usage:
    python code_quality_reviewer.py --review path/to/file.py
    python code_quality_reviewer.py --scan 30-scripts-tools/
    python code_quality_reviewer.py --report  # Generate report
    python code_quality_reviewer.py --trend   # Show quality trend
"""

import os
import sys
import json
import ast
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports" / "code-quality"
REPORTS_DIR = DATA_DIR / "reports"
HISTORY_FILE = DATA_DIR / "review-history.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class CodeQualityReviewer:
    """Automated code quality reviewer"""
    
    def __init__(self):
        self.history = self._load_history()
        self.results = []
    
    def _load_history(self) -> Dict:
        """Load review history"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"reviews": [], "trends": {}}
    
    def _save_history(self):
        """Save review history"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Python file"""
        print(f"[REVIEW] {file_path.name}...")
        
        result = {
            'file': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'issues': [],
            'suggestions': [],
            'score': 0,
            'grade': 'F'
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Metric 1: Lines of Code
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            result['metrics']['lines_of_code'] = loc
            result['metrics']['total_lines'] = len(lines)
            
            # Metric 2: Complexity (cyclomatic approximation)
            complexity = self._calculate_complexity(content)
            result['metrics']['complexity'] = complexity
            
            # Metric 3: Documentation ratio
            doc_ratio = self._calculate_doc_ratio(lines)
            result['metrics']['documentation_ratio'] = round(doc_ratio, 2)
            
            # Metric 4: Function count
            func_count = content.count('def ')
            result['metrics']['function_count'] = func_count
            
            # Metric 5: Class count
            class_count = content.count('class ')
            result['metrics']['class_count'] = class_count
            
            # Metric 6: Import count
            import_count = len([l for l in lines if l.strip().startswith('import ') or l.strip().startswith('from ')])
            result['metrics']['import_count'] = import_count
            
            # Detect issues
            issues = self._detect_issues(content, lines)
            result['issues'] = issues
            
            # Generate suggestions
            suggestions = self._generate_suggestions(issues, result['metrics'])
            result['suggestions'] = suggestions
            
            # Calculate score (0-100)
            score = self._calculate_score(result['metrics'], len(issues))
            result['score'] = score
            
            # Assign grade
            result['grade'] = self._score_to_grade(score)
            
        except Exception as e:
            result['error'] = str(e)
            result['score'] = 0
        
        return result
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity approximation"""
        complexity = 1  # Base complexity
        
        # Count decision points
        keywords = ['if ', 'elif ', 'for ', 'while ', 'except ', 'and ', 'or ']
        for kw in keywords:
            complexity += content.count(kw)
        
        return complexity
    
    def _calculate_doc_ratio(self, lines: List[str]) -> float:
        """Calculate documentation ratio"""
        if not lines:
            return 0.0
        
        doc_lines = 0
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            
            if '"""' in stripped or "'''" in stripped:
                docstring_marker = '"""' if '"""' in stripped else "'''"
                count = stripped.count(docstring_marker)
                if count == 1:
                    in_docstring = not in_docstring
                elif count >= 2:
                    doc_lines += 1
                doc_lines += count // 2
            
            if in_docstring:
                doc_lines += 1
            
            if stripped.startswith('#'):
                doc_lines += 1
        
        return doc_lines / len(lines)
    
    def _detect_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """Detect code quality issues"""
        issues = []
        
        # Issue 1: Long lines (>120 chars)
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'type': 'long_line',
                    'severity': 'low',
                    'line': i,
                    'message': f'Line {i} exceeds 120 characters ({len(line)} chars)',
                    'suggestion': 'Break into multiple lines'
                })
        
        # Issue 2: Missing docstrings
        if 'def ' in content and '"""' not in content and "'''" not in content:
            issues.append({
                'type': 'missing_docstring',
                'severity': 'medium',
                'line': 0,
                'message': 'No docstrings found in file with functions',
                'suggestion': 'Add docstrings to all public functions'
            })
        
        # Issue 3: Too many imports (>20)
        import_lines = [l for l in lines if l.strip().startswith('import ') or l.strip().startswith('from ')]
        if len(import_lines) > 20:
            issues.append({
                'type': 'too_many_imports',
                'severity': 'low',
                'line': 0,
                'message': f'Too many imports ({len(import_lines)})',
                'suggestion': 'Consider grouping related imports or refactoring'
            })
        
        # Issue 4: Long functions (>50 lines)
        func_starts = []
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                func_starts.append(i)
        
        for i, start in enumerate(func_starts):
            end = func_starts[i + 1] if i + 1 < len(func_starts) else len(lines)
            func_length = end - start
            if func_length > 50:
                issues.append({
                    'type': 'long_function',
                    'severity': 'medium',
                    'line': start + 1,
                    'message': f'Function at line {start + 1} is {func_length} lines long',
                    'suggestion': 'Break into smaller functions'
                })
        
        # Issue 5: Magic numbers
        import re
        magic_numbers = re.findall(r'(?<!["\w])(\d{2,})(?!["\w])', content)
        if len(magic_numbers) > 5:
            issues.append({
                'type': 'magic_numbers',
                'severity': 'low',
                'line': 0,
                'message': f'Found {len(magic_numbers)} magic numbers',
                'suggestion': 'Define constants for magic numbers'
            })
        
        # Issue 6: Bare except
        if 'except:' in content:
            issues.append({
                'type': 'bare_except',
                'severity': 'high',
                'line': 0,
                'message': 'Found bare except: clause',
                'suggestion': 'Use except Exception: or specific exception types'
            })
        
        # Issue 7: Print statements (in production code)
        print_count = content.count('print(')
        if print_count > 5:
            issues.append({
                'type': 'too_many_prints',
                'severity': 'low',
                'line': 0,
                'message': f'Found {print_count} print statements',
                'suggestion': 'Use logging module instead of print'
            })
        
        return issues
    
    def _generate_suggestions(self, issues: List[Dict], metrics: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if metrics.get('complexity', 0) > 20:
            suggestions.append("Consider refactoring to reduce complexity (current: {})".format(metrics['complexity']))
        
        if metrics.get('documentation_ratio', 0) < 0.1:
            suggestions.append("Add more documentation (current: {:.1f}%)".format(metrics['documentation_ratio'] * 100))
        
        if metrics.get('lines_of_code', 0) > 500:
            suggestions.append("Consider splitting this file ({} LOC)".format(metrics['lines_of_code']))
        
        # Add suggestions from issues
        for issue in issues:
            if issue.get('suggestion') and issue['suggestion'] not in suggestions:
                suggestions.append(issue['suggestion'])
        
        return suggestions
    
    def _calculate_score(self, metrics: Dict, issue_count: int) -> int:
        """Calculate overall quality score (0-100)"""
        score = 100
        
        # Deduct for issues
        severity_weights = {'high': 10, 'medium': 5, 'low': 2}
        # We'll need to recalculate issues or pass them - for now approximate
        score -= min(issue_count * 3, 30)  # Max 30 point deduction for issues
        
        # Deduct for complexity
        if metrics.get('complexity', 0) > 30:
            score -= 10
        elif metrics.get('complexity', 0) > 20:
            score -= 5
        
        # Deduct for low documentation
        if metrics.get('documentation_ratio', 0) < 0.05:
            score -= 10
        elif metrics.get('documentation_ratio', 0) < 0.1:
            score -= 5
        
        # Bonus for good practices
        if metrics.get('documentation_ratio', 0) > 0.2:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'B+'
        elif score >= 80:
            return 'B'
        elif score >= 75:
            return 'C+'
        elif score >= 70:
            return 'C'
        elif score >= 65:
            return 'D+'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def review_file(self, file_path: Path) -> Dict:
        """Review a single file and store result"""
        result = self.analyze_file(file_path)
        self.results.append(result)
        return result
    
    def scan_directory(self, dir_path: Path, pattern: str = "*.py") -> List[Dict]:
        """Scan directory for Python files"""
        print(f"[SCAN] Scanning {dir_path} for {pattern}...")
        
        py_files = list(dir_path.glob(pattern))
        print(f"[SCAN] Found {len(py_files)} files")
        
        results = []
        for i, file_path in enumerate(py_files, 1):
            result = self.analyze_file(file_path)
            results.append(result)
            
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(py_files)}...")
        
        self.results = results
        
        # Save to history
        self.history['reviews'].append({
            'timestamp': datetime.now().isoformat(),
            'directory': str(dir_path),
            'file_count': len(results),
            'results': results
        })
        
        # Keep only last 50 reviews
        self.history['reviews'] = self.history['reviews'][-50:]
        self._save_history()
        
        return results
    
    def generate_report(self, output_path: Path = None) -> str:
        """Generate quality report"""
        if not self.results:
            return "No review results available"
        
        # Calculate summary statistics
        total_files = len(self.results)
        avg_score = sum(r['score'] for r in self.results) / total_files if total_files > 0 else 0
        
        grade_distribution = {}
        for r in self.results:
            grade = r.get('grade', 'F')
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        issue_types = {}
        for r in self.results:
            for issue in r.get('issues', []):
                itype = issue.get('type', 'unknown')
                issue_types[itype] = issue_types.get(itype, 0) + 1
        
        # Generate report
        report = f"""
# Code Quality Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Files Reviewed:** {total_files}

## Summary

| Metric | Value |
|--------|-------|
| Average Score | {avg_score:.1f}/100 |
| Average Grade | {self._score_to_grade(int(avg_score))} |
| Total Issues | {sum(len(r.get('issues', [])) for r in self.results)} |

## Grade Distribution

"""
        for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']:
            count = grade_distribution.get(grade, 0)
            if count > 0:
                bar = '█' * (count * 2)
                report += f"- **{grade}**: {count} files {bar}\n"
        
        report += "\n## Issue Types\n\n"
        for itype, count in sorted(issue_types.items(), key=lambda x: -x[1])[:10]:
            report += f"- **{itype}**: {count} occurrences\n"
        
        report += "\n## Top Issues by File\n\n"
        
        # Show files with most issues
        by_issue_count = sorted(self.results, key=lambda x: -len(x.get('issues', [])))[:10]
        for r in by_issue_count:
            file_name = Path(r['file']).name
            issue_count = len(r.get('issues', []))
            score = r.get('score', 0)
            report += f"- `{file_name}`: {issue_count} issues (Score: {score})\n"
        
        # Save report
        if output_path is None:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = REPORTS_DIR / f"quality-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        
        output_path.write_text(report, encoding='utf-8')
        print(f"[REPORT] Saved to {output_path}")
        
        return report
    
    def show_trend(self):
        """Show quality trend over time"""
        if not self.history.get('reviews'):
            print("[INFO] No review history available")
            return
        
        print("\n" + "=" * 60)
        print("Code Quality Trend")
        print("=" * 60)
        
        # Group by date
        by_date = {}
        for review in self.history['reviews']:
            date = review['timestamp'][:10]
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(review)
        
        print("\nRecent Reviews:")
        for date in sorted(by_date.keys())[-10:]:
            reviews = by_date[date]
            total_files = sum(r.get('file_count', len(r.get('results', []))) for r in reviews)
            avg_scores = []
            for r in reviews:
                for result in r.get('results', []):
                    if 'score' in result:
                        avg_scores.append(result['score'])
            
            avg_score = sum(avg_scores) / len(avg_scores) if avg_scores else 0
            
            print(f"  {date}: {total_files} files, avg score {avg_score:.1f}")
        
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Code Quality Auto-Reviewer')
    parser.add_argument('--review', type=str, help='Review a single file')
    parser.add_argument('--scan', type=str, help='Scan a directory')
    parser.add_argument('--pattern', type=str, default='*.py', help='File pattern (default: *.py)')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--trend', action='store_true', help='Show quality trend')
    args = parser.parse_args()
    
    reviewer = CodeQualityReviewer()
    
    if args.review:
        file_path = Path(args.review)
        result = reviewer.review_file(file_path)
        
        print(f"\n{'=' * 60}")
        print(f"Review: {file_path.name}")
        print(f"{'=' * 60}")
        print(f"Score: {result['score']}/100 (Grade: {result['grade']})")
        print(f"Lines of Code: {result['metrics'].get('lines_of_code', 'N/A')}")
        print(f"Complexity: {result['metrics'].get('complexity', 'N/A')}")
        print(f"Documentation: {result['metrics'].get('documentation_ratio', 0) * 100:.1f}%")
        print(f"Issues: {len(result.get('issues', []))}")
        
        if result.get('issues'):
            print(f"\nTop Issues:")
            for issue in result['issues'][:5]:
                print(f"  [{issue['severity'].upper()}] {issue['message']}")
        
        if result.get('suggestions'):
            print(f"\nSuggestions:")
            for sug in result['suggestions'][:3]:
                print(f"  • {sug}")
        
        print(f"{'=' * 60}")
    
    if args.scan:
        dir_path = Path(args.scan)
        results = reviewer.scan_directory(dir_path, args.pattern)
        
        # Summary
        total = len(results)
        avg_score = sum(r['score'] for r in results) / total if total > 0 else 0
        
        print(f"\n{'=' * 60}")
        print(f"Scan Complete: {total} files")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Average Grade: {reviewer._score_to_grade(int(avg_score))}")
        print(f"{'=' * 60}")
    
    if args.report:
        report = reviewer.generate_report()
        print(report[:2000])  # Show first 2000 chars
    
    if args.trend:
        reviewer.show_trend()
    
    if not any([args.review, args.scan, args.report, args.trend]):
        parser.print_help()


if __name__ == "__main__":
    main()
