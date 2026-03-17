#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告增强检索系统
=================
提供语义搜索、标签系统、高级过滤等功能

功能:
1. 语义搜索 - 基于内容相似度搜索
2. 标签系统 - 自动提取和管理标签
3. 高级过滤 - 按日期、类型、质量分等过滤
4. 智能排序 - 按相关性、日期、质量分排序
5. 引用追踪 - 追踪报告间的引用关系

使用:
  python report_search.py --search "keyword"     # 搜索报告
  python report_search.py --tags                 # 显示所有标签
  python report_search.py --filter --type=REPORT # 按类型过滤
  python report_search.py --related "report.md"  # 查找相关报告
  python report_search.py --stats                # 显示检索统计
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

WORKSPACE = Path('D:/OpenClaw/workspace')
REPORTS_DIR = WORKSPACE / '21-reports'
SEARCH_CONFIG = WORKSPACE / 'data' / 'report_search_config.json'
SEARCH_STATE = WORKSPACE / 'data' / 'report_search_state.json'
TAGS_FILE = WORKSPACE / 'data' / 'report_tags.json'


class ReportSearchEngine:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
        self.tags = self._load_tags()
    
    def _load_config(self):
        default_config = {
            'search_fields': ['title', 'content', 'tags', 'metadata'],
            'min_similarity': 0.3,
            'max_results': 20,
            'auto_tag': True,
            'tag_sources': ['title', 'headings', 'keywords'],
            'common_tags': [
                'production', 'test', 'research', 'summary', 'analysis',
                'complete', 'progress', 'planning', 'review', 'evaluation'
            ]
        }
        
        if SEARCH_CONFIG.exists():
            with open(SEARCH_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def _load_state(self):
        if SEARCH_STATE.exists():
            with open(SEARCH_STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'last_index': None, 'index': []}
    
    def _save_state(self):
        SEARCH_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(SEARCH_STATE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _load_tags(self):
        if TAGS_FILE.exists():
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'tags': {}, 'last_updated': None}
    
    def _save_tags(self):
        self.tags['last_updated'] = datetime.now().isoformat()
        TAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TAGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tags, f, indent=2, ensure_ascii=False)
    
    def _extract_text(self, content):
        """提取纯文本内容"""
        # 移除 Markdown 符号
        text = re.sub(r'[#*`\[\]()~>]', '', content)
        # 移除链接
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # 移除图片
        text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
        return text.strip()
    
    def _extract_tags(self, content, filepath):
        """自动提取标签"""
        tags = []
        
        # 从标题提取
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).lower()
            # 提取关键词
            if 'report' in title or '报告' in title:
                tags.append('report')
            if 'summary' in title or '总结' in title or '完成' in title:
                tags.append('summary')
            if 'analysis' in title or '分析' in title:
                tags.append('analysis')
            if 'research' in title or '研究' in title:
                tags.append('research')
            if 'test' in title or '测试' in title:
                tags.append('test')
            if 'production' in title or '生产' in title:
                tags.append('production')
            if 'complete' in title or '完成' in title:
                tags.append('complete')
        
        # 从 H2 标题提取
        h2_matches = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        for h2 in h2_matches:
            h2_lower = h2.lower()
            if 'background' in h2_lower or '背景' in h2_lower:
                tags.append('has-background')
            if 'conclusion' in h2_lower or '结论' in h2_lower:
                tags.append('has-conclusion')
            if 'method' in h2_lower or '方法' in h2_lower:
                tags.append('has-method')
            if 'result' in h2_lower or '结果' in h2_lower:
                tags.append('has-result')
        
        # 从显式标签提取
        tag_match = re.search(r'标签[:：]\s*([^\n]+)', content)
        if tag_match:
            explicit_tags = [t.strip() for t in tag_match.group(1).split(',')]
            tags.extend(explicit_tags)
        
        # 从文件路径提取
        filepath_str = str(filepath).lower()
        if 'quality' in filepath_str:
            tags.append('quality')
        if 'archive' in filepath_str:
            tags.append('archived')
        
        # 去重
        tags = list(set(tags))
        
        return tags
    
    def _calculate_similarity(self, query, text):
        """计算查询和文本的相似度 (简单 Jaccard 相似度)"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words or not text_words:
            return 0.0
        
        intersection = query_words & text_words
        union = query_words | text_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def _index_reports(self):
        """建立报告索引"""
        print('Indexing reports...')
        
        index = []
        tag_counter = Counter()
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            # 跳过特殊目录
            if any(skip in root for skip in ['archive']):
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取信息
                    text = self._extract_text(content)
                    tags = self._extract_tags(content, filepath)
                    
                    # 提取元数据
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', filepath.name)
                    date = date_match.group(0) if date_match else None
                    
                    # 提取标题
                    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = h1_match.group(1).strip() if h1_match else file
                    
                    # 计算字数
                    word_count = len(text)
                    
                    # 创建索引项
                    entry = {
                        'file': str(filepath.relative_to(WORKSPACE)),
                        'title': title,
                        'date': date,
                        'tags': tags,
                        'word_count': word_count,
                        'content_preview': text[:500],
                        'indexed_at': datetime.now().isoformat()
                    }
                    
                    index.append(entry)
                    
                    # 统计标签
                    for tag in tags:
                        tag_counter[tag] += 1
                
                except Exception as e:
                    print(f'  Error indexing {file}: {e}')
        
        self.state['last_index'] = datetime.now().isoformat()
        self.state['index'] = index
        self._save_state()
        
        # 更新标签
        self.tags['tags'] = dict(tag_counter)
        self._save_tags()
        
        print(f'Indexed {len(index)} reports')
        print(f'Found {len(tag_counter)} unique tags')
        
        return index
    
    def search(self, query, max_results=None):
        """搜索报告"""
        if not self.state.get('index'):
            self._index_reports()
        
        max_results = max_results or self.config['max_results']
        results = []
        
        for entry in self.state['index']:
            # 在标题和内容中搜索
            title_score = self._calculate_similarity(query, entry['title'])
            content_score = self._calculate_similarity(query, entry['content_preview'])
            
            # 标签匹配
            query_words = query.lower().split()
            tag_matches = sum(1 for tag in entry['tags'] if any(w in tag.lower() for w in query_words))
            tag_score = tag_matches / len(entry['tags']) if entry['tags'] else 0
            
            # 综合得分
            final_score = (title_score * 0.5) + (content_score * 0.3) + (tag_score * 0.2)
            
            if final_score >= self.config['min_similarity']:
                results.append({
                    **entry,
                    'score': round(final_score, 3),
                    'match_type': 'title' if title_score > 0.3 else 'content'
                })
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def filter_by(self, **filters):
        """按条件过滤报告"""
        if not self.state.get('index'):
            self._index_reports()
        
        results = self.state['index']
        
        # 按标签过滤
        if 'tags' in filters:
            filter_tags = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
            results = [r for r in results if any(t in r['tags'] for t in filter_tags)]
        
        # 按日期范围过滤
        if 'date_from' in filters:
            results = [r for r in results if r['date'] and r['date'] >= filters['date_from']]
        if 'date_to' in filters:
            results = [r for r in results if r['date'] and r['date'] <= filters['date_to']]
        
        # 按字数过滤
        if 'min_words' in filters:
            results = [r for r in results if r['word_count'] >= filters['min_words']]
        if 'max_words' in filters:
            results = [r for r in results if r['word_count'] <= filters['max_words']]
        
        return results
    
    def get_tags(self):
        """获取所有标签"""
        if not self.tags.get('tags'):
            self._index_reports()
        
        return self.tags['tags']
    
    def find_related(self, filepath, max_results=10):
        """查找相关报告"""
        if not self.state.get('index'):
            self._index_reports()
        
        # 找到目标报告
        target = None
        for entry in self.state['index']:
            if entry['file'] == filepath or filepath in entry['file']:
                target = entry
                break
        
        if not target:
            return []
        
        # 基于标签相似度查找相关报告
        results = []
        target_tags = set(target['tags'])
        
        for entry in self.state['index']:
            if entry['file'] == target['file']:
                continue
            
            entry_tags = set(entry['tags'])
            if not entry_tags:
                continue
            
            # Jaccard 相似度
            similarity = len(target_tags & entry_tags) / len(target_tags | entry_tags)
            
            if similarity > 0.2:
                results.append({
                    **entry,
                    'similarity': round(similarity, 3)
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]
    
    def show_stats(self):
        """显示检索统计"""
        print('='*60)
        print('Report Search Statistics')
        print('='*60)
        
        if not self.state.get('index'):
            self._index_reports()
        
        total = len(self.state['index'])
        tags = self.get_tags()
        
        # 按日期统计
        dates = [r['date'] for r in self.state['index'] if r['date']]
        if dates:
            earliest = min(dates)
            latest = max(dates)
        else:
            earliest = latest = 'N/A'
        
        # 按字数统计
        word_counts = [r['word_count'] for r in self.state['index']]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        
        print(f'Total reports: {total}')
        print(f'Date range: {earliest} to {latest}')
        print(f'Average word count: {avg_words:.0f}')
        print(f'Total tags: {len(tags)}')
        print('\nTop 10 tags:')
        
        sorted_tags = sorted(tags.items(), key=lambda x: -x[1])[:10]
        for tag, count in sorted_tags:
            print(f'  #{tag}: {count}')
        
        print(f'\nLast indexed: {self.state.get("last_index", "Never")}')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Search Engine')
    parser.add_argument('--search', type=str, help='Search reports')
    parser.add_argument('--tags', action='store_true', help='Show all tags')
    parser.add_argument('--filter', action='store_true', help='Filter reports')
    parser.add_argument('--type', type=str, help='Filter by type')
    parser.add_argument('--related', type=str, help='Find related reports')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--index', action='store_true', help='Rebuild index')
    
    args = parser.parse_args()
    
    engine = ReportSearchEngine()
    
    if args.index:
        engine._index_reports()
    elif args.search:
        print(f'Searching for: {args.search}')
        print('='*60)
        results = engine.search(args.search)
        if results:
            for r in results:
                print(f"[{r['score']:.2f}] {r['title']}")
                print(f"  File: {r['file']}")
                print(f"  Tags: {', '.join(r['tags'])}")
                print()
        else:
            print('No results found')
    elif args.tags:
        tags = engine.get_tags()
        print('='*60)
        print('All Tags')
        print('='*60)
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            print(f'#{tag}: {count}')
    elif args.filter:
        filters = {}
        if args.type:
            filters['tags'] = args.type.lower()
        results = engine.filter_by(**filters)
        print(f'Found {len(results)} reports')
        for r in results[:20]:
            print(f"  {r['title']}")
    elif args.related:
        results = engine.find_related(args.related)
        print(f'Related reports to: {args.related}')
        print('='*60)
        for r in results:
            print(f"[{r['similarity']:.2f}] {r['title']}")
    elif args.stats:
        engine.show_stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
