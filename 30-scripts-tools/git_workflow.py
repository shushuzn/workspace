#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Workflow Automator - Streamlined commit process

Features:
- Single commit for code + memory + report
- Auto-generate commit messages
- Auto-push to remote
- Iteration tracking

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class GitWorkflow:
    """Automate Git workflow for iterations"""
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path)
        self.changes = []
        self.commit_message = []
    
    def run_command(self, command: list, capture: bool = True) -> str:
        """Run shell command"""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=capture,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def get_status(self) -> dict:
        """Get git status"""
        output = self.run_command(['git', 'status', '--short'])
        
        staged = []
        unstaged = []
        untracked = []
        
        for line in output.split('\n'):
            if not line:
                continue
            status = line[:2].strip()
            file = line[3:].strip()
            
            if status in ['A', 'M', 'D', 'R']:
                if status[0] in ['A', 'M', 'D', 'R']:
                    staged.append(file)
            elif status == '??':
                untracked.append(file)
            else:
                unstaged.append(file)
        
        return {
            'staged': staged,
            'unstaged': unstaged,
            'untracked': untracked
        }
    
    def add_files(self, files: list):
        """Add files to staging"""
        for file in files:
            self.run_command(['git', 'add', str(file)])
            self.changes.append(file)
            print(f"✅ Added: {file}")
    
    def add_all(self, pattern: str = '*'):
        """Add all matching files"""
        self.run_command(['git', 'add', '-A'])
        print(f"✅ Added all changes")
    
    def create_commit_message(self, 
                              iteration: int,
                              title: str,
                              features: list,
                              lessons: list) -> str:
        """Generate standardized commit message"""
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        msg = f"""⚡ Obsidian Skills Iteration {iteration}: {title}

New Features ({len(features)}):
{chr(10).join(f'- ✅ {f}' for f in features)}

New Lessons ({len(lessons)}):
{chr(10).join(f'- [{l}]' for l in lessons)}

Performance:
- Git commits: 1 (optimized from 3)
- Process: code + memory + report → single commit

Date: {date}
Iteration: {iteration}
"""
        return msg
    
    def commit(self, message: str, push: bool = True):
        """Create commit and optionally push"""
        
        # Commit
        result = self.run_command(['git', 'commit', '-m', message], capture=True)
        print(f"\n📝 Committed:\n{result}")
        
        # Push
        if push:
            print("\n🚀 Pushing to remote...")
            push_result = self.run_command(['git', 'push', 'origin', 'master'], capture=True)
            print(f"📤 Pushed:\n{push_result}")
        
        return result
    
    def get_last_commit(self) -> str:
        """Get last commit hash"""
        return self.run_command(['git', 'log', '--oneline', '-1'])
    
    def finalize_iteration(self, 
                          iteration: int,
                          title: str,
                          features: list,
                          lessons: list,
                          push: bool = True,
                          complete: bool = False):
        """Complete iteration with single commit
        
        Args:
            complete: If True, auto-detect and include all related files
                     (code + report + MEMORY.md + canvas)
        """
        
        print(f"\n{'='*70}")
        print(f"🎯 Finalizing Iteration {iteration}")
        if complete:
            print(f"🚀 Mode: COMPLETE (auto-detect all files)")
        print(f"{'='*70}\n")
        
        # Check status
        status = self.get_status()
        print(f"📊 Git Status:")
        print(f"  Staged: {len(status['staged'])}")
        print(f"  Unstaged: {len(status['unstaged'])}")
        print(f"  Untracked: {len(status['untracked'])}\n")
        
        # Add all changes
        if status['staged'] or status['unstaged'] or status['untracked']:
            self.add_all()
            print(f"\n📦 Total files to commit: {len(status['staged']) + len(status['unstaged']) + len(status['untracked'])}")
        else:
            print("⚠️  No changes detected!")
            return
        
        # Create commit message
        msg = self.create_commit_message(iteration, title, features, lessons)
        print(f"\n📝 Commit Message:\n{msg}")
        
        # Commit ONCE
        self.commit(msg, push=push)
        
        # Show result
        last_commit = self.get_last_commit()
        print(f"\n{'='*70}")
        print(f"✅ Iteration {iteration} Complete!")
        print(f"📍 Last Commit: {last_commit}")
        print(f"{'='*70}\n")
        
        return {
            'success': True,
            'iteration': iteration,
            'commit': last_commit,
            'changes': len(self.changes)
        }
    
    def show_history(self, count: int = 5):
        """Show recent commit history"""
        print(f"\n📜 Git History (last {count} commits):\n")
        history = self.run_command(['git', 'log', '--oneline', f'-{count}'])
        print(history)
        print()


def main():
    parser = argparse.ArgumentParser(description='Git Workflow Automator')
    parser.add_argument('action', choices=['finalize', 'status', 'history', 'add', 'commit'],
                       help='Action to perform')
    parser.add_argument('--iteration', type=int, help='Iteration number')
    parser.add_argument('--title', type=str, help='Iteration title')
    parser.add_argument('--feature', type=str, action='append', help='Feature (can repeat)')
    parser.add_argument('--lesson', type=str, action='append', help='Lesson code (can repeat)')
    parser.add_argument('--no-push', action='store_true', help='Do not push')
    parser.add_argument('--count', type=int, default=5, help='History count')
    parser.add_argument('--files', type=str, nargs='+', help='Files to add')
    parser.add_argument('--message', type=str, help='Commit message')
    parser.add_argument('--complete', action='store_true', help='Complete mode: auto-detect all files (code+report+memory+canvas)')
    
    args = parser.parse_args()
    workflow = GitWorkflow()
    
    if args.action == 'finalize':
        if not args.iteration or not args.title:
            print("❌ --iteration and --title required for finalize")
            return 1
        
        features = args.feature or []
        lessons = args.lesson or []
        
        workflow.finalize_iteration(
            iteration=args.iteration,
            title=args.title,
            features=features,
            lessons=lessons,
            push=not args.no_push,
            complete=args.complete
        )
        
    elif args.action == 'status':
        status = workflow.get_status()
        print(f"\n📊 Git Status:")
        print(f"  Staged: {len(status['staged'])}")
        for f in status['staged']:
            print(f"    {f}")
        print(f"  Unstaged: {len(status['unstaged'])}")
        for f in status['unstaged']:
            print(f"    {f}")
        print(f"  Untracked: {len(status['untracked'])}")
        for f in status['untracked']:
            print(f"    {f}")
        print()
        
    elif args.action == 'history':
        workflow.show_history(args.count)
        
    elif args.action == 'add':
        if args.files:
            workflow.add_files(args.files)
        else:
            workflow.add_all()
            
    elif args.action == 'commit':
        if not args.message:
            print("❌ --message required for commit")
            return 1
        workflow.commit(args.message, push=not args.no_push)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
