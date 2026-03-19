#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add Automation Triggers Phase 2 - 第 2 批自动化工具

继续为更多工具添加触发器，目标自动化率 10.8%->18%+
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 第 2 批自动化工具配置 (24 个工具)
AUTOMATION_TRIGGERS_PHASE2 = {
    # 内存相关工具 (6 个)
    "session_end": {
        "triggers": [
            {"type": "event", "event": "session_end", "description": "会话结束自动执行"},
            {"type": "cron", "schedule": "0 */2 * * *", "description": "每 2 小时检查"}
        ]
    },
    "pre_session_hook": {
        "triggers": [
            {"type": "event", "event": "session_start", "description": "会话开始自动执行"}
        ]
    },
    "post_session_compress": {
        "triggers": [
            {"type": "event", "event": "session_end", "description": "会话结束自动压缩"},
            {"type": "cron", "schedule": "0 */4 * * *", "description": "每 4 小时压缩"}
        ]
    },
    "memory_checker": {
        "triggers": [
            {"type": "cron", "schedule": "0 6 * * *", "description": "每日 06:00 检查内存"},
            {"type": "event", "event": "memory_low", "description": "内存不足自动检查"}
        ]
    },
    "memory_optimizer": {
        "triggers": [
            {"type": "event", "event": "memory_fragmented", "description": "内存碎片自动优化"}
        ]
    },
    "long_term_memory": {
        "triggers": [
            {"type": "cron", "schedule": "0 5 * * 0", "description": "每周日 05:00 提炼长期记忆"}
        ]
    },
    
    # 批判者相关工具 (6 个)
    "critic_v5": {
        "triggers": [
            {"type": "event", "event": "code_complete", "description": "代码完成自动审查"},
            {"type": "event", "event": "pre_delivery", "description": "交付前自动审查"}
        ]
    },
    "critic_embedded": {
        "triggers": [
            {"type": "event", "event": "workflow_step", "description": "工作流步骤自动审查"}
        ]
    },
    "critic_review": {
        "triggers": [
            {"type": "event", "event": "task_complete", "description": "任务完成自动审查"}
        ]
    },
    "auto_critic_daily": {
        "triggers": [
            {"type": "cron", "schedule": "0 22 * * *", "description": "每日 22:00 审查"}
        ]
    },
    "critic_quality_check": {
        "triggers": [
            {"type": "event", "event": "quality_gate", "description": "质量关卡自动审查"}
        ]
    },
    "critic_workflow": {
        "triggers": [
            {"type": "event", "event": "workflow_complete", "description": "工作流完成自动审查"}
        ]
    },
    
    # 工作流相关工具 (6 个)
    "workflow_manager": {
        "triggers": [
            {"type": "event", "event": "workflow_init", "description": "工作流初始化自动管理"}
        ]
    },
    "workflow_validator": {
        "triggers": [
            {"type": "event", "event": "workflow_create", "description": "工作流创建自动验证"}
        ]
    },
    "workflow_optimizer": {
        "triggers": [
            {"type": "cron", "schedule": "0 3 * * 0", "description": "每周日 03:00 优化工作流"}
        ]
    },
    "flow_monitor": {
        "triggers": [
            {"type": "cron", "schedule": "*/15 * * * *", "description": "每 15 分钟监控工作流"}
        ]
    },
    "step_validator": {
        "triggers": [
            {"type": "event", "event": "step_complete", "description": "步骤完成自动验证"}
        ]
    },
    "completion_checker": {
        "triggers": [
            {"type": "event", "event": "task_assigned", "description": "任务分配自动检查完成"}
        ]
    },
    
    # 工具治理相关 (6 个)
    "tool_quality_scorer": {
        "triggers": [
            {"type": "cron", "schedule": "0 4 * * 0", "description": "每周日 04:00 评分工具"}
        ]
    },
    "tool_usage_tracker": {
        "triggers": [
            {"type": "event", "event": "tool_used", "description": "工具使用自动追踪"}
        ]
    },
    "tool_deprecated_marker": {
        "triggers": [
            {"type": "cron", "schedule": "0 2 * * 0", "description": "每周日 02:00 标记废弃"}
        ]
    },
    "duplicate_detector": {
        "triggers": [
            {"type": "cron", "schedule": "0 1 * * 0", "description": "每周日 01:00 检测重复"}
        ]
    },
    "naming_standard_checker": {
        "triggers": [
            {"type": "event", "event": "tool_create", "description": "工具创建自动检查命名"}
        ]
    },
    "tool_directory_generator": {
        "triggers": [
            {"type": "cron", "schedule": "0 0 * * 0", "description": "每周日 00:00 生成目录"}
        ]
    }
}


def add_automation_triggers_phase2():
    """第 2 批自动化工具触发器"""
    
    print("=" * 70)
    print("Add Automation Triggers - Phase 2")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    updated_count = 0
    skipped_count = 0
    already_automated = 0
    
    for tool_id, config in AUTOMATION_TRIGGERS_PHASE2.items():
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 检查是否已自动化
            if tool.get("automation_enabled"):
                print(f"SKIP {tool_id}: Already automated")
                already_automated += 1
                continue
            
            # 添加触发器
            if "triggers" not in tool:
                tool["triggers"] = []
            
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
    registry["version"] = "1.11.0"
    
    # 统计自动化率
    automated_count = sum(1 for t in tools.values() if t.get("automation_enabled"))
    automation_rate = round(automated_count / len(tools) * 100, 2)
    
    registry["automation_stats"] = {
        "total_tools": len(tools),
        "automated_tools": automated_count,
        "automation_rate": automation_rate,
        "phase2_added": updated_count,
        "updated_at": datetime.now().isoformat()
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\nAutomation Statistics:")
    print(f"  Tools updated: {updated_count}")
    print(f"  Tools skipped: {skipped_count}")
    print(f"  Already automated: {already_automated}")
    print(f"  Total automated: {automated_count}/{len(tools)}")
    print(f"  Automation rate: {automation_rate}%")
    
    # 保存配置
    config_file = Path("flow-archive/20260318-universal-workflow-001/flow-governance-layer4/automation_triggers_phase2.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "tools_configured": list(AUTOMATION_TRIGGERS_PHASE2.keys()),
            "count": updated_count,
            "automation_rate": automation_rate,
            "phase": 2
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nConfig saved to: {config_file}")
    
    return updated_count, automation_rate


if __name__ == '__main__':
    add_automation_triggers_phase2()
