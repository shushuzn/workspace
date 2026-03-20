#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具调用拦截器 - 强制所有 execute_shell_command 通过防护检查
【系统级防护】- 无法绕过

使用方法：
  在工具调用前自动检查：
  1. session 是否存在
  2. 停止标志是否激活
  3. 封锁状态是否激活
  4. 惩罚等级是否超标
  
【关键】此脚本必须被工具执行器调用，而不是直接执行
"""
import json
import sys
from pathlib import Path
from datetime import datetime

class ToolCallInterceptor:
    """工具调用拦截器 - 系统级防护"""
    
    def __init__(self):
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.stop_flag = Path("30-scripts-tools/.STOP_FLAG")
        self.lockdown_file = Path("30-scripts-tools/.lockdown_active")
        self.penalty_file = Path("30-scripts-tools/penalty_state.json")
        self.violation_log = Path("30-scripts-tools/violation_log.jsonl")
        
    def intercept(self, command: str) -> dict:
        """拦截工具调用 - 强制防护检查"""
        
        # 检查 1: session 存在性
        if not self.state_file.exists():
            return self._block("no_session", "execution-state.json 不存在，必须通过 copaw_entry.py 启动")
        
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        if not state.get("session_id"):
            return self._block("no_session_id", "session_id 缺失")
        
        if not state.get("mandatory_execution"):
            return self._block("no_mandatory_execution", "mandatory_execution 未启用")
        
        # 检查 2: 停止标志
        if self.stop_flag.exists():
            with open(self.stop_flag, "r", encoding="utf-8") as f:
                stop_data = json.load(f)
            return self._block("stop_flag", f"系统停止：{stop_data.get('reason', '未知')}")
        
        # 检查 3: 封锁状态
        if self.lockdown_file.exists():
            return self._block("lockdown", "系统封锁中")
        
        # 检查 4: 惩罚等级
        if self.penalty_file.exists():
            with open(self.penalty_file, "r", encoding="utf-8") as f:
                penalty = json.load(f)
            level = penalty.get("current_level", 0)
            if level >= 3:
                return self._block("penalty_level_3", f"惩罚等级 Level {level} - 只读模式")
        
        # 所有检查通过
        return {
            "allowed": True,
            "session_id": state["session_id"],
            "command": command,
            "checked_at": datetime.now().isoformat()
        }
    
    def _block(self, reason: str, message: str) -> dict:
        """阻断调用并记录违规"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "session_id": "unknown",
            "violation_type": "bypass_attempt",
            "reason": reason,
            "message": message,
            "action": "BLOCKED"
        }
        
        # 记录违规日志
        try:
            with open(self.violation_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(violation, ensure_ascii=False) + "\n")
        except:
            pass
        
        return {
            "allowed": False,
            "blocked": True,
            "reason": reason,
            "message": message,
            "action": "BLOCKED"
        }


def create_interceptor():
    """创建拦截器实例"""
    return ToolCallInterceptor()


# 测试模式
if __name__ == "__main__":
    print("=" * 70)
    print("工具调用拦截器 - 测试")
    print("=" * 70)
    
    interceptor = create_interceptor()
    
    # 测试拦截
    result = interceptor.intercept("echo test")
    print(f"\n测试结果：{result}")
    
    if result.get("allowed"):
        print("[OK] 防护检查通过")
    else:
        print(f"[BLOCK] 防护检查失败：{result.get('message')}")
