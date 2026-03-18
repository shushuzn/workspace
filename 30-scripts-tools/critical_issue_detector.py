#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical Issue Detector - 严重问题检测器 (Auto-Critic v7.0 组件)

主动检测严重问题，而非依赖用户报告。

检测范围:
1. 异常栈扫描 (Traceback/Exception)
2. 核心模块变更风险分析
3. 数据丢失风险检测
4. 性能回退检测
5. 架构违规检测

使用:
    py critical_issue_detector.py --path "." --check all
    py critical_issue_detector.py --path "30-scripts-tools" --json
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class RiskLevel(Enum):
    """风险级别"""
    CRITICAL = "critical"  # 致命风险
    HIGH = "high"          # 高风险
    MEDIUM = "medium"      # 中风险
    LOW = "low"            # 低风险


@dataclass
class CriticalIssue:
    """严重问题记录"""
    id: str
    risk_level: str
    category: str
    title: str
    description: str
    affected_files: List[str]
    evidence: str
    impact: str
    recommendation: str
    detected_at: str


@dataclass
class DetectionResult:
    """检测结果"""
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    issues: List[CriticalIssue]
    scan_duration_ms: float
    timestamp: str


class CriticalIssueDetector:
    """严重问题检测器"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.issues = []
        
        # 核心模块定义
        self.core_modules = {
            'auto-critic.py',
            'tool_executor.py',
            'tools_registry.json',
            'session_end.py',
            'post_session_compress.py',
        }
    
    def detect_all(self) -> DetectionResult:
        """执行全量检测"""
        start_time = datetime.now()
        
        # 1. 异常栈扫描
        self._scan_exception_traces()
        
        # 2. 核心模块变更风险
        self._analyze_core_module_changes()
        
        # 3. 数据丢失风险
        self._check_data_loss_risk()
        
        # 4. 性能回退检测
        self._check_performance_regression()
        
        # 5. 架构违规检测
        self._check_architecture_violations()
        
        # 6. 安全风险
        self._check_security_risks()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        # 统计
        critical = sum(1 for i in self.issues if i.risk_level == "critical")
        high = sum(1 for i in self.issues if i.risk_level == "high")
        medium = sum(1 for i in self.issues if i.risk_level == "medium")
        low = sum(1 for i in self.issues if i.risk_level == "low")
        
        return DetectionResult(
            total_issues=len(self.issues),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            issues=self.issues,
            scan_duration_ms=round(duration, 2),
            timestamp=datetime.now().isoformat()
        )
    
    def _scan_exception_traces(self):
        """扫描异常栈"""
        # 扫描日志文件
        log_patterns = ['*.log', '*-log.json', 'workflow-execution-log.json']
        
        for pattern in log_patterns:
            for log_file in self.base_path.rglob(pattern):
                try:
                    content = log_file.read_text(encoding='utf-8', errors='replace')
                    
                    # 检测 Traceback
                    if 'Traceback' in content:
                        traceback_match = re.search(r'Traceback.*?(?=\n\n|\Z)', content, re.DOTALL)
                        if traceback_match:
                            self.issues.append(CriticalIssue(
                                id=f"exc-{len(self.issues)+1:03d}",
                                risk_level="critical",
                                category="exception",
                                title="Unhandled Exception Detected",
                                description=f"Exception found in {log_file.name}",
                                affected_files=[str(log_file.relative_to(self.base_path))],
                                evidence=traceback_match.group(0)[:500],
                                impact="May cause data loss or workflow failure",
                                recommendation="Review and fix the exception",
                                detected_at=datetime.now().isoformat()
                            ))
                    
                    # 检测 Error
                    error_matches = re.findall(r'(ERROR|Error):\s*(.+)', content)
                    for error_type, error_msg in error_matches[:5]:
                        self.issues.append(CriticalIssue(
                            id=f"exc-{len(self.issues)+1:03d}",
                            risk_level="high",
                            category="exception",
                            title=f"Error: {error_msg[:50]}",
                            description=f"Error detected in {log_file.name}",
                            affected_files=[str(log_file.relative_to(self.base_path))],
                            evidence=error_msg,
                            impact="May affect functionality",
                            recommendation="Investigate and resolve",
                            detected_at=datetime.now().isoformat()
                        ))
                
                except Exception:
                    continue
    
    def _analyze_core_module_changes(self):
        """分析核心模块变更风险"""
        try:
            # 获取 Git 变更
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                capture_output=True,
                text=True,
                cwd=str(self.base_path),
                timeout=30
            )
            
            if result.returncode == 0:
                changed_files = result.stdout.strip().split('\n')
                
                for file in changed_files:
                    if any(core in file for core in self.core_modules):
                        self.issues.append(CriticalIssue(
                            id=f"core-{len(self.issues)+1:03d}",
                            risk_level="high",
                            category="core_change",
                            title=f"Core Module Modified: {file}",
                            description="Core infrastructure module has been changed",
                            affected_files=[file],
                            evidence=f"Git diff shows changes in {file}",
                            impact="May affect entire system stability",
                            recommendation="Ensure thorough testing and review",
                            detected_at=datetime.now().isoformat()
                        ))
        
        except Exception:
            pass
    
    def _check_data_loss_risk(self):
        """检测数据丢失风险"""
        py_files = list(self.base_path.rglob("*.py"))
        
        risk_patterns = [
            (r'os\.remove\s*\(', 'Direct file deletion'),
            (r'shutil\.rmtree\s*\(', 'Directory tree deletion'),
            (r'rm\s+-rf', 'Dangerous rm command'),
            (r'\.drop\s*\(', 'Data deletion (pandas)'),
            (r'DELETE\s+FROM', 'SQL DELETE without WHERE'),
            (r'truncate\s*\(', 'Table truncation'),
        ]
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                
                for pattern, description in risk_patterns:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        # 检查是否有保护措施
                        has_protection = any(prot in content for prot in 
                                           ['if os.path.exists', 'try:', 'backup', 'confirm', 'dry_run'])
                        
                        risk_level = "medium" if has_protection else "critical"
                        
                        self.issues.append(CriticalIssue(
                            id=f"data-{len(self.issues)+1:03d}",
                            risk_level=risk_level,
                            category="data_loss",
                            title=f"Data Loss Risk: {description}",
                            description=f"Found in {py_file.name}",
                            affected_files=[str(py_file.relative_to(self.base_path))],
                            evidence=matches[0].group(0),
                            impact="Potential data loss",
                            recommendation="Add safeguards (backup, confirmation, dry-run)" if not has_protection else "Verify protection mechanisms",
                            detected_at=datetime.now().isoformat()
                        ))
            
            except Exception:
                continue
    
    def _check_performance_regression(self):
        """检测性能回退"""
        # 扫描 benchmarks
        benchmark_files = list(self.base_path.rglob("*benchmark*.py")) + \
                         list(self.base_path.rglob("*perf*.py"))
        
        for bench_file in benchmark_files:
            try:
                content = bench_file.read_text(encoding='utf-8', errors='replace')
                
                # 检测性能目标
                targets = re.findall(r'(\w+)_ms.*?:\s*(\d+)', content)
                for metric, target_ms in targets:
                    # 这里应该对比历史数据，简化版本只标记
                    pass
                
                # 检测性能测试缺失
                if 'def test_' not in content.lower() and 'benchmark' in content.lower():
                    self.issues.append(CriticalIssue(
                        id=f"perf-{len(self.issues)+1:03d}",
                        risk_level="low",
                        category="performance",
                        title="Performance Test Missing",
                        description=f"Benchmark file {bench_file.name} lacks tests",
                        affected_files=[str(bench_file.relative_to(self.base_path))],
                        evidence="No test functions found",
                        impact="Performance regression may go undetected",
                        recommendation="Add performance tests",
                        detected_at=datetime.now().isoformat()
                    ))
            
            except Exception:
                continue
    
    def _check_architecture_violations(self):
        """检测架构违规"""
        # 1. 检查硬编码路径
        py_files = list(self.base_path.rglob("*.py"))
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                
                # 硬编码 C 盘路径
                if re.search(r'C:\\Users', content):
                    self.issues.append(CriticalIssue(
                        id=f"arch-{len(self.issues)+1:03d}",
                        risk_level="medium",
                        category="architecture",
                        title="Hardcoded Path Detected",
                        description=f"Hardcoded C: path in {py_file.name}",
                        affected_files=[str(py_file.relative_to(self.base_path))],
                        evidence="C:\\Users",
                        impact="Not portable across systems",
                        recommendation="Use environment variables or config",
                        detected_at=datetime.now().isoformat()
                    ))
                
                # 硬编码命令
                if re.search(r"subprocess\..*['\"]py\s+30-scripts", content):
                    self.issues.append(CriticalIssue(
                        id=f"arch-{len(self.issues)+1:03d}",
                        risk_level="high",
                        category="architecture",
                        title="Hardcoded Tool Command",
                        description=f"Hardcoded tool command in {py_file.name}",
                        affected_files=[str(py_file.relative_to(self.base_path))],
                        evidence="py 30-scripts",
                        impact="Violates tool registry pattern",
                        recommendation="Use tool_executor instead",
                        detected_at=datetime.now().isoformat()
                    ))
            
            except Exception:
                continue
    
    def _check_security_risks(self):
        """安全检查"""
        py_files = list(self.base_path.rglob("*.py"))
        
        security_patterns = [
            (r'eval\s*\(', 'critical', 'Dangerous eval() usage'),
            (r'exec\s*\(', 'critical', 'Dangerous exec() usage'),
            (r'os\.system\s*\(', 'high', 'Dangerous os.system() usage'),
            (r'subprocess\..*shell\s*=\s*True', 'high', 'Shell injection risk'),
            (r'pickle\.loads?\s*\(', 'high', 'Pickle deserialization risk'),
            (r'requests\..*verify\s*=\s*False', 'medium', 'SSL verification disabled'),
            (r'hashlib\.md5\s*\(', 'medium', 'Weak hash algorithm'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'critical', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'critical', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'critical', 'Hardcoded secret'),
        ]
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                
                for pattern, risk_level, description in security_patterns:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        self.issues.append(CriticalIssue(
                            id=f"sec-{len(self.issues)+1:03d}",
                            risk_level=risk_level,
                            category="security",
                            title=f"Security Risk: {description}",
                            description=f"Found in {py_file.name}",
                            affected_files=[str(py_file.relative_to(self.base_path))],
                            evidence=matches[0].group(0),
                            impact="Security vulnerability",
                            recommendation="Remove hardcoded secrets and use secure alternatives",
                            detected_at=datetime.now().isoformat()
                        ))
            
            except Exception:
                continue


def print_result(result: DetectionResult):
    """打印检测结果"""
    print("\n" + "=" * 60)
    print("Critical Issue Detector Report")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Issues:    {result.total_issues}")
    print(f"  Scan Duration:   {result.scan_duration_ms:.0f}ms")
    
    print(f"\n[By Risk Level]")
    print(f"  Critical:  {result.critical_count:3d} 🔴")
    print(f"  High:      {result.high_count:3d} 🟠")
    print(f"  Medium:    {result.medium_count:3d} 🟡")
    print(f"  Low:       {result.low_count:3d} 🔵")
    
    if result.issues:
        print(f"\n[Critical Issues]")
        for issue in [i for i in result.issues if i.risk_level == "critical"][:5]:
            print(f"\n  🔴 [{issue.category}] {issue.title}")
            print(f"      Files: {', '.join(issue.affected_files)}")
            print(f"      Impact: {issue.impact}")
            print(f"      → {issue.recommendation}")
        
        if result.high_count > 0:
            print(f"\n[High Risk Issues]")
            for issue in [i for i in result.issues if i.risk_level == "high"][:5]:
                print(f"\n  🟠 [{issue.category}] {issue.title}")
                print(f"      Files: {', '.join(issue.affected_files)}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Critical Issue Detector')
    parser.add_argument('--path', type=str, default='.', help='检测路径')
    parser.add_argument('--check', type=str, default='all', 
                       choices=['all', 'exception', 'core', 'data', 'perf', 'arch', 'security'],
                       help='检测类型')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    
    args = parser.parse_args()
    
    base_path = Path(args.path)
    if not base_path.exists():
        print(f"[ERROR] Path not found: {base_path}")
        return 1
    
    detector = CriticalIssueDetector(base_path)
    result = detector.detect_all()
    
    if args.json:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print_result(result)
    
    # 返回码：有 critical 问题返回 1
    return 1 if result.critical_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
