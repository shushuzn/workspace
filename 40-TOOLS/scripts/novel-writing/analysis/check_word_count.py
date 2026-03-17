#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Word Count Checker
Detect word count of all chapters in drafts folder
Ensure each chapter reaches target words
"""

import os
import re
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"
TARGET_WORD_COUNT = 3000  # Modified target: 3000 words/chapter

def count_chinese_words(text):
    """Count Chinese words including punctuation"""
    text = re.sub(r'\s+', '', text)
    return len(text)

def check_chapter_word_count(file_path):
    """Check single chapter word count"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        word_count = count_chinese_words(content)
        
        return {
            'file': file_path,
            'name': os.path.basename(file_path),
            'word_count': word_count,
            'status': 'PASS' if word_count >= TARGET_WORD_COUNT else 'FAIL',
            'gap': TARGET_WORD_COUNT - word_count if word_count < TARGET_WORD_COUNT else 0
        }
    except Exception as e:
        return {
            'file': file_path,
            'name': os.path.basename(file_path),
            'word_count': 0,
            'status': 'ERROR',
            'error': str(e)
        }

def scan_drafts_folder():
    """Scan drafts folder"""
    print("=" * 60)
    print("Chapter Word Count Report")
    print("=" * 60)
    print(f"Folder: {DRAFTS_FOLDER}")
    print(f"Target: {TARGET_WORD_COUNT} words/chapter")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    draft_files = []
    for file in os.listdir(DRAFTS_FOLDER):
        if file.endswith('.md') and file.startswith('第'):
            draft_files.append(os.path.join(DRAFTS_FOLDER, file))
    
    draft_files.sort(key=lambda x: int(re.search(r'第 (\d+) 章', x).group(1)) if re.search(r'第 (\d+) 章', x) else 0)
    
    results = []
    for file_path in draft_files:
        result = check_chapter_word_count(file_path)
        results.append(result)
    
    print("Chapter Statistics:")
    print("-" * 60)
    print(f"{'Chapter':<40} {'Words':<10} {'Status':<10}")
    print("-" * 60)
    
    total_words = 0
    passed_chapters = 0
    
    for result in results:
        chapter_name = result['name'][:38].ljust(40)
        word_count = str(result['word_count']).ljust(10)
        status = result['status'].ljust(10)
        
        if result['status'] == 'FAIL':
            status += f" (-{result['gap']})"
        
        print(f"{chapter_name} {word_count} {status}")
        
        total_words += result['word_count']
        if result['word_count'] >= TARGET_WORD_COUNT:
            passed_chapters += 1
    
    print("-" * 60)
    print()
    
    print("Summary:")
    print(f"  Total chapters: {len(results)}")
    print(f"  Passed: {passed_chapters}")
    print(f"  Failed: {len(results) - passed_chapters}")
    print(f"  Total words: {total_words}")
    print(f"  Average: {total_words // len(results) if results else 0} words/chapter")
    print()
    
    if len(results) - passed_chapters > 0:
        print("Failed Chapters:")
        print("-" * 60)
        for result in results:
            if result['word_count'] < TARGET_WORD_COUNT:
                print(f"  {result['name']}: {result['word_count']} words (need {result['gap']} more)")
        print("-" * 60)
        print()
    
    print("Suggestions:")
    if len(results) - passed_chapters > 0:
        print("  Please expand failed chapters to reach 3000 words")
        print("  Expansion directions:")
        print("    1. Add environment description")
        print("    2. Add inner monologue")
        print("    3. Add dialogue details")
        print("    4. Add plot details")
    else:
        print("  All chapters passed, keep it up!")
    
    print()
    print("=" * 60)
    
    return results

def main():
    """Main function"""
    if not os.path.exists(DRAFTS_FOLDER):
        print(f"Error: Folder not found - {DRAFTS_FOLDER}")
        return
    
    results = scan_drafts_folder()
    
    report_file = os.path.join(DRAFTS_FOLDER, "word_count_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Chapter Word Count Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target: {TARGET_WORD_COUNT} words/chapter\n")
        f.write("=" * 60 + "\n\n")
        
        for result in results:
            f.write(f"{result['name']}: {result['word_count']} words [{result['status']}]\n")
            if result['gap'] > 0:
                f.write(f"  Gap: {result['gap']} words\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"Report saved to: {report_file}")

if __name__ == "__main__":
    main()
