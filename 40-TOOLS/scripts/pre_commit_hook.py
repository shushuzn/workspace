#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-commit Workflow Hook - Enforce single-commit workflow

Features:
- Check iteration state before commit
- Verify all files ready
- Block commits if workflow not followed
- Provide helpful suggestions

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class PreCommitHook:
    """Pre-commit workflow checker"""
    
    STATE_FILE = Path('data/iteration_state.json')
    WORKFLOW_DOC = Path('GIT-WORKFLOW-SINGLE-COMMIT.md')
    
    def __init__(self):
        self.state = None
        self.errors = []
        self.warnings = []
        self.load_state()
    
    def load_state(self):
        """Load iteration state"""
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
    
    def check_git_status(self) -> dict:
        """Check git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, timeout=10, encoding='utf-8'
            )
            files = [line.split()[1] for line in result.stdout.split('\n') if line.strip()]
            
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%s'],
                capture_output=True, text=True, timeout=10, encoding='utf-8'
            )
            last_commit = result.stdout.strip()
            
            return {
                'changed_files': files,
                'last_commit': last_commit,
                'has_changes': len(files) > 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_iteration_state(self) -> dict:
        """Check iteration state"""
        if not self.state:
            return {
                'has_iteration': False,
                'error': 'No active iteration'
            }
        
        return {
            'has_iteration': True,
            'iteration': self.state.get('iteration'),
            'status': self.state.get('status'),
            'files_count': len(self.state.get('files_created', [])),
            'reports_count': len(self.state.get('reports_created', [])),
            'memory_updated': self.state.get('memory_updated', False),
            'tests_passed': self.state.get('tests_passed', False),
            'commit_count': self.state.get('commit_count', 0)
        }
    
    def check_single_commit(self) -> dict:
        """Check if this would violate single-commit rule"""
        if not self.state:
            return {'violated': False}
        
        commit_count = self.state.get('commit_count', 0)
        
        # Check if already committed
        if commit_count >= 1:
            return {
                'violated': True,
                'reason': f'Already committed {commit_count} time(s)',
                'suggestion': 'Use git commit --amend instead'
            }
        
        return {'violated': False}
    
    def check_workflow_readiness(self) -> dict:
        """Check if workflow is ready for commit"""
        checks = {
            'has_files': self.state and len(self.state.get('files_created', [])) > 0,
            'has_report': self.state and len(self.state.get('reports_created', [])) > 0,
            'memory_updated': self.state and self.state.get('memory_updated', False),
            'tests_passed': self.state and self.state.get('tests_passed', False),
        }
        
        checks['ready'] = all(checks.values())
        checks['score'] = sum(checks.values()) / len(checks) * 100
        
        return checks
    
    def run_checks(self) -> bool:
        """Run all pre-commit checks"""
        print(f"\n{'='*70}")
        print(f"🔍 Pre-commit Workflow Check")
        print(f"{'='*70}\n")
        
        # Git status
        git_status = self.check_git_status()
        print(f"📊 Git Status:")
        if 'error' in git_status:
            print(f"   ❌ Error: {git_status['error']}")
            return False
        
        print(f"   Changed files: {len(git_status['changed_files'])}")
        if not git_status['has_changes']:
            print(f"   ⚠️  No changes to commit")
            return False
        
        # Iteration state
        iter_state = self.check_iteration_state()
        print(f"\n📋 Iteration State:")
        if not iter_state['has_iteration']:
            print(f"   ⚠️  {iter_state.get('error', 'Unknown')}")
            print(f"   💡 Start iteration: iteration-manager start --iteration N")
            self.warnings.append("No active iteration")
        else:
            print(f"   Iteration: {iter_state['iteration']}")
            print(f"   Status: {iter_state['status']}")
            print(f"   Files: {iter_state['files_count']}")
            print(f"   Reports: {iter_state['reports_count']}")
            print(f"   MEMORY.md: {'✅' if iter_state['memory_updated'] else '❌'}")
            print(f"   Tests: {'✅' if iter_state['tests_passed'] else '❌'}")
            print(f"   Commits: {iter_state['commit_count']}")
        
        # Single commit check
        single_commit = self.check_single_commit()
        print(f"\n🎯 Single Commit Rule:")
        if single_commit['violated']:
            print(f"   ❌ VIOLATED: {single_commit['reason']}")
            print(f"   💡 {single_commit['suggestion']}")
            self.errors.append(single_commit['reason'])
            return False
        else:
            print(f"   ✅ Compliant")
        
        # Workflow readiness
        readiness = self.check_workflow_readiness()
        print(f"\n✅ Workflow Readiness:")
        print(f"   Files created: {'✅' if readiness.get('has_files') else '❌'}")
        print(f"   Report created: {'✅' if readiness.get('has_report') else '❌'}")
        print(f"   MEMORY.md updated: {'✅' if readiness.get('memory_updated') else '❌'}")
        print(f"   Tests passed: {'✅' if readiness.get('tests_passed') else '❌'}")
        print(f"\n   📊 Score: {readiness['score']:.0f}/100")
        
        if not readiness['ready']:
            print(f"\n⚠️  NOT READY for commit!")
            print(f"\n   Missing:")
            if not readiness.get('has_files'):
                print(f"   - Create tool files (iteration-manager add file.py)")
            if not readiness.get('has_report'):
                print(f"   - Create report (iteration-manager report report.md)")
            if not readiness.get('memory_updated'):
                print(f"   - Update MEMORY.md (iteration-manager memory)")
            if not readiness.get('tests_passed'):
                print(f"   - Pass tests (iteration-manager tests)")
            
            print(f"\n   💡 Run: iteration-manager status")
            self.errors.append("Workflow not ready")
            return False
        
        print(f"\n{'='*70}")
        print(f"✅ Pre-commit checks PASSED")
        print(f"{'='*70}\n")
        
        return True
    
    def show_tips(self):
        """Show workflow tips"""
        print(f"\n💡 Workflow Tips:")
        print(f"   1. Complete ALL work before committing")
        print(f"   2. Use iteration-manager to track progress")
        print(f"   3. Run 'iteration-manager commit' for automated commit")
        print(f"   4. Never commit mid-iteration")
        print(f"   5. Single commit = 1 iteration\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-commit Workflow Hook')
    parser.add_argument('--enforce', action='store_true', 
                       help='Enforce checks (exit code 1 on failure)')
    parser.add_argument('--warn', action='store_true',
                       help='Warn only (always exit 0)')
    args = parser.parse_args()
    
    hook = PreCommitHook()
    
    success = hook.run_checks()
    
    if not success:
        hook.show_tips()
        
        if args.enforce:
            print(f"\n❌ Commit BLOCKED. Fix issues first.\n")
            return 1
        elif args.warn:
            print(f"\n⚠️  Proceeding despite warnings...\n")
            return 0
    
    hook.show_tips()
    return 0


if __name__ == "__main__":
    sys.exit(main())
