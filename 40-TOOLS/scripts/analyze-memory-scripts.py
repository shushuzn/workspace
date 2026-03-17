#!/usr/bin/env python3
"""
Memory Scripts Analyzer - Find duplicates and suggest merges
"""

import os
import re
import hashlib
from pathlib import Path
from collections import defaultdict

# Configuration
SCRIPTS_DIR = Path(__file__).parent
BACKUP_DIR = Path(__file__).parent.parent / 'backup' / 'memory-scripts'

# Script categories
CATEGORIES = {
    'distiller': ['distill', 'compress', 'extract'],
    'scorer': ['score', 'assess', 'evaluate', 'quality'],
    'search': ['search', 'retrieve', 'find'],
    'forgetting': ['forget', 'archive', 'cleanup', 'delete'],
    'conflict': ['conflict', 'resolve', 'detect'],
    'evolution': ['evolve', 'evolution', 'adaptive', 'improve'],
    'association': ['associate', 'link', 'graph', 'kg'],
    'dashboard': ['dashboard', 'visualize', 'monitor'],
    'fix': ['fix', 'repair', 'correct'],
    'core': ['engine', 'orchestrator', 'ops', 'autonomous'],
}

def get_script_category(filename):
    """Categorize script by filename"""
    name_lower = filename.lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return 'other'

def calculate_similarity(file1, file2):
    """Calculate code similarity between two files"""
    try:
        with open(file1, 'r', encoding='utf-8') as f1:
            content1 = f1.read()
        with open(file2, 'r', encoding='utf-8') as f2:
            content2 = f2.read()
        
        # Simple similarity: count common lines
        lines1 = set(content1.split('\n'))
        lines2 = set(content2.split('\n'))
        
        if not lines1 or not lines2:
            return 0.0
        
        common = len(lines1 & lines2)
        total = len(lines1 | lines2)
        
        return (common / total) * 100 if total > 0 else 0.0
    except:
        return 0.0

def find_duplicates():
    """Find duplicate and similar scripts"""
    scripts = list(SCRIPTS_DIR.glob('memory*.py'))
    
    # Group by category
    by_category = defaultdict(list)
    for script in scripts:
        category = get_script_category(script.name)
        by_category[category].append(script)
    
    print("=" * 80)
    print("MEMORY SCRIPTS ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nTotal scripts found: {len(scripts)}")
    print(f"Categories: {len(by_category)}")
    
    # Analyze each category
    duplicates = []
    
    for category, script_list in sorted(by_category.items()):
        if len(script_list) > 1:
            print(f"\n{'='*80}")
            print(f"Category: {category.upper()} ({len(script_list)} scripts)")
            print(f"{'='*80}")
            
            for i, script1 in enumerate(script_list):
                for script2 in script_list[i+1:]:
                    similarity = calculate_similarity(script1, script2)
                    if similarity > 30:  # Threshold for potential duplicate
                        duplicates.append((script1, script2, similarity))
                        print(f"\n  ⚠️  SIMILAR: {script1.name} <-> {script2.name}")
                        print(f"     Similarity: {similarity:.1f}%")
                        
                        # Suggest action
                        if similarity > 70:
                            print(f"     👉 RECOMMENDATION: MERGE these scripts")
                        elif similarity > 50:
                            print(f"     👉 RECOMMENDATION: Review for consolidation")
                        else:
                            print(f"     👉 RECOMMENDATION: Keep separate but document differences")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY & RECOMMENDATIONS")
    print(f"{'='*80}")
    
    # Group duplicates by merge candidates
    merge_candidates = [(s1, s2, sim) for s1, s2, sim in duplicates if sim > 70]
    review_candidates = [(s1, s2, sim) for s1, s2, sim in duplicates if 50 <= sim <= 70]
    
    print(f"\nTotal duplicate pairs found: {len(duplicates)}")
    print(f"  - High similarity (>70%): {len(merge_candidates)} pairs → MERGE")
    print(f"  - Medium similarity (50-70%): {len(review_candidates)} pairs → REVIEW")
    print(f"  - Low similarity (30-50%): {len(duplicates) - len(merge_candidates) - len(review_candidates)} pairs → DOCUMENT")
    
    if merge_candidates:
        print(f"\n📋 MERGE ACTION LIST:")
        for i, (s1, s2, sim) in enumerate(merge_candidates, 1):
            print(f"  {i}. Merge {s1.name} + {s2.name} ({sim:.0f}% similar)")
    
    # Estimate savings
    estimated_savings = len(merge_candidates) + (len(review_candidates) // 2)
    print(f"\n💾 ESTIMATED SAVINGS:")
    print(f"  - Scripts to remove: ~{estimated_savings}")
    print(f"  - Code reduction: ~{estimated_savings * 2:.0f}%")
    
    return duplicates

if __name__ == '__main__':
    find_duplicates()
