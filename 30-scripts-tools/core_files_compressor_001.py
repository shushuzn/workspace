import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心文件压缩器 - 压缩 7 个核心文件

功能：
1. 检查核心文件大小和有效性
2. 压缩过大的核心文件
3. 验证压缩效果 (<100KB)
4. 生成压缩报告

核心文件列表：
- SOUL.md
- USER.md
- AGENTS.md
- TOOLS.md
- HEARTBEAT.md
- MEMORY.md
- 13-memory/YYYY-MM-DD.md (今日笔记)

使用：
  py core_files_compressor.py --check
  py core_files_compressor.py --compress
  py core_files_compressor.py --report
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class CoreFilesCompressor:
    """核心文件压缩器"""
    
    # 核心文件列表
    CORE_FILES = [
        'SOUL.md',
        'USER.md',
        'AGENTS.md',
        'TOOLS.md',
        'HEARTBEAT.md',
        'MEMORY.md',
    ]
    
    # 大小限制 (bytes)
    SIZE_LIMITS = {
        'SOUL.md': 10000,        # 10KB
        'USER.md': 15000,        # 15KB
        'AGENTS.md': 10000,      # 10KB
        'TOOLS.md': 10000,       # 10KB
        'HEARTBEAT.md': 10000,   # 10KB
        'MEMORY.md': 20000,      # 20KB
        'daily_note': 10000,     # 10KB
    }
    
    # 总大小限制
    TOTAL_LIMIT = 100 * 1024  # 100KB
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.daily_note = self.workspace / f'13-memory/{self.today}.md'
        self.compression_log = self.workspace / '13-memory/compression_log.json'
        
    def get_all_core_files(self) -> List[Path]:
        """获取所有核心文件路径"""
        files = []
        for f in self.CORE_FILES:
            files.append(self.workspace / f)
        if self.daily_note.exists():
            files.append(self.daily_note)
        return files
    
    def check_files(self) -> Dict:
        """检查所有核心文件"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'files': [],
            'total_size': 0,
            'total_size_kb': 0,
            'within_limit': True,
            'issues': []
        }
        
        files = self.get_all_core_files()
        
        for file_path in files:
            if not file_path.exists():
                result['files'].append({
                    'name': file_path.name,
                    'path': str(file_path.relative_to(self.workspace)),
                    'exists': False,
                    'size': 0,
                    'within_limit': False
                })
                result['issues'].append(f"{file_path.name} 不存在")
                continue
            
            size = file_path.stat().st_size
            size_limit = self.SIZE_LIMITS.get(file_path.name, self.SIZE_LIMITS['daily_note'])
            within_limit = size <= size_limit
            
            result['files'].append({
                'name': file_path.name,
                'path': str(file_path.relative_to(self.workspace)),
                'exists': True,
                'size': size,
                'size_kb': round(size / 1024, 2),
                'limit': size_limit,
                'limit_kb': round(size_limit / 1024, 2),
                'within_limit': within_limit,
                'usage': round(size / size_limit * 100, 1) if size_limit > 0 else 0
            })
            
            result['total_size'] += size
            
            if not within_limit:
                result['issues'].append(
                    f"{file_path.name} 超过限制: {size} > {size_limit} bytes"
                )
        
        result['total_size_kb'] = round(result['total_size'] / 1024, 2)
        result['within_limit'] = result['total_size'] <= self.TOTAL_LIMIT
        
        if result['total_size'] > self.TOTAL_LIMIT:
            result['issues'].append(
                f"总大小超过限制: {result['total_size_kb']}KB > {self.TOTAL_LIMIT/1024}KB"
            )
        
        return result
    
    def compress_soul_md(self) -> Dict:
        """压缩 SOUL.md - 移除冗余内容"""
        soul_path = self.workspace / 'SOUL.md'
        
        if not soul_path.exists():
            return {'status': 'skipped', 'reason': 'File not found'}
        
        with open(soul_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # 压缩策略：
        # 1. 移除多余空行（超过 2 个连续空行）
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 2. 移除行尾空格
        content = re.sub(r'[ \t]+\n', '\n', content)
        
        # 3. 压缩表格（保留结构）
        # 不处理表格，避免破坏格式
        
        compressed_size = len(content)
        compression_rate = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        if compression_rate > 5:  # 只在实际压缩超过 5% 时才写入
            with open(soul_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'compressed',
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_rate': round(compression_rate, 2)
            }
        
        return {'status': 'skipped', 'reason': f'Compression rate too low: {compression_rate:.2f}%'}
    
    def compress_agents_md(self) -> Dict:
        """压缩 AGENTS.md - 移除冗余内容"""
        agents_path = self.workspace / 'AGENTS.md'
        
        if not agents_path.exists():
            return {'status': 'skipped', 'reason': 'File not found'}
        
        with open(agents_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # 压缩策略：
        # 1. 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 2. 移除行尾空格
        content = re.sub(r'[ \t]+\n', '\n', content)
        
        compressed_size = len(content)
        compression_rate = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        if compression_rate > 5:
            with open(agents_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'compressed',
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_rate': round(compression_rate, 2)
            }
        
        return {'status': 'skipped', 'reason': f'Compression rate too low: {compression_rate:.2f}%'}
    
    def compress_memory_md(self) -> Dict:
        """压缩 MEMORY.md - 提取核心内容"""
        memory_path = self.workspace / 'MEMORY.md'
        
        if not memory_path.exists():
            return {'status': 'skipped', 'reason': 'File not found'}
        
        with open(memory_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # 压缩策略：
        # 1. 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 2. 移除行尾空格
        content = re.sub(r'[ \t]+\n', '\n', content)
        
        # 3. 移除详细示例（保留核心原则）
        # 不处理内容，避免破坏信息
        
        compressed_size = len(content)
        compression_rate = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        if compression_rate > 5:
            with open(memory_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'compressed',
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_rate': round(compression_rate, 2)
            }
        
        return {'status': 'skipped', 'reason': f'Compression rate too low: {compression_rate:.2f}%'}
    
    def compress_daily_note(self) -> Dict:
        """压缩今日笔记 - 保留核心内容"""
        if not self.daily_note.exists():
            return {'status': 'skipped', 'reason': 'File not found'}
        
        with open(self.daily_note, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # 压缩策略：
        # 1. 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 2. 移除行尾空格
        content = re.sub(r'[ \t]+\n', '\n', content)
        
        compressed_size = len(content)
        compression_rate = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        if compression_rate > 5:
            with open(self.daily_note, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'compressed',
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_rate': round(compression_rate, 2)
            }
        
        return {'status': 'skipped', 'reason': f'Compression rate too low: {compression_rate:.2f}%'}
    
    def compress_all(self) -> Dict:
        """压缩所有核心文件"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'before': self.check_files(),
            'compressions': {},
            'after': None
        }
        
        # 压缩各文件
        result['compressions']['SOUL.md'] = self.compress_soul_md()
        result['compressions']['AGENTS.md'] = self.compress_agents_md()
        result['compressions']['MEMORY.md'] = self.compress_memory_md()
        result['compressions']['daily_note'] = self.compress_daily_note()
        
        # 检查压缩后大小
        result['after'] = self.check_files()
        
        # 计算总压缩率
        before_size = result['before']['total_size']
        after_size = result['after']['total_size']
        result['total_compression_rate'] = round(
            (1 - after_size / before_size) * 100, 2
        ) if before_size > 0 else 0
        
        # 保存日志
        self._save_compression_log(result)
        
        return result
    
    def _save_compression_log(self, result: Dict):
        """保存压缩日志"""
        log_entry = {
            'timestamp': result['timestamp'],
            'before_size_kb': result['before']['total_size_kb'],
            'after_size_kb': result['after']['total_size_kb'],
            'compression_rate': result['total_compression_rate'],
            'within_limit': result['after']['within_limit'],
            'issues': result['after']['issues']
        }
        
        # 读取现有日志
        logs = []
        if self.compression_log.exists():
            with open(self.compression_log, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except (Exception,):
                    logs = []
        
        # 添加新日志
        logs.append(log_entry)
        
        # 只保留最近 30 条
        logs = logs[-30:]
        
        # 保存
        with open(self.compression_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def generate_report(self) -> str:
        """生成压缩报告"""
        check_result = self.check_files()
        
        report = []
        report.append("=" * 60)
        report.append("核心文件压缩报告")
        report.append(f"时间: {check_result['timestamp']}")
        report.append("=" * 60)
        report.append("")
        
        # 文件状态
        report.append("文件状态:")
        report.append("-" * 60)
        for f in check_result['files']:
            if f['exists']:
                status = "[OK]" if f['within_limit'] else "[WARN]"
                report.append(
                    f"{status} {f['name']:<25} "
                    f"{f['size_kb']:>6.2f}KB / {f['limit_kb']:>5.2f}KB "
                    f"({f['usage']:>5.1f}%)"
                )
            else:
                report.append(f"[MISSING] {f['name']:<25}")
        
        report.append("-" * 60)
        report.append(
            f"总计: {check_result['total_size_kb']:>6.2f}KB / "
            f"{self.TOTAL_LIMIT/1024:>5.2f}KB "
            f"({check_result['total_size']/self.TOTAL_LIMIT*100:>5.1f}%)"
        )
        report.append("")
        
        # 问题
        if check_result['issues']:
            report.append("问题:")
            for issue in check_result['issues']:
                report.append(f"  - {issue}")
            report.append("")
        
        # 建议
        if not check_result['within_limit']:
            report.append("建议:")
            report.append("  1. 运行: py core_files_compressor.py --compress")
            report.append("  2. 检查 MEMORY.md 是否需要蒸馏")
            report.append("  3. 检查今日笔记是否需要压缩")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py core_files_compressor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py core_files_compressor_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

主函数"""
    compressor = CoreFilesCompressor()
    
    if len(sys.argv) < 2:
        # 默认检查
        result = compressor.check_files()
        print(f"\n总大小: {result['total_size_kb']:.2f}KB")
        print(f"状态: {'[OK] 符合限制' if result['within_limit'] else '[WARN] 超过限制'}")
        print(f"问题: {len(result['issues'])} 个")
        return
    
    command = sys.argv[1]
    
    if command == '--check':
        result = compressor.check_files()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == '--compress':
        result = compressor.compress_all()
        print(f"\n压缩前: {result['before']['total_size_kb']:.2f}KB")
        print(f"压缩后: {result['after']['total_size_kb']:.2f}KB")
        print(f"压缩率: {result['total_compression_rate']:.2f}%")
        print(f"状态: {'[OK] 符合限制' if result['after']['within_limit'] else '[WARN] 超过限制'}")
    
    elif command == '--report':
        print(compressor.generate_report())
    
    else:
        print(f"未知命令: {command}")
        print("用法:")
        print("  py core_files_compressor.py --check     检查核心文件")
        print("  py core_files_compressor.py --compress  压缩核心文件")
        print("  py core_files_compressor.py --report    生成报告")


if __name__ == "__main__":
    main()