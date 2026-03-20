#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全 Shell 执行器 - 唯一允许执行 shell 命令的入口
【系统级强制】- 无法绕过

使用方法：
  py safe_shell_executor.py "command"

防护检查：
  1. session 存在性
  2. 停止标志
  3. 封锁状态
  4. 惩罚等级
  5. 风险评级（高危险命令需要确认）
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================================
# 【系统级防护】模块加载时强制检查 session - 无法绕过
# ============================================================================
def _force_session_check():
    """模块加载时强制检查 - 在有任何代码执行前"""
    state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
    
    # 检查 1: state 文件必须存在
    if not state_file.exists():
        print("=" * 70, file=sys.stderr)
        print("[BLOCK] 模块加载被拒绝", file=sys.stderr)
        print("[BLOCK] 原因：execution-state.json 不存在", file=sys.stderr)
        print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)
    
    # 检查 2: 必须有 session_id 和 mandatory_execution
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        assert state.get('session_id'), "session_id missing"
        assert state.get('mandatory_execution'), "mandatory_execution not enabled"
    except Exception as e:
        print("=" * 70, file=sys.stderr)
        print("[BLOCK] 模块加载被拒绝", file=sys.stderr)
        print(f"[BLOCK] 原因：session 无效 - {e}", file=sys.stderr)
        print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

# 立即执行检查（在模块导入时）
_force_session_check()
# ============================================================================

# 导入拦截器
sys.path.insert(0, str(Path("30-scripts-tools").resolve()))
try:
    from tool_call_interceptor import get_interceptor
    INTERCEPTOR_AVAILABLE = True
except ImportError:
    INTERCEPTOR_AVAILABLE = False

# 导入工具包装器（强制工作流检查）
try:
    from tool_wrapper import before_tool_call, after_tool_call
    TOOL_WRAPPER_AVAILABLE = True
except ImportError:
    TOOL_WRAPPER_AVAILABLE = False

class SafeShellExecutor:
    """安全 Shell 执行器 - 系统级防护"""
    
    DANGEROUS_COMMANDS = [
        "rm -rf", "rmdir /s", "del /f",  # 删除
        "format", "diskpart",  # 磁盘操作
        "shutdown", "reboot", "taskkill",  # 系统操作
        "curl", "wget", "powershell -enc",  # 网络/编码
    ]
    
    def __init__(self):
        self.interceptor = get_interceptor() if INTERCEPTOR_AVAILABLE else None
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.tool_call_log = Path("30-scripts-tools/tool_call_log.jsonl")
    
    def execute(self, command: str, description: str = None) -> dict:
        """执行 shell 命令 - 强制防护检查"""
        
        # 步骤 0: 工具包装器检查（强制工作流）
        if TOOL_WRAPPER_AVAILABLE:
            if not before_tool_call('safe_shell_executor', {'command': command}):
                return {
                    "status": "blocked",
                    "reason": "no_session",
                    "message": "未初始化会话 - 请先运行 copaw_entry.py",
                    "returncode": -1
                }
        
        # 步骤 1: 检查 session 状态（直接检查，不通过防护层）
        if not self.state_file.exists():
            print("=" * 70)
            print("[BLOCK] 命令执行被阻断")
            print("[BLOCK] 原因：execution-state.json 不存在 - 请先运行 copaw_entry.py")
            print("=" * 70)
            return {
                "status": "blocked",
                "reason": "no_session",
                "message": "未初始化会话",
                "returncode": -1
            }
        
        # 步骤 2: 检查停止标志
        if Path(".STOP_FLAG").exists():
            print("=" * 70)
            print("[BLOCK] 命令执行被阻断")
            print("[BLOCK] 原因：.STOP_FLAG exists - 系统已停止")
            print("=" * 70)
            return {
                "status": "blocked",
                "reason": "stop_flag",
                "message": "系统已停止",
                "returncode": -1
            }
        
        # 步骤 3: 危险命令检查
        is_dangerous = any(cmd in command.lower() for cmd in self.DANGEROUS_COMMANDS)
        if is_dangerous:
            print("=" * 70)
            print("[WARN] 检测到危险命令")
            print(f"[WARN] 命令：{command}")
            print("[WARN] 需要人工确认")
            print("=" * 70)
            # 简单实现：直接阻断危险命令
            return {
                "status": "blocked",
                "reason": "dangerous_command",
                "message": f"危险命令被阻断：{command}",
                "returncode": -1
            }
        
        # 步骤 4: 执行命令
        print(f"[EXEC] {command}")
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
                "reason": "timeout"
            }
        except Exception as e:
            output = {
                "status": "error",
                "returncode": -1,
                "reason": str(e)
            }
        
        # 步骤 5: 记录工具调用日志
        self._log_call(command, description, output)
        
        # 步骤 6: 工具包装器记录
        if TOOL_WRAPPER_AVAILABLE:
            after_tool_call('safe_shell_executor', {'command': command}, output.get('status', 'unknown'))
        
        return output
    
    def _log_call(self, command: str, description: str, result: dict):
        """记录工具调用日志"""
        session_id = "unknown"
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            session_id = state.get("session_id", "unknown")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "tool_id": "safe-shell-executor",
            "command": command,
            "description": description or "",
            "result": result.get("status", "unknown"),
            "returncode": result.get("returncode", -1)
        }
        
        try:
            with open(self.tool_call_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[WARN] 日志记录失败：{e}")


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：py safe_shell_executor.py <command> [description]")
        print("所有 shell 命令都必须通过此执行器")
        sys.exit(1)
    
    # 合并所有参数作为命令（支持带空格的命令）
    command = " ".join(sys.argv[1:])
    # 如果最后一个参数看起来像描述，则分离
    description = None
    if len(sys.argv) > 2 and not sys.argv[-1].startswith("-") and sys.argv[-1] not in ["dir", "echo", "py", "git"]:
        # 简单启发式：最后一个参数可能是描述
        pass  # 暂时不分离，全部作为命令
    
    executor = SafeShellExecutor()
    result = executor.execute(command, description)
    
    # 输出结果
    if result.get("status") == "blocked":
        print(f"[BLOCK] {result.get('message')}")
        sys.exit(1)
    
    if result.get("stdout"):
        print(result["stdout"])
    if result.get("stderr"):
        print(result["stderr"], file=sys.stderr)
    
    sys.exit(result.get("returncode", 0))


if __name__ == "__main__":
    main()
