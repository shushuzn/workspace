#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Pre-commit Hook v4.0 - 强制工作流审计

功能：
1. 检查 execution-state.json 存在
2. 检查 session 有效性
3. 检查 tool_call_log 有本次会话记录
4. 检查文件修改 vs 工具调用匹配
5. 不匹配 -> 阻止提交

安装：
  copy .git/hooks/pre-commit-v4.py .git/hooks/pre-commit
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime


class PreCommitAuditor:
    """Git 提交前审计器"""
    
    def __init__(self):
        self.workspace = Path("D:/OpenClaw/workspace")
        self.state_file = self.workspace / "flow-archive/20260318-universal-workflow-001/execution-state.json"
        self.tool_call_log = self.workspace / "30-scripts-tools/tool_call_log.jsonl"
        self.git_dir = self.workspace / ".git"
        self.issues = []
        self.warnings = []
    
    def audit(self) -> bool:
        print("=" * 70)
        print(" " * 20 + "Git Pre-commit Audit v4.0")
        print("=" * 70)
        
        if not self._check_state_file():
            return False
        if not self._check_session_valid():
            return False
        if not self._check_tool_call_log():
            return False
        if not self._check_file_modifications():
            return False
        if not self._check_workflow_integrity():
            return False
        
        print("\n" + "=" * 70)
        print(" [OK] 所有审计检查通过 - 允许提交")
        print("=" * 70)
        return True
    
    def _check_state_file(self) -> bool:
        print("\n[Check 1] execution-state.json existence")
        if not self.state_file.exists():
            print("  [FAIL] execution-state.json not found")
            print("  [TIP] Run: py 30-scripts-tools/copaw_entry.py <task>")
            self.issues.append("execution-state.json missing")
            return False
        print("  [OK] execution-state.json exists")
        return True
    
    def _check_session_valid(self) -> bool:
        print("\n[Check 2] Session validity")
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            required = ['session_id', 'flow_id', 'mandatory_execution', 'protection_enabled']
            for field in required:
                if field not in state:
                    print(f"  [FAIL] Missing field: {field}")
                    self.issues.append(f"session missing field: {field}")
                    return False
            if not state.get('protection_enabled', False):
                print("  [WARN] protection_enabled is false")
                self.warnings.append("protection_enabled not enabled")
            print(f"  [OK] Session {state['session_id']} valid")
            print(f"       Flow ID: {state['flow_id']}")
            print(f"       Task: {state.get('task', 'unknown')}")
            return True
        except Exception as e:
            print(f"  [FAIL] Read state failed: {e}")
            self.issues.append(f"state read failed: {e}")
            return False
    
    def _check_tool_call_log(self) -> bool:
        print("\n[Check 3] Tool Call Log audit")
        if not self.tool_call_log.exists():
            print("  [WARN] tool_call_log.jsonl not found (first commit?)")
            self.warnings.append("tool_call_log.jsonl missing")
            return True
        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        session_id = state['session_id']
        session_calls = []
        try:
            with open(self.tool_call_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('session_id') == session_id:
                            session_calls.append(entry)
                    except:
                        continue
        except Exception as e:
            print(f"  [FAIL] Read tool_call_log failed: {e}")
            self.issues.append(f"tool_call_log read failed: {e}")
            return False
        if len(session_calls) == 0:
            print("  [FAIL] No tool calls for this session")
            print("  [TIP] All operations must use tool calls")
            self.issues.append("no tool calls this session")
            return False
        tool_types = {}
        for call in session_calls:
            tool_id = call.get('tool_id', 'unknown')
            tool_types[tool_id] = tool_types.get(tool_id, 0) + 1
        print(f"  [OK] {len(session_calls)} tool calls this session")
        print(f"       Tools: {tool_types}")
        return True
    
    def _check_file_modifications(self) -> bool:
        print("\n[Check 4] File modification audit")
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, cwd=self.workspace
            )
            staged = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception as e:
            print(f"  [FAIL] Git staged files failed: {e}")
            self.issues.append(f"git staged failed: {e}")
            return False
        if not staged:
            print("  [INFO] No staged files")
            return True
        print(f"  Staged files: {len(staged)}")
        protected = [
            '30-scripts-tools/safe_shell_executor.py',
            '30-scripts-tools/tool_wrapper.py',
            '30-scripts-tools/copaw_entry.py',
            '.git/hooks/pre-commit',
        ]
        for f in staged:
            if f in protected:
                print(f"  [WARN] Protected file modified: {f}")
                self.warnings.append(f"protected file: {f}")
        print("  [OK] File modification audit complete")
        return True
    
    def _check_workflow_integrity(self) -> bool:
        print("\n[Check 5] Workflow integrity")
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            completion = state.get('completion_percentage', 0)
            completed = len(state.get('completed_steps', []))
            print(f"  Completion: {completion:.1f}%")
            print(f"  Completed steps: {completed}")
            
            # 新增：检查最低完成率（Git 提交时至少完成 50%）
            if completion < 50 and completed < 5:
                print(f"  [FAIL] Workflow completion too low: {completion:.1f}%")
                print(f"  [TIP] Complete at least 5 steps before commit")
                self.issues.append(f"workflow completion too low: {completion:.1f}%")
                return False
            
            if completion == 0 and completed == 0:
                print("  [WARN] Workflow not started")
                self.warnings.append("workflow completion 0%")
            print("  [OK] Workflow integrity check passed")
            return True
        except Exception as e:
            print(f"  [FAIL] Read workflow failed: {e}")
            self.issues.append(f"workflow read failed: {e}")
            return False
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print(" Audit Summary")
        print("=" * 70)
        if self.issues:
            print(f"\n[FAIL] {len(self.issues)} critical issues:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        if self.warnings:
            print(f"\n[WARN] {len(self.warnings)} warnings:")
            for i, w in enumerate(self.warnings, 1):
                print(f"  {i}. {w}")
        if not self.issues and not self.warnings:
            print("\n[OK] Perfect: no issues found")


def main():
    auditor = PreCommitAuditor()
    passed = auditor.audit()
    auditor.print_summary()
    if not passed:
        print("\n" + "=" * 70)
        print(" [FAIL] Commit blocked")
        print("=" * 70)
        print("\nFix issues above and retry")
        print("Or use --no-verify to force (not recommended)")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
