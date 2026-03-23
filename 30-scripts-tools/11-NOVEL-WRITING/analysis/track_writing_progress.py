#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Writing Progress Tracker
Track writing progress with charts and statistics
"""

import os
import re
import json
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"
PROGRESS_FILE = r"D:\OpenClaw\workspace\30-scripts\writing_progress.json"

def count_chapter_stats(file_path):
    """Count statistics for single chapter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    word_count = len(re.sub(r'\s+', '', content))

    # Count AI rate from report
    ai_rate = None

    return {
        'word_count': word_count,
        'ai_rate': ai_rate,
    }

def load_previous_progress():
    """Load previous progress data"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'history': []}

def track_progress():
    """Track writing progress"""
    print("=" * 60)
    print("Writing Progress Report")
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

    # Count stats
    chapters = {}
    total_words = 0

    for chapter_num, file_path in draft_files:
        stats = count_chapter_stats(file_path)
        chapters[chapter_num] = stats
        total_words += stats['word_count']

    # Load previous progress
    previous = load_previous_progress()

    # Add new record
    current_record = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_chapters': len(chapters),
        'total_words': total_words,
        'chapters': chapters
    }

    previous['history'].append(current_record)

    # Save progress
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(previous, f, ensure_ascii=False, indent=2)

    # Print report
    print("Current Progress:")
    print("-" * 60)
    print(f"  Total chapters: {len(chapters)}")
    print(f"  Total words: {total_words}")
    print(f"  Average words/chapter: {total_words // len(chapters) if chapters else 0}")
    print()

    print("Chapter Details:")
    print("-" * 60)
    print(f"{'Chapter':<10} {'Words':<10} {'Status':<15}")
    print("-" * 60)

    for chapter_num in sorted(chapters.keys()):
        stats = chapters[chapter_num]
        word_count = str(stats['word_count']).ljust(10)
        status = '✅ 3000+' if stats['word_count'] >= 3000 else '❌ <3000'

        print(f"第{chapter_num:<7}章 {word_count} {status}")

    print("-" * 60)
    print()

    # Show trend
    if len(previous['history']) > 1:
        print("Progress Trend:")
        print("-" * 60)
        for record in previous['history'][-5:]:  # Last 5 records
            print(f"  {record['date']}: {record['total_chapters']} chapters, {record['total_words']} words")
        print("-" * 60)
        print()

    print(f"Progress file saved to: {PROGRESS_FILE}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    track_progress()
