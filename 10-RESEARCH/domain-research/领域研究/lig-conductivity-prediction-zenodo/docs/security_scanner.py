#!/usr/bin/env python3
"""
Security Scanner - 秘密扫描器
扫描代码库中的敏感信息 (API 密钥/密码/私钥等)

Usage:
    python security_scanner.py --scan
    python security_scanner.py --report
    python security_scanner.py --fix
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SecretFinding:
    """秘密发现"""
    file: str
    line: int
    type: str
    severity: str  # CRITICAL/HIGH/MEDIUM/LOW
    pattern: str
    context: str
    recommendation: str


class SecurityScanner:
    """安全扫描器"""

    # 秘密检测模式
    PATTERNS = {
        'api_key': {
            'regex': r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            'severity': 'CRITICAL',
            'recommendation': '使用环境变量存储 API 密钥，添加到 .gitignore'
        },
        'password': {
            'regex': r'(?:password|passwd|pwd)\s*[=:]\s*["\']?([^\s"\']{8,})["\']?',
            'severity': 'CRITICAL',
            'recommendation': '使用环境变量或密钥管理服务，不要硬编码密码'
        },
        'secret': {
            'regex': r'(?:secret|token)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            'severity': 'CRITICAL',
            'recommendation': '使用环境变量存储密钥，添加到 .gitignore'
        },
        'private_key': {
            'regex': r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
            'severity': 'CRITICAL',
            'recommendation': '私钥绝对不能提交到代码库，立即删除并轮换'
        },
        'aws_key': {
            'regex': r'(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}',
            'severity': 'CRITICAL',
            'recommendation': 'AWS 密钥泄露，立即轮换并使用 IAM 角色'
        },
        'github_token': {
            'regex': r'gh[pousr]_[A-Za-z0-9_]{36,}',
            'severity': 'CRITICAL',
            'recommendation': 'GitHub Token 泄露，立即撤销并重新生成'
        },
        'database_url': {
            'regex': r'(?:mysql|postgresql|mongodb|redis)://[^\s]+:[^\s]+@[^\s]+',
            'severity': 'HIGH',
            'recommendation': '数据库连接字符串包含密码，使用环境变量'
        },
        'email': {
            'regex': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'severity': 'LOW',
            'recommendation': '考虑使用占位符邮箱，避免暴露真实邮箱'
        },
        'ip_address': {
            'regex': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'severity': 'LOW',
            'recommendation': '检查是否为敏感 IP 地址，考虑使用占位符'
        },
        'hardcoded_path': {
            'regex': r'(?:C:\\|D:\\|/Users/)[^\s"\']+',
            'severity': 'MEDIUM',
            'recommendation': '使用 pathlib 和相对路径，避免硬编码绝对路径'
        },
    }

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.findings: List[SecretFinding] = []
        self.files_scanned = 0
        self.lines_scanned = 0

    def should_skip(self, path: Path) -> bool:
        """检查是否应该跳过该文件/目录"""

        skip_dirs = {
            '.git', 'node_modules', '__pycache__', 'venv', '.venv',
            'env', '.env', 'dist', 'build', '.idea', '.vscode',
            'models', 'data', 'cache', '.cache', 'tmp', 'temp'
        }

        skip_extensions = {
            '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin',
            '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.db', '.sqlite', '.sqlite3', '.pkl', '.pickle',
            '.gguf', '.bin', '.pt', '.pth', '.onnx'
        }

        # 跳过特定目录
        for part in path.parts:
            if part in skip_dirs:
                return True

        # 跳过特定扩展名
        if path.suffix.lower() in skip_extensions:
            return True

        # 跳过太大的文件
        try:
            if path.stat().st_size > 1024 * 1024:  # 1MB
                return True
        except:
            return True

        return False

    def scan_file(self, file_path: Path) -> List[SecretFinding]:
        """扫描单个文件"""

        findings = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return findings

        self.lines_scanned += len(lines)

        for line_num, line in enumerate(lines, 1):
            # 跳过注释和空行
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 检查每个模式
            for pattern_name, pattern_info in self.PATTERNS.items():
                try:
                    matches = re.finditer(pattern_info['regex'], line, re.IGNORECASE)

                    for match in matches:
                        # 跳过误报
                        if self.is_false_positive(line, pattern_name, match.group()):
                            continue

                        finding = SecretFinding(
                            file=str(file_path),
                            line=line_num,
                            type=pattern_name,
                            severity=pattern_info['severity'],
                            pattern=match.group(),
                            context=line.strip()[:100],
                            recommendation=pattern_info['recommendation']
                        )
                        findings.append(finding)
                except:
                    continue

        return findings

    def is_false_positive(self, line: str, pattern_name: str, match: str) -> bool:
        """检查是否为误报"""

        # 跳过示例/文档
        if 'example' in line.lower() or 'example' in match.lower():
            return True

        # 跳过占位符
        placeholders = ['your_', 'xxx', 'placeholder', 'dummy', 'fake', 'test_']
        if any(p in match.lower() for p in placeholders):
            return True

        # 跳过配置示例
        if 'config' in line.lower() and '=' in line:
            if 'YOUR_' in line or 'CHANGEME' in line:
                return True

        # 特定模式跳过
        if pattern_name == 'email':
            # 跳过文档中的邮箱
            if 'author' in line.lower() or 'contact' in line.lower():
                return True

        if pattern_name == 'ip_address':
            # 跳过 localhost 和常见 IP
            if match in ['127.0.0.1', '0.0.0.0', '255.255.255.255']:
                return True

        return False

    def scan_directory(self) -> List[SecretFinding]:
        """扫描整个目录"""

        print("\n" + "=" *80)
        print("🔍 安全扫描 - 秘密检测")
        print("=" *80)

        all_findings = []

        # 扫描 Python 文件和配置文件
        file_patterns = ['*.py', '*.json', '*.yaml', '*.yml', '*.env', '*.toml', '*.ini', '*.sh']

        files_to_scan = []
        for pattern in file_patterns:
            files_to_scan.extend(self.root_dir.rglob(pattern))

        # 添加 .env 文件
        files_to_scan.extend(self.root_dir.rglob('.env'))
        files_to_scan.extend(self.root_dir.rglob('.env.*'))

        for file_path in files_to_scan:
            if self.should_skip(file_path):
                continue

            self.files_scanned += 1
            findings = self.scan_file(file_path)
            all_findings.extend(findings)

            if findings:
                print(f"  ⚠️  {file_path}: {len(findings)} 个问题")

        self.findings = all_findings

        print(f"\n  扫描完成：{self.files_scanned} 文件，{self.lines_scanned} 行")
        print(f"  发现问题：{len(all_findings)} 个")

        return all_findings

    def get_statistics(self) -> Dict:
        """获取统计信息"""

        by_severity = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        by_type = {}

        for finding in self.findings:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
            by_type[finding.type] = by_type.get(finding.type, 0) + 1

        return {
            'total': len(self.findings),
            'by_severity': by_severity,
            'by_type': by_type,
            'files_scanned': self.files_scanned,
            'lines_scanned': self.lines_scanned,
            'scan_time': datetime.now().isoformat()
        }

    def generate_report(self, output_file: str = "data/security_scan_report.json"):
        """生成扫描报告"""

        report = {
            'scan_time': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'findings': [asdict(f) for f in self.findings]
        }

        # 确保目录存在
        Path(output_file).parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n  报告保存到：{output_file}")

        return report

    def print_summary(self):
        """打印摘要"""

        stats = self.get_statistics()

        print("\n" + "=" *80)
        print("📊 安全扫描摘要")
        print("=" *80)

        print(f"\n  扫描范围:")
        print(f"    文件数：{stats['files_scanned']}")
        print(f"    代码行数：{stats['lines_scanned']}")

        print(f"\n  发现问题:")
        print(f"    总计：{stats['total']} 个")

        print(f"\n  按严重程度:")
        for severity, count in stats['by_severity'].items():
            if count > 0:
                emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}[severity]
                print(f"    {emoji} {severity}: {count} 个")

        if stats['by_type']:
            print(f"\n  按类型:")
            for type_name, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"    {type_name}: {count} 个")

        print("\n" + "=" *80)

        if stats['by_severity']['CRITICAL'] > 0:
            print("\n🚨 发现严重安全问题！请立即处理！")
        elif stats['by_severity']['HIGH'] > 0:
            print("\n⚠️  发现高风险问题，建议尽快处理！")
        elif stats['total'] > 0:
            print("\nℹ️  发现一些安全问题，建议审查！")
        else:
            print("\n✅ 未发现明显安全问题！")

        print("\n" + "=" *80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='安全扫描器 - 秘密检测')
    parser.add_argument('--scan', action='store_true', help='扫描代码库')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--fix', action='store_true', help='提供修复建议')
    parser.add_argument('--dir', type=str, default='.', help='扫描目录')

    args = parser.parse_args()

    scanner = SecurityScanner(args.dir)

    if args.scan or not (args.report or args.fix):
        scanner.scan_directory()
        scanner.print_summary()

    if args.report:
        scanner.generate_report()

    if args.fix:
        scanner.print_summary()
        print("\n💡 修复建议:")
        print("  1. 立即删除所有硬编码的秘密")
        print("  2. 使用环境变量存储敏感信息")
        print("  3. 将 .env 文件添加到 .gitignore")
        print("  4. 轮换所有已泄露的密钥")
        print("  5. 安装 pre-commit hook 自动扫描")


if __name__ == "__main__":
    main()
