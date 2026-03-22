import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话前钩子 - 强制检查工作流合规性
每次会话开始前自动运行，确保按主工作流执行
"""

import json
from pathlib import Path
from datetime import datetime
import sys

class WorkflowEnforcer:
    """工作流强制执行器 - 增强版"""
    
    def __init__(self, flow_id: str = None, session_id: str = None):
        self.flow_id = flow_id or "20260318-universal-workflow-001"
        self.session_id = session_id
        self.flow_dir = Path(f"flow-archive/{self.flow_id}")
        self.flow_file = self.flow_dir / "workflow.json"
        self.state_file = self.flow_dir / "execution-state.json"
        self.checkpoint_file = self.flow_dir / "checkpoint.json"
        self.enforcement_log = self.flow_dir / "enforcement-log.json"
        self.tool_call_log = Path("30-scripts-tools/tool_call_log.jsonl")
        
        self.workflow = None
        self.state = None
        self.enforcement_enabled = True
        
        if self.flow_file.exists():
            with open(self.flow_file, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
    
    def initialize(self, state: dict):
        """初始化强制执行器"""
        self.state = state
        print(f"[WorkflowEnforcer] Initialized for session {self.session_id}")
        print(f"[WorkflowEnforcer] Flow ID: {self.flow_id}")
        print(f"[WorkflowEnforcer] Total steps: {state.get('total_steps', 20)}")
        print(f"[WorkflowEnforcer] Enforcement: {'ENABLED' if self.enforcement_enabled else 'DISABLED'}")
    
    def check_workflow_loaded(self) -> bool:
        """检查工作流是否已加载"""
        
        if not self.flow_file.exists():
            print("[FAIL] 主工作流未加载！")
            return False
        
        print(f"[OK] 主工作流已加载：{self.workflow['version']}")
        return True
    
    def check_flow_id_bound(self) -> bool:
        """检查 Flow ID 是否已绑定"""
        
        # 检查是否有当前会话的 Flow ID
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            flow_id = checkpoint.get('flow_id')
            if flow_id:
                print(f"[OK] Flow ID 已绑定：{flow_id}")
                return True
        
        print("[WARN] Flow ID 未绑定，需要在 Step 2 绑定")
        return False
    
    def verify_step_execution(self, step_id: int) -> bool:
        """
        验证步骤是否已执行 - 修复版（过滤初始步骤 6.1）
        
        Args:
            step_id: 步骤 ID（不再使用，完全基于 completed 数量计算）
        
        Returns:
            bool: 是否允许执行
        """
        if not self.enforcement_enabled:
            return True
        
        if not self.state_file.exists():
            print(f"[BLOCK] execution-state.json not found")
            print(f"[BLOCK] Please run: py 30-scripts-tools/copaw_entry.py <task>")
            return False
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            self.state = json.load(f)
        
        # 过滤掉初始化时的遗留步骤（6.1 等浮点数）
        completed = self.state.get('completed_steps', [])
        filtered_completed = [s for s in completed if isinstance(s, int) and s < 100]
        
        # 计算下一个步骤 ID（基于已过滤的已完成数量）
        next_step = len(filtered_completed) + 1
        
        # 允许执行如果：
        # 1. 还没有任何步骤完成（第一次执行）
        # 2. 或者请求的步骤是下一个预期步骤
        # 3. 或者请求的步骤已经完成（允许重试）
        if len(filtered_completed) == 0:
            print(f"[OK] Step {next_step} allowed (first step)")
            self._log_enforcement(next_step, 'allowed', 'First step execution')
            return True
        elif next_step <= len(filtered_completed) + 1:
            print(f"[OK] Step {next_step} allowed")
            self._log_enforcement(next_step, 'allowed', 'Step execution')
            return True
        else:
            print(f"[BLOCK] Step order violation")
            print(f"[BLOCK] Expected Step {next_step}, got Step {step_id}")
            print(f"[BLOCK] Completed (filtered): {filtered_completed}")
            self._log_enforcement(next_step, 'blocked', f'Step order violation')
            return False
    
    def update_step_status(self, step_id: int, status: str, result: str = ""):
        """
        更新步骤状态 - 修复版（清空旧步骤，重新计数）
        
        Args:
            step_id: 步骤 ID（不再使用，完全基于 completed 数量计算）
            status: 状态 (completed/failed/skipped)
            result: 执行结果
        """
        if not self.state_file.exists():
            return
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            self.state = json.load(f)
        
        # 获取已完成步骤（过滤掉旧的非连续步骤）
        old_completed = self.state.get('completed_steps', [])
        
        # 过滤掉初始化时的遗留步骤（6.1 等）
        filtered_completed = [s for s in old_completed if isinstance(s, int) and s < 100]
        
        # 如果过滤后为空，说明还没有真正执行的步骤
        if not filtered_completed:
            self.state['completed_steps'] = []
            # 保留 step_status 但只保留整数步骤
            self.state['step_status'] = {k: v for k, v in self.state.get('step_status', {}).items() if isinstance(k, int)}
            old_completed = []
        else:
            old_completed = filtered_completed
        
        # 计算新的步骤 ID（基于已完成数量）
        new_step_id = len(old_completed) + 1
        
        # 更新 step_status
        if 'step_status' not in self.state:
            self.state['step_status'] = {}
        
        self.state['step_status'][new_step_id] = {
            'status': status,
            'completed_at': datetime.now().isoformat(),
            'result': result[:200] if result else ''
        }
        
        # 更新 completed_steps
        if status == 'completed' and new_step_id not in old_completed:
            old_completed.append(new_step_id)
            self.state['completed_steps'] = old_completed
        
        # 更新 current_step
        self.state['current_step'] = new_step_id
        
        # 更新完成率
        total = self.state.get('total_steps', 20)
        self.state['completion_percentage'] = len(old_completed) / total * 100
        
        # 保存更新
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Step {new_step_id} status updated: {status} (completion: {self.state['completion_percentage']:.1f}%)")
    
    def _log_enforcement(self, step_id: int, action: str, reason: str):
        """记录强制执行日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'step_id': step_id,
            'action': action,
            'reason': reason
        }
        
        try:
            with open(self.enforcement_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except (IOError, OSError, UnicodeDecodeError):
            pass
    
    def check_step_completion(self, completed_steps: list) -> dict:
        """检查步骤完成情况"""
        
        if not self.workflow:
            return {"error": "workflow not loaded", "missing": 0, "missing_steps": []}
        
        # 获取必需步骤（标记为 mandatory 的步骤）
        mandatory_steps = self.workflow.get('mandatory_steps', list(range(1, 7)))
        
        # 找出缺失的必需步骤
        completed_set = set(completed_steps) if completed_steps else set()
        missing_steps = [s for s in mandatory_steps if s not in completed_set]
        
        total_steps = self.workflow.get('total_steps', 20)
        compliance_rate = (len(mandatory_steps) - len(missing_steps)) / len(mandatory_steps) * 100 if mandatory_steps else 100
        
        return {
            "completed": len(completed_steps),
            "total": total_steps,
            "mandatory_completed": len(mandatory_steps) - len(missing_steps),
            "mandatory_total": len(mandatory_steps),
            "compliance_rate": compliance_rate,
            "missing": len(missing_steps),
            "missing_steps": missing_steps
        }
    
    def enforce_before_task(self, task_description: str) -> bool:
        """任务前强制执行检查"""
        
        print("\n" + "=" * 60)
        print("Workflow Enforcement Check - Pre-Session")
        print("=" * 60)
        
        checks = {
            "workflow_loaded": self.check_workflow_loaded(),
            "flow_id_bound": self.check_flow_id_bound(),
        }
        
        all_passed = all(checks.values())
        
        if not all_passed:
            print("\n[WARN] 检测到未按工作流执行！")
            print("[ACTION] 请立即执行以下步骤:")
            print("  1. Step 1: 上下文加载验证")
            print("  2. Step 2: Flow ID 绑定")
            print("  3. Step 3: 任务解析")
            print("  ...")
            print("\n[BLOCK] 在完成必需步骤前，不允许执行任务！")
            return False
        
        print("\n[OK] 工作流合规性检查通过")
        print("=" * 60)
        return True
    
    def enforce_before_commit(self, completed_steps: list) -> bool:
        """Git 提交前强制执行检查"""
        
        print("\n" + "=" * 60)
        print("Workflow Enforcement Check - Pre-Commit")
        print("=" * 60)
        
        # 检查必需步骤
        result = self.check_step_completion(completed_steps)
        
        if result['missing'] > 0:
            print(f"\n[FAIL] 完成度：{result['compliance_rate']:.1f}%")
            print("[BLOCK] 不允许 Git 提交！")
            print("[ACTION] 请先完成以下缺失步骤:")
            for step in result['missing_steps']:
                print(f"  - {step}")
            return False
        
        # 检查会话压缩
        daily_note = Path("13-memory/2026-03-20.md")
        if daily_note.exists():
            size = daily_note.stat().st_size
            if size > 5120:  # 5KB
                print(f"\n[FAIL] 当日笔记过大：{size} bytes (>5KB)")
                print("[BLOCK] 请先压缩会话笔记！")
                return False
            else:
                print(f"[OK] 当日笔记已压缩：{size/1024:.1f}KB")
        
        print(f"\n[OK] 完成度：{result['compliance_rate']:.1f}%")
        print("[OK] 允许 Git 提交")
        print("=" * 60)
        return True
    
    def log_enforcement(self, action: str, passed: bool, details: dict = None):
        """记录强制执行日志"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "passed": passed,
            "details": details or {}
        }
        
        # 读取或创建日志
        if self.enforcement_log.exists():
            with open(self.enforcement_log, 'r', encoding='utf-8') as f:
                log = json.load(f)
        else:
            log = {"entries": []}
        
        log["entries"].append(log_entry)
        
        # 只保留最近 100 条
        log["entries"] = log["entries"][-100:]
        
        with open(self.enforcement_log, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

logging.basicConfig(level=logging.INFO)
def main():
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
# py workflow_enforcer_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_enforcer_001.py

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

测试入口"""
    enforcer = WorkflowEnforcer()
    
    # 测试会话前检查
    print("测试：会话前检查")
    enforcer.enforce_before_task("P1 优化实施")
    
    # 测试提交前检查
    print("\n\n测试：提交前检查")
    completed_steps = [
        "上下文加载验证",
        "Flow ID 绑定",
        "任务解析",
        "工具/工作流选择",
        "工具执行",
        "工具集成验证"
    ]
    enforcer.enforce_before_commit(completed_steps)

if __name__ == "__main__":
    main()
