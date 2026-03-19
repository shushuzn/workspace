#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add Automation Triggers - 添加工具自动化触发器

为工具添加 cron 和事件触发器，提升自动化率从 6.4% 到 25%+
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 自动化工具配置 (20 个工具)
AUTOMATION_TRIGGERS = {
    # Cron 触发器 (10 个)
    "context_loader": {
        "triggers": [
            {"type": "cron", "schedule": "0 * * * *", "description": "每小时加载上下文"},
            {"type": "event", "event": "session_start", "description": "会话开始自动加载"}
        ]
    },
    "session_compress": {
        "triggers": [
            {"type": "cron", "schedule": "*/30 * * * *", "description": "每 30 分钟压缩会话"},
            {"type": "event", "event": "session_end", "description": "会话结束自动压缩"}
        ]
    },
    "memory_distill": {
        "triggers": [
            {"type": "cron", "schedule": "0 6 * * *", "description": "每日 06:00 提炼记忆"}
        ]
    },
    "arxiv_collector": {
        "triggers": [
            {"type": "cron", "schedule": "0 7 * * *", "description": "每日 07:00 收集 arXiv"}
        ]
    },
    "critic_daily_note": {
        "triggers": [
            {"type": "cron", "schedule": "0 23 * * *", "description": "每日 23:00 审查笔记"}
        ]
    },
    "workflow_enforcer": {
        "triggers": [
            {"type": "event", "event": "workflow_start", "description": "工作流开始自动检查"},
            {"type": "event", "event": "step_complete", "description": "步骤完成自动验证"}
        ]
    },
    "tool_executor": {
        "triggers": [
            {"type": "event", "event": "task_assigned", "description": "任务分配自动执行"}
        ]
    },
    "auto_critic_v7": {
        "triggers": [
            {"type": "event", "event": "code_written", "description": "代码完成自动审查"},
            {"type": "event", "event": "pre_commit", "description": "提交前自动审查"}
        ]
    },
    "context_verify": {
        "triggers": [
            {"type": "event", "event": "session_start", "description": "会话开始验证上下文"}
        ]
    },
    "git_workflow": {
        "triggers": [
            {"type": "event", "event": "task_complete", "description": "任务完成自动提交"}
        ]
    },
    
    # 事件触发器 (10 个)
    "register_core_tools": {
        "triggers": [
            {"type": "event", "event": "tool_missing", "description": "工具缺失自动注册"}
        ]
    },
    "check_core_tools": {
        "triggers": [
            {"type": "cron", "schedule": "0 */2 * * *", "description": "每 2 小时检查核心工具"}
        ]
    },
    "check_flow_manager": {
        "triggers": [
            {"type": "event", "event": "workflow_start", "description": "工作流开始检查管理器"}
        ]
    },
    "auto_execute_workflow": {
        "triggers": [
            {"type": "event", "event": "workflow_approved", "description": "工作流批准自动执行"}
        ]
    },
    "critical_issue_detector": {
        "triggers": [
            {"type": "event", "event": "error_occurred", "description": "错误发生自动检测"},
            {"type": "cron", "schedule": "0 */4 * * *", "description": "每 4 小时检测问题"}
        ]
    },
    "critical_checks": {
        "triggers": [
            {"type": "event", "event": "pre_delivery", "description": "交付前自动检查"}
        ]
    },
    "analyze_memory_scripts": {
        "triggers": [
            {"type": "cron", "schedule": "0 5 * * 0", "description": "每周日 05:00 分析脚本"}
        ]
    },
    "analyze_memory_tools": {
        "triggers": [
            {"type": "cron", "schedule": "0 5 * * 0", "description": "每周日 05:00 分析工具"}
        ]
    },
    "memory_fix_tools": {
        "triggers": [
            {"type": "event", "event": "memory_corruption", "description": "内存损坏自动修复"}
        ]
    },
    "proactive_agent": {
        "triggers": [
            {"type": "cron", "schedule": "0 */2 * * *", "description": "每 2 小时主动检查"},
            {"type": "event", "event": "user_idle", "description": "用户空闲主动询问"}
        ]
    }
}


def add_automation_triggers():
    """为工具添加自动化触发器"""
    
    print("=" * 70)
    print("Add Automation Triggers - Layer 4")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    updated_count = 0
    skipped_count = 0
    
    for tool_id, config in AUTOMATION_TRIGGERS.items():
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 添加触发器
            if "triggers" not in tool:
                tool["triggers"] = []
            
            # 合并触发器 (避免重复)
            existing_triggers = [json.dumps(t, sort_keys=True) for t in tool["triggers"]]
            
            for new_trigger in config["triggers"]:
                new_trigger_str = json.dumps(new_trigger, sort_keys=True)
                if new_trigger_str not in existing_triggers:
                    tool["triggers"].append(new_trigger)
                    existing_triggers.append(new_trigger_str)
            
            # 标记为自动化工具
            tool["automation_enabled"] = True
            tool["automation_updated_at"] = datetime.now().isoformat()
            
            print(f"OK {tool_id}: Added {len(config['triggers'])} triggers")
            updated_count += 1
        else:
            print(f"WARNING {tool_id}: Tool not found")
            skipped_count += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["updated_at"] = datetime.now().isoformat()
    registry["version"] = "1.10.0"
    registry["automation_stats"] = {
        "total_tools": len(tools),
        "automated_tools": sum(1 for t in tools.values() if t.get("automation_enabled")),
        "automation_rate": round(sum(1 for t in tools.values() if t.get("automation_enabled")) / len(tools) * 100, 2),
        "updated_at": datetime.now().isoformat()
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 统计自动化率
    automated_count = sum(1 for t in tools.values() if t.get("automation_enabled"))
    automation_rate = round(automated_count / len(tools) * 100, 2)
    
    print(f"\nAutomation Statistics:")
    print(f"  Tools updated: {updated_count}")
    print(f"  Tools skipped: {skipped_count}")
    print(f"  Total automated: {automated_count}/{len(tools)}")
    print(f"  Automation rate: {automation_rate}%")
    
    # 保存配置
    config_file = Path("flow-archive/20260318-universal-workflow-001/flow-governance-layer4/automation_triggers_config.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "tools_configured": list(AUTOMATION_TRIGGERS.keys()),
            "count": updated_count,
            "automation_rate": automation_rate
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nConfig saved to: {config_file}")
    
    return updated_count, automation_rate


if __name__ == '__main__':
    add_automation_triggers()
