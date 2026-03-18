#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Incremental Compressor - 增量压缩工具

核心思想:
- 检测会话间的重复内容
- 只存储差异部分 (diff)
- 使用 LCS 算法识别公共子序列
- 版本控制支持 (可回溯)

压缩策略:
1. 与前一天笔记对比 → 提取新增内容
2. 与最近 7 天对比 → 识别重复模式
3. 与 MEMORY.md 对比 → 避免重复蒸馏
4. 生成增量包 → 只保存变更

使用:
    # 单文件增量压缩
    py memory_incremental_compressor.py --memory "13-memory/2026-03-18.md"
    
    # 批量增量压缩 (最近 7 天)
    py memory_incremental_compressor.py --batch --days 7
    
    # 生成差异报告
    py memory_incremental_compressor.py --diff --days 7
    
    # 查看重复率
    py memory_incremental_compressor.py --redundancy --days 30
"""

import sys
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict
import difflib

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'
INCREMENTAL_DIR = WORKSPACE / '13-memory' / 'incremental'


@dataclass
class IncrementalReport:
    """增量压缩报告"""
    memory_id: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    redundancy_rate: float
    new_content_ratio: float
    duplicates_found: List[Dict]
    timestamp: str


class MemoryIncrementalCompressor:
    """记忆增量压缩器"""
    
    def __init__(self):
        self.cache = {}  # 内容缓存
    
    def _normalize_content(self, content: str) -> str:
        """标准化内容（移除格式差异）"""
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content)
        # 移除行首尾空白
        lines = [line.strip() for line in content.split('\n')]
        # 移除空行
        lines = [line for line in lines if line]
        return '\n'.join(lines)
    
    def _calculate_hash(self, content: str) -> str:
        """计算内容哈希"""
        normalized = self._normalize_content(content)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _lcs(self, a: List[str], b: List[str]) -> List[str]:
        """
        最长公共子序列 (Longest Common Subsequence)
        
        用于识别两个文本块的共同部分
        """
        m, n = len(a), len(b)
        
        # DP 表
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # 填充 DP 表
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        # 回溯获取 LCS
        lcs = []
        i, j = m, n
        while i > 0 and j > 0:
            if a[i-1] == b[j-1]:
                lcs.append(a[i-1])
                i -= 1
                j -= 1
            elif dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1
        
        return lcs[::-1]  # 反转
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """计算两个内容的相似度 (0-1)"""
        # 使用 difflib SequenceMatcher
        matcher = difflib.SequenceMatcher(None, content1, content2)
        return matcher.ratio()
    
    def _find_redundant_blocks(self, content: str, reference_contents: List[str], 
                               block_size: int = 5) -> List[Dict]:
        """
        查找冗余内容块
        
        Args:
            content: 当前内容
            reference_contents: 参考内容列表（历史笔记）
            block_size: 块大小（行数）
        
        Returns:
            冗余块列表
        """
        lines = content.split('\n')
        duplicates = []
        
        # 将内容分块
        blocks = []
        for i in range(0, len(lines) - block_size + 1, block_size):
            block = '\n'.join(lines[i:i+block_size])
            blocks.append({
                'start_line': i + 1,
                'end_line': i + block_size,
                'content': block,
                'hash': self._calculate_hash(block)
            })
        
        # 检查每个块是否在参考内容中出现
        for block in blocks:
            for ref_idx, ref_content in enumerate(reference_contents):
                if block['content'] in ref_content:
                    duplicates.append({
                        'block_hash': block['hash'],
                        'start_line': block['start_line'],
                        'end_line': block['end_line'],
                        'found_in': f'ref_{ref_idx}',
                        'similarity': 1.0
                    })
                    break
        
        return duplicates
    
    def _extract_new_content(self, current: str, previous: str) -> Tuple[str, float]:
        """
        提取新增内容
        
        Returns:
            (新增内容，新增比例)
        """
        # 使用 difflib 生成差异
        diff = difflib.unified_diff(
            previous.splitlines(keepends=True),
            current.splitlines(keepends=True),
            lineterm=''
        )
        
        # 提取新增行
        new_lines = []
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                new_lines.append(line[1:])
        
        new_content = '\n'.join(new_lines)
        new_ratio = len(new_content) / len(current) if current else 0
        
        return new_content, min(new_ratio, 1.0)
    
    def compress_single(self, memory_path: Path, reference_paths: List[Path] = None) -> IncrementalReport:
        """
        压缩单条记忆
        
        Args:
            memory_path: 当前记忆文件
            reference_paths: 参考文件列表（用于对比）
        """
        # 读取当前内容
        current_content = memory_path.read_text(encoding='utf-8', errors='replace')
        original_size = len(current_content)
        
        # 读取参考内容
        reference_contents = []
        if reference_paths:
            for ref_path in reference_paths:
                if ref_path.exists():
                    ref_content = ref_path.read_text(encoding='utf-8', errors='replace')
                    reference_contents.append(ref_content)
        
        # 查找冗余块
        duplicates = self._find_redundant_blocks(current_content, reference_contents)
        
        # 计算冗余率
        redundancy_rate = len(duplicates) / max(1, len(current_content.split('\n')))
        
        # 提取新增内容（如果有前一天的笔记）
        new_content_ratio = 1.0
        if reference_paths and len(reference_paths) > 0:
            prev_path = reference_paths[0]
            if prev_path.exists():
                prev_content = prev_path.read_text(encoding='utf-8', errors='replace')
                _, new_content_ratio = self._extract_new_content(current_content, prev_content)
        
        # 计算压缩后大小（只存储新增内容 + 索引）
        compressed_size = int(original_size * new_content_ratio) + len(duplicates) * 32  # 索引开销
        
        # 压缩率
        compression_ratio = (original_size - compressed_size) / original_size if original_size > 0 else 0
        
        return IncrementalReport(
            memory_id=memory_path.name,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=round(compression_ratio, 3),
            redundancy_rate=round(redundancy_rate, 3),
            new_content_ratio=round(new_content_ratio, 3),
            duplicates_found=duplicates[:10],  # 最多 10 个
            timestamp=datetime.now().isoformat()
        )
    
    def compress_batch(self, days: int = 7) -> List[IncrementalReport]:
        """批量压缩最近 N 天的记忆"""
        reports = []
        
        if not MEMORY_DIR.exists():
            return reports
        
        # 获取最近的日常笔记
        cutoff_date = datetime.now() - timedelta(days=days)
        daily_notes = []
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            try:
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date >= cutoff_date:
                    daily_notes.append((note_file, note_date))
            except ValueError:
                continue
        
        # 按日期排序
        daily_notes.sort(key=lambda x: x[1], reverse=True)
        
        # 逐个压缩
        for i, (note_file, note_date) in enumerate(daily_notes):
            # 参考文件：前一天的笔记
            reference_paths = []
            if i < len(daily_notes) - 1:
                reference_paths.append(daily_notes[i + 1][0])
            
            # 额外参考：最近 7 天的所有笔记
            for j in range(max(0, i-3), min(len(daily_notes), i+4)):
                if j != i:
                    reference_paths.append(daily_notes[j][0])
            
            try:
                report = self.compress_single(note_file, reference_paths)
                reports.append(report)
            except Exception as e:
                print(f"[ERROR] {note_file.name}: {e}")
        
        return reports
    
    def generate_diff_report(self, days: int = 7) -> Dict:
        """生成差异报告"""
        reports = self.compress_batch(days)
        
        if not reports:
            return {'error': 'No memories found'}
        
        # 统计
        total_original = sum(r.original_size for r in reports)
        total_compressed = sum(r.compressed_size for r in reports)
        avg_redundancy = sum(r.redundancy_rate for r in reports) / len(reports)
        avg_new_content = sum(r.new_content_ratio for r in reports) / len(reports)
        
        return {
            'total_memories': len(reports),
            'total_original_size': total_original,
            'total_compressed_size': total_compressed,
            'overall_compression_ratio': round((total_original - total_compressed) / total_original, 3) if total_original > 0 else 0,
            'average_redundancy_rate': round(avg_redundancy, 3),
            'average_new_content_ratio': round(avg_new_content, 3),
            'details': [asdict(r) for r in reports]
        }
    
    def analyze_redundancy(self, days: int = 30) -> Dict:
        """分析冗余度"""
        reports = self.compress_batch(days)
        
        if not reports:
            return {'error': 'No memories found'}
        
        # 按冗余率排序
        reports.sort(key=lambda r: r.redundancy_rate, reverse=True)
        
        # 高冗余记忆
        high_redundancy = [r for r in reports if r.redundancy_rate > 0.3]
        
        # 低新内容记忆
        low_new_content = [r for r in reports if r.new_content_ratio < 0.5]
        
        return {
            'total_memories': len(reports),
            'high_redundancy_count': len(high_redundancy),
            'low_new_content_count': len(low_new_content),
            'high_redundancy_memories': [asdict(r) for r in high_redundancy[:5]],
            'low_new_content_memories': [asdict(r) for r in low_new_content[:5]],
            'recommendations': self._generate_recommendations(high_redundancy, low_new_content)
        }
    
    def _generate_recommendations(self, high_redundancy: List, low_new_content: List) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if high_redundancy:
            recommendations.append(f"发现 {len(high_redundancy)} 条高冗余记忆，建议合并或归档")
            recommendations.append("考虑使用模板减少重复内容")
        
        if low_new_content:
            recommendations.append(f"发现 {len(low_new_content)} 条低新内容记忆，可能只是轻微更新")
            recommendations.append("建议使用增量存储，只保存变更部分")
        
        if not high_redundancy and not low_new_content:
            recommendations.append("记忆质量良好，冗余度低")
        
        return recommendations


def print_report(report: IncrementalReport):
    """打印压缩报告"""
    print("\n" + "=" * 60)
    print(f"Incremental Compression: {report.memory_id}")
    print("=" * 60)
    
    print(f"\n[Size]")
    print(f"  Original:   {report.original_size:,} bytes")
    print(f"  Compressed: {report.compressed_size:,} bytes")
    print(f"  Ratio:      {report.compression_ratio:.1%} reduction")
    
    print(f"\n[Content Analysis]")
    print(f"  Redundancy Rate:  {report.redundancy_rate:.1%}")
    print(f"  New Content:      {report.new_content_ratio:.1%}")
    
    if report.duplicates_found:
        print(f"\n[Duplicates Found] {len(report.duplicates_found)} blocks")
        for dup in report.duplicates_found[:3]:
            print(f"  - Lines {dup['start_line']}-{dup['end_line']} (found in {dup['found_in']})")
    
    print(f"\n[Timestamp] {report.timestamp}")


def print_diff_report(diff_report: Dict):
    """打印差异报告"""
    print("\n" + "=" * 60)
    print("Incremental Compression - Diff Report")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Memories:        {diff_report.get('total_memories', 0)}")
    print(f"  Total Original Size:   {diff_report.get('total_original_size', 0):,} bytes")
    print(f"  Total Compressed Size: {diff_report.get('total_compressed_size', 0):,} bytes")
    print(f"  Overall Compression:   {diff_report.get('overall_compression_ratio', 0):.1%} reduction")
    
    print(f"\n[Content Analysis]")
    print(f"  Average Redundancy Rate:  {diff_report.get('average_redundancy_rate', 0):.1%}")
    print(f"  Average New Content:      {diff_report.get('average_new_content_ratio', 0):.1%}")
    
    if 'details' in diff_report:
        print(f"\n[Details]")
        for detail in diff_report['details'][:5]:
            print(f"  {detail['memory_id']}: {detail['compression_ratio']:.1%} (new: {detail['new_content_ratio']:.1%})")


def print_redundancy_analysis(analysis: Dict):
    """打印冗余分析"""
    print("\n" + "=" * 60)
    print("Memory Redundancy Analysis")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Memories:        {analysis.get('total_memories', 0)}")
    print(f"  High Redundancy:       {analysis.get('high_redundancy_count', 0)}")
    print(f"  Low New Content:       {analysis.get('low_new_content_count', 0)}")
    
    if analysis.get('high_redundancy_memories'):
        print(f"\n[Top High Redundancy Memories]")
        for mem in analysis['high_redundancy_memories'][:3]:
            print(f"  {mem['memory_id']}: {mem['redundancy_rate']:.1%} redundancy")
    
    if analysis.get('low_new_content_memories'):
        print(f"\n[Top Low New Content Memories]")
        for mem in analysis['low_new_content_memories'][:3]:
            print(f"  {mem['memory_id']}: {mem['new_content_ratio']:.1%} new content")
    
    if analysis.get('recommendations'):
        print(f"\n[Recommendations]")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Incremental Compressor')
    parser.add_argument('--memory', type=str, help='压缩单条记忆文件')
    parser.add_argument('--batch', action='store_true', help='批量压缩')
    parser.add_argument('--days', type=int, default=7, help='处理最近 N 天 (默认 7)')
    parser.add_argument('--diff', action='store_true', help='生成差异报告')
    parser.add_argument('--redundancy', action='store_true', help='分析冗余度')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    compressor = MemoryIncrementalCompressor()
    
    # 单文件压缩
    if args.memory:
        memory_path = Path(args.memory.replace('"', '').replace("'", ""))
        if not memory_path.is_absolute():
            memory_path = WORKSPACE / memory_path
        
        if not memory_path.exists():
            print(f"[ERROR] File not found: {memory_path}")
            return 1
        
        # 参考文件：前一天的笔记
        reference_paths = []
        try:
            note_date = datetime.strptime(memory_path.stem, '%Y-%m-%d')
            prev_date = note_date - timedelta(days=1)
            prev_path = MEMORY_DIR / f"{prev_date.strftime('%Y-%m-%d')}.md"
            if prev_path.exists():
                reference_paths.append(prev_path)
        except ValueError:
            pass
        
        report = compressor.compress_single(memory_path, reference_paths)
        
        if args.json:
            print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
        else:
            print_report(report)
        
        return 0
    
    # 批量压缩
    if args.batch:
        reports = compressor.compress_batch(args.days)
        
        if args.json:
            print(json.dumps([asdict(r) for r in reports], indent=2, ensure_ascii=False))
        else:
            print(f"\n[Batch Compression] Last {args.days} days")
            print(f"Total memories: {len(reports)}")
            
            if reports:
                total_original = sum(r.original_size for r in reports)
                total_compressed = sum(r.compressed_size for r in reports)
                overall_ratio = (total_original - total_compressed) / total_original if total_original > 0 else 0
                
                print(f"\n[Overall]")
                print(f"  Original:   {total_original:,} bytes")
                print(f"  Compressed: {total_compressed:,} bytes")
                print(f"  Reduction:  {overall_ratio:.1%}")
                
                print(f"\n[Details]")
                for report in reports[:5]:
                    print(f"  {report.memory_id}: {report.compression_ratio:.1%} (redundancy: {report.redundancy_rate:.1%})")
        
        return 0
    
    # 差异报告
    if args.diff:
        diff_report = compressor.generate_diff_report(args.days)
        
        if args.json:
            print(json.dumps(diff_report, indent=2, ensure_ascii=False))
        else:
            print_diff_report(diff_report)
        
        return 0
    
    # 冗余分析
    if args.redundancy:
        analysis = compressor.analyze_redundancy(args.days)
        
        if args.json:
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print_redundancy_analysis(analysis)
        
        return 0
    
    # 默认显示帮助
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
