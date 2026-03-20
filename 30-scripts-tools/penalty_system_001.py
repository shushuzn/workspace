#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
违规惩罚机制 - 对违反工作流和规定的行为进行惩罚
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
PENALTY_STATE = Path("30-scripts-tools/penalty_state.json")

# 违规类型和惩罚
VIOLATION_TYPES = {
    "skip_workflow_step": {
        "name": "跳过工作流步骤",
        "severity": "high",
        "penalty_points": 10,
        "cooldown_hours": 24
    },
    "fabricate_result": {
        "name": "编造结果",
        "severity": "critical",
        "penalty_points": 20,
        "cooldown_hours": 48
    },
    "skip_tool_call": {
        "name": "跳过工具调用",
        "severity": "high",
        "penalty_points": 10,
        "cooldown_hours": 12
    },
    "batch_execution": {
        "name": "批量执行",
        "severity": "medium",
        "penalty_points": 5,
        "cooldown_hours": 6
    },
    "missing_backup": {
        "name": "未备份就修改",
        "severity": "medium",
        "penalty_points": 5,
        "cooldown_hours": 6
    },
    "skip_risk_assessment": {
        "name": "跳过风险评估",
        "severity": "high",
        "penalty_points": 10,
        "cooldown_hours": 12
    },
    "missing_confirmation": {
        "name": "高风险操作未确认",
        "severity": "high",
        "penalty_points": 10,
        "cooldown_hours": 12
    },
    "invalid_tool_call": {
        "name": "无效工具调用",
        "severity": "low",
        "penalty_points": 2,
        "cooldown_hours": 1
    },
}

# 惩罚等级
PENALTY_LEVELS = {
    0: {"level": 0, "name": "正常", "restrictions": []},
    10: {"level": 1, "name": "警告", "restrictions": ["需要额外确认"]},
    20: {"level": 2, "name": "限制", "restrictions": ["禁止高风险操作", "需要人工审核"]},
    30: {"level": 3, "name": "严重", "restrictions": ["只读模式", "禁止修改"]},
    50: {"level": 4, "name": "封锁", "restrictions": ["完全禁止操作", "需要管理员解锁"]},
}

def record_violation(violation_type: str, session_id: str, details: str = None) -> dict:
    """记录违规"""
    
    if violation_type not in VIOLATION_TYPES:
        return {
            "status": "error",
            "reason": f"未知违规类型：{violation_type}"
        }
    
    violation_info = VIOLATION_TYPES[violation_type]
    
    # 记录违规
    entry = {
        "timestamp": datetime.now().isoformat(),
        "violation_type": violation_type,
        "violation_name": violation_info["name"],
        "severity": violation_info["severity"],
        "penalty_points": violation_info["penalty_points"],
        "session_id": session_id,
        "details": details
    }
    
    # 追加到日志
    with open(VIOLATION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # 更新惩罚状态
    update_penalty_state(violation_info["penalty_points"])
    
    return {
        "status": "recorded",
        "violation": entry,
        "message": f"违规已记录：{violation_info['name']} (+{violation_info['penalty_points']}分)"
    }

def update_penalty_state(new_points: int):
    """更新惩罚状态"""
    
    # 读取现有状态
    current_points = 0
    if PENALTY_STATE.exists():
        with open(PENALTY_STATE, "r", encoding="utf-8") as f:
            state = json.load(f)
            current_points = state.get("total_points", 0)
    
    # 累加分数
    total_points = current_points + new_points
    
    # 确定惩罚等级
    level = 0
    for threshold in sorted(PENALTY_LEVELS.keys(), reverse=True):
        if total_points >= threshold:
            level = PENALTY_LEVELS[threshold]["level"]
            break
    
    # 计算解封时间
    cooldown_hours = max(
        v["cooldown_hours"] 
        for v in VIOLATION_TYPES.values()
    )
    unlock_time = datetime.now() + timedelta(hours=cooldown_hours)
    
    # 保存状态
    state = {
        "total_points": total_points,
        "current_level": level,
        "level_name": PENALTY_LEVELS.get(
            min([t for t in PENALTY_LEVELS.keys() if total_points >= t] or [0]),
            {"level": 0, "name": "正常"}
        )["name"],
        "restrictions": PENALTY_LEVELS.get(
            min([t for t in PENALTY_LEVELS.keys() if total_points >= t] or [0]),
            {"restrictions": []}
        )["restrictions"],
        "last_violation": datetime.now().isoformat(),
        "unlock_time": unlock_time.isoformat()
    }
    
    with open(PENALTY_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_penalty_status() -> dict:
    """检查惩罚状态"""
    
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
        # 重置状态
        reset_state()
        return {
            "status": "reset",
            "message": "惩罚已解除"
        }
    
    return {
        "status": "penalized",
        "level": state["current_level"],
        "level_name": state["level_name"],
        "total_points": state["total_points"],
        "restrictions": state["restrictions"],
        "unlock_time": state["unlock_time"]
    }

def reset_state():
    """重置惩罚状态"""
    if PENALTY_STATE.exists():
        PENALTY_STATE.unlink()

def list_violations(session_id: str = None, limit: int = 20) -> dict:
    """列出违规记录"""
    
    if not VIOLATION_LOG.exists():
        return {
            "status": "empty",
            "message": "无违规记录"
        }
    
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
    
    return {
        "status": "success",
        "count": len(violations),
        "violations": violations[:limit]
    }

def main():
    import sys
    
    if len(sys.argv) < 2:
        # 测试模式
        print("违规惩罚机制测试")
        print("=" * 60)
        
        # 检查当前状态
        status = check_penalty_status()
        print(f"\n当前状态：{status['status']}")
        if status.get('level_name'):
            print(f"惩罚等级：{status['level_name']}")
            print(f"总分数：{status.get('total_points', 0)}")
        
        # 列出违规
        violations = list_violations()
        print(f"\n违规记录：{violations.get('count', 0)} 条")
        for v in violations.get("violations", [])[:5]:
            print(f"  - {v['violation_name']} (+{v['penalty_points']}分) @ {v['timestamp']}")
        
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
        reset_state()
        result = {"status": "reset", "message": "惩罚状态已重置"}
    else:
        print("用法:")
        print("  py penalty_system.py record <violation_type> <session_id> [details]")
        print("  py penalty_system.py check")
        print("  py penalty_system.py list [session_id]")
        print("  py penalty_system.py reset")
        print("\n违规类型:")
        for vtype, info in VIOLATION_TYPES.items():
            print(f"  {vtype}: {info['name']} (+{info['penalty_points']}分)")
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ["clean", "success", "recorded", "reset"] else 1

if __name__ == "__main__":
    sys.exit(main())
