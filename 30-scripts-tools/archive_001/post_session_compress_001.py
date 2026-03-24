import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话后压缩脚本 - 完整的会话后压缩流程

功能：
1. 压缩核心文件
2. 压缩今日笔记
3. 蒸馏记忆
4. 生成压缩报告
5. 验证压缩效果

使用：
  py post_session_compress.py --auto
  py post_session_compress.py --force
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent))

from core_files_compressor_001 import CoreFilesCompressor


class PostSessionCompress:
    """会话后压缩处理器"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.compression_log = self.workspace / '10-MEMORY/00-CORE/compression_log.json'

    def compress_core_files(self) -> Dict:
        """压缩核心文件"""
        compressor = CoreFilesCompressor()
        return compressor.compress_all()

    def compress_daily_note(self) -> Dict:
        """压缩今日笔记"""
        daily_note = self.workspace / f'10-MEMORY/00-CORE/{self.today}.md'

        if not daily_note.exists():
            return {'status': 'skipped', 'reason': 'Daily note not found'}

        with open(daily_note, 'r', encoding='utf-8') as f:
            content = f.read()

        original_size = len(content)

        # 压缩策略：
        # 1. 移除多余空行
        import re
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+\n', '\n', content)

        compressed_size = len(content)
        compression_rate = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        if compression_rate > 5:
            with open(daily_note, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'compressed',
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_rate': round(compression_rate, 2)
            }

        return {'status': 'skipped', 'reason': f'Compression rate too low: {compression_rate:.2f}%'}

    def distill_memory(self) -> Dict:
        """蒸馏记忆（调用 memory_distiller）"""
        memory_path = self.workspace / 'MEMORY.md'

        if not memory_path.exists():
            return {'status': 'skipped', 'reason': 'MEMORY.md not found'}

        # 检查是否需要蒸馏
        size = memory_path.stat().st_size
        size_limit = 20 * 1024  # 20KB

        if size <= size_limit:
            return {'status': 'skipped', 'reason': f'MEMORY.md within limit: {size} <= {size_limit}'}

        # 尝试调用 memory_distiller
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, '30-scripts-tools/memory_distiller_v2.py', '--auto'],
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'returncode': result.returncode,
                'output': result.stdout[:500] if result.stdout else '',
                'error': result.stderr[:500] if result.stderr else ''
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def validate_result(self, compression_result: Dict) -> Dict:
        """验证压缩结果"""
        compressor = CoreFilesCompressor()
        check_result = compressor.check_files()

        return {
            'total_size_kb': check_result['total_size_kb'],
            'within_limit': check_result['within_limit'],
            'issues': check_result['issues']
        }

    def execute(self, auto: bool = False, force: bool = False) -> Dict:
        """执行压缩流程"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'auto' if auto else ('force' if force else 'manual'),
            'steps': {}
        }

        # 1. 压缩核心文件
        print("\n[1/4] 压缩核心文件...")
        result['steps']['compress_core'] = self.compress_core_files()
        core_result = result['steps']['compress_core']
        print(f"  压缩前: {core_result['before']['total_size_kb']:.2f}KB")
        print(f"  压缩后: {core_result['after']['total_size_kb']:.2f}KB")
        print(f"  压缩率: {core_result['total_compression_rate']:.2f}%")

        # 2. 压缩今日笔记
        print("\n[2/4] 压缩今日笔记...")
        result['steps']['compress_note'] = self.compress_daily_note()
        note_result = result['steps']['compress_note']
        if note_result['status'] == 'compressed':
            print(f"  压缩率: {note_result['compression_rate']:.2f}%")
        else:
            print(f"  跳过: {note_result['reason']}")

        # 3. 蒸馏记忆
        print("\n[3/4] 蒸馏记忆...")
        result['steps']['distill_memory'] = self.distill_memory()
        memory_result = result['steps']['distill_memory']
        if memory_result['status'] == 'success':
            print("  完成")
        else:
            print(f"  跳过: {memory_result['reason']}")

        # 4. 验证结果
        print("\n[4/4] 验证压缩结果...")
        result['validation'] = self.validate_result(core_result)
        validation = result['validation']
        print(f"  总大小: {validation['total_size_kb']:.2f}KB")
        print(f"  状态: {'[OK] 符合限制' if validation['within_limit'] else '[WARN] 超过限制'}")

        if validation['issues']:
            print("  问题:")
            for issue in validation['issues']:
                print(f"    - {issue}")

        # 生成报告
        result['summary'] = self._generate_summary(result)
        print(result['summary'])

        return result

    def _generate_summary(self, result: Dict) -> str:
        """生成摘要"""
        summary = []
        summary.append("\n" + "=" * 60)
        summary.append("会话后压缩报告")
        summary.append(f"时间: {result['timestamp']}")
        summary.append(f"模式: {result['mode']}")
        summary.append("=" * 60)

        core = result['steps']['compress_core']
        summary.append(f"\n核心文件:")
        summary.append(f"  压缩前: {core['before']['total_size_kb']:.2f}KB")
        summary.append(f"  压缩后: {core['after']['total_size_kb']:.2f}KB")
        summary.append(f"  压缩率: {core['total_compression_rate']:.2f}%")

        note = result['steps']['compress_note']
        summary.append(f"\n今日笔记:")
        summary.append(f"  状态: {note['status']}")

        memory = result['steps']['distill_memory']
        summary.append(f"\n记忆蒸馏:")
        summary.append(f"  状态: {memory['status']}")

        validation = result['validation']
        summary.append(f"\n验证结果:")
        summary.append(f"  总大小: {validation['total_size_kb']:.2f}KB")
        summary.append(f"  状态: {'通过' if validation['within_limit'] else '不通过'}")

        summary.append("\n" + "=" * 60)

        return "\n".join(summary)


logging.basicConfig(level=logging.INFO)

def main():
    """Post-session compression main entry point."""
    auto = '--auto' in sys.argv
    force = '--force' in sys.argv

    compressor = PostSessionCompress()
    result = compressor.execute(auto=auto, force=force)

    if result['validation']['within_limit']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
