#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
立即停止机制 - 出现问题立刻停止所有操作
紧急制动系统
"""
import json
import sys
from pathlib import Path
from datetime import datetime

STOP_FLAG = Path("30-scripts-tools/.STOP_FLAG")
EMERGENCY_LOG = Path("30-scripts-tools/emergency_stop_log.jsonl")

# 触发立即停止的条件
STOP_TRIGGERS = {
    "critical_violation": {
        "name": "Critical 违规",
        "severity": "critical",
        "auto_stop": True,
        "message": "检测到 Critical 级别违规"
    },
    "lockdown_active": {
        "name": "系统封锁",
        "severity": "critical",
        "auto_stop": True,
        "message": "系统处于封锁状态"
    },
    "fabrication_detected": {
        "name": "检测到编造",
        "severity": "critical",
        "auto_stop": True,
        "message": "检测到结果编造"
    },
    "workflow_tampering": {
        "name": "工作流篡改",
        "severity": "critical",
        "auto_stop": True,
        "message": "检测到工作流状态篡改"
    },
    "tool_call_fraud": {
        "name": "工具调用欺诈",
        "severity": "critical",
        "auto_stop": True,
        "message": "检测到工具调用记录欺诈"
    },
    "consecutive_errors": {
        "name": "连续错误",
        "severity": "high",
        "threshold": 3,
        "auto_stop": True,
        "message": "连续 3 次错误"
    },
    "guardian_failure": {
        "name": "守护者检查失败",
        "severity": "high",
        "auto_stop": True,
        "message": "Workflow Guardian 检查失败"
    },
    "hook_block": {
        "name": "Git Hook 阻止",
        "severity": "high",
        "auto_stop": True,
        "message": "Git Pre-Commit Hook 阻止提交"
    },
    "manual_stop": {
        "name": "手动停止",
        "severity": "medium",
        "auto_stop": False,
        "message": "用户手动触发停止"
    },
}

def trigger_stop(reason: str, session_id: str, trigger_type: str = "manual_stop", details: dict = None) -> dict:
    """触发立即停止"""

    if trigger_type not in STOP_TRIGGERS:
        trigger_type = "manual_stop"

    trigger_info = STOP_TRIGGERS[trigger_type]

    # 设置停止标志
    stop_data = {
        "activated_at": datetime.now().isoformat(),
        "session_id": session_id,
        "trigger_type": trigger_type,
        "trigger_name": trigger_info["name"],
        "severity": trigger_info["severity"],
        "reason": reason,
        "details": details,
        "status": "active",
        "auto_triggered": trigger_info.get("auto_stop", False)
    }

    with open(STOP_FLAG, "w", encoding="utf-8") as f:
        json.dump(stop_data, f, ensure_ascii=False, indent=2)

    # 记录到紧急日志
    emergency_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "emergency_stop",
        "data": stop_data
    }

    with open(EMERGENCY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(emergency_entry, ensure_ascii=False) + "\n")

    # 如果自动触发，同时记录违规
    if trigger_info.get("auto_stop", False):
        from pathlib import Path
        penalty_script = Path("30-scripts-tools/penalty_system_v2.py")
        if penalty_script.exists():
            # 这里不直接调用，而是记录待处理
            stop_data["pending_penalty"] = True

    return {
        "status": "stopped",
        "stop_flag": "ACTIVE",
        "trigger": trigger_info["name"],
        "severity": trigger_info["severity"],
        "message": f"[紧急停止] {trigger_info['message']}",
        "reason": reason
    }

def check_stop_status() -> dict:
    """检查停止状态"""

    if not STOP_FLAG.exists():
        return {
            "status": "running",
            "stop_flag": "CLEAR",
            "message": "系统正常运行"
        }

    try:
        with open(STOP_FLAG, "r", encoding="utf-8") as f:
            stop_data = json.load(f)

        return {
            "status": "stopped",
            "stop_flag": "ACTIVE",
            "activated_at": stop_data["activated_at"],
            "trigger_type": stop_data["trigger_type"],
            "trigger_name": stop_data["trigger_name"],
            "severity": stop_data["severity"],
            "reason": stop_data["reason"],
            "session_id": stop_data.get("session_id"),
            "auto_triggered": stop_data.get("auto_triggered", False)
        }
    except Exception as e:
        return {
            "status": "error",
            "stop_flag": "ERROR",
            "reason": str(e)
        }

def resume_operation(admin_code: str = None, reason: str = None) -> dict:
    """恢复操作 (需要管理员授权)"""

    if not STOP_FLAG.exists():
        return {
            "status": "skip",
            "message": "无活跃停止标志"
        }

    # 读取停止数据
    with open(STOP_FLAG, "r", encoding="utf-8") as f:
        stop_data = json.load(f)

    # 检查是否需要管理员授权
    if stop_data.get("severity") in ["critical", "high"]:
        if admin_code is None:
            return {
                "status": "error",
                "message": "需要管理员授权码才能恢复"
            }
        # 简化：实际应该验证授权码

    # 移除停止标志
    STOP_FLAG.unlink()

    # 记录恢复
    resume_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "resume_operation",
        "previous_stop": stop_data,
        "resume_reason": reason,
        "admin_code_provided": admin_code is not None
    }

    with open(EMERGENCY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(resume_entry, ensure_ascii=False) + "\n")

    return {
        "status": "resumed",
        "message": "操作已恢复",
        "stopped_duration": "未知",
        "resume_reason": reason
    }

def can_proceed() -> dict:
    """检查是否可以继续操作"""

    stop_status = check_stop_status()

    if stop_status["status"] == "stopped":
        return {
            "can_proceed": False,
            "reason": "系统处于停止状态",
            "details": stop_status
        }

    # 检查惩罚状态
    penalty_state = Path("30-scripts-tools/penalty_state.json")
    if penalty_state.exists():
        with open(penalty_state, "r", encoding="utf-8") as f:
            penalty = json.load(f)

        if penalty.get("current_level", 0) >= 3:
            return {
                "can_proceed": False,
                "reason": f"惩罚等级 Level {penalty['current_level']} ({penalty.get('level_name', '未知')})",
                "details": penalty
            }

    # 检查封锁状态
    lockdown_file = Path("30-scripts-tools/.lockdown_active")
    if lockdown_file.exists():
        return {
            "can_proceed": False,
            "reason": "系统处于封锁状态",
            "details": {"lockdown": "active"}
        }

    return {
        "can_proceed": True,
        "reason": "所有检查通过",
        "status": "clear"
    }

def list_emergency_events(limit: int = 50) -> dict:
    """列出紧急事件"""

    if not EMERGENCY_LOG.exists():
        return {"status": "empty", "message": "无紧急事件记录"}

    events = []
    with open(EMERGENCY_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                events.append(entry)
            except Exception:
                pass

    events.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "status": "success",
        "count": len(events),
        "events": events[:limit]
    }

def clear_stop_flag():
    """清除停止标志 (管理员功能)"""
    if STOP_FLAG.exists():
        STOP_FLAG.unlink()

def main():
    if len(sys.argv) < 2:
        # 测试模式
        print("=" * 70)
        print("立即停止机制 v1.0")
        print("=" * 70)

        # 检查当前状态
        status = check_stop_status()
        print(f"\n停止标志：{status['stop_flag']}")
        if status['status'] == 'stopped':
            print(f"触发类型：{status.get('trigger_name', '未知')}")
            print(f"严重程度：{status.get('severity', '未知')}")
            print(f"原因：{status.get('reason', '未知')}")

        # 检查是否可以继续
        can = can_proceed()
        print(f"\n可以继续操作：{'是' if can['can_proceed'] else '否'}")
        if not can['can_proceed']:
            print(f"原因：{can['reason']}")

        # 列出紧急事件
        events = list_emergency_events()
        print(f"\n紧急事件记录：{events.get('count', 0)} 条")

        print("\n" + "=" * 70)
        print("停止触发条件:")
        print("=" * 70)
        for stype, info in sorted(STOP_TRIGGERS.items(), key=lambda x: -["critical", "high", "medium", "low"].index(x[1]["severity"])):
            auto = "自动" if info.get("auto_stop") else "手动"
            print(f"  {stype:30s} [{info['severity']:8s}] {auto}")

        return 0

    command = sys.argv[1]

    if command == "trigger" and len(sys.argv) >= 4:
        reason = sys.argv[2]
        session_id = sys.argv[3]
        trigger_type = sys.argv[4] if len(sys.argv) > 4 else "manual_stop"
        result = trigger_stop(reason, session_id, trigger_type)
    elif command == "check":
        result = check_stop_status()
    elif command == "can_proceed":
        result = can_proceed()
    elif command == "resume":
        admin_code = sys.argv[2] if len(sys.argv) > 2 else None
        reason = sys.argv[3] if len(sys.argv) > 3 else None
        result = resume_operation(admin_code, reason)
    elif command == "list":
        result = list_emergency_events()
    elif command == "clear":
        clear_stop_flag()
        result = {"status": "cleared", "message": "停止标志已清除"}
    else:
        print("用法:")
        print("  py emergency_stop.py trigger <reason> <session_id> [trigger_type]")
        print("  py emergency_stop.py check")
        print("  py emergency_stop.py can_proceed")
        print("  py emergency_stop.py resume [admin_code] [reason]")
        print("  py emergency_stop.py list")
        print("  py emergency_stop.py clear")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ["running", "resumed", "success", "clear", "cleared", "skip"] else 1

if __name__ == "__main__":
    sys.exit(main())
