#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Pre-Check - Git 提交前检查工具

在 git commit 前手动运行检查，提前发现问题。

功能:
- 编码检查 (UTF-8, 无 BOM)
- 敏感信息扫描 (.env, API 密钥)
- 报告文件阻止 (*-report-*.md)
- 大文件检测 (>50MB)
- 中文文件名警告 (研究目录除外)
- 嵌套备份检测 (>2 层)
- 重复文件检测 (_from_ 模式)

使用:
  py git-precheck.py              # 检查暂存区文件
  py git-precheck.py --all        # 检查工作区所有文件
  py git-precheck.py --file X.py  # 检查指定文件
  py git-precheck.py --quick      # 快速检查 (仅关键项)
  py git-precheck.py --verbose    # 详细输出

安装 Git Hook:
  py install-git-hooks.py
"""

import subprocess
import sys
import os
import io
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Paths
WORKSPACE = Path(__file__).parent.parent
WORKSPACE_NAME = 'workspace'

# 报告文件关键词（命中即阻止）
BLOCKED_PATTERNS = [
    '-report-',
    'operations-report',
    'multi-persona',
    'brainstorm',
    'file-organization-plan',
    '-cleanup-',
    '-scan-',
]

# 白名单（允许的文件）
WHITELIST = [
    'README.md',
    'INDEX.md',
    '.gitignore',
    'GUIDE.md',  # 新增：允许 GUIDE 文件
]

# 敏感文件模式
SENSITIVE_PATTERNS = [
    '.env',
    'aliyun',
    'access_key',
    'secret',
    '.tiff',
]

# 备份目录（禁止自动修改）
BACKUP_DIRECTORIES = [
    '99-backups/',
    'backups/',
    '.backup/',
    '_backup/',
]

# 嵌套备份检测（路径深度>5 层）
MAX_PATH_DEPTH = 5

# 允许中文文件名的目录
ALLOW_CHINESE_PATH = [
    '10-RESEARCH/',
    '99-archive/',
    '90-TESTS/',
    '06-research/',
]

# 文本文件扩展名
TEXT_EXTENSIONS = [
    '.py', '.md', '.txt', '.json', '.yaml', '.yml',
    '.js', '.ts', '.tsx', '.jsx', '.vue', '.html', '.css',
    '.sh', '.bat', '.cmd', '.ps1',
]

# 二进制文件扩展名
BINARY_EXTENSIONS = [
    '.png', '.jpg', '.jpeg', '.gif', '.ico',
    '.pdf', '.zip', '.tar', '.gz',
    '.pyc', '.pyo', '.so', '.dll',
]


class PreCheckResult:
    """检查结果"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.skipped = 0
        self.errors = []
        self.warnings_list = []
        self.details = {}
    
    def add_error(self, category: str, message: str):
        self.errors.append({'category': category, 'message': message})
        self.failed += 1
    
    def add_warning(self, category: str, message: str):
        self.warnings_list.append({'category': category, 'message': message})
        self.warnings += 1
    
    def add_passed(self, category: str):
        self.passed += 1
    
    def add_skipped(self, category: str):
        self.skipped += 1
    
    def summary(self) -> str:
        total = self.passed + self.failed + self.warnings + self.skipped
        if self.failed > 0:
            status = '❌ FAILED'
        elif self.warnings > 0:
            status = '⚠️  WARNINGS'
        else:
            status = '✅ PASSED'
        
        return f"{status} (通过:{self.passed}, 失败:{self.failed}, 警告:{self.warnings}, 跳过:{self.skipped})"


def get_staged_files() -> List[str]:
    """获取暂存区文件列表"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            cwd=WORKSPACE,
            shell=True
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except Exception as e:
        print(f"❌ 获取暂存文件失败：{e}")
        return []


def get_all_files(directory: Path = None) -> List[str]:
    """获取工作区所有文件"""
    if directory is None:
        directory = WORKSPACE
    
    files = []
    for root, dirs, filenames in os.walk(directory):
        # 跳过隐藏目录和备份目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['99-backups', '__pycache__', 'node_modules']]
        
        for filename in filenames:
            if not filename.startswith('.'):
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(WORKSPACE)
                files.append(str(rel_path))
    
    return files


def is_binary_file(file_path: str) -> bool:
    """判断是否为二进制文件"""
    ext = Path(file_path).suffix.lower()
    return ext in BINARY_EXTENSIONS


def check_encoding(file_path: Path) -> Tuple[str, str]:
    """检查文件编码"""
    full_path = WORKSPACE / file_path
    
    if not full_path.exists():
        return 'SKIP', '文件不存在'
    
    if is_binary_file(str(file_path)):
        return 'SKIP', '二进制文件'
    
    try:
        # 检查 BOM 头
        with open(full_path, 'rb') as f:
            bom = f.read(3)
            if bom == b'\xef\xbb\xbf':
                return 'ERROR', 'BOM 头 (应使用 UTF-8 without BOM)'
        
        # 尝试用 UTF-8 读取
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                f.read()
            return 'OK', 'UTF-8 验证通过'
        except UnicodeDecodeError:
            return 'ERROR', '编码错误：无法用 UTF-8 读取'
        
    except Exception as e:
        return 'ERROR', f'检查失败：{str(e)}'


def check_chinese_filename(file_path: str) -> Tuple[str, str]:
    """检查中文文件名"""
    for allowed_path in ALLOW_CHINESE_PATH:
        if file_path.startswith(allowed_path):
            return 'OK', '允许目录'
    
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_path)
    
    if has_chinese:
        return 'WARNING', f'中文文件名：{file_path} (建议英文)'
    
    return 'OK', None


def check_nested_backup(file_path: str) -> Tuple[str, str]:
    """检测嵌套备份目录"""
    # 计算路径深度
    parts = file_path.replace('\\', '/').split('/')
    
    # 检测是否包含备份目录关键词
    backup_keywords = ['backup', 'backups', '_backup', '.backup']
    depth = 0
    for part in parts:
        if any(kw in part.lower() for kw in backup_keywords):
            depth += 1
    
    # 如果备份目录出现>2 次，说明是嵌套
    if depth > 2:
        return 'BLOCKED', f'嵌套备份目录 (深度={depth}): {file_path}'
    
    # 检测路径深度
    if len(parts) > MAX_PATH_DEPTH and any(kw in file_path.lower() for kw in backup_keywords):
        return 'BLOCKED', f'备份目录路径过深 (深度={len(parts)}): {file_path}'
    
    return 'OK', None


def check_duplicate_from_file(file_path: str) -> Tuple[str, str]:
    """检测 _from_ 重复文件"""
    if '_from_' in file_path:
        return 'BLOCKED', f'重复文件 (_from_): {file_path}'
    
    return 'OK', None


def check_large_file(file_path: Path) -> Tuple[str, str]:
    """检测大文件 (>50MB)"""
    full_path = WORKSPACE / file_path
    
    if not full_path.exists():
        return 'OK', None
    
    try:
        size_mb = full_path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            return 'BLOCKED', f'大文件 ({size_mb:.1f}MB > 50MB): {file_path}'
    except:
        pass
    
    return 'OK', None


def check_file(file_path: str) -> Tuple[str, str]:
    """检查单个文件（报告 + 敏感）"""
    # 检查敏感文件
    for pattern in SENSITIVE_PATTERNS:
        if pattern.lower() in file_path.lower():
            return 'BLOCKED', f'敏感文件：{file_path}'
    
    # 检查 21-reports/ 目录
    if file_path.startswith('21-reports/'):
        # 白名单检查
        for allowed in WHITELIST:
            if allowed in file_path:
                return 'OK', None
        
        # 阻止模式检查
        for pattern in BLOCKED_PATTERNS:
            if pattern in file_path.lower():
                return 'BLOCKED', f'自动生成报告：{file_path}'
        
        # 其他报告文件警告
        return 'WARNED', f'21-reports 新增：{file_path}'
    
    # 检查所有目录的报告文件（全局阻止）
    filename_lower = file_path.lower()
    if '-report-' in filename_lower and filename_lower.endswith('.md'):
        # 排除白名单
        for allowed in WHITELIST:
            if allowed in file_path:
                return 'OK', None
        return 'BLOCKED', f'自动生成报告 (全局): {file_path}'
    
    # 阻止 *-test-report-*.md 模式
    if 'test-report' in filename_lower and filename_lower.endswith('.md'):
        return 'BLOCKED', f'测试报告 (应删除): {file_path}'
    
    return 'OK', None


def run_checks(files: List[str], quick: bool = False) -> PreCheckResult:
    """运行所有检查"""
    result = PreCheckResult()
    
    blocked_files = []
    warned_files = []
    encoding_errors = []
    filename_warnings = []
    nested_backups = []
    duplicate_files = []
    large_files = []
    
    for file_path in files:
        # 检查报告文件 + 敏感文件
        status, message = check_file(file_path)
        if status == 'BLOCKED':
            blocked_files.append(message)
            result.add_error('报告/敏感文件', message)
        elif status == 'WARNED':
            warned_files.append(message)
            result.add_warning('报告/敏感文件', message)
        else:
            result.add_passed('报告/敏感文件')
        
        # 检查嵌套备份
        status, message = check_nested_backup(file_path)
        if status == 'BLOCKED':
            nested_backups.append(message)
            result.add_error('嵌套备份', message)
        else:
            result.add_passed('嵌套备份')
        
        # 检查重复文件 (_from_)
        status, message = check_duplicate_from_file(file_path)
        if status == 'BLOCKED':
            duplicate_files.append(message)
            result.add_error('重复文件', message)
        else:
            result.add_passed('重复文件')
        
        # 检查大文件
        if not quick:
            status, message = check_large_file(Path(file_path))
            if status == 'BLOCKED':
                large_files.append(message)
                result.add_error('大文件', message)
            else:
                result.add_passed('大文件')
        
        # 检查编码 (跳过二进制文件)
        if not quick and not is_binary_file(file_path):
            status, message = check_encoding(Path(file_path))
            if status == 'ERROR':
                encoding_errors.append(f"[编码] {file_path}: {message}")
                result.add_error('编码', f"{file_path}: {message}")
            else:
                result.add_passed('编码')
        
        # 检查中文文件名
        status, message = check_chinese_filename(file_path)
        if status == 'WARNING':
            filename_warnings.append(message)
            result.add_warning('中文文件名', message)
        else:
            result.add_passed('中文文件名')
    
    return result


def print_report(result: PreCheckResult, files: List[str]):
    """打印检查报告"""
    print()
    print("=" * 70)
    print("  Git Pre-Check 报告")
    print("=" * 70)
    print()
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"检查文件：{len(files)} 个")
    print()
    
    # 总体状态
    print("【总体状态】")
    print(f"  {result.summary()}")
    print()
    
    # 错误详情
    if result.errors:
        print("【❌ 错误】必须修复后才能提交")
        print()
        
        # 按类别分组
        by_category = {}
        for error in result.errors:
            cat = error['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(error['message'])
        
        for category, messages in by_category.items():
            print(f"  {category} ({len(messages)} 个):")
            for msg in messages[:5]:
                print(f"    - {msg}")
            if len(messages) > 5:
                print(f"    ... 还有 {len(messages)-5} 个")
            print()
        
        print("  解决方案:")
        print("    1. 删除文件：git reset HEAD <file> && rm <file>")
        print("    2. 修复编码：用 VSCode 打开 → 另存为 UTF-8")
        print("    3. 或强制提交：git commit --no-verify (不推荐)")
        print()
    
    # 警告详情
    if result.warnings_list:
        print("【⚠️  警告】建议修复，但可强制提交")
        print()
        for warning in result.warnings_list[:10]:
            print(f"    - {warning['message']}")
        if len(result.warnings_list) > 10:
            print(f"    ... 还有 {len(result.warnings_list)-10} 个警告")
        print()
        print("  强制提交：git commit --no-verify")
        print()
    
    # 成功信息
    if result.failed == 0:
        print("【✅ 检查通过】可以安全提交")
        print()
        print("  提交命令：git commit -m \"你的提交消息\"")
        print()
    
    print("=" * 70)


def save_report(result: PreCheckResult, files: List[str], output_file: str = None):
    """保存检查报告到文件"""
    if output_file is None:
        output_file = 'pre-check-report.json'
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'files_checked': len(files),
        'summary': {
            'passed': result.passed,
            'failed': result.failed,
            'warnings': result.warnings,
            'skipped': result.skipped
        },
        'errors': result.errors,
        'warnings': result.warnings_list
    }
    
    output_path = WORKSPACE / '20-data-reports' / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 报告已保存：{output_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Pre-Check - 提交前检查工具')
    parser.add_argument('--all', action='store_true', help='检查工作区所有文件')
    parser.add_argument('--file', type=str, help='检查指定文件')
    parser.add_argument('--quick', action='store_true', help='快速检查 (仅关键项)')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument('--save', type=str, help='保存报告到文件')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    # 获取文件列表
    if args.file:
        files = [args.file]
        mode = '单文件检查'
    elif args.all:
        files = get_all_files()
        mode = '全工作区检查'
    else:
        files = get_staged_files()
        mode = '暂存区检查'
    
    if not files:
        print("⚠️  没有文件需要检查")
        if not args.all and not args.file:
            print("提示：先 git add 文件，或运行 --all 检查所有文件")
        return 0
    
    # 运行检查
    result = run_checks(files, quick=args.quick)
    
    # 输出结果
    if args.json:
        print(json.dumps({
            'mode': mode,
            'files': len(files),
            'summary': {
                'passed': result.passed,
                'failed': result.failed,
                'warnings': result.warnings,
                'skipped': result.skipped
            },
            'errors': result.errors,
            'warnings': result.warnings_list
        }, indent=2, ensure_ascii=False))
    else:
        print_report(result, files)
    
    # 保存报告
    if args.save:
        save_report(result, files, args.save)
    
    # 返回码
    return 1 if result.failed > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
