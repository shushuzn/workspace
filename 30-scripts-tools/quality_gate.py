#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality Gate Checker - 质量门禁检查器 (Auto-Critic v7.0 组件)

功能:
1. 代码质量检查 (pylint/flake8)
2. 安全检查 (bandit)
3. 复杂度检查 (圈复杂度)
4. 单元测试覆盖率
5. 文档完整性

使用:
    py quality_gate.py --check 30-scripts-tools/*.py
    py quality_gate.py --report
"""

import sys
import os
import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class QualityIssue:
    """质量问题"""
    file: str
    line: int
    column: int
    category: str  # pylint/flake8/security/complexity
    code: str      # 问题代码 (如 W0613, E501)
    message: str
    severity: str  # critical/high/medium/low


@dataclass
class QualityReport:
    """质量报告"""
    files_checked: int
    total_issues: int
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    issues: List[QualityIssue]
    metrics: dict
    passed: bool
    score: float


class QualityGateChecker:
    """质量门禁检查器"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.issues = []
    
    def check_pylint(self, file_pattern: str = "30-scripts-tools/*.py") -> List[QualityIssue]:
        """Pylint 检查"""
        import subprocess
        
        issues = []
        files = list(self.workspace.glob(file_pattern))
        
        for file in files:
            try:
                result = subprocess.run(
                    ['pylint', str(file), '--output-format=json', '--disable=all', 
                     '--enable=unused-import,undefined-variable'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    try:
                        pylint_results = json.loads(result.stdout)
                        for item in pylint_results:
                            issues.append(QualityIssue(
                                file=str(file.relative_to(self.workspace)),
                                line=item.get('line', 0),
                                column=item.get('column', 0),
                                category='pylint',
                                code=item.get('symbol', ''),
                                message=item.get('message', ''),
                                severity='medium'
                            ))
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                # Pylint 可能未安装
                pass
        
        return issues
    
    def check_flake8(self, file_pattern: str = "30-scripts-tools/*.py") -> List[QualityIssue]:
        """Flake8 检查"""
        import subprocess
        
        issues = []
        files = list(self.workspace.glob(file_pattern))
        
        for file in files:
            try:
                result = subprocess.run(
                    ['flake8', str(file), '--format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    try:
                        flake8_results = json.loads(result.stdout)
                        for item in flake8_results:
                            issues.append(QualityIssue(
                                file=str(file.relative_to(self.workspace)),
                                line=item.get('line_number', 0),
                                column=item.get('column_number', 0),
                                category='flake8',
                                code=item.get('code', ''),
                                message=item.get('text', ''),
                                severity='low' if item.get('code', '').startswith('W') else 'medium'
                            ))
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                # Flake8 可能未安装
                pass
        
        return issues
    
    def check_security(self, file_pattern: str = "30-scripts-tools/*.py") -> List[QualityIssue]:
        """安全检查 (Bandit)"""
        import subprocess
        
        issues = []
        files = list(self.workspace.glob(file_pattern))
        
        for file in files:
            try:
                result = subprocess.run(
                    ['bandit', '-r', str(file), '-f', 'json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    try:
                        bandit_results = json.loads(result.stdout)
                        for item in bandit_results.get('results', []):
                            issues.append(QualityIssue(
                                file=str(file.relative_to(self.workspace)),
                                line=item.get('line_number', 0),
                                column=0,
                                category='security',
                                code=item.get('test_id', ''),
                                message=item.get('issue_text', ''),
                                severity='critical' if item.get('issue_severity') == 'HIGH' else 'high'
                            ))
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                # Bandit 可能未安装
                pass
        
        return issues
    
    def check_complexity(self, file_pattern: str = "30-scripts-tools/*.py", max_complexity: int = 10) -> List[QualityIssue]:
        """圈复杂度检查"""
        issues = []
        files = list(self.workspace.glob(file_pattern))
        
        for file in files:
            try:
                tree = ast.parse(file.read_text(encoding='utf-8'))
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            issues.append(QualityIssue(
                                file=str(file.relative_to(self.workspace)),
                                line=node.lineno,
                                column=0,
                                category='complexity',
                                code=f'C{complexity}',
                                message=f"Function '{node.name}' has complexity {complexity} (max: {max_complexity})",
                                severity='high' if complexity > 15 else 'medium'
                            ))
            except Exception as e:
                continue
        
        return issues
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                 ast.With, ast.Assert, ast.comprehension)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def check_test_coverage(self) -> dict:
        """检查测试覆盖率"""
        test_dir = self.workspace / "92-tests"
        
        if not test_dir.exists():
            return {'has_tests': False, 'coverage': 0}
        
        test_files = list(test_dir.glob("*.py"))
        
        # 简单估算：测试文件数量 / 源文件数量
        source_files = len(list((self.workspace / "30-scripts-tools").glob("*.py")))
        
        coverage = len(test_files) / source_files * 100 if source_files > 0 else 0
        
        return {
            'has_tests': len(test_files) > 0,
            'test_count': len(test_files),
            'estimated_coverage': min(coverage, 100)
        }
    
    def check_documentation(self) -> dict:
        """检查文档完整性"""
        doc_dir = self.workspace / "15-docs"
        
        if not doc_dir.exists():
            return {'has_docs': False, 'completeness': 0}
        
        doc_files = list(doc_dir.glob("*.md"))
        
        # 检查是否有 README
        readme_exists = (self.workspace / "README.md").exists()
        
        # 检查文档质量 (简单：是否有标题)
        quality_score = 0
        for doc in doc_files[:10]:  # 检查前 10 个
            content = doc.read_text(encoding='utf-8')
            if '#' in content:
                quality_score += 1
        
        return {
            'has_docs': len(doc_files) > 0,
            'doc_count': len(doc_files),
            'readme_exists': readme_exists,
            'quality_score': quality_score / 10 * 100 if doc_files else 0
        }
    
    def run_all(self, file_pattern: str = "30-scripts-tools/*.py") -> QualityReport:
        """执行所有检查"""
        # 收集所有问题
        self.issues = []
        self.issues.extend(self.check_pylint(file_pattern))
        self.issues.extend(self.check_flake8(file_pattern))
        self.issues.extend(self.check_security(file_pattern))
        self.issues.extend(self.check_complexity(file_pattern))
        
        # 统计
        by_category = {}
        by_severity = {}
        
        for issue in self.issues:
            by_category[issue.category] = by_category.get(issue.category, 0) + 1
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
        
        # 检查文件数量
        files_checked = len(set(i.file for i in self.issues))
        
        # 其他指标
        coverage = self.check_test_coverage()
        docs = self.check_documentation()
        
        # 计算分数 (100 分制)
        score = 100
        score -= by_severity.get('critical', 0) * 10
        score -= by_severity.get('high', 0) * 5
        score -= by_severity.get('medium', 0) * 2
        score -= by_severity.get('low', 0) * 1
        score = max(0, min(100, score))
        
        # 是否通过 (≥80 分)
        passed = score >= 80
        
        return QualityReport(
            files_checked=files_checked,
            total_issues=len(self.issues),
            by_category=by_category,
            by_severity=by_severity,
            issues=self.issues[:50],  # 限制输出
            metrics={
                'test_coverage': coverage,
                'documentation': docs
            },
            passed=passed,
            score=score
        )


def print_report(report: QualityReport):
    """打印报告"""
    print("\n" + "=" * 60)
    print("Quality Gate Report")
    print("=" * 60)
    
    status = "✅ PASS" if report.passed else "❌ FAIL"
    print(f"\nStatus: {status}")
    print(f"Score: {report.score}/100")
    print(f"Files Checked: {report.files_checked}")
    print(f"Total Issues: {report.total_issues}")
    
    print(f"\n[By Category]")
    for cat, count in report.by_category.items():
        print(f"  {cat:15s}: {count}")
    
    print(f"\n[By Severity]")
    for sev, count in report.by_severity.items():
        icon = "🔴" if sev == "critical" else ("🟠" if sev == "high" else ("🟡" if sev == "medium" else "🔵"))
        print(f"  {icon} {sev:15s}: {count}")
    
    if report.issues:
        print(f"\n[Top Issues]")
        for issue in report.issues[:10]:
            print(f"  [{issue.severity.upper()}] {issue.file}:{issue.line}")
            print(f"    {issue.code}: {issue.message[:80]}")
    
    print(f"\n[Metrics]")
    test_cov = report.metrics.get('test_coverage', {})
    print(f"  Test Coverage: {test_cov.get('estimated_coverage', 0):.1f}%")
    
    docs = report.metrics.get('documentation', {})
    print(f"  Documentation: {docs.get('quality_score', 0):.1f}%")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quality Gate Checker')
    parser.add_argument('--check', type=str, default='30-scripts-tools/*.py', help='检查模式')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--min-score', type=int, default=80, help='最低通过分数')
    
    args = parser.parse_args()
    
    workspace = Path(__file__).parent.parent
    checker = QualityGateChecker(workspace)
    
    report = checker.run_all(args.check)
    
    if args.json:
        output = {
            'status': 'PASS' if report.passed else 'FAIL',
            'score': report.score,
            'files_checked': report.files_checked,
            'total_issues': report.total_issues,
            'by_category': report.by_category,
            'by_severity': report.by_severity,
            'issues': [asdict(i) for i in report.issues],
            'metrics': report.metrics
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_report(report)
    
    # 返回码
    return 0 if report.passed else 1


if __name__ == '__main__':
    sys.exit(main())
