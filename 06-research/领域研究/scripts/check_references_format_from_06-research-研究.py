#!/usr/bin/env python3
"""
Check references format for Carbon journal (Elsevier)
"""
import re
from pathlib import Path

def main():
    ref_file = Path("D:/OpenClaw/workspace/11-research/paper/references.md")
    
    with open(ref_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all references
    refs = re.findall(r'(\[\d+\].+?)(?=\n\[\d+\]|\n---|\Z)', content, re.DOTALL)
    
    print("=" * 70)
    print("Carbon Journal Reference Format Check")
    print("=" * 70)
    print(f"\nTotal references: {len(refs)}\n")
    
    issues_count = 0
    
    for i, ref in enumerate(refs, 1):
        ref = ref.strip()
        issues = []
        
        # Check if starts with [number]
        if not re.match(r'^\[\d+\]', ref):
            issues.append("Missing number [X]")
        
        # Check if journal name is italicized (*Journal*)
        if '*' not in ref:
            issues.append("Journal/book name not italicized")
        
        # Check year format
        if not re.search(r'\(20\d{2}\)\.$', ref.strip()):
            if not re.search(r'20\d{2}\.$', ref.strip()):
                issues.append("Year format may be incorrect")
        
        if issues:
            ref_num = re.match(r'\[(\d+)\]', ref)
            ref_num = ref_num.group(1) if ref_num else str(i)
            
            print(f"[{ref_num}] [!] Issues found:")
            for issue in issues:
                print(f"    - {issue}")
            print()
            issues_count += 1
    
    if issues_count == 0:
        print("[OK] All references format is basically correct!\n")
    else:
        print("=" * 70)
        print(f"Found {issues_count} references with format issues\n")
    
    # Carbon format example
    print("=" * 70)
    print("Carbon Journal Standard Format Example:")
    print("=" * 70)
    print("""
Journal Article:
[1] Author, A., Author, B. Title of the paper. Journal Name (italic) Volume(Issue), Page-Page, Year.

Book:
[2] Author, A. Title of the Book (italic). Publisher, Year.

Current format (mostly correct):
[1] Lin, J., Peng, Z., Liu, Y. (2014). Laser-induced porous graphene films. Nature Communications, 5(1), 5714.
    """)

if __name__ == "__main__":
    main()
