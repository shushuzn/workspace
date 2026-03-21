import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
奖励系统 - 只有完整执行工作流才有奖励
与惩罚系统配对，正向激励
"""
import json
import sys
from pathlib import Path
from datetime import datetime

REWARD_LOG = Path("30-scripts-tools/reward_log.jsonl")
REWARD_STATE = Path("30-scripts-tools/reward_state.json")

# 奖励类型和分数
REWARD_TYPES = {
    "complete_workflow_100": {
        "name": "100% 完成工作流",
        "points": 50,
        "requirements": ["completion_percentage == 100", "workflow_compliance == true"]
    },
    "complete_workflow_80": {
        "name": "80% 完成工作流",
        "points": 30,
        "requirements": ["completion_percentage >= 80"]
    },
    "complete_workflow_50": {
        "name": "50% 完成工作流",
        "points": 15,
        "requirements": ["completion_percentage >= 50"]
    },
    "zero_violations": {
        "name": "零违规会话",
        "points": 20,
        "requirements": ["violations_count == 0"]
    },
    "full_tool_usage": {
        "name": "完整工具使用",
        "points": 25,
        "requirements": ["tool_call_count >= total_steps * 1.5"]
    },
    "proper_backup": {
        "name": "规范备份",
        "points": 10,
        "requirements": ["all_modifications_backed_up == true"]
    },
    "fast_completion": {
        "name": "快速完成",
        "points": 15,
        "requirements": ["completion_time < 30min"]
    },
    "perfect_compliance": {
        "name": "完美合规",
        "points": 100,
        "requirements": ["all_steps_verified == true", "zero_violations == true"]
    },
}

# 奖励等级
REWARD_LEVELS = {
    0: {"level": 0, "name": "新手", "badge": "🥉", "privileges": []},
    100: {"level": 1, "name": "合格", "badge": "🥈", "privileges": ["简化确认流程"]},
    300: {"level": 2, "name": "优秀", "badge": "🥇", "privileges": ["简化确认流程", "优先资源"]},
    500: {"level": 3, "name": "专家", "badge": "💎", "privileges": ["简化确认流程", "优先资源", "批量操作许可"]},
    1000: {"level": 4, "name": "大师", "badge": "👑", "privileges": ["全部特权", "信任模式"]},
}

def award_reward(reward_type: str, session_id: str, details: dict = None) -> dict:
    """授予奖励"""
    
    if reward_type not in REWARD_TYPES:
        return {
            "status": "error",
            "reason": f"未知奖励类型：{reward_type}"
        }
    
    reward_info = REWARD_TYPES[reward_type]
    
    # 记录奖励
    entry = {
        "id": f"R-{datetime.now().strftime('%Y%m%d%H%M%S')}-{session_id[-6:]}",
        "timestamp": datetime.now().isoformat(),
        "reward_type": reward_type,
        "reward_name": reward_info["name"],
        "points": reward_info["points"],
        "session_id": session_id,
        "details": details,
        "requirements": reward_info["requirements"]
    }
    
    # 追加到日志
    with open(REWARD_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # 更新奖励状态
    level_result = update_reward_state(reward_info["points"])
    
    return {
        "status": "awarded",
        "reward": entry,
        "level": level_result,
        "message": f"[奖励] {reward_info['name']} (+{reward_info['points']}分)"
    }

def update_reward_state(new_points: int) -> dict:
    """更新奖励状态"""
    
    # 读取现有状态
    current_points = 0
    if REWARD_STATE.exists():
        with open(REWARD_STATE, "r", encoding="utf-8") as f:
            state = json.load(f)
            current_points = state.get("total_points", 0)
    
    # 累加分数
    total_points = current_points + new_points
    
    # 确定等级
    level = 0
    for threshold in sorted(REWARD_LEVELS.keys(), reverse=True):
        if total_points >= threshold:
            level = REWARD_LEVELS[threshold]["level"]
            break
    
    # 保存状态
    state = {
        "total_points": total_points,
        "previous_points": current_points,
        "points_added": new_points,
        "current_level": level,
        "level_name": REWARD_LEVELS.get(
            min([t for t in REWARD_LEVELS.keys() if total_points >= t] or [0]),
            {"level": 0, "name": "新手"}
        )["name"],
        "badge": REWARD_LEVELS.get(
            min([t for t in REWARD_LEVELS.keys() if total_points >= t] or [0]),
            {"badge": "🥉"}
        )["badge"],
        "privileges": REWARD_LEVELS.get(
            min([t for t in REWARD_LEVELS.keys() if total_points >= t] or [0]),
            {"privileges": []}
        )["privileges"],
        "last_reward": datetime.now().isoformat(),
        "next_level_threshold": min([t for t in REWARD_LEVELS.keys() if t > total_points] or [1000])
    }
    
    with open(REWARD_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    return {
        "total_points": total_points,
        "level": level,
        "level_name": state["level_name"],
        "badge": state["badge"],
        "privileges_count": len(state["privileges"]),
        "next_threshold": state["next_level_threshold"]
    }

def check_reward_status() -> dict:
    """检查奖励状态"""
    
    if not REWARD_STATE.exists():
        return {
            "status": "new",
            "level": 0,
            "message": "新会话，开始积累奖励积分"
        }
    
    with open(REWARD_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    return {
        "status": "active",
        "level": state["current_level"],
        "level_name": state["level_name"],
        "badge": state["badge"],
        "total_points": state["total_points"],
        "privileges": state["privileges"],
        "next_threshold": state.get("next_level_threshold", 100),
        "points_to_next": state.get("next_level_threshold", 100) - state["total_points"]
    }

def verify_workflow_completion(session_id: str) -> dict:
    """验证工作流完成情况 (决定是否给予奖励)"""
    
    state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
    
    if not state_file.exists():
        return {
            "status": "error",
            "reason": "execution-state.json 不存在"
        }
    
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        completion = state.get("completion_percentage", 0)
        compliance = state.get("workflow_compliance", False)
        completed_steps = len(state.get("completed_steps", []))
        total_steps = state.get("total_steps", 20)
        
        # 检查违规
        violation_log = Path("30-scripts-tools/violation_log.jsonl")
        violations = 0
        if violation_log.exists():
            with open(violation_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("session_id") == session_id:
                            violations += 1
                    except Exception:
                        pass
        
        # 判定奖励
        rewards_earned = []
        
        if completion == 100 and compliance:
            rewards_earned.append("complete_workflow_100")
            if violations == 0:
                rewards_earned.append("perfect_compliance")
        elif completion >= 80:
            rewards_earned.append("complete_workflow_80")
        elif completion >= 50:
            rewards_earned.append("complete_workflow_50")
        
        if violations == 0:
            rewards_earned.append("zero_violations")
        
        return {
            "status": "verified",
            "session_id": session_id,
            "completion_percentage": completion,
            "workflow_compliance": compliance,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "violations": violations,
            "rewards_earned": rewards_earned,
            "ready_for_award": len(rewards_earned) > 0
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }

def list_rewards(session_id: str = None, limit: int = 50) -> dict:
    """列出奖励记录"""
    
    if not REWARD_LOG.exists():
        return {"status": "empty", "message": "无奖励记录"}
    
    rewards = []
    with open(REWARD_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if session_id and entry.get("session_id") != session_id:
                    continue
                rewards.append(entry)
            except Exception:
                pass
    
    rewards.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # 统计
    total_points = sum(r.get("points", 0) for r in rewards)
    
    return {
        "status": "success",
        "count": len(rewards),
        "total_points_awarded": total_points,
        "rewards": rewards[:limit]
    }

def reset_rewards():
    """重置奖励状态 (管理员功能)"""
    if REWARD_STATE.exists():
        REWARD_STATE.unlink()

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        # 测试模式
        print("=" * 70)
        print("奖励系统 v1.0")
        print("=" * 70)
        
        # 检查当前状态
        status = check_reward_status()
        print(f"\n当前状态：{status['status']}")
        if status.get('level_name'):
            print(f"奖励等级：{status['badge']} {status['level_name']}")
            print(f"总积分：{status.get('total_points', 0)}")
            if status.get('privileges'):
                print(f"特权：{', '.join(status['privileges'])}")
            if status.get('points_to_next'):
                print(f"距离下一级：{status['points_to_next']}分")
        
        # 列出奖励
        rewards = list_rewards()
        print(f"\n奖励记录：{rewards.get('count', 0)} 条")
        print(f"总授予积分：{rewards.get('total_points_awarded', 0)}")
        
        print("\n" + "=" * 70)
        print("奖励类型列表:")
        print("=" * 70)
        for rtype, info in sorted(REWARD_TYPES.items(), key=lambda x: -x[1]["points"]):
            print(f"  {rtype:30s} +{info['points']:3d}分 - {info['name']}")
        
        return 0
    
    command = sys.argv[1]
    
    if command == "award" and len(sys.argv) >= 4:
        reward_type = sys.argv[2]
        session_id = sys.argv[3]
        result = award_reward(reward_type, session_id)
    elif command == "check":
        result = check_reward_status()
    elif command == "verify" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        result = verify_workflow_completion(session_id)
    elif command == "list":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = list_rewards(session_id)
    elif command == "reset":
        reset_rewards()
        result = {"status": "reset", "message": "奖励状态已重置"}
    else:
        print("用法:")
        print("  py reward_system.py award <reward_type> <session_id>")
        print("  py reward_system.py check")
        print("  py reward_system.py verify <session_id>")
        print("  py reward_system.py list [session_id]")
        print("  py reward_system.py reset")
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ["awarded", "verified", "success", "reset", "new", "active"] else 1

if __name__ == "__main__":
    sys.exit(main())
