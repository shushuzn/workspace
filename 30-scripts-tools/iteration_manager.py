#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iteration Workflow Manager - Enforce single-commit workflow

Features:
- Iteration lifecycle management
- Pre-commit workflow checks
- Auto-detect incomplete iterations
- Progress tracking
- Template generation

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


@dataclass
class IterationState:
    """Iteration state tracking"""
    iteration: int
    status: str  # planning/developing/documenting/verifying/ready/completed
    started_at: str
    files_created: List[str]
    reports_created: List[str]
    memory_updated: bool
    tests_passed: bool
    commit_count: int = 0
    completed_at: Optional[str] = None


class WorkflowManager:
    """Manage iteration workflow"""
    
    STATE_FILE = Path('data/iteration_state.json')
    WORKFLOW_FILE = Path('GIT-WORKFLOW-SINGLE-COMMIT.md')
    
    # Workflow phases
    PHASES = {
        'planning': '📋 Planning',
        'developing': '💻 Developing',
        'documenting': '📝 Documenting',
        'verifying': '🔍 Verifying',
        'ready': '✅ Ready to Commit',
        'completed': '🎉 Completed'
    }
    
    def __init__(self):
        self.state: Optional[IterationState] = None
        self.state_file = self.STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_state()
    
    def load_state(self):
        """Load iteration state from disk"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.state = IterationState(**data)
    
    def save_state(self):
        """Save iteration state to disk"""
        if self.state:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.state), f, indent=2, ensure_ascii=False)
    
    def start_iteration(self, iteration: int):
        """Start new iteration"""
        self.state = IterationState(
            iteration=iteration,
            status='planning',
            started_at=datetime.now().isoformat(),
            files_created=[],
            reports_created=[],
            memory_updated=False,
            tests_passed=False,
            commit_count=0
        )
        self.save_state()
        print(f"✅ Iteration {iteration} started")
        print(f"   Status: {self.PHASES['planning']}")
        print(f"   Started: {self.state.started_at}")
    
    def add_file(self, filepath: str):
        """Add file to iteration"""
        if not self.state:
            print("❌ No active iteration. Start one first.")
            return
        
        if filepath not in self.state.files_created:
            self.state.files_created.append(filepath)
            self.save_state()
            print(f"✅ Added: {filepath}")
            print(f"   Total files: {len(self.state.files_created)}")
    
    def add_report(self, filepath: str):
        """Add report to iteration"""
        if not self.state:
            print("❌ No active iteration")
            return
        
        if filepath not in self.state.reports_created:
            self.state.reports_created.append(filepath)
            self.save_state()
            print(f"✅ Added report: {filepath}")
    
    def update_memory(self):
        """Mark MEMORY.md as updated"""
        if not self.state:
            print("❌ No active iteration")
            return
        
        self.state.memory_updated = True
        self.save_state()
        print("✅ MEMORY.md marked as updated")
    
    def pass_tests(self):
        """Mark tests as passed"""
        if not self.state:
            print("❌ No active iteration")
            return
        
        self.state.tests_passed = True
        self.save_state()
        print("✅ Tests marked as passed")
    
    def next_phase(self):
        """Move to next workflow phase"""
        if not self.state:
            print("❌ No active iteration")
            return
        
        phase_order = ['planning', 'developing', 'documenting', 'verifying', 'ready']
        current_idx = phase_order.index(self.state.status) if self.state.status in phase_order else 0
        
        if current_idx < len(phase_order) - 1:
            self.state.status = phase_order[current_idx + 1]
            self.save_state()
            print(f"✅ Moved to: {self.PHASES[self.state.status]}")
        else:
            print("⚠️  Already at final phase")
    
    def check_workflow(self) -> Dict:
        """Check workflow compliance"""
        if not self.state:
            return {'error': 'No active iteration'}
        
        checks = {
            'has_files': len(self.state.files_created) > 0,
            'has_report': len(self.state.reports_created) > 0,
            'memory_updated': self.state.memory_updated,
            'tests_passed': self.state.tests_passed,
            'single_commit': self.state.commit_count <= 1,
            'ready': (
                len(self.state.files_created) > 0 and
                len(self.state.reports_created) > 0 and
                self.state.memory_updated and
                self.state.tests_passed
            )
        }
        
        checks['score'] = sum(checks.values()) / len(checks) * 100
        
        return checks
    
    def show_status(self):
        """Show iteration status"""
        if not self.state:
            print("❌ No active iteration")
            print("\n💡 Start one with: iteration-manager start --iteration 8")
            return
        
        checks = self.check_workflow()
        
        print(f"\n{'='*70}")
        print(f"📊 Iteration {self.state.iteration} Status")
        print(f"{'='*70}\n")
        
        print(f"📍 Phase: {self.PHASES.get(self.state.status, self.state.status)}")
        print(f"⏰ Started: {self.state.started_at}")
        if self.state.completed_at:
            print(f"⏰ Completed: {self.state.completed_at}")
        
        print(f"\n📁 Files ({len(self.state.files_created)}):")
        for f in self.state.files_created:
            print(f"  - {f}")
        
        print(f"\n📄 Reports ({len(self.state.reports_created)}):")
        for r in self.state.reports_created:
            print(f"  - {r}")
        
        print(f"\n✅ Checks:")
        print(f"  Files created: {'✅' if checks['has_files'] else '❌'}")
        print(f"  Report created: {'✅' if checks['has_report'] else '❌'}")
        print(f"  MEMORY.md updated: {'✅' if checks['memory_updated'] else '❌'}")
        print(f"  Tests passed: {'✅' if checks['tests_passed'] else '❌'}")
        print(f"  Single commit: {'✅' if checks['single_commit'] else '❌'}")
        
        print(f"\n🎯 Ready to commit: {'✅ YES' if checks['ready'] else '❌ NO'}")
        print(f"📊 Workflow score: {checks['score']:.0f}/100")
        
        if not checks['ready']:
            print(f"\n⚠️  Missing:")
            if not checks['has_files']:
                print("   - Create tool files")
            if not checks['has_report']:
                print("   - Create iteration report")
            if not checks['memory_updated']:
                print("   - Update MEMORY.md")
            if not checks['tests_passed']:
                print("   - Run and pass tests")
        
        print(f"\n{'='*70}\n")
    
    def complete_iteration(self, commit_hash: str):
        """Mark iteration as completed"""
        if not self.state:
            print("❌ No active iteration")
            return
        
        self.state.status = 'completed'
        self.state.completed_at = datetime.now().isoformat()
        self.state.commit_count += 1
        self.save_state()
        
        print(f"🎉 Iteration {self.state.iteration} completed!")
        print(f"   Commit: {commit_hash}")
        print(f"   Total commits: {self.state.commit_count}")
        
        if self.state.commit_count > 1:
            print(f"⚠️  Warning: {self.state.commit_count} commits (should be 1)")
    
    def get_git_commit_count(self, iteration: int) -> int:
        """Get actual commit count from git log"""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--all', '--grep', f'Iteration {iteration}'],
                capture_output=True, text=True, timeout=10
            )
            commits = [line for line in result.stdout.strip().split('\n') if line]
            return len(commits)
        except Exception:
            return 0
    
    def generate_template(self, iteration: int):
        """Generate iteration template"""
        template = f"""# 📋 Iteration {iteration} Plan

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** Planning  
**Goal:** [Describe iteration goal]

---

## 📝 Checklist

### Phase 1: Development
- [ ] Create tool files
- [ ] Write tests
- [ ] Run tests (all pass)
- [ ] Fix bugs
- [ ] UTF-8 encoding check

### Phase 2: Documentation
- [ ] Create ITERATION-{iteration}-REPORT.md
- [ ] Update MEMORY.md
- [ ] Add lesson numbers

### Phase 3: Verification
- [ ] Run `iteration-manager status`
- [ ] Check workflow score = 100
- [ ] Verify all files ready

### Phase 4: Commit (SINGLE COMMIT!)
- [ ] Run: `iteration-manager commit --iteration {iteration} --title "..."`
- [ ] Verify 1 commit only
- [ ] Push to remote

---

## 🎯 Success Criteria

- [ ] Single commit (1 only!)
- [ ] All files included
- [ ] Report complete
- [ ] MEMORY.md updated
- [ ] Tests passing
- [ ] Workflow score: 100/100

---

## 📊 Files to Include

### Tools
- [ ] tool1.py
- [ ] tool2.py

### Reports
- [ ] ITERATION-{iteration}-REPORT.md
- [ ] MEMORY.md (updated)

---

_Generated by Iteration Workflow Manager_
"""
        
        template_file = Path(f'ITERATION-{iteration}-PLAN.md')
        template_file.write_text(template, encoding='utf-8')
        print(f"✅ Template created: {template_file}")
        
        return template_file
    
    def auto_commit(self, iteration: int, title: str, features: list, lessons: list):
        """Automated single commit with workflow check"""
        
        # Load state
        self.load_state()
        
        # Check workflow
        checks = self.check_workflow()
        
        if not checks.get('ready', False):
            print("❌ Workflow not ready!")
            print(f"   Score: {checks.get('score', 0):.0f}/100")
            print("\nRun: iteration-manager status")
            return 1
        
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, timeout=10)
        changed_files = [line for line in result.stdout.split('\n') if line.strip()]
        
        if not changed_files:
            print("⚠️  No changes to commit")
            return 0
        
        print(f"\n{'='*70}")
        print(f"🎯 Auto Commit - Iteration {iteration}")
        print(f"{'='*70}\n")
        
        print(f"📦 Files to commit: {len(changed_files)}")
        for f in changed_files[:10]:  # Show first 10
            print(f"   {f}")
        if len(changed_files) > 10:
            print(f"   ... and {len(changed_files) - 10} more")
        
        # Add all
        subprocess.run(['git', 'add', '-A'], check=True, timeout=10)
        
        # Create commit message
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

Workflow:
- Files: {len(self.state.files_created) if self.state else 0}
- Reports: {len(self.state.reports_created) if self.state else 0}
- Score: {checks.get('score', 0):.0f}/100
"""
        
        # Commit
        subprocess.run(['git', 'commit', '-m', msg], check=True, timeout=30)
        
        # Get commit hash
        result = subprocess.run(['git', 'log', '-1', '--format=%H'], 
                              capture_output=True, text=True, timeout=10)
        commit_hash = result.stdout.strip()[:7]
        
        # Push
        print("\n🚀 Pushing to remote...")
        subprocess.run(['git', 'push'], check=True, timeout=30)
        
        # Update state
        self.complete_iteration(commit_hash)
        
        print(f"\n{'='*70}")
        print(f"✅ Iteration {iteration} Complete!")
        print(f"📍 Commit: {commit_hash}")
        print(f"📊 Workflow Score: {checks.get('score', 0):.0f}/100")
        print(f"{'='*70}\n")
        
        return 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Iteration Workflow Manager')
    subparsers = parser.add_subparsers(dest='action', help='Action')
    
    # Start
    p_start = subparsers.add_parser('start', help='Start new iteration')
    p_start.add_argument('--iteration', type=int, required=True, help='Iteration number')
    p_start.set_defaults(func=lambda args: manager.start_iteration(args.iteration))
    
    # Add file
    p_add = subparsers.add_parser('add', help='Add file to iteration')
    p_add.add_argument('files', nargs='+', help='Files to add')
    p_add.set_defaults(func=lambda args: [manager.add_file(f) for f in args.files])
    
    # Report
    p_report = subparsers.add_parser('report', help='Add report to iteration')
    p_report.add_argument('files', nargs='+', help='Report files')
    p_report.set_defaults(func=lambda args: [manager.add_report(f) for f in args.files])
    
    # Memory
    p_memory = subparsers.add_parser('memory', help='Mark MEMORY.md updated')
    p_memory.set_defaults(func=lambda args: manager.update_memory())
    
    # Tests
    p_tests = subparsers.add_parser('tests', help='Mark tests passed')
    p_tests.set_defaults(func=lambda args: manager.pass_tests())
    
    # Phase
    p_phase = subparsers.add_parser('phase', help='Move to next phase')
    p_phase.set_defaults(func=lambda args: manager.next_phase())
    
    # Status
    p_status = subparsers.add_parser('status', help='Show iteration status')
    p_status.set_defaults(func=lambda args: manager.show_status())
    
    # Template
    p_template = subparsers.add_parser('template', help='Generate iteration template')
    p_template.add_argument('--iteration', type=int, required=True, help='Iteration number')
    p_template.set_defaults(func=lambda args: manager.generate_template(args.iteration))
    
    # Commit (automated)
    p_commit = subparsers.add_parser('commit', help='Automated single commit')
    p_commit.add_argument('--iteration', type=int, required=True, help='Iteration number')
    p_commit.add_argument('--title', type=str, required=True, help='Iteration title')
    p_commit.add_argument('--feature', type=str, action='append', help='Feature (repeat)')
    p_commit.add_argument('--lesson', type=str, action='append', help='Lesson (repeat)')
    p_commit.set_defaults(func=lambda args: manager.auto_commit(
        args.iteration, args.title, args.feature or [], args.lesson or []
    ))
    
    # Check
    p_check = subparsers.add_parser('check', help='Check workflow compliance')
    p_check.set_defaults(func=lambda args: print(json.dumps(manager.check_workflow(), indent=2)))
    
    args = parser.parse_args()
    
    manager = WorkflowManager()
    
    if args.action:
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
