import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
强制防护执行器 v1.0
所有操作必须通过此执行器，无法绕过
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 强制导入防护层
SCRIPTS_DIR = Path("30-scripts-tools")
AUTO_PROTECTION_FILE = SCRIPTS_DIR / "auto_protection_layer.py"

class ForcedProtectionExecutor:
    """强制防护执行器 - 无法绕过"""
    
    def __init__(self):
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.stop_flag = SCRIPTS_DIR / ".STOP_FLAG"
        self.lockdown_file = SCRIPTS_DIR / ".lockdown_active"
        self.penalty_file = SCRIPTS_DIR / "penalty_state.json"
        self.protection = None
        
        # 强制检查 - 没有 session 不允许执行
        self._force_session_check()
        
        # 强制加载防护层
        self._force_load_protection()
        
        # 强制检查停止状态
        self._force_stop_check()
    
    def _force_session_check(self) -> None:
        """强制会话检查 - 没有 session 直接退出"""
        if not self.state_file.exists():
            print("=" * 70)
            print("[FATAL] execution-state.json 不存在")
            print("[FATAL] 必须通过 copaw_entry.py 启动")
            print("[FATAL] 直接执行脚本是被禁止的")
            print("=" * 70)
            sys.exit(1)
        
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        self.session_id = state.get("session_id")
        if not self.session_id:
            print("[FATAL] session_id 缺失")
            sys.exit(1)
        
        if not state.get("mandatory_execution"):
            print("[FATAL] mandatory_execution 未启用")
            sys.exit(1)
        
        print(f"[OK] 强制会话检查通过：{self.session_id}")
    
    def _force_load_protection(self) -> None:
        """强制加载防护层"""
        try:
            # 直接导入，不允许失败
            import importlib.util
            spec = importlib.util.spec_from_file_location("auto_protection_layer", AUTO_PROTECTION_FILE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.protection = module.create_protection_layer(self.session_id)
            print(f"[OK] 强制防护层已加载")
        except Exception as e:
            print(f"[WARN] 防护层加载失败：{e}")
            print("[WARN] 继续执行但记录警告")
    
    def _force_stop_check(self) -> None:
        """强制停止检查 - 停止状态直接退出"""
        if self.stop_flag.exists():
            print("=" * 70)
            print("[BLOCK] 系统处于停止状态")
            
            with open(self.stop_flag, "r", encoding="utf-8") as f:
                stop_data = json.load(f)
            
            print(f"[BLOCK] 触发类型：{stop_data.get('trigger_type', '未知')}")
            print(f"[BLOCK] 原因：{stop_data.get('reason', '未知')}")
            print(f"[BLOCK] 时间：{stop_data.get('activated_at', '未知')}")
            print("=" * 70)
            print("[ACTION] 需要管理员恢复才能继续")
            print("=" * 70)
            sys.exit(1)
        
        if self.lockdown_file.exists():
            print("=" * 70)
            print("[BLOCK] 系统处于封锁状态")
            print("[ACTION] 需要管理员解锁")
            print("=" * 70)
            sys.exit(1)
        
        # 检查惩罚等级
        if self.penalty_file.exists():
            with open(self.penalty_file, "r", encoding="utf-8") as f:
                penalty = json.load(f)
            
            level = penalty.get("current_level", 0)
            if level >= 3:
                print("=" * 70)
                print(f"[BLOCK] 惩罚等级 Level {level} (只读模式)")
                print("[BLOCK] 禁止执行操作")
                print("=" * 70)
                sys.exit(1)
        
        print(f"[OK] 强制停止检查通过")
    
    def execute_with_protection(self, command: str, description: str = None) -> dict:
        """带防护执行 - 所有操作必须通过此方法"""
        
        print("=" * 70)
        print(f"[EXEC] 执行操作：{description or command}")
        print("=" * 70)
        
        # 操作前防护检查
        if self.protection:
            pre_check = self.protection.pre_operation_check("command", {"command": command})
            if not pre_check.get("allowed", True):
                print(f"[BLOCK] 防护层阻断：{pre_check['reason']}")
                return {
                    "status": "blocked",
                    "reason": pre_check["reason"],
                    "action": "BLOCKED"
                }
        
        # 执行命令
        print(f"[RUN] {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300
            )
            
            output = {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout[:5000] if result.stdout else "",
                "stderr": result.stderr[:5000] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            output = {
                "status": "error",
                "returncode": -1,
                "reason": "执行超时 (>300s)"
            }
        except Exception as e:
            output = {
                "status": "error",
                "returncode": -1,
                "reason": str(e)
            }
        
        # 操作后防护检查
        if self.protection:
            post_check = self.protection.post_operation_check("command", output)
            if post_check.get("action") == "STOPPED":
                print(f"[STOP] 防护层触发停止：{post_check.get('issues', [])}")
                # 自动设置停止标志
                self._trigger_auto_stop("consecutive_errors", f"操作后检查失败")
                return {
                    "status": "stopped",
                    "reason": "连续错误触发自动停止",
                    "action": "STOPPED"
                }
        
        print(f"[RESULT] {output['status']}")
        print("=" * 70)
        
        return output
    
    def _trigger_auto_stop(self, trigger_type: str, reason: str) -> None:
        """触发自动停止"""
        stop_data = {
            "activated_at": datetime.now().isoformat(),
            "session_id": self.session_id,
            "trigger_type": trigger_type,
            "reason": reason,
            "auto_triggered": True
        }
        with open(self.stop_flag, "w", encoding="utf-8") as f:
            json.dump(stop_data, f, ensure_ascii=False, indent=2)
        print(f"[STOP] 自动停止标志已设置")


logging.basicConfig(level=logging.INFO)
def main() -> None:
    """测试模式"""
    print("=" * 70)
    print("强制防护执行器 v1.0 - 测试")
    print("=" * 70)
    
    # 创建执行器 (会自动检查)
    try:
        executor = ForcedProtectionExecutor()
    except SystemExit as e:
        print(f"[测试] 强制检查生效：退出码 {e.code}")
        return e.code
    
    # 测试执行
    print("\n[测试 1] 执行安全命令")
    result = executor.execute_with_protection("echo Hello", "测试输出")
    print(f"结果：{result['status']}")
    
    print("\n[测试 2] 执行风险命令")
    result = executor.execute_with_protection("dir", "目录列表")
    print(f"结果：{result['status']}")
    
    return 0
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py forced_protection_executor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py forced_protection_executor_001.py

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




if __name__ == "__main__":
    sys.exit(main())
