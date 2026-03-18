#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue Scanner - 问题扫描器 (Auto-Critic v7.0 组件)

主动扫描各类问题，填补管控盲区。

功能:
1. 扫描执行日志中的警告/错误
2. 静态代码分析 (pylint/flake8)
3. 提取编译器告警
4. 统计 TODO/FIXME 注释
5. 检测代码异味 (code smells)

使用:
    py issue_scanner.py --path "30-scripts-tools" --level all
    py issue_scanner.py --path "." --level critical --json
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class IssueLevel(Enum):
    """问题级别"""
    CRITICAL = "critical"  # 致命
    MAJOR = "major"        # 严重
    MINOR = "minor"        # 一般
    INFO = "info"          # 提示


@dataclass
class Issue:
    """问题记录"""
    id: str
    level: str
    category: str
    file: str
    line: int
    message: str
    evidence: str
    suggestion: str
    timestamp: str


@dataclass
class ScanResult:
    """扫描结果"""
    total_issues: int
    critical_count: int
    major_count: int
    minor_count: int
    info_count: int
    issues: List[Issue]
    scan_duration_ms: float
    files_scanned: int
    timestamp: str


class IssueScanner:
    """问题扫描器"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.issues = []
    
    def scan_all(self) -> ScanResult:
        """执行全量扫描"""
        start_time = datetime.now()
        
        # 1. 扫描日志文件
        self._scan_logs()
        
        # 2. 静态代码分析
        self._run_pylint()
        self._run_flake8()
        
        # 3. 提取 TODO/FIXME
        self._scan_todo_comments()
        
        # 4. 检测代码异味
        self._detect_code_smells()
        
        # 5. 安全检查
        self._security_scan()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        # 统计
        critical = sum(1 for i in self.issues if i.level == "critical")
        major = sum(1 for i in self.issues if i.level == "major")
        minor = sum(1 for i in self.issues if i.level == "minor")
        info = sum(1 for i in self.issues if i.level == "info")
        
        return ScanResult(
            total_issues=len(self.issues),
            critical_count=critical,
            major_count=major,
            minor_count=minor,
            info_count=info,
            issues=self.issues,
            scan_duration_ms=round(duration, 2),
            files_scanned=self._count_files(),
            timestamp=datetime.now().isoformat()
        )
    
    def _scan_logs(self):
        """扫描日志文件"""
        log_patterns = ['*.log', '*-log.json', 'workflow-execution-log.json']
        
        for pattern in log_patterns:
            for log_file in self.base_path.rglob(pattern):
                try:
                    content = log_file.read_text(encoding='utf-8', errors='replace')
                    
                    # 检测错误
                    for match in re.finditer(r'(ERROR|Exception|Traceback|Failed|Failure)', content, re.IGNORECASE):
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues.append(Issue(
                            id=f"log-{len(self.issues)+1:03d}",
                            level="major",
                            category="log",
                            file=str(log_file.relative_to(self.base_path)),
                            line=line_num,
                            message=f"Error detected in log: {match.group()}",
                            evidence=content[match.start():match.start()+100],
                            suggestion="Review log for root cause",
                            timestamp=datetime.now().isoformat()
                        ))
                    
                    # 检测警告
                    for match in re.finditer(r'(WARNING|WARN|Deprecated)', content, re.IGNORECASE):
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues.append(Issue(
                            id=f"log-{len(self.issues)+1:03d}",
                            level="minor",
                            category="log",
                            file=str(log_file.relative_to(self.base_path)),
                            line=line_num,
                            message=f"Warning detected in log: {match.group()}",
                            evidence=content[match.start():match.start()+100],
                            suggestion="Review warning",
                            timestamp=datetime.now().isoformat()
                        ))
                
                except Exception as e:
                    continue
    
    def _run_pylint(self):
        """运行 pylint"""
        py_files = list(self.base_path.rglob("*.py"))
        
        for py_file in py_files[:20]:  # 限制文件数
            try:
                result = subprocess.run(
                    ['pylint', '--errors-only', str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    for line in result.stdout.split('\n'):
                        match = re.search(r':(\d+):\d+:.*?(E\d+):(.+)', line)
                        if match:
                            self.issues.append(Issue(
                                id=f"pylint-{len(self.issues)+1:03d}",
                                level="major",
                                category="pylint",
                                file=str(py_file.relative_to(self.base_path)),
                                line=int(match.group(1)),
                                message=f"Pylint error: {match.group(3).strip()}",
                                evidence=line,
                                suggestion="Fix pylint error",
                                timestamp=datetime.now().isoformat()
                            ))
            
            except Exception:
                continue
    
    def _run_flake8(self):
        """运行 flake8"""
        try:
            result = subprocess.run(
                ['flake8', '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics', str(self.base_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for line in result.stdout.split('\n'):
                match = re.search(r':(\d+):\d+:\s*(\w+\d+):\s*(.+)', line)
                if match:
                    self.issues.append(Issue(
                        id=f"flake8-{len(self.issues)+1:03d}",
                        level="major",
                        category="flake8",
                        file=line.split(':')[0],
                        line=int(match.group(1)),
                        message=f"Flake8 error: {match.group(3).strip()}",
                        evidence=line,
                        suggestion="Fix flake8 error",
                        timestamp=datetime.now().isoformat()
                    ))
        
        except Exception:
            pass
    
    def _scan_todo_comments(self):
        """扫描 TODO/FIXME 注释"""
        py_files = list(self.base_path.rglob("*.py"))
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # TODO
                    match = re.search(r'#\s*(TODO|FIXME|XXX|HACK)[:\s]*(.+)', line, re.IGNORECASE)
                    if match:
                        self.issues.append(Issue(
                            id=f"todo-{len(self.issues)+1:03d}",
                            level="minor",
                            category="todo",
                            file=str(py_file.relative_to(self.base_path)),
                            line=i,
                            message=f"{match.group(1)}: {match.group(2).strip()}",
                            evidence=line.strip(),
                            suggestion=f"Resolve {match.group(1).lower()}",
                            timestamp=datetime.now().isoformat()
                        ))
            
            except Exception:
                continue
    
    def _detect_code_smells(self):
        """检测代码异味"""
        py_files = list(self.base_path.rglob("*.py"))
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                lines = content.split('\n')
                
                # 1. 过长函数 (>50 行)
                func_pattern = r'^\s*def\s+(\w+)\s*\('
                current_func = None
                func_start = 0
                
                for i, line in enumerate(lines, 1):
                    match = re.match(func_pattern, line)
                    if match:
                        if current_func and (i - func_start) > 50:
                            self.issues.append(Issue(
                                id=f"smell-{len(self.issues)+1:03d}",
                                level="minor",
                                category="code_smell",
                                file=str(py_file.relative_to(self.base_path)),
                                line=func_start,
                                message=f"Function '{current_func}' is too long ({i - func_start} lines)",
                                evidence=f"def {current_func}(...)",
                                suggestion="Refactor into smaller functions",
                                timestamp=datetime.now().isoformat()
                            ))
                        current_func = match.group(1)
                        func_start = i
                
                # 2. 过长行 (>120 字符)
                for i, line in enumerate(lines, 1):
                    if len(line) > 120 and not line.strip().startswith('#'):
                        self.issues.append(Issue(
                            id=f"smell-{len(self.issues)+1:03d}",
                            level="info",
                            category="code_smell",
                            file=str(py_file.relative_to(self.base_path)),
                            line=i,
                            message=f"Line too long ({len(line)} characters)",
                            evidence=line[:80] + "...",
                            suggestion="Break into multiple lines",
                            timestamp=datetime.now().isoformat()
                        ))
                
                # 3. 重复导入
                imports = re.findall(r'^(import\s+\S+|from\s+\S+\s+import\s+\S+)', content, re.MULTILINE)
                import_counts = {}
                for imp in imports:
                    import_counts[imp] = import_counts.get(imp, 0) + 1
                
                for imp, count in import_counts.items():
                    if count > 1:
                        self.issues.append(Issue(
                            id=f"smell-{len(self.issues)+1:03d}",
                            level="minor",
                            category="code_smell",
                            file=str(py_file.relative_to(self.base_path)),
                            line=0,
                            message=f"Duplicate import: {imp} ({count} times)",
                            evidence=imp,
                            suggestion="Remove duplicate imports",
                            timestamp=datetime.now().isoformat()
                        ))
            
            except Exception:
                continue
    
    def _security_scan(self):
        """安全检查"""
        py_files = list(self.base_path.rglob("*.py"))
        
        security_patterns = [
            (r'eval\s*\(', 'Use of eval() is dangerous'),
            (r'exec\s*\(', 'Use of exec() is dangerous'),
            (r'os\.system\s*\(', 'Use of os.system() is dangerous'),
            (r'subprocess\..*shell\s*=\s*True', 'Shell injection risk'),
            (r'pickle\.loads?\s*\(', 'Pickle deserialization risk'),
            (r'requests\..*verify\s*=\s*False', 'SSL verification disabled'),
            (r'hashlib\.md5\s*\(', 'Weak hash algorithm (MD5)'),
        ]
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                
                for pattern, message in security_patterns:
                    for match in re.finditer(pattern, content):
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues.append(Issue(
                            id=f"security-{len(self.issues)+1:03d}",
                            level="critical",
                            category="security",
                            file=str(py_file.relative_to(self.base_path)),
                            line=line_num,
                            message=message,
                            evidence=match.group(0),
                            suggestion="Use safer alternative",
                            timestamp=datetime.now().isoformat()
                        ))
            
            except Exception:
                continue
    
    def _count_files(self) -> int:
        """统计扫描文件数"""
        return len(list(self.base_path.rglob("*.py")))


def print_result(result: ScanResult):
    """打印扫描结果"""
    print("\n" + "=" * 60)
    print("Issue Scanner Report")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Issues:    {result.total_issues}")
    print(f"  Files Scanned:   {result.files_scanned}")
    print(f"  Scan Duration:   {result.scan_duration_ms:.0f}ms")
    
    print(f"\n[By Level]")
    print(f"  Critical:  {result.critical_count:3d} 🔴")
    print(f"  Major:     {result.major_count:3d} 🟠")
    print(f"  Minor:     {result.minor_count:3d} 🟡")
    print(f"  Info:      {result.info_count:3d} 🔵")
    
    if result.issues:
        print(f"\n[Top Issues]")
        for issue in result.issues[:10]:
            level_icon = {'critical': '🔴', 'major': '🟠', 'minor': '🟡', 'info': '🔵'}.get(issue.level, '⚪')
            print(f"\n  {level_icon} [{issue.category}] {issue.file}:{issue.line}")
            print(f"      {issue.message}")
            if issue.suggestion:
                print(f"      → {issue.suggestion}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Issue Scanner')
    parser.add_argument('--path', type=str, default='.', help='扫描路径')
    parser.add_argument('--level', type=str, default='all', 
                       choices=['all', 'critical', 'major', 'minor', 'info'],
                       help='最低级别')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    
    args = parser.parse_args()
    
    base_path = Path(args.path)
    if not base_path.exists():
        print(f"[ERROR] Path not found: {base_path}")
        return 1
    
    scanner = IssueScanner(base_path)
    result = scanner.scan_all()
    
    # 过滤级别
    level_order = {'critical': 0, 'major': 1, 'minor': 2, 'info': 3}
    min_level = level_order.get(args.level, 0)
    filtered_issues = [i for i in result.issues if level_order.get(i.level, 3) >= min_level]
    result.issues = filtered_issues
    result.total_issues = len(filtered_issues)
    
    if args.json:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print_result(result)
    
    # 返回码：有 critical 问题返回 1
    return 1 if result.critical_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
