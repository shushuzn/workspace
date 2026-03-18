#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Code Reviewer - Automated code quality review

Usage:
    python code_reviewer.py --file FILE [--output OUTPUT]
    python code_reviewer.py --dir DIRECTORY [--output OUTPUT]
"""

import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
OUTPUT_DIR = Path(r"D:\OpenClaw\workspace\20-data-reports")
OUTPUT_FILE = OUTPUT_DIR / "code-review-report.json"

class CodeReviewer:
    """Automated code reviewer"""
    
    def __init__(self):
        self.issues = []
        self.metrics = {}
        
        # Review rules
        self.rules = {
            'line_length': {'max': 120, 'weight': 1},
            'function_length': {'max': 50, 'weight': 2},
            'class_length': {'max': 300, 'weight': 2},
            'docstring_required': {'enabled': True, 'weight': 3},
            'type_hints': {'enabled': True, 'weight': 2},
            'magic_numbers': {'enabled': True, 'weight': 1},
            'too_many_args': {'max': 5, 'weight': 2},
            'nested_loops': {'max': 3, 'weight': 3},
            'duplicate_imports': {'enabled': True, 'weight': 1},
            'unused_imports': {'enabled': True, 'weight': 2}
        }
    
    def review_file(self, file_path: Path) -> Dict:
        """Review a single Python file"""
        self.issues = []
        self.metrics = {}
        
        if not file_path.exists():
            return {'error': f'File not found: {file_path}'}
        
        if file_path.suffix != '.py':
            return {'error': f'Not a Python file: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return {'error': f'Syntax error: {e}'}
            
            # Run checks
            self._check_line_length(lines)
            self._check_function_length(tree)
            self._check_class_length(tree)
            self._check_docstrings(tree)
            self._check_type_hints(tree)
            self._check_magic_numbers(lines)
            self._check_function_args(tree)
            self._check_nested_loops(tree)
            self._check_imports(tree, lines)
            
            # Calculate score
            score = self._calculate_score()
            
            return {
                'file': str(file_path),
                'lines': len(lines),
                'issues': self.issues,
                'metrics': self.metrics,
                'score': score,
                'grade': self._score_to_grade(score),
                'reviewed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Review failed: {e}'}
    
    def _check_line_length(self, lines: List[str]):
        """Check line length"""
        max_length = self.rules['line_length']['max']
        violations = []
        
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                violations.append(i)
        
        if violations:
            self.issues.append({
                'type': 'line_length',
                'severity': 'low',
                'message': f'{len(violations)} lines exceed {max_length} characters',
                'lines': violations[:10],  # Show first 10
                'weight': self.rules['line_length']['weight']
            })
        
        self.metrics['line_count'] = len(lines)
        self.metrics['max_line_length'] = max(len(l) for l in lines) if lines else 0
    
    def _check_function_length(self, tree: ast.AST):
        """Check function length"""
        max_length = self.rules['function_length']['max']
        long_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count lines in function
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    func_length = node.end_lineno - node.lineno + 1
                    if func_length > max_length:
                        long_functions.append({
                            'name': node.name,
                            'lines': func_length,
                            'line': node.lineno
                        })
        
        if long_functions:
            self.issues.append({
                'type': 'function_length',
                'severity': 'medium',
                'message': f'{len(long_functions)} functions exceed {max_length} lines',
                'details': long_functions,
                'weight': self.rules['function_length']['weight']
            })
    
    def _check_class_length(self, tree: ast.AST):
        """Check class length"""
        max_length = self.rules['class_length']['max']
        long_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    class_length = node.end_lineno - node.lineno + 1
                    if class_length > max_length:
                        long_classes.append({
                            'name': node.name,
                            'lines': class_length,
                            'line': node.lineno
                        })
        
        if long_classes:
            self.issues.append({
                'type': 'class_length',
                'severity': 'medium',
                'message': f'{len(long_classes)} classes exceed {max_length} lines',
                'details': long_classes,
                'weight': self.rules['class_length']['weight']
            })
    
    def _check_docstrings(self, tree: ast.AST):
        """Check for missing docstrings"""
        if not self.rules['docstring_required']['enabled']:
            return
        
        missing = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing.append({
                        'name': node.name,
                        'type': node.__class__.__name__,
                        'line': node.lineno
                    })
        
        if missing:
            self.issues.append({
                'type': 'missing_docstrings',
                'severity': 'medium',
                'message': f'{len(missing)} functions/classes missing docstrings',
                'details': missing[:10],  # Show first 10
                'weight': self.rules['docstring_required']['weight']
            })
    
    def _check_type_hints(self, tree: ast.AST):
        """Check for missing type hints"""
        if not self.rules['type_hints']['enabled']:
            return
        
        missing = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check return type
                if not node.returns:
                    missing.append({
                        'name': node.name,
                        'issue': 'missing return type',
                        'line': node.lineno
                    })
                
                # Check argument types
                for arg in node.args.args:
                    if arg.annotation is None and arg.arg != 'self':
                        missing.append({
                            'name': node.name,
                            'issue': f'missing type for argument "{arg.arg}"',
                            'line': node.lineno
                        })
        
        if missing:
            self.issues.append({
                'type': 'missing_type_hints',
                'severity': 'low',
                'message': f'{len(missing)} missing type hints',
                'details': missing[:10],
                'weight': self.rules['type_hints']['weight']
            })
    
    def _check_magic_numbers(self, lines: List[str]):
        """Check for magic numbers"""
        if not self.rules['magic_numbers']['enabled']:
            return
        
        # Pattern for numbers not in obvious contexts
        magic_pattern = re.compile(r'(?<!["\'\w])(\d{3,})(?!["\'\w])')
        magic_numbers = []
        
        for i, line in enumerate(lines, 1):
            # Skip comments and strings
            if line.strip().startswith('#'):
                continue
            
            matches = magic_pattern.findall(line)
            for num in matches:
                if num not in ['100', '1000', '1024']:  # Common constants
                    magic_numbers.append({'line': i, 'number': num})
        
        if magic_numbers:
            self.issues.append({
                'type': 'magic_numbers',
                'severity': 'low',
                'message': f'{len(magic_numbers)} magic numbers found',
                'details': magic_numbers[:10],
                'weight': self.rules['magic_numbers']['weight']
            })
    
    def _check_function_args(self, tree: ast.AST):
        """Check for too many arguments"""
        max_args = self.rules['too_many_args']['max']
        too_many = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arg_count = len(node.args.args)
                if arg_count > max_args:
                    too_many.append({
                        'name': node.name,
                        'args': arg_count,
                        'line': node.lineno
                    })
        
        if too_many:
            self.issues.append({
                'type': 'too_many_arguments',
                'severity': 'medium',
                'message': f'{len(too_many)} functions have >{max_args} arguments',
                'details': too_many,
                'weight': self.rules['too_many_args']['weight']
            })
    
    def _check_nested_loops(self, tree: ast.AST):
        """Check for deeply nested loops"""
        max_depth = self.rules['nested_loops']['max']
        deep_nesting = []
        
        def check_depth(node, depth=0):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.For, ast.While)):
                    new_depth = depth + 1
                    if new_depth > max_depth:
                        deep_nesting.append({
                            'line': child.lineno,
                            'depth': new_depth
                        })
                    check_depth(child, new_depth)
                else:
                    check_depth(child, depth)
        
        check_depth(tree)
        
        if deep_nesting:
            self.issues.append({
                'type': 'nested_loops',
                'severity': 'high',
                'message': f'{len(deep_nesting)} loops exceed depth {max_depth}',
                'details': deep_nesting,
                'weight': self.rules['nested_loops']['weight']
            })
    
    def _check_imports(self, tree: ast.AST, lines: List[str]):
        """Check for duplicate and unused imports"""
        imports = []
        import_lines = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
                    import_lines[alias.name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_name = f'{module}.{alias.name}'
                    imports.append(full_name)
                    import_lines[full_name] = node.lineno
        
        # Check duplicates
        seen = set()
        duplicates = []
        for imp in imports:
            if imp in seen:
                duplicates.append(imp)
            seen.add(imp)
        
        if duplicates:
            self.issues.append({
                'type': 'duplicate_imports',
                'severity': 'low',
                'message': f'{len(duplicates)} duplicate imports',
                'details': list(set(duplicates)),
                'weight': self.rules['duplicate_imports']['weight']
            })
        
        self.metrics['import_count'] = len(set(imports))
    
    def _calculate_score(self) -> int:
        """Calculate quality score (0-100)"""
        base_score = 100
        
        for issue in self.issues:
            weight = issue.get('weight', 1)
            severity = issue.get('severity', 'low')
            
            # Severity multiplier
            if severity == 'high':
                penalty = 10 * weight
            elif severity == 'medium':
                penalty = 5 * weight
            else:  # low
                penalty = 2 * weight
            
            base_score -= penalty
        
        return max(0, min(100, base_score))
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to grade"""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Acceptable)'
        elif score >= 60:
            return 'D (Needs Improvement)'
        else:
            return 'F (Poor)'
    
    def review_directory(self, dir_path: Path, pattern: str = '*.py') -> List[Dict]:
        """Review all Python files in directory"""
        results = []
        
        py_files = list(dir_path.rglob(pattern))
        
        for i, py_file in enumerate(py_files, 1):
            print(f"Reviewing [{i}/{len(py_files)}]: {py_file}")
            result = self.review_file(py_file)
            if 'error' not in result:
                results.append(result)
        
        return results
    
    def save_report(self, results: List[Dict], output_file: Path = None):
        """Save review report"""
        if output_file is None:
            output_file = OUTPUT_FILE
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate summary
        total_files = len(results)
        avg_score = sum(r['score'] for r in results) / total_files if total_files > 0 else 0
        total_issues = sum(len(r['issues']) for r in results)
        
        # Grade distribution
        grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for r in results:
            grade = r['grade'][0]
            grades[grade] = grades.get(grade, 0) + 1
        
        report = {
            'version': '1.0',
            'reviewed_at': datetime.now().isoformat(),
            'summary': {
                'total_files': total_files,
                'average_score': round(avg_score, 1),
                'total_issues': total_issues,
                'grade_distribution': grades
            },
            'files': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Report saved to {output_file}")
        print(f"   Files: {total_files} | Avg Score: {avg_score:.1f} | Issues: {total_issues}")
    
    def preview(self, results: List[Dict]):
        """Preview results in console"""
        print(f"\n[CHART] Code Review Results ({len(results)} files)\n")
        
        for result in results[:5]:  # Show first 5
            print(f"📄 {result['file']}")
            print(f"   Score: {result['score']}/100 ({result['grade']})")
            print(f"   Lines: {result['lines']} | Issues: {len(result['issues'])}")
            
            for issue in result['issues'][:3]:  # Show first 3 issues
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
                print(f"   {severity_icon} {issue['message']}")
            
            print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Code Reviewer')
    parser.add_argument('--file', '-f', type=Path, help='Single file to review')
    parser.add_argument('--dir', '-d', type=Path, help='Directory to review')
    parser.add_argument('--pattern', '-p', type=str, default='*.py', help='File pattern')
    parser.add_argument('--output', '-o', type=Path, help='Output file')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--save', action='store_true', help='Save report')
    
    args = parser.parse_args()
    
    reviewer = CodeReviewer()
    
    if args.file:
        results = [reviewer.review_file(args.file)]
    elif args.dir:
        results = reviewer.review_directory(args.dir, args.pattern)
    else:
        # Default: review 30-scripts-tools
        results = reviewer.review_directory(Path('30-scripts-tools'))
    
    if args.preview or not args.save:
        reviewer.preview(results)
    
    if args.save:
        reviewer.save_report(results, args.output)


if __name__ == '__main__':
    main()
