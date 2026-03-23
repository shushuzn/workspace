#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensitive Content Detector
Detect political, pornographic, violent content
"""

import os
import re
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"

# Sensitive keywords
SENSITIVE_WORDS = {
    'political': [
        '国家领导人', '政府', '政治', '共产党', '国民党',
        '文革', '六四', '天安门', '敏感事件',
    ],
    'pornographic': [
        '色情', '淫秽', '性爱', '裸体', '性交',
    ],
    'violent': [
        '杀人', '自杀', '血腥', '暴力', '恐怖',
        '砍', '刺', '捅', '血', '尸体',
    ],
}

def detect_sensitive_content(content):
    """Detect sensitive content"""
    found = {
        'political': [],
        'pornographic': [],
        'violent': [],
    }

    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in content:
                found[category].append(word)

    return found

def check_all_chapters():
    """Check all chapters"""
    print("=" * 60)
    print("Sensitive Content Detection Report")
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

    # Check sensitive content
    issues_found = False

    for chapter_num, file_path in draft_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        found = detect_sensitive_content(content)

        has_issues = any(len(v) > 0 for v in found.values())

        if has_issues:
            issues_found = True
            print(f"第{chapter_num}章:")
            for category, words in found.items():
                if words:
                    print(f"  {category}: {', '.join(words)}")
            print()

    if not issues_found:
        print("✅ No sensitive content detected!")
        print()

    print("Categories:")
    print("  - Political: 政治敏感内容")
    print("  - Pornographic: 色情内容")
    print("  - Violent: 暴力内容")
    print()
    print("Suggestions:")
    print("  If sensitive content found, please revise or remove")
    print()
    print("=" * 60)

if __name__ == "__main__":
    check_all_chapters()
