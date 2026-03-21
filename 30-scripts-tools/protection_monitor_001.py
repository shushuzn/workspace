import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时防护监控 - 监控所有操作并实时阻断违规
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import time

MONITOR_LOG = Path("30-scripts-tools/monitor_log.jsonl")
PROTECTION_STATE = Path("30-scripts-tools/protection_state.json")

class ProtectionMonitor:
    def __init__(self):
        self.session_id = None
        self.current_step = None
        self.last_tool_call = None
        self.violations = []
    
    def start_session(self, session_id: str):
        """开始监控会话"""
        self.session_id = session_id
        start_time = datetime.now().isoformat()
        
        # 检查是否有活跃封锁
        lockdown_file = Path("30-scripts-tools/.lockdown_active")
        if lockdown_file.exists():
            return {
                "status": "blocked",
                "reason": "系统处于封锁状态",
                "session_id": session_id
            }
        
        # 检查惩罚状态
        penalty_state = Path("30-scripts-tools/penalty_state.json")
        if penalty_state.exists():
            with open(penalty_state, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            if state.get("current_level", 0) >= 3:
                return {
                    "status": "restricted",
                    "level": state["current_level"],
                    "restrictions": state.get("restrictions", []),
                    "session_id": session_id
                }
        
        # 记录会话开始
        self._log_event("session_start", {"session_id": session_id})
        
        return {
            "status": "allowed",
            "session_id": session_id,
            "started_at": start_time
        }
    
    def check_tool_call(self, tool_id: str, command: str = None) -> dict:
        """检查工具调用"""
        
        # 检查封锁
        if self._is_lockdown():
            return self._block_action("系统封锁中，禁止所有操作")
        
        # 检查惩罚等级
        restrictions = self._get_restrictions()
        if restrictions:
            # Level 3: 只读模式
            if "只读模式" in restrictions:
                read_only_tools = ["risk-assessor", "penalty-system", "context-verify"]
                if tool_id not in read_only_tools:
                    return self._block_action(f"只读模式，禁止调用 {tool_id}")
            
            # Level 2: 禁止高风险操作
            if "禁止高风险操作" in restrictions:
                high_risk_tools = ["sync-registry", "cleanup-tools", "delete-tool"]
                if tool_id in high_risk_tools:
                    return self._block_action(f"限制模式，禁止高风险工具 {tool_id}")
        
        # 记录工具调用
        self.last_tool_call = {
            "tool_id": tool_id,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        self._log_event("tool_call", self.last_tool_call)
        
        return {
            "status": "allowed",
            "tool_id": tool_id
        }
    
    def check_workflow_step(self, step_id: int, step_name: str) -> dict:
        """检查工作流步骤"""
        
        if self._is_lockdown():
            return self._block_action("系统封锁中，禁止执行工作流")
        
        # 检查是否按顺序执行
        if self.current_step is not None:
            if step_id != self.current_step + 1:
                violation = {
                    "type": "skip_workflow_step",
                    "expected": self.current_step + 1,
                    "actual": step_id,
                    "timestamp": datetime.now().isoformat()
                }
                self._record_violation(violation)
                return self._block_action(f"步骤跳跃：期望 Step {self.current_step + 1}, 实际 Step {step_id}")
        
        self.current_step = step_id
        self._log_event("workflow_step", {
            "step_id": step_id,
            "step_name": step_name
        })
        
        return {
            "status": "allowed",
            "step_id": step_id
        }
    
    def check_file_modification(self, file_path: str, operation: str) -> dict:
        """检查文件修改"""
        
        if self._is_lockdown():
            return self._block_action("系统封锁中，禁止修改文件")
        
        restrictions = self._get_restrictions()
        
        # 只读模式禁止所有修改
        if restrictions and "只读模式" in restrictions:
            return self._block_action(f"只读模式，禁止修改 {file_path}")
        
        # 检查是否需要备份
        critical_files = [
            "tools_registry.json",
            "execution-state.json",
            "workflow.json",
            ".py"
        ]
        
        needs_backup = any(cf in file_path for cf in critical_files)
        
        if needs_backup and operation in ["write", "modify", "delete"]:
            # 检查是否有备份
            backup_dir = Path("99-backups/auto")
            if backup_dir.exists():
                backups = list(backup_dir.glob(f"*{Path(file_path).name}"))
                if not backups:
                    return self._warn_action(f"关键文件 {file_path} 修改前未备份")
        
        self._log_event("file_modification", {
            "file_path": file_path,
            "operation": operation
        })
        
        return {
            "status": "allowed",
            "file_path": file_path,
            "needs_backup": needs_backup
        }
    
    def _is_lockdown(self) -> bool:
        """检查是否处于封锁状态"""
        lockdown_file = Path("30-scripts-tools/.lockdown_active")
        return lockdown_file.exists()
    
    def _get_restrictions(self) -> list:
        """获取当前限制措施"""
        penalty_state = Path("30-scripts-tools/penalty_state.json")
        if penalty_state.exists():
            with open(penalty_state, "r", encoding="utf-8") as f:
                state = json.load(f)
            return state.get("restrictions", [])
        return []
    
    def _block_action(self, reason: str) -> dict:
        """阻断操作"""
        self._log_event("blocked", {"reason": reason})
        return {
            "status": "blocked",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def _warn_action(self, warning: str) -> dict:
        """警告"""
        self._log_event("warning", {"warning": warning})
        return {
            "status": "allowed_with_warning",
            "warning": warning
        }
    
    def _record_violation(self, violation: dict):
        """记录违规"""
        violation["session_id"] = self.session_id
        self.violations.append(violation)
        self._log_event("violation", violation)
    
    def _log_event(self, event_type: str, data: dict):
        """记录事件"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "session_id": self.session_id,
            "data": data
        }
        
        with open(MONITOR_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def get_session_report(self) -> dict:
        """生成会话报告"""
        return {
            "session_id": self.session_id,
            "current_step": self.current_step,
            "last_tool_call": self.last_tool_call,
            "violations_count": len(self.violations),
            "violations": self.violations
        }

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        # 测试模式
        print("=" * 70)
        print("实时防护监控测试")
        print("=" * 70)
        
        monitor = ProtectionMonitor()
        
        # 测试会话开始
        print("\n[测试 1] 开始会话")
        result = monitor.start_session("session-test-001")
        print(f"状态：{result['status']}")
        
        # 测试工具调用
        print("\n[测试 2] 工具调用")
        result = monitor.check_tool_call("context-verify")
        print(f"工具：context-verify → {result['status']}")
        
        result = monitor.check_tool_call("sync-registry")
        print(f"工具：sync-registry → {result['status']}")
        
        # 测试工作流步骤
        print("\n[测试 3] 工作流步骤")
        result = monitor.check_workflow_step(1, "上下文加载")
        print(f"Step 1 → {result['status']}")
        
        result = monitor.check_workflow_step(3, "任务分析")  # 跳过 Step 2
        print(f"Step 3 (跳过 2) → {result['status']}")
        
        # 生成报告
        print("\n[测试 4] 会话报告")
        report = monitor.get_session_report()
        print(f"违规次数：{report['violations_count']}")
        
        return 0
    
    command = sys.argv[1]
    
    if command == "start" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        monitor = ProtectionMonitor()
        result = monitor.start_session(session_id)
    elif command == "check_tool" and len(sys.argv) >= 3:
        tool_id = sys.argv[2]
        monitor = ProtectionMonitor()
        result = monitor.check_tool_call(tool_id)
    elif command == "check_step" and len(sys.argv) >= 4:
        step_id = int(sys.argv[2])
        step_name = sys.argv[3]
        monitor = ProtectionMonitor()
        result = monitor.check_workflow_step(step_id, step_name)
    elif command == "report":
        monitor = ProtectionMonitor()
        result = monitor.get_session_report()
    else:
        print("用法:")
        print("  py protection_monitor.py start <session_id>")
        print("  py protection_monitor.py check_tool <tool_id>")
        print("  py protection_monitor.py check_step <step_id> <step_name>")
        print("  py protection_monitor.py report")
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ["allowed", "success"] else 1

if __name__ == "__main__":
    sys.exit(main())
