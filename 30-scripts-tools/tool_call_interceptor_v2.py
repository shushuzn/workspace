#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具调用拦截器 - 拦截所有工具调用并验证合规性
【防护 v10 核心】- 调用拦截 + 合规验证 + 自动阻止

功能:
  1. 拦截所有工具调用请求
  2. 验证调用者身份
  3. 验证会话有效性
  4. 记录调用日志
  5. 阻止未授权调用
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
TOOL_REGISTRY = Path("30-scripts-tools/tools_registry.json")
INTERCEPTOR_LOG = Path("30-scripts-tools/interceptor_log.jsonl")
VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")

class ToolCallInterceptor:
    """工具调用拦截器 - 防护 v10"""
    
    def __init__(self):
        self.session_id = self._get_session_id()
        self.registry = self._load_registry()
    
    def _get_session_id(self):
        if not STATE_FILE.exists():
            return None
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("session_id")
    
    def _load_registry(self):
        if not TOOL_REGISTRY.exists():
            return None
        with open(TOOL_REGISTRY, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def intercept(self, tool_id: str, caller: str = "unknown") -> dict:
        """拦截工具调用"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "tool_id": tool_id,
            "caller": caller,
            "allowed": False,
            "reason": ""
        }
        
        # 检查 1: 会话有效性
        if not self.session_id:
            result["reason"] = "No valid session (must use copaw_entry.py)"
            self._log_and_violate(result)
            return result
        
        # 检查 2: 工具注册
        if self.registry and tool_id not in self.registry.get("tools", {}):
            result["reason"] = f"Unregistered tool: {tool_id}"
            self._log_and_violate(result)
            return result
        
        # 检查 3: 调用者权限
        if not self._check_caller_permission(caller, tool_id):
            result["reason"] = f"Caller {caller} not authorized for {tool_id}"
            self._log_and_violate(result)
            return result
        
        # 检查 4: 防护层完整性
        if not self._check_protection_integrity():
            result["reason"] = "Protection layer integrity check failed"
            self._log_and_violate(result)
            return result
        
        # 所有检查通过
        result["allowed"] = True
        result["reason"] = "Authorized"
        self._log_call(result)
        
        return result
    
    def _check_caller_permission(self, caller: str, tool_id: str) -> bool:
        """检查调用者权限"""
        # 白名单：允许所有已注册工具通过 tool_executor.py 调用
        if caller in ["tool_executor.py", "workflow_helper.py", "copaw_entry.py"]:
            return True
        
        # 黑名单：禁止直接调用
        if caller in ["unknown", "direct_call", "manual"]:
            return False
        
        # 默认：允许（可配置）
        return True
    
    def _check_protection_integrity(self) -> bool:
        """检查防护层完整性"""
        critical_files = [
            Path("30-scripts-tools/copaw_entry.py"),
            Path("30-scripts-tools/tool_executor.py"),
            Path("30-scripts-tools/safe_shell_executor.py"),
            Path(".git/hooks/pre-commit"),
        ]
        
        for file_path in critical_files:
            if not file_path.exists():
                return False
        
        return True
    
    def _log_call(self, result: dict):
        """记录调用日志"""
        with open(INTERCEPTOR_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    def _log_and_violate(self, result: dict):
        """记录违规"""
        # 记录调用
        self._log_call(result)
        
        # 记录违规
        violation = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "violation_type": "unauthorized_tool_call",
            "details": result,
            "action": "BLOCKED",
            "penalty_points": 20
        }
        
        with open(VIOLATION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(violation, ensure_ascii=False) + "\n")
    
    def display_stats(self):
        """显示统计"""
        if not INTERCEPTOR_LOG.exists():
            print("No interceptor logs found")
            return
        
        with open(INTERCEPTOR_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        total = len(lines)
        allowed = sum(1 for line in lines if json.loads(line).get("allowed"))
        blocked = total - allowed
        
        print("=" * 70)
        print("工具调用拦截器 v10.0 - 统计")
        print("=" * 70)
        print(f"会话：{self.session_id}")
        print()
        print(f"总调用：{total} 次")
        print(f"  允许：{allowed} 次 ({allowed/total*100:.1f}%)")
        print(f"  阻止：{blocked} 次 ({blocked/total*100:.1f}%)")
        print("=" * 70)


def main():
    import sys
    
    interceptor = ToolCallInterceptor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            interceptor.display_stats()
            return 0
        elif sys.argv[1] == "--test":
            # 测试拦截
            result = interceptor.intercept("safe-shell-executor", "tool_executor.py")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
    
    # 默认：显示统计
    interceptor.display_stats()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
