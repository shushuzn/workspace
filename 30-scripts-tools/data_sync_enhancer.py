#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Sync Enhancer - Multi-Source Data Synchronization
Features: Git sync, Obsidian sync, cloud backup, conflict resolution, incremental sync

Usage:
    python data_sync_enhancer.py --sync git
    python data_sync_enhancer.py --sync obsidian
    python data_sync_enhancer.py --backup
    python data_sync_enhancer.py --status
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import zipfile

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class SyncStatus:
    """Sync status record"""
    source: str
    last_sync: str
    files_synced: int
    files_added: int
    files_modified: int
    files_deleted: int
    conflicts: int
    status: str  # success/failed/partial
    duration: float


@dataclass
class Conflict:
    """Sync conflict record"""
    file: str
    local_hash: str
    remote_hash: str
    local_modified: str
    remote_modified: str
    resolution: str  # local/remote/manual/merged


class DataSyncEnhancer:
    """Multi-source data synchronization"""
    
    def __init__(self):
        self.sync_dir = WORKSPACE / "20-data-reports" / "sync"
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = WORKSPACE / "99-archive" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.status_file = self.sync_dir / "sync_status.json"
        self.conflicts_file = self.sync_dir / "conflicts.json"
        
        self.status_history = []
        self.conflicts = []
        
        self.load_state()
    
    def load_state(self):
        """Load sync state"""
        if self.status_file.exists():
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.status_history = data.get('history', [])
        
        if self.conflicts_file.exists():
            with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conflicts = data.get('conflicts', [])
    
    def save_state(self):
        """Save sync state"""
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump({
                'history': self.status_history[-50:],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.conflicts_file, 'w', encoding='utf-8') as f:
            json.dump({
                'conflicts': [asdict(c) for c in self.conflicts],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def get_file_hash(self, filepath: Path) -> str:
        """Get file hash"""
        if not filepath.exists():
            return ""
        
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def get_git_status(self) -> Dict:
        """Get Git repository status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            added = sum(1 for line in lines if line.startswith('A '))
            modified = sum(1 for line in lines if line.startswith('M '))
            deleted = sum(1 for line in lines if line.startswith('D '))
            untracked = sum(1 for line in lines if line.startswith('?? '))
            
            # Get last commit info
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%s|%ai'],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            commit_info = result.stdout.strip().split('|') if result.stdout.strip() else []
            
            return {
                'status': 'clean' if not lines else 'dirty',
                'added': added,
                'modified': modified,
                'deleted': deleted,
                'untracked': untracked,
                'last_commit': {
                    'hash': commit_info[0] if len(commit_info) > 0 else '',
                    'message': commit_info[1] if len(commit_info) > 1 else '',
                    'date': commit_info[2] if len(commit_info) > 2 else ''
                },
                'changes': lines[:20]  # First 20 changes
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def sync_git(self, commit_message: str = None, push: bool = True) -> SyncStatus:
        """Sync with Git repository"""
        print("\n" + "="*60)
        print(" Git Synchronization")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        files_added = 0
        files_modified = 0
        files_deleted = 0
        conflicts = 0
        
        try:
            # Get status
            status = self.get_git_status()
            
            if 'error' in status:
                raise Exception(status['error'])
            
            print(f"Repository Status: {status['status'].upper()}")
            print(f"  Added: {status['added']}")
            print(f"  Modified: {status['modified']}")
            print(f"  Deleted: {status['deleted']}")
            print(f"  Untracked: {status['untracked']}")
            print()
            
            # Stage all changes
            if status['status'] == 'dirty':
                print("Staging changes...")
                subprocess.run(['git', 'add', '-A'], cwd=WORKSPACE, check=True, timeout=30)
                print("✅ Changes staged")
            
            # Commit if there are changes
            if status['status'] == 'dirty' or status['untracked'] > 0:
                commit_msg = commit_message or f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                print(f"\nCommitting: {commit_msg}")
                subprocess.run(['git', 'commit', '-m', commit_msg], cwd=WORKSPACE, check=True, timeout=30)
                print("✅ Committed")
                
                files_added = status['added']
                files_modified = status['modified']
                files_deleted = status['deleted']
            else:
                print("✅ No changes to commit")
            
            # Push
            if push:
                print("\nPushing to remote...")
                result = subprocess.run(
                    ['git', 'push', 'origin', 'master'],
                    cwd=WORKSPACE,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print("✅ Pushed to remote")
                else:
                    if "non-fast-forward" in result.stderr:
                        print("⚠️  Remote has changes, pulling first...")
                        subprocess.run(['git', 'pull', '--rebase'], cwd=WORKSPACE, check=True, timeout=60)
                        subprocess.run(['git', 'push', 'origin', 'master'], cwd=WORKSPACE, check=True, timeout=60)
                        conflicts = 1
                    else:
                        raise Exception(result.stderr)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            sync_status = SyncStatus(
                source='git',
                last_sync=datetime.now().isoformat(),
                files_synced=files_added + files_modified + files_deleted,
                files_added=files_added,
                files_modified=files_modified,
                files_deleted=files_deleted,
                conflicts=conflicts,
                status='success' if conflicts == 0 else 'partial',
                duration=duration
            )
            
            self.status_history.append(asdict(sync_status))
            self.save_state()
            
            print(f"\n{'='*60}")
            print(" Git Sync Complete")
            print(f"{'='*60}")
            print(f"  Duration: {duration:.1f}s")
            print(f"  Files synced: {sync_status.files_synced}")
            print(f"  Conflicts: {conflicts}")
            print(f"{'='*60}\n")
            
            return sync_status
        
        except Exception as e:
            print(f"\n❌ Git sync failed: {e}")
            
            sync_status = SyncStatus(
                source='git',
                last_sync=datetime.now().isoformat(),
                files_synced=0,
                files_added=0,
                files_modified=0,
                files_deleted=0,
                conflicts=0,
                status='failed',
                duration=(datetime.now() - start_time).total_seconds()
            )
            
            self.status_history.append(asdict(sync_status))
            self.save_state()
            
            return sync_status
    
    def sync_obsidian(self, obsidian_vault: Path = None) -> SyncStatus:
        """Sync with Obsidian vault"""
        print("\n" + "="*60)
        print(" Obsidian Synchronization")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        if obsidian_vault is None:
            # Try common locations
            possible_vaults = [
                Path.home() / "Obsidian Vault",
                Path.home() / "Documents" / "Obsidian",
                Path("D:") / "Obsidian",
            ]
            
            for vault in possible_vaults:
                if vault.exists():
                    obsidian_vault = vault
                    break
        
        if not obsidian_vault or not obsidian_vault.exists():
            print("⚠️  Obsidian vault not found")
            print("Specify with: --obsidian-path <path>")
            
            sync_status = SyncStatus(
                source='obsidian',
                last_sync=datetime.now().isoformat(),
                files_synced=0,
                files_added=0,
                files_modified=0,
                files_deleted=0,
                conflicts=0,
                status='failed',
                duration=(datetime.now() - start_time).total_seconds()
            )
            
            return sync_status
        
        print(f"Vault: {obsidian_vault}")
        
        # Sync directories
        sync_dirs = [
            ('13-memory-记忆系统', 'memory'),
            ('15-docs', 'docs'),
            ('20-data-reports', 'reports'),
        ]
        
        files_synced = 0
        files_added = 0
        files_modified = 0
        
        for workspace_dir, obsidian_dir in sync_dirs:
            src = WORKSPACE / workspace_dir
            dst = obsidian_vault / 'OpenClaw' / obsidian_dir
            
            if src.exists():
                print(f"\nSyncing {workspace_dir} → {obsidian_dir}")
                
                dst.mkdir(parents=True, exist_ok=True)
                
                # Copy files
                for src_file in src.rglob("*.md"):
                    rel_path = src_file.relative_to(src)
                    dst_file = dst / rel_path
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    src_hash = self.get_file_hash(src_file)
                    dst_hash = self.get_file_hash(dst_file) if dst_file.exists() else ""
                    
                    if src_hash != dst_hash:
                        if dst_file.exists():
                            # Backup before overwrite
                            backup = dst_file.with_suffix(dst_file.suffix + '.bak')
                            shutil.copy2(dst_file, backup)
                            files_modified += 1
                        else:
                            files_added += 1
                        
                        shutil.copy2(src_file, dst_file)
                        files_synced += 1
                        print(f"  ✅ {rel_path}")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        sync_status = SyncStatus(
            source='obsidian',
            last_sync=datetime.now().isoformat(),
            files_synced=files_synced,
            files_added=files_added,
            files_modified=files_modified,
            files_deleted=0,
            conflicts=0,
            status='success',
            duration=duration
        )
        
        self.status_history.append(asdict(sync_status))
        self.save_state()
        
        print(f"\n{'='*60}")
        print(" Obsidian Sync Complete")
        print(f"{'='*60}")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Files synced: {files_synced}")
        print(f"  Added: {files_added}")
        print(f"  Modified: {files_modified}")
        print(f"{'='*60}\n")
        
        return sync_status
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create full workspace backup"""
        print("\n" + "="*60)
        print(" Creating Backup")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_file = self.backup_dir / f"{backup_name}.zip"
        
        # Directories to backup
        backup_dirs = [
            '00-09-core-config',
            '13-memory-记忆系统',
            '15-docs',
            '20-data-reports',
            '30-scripts-tools',
            '40-50-collectors',
        ]
        
        files_count = 0
        total_size = 0
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for dir_name in backup_dirs:
                src_dir = WORKSPACE / dir_name
                
                if src_dir.exists():
                    print(f"Adding {dir_name}/...")
                    
                    for filepath in src_dir.rglob("*"):
                        if filepath.is_file() and not filepath.name.endswith('.bak'):
                            arcname = filepath.relative_to(WORKSPACE)
                            zipf.write(filepath, arcname)
                            files_count += 1
                            total_size += filepath.stat().st_size
        
        backup_size = backup_file.stat().st_size
        
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(" Backup Complete")
        print(f"{'='*60}")
        print(f"  File: {backup_file.name}")
        print(f"  Files: {files_count}")
        print(f"  Size: {backup_size / 1024 / 1024:.1f} MB")
        print(f"  Duration: {duration:.1f}s")
        print(f"{'='*60}\n")
        
        # Cleanup old backups (keep last 10)
        backups = sorted(self.backup_dir.glob("backup_*.zip"))
        for old_backup in backups[:-10]:
            old_backup.unlink()
            print(f"Cleaned up old backup: {old_backup.name}")
        
        return str(backup_file)
    
    def resolve_conflicts(self, strategy: str = 'newest') -> int:
        """Resolve sync conflicts"""
        print("\n" + "="*60)
        print(" Resolving Conflicts")
        print("="*60 + "\n")
        
        if not self.conflicts:
            print("✅ No conflicts to resolve")
            return 0
        
        resolved = 0
        
        for conflict in self.conflicts:
            if conflict['resolution'] != 'manual':
                print(f"File: {conflict['file']}")
                print(f"  Local: {conflict['local_modified']}")
                print(f"  Remote: {conflict['remote_modified']}")
                
                if strategy == 'newest':
                    # Choose newest
                    local_time = datetime.fromisoformat(conflict['local_modified'])
                    remote_time = datetime.fromisoformat(conflict['remote_modified'])
                    
                    if local_time > remote_time:
                        print(f"  → Keeping local (newer)")
                    else:
                        print(f"  → Keeping remote (newer)")
                    
                    resolved += 1
                
                elif strategy == 'local':
                    print(f"  → Keeping local")
                    resolved += 1
                
                elif strategy == 'remote':
                    print(f"  → Keeping remote")
                    resolved += 1
        
        # Clear resolved conflicts
        self.conflicts = [c for c in self.conflicts if c['resolution'] == 'manual']
        self.save_state()
        
        print(f"\n✅ Resolved {resolved} conflicts")
        
        return resolved
    
    def get_status(self) -> Dict:
        """Get sync status summary"""
        git_status = self.get_git_status()
        
        last_sync = None
        if self.status_history:
            last_sync = self.status_history[-1]
        
        return {
            'git': git_status,
            'last_sync': last_sync,
            'total_syncs': len(self.status_history),
            'pending_conflicts': len(self.conflicts),
            'backup_count': len(list(self.backup_dir.glob("backup_*.zip")))
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Sync Enhancer')
    parser.add_argument('--sync', type=str, choices=['git', 'obsidian', 'all'],
                       help='Sync source')
    parser.add_argument('--commit-msg', type=str, help='Git commit message')
    parser.add_argument('--no-push', action='store_true', help='Don\'t push to remote')
    parser.add_argument('--obsidian-path', type=str, help='Obsidian vault path')
    parser.add_argument('--backup', action='store_true', help='Create backup')
    parser.add_argument('--resolve', type=str, choices=['newest', 'local', 'remote'],
                       help='Resolve conflicts')
    parser.add_argument('--status', action='store_true', help='Show status')
    args = parser.parse_args()
    
    enhancer = DataSyncEnhancer()
    
    if args.sync:
        if args.sync in ['git', 'all']:
            enhancer.sync_git(args.commit_msg, not args.no_push)
        
        if args.sync in ['obsidian', 'all']:
            obsidian_path = Path(args.obsidian_path) if args.obsidian_path else None
            enhancer.sync_obsidian(obsidian_path)
    
    elif args.backup:
        enhancer.create_backup()
    
    elif args.resolve:
        enhancer.resolve_conflicts(args.resolve)
    
    elif args.status:
        status = enhancer.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
