#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Cleanup: 60-DATA sensitive files
Target: Clean up Medium/Twitter collector files in 60-DATA
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Ensure UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "60-DATA"
BACKUP_DIR = WORKSPACE / "99-backups" / "data-cleanup-20260318"

def cleanup_sensitive_files():
    """Clean up sensitive files in 60-DATA"""
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Patterns to delete
    patterns = {
        'medium': ['**/Medium/**/*', '**/medium-*.md'],
        'twitter': ['**/Twitter/**/*', '**/twitter-*.md'],
        'aliyun': ['**/aliyun/**/*', '**/ALIYUN*'],
    }
    
    deleted_count = 0
    backup_count = 0
    
    print("[Scan] Searching for sensitive files in 60-DATA...")
    
    # Scan and delete
    for pattern_list in patterns.values():
        for pattern in pattern_list:
            try:
                for file_path in DATA_DIR.glob(pattern):
                    if file_path.is_file():
                        # Backup first
                        try:
                            rel_path = file_path.relative_to(WORKSPACE)
                            backup_path = BACKUP_DIR / rel_path
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, backup_path)
                            backup_count += 1
                        except Exception as e:
                            print(f"  [WARN] Backup failed: {file_path}")
                        
                        # Delete
                        try:
                            file_path.unlink()
                            deleted_count += 1
                            print(f"  [DEL] {file_path.relative_to(WORKSPACE)}")
                        except Exception as e:
                            print(f"  [ERROR] Delete failed: {file_path} - {e}")
            except Exception as e:
                pass  # Pattern might not match anything
    
    print(f"\n[Results]")
    print(f"  Deleted: {deleted_count} files")
    print(f"  Backed up: {backup_count} files")
    print(f"  Backup location: {BACKUP_DIR}")
    
    if deleted_count > 0:
        print(f"\n[OK] Cleanup complete! Run git add -A to stage changes.")
    else:
        print(f"\n[OK] No sensitive files found in 60-DATA.")

if __name__ == "__main__":
    cleanup_sensitive_files()
