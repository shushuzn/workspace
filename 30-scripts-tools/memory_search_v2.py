#!/usr/bin/env python3
"""
增强版记忆检索系统 - Memory Search V2
功能：语义搜索 + 关键词搜索 + 智能排序 + 质量评分
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# 记忆存储位置
MEMORY_FILE = Path(r"C:\Users\华为\.copaw\MEMORY.md")
MEMORY_DIR = Path(r"D:\OpenClaw\workspace\13-memory-记忆系统")

class MemorySearchV2:
    """增强版记忆检索系统"""
    
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.memory_dir = MEMORY_DIR
        self.cache = {}
        self.cache_time = {}
        self.cache_ttl = 300  # 5 分钟缓存
        
    def search(self, query: str, max_results: int = 5, min_score: float = 0.1) -> List[Dict]:
        """
        智能记忆检索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            min_score: 最低相似度分数
            
        Returns:
            记忆片段列表 (包含分数、位置、内容)
        """
        # 检查缓存
        cache_key = f"{query}:{max_results}:{min_score}"
        if cache_key in self.cache:
            if (datetime.now() - self.cache_time[cache_key]).total_seconds() < self.cache_ttl:
                return self.cache[cache_key]
        
        results = []
        
        # 1. 语义搜索 (基于关键词匹配)
        semantic_results = self._semantic_search(query)
        results.extend(semantic_results)
        
        # 2. 关键词搜索
        keyword_results = self._keyword_search(query)
        results.extend(keyword_results)
        
        # 3. 去重和排序
        results = self._deduplicate_and_sort(results, max_results, min_score)
        
        # 缓存结果
        self.cache[cache_key] = results
        self.cache_time[cache_key] = datetime.now()
        
        return results
    
    def _semantic_search(self, query: str) -> List[Dict]:
        """语义搜索 (基于关键词扩展)"""
        results = []
        
        # 读取 MEMORY.md
        if not self.memory_file.exists():
            return results
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割记忆片段 (按 ## 标题)
        sections = re.split(r'\n(?=## )', content)
        
        # 关键词扩展
        query_keywords = self._expand_keywords(query)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # 计算相关性分数
            score = self._calculate_relevance(section, query_keywords)
            
            if score > 0.1:
                # 提取片段信息
                title_match = re.search(r'^## (.+)', section, re.MULTILINE)
                title = title_match.group(1) if title_match else "Untitled"
                
                # 提取前 200 字
                preview = section[:200].replace('\n', ' ').strip()
                
                results.append({
                    'type': 'memory',
                    'title': title,
                    'content': preview,
                    'score': score,
                    'source': str(self.memory_file),
                    'line': i * 20,  # 估算行号
                    'quality': self._estimate_quality(section)
                })
        
        return results
    
    def _keyword_search(self, query: str) -> List[Dict]:
        """关键词搜索"""
        results = []
        
        # 搜索每日笔记
        if self.memory_dir.exists():
            for md_file in self.memory_dir.glob("*.md"):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query.lower() in content.lower():
                    # 找到匹配位置
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append({
                                'type': 'daily_note',
                                'title': md_file.stem,
                                'content': line[:200],
                                'score': 0.8,
                                'source': str(md_file),
                                'line': i + 1,
                                'quality': 0.7
                            })
                            break
        
        return results
    
    def _expand_keywords(self, query: str) -> List[str]:
        """关键词扩展"""
        # 简单扩展：同义词、相关词
        expansions = {
            '防护': ['保护', '安全', 'security', 'protection'],
            '会话': ['session', '启动', '启动'],
            '文件': ['file', '路径', 'path', '位置'],
            '记忆': ['memory', '笔记', 'note', '记录'],
            '系统': ['system', '机制', '机制'],
        }
        
        keywords = [query.lower()]
        
        for key, values in expansions.items():
            if key in query.lower():
                keywords.extend(values)
        
        return list(set(keywords))
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """计算相关性分数"""
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        return min(1.0, matches / max(1, len(keywords)))
    
    def _estimate_quality(self, content: str) -> float:
        """估算记忆质量"""
        score = 0.5
        
        # 有编号 → 质量 +0.2
        if re.search(r'\[SYS-\d+\]|\[MEM-\d+\]|\[MULTI-\d+\]', content):
            score += 0.2
        
        # 有日期 → 质量 +0.1
        if re.search(r'\d{4}-\d{2}-\d{2}', content):
            score += 0.1
        
        # 有代码块 → 质量 +0.1
        if '```' in content:
            score += 0.1
        
        # 长度适中 → 质量 +0.1
        if 100 < len(content) < 2000:
            score += 0.1
        
        return min(1.0, score)
    
    def _deduplicate_and_sort(self, results: List[Dict], max_results: int, min_score: float) -> List[Dict]:
        """去重和排序"""
        # 过滤低分
        results = [r for r in results if r['score'] >= min_score]
        
        # 去重 (基于内容)
        seen = set()
        unique_results = []
        for r in results:
            key = r['content'][:50]
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        # 排序 (分数 + 质量)
        unique_results.sort(key=lambda x: x['score'] * 0.7 + x.get('quality', 0.5) * 0.3, reverse=True)
        
        return unique_results[:max_results]
    
    def get_statistics(self) -> Dict:
        """获取记忆统计信息"""
        stats = {
            'total_memories': 0,
            'daily_notes': 0,
            'avg_quality': 0.0,
            'last_updated': None,
            'total_size': 0
        }
        
        # MEMORY.md 统计
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算记忆片段数
            sections = re.split(r'\n(?=## )', content)
            stats['total_memories'] = len([s for s in sections if s.strip()])
            
            # 文件大小
            stats['total_size'] = self.memory_file.stat().st_size
            
            # 最后修改时间
            mtime = datetime.fromtimestamp(self.memory_file.stat().st_mtime)
            stats['last_updated'] = mtime.strftime('%Y-%m-%d %H:%M:%S')
        
        # 每日笔记统计
        if self.memory_dir.exists():
            stats['daily_notes'] = len(list(self.memory_dir.glob("*.md")))
        
        return stats


def demo_search():
    """演示记忆检索"""
    print("=" * 60)
    print("增强版记忆检索系统 V2")
    print("=" * 60)
    
    searcher = MemorySearchV2()
    
    # 演示搜索
    queries = ["防护", "会话", "文件路径", "7 人格"]
    
    print("\n搜索演示:")
    for query in queries:
        print(f"\n查询：{query}")
        results = searcher.search(query, max_results=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['score']:.2f}] {result['title']}")
            print(f"     {result['content'][:100]}...")
    
    # 显示统计
    print("\n" + "=" * 60)
    print("记忆系统统计")
    print("=" * 60)
    stats = searcher.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    demo_search()
