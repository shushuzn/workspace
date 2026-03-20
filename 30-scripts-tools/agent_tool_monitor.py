#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent 工具监控器 - 监控 execute_shell_command 调用
【防护 v4 核心】- 检测并记录绕过防护的行为

工作原理:
  1. 每次 Agent 调用 execute_shell_command 时，此工具会被触发
  2. 检查命令是否通过 safe_shell_executor
  3. 如果直接调用 → 记录违规 + 惩罚
  4. 如果通过防护 → 记录合规

使用方法:
  在 agent 工具定义中，将 execute_shell_command 包装为:
  monitor.check_and_execute(command)
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
COMPLIANCE_LOG = Path("30-scripts-tools/shell_compliance_log.jsonl")
PENALTY_FILE = Path("30-scripts-tools/penalty_state.json")
STOP_FLAG = Path("30-scripts-tools/.STOP_FLAG")

class AgentToolMonitor:
    """Agent 工具监控器 - 防护 v4"""
    
    def __init__(self):
        self.session_id = self._get_session_id()
        self.safe_prefixes = [
            "safe_shell_executor.py",
            "safe_shell.bat",
            "protected_py.py",
            "tool_executor.py",
        ]
    
    def _get_session_id(self):
        """获取当前 session_id"""
        if not STATE_FILE.exists():
            return None
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("session_id")
    
    def check_and_execute(self, command: str, description: str = None) -> dict:
        """检查并执行命令"""
        
        # 检查 1: session 存在性
        if not self.session_id:
            return self._block("no_session", "没有有效 session，必须通过 copaw_entry.py 启动")
        
        # 检查 2: 是否通过防护层
        is_protected = any(prefix in command for prefix in self.safe_prefixes)
        
        if not is_protected:
            # 检测到绕过防护！
            return self._violation(command, "绕过防护层 - 未使用 safe_shell_executor")
        
        # 检查 3: 执行命令（已防护）
        result = self._execute(command)
        
        # 记录合规日志
        self._log_compliance(command, description, result)
        
        return result
    
    def _execute(self, command: str) -> dict:
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout[:5000] if result.stdout else "",
                "stderr": result.stderr[:5000] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "returncode": -1, "reason": "timeout"}
        except Exception as e:
            return {"status": "error", "returncode": -1, "reason": str(e)}
    
    def _violation(self, command: str, reason: str) -> dict:
        """记录违规并惩罚"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "violation_type": "bypass_protection",
            "command": command,
            "reason": reason,
            "action": "BLOCKED",
            "penalty_points": 50
        }
        
        # 记录违规日志
        with open(VIOLATION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(violation, ensure_ascii=False) + "\n")
        
        # 增加惩罚分
        self._add_penalty(50)
        
        # 检查是否达到自动停止阈值
        self._check_auto_stop()
        
        return {
            "status": "blocked",
            "reason": reason,
            "message": f"检测到绕过防护！已记录违规 +50 分",
            "penalty": 50
        }
    
    def _log_compliance(self, command: str, description: str, result: dict):
        """记录合规日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "command": command,
            "description": description or "",
            "result": result.get("status", "unknown"),
            "compliance": True
        }
        
        with open(COMPLIANCE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def _add_penalty(self, points: int):
        """增加惩罚分"""
        penalty = {"current_level": 0, "total_points": 0, "violations": []}
        
        if PENALTY_FILE.exists():
            with open(PENALTY_FILE, "r", encoding="utf-8") as f:
                penalty = json.load(f)
        
        penalty["total_points"] += points
        penalty["violations"].append({
            "timestamp": datetime.now().isoformat(),
            "points": points,
            "reason": "bypass_protection"
        })
        
        # 计算等级
        if penalty["total_points"] >= 50:
            penalty["current_level"] = 4
        elif penalty["total_points"] >= 30:
            penalty["current_level"] = 3
        elif penalty["total_points"] >= 20:
            penalty["current_level"] = 2
        elif penalty["total_points"] >= 10:
            penalty["current_level"] = 1
        
        with open(PENALTY_FILE, "w", encoding="utf-8") as f:
            json.dump(penalty, f, ensure_ascii=False, indent=2)
    
    def _check_auto_stop(self):
        """检查是否需要自动停止"""
        if not PENALTY_FILE.exists():
            return
        
        with open(PENALTY_FILE, "r", encoding="utf-8") as f:
            penalty = json.load(f)
        
        if penalty.get("current_level", 0) >= 4:
            # 自动停止
            stop_data = {
                "activated_at": datetime.now().isoformat(),
                "session_id": self.session_id,
                "trigger_type": "penalty_level_4",
                "reason": f"惩罚等级达到 Level 4 ({penalty['total_points']}分)",
                "auto_triggered": True
            }
            
            with open(STOP_FLAG, "w", encoding="utf-8") as f:
                json.dump(stop_data, f, ensure_ascii=False, indent=2)
    
    def get_compliance_report(self) -> dict:
        """获取合规报告"""
        compliance_count = 0
        violation_count = 0
        
        if COMPLIANCE_LOG.exists():
            with open(COMPLIANCE_LOG, "r", encoding="utf-8") as f:
                compliance_count = sum(1 for _ in f)
        
        if VIOLATION_LOG.exists():
            with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
                violation_count = sum(1 for _ in f)
        
        total = compliance_count + violation_count
        compliance_rate = (compliance_count / total * 100) if total > 0 else 0
        
        return {
            "session_id": self.session_id,
            "compliance_count": compliance_count,
            "violation_count": violation_count,
            "compliance_rate": round(compliance_rate, 2),
            "status": "compliant" if compliance_rate >= 95 else "warning" if compliance_rate >= 80 else "non_compliant"
        }


def main():
    """命令行入口"""
    monitor = AgentToolMonitor()
    
    if len(sys.argv) < 2:
        # 显示合规报告
        report = monitor.get_compliance_report()
        print("=" * 70)
        print("Agent 工具合规报告")
        print("=" * 70)
        print(f"会话：{report['session_id']}")
        print(f"合规调用：{report['compliance_count']}")
        print(f"违规调用：{report['violation_count']}")
        print(f"合规率：{report['compliance_rate']}%")
        print(f"状态：{report['status']}")
        print("=" * 70)
        return 0
    
    # 执行命令
    command = " ".join(sys.argv[1:])
    result = monitor.check_and_execute(command)
    
    if result.get("status") == "blocked":
        print(f"[BLOCK] {result.get('message')}")
        return 1
    
    if result.get("stdout"):
        print(result["stdout"])
    if result.get("stderr"):
        print(result["stderr"], file=sys.stderr)
    
    return result.get("returncode", 0)


if __name__ == "__main__":
    sys.exit(main())
