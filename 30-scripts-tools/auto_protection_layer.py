#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化防护集成层 v1.0
所有防护检查自动执行，不依赖 AI 主动调用
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# 导入防护工具
SCRIPTS_DIR = Path("30-scripts-tools")

class AutoProtectionLayer:
    """自动化防护层 - 所有检查自动执行"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.violations = []
        self.stopped = False
        
        # 自动加载防护状态
        self._load_protection_state()
    
    def _load_protection_state(self):
        """加载防护状态"""
        # 检查停止标志
        stop_flag = SCRIPTS_DIR / ".STOP_FLAG"
        if stop_flag.exists():
            self.stopped = True
        
        # 检查封锁状态
        lockdown_file = SCRIPTS_DIR / ".lockdown_active"
        if lockdown_file.exists():
            self.stopped = True
    
    def pre_operation_check(self, operation_type: str, details: dict = None) -> dict:
        """操作前自动检查 (每次操作前必须调用)"""
        
        if self.stopped:
            return {
                "allowed": False,
                "reason": "系统处于停止状态",
                "action": "BLOCKED"
            }
        
        checks = {
            "lockdown": self._check_lockdown(),
            "penalty": self._check_penalty_level(),
            "stop_flag": self._check_stop_flag(),
        }
        
        # 任何检查失败 → 阻断
        for check_name, check_result in checks.items():
            if not check_result["passed"]:
                return {
                    "allowed": False,
                    "reason": check_result["reason"],
                    "check_failed": check_name,
                    "action": "BLOCKED"
                }
        
        return {
            "allowed": True,
            "reason": "所有检查通过",
            "action": "ALLOWED"
        }
    
    def _check_lockdown(self) -> dict:
        """检查封锁状态"""
        lockdown_file = SCRIPTS_DIR / ".lockdown_active"
        if lockdown_file.exists():
            return {
                "passed": False,
                "reason": "系统处于封锁状态"
            }
        return {"passed": True, "reason": "无封锁"}
    
    def _check_penalty_level(self) -> dict:
        """检查惩罚等级"""
        penalty_file = SCRIPTS_DIR / "penalty_state.json"
        if penalty_file.exists():
            with open(penalty_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            level = state.get("current_level", 0)
            if level >= 3:
                return {
                    "passed": False,
                    "reason": f"惩罚等级 Level {level} (只读模式)"
                }
            elif level >= 1:
                # Level 1-2 需要额外确认
                return {
                    "passed": True,
                    "reason": f"惩罚等级 Level {level} (需要确认)",
                    "requires_confirmation": True
                }
        return {"passed": True, "reason": "无惩罚"}
    
    def _check_stop_flag(self) -> dict:
        """检查停止标志"""
        stop_flag = SCRIPTS_DIR / ".STOP_FLAG"
        if stop_flag.exists():
            return {
                "passed": False,
                "reason": "停止标志激活"
            }
        return {"passed": True, "reason": "无停止"}
    
    def post_operation_check(self, operation_type: str, result: dict) -> dict:
        """操作后自动检查 (每次操作后自动执行)"""
        
        issues = []
        
        # 检查结果是否有效
        if result is None:
            issues.append("操作结果为空")
        
        # 检查是否有错误
        if isinstance(result, dict):
            if result.get("status") == "error":
                issues.append(f"操作错误：{result.get('reason', '未知')}")
            
            # 检查返回码
            if "returncode" in result and result["returncode"] != 0:
                if result.get("status") == "success":
                    issues.append(f"成功状态但返回码非零：{result['returncode']}")
        
        # 如果有问题，记录并可能触发停止
        if issues:
            self._record_issue(operation_type, issues)
            
            # 连续错误触发停止
            if len(self.violations) >= 3:
                self._trigger_auto_stop("consecutive_errors", f"连续 {len(self.violations)} 次错误")
            
            return {
                "status": "issues_detected",
                "issues": issues,
                "violations_count": len(self.violations),
                "action": "WARNING" if len(self.violations) < 3 else "STOPPED"
            }
        
        return {
            "status": "clean",
            "action": "CONTINUE"
        }
    
    def workflow_step_check(self, step_id: int, step_name: str, completed: bool) -> dict:
        """工作流步骤检查 (每步执行前后自动调用)"""
        
        if not completed:
            # 步骤未完成，检查原因
            return {
                "status": "incomplete",
                "step_id": step_id,
                "action": "RETRY"
            }
        
        # 步骤完成，记录
        return {
            "status": "completed",
            "step_id": step_id,
            "action": "CONTINUE"
        }
    
    def workflow_completion_check(self, completion_percentage: float, compliance: bool) -> dict:
        """工作流完成检查 (自动决定奖励或惩罚)"""
        
        from pathlib import Path
        
        if completion_percentage == 100 and compliance:
            # 100% 完成 → 自动授予奖励
            return self._auto_award_reward()
        elif completion_percentage < 50:
            # 完成率过低 → 记录违规
            return self._record_violation("incomplete_workflow", f"完成率仅 {completion_percentage}%")
        else:
            # 部分完成 → 无奖励无惩罚
            return {
                "status": "partial",
                "completion": completion_percentage,
                "action": "NO_REWARD"
            }
    
    def _auto_award_reward(self) -> dict:
        """自动授予奖励"""
        # 调用奖励系统
        reward_script = SCRIPTS_DIR / "reward_system.py"
        if reward_script.exists():
            # 这里记录待授予的奖励，实际授予由 session_end 执行
            return {
                "status": "reward_pending",
                "rewards": [
                    "complete_workflow_100",
                    "zero_violations"
                ],
                "action": "AWARD"
            }
        return {"status": "error", "reason": "奖励系统不可用"}
    
    def _record_violation(self, violation_type: str, reason: str) -> dict:
        """记录违规"""
        violation = {
            "type": violation_type,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.violations.append(violation)
        
        # 调用惩罚系统
        penalty_script = SCRIPTS_DIR / "penalty_system_v2.py"
        if penalty_script.exists():
            # 这里记录待处理的违规，实际记录由统一入口执行
            pass
        
        return {
            "status": "violation_recorded",
            "violation": violation,
            "action": "PENALIZE"
        }
    
    def _record_issue(self, operation_type: str, issues: list):
        """记录问题"""
        issue = {
            "operation": operation_type,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
        self.violations.append(issue)
    
    def _trigger_auto_stop(self, trigger_type: str, reason: str):
        """触发自动停止"""
        stop_script = SCRIPTS_DIR / "emergency_stop.py"
        if stop_script.exists():
            # 设置停止标志
            stop_flag = SCRIPTS_DIR / ".STOP_FLAG"
            stop_data = {
                "activated_at": datetime.now().isoformat(),
                "session_id": self.session_id,
                "trigger_type": trigger_type,
                "reason": reason,
                "auto_triggered": True
            }
            with open(stop_flag, "w", encoding="utf-8") as f:
                json.dump(stop_data, f, ensure_ascii=False, indent=2)
            
            self.stopped = True
    
    def get_protection_report(self) -> dict:
        """生成防护报告"""
        return {
            "session_id": self.session_id,
            "stopped": self.stopped,
            "violations_count": len(self.violations),
            "violations": self.violations,
            "status": "ACTIVE" if not self.stopped else "STOPPED"
        }


def create_protection_layer(session_id: str) -> AutoProtectionLayer:
    """创建防护层实例"""
    return AutoProtectionLayer(session_id)


def main():
    """测试模式"""
    print("=" * 70)
    print("自动化防护集成层 v1.0")
    print("=" * 70)
    
    # 创建防护层
    protection = create_protection_layer("session-test-auto")
    
    # 测试操作前检查
    print("\n[测试 1] 操作前检查")
    result = protection.pre_operation_check("tool_call", {"tool_id": "test"})
    print(f"允许：{result['allowed']}")
    print(f"操作：{result['action']}")
    
    # 测试操作后检查
    print("\n[测试 2] 操作后检查")
    result = protection.post_operation_check("tool_call", {"status": "success"})
    print(f"状态：{result['status']}")
    print(f"操作：{result['action']}")
    
    # 测试工作流步骤检查
    print("\n[测试 3] 工作流步骤检查")
    result = protection.workflow_step_check(1, "上下文加载", True)
    print(f"步骤 1: {result['status']}")
    
    # 测试工作流完成检查
    print("\n[测试 4] 工作流完成检查")
    result = protection.workflow_completion_check(100, True)
    print(f"完成检查：{result['status']}")
    print(f"操作：{result['action']}")
    
    # 生成报告
    print("\n[测试 5] 防护报告")
    report = protection.get_protection_report()
    print(f"状态：{report['status']}")
    print(f"违规数：{report['violations_count']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
