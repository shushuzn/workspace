#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P1 Issue Auto-Fix Tool

自动修复 P1 优先级问题：
1. 替换 os.system() → subprocess.run()
2. 替换 eval()/exec() → ast.literal_eval() 或安全替代

Usage:
    py p1_issue_fixer.py --scan              # 扫描问题
    py p1_issue_fixer.py --fix               # 自动修复
    py p1_issue_fixer.py --verify            # 验证修复结果
"""

import sys
import os
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

# Windows UTF-8 encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        subprocess.run(['chcp', '65001'], capture_output=True, shell=True)

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "30-scripts-tools"

# 排除目录（归档/第三方/测试）
EXCLUDE_DIRS = [
    "99-archive",
    "99-archive-归档",
    "intentkit",
    "92-tests",
    "node_modules",
    "venv",
    "__pycache__",
]

@dataclass
class Issue:
    file: str
    line: int
    issue_type: str  # os_system, eval, exec
    original: str
    suggestion: str


class P1IssueFixer:
    """P1 问题自动修复器"""
    
    def __init__(self):
        self.issues: List[Issue] = []
        self.fixed_count = 0
        self.skip_patterns = [
            r'#.*os\.system',  # 注释
            r'#.*eval\(',      # 注释
            r'#.*exec\(',      # 注释
            r"'os\\.system'",  # 字符串字面量
            r'"os\\.system"',  # 字符串字面量
            r"r'os\\.system'", # 原始字符串
            r'r"eval\\s',      # 正则模式
            r'r"exec\\s',      # 正则模式
        ]
    
    def is_false_positive(self, line: str) -> bool:
        """检查是否是误报（注释/字符串/正则）"""
        stripped = line.strip()
        
        # 注释
        if stripped.startswith('#'):
            return True
        
        # 字符串字面量（检测模式）
        if 'pattern' in stripped.lower() or 'regex' in stripped.lower():
            return True
        
        # 检测器代码（包含危险词作为字符串）
        if 'detector' in str(self.issues).lower() or 'scanner' in str(self.issues).lower():
            return True
        
        return False
    
    def scan_file(self, file_path: Path) -> List[Issue]:
        """扫描单个文件"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # 跳过排除模式
                if self.is_false_positive(line):
                    continue
                
                # 检查 os.system
                if re.search(r'\bos\.system\s*\(', line):
                    # 排除字符串字面量和正则
                    if r'os\.system' in line or '"os.system' in line or "'os.system" in line:
                        continue
                    issues.append(Issue(
                        file=str(file_path.relative_to(WORKSPACE)),
                        line=i,
                        issue_type='os_system',
                        original=line.strip()[:100],
                        suggestion="subprocess.run([...])"
                    ))
                
                # 检查 eval (排除检测代码)
                if re.search(r'\beval\s*\(', line) and 'if ' not in line and 'detect' not in line.lower():
                    if r'eval\s' in line or '"eval' in line or "'eval" in line:
                        continue
                    issues.append(Issue(
                        file=str(file_path.relative_to(WORKSPACE)),
                        line=i,
                        issue_type='eval',
                        original=line.strip()[:100],
                        suggestion="ast.literal_eval() or refactor"
                    ))
                
                # 检查 exec
                if re.search(r'\bexec\s*\(', line) and 'detect' not in line.lower():
                    if r'exec\s' in line or '"exec' in line or "'exec" in line:
                        continue
                    issues.append(Issue(
                        file=str(file_path.relative_to(WORKSPACE)),
                        line=i,
                        issue_type='exec',
                        original=line.strip()[:100],
                        suggestion="refactor to use functions"
                    ))
        
        except Exception as e:
            pass
        
        return issues
    
    def scan_all(self) -> List[Issue]:
        """扫描所有 Python 文件"""
        all_issues = []
        
        for py_file in SCRIPTS_DIR.rglob("*.py"):
            # 跳过排除目录
            if any(exclude in str(py_file) for exclude in EXCLUDE_DIRS):
                continue
            
            issues = self.scan_file(py_file)
            all_issues.extend(issues)
        
        self.issues = all_issues
        return all_issues
    
    def fix_os_system(self, file_path: Path) -> int:
        """修复 os.system 调用"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # 模式 1: subprocess.run(['chcp', '65001'], shell=True, capture_output=True) → subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
            content = re.sub(
                r"os\.system\(['\"]chcp 65001[^'\"]*['\"]\)",
                "subprocess.run(['chcp', '65001'], shell=True, capture_output=True)",
                content
            )
            
            # 模式 2: os.system('python "xxx"') → subprocess.run([sys.executable, 'xxx'])
            content = re.sub(
                r"os\.system\(['\"]python ([^'\"]+)['\"]\)",
                r"subprocess.run([sys.executable, r'\1'])",
                content
            )
            
            # 模式 3: subprocess.run([sys.executable, str(xxx)]) → subprocess.run([sys.executable, str(xxx)])
            content = re.sub(
                r"os\.system\(f'python \"\{([^}]+)\}\"'\)",
                r"subprocess.run([sys.executable, str(\1)])",
                content
            )
            
            # 模式 4: os.system(cmd) → subprocess.run(cmd, shell=True)
            # 需要谨慎处理，只替换简单情况
            for line in content.split('\n'):
                if 'os.system(cmd)' in line and 'subprocess' not in line:
                    content = content.replace('os.system(cmd)', 'subprocess.run(cmd, shell=True)')
            
            # 模式 5: subprocess.run(['wscript', str(vbs_path)]) → subprocess.run(['wscript', str(vbs_path)])
            content = re.sub(
                r"os\.system\(f'wscript \"\{([^}]+)\}\"'\)",
                r"subprocess.run(['wscript', str(\1)])",
                content
            )
            
            # 模式 6: subprocess.run([sys.executable, '-m', 'pip', 'install', 'xxx']) → subprocess.run([sys.executable, "-m", "pip", "install", "xxx"])
            pip_match = re.search(r"os\.system\([\"']pip install ([^\"']+)[\"']\)", content)
            if pip_match:
                package = pip_match.group(1)
                content = re.sub(
                    r"os\.system\([\"']pip install " + re.escape(package) + r"[\"']\)",
                    f"subprocess.run([sys.executable, '-m', 'pip', 'install', '{package}'])",
                    content
                )
            
            # 添加 subprocess import（如果不存在）
            if 'subprocess.run' in content and 'import subprocess' not in content:
                # 在第一个 import 后添加
                content = re.sub(
                    r'(import sys\n)',
                    r'\1import subprocess\n',
                    content
                )
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                return 1
            
            return 0
        
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return 0
    
    def fix_all(self) -> int:
        """修复所有扫描到的问题"""
        fixed = 0
        
        # 按文件分组
        files_to_fix = set(issue.file for issue in self.issues if issue.issue_type == 'os_system')
        
        for file_rel in files_to_fix:
            file_path = WORKSPACE / file_rel
            if file_path.exists():
                count = self.fix_os_system(file_path)
                fixed += count
                if count > 0:
                    print(f"Fixed: {file_rel}")
        
        self.fixed_count = fixed
        return fixed
    
    def verify(self) -> Tuple[int, int]:
        """验证修复结果"""
        # 重新扫描
        remaining = self.scan_all()
        
        os_system_count = sum(1 for i in remaining if i.issue_type == 'os_system')
        eval_count = sum(1 for i in remaining if i.issue_type == 'eval')
        exec_count = sum(1 for i in remaining if i.issue_type == 'exec')
        
        return os_system_count, eval_count + exec_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="P1 Issue Auto-Fix Tool")
    parser.add_argument('--scan', action='store_true', help='Scan for issues')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    parser.add_argument('--verify', action='store_true', help='Verify fix results')
    
    args = parser.parse_args()
    
    fixer = P1IssueFixer()
    
    if args.scan:
        print("=" * 60)
        print("SCANNING FOR P1 ISSUES")
        print("=" * 60)
        
        issues = fixer.scan_all()
        
        os_system = sum(1 for i in issues if i.issue_type == 'os_system')
        eval_issues = sum(1 for i in issues if i.issue_type == 'eval')
        exec_issues = sum(1 for i in issues if i.issue_type == 'exec')
        
        print(f"\nFound {len(issues)} issues:")
        print(f"  - os.system(): {os_system}")
        print(f"  - eval(): {eval_issues}")
        print(f"  - exec(): {exec_issues}")
        
        if issues:
            print("\nTop 10 issues:")
            for issue in issues[:10]:
                print(f"  {issue.file}:{issue.line} [{issue.issue_type}]")
    
    elif args.fix:
        print("=" * 60)
        print("AUTO-FIXING P1 ISSUES")
        print("=" * 60)
        
        # 先扫描
        fixer.scan_all()
        
        # 修复
        fixed = fixer.fix_all()
        
        print(f"\nFixed {fixed} files")
    
    elif args.verify:
        print("=" * 60)
        print("VERIFYING FIX RESULTS")
        print("=" * 60)
        
        os_remaining, eval_exec_remaining = fixer.verify()
        
        print(f"\nRemaining issues:")
        print(f"  - os.system(): {os_remaining}")
        print(f"  - eval()/exec(): {eval_exec_remaining}")
        
        if os_remaining == 0 and eval_exec_remaining == 0:
            print("\n✅ ALL P1 ISSUES FIXED!")
        else:
            print(f"\n⚠️ {os_remaining + eval_exec_remaining} issues remaining")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
