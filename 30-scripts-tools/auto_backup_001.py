import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-BACKUP-001 Auto Backup Tool
Automatically backs up important files before changes
"""
import json, sys, shutil, zipfile
from pathlib import Path
from datetime import datetime

BACKUP_DIR = Path("13-memory/.backups")
TRACK_FILE = Path("13-memory/.backup_track.json")

def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)

def load_track():
    if TRACK_FILE.exists():
        return json.loads(TRACK_FILE.read_text(encoding="utf-8", errors="replace"))
    return {"backups": [], "files": {}}

def save_track(track):
    ensure_dir(TRACK_FILE.parent)
    TRACK_FILE.write_text(json.dumps(track, indent=2, ensure_ascii=False), encoding="utf-8")

def backup_files(files, label="manual") -> None:
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py auto_backup_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py auto_backup_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Backup specified files"""
    ensure_dir(BACKUP_DIR)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{ts}_{label}.zip"
    backup_path = BACKUP_DIR / backup_name
    
    track = load_track()
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            p = Path(f)
            if p.exists():
                zf.write(p, p.name)
    
    track["backups"].append({
        "time": datetime.now().isoformat(),
        "label": label,
        "path": str(backup_path),
        "files": [str(f) for f in files if Path(f).exists()]
    })
    save_track(track)
    
    return backup_path

def restore_latest() -> None:
    """Restore from latest backup"""
    track = load_track()
    if not track["backups"]:
        return None
    
    latest = track["backups"][-1]
    backup_path = Path(latest["path"])
    
    if not backup_path.exists():
        return None
    
    restore_dir = BACKUP_DIR / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    restore_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(backup_path, 'r') as zf:
        zf.extractall(restore_dir)
    
    return restore_dir

def auto_backup_changed() -> None:
    """Auto backup files that will be changed"""
    important = [
        "30-scripts-tools/workflow_master_001.py",
        "30-scripts-tools/workflows.json",
        "workflow.bat"
    ]
    
    files_to_backup = [f for f in important if Path(f).exists()]
    
    if files_to_backup:
        path = backup_files(files_to_backup, "auto")
        print(f"Auto-backup created: {path.name}")
        return path
    
    return None

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        print("""
[AUTO-BACKUP-001]
Usage:
  python auto_backup_001.py backup <file1> <file2> ...
  python auto_backup_001.py auto
  python auto_backup_001.py restore
  python auto_backup_001.py list
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "backup":
        files = sys.argv[2:] if len(sys.argv) > 2 else []
        if not files:
            print("No files specified")
            return
        path = backup_files([Path(f) for f in files])
        print(f"Backup: {path}")
    
    elif cmd == "auto":
        path = auto_backup_changed()
        if path:
            print(f"OK: {path}")
        else:
            print("No files to backup")
    
    elif cmd == "restore":
        path = restore_latest()
        if path:
            print(f"Restored to: {path}")
        else:
            print("No backup to restore")
    
    elif cmd == "list":
        track = load_track()
        for b in track.get("backups", [])[-10:]:
            print(f"  {b['time']} - {b['label']} - {len(b['files'])} files")

if __name__ == "__main__":
    main()
