#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Cleanup & Deduplication - 记忆去重清理工具

识别并清理重复、冗余内容。

功能:
1. 检测重复内容 (基于相似度)
2. 识别冗余段落
3. 清理空行、无效内容
4. 合并相似记忆

算法:
- Jaccard 相似度检测重复
- LCS (Longest Common Subsequence) 检测冗余
- 文本清理 (空行、空白字符)

使用:
    # 检测重复
    py memory_cleanup_compress.py --detect-duplicates --days 30
    
    # 清理单条记忆
    py memory_cleanup_compress.py --cleanup --memory "13-memory/2026-03-18.md"
    
    # 批量清理 (最近 7 天)
    py memory_cleanup_compress.py --batch --days 7
    
    # 生成清理报告
    py memory_cleanup_compress.py --report --days 30
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import hashlib

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'


@dataclass
class DuplicatePair:
    """重复对"""
    memory_1: str
    memory_2: str
    similarity: float
    duplicate_type: str  # 'exact', 'near_duplicate', 'partial'
    common_content: str


@dataclass
class CleanupResult:
    """清理结果"""
    memory_id: str
    original_size: int
    cleaned_size: int
    reduction_ratio: float
    lines_removed: int
    empty_lines_removed: int
    duplicates_removed: int
    timestamp: str


@dataclass
class DeduplicationReport:
    """去重报告"""
    total_memories: int
    duplicate_pairs: int
    exact_duplicates: int
    near_duplicates: int
    partial_duplicates: int
    total_redundancy_bytes: int
    details: List[DuplicatePair]
    recommendations: List[str]
    timestamp: str


class MemoryCleanup:
    """记忆清理工具"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
    
    def _normalize_text(self, text: str) -> str:
        """标准化文本"""
        # 移除多余空白
        text = re.sub(r'[ \t]+', ' ', text)
        # 移除空行
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return '\n'.join(lines)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """计算 Jaccard 相似度"""
        # 分词 (按字符 n-gram)
        def get_ngrams(text: str, n: int = 3) -> Set[str]:
            text = text.lower()
            return set(text[i:i+n] for i in range(len(text) - n + 1))
        
        set1 = get_ngrams(text1)
        set2 = get_ngrams(text2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _sequence_similarity(self, text1: str, text2: str) -> float:
        """计算序列相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _find_common_substring(self, text1: str, text2: str, min_length: int = 50) -> str:
        """查找共同子串"""
        match = SequenceMatcher(None, text1, text2).find_longest_match(
            0, len(text1), 0, len(text2)
        )
        
        if match.size >= min_length:
            return text1[match.a:match.a + match.size]
        return ""
    
    def detect_duplicates(self, days: int = 30) -> List[DuplicatePair]:
        """检测重复"""
        duplicates = []
        
        if not MEMORY_DIR.exists():
            return duplicates
        
        # 加载记忆
        memories = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', note_file.stem):
                continue
            
            try:
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date < cutoff_date:
                    continue
                
                content = note_file.read_text(encoding='utf-8', errors='replace')
                normalized = self._normalize_text(content)
                
                memories.append({
                    'id': note_file.name,
                    'content': content,
                    'normalized': normalized,
                    'hash': hashlib.md5(normalized.encode()).hexdigest()
                })
            
            except Exception as e:
                continue
        
        # 两两比较
        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                mem1 = memories[i]
                mem2 = memories[j]
                
                # 1. 精确重复 (哈希相同)
                if mem1['hash'] == mem2['hash']:
                    duplicates.append(DuplicatePair(
                        memory_1=mem1['id'],
                        memory_2=mem2['id'],
                        similarity=1.0,
                        duplicate_type='exact',
                        common_content=mem1['content'][:200]
                    ))
                    continue
                
                # 2. 近似重复 (相似度≥阈值)
                similarity = self._sequence_similarity(mem1['normalized'], mem2['normalized'])
                
                if similarity >= self.similarity_threshold:
                    common = self._find_common_substring(mem1['normalized'], mem2['normalized'])
                    duplicates.append(DuplicatePair(
                        memory_1=mem1['id'],
                        memory_2=mem2['id'],
                        similarity=round(similarity, 3),
                        duplicate_type='near_duplicate',
                        common_content=common[:200] if common else "N/A"
                    ))
                    continue
                
                # 3. 部分重复 (相似度≥0.5)
                if similarity >= 0.5:
                    common = self._find_common_substring(mem1['normalized'], mem2['normalized'])
                    if common:
                        duplicates.append(DuplicatePair(
                            memory_1=mem1['id'],
                            memory_2=mem2['id'],
                            similarity=round(similarity, 3),
                            duplicate_type='partial',
                            common_content=common[:200]
                        ))
        
        return sorted(duplicates, key=lambda x: x.similarity, reverse=True)
    
    def cleanup_single(self, memory_path: Path) -> CleanupResult:
        """清理单条记忆"""
        content = memory_path.read_text(encoding='utf-8', errors='replace')
        original_size = len(content)
        original_lines = content.split('\n')
        
        # 1. 移除空行
        non_empty_lines = [l for l in original_lines if l.strip()]
        empty_lines_removed = len(original_lines) - len(non_empty_lines)
        
        # 2. 移除行内多余空白
        cleaned_lines = [re.sub(r'[ \t]+', ' ', l.strip()) for l in non_empty_lines]
        
        # 3. 移除重复行
        seen_lines = set()
        unique_lines = []
        duplicates_removed = 0
        
        for line in cleaned_lines:
            if line not in seen_lines:
                seen_lines.add(line)
                unique_lines.append(line)
            else:
                duplicates_removed += 1
        
        # 生成清理后内容
        cleaned_content = '\n'.join(unique_lines)
        cleaned_size = len(cleaned_content)
        
        # 计算压缩率
        reduction_ratio = (original_size - cleaned_size) / original_size if original_size > 0 else 0
        
        return CleanupResult(
            memory_id=memory_path.name,
            original_size=original_size,
            cleaned_size=cleaned_size,
            reduction_ratio=round(reduction_ratio, 3),
            lines_removed=len(original_lines) - len(unique_lines),
            empty_lines_removed=empty_lines_removed,
            duplicates_removed=duplicates_removed,
            timestamp=datetime.now().isoformat()
        )
    
    def cleanup_batch(self, days: int = 7) -> List[CleanupResult]:
        """批量清理"""
        results = []
        
        if not MEMORY_DIR.exists():
            return results
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', note_file.stem):
                continue
            
            try:
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date < cutoff_date:
                    continue
                
                result = self.cleanup_single(note_file)
                results.append(result)
            
            except Exception as e:
                print(f"[ERROR] {note_file.name}: {e}")
        
        return results
    
    def generate_report(self, days: int = 30) -> DeduplicationReport:
        """生成去重报告"""
        duplicates = self.detect_duplicates(days)
        
        if not duplicates:
            return DeduplicationReport(
                total_memories=0,
                duplicate_pairs=0,
                exact_duplicates=0,
                near_duplicates=0,
                partial_duplicates=0,
                total_redundancy_bytes=0,
                details=[],
                recommendations=["No duplicates found"],
                timestamp=datetime.now().isoformat()
            )
        
        # 统计
        exact = sum(1 for d in duplicates if d.duplicate_type == 'exact')
        near = sum(1 for d in duplicates if d.duplicate_type == 'near_duplicate')
        partial = sum(1 for d in duplicates if d.duplicate_type == 'partial')
        
        # 估算冗余字节
        total_redundancy = sum(len(d.common_content) for d in duplicates)
        
        # 建议
        recommendations = []
        if exact > 0:
            recommendations.append(f"发现 {exact} 对精确重复，建议删除重复文件")
        if near > 0:
            recommendations.append(f"发现 {near} 对近似重复，建议合并内容")
        if partial > 0:
            recommendations.append(f"发现 {partial} 对部分重复，建议检查共同内容")
        if not recommendations:
            recommendations.append("记忆重复度低，质量良好")
        
        # 计算总记忆数
        total_memories = len(set(d.memory_1 for d in duplicates) | set(d.memory_2 for d in duplicates))
        
        return DeduplicationReport(
            total_memories=total_memories,
            duplicate_pairs=len(duplicates),
            exact_duplicates=exact,
            near_duplicates=near,
            partial_duplicates=partial,
            total_redundancy_bytes=total_redundancy,
            details=duplicates,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )


def print_cleanup_result(result: CleanupResult):
    """打印清理结果"""
    print(f"\n{result.memory_id}:")
    print(f"  {result.original_size:,} → {result.cleaned_size:,} bytes ({result.reduction_ratio:.1%} reduction)")
    print(f"  Empty lines removed: {result.empty_lines_removed}")
    print(f"  Duplicate lines removed: {result.duplicates_removed}")


def print_report(report: DeduplicationReport):
    """打印去重报告"""
    print("\n" + "=" * 60)
    print("Memory Deduplication Report")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Memories Scanned: {report.total_memories}")
    print(f"  Duplicate Pairs Found:  {report.duplicate_pairs}")
    print(f"  Total Redundancy:       {report.total_redundancy_bytes:,} bytes")
    
    print(f"\n[Duplicate Types]")
    print(f"  Exact:           {report.exact_duplicates}")
    print(f"  Near Duplicate:  {report.near_duplicates}")
    print(f"  Partial:         {report.partial_duplicates}")
    
    if report.details:
        print(f"\n[Top Duplicates]")
        for dup in report.details[:5]:
            print(f"\n  {dup.memory_1} ↔ {dup.memory_2}")
            print(f"    Similarity: {dup.similarity:.1%} ({dup.duplicate_type})")
            if dup.common_content and dup.common_content != "N/A":
                preview = dup.common_content[:100].replace('\n', ' ')
                print(f"    Common: {preview}...")
    
    print(f"\n[Recommendations]")
    for rec in report.recommendations:
        print(f"  • {rec}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Cleanup & Deduplication')
    parser.add_argument('--detect-duplicates', action='store_true', help='检测重复')
    parser.add_argument('--cleanup', action='store_true', help='清理单条记忆')
    parser.add_argument('--memory', type=str, help='清理的记忆文件')
    parser.add_argument('--batch', action='store_true', help='批量清理')
    parser.add_argument('--days', type=int, default=7, help='处理最近 N 天 (默认 7)')
    parser.add_argument('--report', action='store_true', help='生成去重报告')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值 (默认 0.8)')
    
    args = parser.parse_args()
    
    cleanup = MemoryCleanup(similarity_threshold=args.threshold)
    
    # 检测重复
    if args.detect_duplicates:
        duplicates = cleanup.detect_duplicates(args.days)
        
        if args.json:
            print(json.dumps([asdict(d) for d in duplicates], indent=2, ensure_ascii=False))
        else:
            print(f"\n[Duplicate Pairs: {len(duplicates)}]")
            for dup in duplicates[:10]:
                print(f"\n{dup.memory_1} ↔ {dup.memory_2}")
                print(f"  Similarity: {dup.similarity:.1%} ({dup.duplicate_type})")
        
        return 0
    
    # 清理单条
    if args.cleanup and args.memory:
        memory_path = Path(args.memory.replace('"', '').replace("'", ""))
        if not memory_path.is_absolute():
            memory_path = WORKSPACE / memory_path
        
        if not memory_path.exists():
            print(f"[ERROR] File not found: {memory_path}")
            return 1
        
        result = cleanup.cleanup_single(memory_path)
        
        if args.json:
            print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
        else:
            print_cleanup_result(result)
        
        return 0
    
    # 批量清理
    if args.batch:
        results = cleanup.cleanup_batch(args.days)
        
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False))
        else:
            print(f"\n[Cleanup Results: {len(results)} memories]")
            total_original = sum(r.original_size for r in results)
            total_cleaned = sum(r.cleaned_size for r in results)
            print(f"  Total: {total_original:,} → {total_cleaned:,} bytes ({(total_original-total_cleaned)/total_original:.1%} reduction)")
            
            for result in results:
                print_cleanup_result(result)
        
        return 0
    
    # 生成报告
    if args.report:
        report = cleanup.generate_report(args.days)
        
        if args.json:
            print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
        else:
            print_report(report)
        
        return 0
    
    # 默认显示帮助
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
