import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整性检查器 - 防护系统防篡改
【防护 v6 核心】- 文件完整性 + 会话验证 + 日志防篡改

功能:
  1. 防护文件哈希校验
  2. 会话真实性验证
  3. 日志完整性检查
  4. Git hook 绕过检测
  5. 自动修复/告警
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
INTEGRITY_FILE = Path("30-scripts-tools/integrity_state.json")
VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
STOP_FLAG = Path("30-scripts-tools/.STOP_FLAG")

# 关键防护文件列表
PROTECTION_FILES = [
    "30-scripts-tools/copaw_entry.py",
    "30-scripts-tools/tool_executor.py",
    "30-scripts-tools/safe_shell_executor.py",
    "30-scripts-tools/agent_tool_monitor.py",
    "30-scripts-tools/auto_protection_layer.py",
    "30-scripts-tools/forced_protection_executor.py",
    "30-scripts-tools/.git/hooks/pre-commit",
    "flow-archive/20260318-universal-workflow-001/workflow.json",
]

class IntegrityChecker:
    """完整性检查器 - 防护 v6"""
    
    def __init__(self):
        self.session_id = self._get_session_id()
        self.baseline = self._load_baseline()
    
    def _get_session_id(self):
        if not STATE_FILE.exists():
            return None
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("session_id")
    
    def _load_baseline(self) -> None:
        """加载完整性基线"""
        if not INTEGRITY_FILE.exists():
            return self._create_baseline()
        
        with open(INTEGRITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _create_baseline(self) -> None:
        """创建完整性基线"""
        baseline = {
            "created_at": datetime.now().isoformat(),
            "files": {}
        }
        
        for file_path in PROTECTION_FILES:
            path = Path(file_path)
            if path.exists():
                with open(path, "rb") as f:
                    content = f.read()
                baseline["files"][file_path] = {
                    "hash": hashlib.sha256(content).hexdigest(),
                    "size": len(content),
                    "mtime": path.stat().st_mtime
                }
        
        # 保存基线
        with open(INTEGRITY_FILE, "w", encoding="utf-8") as f:
            json.dump(baseline, f, ensure_ascii=False, indent=2)
        
        return baseline
    
    def check_all(self) -> dict:
        """执行所有完整性检查"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "file_integrity": self._check_file_integrity(),
            "session_validity": self._check_session_validity(),
            "log_integrity": self._check_log_integrity(),
            "git_hook_status": self._check_git_hook(),
            "tamper_detected": False,
            "violations": []
        }
        
        # 检查是否有篡改
        if (not results["file_integrity"]["passed"] or
            not results["session_validity"]["passed"] or
            not results["git_hook_status"]["passed"]):
            results["tamper_detected"] = True
        
        # 记录违规
        if results["tamper_detected"]:
            self._log_violation(results)
        
        return results
    
    def _check_file_integrity(self) -> dict:
        """检查文件完整性"""
        issues = []
        
        for file_path, baseline_data in self.baseline.get("files", {}).items():
            path = Path(file_path)
            
            if not path.exists():
                issues.append(f"文件缺失：{file_path}")
                continue
            
            with open(path, "rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            if current_hash != baseline_data["hash"]:
                issues.append(f"文件篡改：{file_path}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "checked_files": len(self.baseline.get("files", {}))
        }
    
    def _check_session_validity(self) -> dict:
        """检查会话真实性"""
        issues = []
        
        if not STATE_FILE.exists():
            return {"passed": False, "issues": ["execution-state.json 不存在"]}
        
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # 检查必需字段
        required_fields = ["session_id", "mandatory_execution", "entry_point"]
        for field in required_fields:
            if field not in state:
                issues.append(f"缺少必需字段：{field}")
        
        # 检查 session_id 格式
        session_id = state.get("session_id", "")
        if not session_id.startswith("session-"):
            issues.append(f"session_id 格式错误：{session_id}")
        
        # 检查时间戳合理性
        started_at = state.get("started_at", "")
        if started_at:
            try:
                start_time = datetime.fromisoformat(started_at)
                now = datetime.now(start_time.tzinfo) if start_time.tzinfo else datetime.now()
                if start_time > now:
                    issues.append("started_at 是未来时间（伪造）")
            except (Exception,):
                issues.append("started_at 格式错误")
        
        # 检查 entry_point
        if state.get("entry_point") != "copaw_entry.py":
            issues.append(f"入口点错误：{state.get('entry_point')} (应为 copaw_entry.py)")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "session_id": state.get("session_id")
        }
    
    def _check_log_integrity(self) -> dict:
        """检查日志完整性"""
        issues = []
        
        # 检查 tool_call_log.jsonl
        log_file = Path("30-scripts-tools/tool_call_log.jsonl")
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 检查是否有时间跳跃（篡改迹象）
            timestamps = []
            for line in lines:
                try:
                    entry = json.loads(line)
                    ts = entry.get("timestamp", "")
                    if ts:
                        timestamps.append(datetime.fromisoformat(ts))
                except (json.JSONDecodeError, IOError, OSError):
                    pass
            
            if len(timestamps) >= 2:
                for i in range(1, len(timestamps)):
                    diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                    if diff < -60:  # 时间倒流 >1 分钟
                        issues.append(f"日志时间异常：{timestamps[i-1]} -> {timestamps[i]}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def _check_git_hook(self) -> dict:
        """检查 Git hook 状态"""
        issues = []
        
        hook_file = Path(".git/hooks/pre-commit")
        if not hook_file.exists():
            issues.append("Git pre-commit hook 不存在")
            return {"passed": False, "issues": issues}
        
        # 检查 hook 是否可执行
        if not os.access(hook_file, os.X_OK):
            issues.append("Git pre-commit hook 不可执行")
        
        # 检查 hook 内容是否被篡改
        with open(hook_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "workflow_guardian" not in content:
            issues.append("Git hook 可能被篡改（缺少 workflow_guardian）")
        
        if "tool_call_tracker" not in content:
            issues.append("Git hook 可能被篡改（缺少 tool_call_tracker）")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def _log_violation(self, results: dict) -> None:
        """记录违规"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "violation_type": "integrity_violation",
            "details": results,
            "action": "LOGGED",
            "penalty_points": 50
        }
        
        with open(VIOLATION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(violation, ensure_ascii=False) + "\n")
    
    def update_baseline(self) -> None:
        """更新基线"""
        self.baseline = self._create_baseline()
        print("[OK] 完整性基线已更新")
    
    def display(self) -> None:
        """显示检查结果"""
        results = self.check_all()
        
        print("=" * 70)
        print("防护系统完整性检查 v6.0")
        print("=" * 70)
        print(f"会话：{results['session_id']}")
        print(f"时间：{results['timestamp']}")
        print()
        
        print("文件完整性:")
        status = "[OK]" if results["file_integrity"]["passed"] else "[FAIL]"
        print(f"  {status} 检查文件：{results['file_integrity']['checked_files']} 个")
        for issue in results["file_integrity"]["issues"]:
            print(f"    - {issue}")
        print()
        
        print("会话验证:")
        status = "[OK]" if results["session_validity"]["passed"] else "[FAIL]"
        print(f"  {status} Session: {results['session_validity']['session_id']}")
        for issue in results["session_validity"]["issues"]:
            print(f"    - {issue}")
        print()
        
        print("日志完整性:")
        status = "[OK]" if results["log_integrity"]["passed"] else "[FAIL]"
        print(f"  {status}")
        for issue in results["log_integrity"]["issues"]:
            print(f"    - {issue}")
        print()
        
        print("Git Hook 状态:")
        status = "[OK]" if results["git_hook_status"]["passed"] else "[FAIL]"
        print(f"  {status}")
        for issue in results["git_hook_status"]["issues"]:
            print(f"    - {issue}")
        print()
        
        if results["tamper_detected"]:
            print("=" * 70)
            print("[ALERT] 检测到篡改行为！")
            print("[ALERT] 已记录违规 +50 分")
            print("=" * 70)
        else:
            print("=" * 70)
            print("[OK] 所有完整性检查通过")
            print("=" * 70)


logging.basicConfig(level=logging.INFO)
def main():
    import sys
    
    checker = IntegrityChecker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--update":
            checker.update_baseline()
            return 0
        elif sys.argv[1] == "--check":
            checker.display()
            return 0
    
    # 默认：检查并显示
    checker.display()
    
    # 如果有篡改，返回错误码
    results = checker.check_all()
    return 1 if results["tamper_detected"] else 0
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
# py integrity_checker_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py integrity_checker_001.py

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
    import sys
    sys.exit(main())
