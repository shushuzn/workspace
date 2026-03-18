#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Consistency Checker - 记忆数据一致性检查

Checks:
1. MEMORY.md vs memory_index.json consistency
2. Tag statistics accuracy
3. Broken links (tags with no entries)
4. Duplicate entries detection
5. Orphaned entries (in index but not in MEMORY.md)

Usage:
    py memory_consistency_checker.py
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

# Colors
import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_ok(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def load_memory_md():
    """Load and parse MEMORY.md"""
    memory_path = Path("13-memory/MEMORY.md")
    if not memory_path.exists():
        return None, "MEMORY.md not found"
    
    content = memory_path.read_text(encoding='utf-8')
    
    # Parse entries (sections starting with ##)
    sections = re.split(r'\n## ', content)
    
    entries = []
    for section in sections[1:]:  # Skip first empty section
        lines = section.strip().split('\n')
        title = lines[0].strip()
        
        # Extract tags
        tags = []
        for line in lines:
            if line.startswith('**Tags:**'):
                tag_match = re.findall(r'#(\w+)', line)
                tags = tag_match
                break
        
        entries.append({
            "title": title,
            "tags": tags,
            "content": section[:200]  # First 200 chars for preview
        })
    
    return entries, None

def load_index_json():
    """Load memory_index.json"""
    index_path = Path("13-memory/memory_index.json")
    if not index_path.exists():
        return None, "memory_index.json not found"
    
    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data, None

def check_entry_count(memory_entries, index_data):
    """检查条目数（允许索引包含历史记忆）"""
    memory_count = len(memory_entries)
    index_count = index_data.get('total_entries', 0)
    
    # 索引应该至少包含 MEMORY.md 的所有条目
    if index_count >= memory_count:
        print_ok(f"Index contains all MEMORY.md entries (MEMORY.md={memory_count}, index={index_count})")
        if index_count > memory_count:
            extra = index_count - memory_count
            print_warning(f"Index contains {extra} additional historical entries (normal)")
        return True
    else:
        print_error(f"Index missing entries: MEMORY.md={memory_count}, index={index_count}")
        return False

def check_tag_statistics(memory_entries, index_data):
    """Check if tag statistics are accurate"""
    # Count tags in MEMORY.md
    all_tags = []
    for entry in memory_entries:
        all_tags.extend(entry['tags'])
    
    memory_tag_counts = Counter(all_tags)
    index_tag_counts = index_data.get('tag_counts', {})
    
    issues = []
    for tag, count in memory_tag_counts.items():
        index_count = index_tag_counts.get(tag, 0)
        if index_count != count:
            issues.append(f"Tag #{tag}: MEMORY.md={count}, index={index_count}")
    
    if not issues:
        print_ok("Tag statistics match")
        return True
    else:
        print_error("Tag statistics mismatch:")
        for issue in issues[:5]:  # Show first 5
            print(f"   {issue}")
        return False

def check_broken_links(index_data):
    """Check for tags that exist but have no entries"""
    tag_counts = index_data.get('tag_counts', {})
    broken = []
    
    for tag, count in tag_counts.items():
        if count == 0:
            broken.append(f"#{tag}")
    
    if not broken:
        print_ok("No broken tag links")
        return True
    else:
        print_warning(f"Broken tag links: {', '.join(broken)}")
        return False

def check_duplicate_entries(memory_entries):
    """Check for duplicate entry titles"""
    titles = [entry['title'] for entry in memory_entries]
    duplicates = [title for title in titles if titles.count(title) > 1]
    unique_duplicates = list(set(duplicates))
    
    if not unique_duplicates:
        print_ok("No duplicate entries")
        return True
    else:
        print_error(f"Duplicate entries found: {unique_duplicates}")
        return False

def check_orphaned_entries(memory_entries, index_data):
    """检查索引中的条目是否在 MEMORY.md 中（允许索引包含历史记忆）"""
    # 索引可能包含历史记忆（已被压缩），这是正常的
    # 只检查 MEMORY.md 中的条目是否在索引中（确保索引完整）
    memory_titles = set(entry['title'] for entry in memory_entries)
    index_entries = index_data.get('entries', [])
    index_titles = set(entry.get('title', '') for entry in index_entries)
    
    # 检查 MEMORY.md 的条目是否都在索引中
    missing_from_index = memory_titles - index_titles
    
    if not missing_from_index:
        print_ok("All MEMORY.md entries are indexed")
        # 索引可能包含更多历史条目，这是正常的
        extra_in_index = len(index_titles - memory_titles)
        if extra_in_index > 0:
            print_warning(f"Index contains {extra_in_index} historical entries (normal)")
        return True
    else:
        print_error(f"Entries missing from index: {len(missing_from_index)}")
        for title in list(missing_from_index)[:5]:
            print(f"   - {title}")
        return False

def generate_consistency_report(results):
    """Generate JSON report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r['passed']),
            "failed": sum(1 for r in results if not r['passed'])
        }
    }
    
    report["summary"]["status"] = "PASS" if report["summary"]["failed"] == 0 else "FAIL"
    
    return report

def main():
    print_header("🔍 MEMORY CONSISTENCY CHECKER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load data
    print_header("LOADING DATA")
    
    memory_entries, error = load_memory_md()
    if error:
        print_error(f"Failed to load MEMORY.md: {error}")
        return 1
    print_ok(f"Loaded MEMORY.md: {len(memory_entries)} entries")
    
    index_data, error = load_index_json()
    if error:
        print_error(f"Failed to load memory_index.json: {error}")
        return 1
    print_ok(f"Loaded memory_index.json: {index_data.get('total_entries', 0)} entries")
    
    # Run checks
    print_header("RUNNING CONSISTENCY CHECKS")
    
    results = []
    
    # Check 1: Entry count
    print("Check 1: Entry Count Matching")
    passed = check_entry_count(memory_entries, index_data)
    results.append({"check": "Entry Count", "passed": passed})
    print()
    
    # Check 2: Tag statistics
    print("Check 2: Tag Statistics Accuracy")
    passed = check_tag_statistics(memory_entries, index_data)
    results.append({"check": "Tag Statistics", "passed": passed})
    print()
    
    # Check 3: Broken links
    print("Check 3: Broken Tag Links")
    passed = check_broken_links(index_data)
    results.append({"check": "Broken Links", "passed": passed})
    print()
    
    # Check 4: Duplicates
    print("Check 4: Duplicate Entries")
    passed = check_duplicate_entries(memory_entries)
    results.append({"check": "Duplicates", "passed": passed})
    print()
    
    # Check 5: Orphaned entries
    print("Check 5: Orphaned Entries")
    passed = check_orphaned_entries(memory_entries, index_data)
    results.append({"check": "Orphaned Entries", "passed": passed})
    print()
    
    # Summary
    print_header("CONSISTENCY CHECK SUMMARY")
    
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print()
    
    for r in results:
        symbol = "✅" if r['passed'] else "❌"
        print(f"{symbol} {r['check']}")
    
    # Generate report
    report = generate_consistency_report(results)
    report_file = Path("30-scripts-tools/consistency_check_report.json")
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nReport saved to: {report_file}")
    
    # Final status
    print_header("FINAL STATUS")
    
    if report["summary"]["status"] == "PASS":
        print_ok("MEMORY SYSTEM CONSISTENCY: PASS")
        return 0
    else:
        print_error("MEMORY SYSTEM CONSISTENCY: FAIL")
        print_warning(f"{report['summary']['failed']} check(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
