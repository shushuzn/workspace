#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classical/Modern Chinese Ratio Detector
Detect the ratio of classical to modern Chinese in chapters
"""

import os
import re
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"

# Classical Chinese keywords (common in classical writing)
CLASSICAL_KEYWORDS = [
    '之', '乎', '者', '也', '矣', '焉', '哉',
    '乃', '其', '且', '然', '而', '则', '虽',
    '若', '如', '似', '犹', '尚', '岂', '何',
    '暮色', '渐', '愈', '甚', '颇', '皆', '俱',
]

# Modern Chinese keywords
MODERN_KEYWORDS = [
    '的', '了', '在', '是', '有', '和', '就',
    '不', '人', '都', '一', '就', '这', '也',
    '着', '他', '她', '我', '你', '我们', '他们',
]

def detect_ratio(content):
    """Detect classical/modern ratio"""
    classical_count = sum(content.count(word) for word in CLASSICAL_KEYWORDS)
    modern_count = sum(content.count(word) for word in MODERN_KEYWORDS)
    
    total = classical_count + modern_count
    
    if total == 0:
        return {
            'classical_ratio': 0,
            'modern_ratio': 0,
            'classical_count': 0,
            'modern_count': 0,
        }
    
    return {
        'classical_ratio': classical_count / total * 100,
        'modern_ratio': modern_count / total * 100,
        'classical_count': classical_count,
        'modern_count': modern_count,
    }

def check_all_chapters():
    """Check all chapters"""
    print("=" * 60)
    print("Classical/Modern Chinese Ratio Report")
    print("=" * 60)
    print(f"Folder: {DRAFTS_FOLDER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Scan draft folder
    draft_files = []
    for file in os.listdir(DRAFTS_FOLDER):
        if file.endswith('.md') and file.startswith('第'):
            match = re.search(r'第 (\d+) 章', file)
            if match:
                chapter_num = int(match.group(1))
                draft_files.append((chapter_num, os.path.join(DRAFTS_FOLDER, file)))
    
    draft_files.sort(key=lambda x: x[0])
    
    # Check ratio
    print("Chapter Ratio:")
    print("-" * 60)
    print(f"{'Chapter':<10} {'Classical%':<12} {'Modern%':<12} {'Status':<15}")
    print("-" * 60)
    
    for chapter_num, file_path in draft_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ratio = detect_ratio(content)
        
        classical_pct = f"{ratio['classical_ratio']:.1f}%".ljust(12)
        modern_pct = f"{ratio['modern_ratio']:.1f}%".ljust(12)
        
        # Target ratio: 70% modern, 30% classical
        if 25 <= ratio['classical_ratio'] <= 35:
            status = '✅ OK'
        elif ratio['classical_ratio'] < 25:
            status = '⚠️ Too modern'
        else:
            status = '⚠️ Too classical'
        
        print(f"第{chapter_num:<7}章 {classical_pct} {modern_pct} {status}")
    
    print("-" * 60)
    print()
    
    print("Suggestions:")
    print("  Target ratio: 70% modern, 30% classical")
    print("  If too modern: add more classical expressions")
    print("  If too classical: simplify language")
    print()
    print("=" * 60)

if __name__ == "__main__":
    check_all_chapters()
