#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
违规惩罚机制 v2.0 - 强化版
更严厉、更快速、更透明
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
PENALTY_STATE = Path("30-scripts-tools/penalty_state.json")
LOCKDOWN_FILE = Path("30-scripts-tools/.lockdown_active")

# 强化版违规类型和惩罚
VIOLATION_TYPES = {
    # Critical 级别 (立即封锁)
    "fabricate_result": {
        "name": "编造结果",
        "severity": "critical",
        "penalty_points": 50,  # 直接封锁
        "cooldown_hours": 168,  # 7 天
        "auto_lockdown": True,
        "notify_admin": True
    },
    "bypass_entry_point": {
        "name": "绕过入口点",
        "severity": "critical",
        "penalty_points": 50,
        "cooldown_hours": 168,
        "auto_lockdown": True,
        "notify_admin": True
    },
    "tamper_with_logs": {
        "name": "篡改日志",
        "severity": "critical",
        "penalty_points": 50,
        "cooldown_hours": 168,
        "auto_lockdown": True,
        "notify_admin": True
    },

    # High 级别
    "skip_workflow_step": {
        "name": "跳过工作流步骤",
        "severity": "high",
        "penalty_points": 20,  # 提升到 20
        "cooldown_hours": 48,  # 延长到 48h
        "auto_lockdown": False,
        "notify_admin": True
    },
    "skip_tool_call": {
        "name": "跳过工具调用",
        "severity": "high",
        "penalty_points": 20,
        "cooldown_hours": 48,
        "auto_lockdown": False,
        "notify_admin": True
    },
    "skip_risk_assessment": {
        "name": "跳过风险评估",
        "severity": "high",
        "penalty_points": 20,
        "cooldown_hours": 48,
        "auto_lockdown": False,
        "notify_admin": True
    },
    "missing_confirmation": {
        "name": "高风险操作未确认",
        "severity": "high",
        "penalty_points": 20,
        "cooldown_hours": 48,
        "auto_lockdown": False,
        "notify_admin": True
    },
    "force_execution": {
        "name": "强制执行被阻断的操作",
        "severity": "high",
        "penalty_points": 30,
        "cooldown_hours": 72,
        "auto_lockdown": False,
        "notify_admin": True
    },

    # Medium 级别
    "batch_execution": {
        "name": "批量执行",
        "severity": "medium",
        "penalty_points": 10,  # 提升到 10
        "cooldown_hours": 24,
        "auto_lockdown": False,
        "notify_admin": False
    },
    "missing_backup": {
        "name": "未备份就修改",
        "severity": "medium",
        "penalty_points": 10,
        "cooldown_hours": 24,
        "auto_lockdown": False,
        "notify_admin": False
    },
    "incomplete_workflow": {
        "name": "工作流未完成",
        "severity": "medium",
        "penalty_points": 10,
        "cooldown_hours": 24,
        "auto_lockdown": False,
        "notify_admin": False
    },

    # Low 级别
    "invalid_tool_call": {
        "name": "无效工具调用",
        "severity": "low",
        "penalty_points": 5,  # 提升到 5
        "cooldown_hours": 6,
        "auto_lockdown": False,
        "notify_admin": False
    },
    "missing_documentation": {
        "name": "缺少文档记录",
        "severity": "low",
        "penalty_points": 5,
        "cooldown_hours": 6,
        "auto_lockdown": False,
        "notify_admin": False
    },
}

# 强化版惩罚等级
PENALTY_LEVELS = {
    0: {
        "level": 0,
        "name": "正常",
        "color": "GREEN",
        "restrictions": [],
        "description": "无限制"
    },
    10: {
        "level": 1,
        "name": "警告",
        "color": "YELLOW",
        "restrictions": [
            "所有操作需要额外确认",
            "禁止跳过任何步骤"
        ],
        "description": "需要额外确认"
    },
    20: {
        "level": 2,
        "name": "限制",
        "color": "ORANGE",
        "restrictions": [
            "禁止高风险操作",
            "需要人工审核",
            "单步执行模式",
            "强制备份所有修改"
        ],
        "description": "功能受限"
    },
    30: {
        "level": 3,
        "name": "严重",
        "color": "RED",
        "restrictions": [
            "只读模式",
            "禁止修改任何文件",
            "禁止 Git 提交",
            "仅允许查询操作"
        ],
        "description": "只读模式"
    },
    50: {
        "level": 4,
        "name": "封锁",
        "color": "BLACK",
        "restrictions": [
            "完全禁止操作",
            "需要管理员解锁",
            "记录到永久档案",
            "通知所有管理员"
        ],
        "description": "系统封锁"
    },
}

def record_violation(violation_type: str, session_id: str, details: str = None, auto_triggered: bool = False) -> dict:
    """记录违规 (强化版)"""

    if violation_type not in VIOLATION_TYPES:
        return {
            "status": "error",
            "reason": f"未知违规类型：{violation_type}"
        }

    violation_info = VIOLATION_TYPES[violation_type]

    # 记录违规
    entry = {
        "id": f"V-{datetime.now().strftime('%Y%m%d%H%M%S')}-{session_id[-6:]}",
        "timestamp": datetime.now().isoformat(),
        "violation_type": violation_type,
        "violation_name": violation_info["name"],
        "severity": violation_info["severity"],
        "penalty_points": violation_info["penalty_points"],
        "session_id": session_id,
        "details": details,
        "auto_triggered": auto_triggered,
        "lockdown_triggered": violation_info.get("auto_lockdown", False)
    }

    # 追加到日志
    with open(VIOLATION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 更新惩罚状态
    penalty_result = update_penalty_state(violation_info)

    # 如果需要自动封锁
    if violation_info.get("auto_lockdown", False):
        activate_lockdown(session_id, violation_type, entry["id"])

    # 如果需要通知管理员
    if violation_info.get("notify_admin", False):
        log_admin_notification(entry)

    return {
        "status": "recorded",
        "violation": entry,
        "penalty": penalty_result,
        "message": f"[{violation_info['severity'].upper()}] {violation_info['name']} (+{violation_info['penalty_points']}分)",
        "lockdown": "ACTIVE" if violation_info.get("auto_lockdown", False) else None
    }

def update_penalty_state(violation_info: dict) -> dict:
    """更新惩罚状态 (强化版)"""

    # 读取现有状态
    current_points = 0
    consecutive_violations = 0
    if PENALTY_STATE.exists():
        with open(PENALTY_STATE, "r", encoding="utf-8") as f:
            state = json.load(f)
            current_points = state.get("total_points", 0)
            consecutive_violations = state.get("consecutive_violations", 0)

    # 累加分数
    new_points = violation_info["penalty_points"]
    total_points = current_points + new_points

    # 连续违规加倍惩罚
    consecutive_violations += 1
    if consecutive_violations >= 3:
        total_points += new_points  # 第 3 次违规加倍
        message = f"连续违规第{consecutive_violations}次，惩罚加倍!"
    else:
        message = "违规已记录"

    # 确定惩罚等级
    level = 0
    for threshold in sorted(PENALTY_LEVELS.keys(), reverse=True):
        if total_points >= threshold:
            level = PENALTY_LEVELS[threshold]["level"]
            break

    # 计算解封时间
    cooldown_hours = violation_info["cooldown_hours"]
    if consecutive_violations >= 3:
        cooldown_hours *= 2  # 连续违规冷却时间加倍

    unlock_time = datetime.now() + timedelta(hours=cooldown_hours)

    # 保存状态
    state = {
        "total_points": total_points,
        "previous_points": current_points,
        "points_added": new_points,
        "current_level": level,
        "level_name": PENALTY_LEVELS.get(
            min([t for t in PENALTY_LEVELS.keys() if total_points >= t] or [0]),
            {"level": 0, "name": "正常"}
        )["name"],
        "level_color": PENALTY_LEVELS.get(
            min([t for t in PENALTY_LEVELS.keys() if total_points >= t] or [0]),
            {"color": "GREEN"}
        )["color"],
        "restrictions": PENALTY_LEVELS.get(
            min([t for t in PENALTY_LEVELS.keys() if total_points >= t] or [0]),
            {"restrictions": []}
        )["restrictions"],
        "consecutive_violations": consecutive_violations,
        "last_violation": datetime.now().isoformat(),
        "last_violation_type": violation_info["name"],
        "unlock_time": unlock_time.isoformat(),
        "cooldown_hours": cooldown_hours,
        "message": message
    }

    with open(PENALTY_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    return {
        "total_points": total_points,
        "level": level,
        "level_name": state["level_name"],
        "restrictions_count": len(state["restrictions"]),
        "unlock_hours": cooldown_hours
    }

def activate_lockdown(session_id: str, violation_type: str, violation_id: str):
    """激活封锁状态"""

    lockdown_data = {
        "activated_at": datetime.now().isoformat(),
        "session_id": session_id,
        "violation_type": violation_type,
        "violation_id": violation_id,
        "status": "active",
        "reason": "触发自动封锁机制"
    }

    with open(LOCKDOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(lockdown_data, f, ensure_ascii=False, indent=2)

def check_lockdown_status() -> dict:
    """检查封锁状态"""

    if not LOCKDOWN_FILE.exists():
        return {"status": "none", "active": False}

    try:
        with open(LOCKDOWN_FILE, "r", encoding="utf-8") as f:
            lockdown_data = json.load(f)

        return {
            "status": "active",
            "active": True,
            "activated_at": lockdown_data["activated_at"],
            "violation_id": lockdown_data["violation_id"],
            "reason": lockdown_data["reason"]
        }
    except Exception:
        return {"status": "error", "active": False}

def deactivate_lockdown(admin_code: str = None) -> dict:
    """解除封锁 (需要管理员权限)"""

    if not LOCKDOWN_FILE.exists():
        return {"status": "skip", "message": "无活跃封锁"}

    # 简化：实际应该验证管理员权限
    if admin_code is None:
        return {
            "status": "error",
            "message": "需要管理员授权码"
        }

    try:
        LOCKDOWN_FILE.unlink()

        # 重置惩罚状态
        if PENALTY_STATE.exists():
            PENALTY_STATE.unlink()

        return {"status": "deactivated", "message": "封锁已解除"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

def check_penalty_status() -> dict:
    """检查惩罚状态 (强化版)"""

    # 先检查封锁
    lockdown = check_lockdown_status()
    if lockdown["active"]:
        return {
            "status": "lockdown",
            "level": 4,
            "level_name": "封锁",
            "message": "系统已被封锁",
            "details": lockdown
        }

    if not PENALTY_STATE.exists():
        return {
            "status": "clean",
            "level": 0,
            "message": "无违规记录"
        }

    with open(PENALTY_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)

    # 检查是否已解封
    unlock_time = datetime.fromisoformat(state["unlock_time"])
    if datetime.now() > unlock_time:
        reset_state()
        return {
            "status": "reset",
            "message": "惩罚已解除"
        }

    return {
        "status": "penalized",
        "level": state["current_level"],
        "level_name": state["level_name"],
        "level_color": state.get("level_color", "GREEN"),
        "total_points": state["total_points"],
        "restrictions": state["restrictions"],
        "restrictions_count": len(state["restrictions"]),
        "unlock_time": state["unlock_time"],
        "hours_remaining": (unlock_time - datetime.now()).total_seconds() / 3600,
        "consecutive_violations": state.get("consecutive_violations", 0),
        "message": state.get("message", "")
    }

def reset_state():
    """重置惩罚状态"""
    if PENALTY_STATE.exists():
        PENALTY_STATE.unlink()
    if LOCKDOWN_FILE.exists():
        LOCKDOWN_FILE.unlink()

def log_admin_notification(violation_entry: dict):
    """记录管理员通知"""

    notification = {
        "type": "admin_notification",
        "timestamp": datetime.now().isoformat(),
        "violation": violation_entry,
        "urgency": "high" if violation_entry["severity"] in ["critical", "high"] else "medium",
        "status": "pending"
    }

    admin_log = Path("30-scripts-tools/admin_notifications.jsonl")
    with open(admin_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(notification, ensure_ascii=False) + "\n")

def list_violations(session_id: str = None, limit: int = 50) -> dict:
    """列出违规记录 (强化版)"""

    if not VIOLATION_LOG.exists():
        return {"status": "empty", "message": "无违规记录"}

    violations = []
    with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if session_id and entry.get("session_id") != session_id:
                    continue
                violations.append(entry)
            except Exception:
                pass

    violations.sort(key=lambda x: x["timestamp"], reverse=True)

    # 统计
    severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in violations:
        sev = v.get("severity", "low")
        severity_count[sev] = severity_count.get(sev, 0) + 1

    return {
        "status": "success",
        "count": len(violations),
        "severity_breakdown": severity_count,
        "violations": violations[:limit]
    }

def main():
    if len(sys.argv) < 2:
        # 测试模式
        print("=" * 70)
        print("违规惩罚机制 v2.0 (强化版)")
        print("=" * 70)

        # 检查当前状态
        status = check_penalty_status()
        print(f"\n当前状态：{status['status']}")
        if status.get('level_name'):
            color = status.get('level_color', 'GREEN')
            print(f"惩罚等级：[{color}] {status['level_name']}")
            print(f"总分数：{status.get('total_points', 0)}")
            if status.get('restrictions_count', 0) > 0:
                print(f"限制措施：{status['restrictions_count']} 项")
            if status.get('hours_remaining'):
                print(f"剩余时间：{status['hours_remaining']:.1f}小时")

        # 列出违规
        violations = list_violations()
        print(f"\n违规记录：{violations['count']} 条")
        if violations.get('severity_breakdown'):
            print(f"  Critical: {violations['severity_breakdown'].get('critical', 0)}")
            print(f"  High: {violations['severity_breakdown'].get('high', 0)}")
            print(f"  Medium: {violations['severity_breakdown'].get('medium', 0)}")
            print(f"  Low: {violations['severity_breakdown'].get('low', 0)}")

        print("\n" + "=" * 70)
        print("违规类型列表:")
        print("=" * 70)
        for vtype, info in sorted(VIOLATION_TYPES.items(), key=lambda x: -x[1]["penalty_points"]):
            lockdown_flag = " [LOCKDOWN]" if info.get("auto_lockdown") else ""
            notify_flag = " [NOTIFY]" if info.get("notify_admin") else ""
            print(f"  {vtype:30s} +{info['penalty_points']:2d}分 {info['severity']:8s}{lockdown_flag}{notify_flag}")

        return 0

    command = sys.argv[1]

    if command == "record" and len(sys.argv) >= 4:
        violation_type = sys.argv[2]
        session_id = sys.argv[3]
        details = sys.argv[4] if len(sys.argv) > 4 else None
        result = record_violation(violation_type, session_id, details)
    elif command == "check":
        result = check_penalty_status()
    elif command == "list":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = list_violations(session_id)
    elif command == "reset":
        admin_code = sys.argv[2] if len(sys.argv) > 2 else None
        result = deactivate_lockdown(admin_code)
    elif command == "unlock":
        admin_code = sys.argv[2] if len(sys.argv) > 2 else None
        result = deactivate_lockdown(admin_code)
    else:
        print("用法:")
        print("  py penalty_system_v2.py record <violation_type> <session_id> [details]")
        print("  py penalty_system_v2.py check")
        print("  py penalty_system_v2.py list [session_id]")
        print("  py penalty_system_v2.py reset [admin_code]")
        print("  py penalty_system_v2.py unlock [admin_code]")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ["clean", "success", "recorded", "reset", "deactivated"] else 1

if __name__ == "__main__":
    sys.exit(main())
