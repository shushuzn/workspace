#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimize causal_inference_engine.py"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Ensure UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPTS_DIR = Path(__file__).parent
BACKUP_DIR = SCRIPTS_DIR.parent / "99-backups" / "causal-optimize"

def optimize_file():
    """Optimize causal_inference_engine.py"""
    src = SCRIPTS_DIR / "causal_inference_engine.py"
    
    # Create backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"causal_inference_engine.py"
    shutil.copy2(src, backup_path)
    print(f"[OK] Backup: {backup_path}")
    
    # Read file
    with open(src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_size = src.stat().st_size
    original_lines = len(lines)
    
    # Optimize
    optimized_lines = []
    prev_empty = False
    long_lines_fixed = 0
    empty_lines_removed = 0
    
    for i, line in enumerate(lines, 1):
        # Remove trailing spaces (but keep newline)
        line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
        
        # Check if empty
        if line.strip() == '':
            if prev_empty:
                # Skip consecutive empty lines
                empty_lines_removed += 1
                continue
            prev_empty = True
        else:
            prev_empty = False
            
            # Fix long lines (>120 chars)
            if len(line.rstrip()) > 120:
                # Just mark for now, don't modify complex lines
                long_lines_fixed += 1
        
        optimized_lines.append(line)
    
    # Write optimized file
    with open(src, 'w', encoding='utf-8') as f:
        f.writelines(optimized_lines)
    
    new_size = src.stat().st_size
    new_lines = len(optimized_lines)
    
    print(f"\n[Results]")
    print(f"  Lines: {original_lines} -> {new_lines} (-{original_lines - new_lines})")
    print(f"  Empty lines removed: {empty_lines_removed}")
    print(f"  Long lines found: {long_lines_fixed}")
    print(f"  Size: {original_size/1024:.1f}KB -> {new_size/1024:.1f}KB (-{(original_size - new_size)/1024:.1f}KB)")
    print(f"\n[OK] Optimization complete!")

if __name__ == "__main__":
    optimize_file()
