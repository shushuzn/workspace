#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Manager
Check chapter naming conventions and compare with outline
"""

import os
import re
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"
OUTLINE_FILE = r"D:\OpenClaw\workspace\50-novels\world-building\九卷大纲_高中设定_v5.0.md"

def check_chapter_naming(file_name):
    """Check if chapter naming follows convention"""
    # Expected format: 第 X 章_XXXX.md
    pattern = r'第 (\d+) 章_(.+)\.md'
    match = re.match(pattern, file_name)

    if match:
        chapter_num = int(match.group(1))
        title = match.group(2)

        # Check title length (should be 4+4 characters roughly)
        title_parts = title.split('_')

        issues = []
        if len(title_parts) != 2:
            issues.append("标题格式不是'XXXX_XXXX'")

        return {
            'valid': True,
            'chapter_num': chapter_num,
            'title': title,
            'issues': issues
        }
    else:
        return {
            'valid': False,
            'chapter_num': None,
            'title': None,
            'issues': ["文件名不符合'第 X 章_XXXX.md'格式"]
        }

def compare_with_outline(draft_chapters, outline_chapters):
    """Compare draft chapters with outline"""
    missing = []
    extra = []

    draft_nums = set(draft_chapters.keys())
    outline_nums = set(outline_chapters.keys())

    missing = outline_nums - draft_nums
    extra = draft_nums - outline_nums

    return {
        'missing': sorted(list(missing)),
        'extra': sorted(list(extra)),
        'matched': len(draft_nums & outline_nums)
    }

def scan_outline():
    """Scan outline file for chapter list"""
    outline_chapters = {}

    if not os.path.exists(OUTLINE_FILE):
        return outline_chapters

    with open(OUTLINE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find chapter references in outline
    pattern = r'第 (\d+)-(\d+) 章.*?([\u4e00-\u9fa5]{4}.*?[\u4e00-\u9fa5]{4})'
    matches = re.findall(pattern, content)

    for match in matches:
        start = int(match[0])
        end = int(match[1])
        title = match[2]

        for i in range(start, end + 1):
            outline_chapters[i] = title

    return outline_chapters

def manage_chapters():
    """Manage all chapters"""
    print("=" * 60)
    print("Chapter Manager Report")
    print("=" * 60)
    print(f"Folder: {DRAFTS_FOLDER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Scan draft folder
    draft_chapters = {}
    invalid_files = []

    for file in os.listdir(DRAFTS_FOLDER):
        if file.endswith('.md') and file.startswith('第'):
            result = check_chapter_naming(file)
            if result['valid']:
                draft_chapters[result['chapter_num']] = {
                    'file': file,
                    'title': result['title'],
                    'issues': result['issues']
                }
            else:
                invalid_files.append({
                    'file': file,
                    'issues': result['issues']
                })

    # Scan outline
    outline_chapters = scan_outline()

    # Compare
    comparison = compare_with_outline(draft_chapters, outline_chapters)

    # Print report
    print("Chapter Naming Status:")
    print("-" * 60)
    print(f"{'Chapter':<10} {'Title':<30} {'Issues':<20}")
    print("-" * 60)

    for chapter_num in sorted(draft_chapters.keys()):
        chapter = draft_chapters[chapter_num]
        title = chapter['title'][:28].ljust(30)
        issues = ','.join(chapter['issues']) if chapter['issues'] else '✅ OK'

        print(f"第{chapter_num:<7}章 {title} {issues}")

    print("-" * 60)
    print()

    if invalid_files:
        print("Invalid Files:")
        print("-" * 60)
        for item in invalid_files:
            print(f"  {item['file']}: {'; '.join(item['issues'])}")
        print("-" * 60)
        print()

    print("Outline Comparison:")
    print(f"  Draft chapters: {len(draft_chapters)}")
    print(f"  Outline chapters: {len(outline_chapters)}")
    print(f"  Matched: {comparison['matched']}")
    print(f"  Missing: {comparison['missing'][:10]}{'...' if len(comparison['missing']) > 10 else ''}")
    print(f"  Extra: {comparison['extra'][:10]}{'...' if len(comparison['extra']) > 10 else ''}")
    print()

    # Save report
    report = {
        'draft_chapters': draft_chapters,
        'invalid_files': invalid_files,
        'outline_chapters': outline_chapters,
        'comparison': comparison
    }

    report_file = os.path.join(DRAFTS_FOLDER, "chapter_manager_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Report saved to: {report_file}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    manage_chapters()
