#!/usr/bin/env python3
"""
Memory Cleanup & Compression - Remove duplicates and compress
"""
import os
import shutil
from datetime import datetime

WORKSPACE = r"C:\Users\华为\.copaw"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_MD = os.path.join(WORKSPACE, "MEMORY.md")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")

def find_duplicates():
    """Find duplicate memory files"""
    duplicates = []
    
    if not os.path.exists(MEMORY_DIR):
        return duplicates
    
    files = [f for f in os.listdir(MEMORY_DIR) if f.endswith('.md')]
    
    for f in files:
        # Pattern 1: _from_13-memory duplicates
        if '_from_13-memory' in f:
            duplicates.append(f)
        # Pattern 2: Backup files
        elif f.startswith('MEMORY.md.') and 'backup' in f.lower():
            duplicates.append(f)
        # Pattern 3: Fixed/temp files
        elif 'fixed' in f.lower() or 'recover' in f.lower():
            if f != 'MEMORY.md':  # Keep main file
                duplicates.append(f)
    
    return duplicates

def archive_files(files):
    """Move files to archive"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archived = []
    
    for f in files:
        src = os.path.join(MEMORY_DIR, f)
        dst = os.path.join(ARCHIVE_DIR, f)
        
        if os.path.exists(src):
            try:
                shutil.move(src, dst)
                archived.append(f)
                print(f"  Archived: {f}")
            except Exception as e:
                print(f"  Failed: {f} - {e}")
    
    return archived

def compress_memory_md():
    """Compress MEMORY.md by removing redundant sections"""
    if not os.path.exists(MEMORY_MD):
        return None
    
    with open(MEMORY_MD, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    original_lines = content.count('\n')
    
    # Remove excessive blank lines (3+ -> 2)
    import re
    compressed = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove trailing whitespace
    compressed = '\n'.join(line.rstrip() for line in compressed.split('\n'))
    
    compressed_size = len(compressed)
    compressed_lines = compressed.count('\n')
    
    savings = original_size - compressed_size
    savings_pct = (savings / original_size * 100) if original_size > 0 else 0
    
    if savings > 0:
        with open(MEMORY_MD, 'w', encoding='utf-8') as f:
            f.write(compressed)
        print(f"  Compressed: {original_size} -> {compressed_size} bytes (-{savings_pct:.1f}%)")
    
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'original_lines': original_lines,
        'compressed_lines': compressed_lines,
        'savings_bytes': savings,
        'savings_pct': savings_pct
    }

def main():
    print("=" * 60)
    print("Memory Cleanup & Compression")
    print("=" * 60)
    print()
    
    # Step 1: Find duplicates
    print("Step 1: Finding duplicates...")
    duplicates = find_duplicates()
    print(f"  Found {len(duplicates)} duplicate/backup files")
    print()
    
    # Step 2: Archive duplicates
    if duplicates:
        print("Step 2: Archiving duplicates...")
        archived = archive_files(duplicates)
        print(f"  Archived {len(archived)} files")
        print()
    else:
        print("Step 2: No duplicates to archive")
        print()
    
    # Step 3: Compress MEMORY.md
    print("Step 3: Compressing MEMORY.md...")
    result = compress_memory_md()
    if result:
        print(f"  Original: {result['original_size']} bytes ({result['original_lines']} lines)")
        print(f"  Compressed: {result['compressed_size']} bytes ({result['compressed_lines']} lines)")
        print(f"  Savings: {result['savings_bytes']} bytes (-{result['savings_pct']:.1f}%)")
    else:
        print("  MEMORY.md not found")
    print()
    
    # Summary
    print("=" * 60)
    print("Summary:")
    print(f"  - Duplicates archived: {len(duplicates)}")
    if result:
        print(f"  - MEMORY.md compressed: -{result['savings_pct']:.1f}%")
    print(f"  - Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
