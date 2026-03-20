#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Executor - 唯一合法工具调用入口 (集成自动防护)
强制：必须有 session，自动记录日志
支持：command 字段（而非 path 字段）
【新增】自动防护检查 - 每次调用前自动检查防护状态
"""
import json
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 导入自动防护层
try:
    from auto_protection_layer import create_protection_layer
    AUTO_PROTECTION_ENABLED = True
except ImportError:
    AUTO_PROTECTION_ENABLED = False

# 导入权限验证器
try:
    from permission_validator import PermissionValidator
    PERMISSION_ENABLED = True
except ImportError:
    PERMISSION_ENABLED = False

class ToolExecutor:
    def __init__(self, role: str = "Executor"):
        self.registry_file = Path("30-scripts-tools/tools_registry.json")
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.log_file = Path("30-scripts-tools/tool_call_log.jsonl")
        self.session_id = None
        self.protection = None
        self.permission = None
        self.role = role
        
        # 加载防护层
        if AUTO_PROTECTION_ENABLED:
            self._load_protection()
        
        # 加载权限验证器
        if PERMISSION_ENABLED:
            self._load_permission()
        
        self._verify_session()
    
    def _load_protection(self):
        """加载防护层"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                session_id = state.get("session_id")
                if session_id:
                    self.protection = create_protection_layer(session_id)
        except Exception as e:
            print(f"[WARN] 防护层加载失败：{e}")
    
    def _load_permission(self):
        """加载权限验证器"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                session_id = state.get("session_id")
                if session_id:
                    self.permission = PermissionValidator(session_id, self.role)
        except Exception as e:
            print(f"[WARN] 权限验证器加载失败：{e}")
    
    def _verify_session(self):
        if not self.state_file.exists():
            raise RuntimeError(
                "[BLOCK] execution-state.json 不存在\n"
                "[ACTION] 必须通过 copaw_entry.py 启动任务"
            )
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.session_id = state.get("session_id")
        if not self.session_id:
            raise RuntimeError("[BLOCK] session_id 缺失")
        if not state.get("mandatory_execution"):
            raise RuntimeError("[BLOCK] mandatory_execution 未启用")
        print(f"[OK] Session 验证通过：{self.session_id}")
    
    def execute(self, tool_id: str, params: dict = None):
        if params is None:
            params = {}
        
        # 【新增】操作前防护检查
        if self.protection:
            pre_check = self.protection.pre_operation_check("tool_call", {"tool_id": tool_id})
            if not pre_check.get("allowed", True):
                print(f"[BLOCK] 防护层阻断：{pre_check['reason']}")
                return {
                    "status": "blocked",
                    "reason": pre_check["reason"],
                    "check_failed": pre_check.get("check_failed"),
                    "action": "BLOCKED"
                }
            if pre_check.get("requires_confirmation"):
                print(f"[WARN] 需要额外确认：{pre_check['reason']}")
        
        # 【新增 v10.1】权限验证
        if self.permission:
            perm_check = self.permission.verify_permission(tool_id)
            if not perm_check.get("allowed", False):
                print(f"[BLOCK] 权限不足：{perm_check.get('denial_reason', 'Unknown')}")
                return {
                    "status": "blocked",
                    "reason": "permission_denied",
                    "denial_reason": perm_check.get("denial_reason"),
                    "risk_level": perm_check.get("risk_level"),
                    "role": perm_check.get("role"),
                    "action": "PERMISSION_DENIED"
                }
            if perm_check.get("requires_confirmation"):
                print(f"[WARN] 需要确认：{tool_id} (风险等级：{perm_check.get('risk_level')})")
            if perm_check.get("requires_backup"):
                print(f"[INFO] 需要备份：{tool_id}")
        
        start = time.time()
        if not self._verify_registered(tool_id):
            raise ValueError(f"[BLOCK] 工具未注册：{tool_id}")
        result = self._run_tool(tool_id, params)
        duration = time.time() - start
        
        # 【新增】操作后防护检查
        if self.protection:
            post_check = self.protection.post_operation_check("tool_call", result)
            if post_check.get("action") == "STOPPED":
                print(f"[STOP] 防护层触发停止：{post_check.get('issues', [])}")
        
        self._log_call(tool_id, params, result, duration)
        return result
    
    def _verify_registered(self, tool_id):
        if not self.registry_file.exists():
            return False
        with open(self.registry_file, "r", encoding="utf-8") as f:
            registry = json.load(f)
        return tool_id in registry.get("tools", {})
    
    def _run_tool(self, tool_id, params):
        with open(self.registry_file, "r", encoding="utf-8") as f:
            registry = json.load(f)
        tool_info = registry["tools"].get(tool_id, {})
        
        # 支持 command 字段
        command = tool_info.get("command", "")
        if not command:
            # 回退到 path 字段
            tool_path = tool_info.get("path", "")
            if tool_path:
                command = f"py {tool_path}"
            else:
                # 回退到 file_path 字段 (旧格式)
                file_path = tool_info.get("file_path", "")
                if file_path:
                    command = f"py {file_path}"
                else:
                    return {"status": "error", "message": f"工具无 command/path/file_path: {tool_id}"}
        
        # 替换参数
        for key, value in params.items():
            command = command.replace("{" + key + "}", str(value))
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": f"工具超时：{tool_id}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _log_call(self, tool_id, params, result, duration):
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_id": tool_id,
            "params": params,
            "result_summary": str(result)[:200],
            "duration_seconds": duration,
            "session_id": self.session_id
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[TRACK] {tool_id} - {duration:.2f}s")

def main():
    if len(sys.argv) < 2:
        print("用法：py tool_executor.py <tool_id> [params_json]")
        sys.exit(1)
    tool_id = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    try:
        executor = ToolExecutor()
        result = executor.execute(tool_id, params)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
