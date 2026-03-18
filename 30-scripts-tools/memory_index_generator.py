#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Index Generator - 记忆索引生成器

功能:
- 扫描 MEMORY.md 和日常笔记
- 提取标签和元数据
- 生成搜索索引 (JSON)
- 支持增量更新

使用:
  py memory_index_generator.py [--rebuild]
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
MEMORY_FILE = WORKSPACE / 'MEMORY.md'
INDEX_FILE = MEMORY_DIR / 'memory_index.json'


class MemoryIndexGenerator:
    def __init__(self):
        self.entries = []
        self.tag_index = {}
        
    def parse_memory_file(self) -> list:
        """解析 MEMORY.md 提取条目"""
        if not MEMORY_FILE.exists():
            print(f"[ERROR] MEMORY.md not found")
            return []
        
        content = MEMORY_FILE.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        entries = []
        current_entry = None
        header_pattern = re.compile(r'^(#{2,4})\s+(.*?)$')
        tag_pattern = re.compile(r'\*\*Tags:\*\*\s*(.+?)$')
        backlink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        
        for i, line in enumerate(lines, 1):
            header_match = header_pattern.match(line)
            if header_match:
                if current_entry:
                    current_entry['line_end'] = i - 1
                    entries.append(current_entry)
                
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                id_match = re.match(r'\[([A-Z]+-\d+)\]\s*(.*)', title)
                if id_match:
                    entry_id = id_match.group(1)
                    entry_title = id_match.group(2)
                else:
                    entry_id = f"SEC-{len(entries)+1:03d}"
                    entry_title = title
                
                current_entry = {
                    'id': entry_id,
                    'title': entry_title,
                    'line_start': i,
                    'line_end': i,
                    'level': level,
                    'tags': [],
                    'backlinks': []
                }
                
                for j in range(i, min(i+5, len(lines)+1)):
                    if j-1 < len(lines):
                        tag_match = tag_pattern.match(lines[j-1])
                        if tag_match:
                            tags_str = tag_match.group(1)
                            tags = re.findall(r'#([\w-]+)', tags_str)
                            current_entry['tags'] = [f'#{tag}' for tag in tags]
                            break
                
                for bl in backlink_pattern.findall(line):
                    if bl not in current_entry['backlinks']:
                        current_entry['backlinks'].append(bl)
        
        if current_entry:
            current_entry['line_end'] = len(lines)
            entries.append(current_entry)
        
        self.entries = entries
        return entries
    
    def build_tag_index(self) -> dict:
        """构建标签索引"""
        tag_index = {}
        for entry in self.entries:
            for tag in entry['tags']:
                if tag not in tag_index:
                    tag_index[tag] = []
                tag_index[tag].append(entry['id'])
        
        self.tag_index = tag_index
        return tag_index
    
    def generate_index(self) -> dict:
        """生成完整索引"""
        print(f"[PARSE] Scanning MEMORY.md...")
        self.parse_memory_file()
        print(f"   Found {len(self.entries)} entries")
        
        print(f"[TAGS] Building tag index...")
        self.build_tag_index()
        print(f"   Found {len(self.tag_index)} unique tags")
        
        index = {
            'version': '1.0',
            'updated': datetime.now().isoformat(),
            'total_entries': len(self.entries),
            'total_tags': len(self.tag_index),
            'entries': self.entries,
            'tag_index': self.tag_index
        }
        
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"[SAVE] Writing index to {INDEX_FILE}...")
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"[DONE] Index generation complete!")
        return index
    
    def load_index(self) -> dict:
        """加载现有索引"""
        if not INDEX_FILE.exists():
            return None
        
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Index Generator')
    parser.add_argument('--rebuild', action='store_true', help='Force rebuild index')
    
    args = parser.parse_args()
    
    generator = MemoryIndexGenerator()
    
    if args.rebuild or not INDEX_FILE.exists():
        generator.generate_index()
    else:
        print(f"[OK] Index exists. Use --rebuild to regenerate.")
        index = generator.load_index()
        print(f"   Entries: {index['total_entries']}")
        print(f"   Tags: {index['total_tags']}")
        print(f"   Updated: {index['updated']}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
