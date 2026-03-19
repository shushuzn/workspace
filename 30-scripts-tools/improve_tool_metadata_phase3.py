#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improve Tool Metadata Phase 3 - 完善工具元数据第 3 批

改进剩余 24 个低分工具中的 12 个
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 第 3 批改进工具 (12 个)
IMPROVEMENTS_PHASE3 = {
    "workflow_interactive": {
        "description": "交互式工作流工具 - 提供交互式工作流执行界面，支持用户输入、实时反馈和进度可视化，适合复杂工作流",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "interactive_mode", "type": "boolean", "required": False, "description": "是否交互模式"},
            {"name": "show_progress", "type": "boolean", "required": False, "description": "是否显示进度条"}
        ],
        "examples": [
            "py workflow_interactive.py --flow_id \"20260318-universal-workflow-001\" --interactive_mode true",
            "py workflow_interactive.py --flow_id \"xxx\" --show_progress true"
        ]
    },
    "register_core_tools": {
        "description": "核心工具注册工具 - 批量注册核心工具到工具库，包括工作流/内存/批判者类基础设施工具，确保系统正常运行",
        "parameters": [
            {"name": "tool_list", "type": "list", "required": True, "description": "工具列表"},
            {"name": "category", "type": "string", "required": False, "description": "工具类别"},
            {"name": "force", "type": "boolean", "required": False, "description": "是否强制覆盖已存在工具"}
        ],
        "examples": [
            "py register_core_tools.py --tool_list \"[\"workflow-enforcer\", \"memory-checker\"]\" --category \"workflow\"",
            "py register_core_tools.py --tool_list \"[...]\" --force true"
        ]
    },
    "check_core_tools": {
        "description": "核心工具检查工具 - 验证核心工具是否已注册且文件存在，确保工作流和系统功能正常运行，提供详细健康报告",
        "parameters": [
            {"name": "tool_ids", "type": "list", "required": False, "description": "要检查的工具 ID 列表"},
            {"name": "check_file", "type": "boolean", "required": False, "description": "是否检查文件存在"},
            {"name": "output_format", "type": "string", "required": False, "description": "输出格式：json/md/text"}
        ],
        "examples": [
            "py check_core_tools.py",
            "py check_core_tools.py --tool_ids \"[\"workflow-enforcer\"]\" --check_file true --output_format md"
        ]
    },
    "check_flow_manager": {
        "description": "工作流管理器检查工具 - 检查工作流管理器状态，包括配置文件、执行进度、历史记录，提供健康度评分",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "check_type", "type": "string", "required": False, "description": "检查类型：config/progress/history/all"},
            {"name": "verbose", "type": "boolean", "required": False, "description": "是否输出详细信息"}
        ],
        "examples": [
            "py check_flow_manager.py --flow_id \"20260318-universal-workflow-001\" --check_type all",
            "py check_flow_manager.py --flow_id \"xxx\" --check_type progress --verbose true"
        ]
    },
    "context_verify": {
        "description": "上下文验证工具 - 验证加载的上下文是否完整正确，包括 7 个核心文件检查、大小验证、编码检测，确保会话正常启动",
        "parameters": [
            {"name": "strict_mode", "type": "boolean", "required": False, "description": "严格模式：是/否"},
            {"name": "output_detail", "type": "boolean", "required": False, "description": "是否输出详情"},
            {"name": "fix_issues", "type": "boolean", "required": False, "description": "是否自动修复问题"}
        ],
        "examples": [
            "py context_verify.py",
            "py context_verify.py --strict_mode true --output_detail true --fix_issues true"
        ]
    },
    "auto_execute_workflow": {
        "description": "自动执行工作流工具 - 根据工作流配置自动执行各个步骤，支持进度跟踪、错误处理、断点续传，适合批量任务",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "start_step", "type": "int", "required": False, "description": "起始步骤编号"},
            {"name": "dry_run", "type": "boolean", "required": False, "description": "是否仅模拟执行"},
            {"name": "auto_retry", "type": "boolean", "required": False, "description": "是否自动重试失败步骤"}
        ],
        "examples": [
            "py auto_execute_workflow.py --flow_id \"20260318-universal-workflow-001\"",
            "py auto_execute_workflow.py --flow_id \"xxx\" --start_step 5 --dry_run true --auto_retry true"
        ]
    },
    "critical-issue-detector": {
        "description": "关键问题检测工具 - 自动检测工作流执行中的关键问题和风险，提前预警，包括资源不足、配置错误、依赖缺失等",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "sensitivity", "type": "string", "required": False, "description": "敏感度：high/medium/low"},
            {"name": "auto_fix", "type": "boolean", "required": False, "description": "是否自动修复可修复问题"}
        ],
        "examples": [
            "py critical_issue_detector.py --flow_id \"20260318-universal-workflow-001\" --sensitivity medium",
            "py critical_issue_detector.py --flow_id \"xxx\" --sensitivity high --auto_fix true"
        ]
    },
    "critical-checks": {
        "description": "关键检查工具 - 执行关键质量检查，包括代码质量、文档完整性、测试覆盖率、性能基准，确保交付物符合标准",
        "parameters": [
            {"name": "check_items", "type": "list", "required": True, "description": "检查项列表"},
            {"name": "threshold", "type": "float", "required": False, "description": "通过阈值 (0-1)"},
            {"name": "output_report", "type": "boolean", "required": False, "description": "是否生成详细报告"}
        ],
        "examples": [
            "py critical_checks.py --check_items \"[\"code_quality\", \"documentation\"]\" --threshold 0.8",
            "py critical_checks.py --check_items \"[...]\" --threshold 0.9 --output_report true"
        ]
    },
    "analyze_memory_scripts": {
        "description": "内存脚本分析工具 - 分析内存相关脚本的使用情况和性能，识别瓶颈和优化机会，提供详细分析报告和改进建议",
        "parameters": [
            {"name": "script_dir", "type": "string", "required": True, "description": "脚本目录"},
            {"name": "include_usage", "type": "boolean", "required": False, "description": "是否包含使用统计"},
            {"name": "time_range", "type": "string", "required": False, "description": "时间范围：day/week/month"}
        ],
        "examples": [
            "py analyze_memory_scripts.py --script_dir \"30-scripts-tools\"",
            "py analyze_memory_scripts.py --script_dir \"xxx\" --include_usage true --time_range week"
        ]
    },
    "analyze_memory_tools": {
        "description": "内存工具分析工具 - 分析内存相关工具的效果和使用频率，识别改进机会和废弃候选，提供数据驱动的优化建议",
        "parameters": [
            {"name": "time_range", "type": "string", "required": False, "description": "时间范围：day/week/month"},
            {"name": "output_format", "type": "string", "required": False, "description": "输出格式：json/md/html"},
            {"name": "include_recommendations", "type": "boolean", "required": False, "description": "是否包含改进建议"}
        ],
        "examples": [
            "py analyze_memory_tools.py --time_range week",
            "py analyze_memory_tools.py --time_range month --output_format md --include_recommendations true"
        ]
    },
    "critic_daily_note_pollution": {
        "description": "批判者每日笔记污染检测工具 - 检测每日笔记中的冗余和污染内容，包括重复信息、过期总结、无效记录，保持笔记简洁",
        "parameters": [
            {"name": "date", "type": "string", "required": False, "description": "日期 (YYYY-MM-DD)"},
            {"name": "auto_clean", "type": "boolean", "required": False, "description": "是否自动清理"},
            {"name": "backup_first", "type": "boolean", "required": False, "description": "清理前是否备份"}
        ],
        "examples": [
            "py critic_daily_note_pollution.py --date \"2026-03-20\"",
            "py critic_daily_note_pollution.py --auto_clean true --backup_first true"
        ]
    },
    "memory_fix_tools": {
        "description": "内存修复工具 - 修复内存相关工具的问题，包括数据损坏、索引错误、备份恢复、一致性检查，确保内存系统健康",
        "parameters": [
            {"name": "issue_type", "type": "string", "required": True, "description": "问题类型：corruption/index/backup/consistency"},
            {"name": "backup_first", "type": "boolean", "required": False, "description": "修复前是否备份"},
            {"name": "dry_run", "type": "boolean", "required": False, "description": "是否仅模拟修复"}
        ],
        "examples": [
            "py memory_fix_tools.py --issue_type corruption --backup_first true",
            "py memory_fix_tools.py --issue_type index --dry_run true"
        ]
    }
}

def improve_phase3():
    """改进第 3 批工具"""
    
    print("=" * 70)
    print("Improve Tool Metadata - Phase 3")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    improved_count = 0
    
    for tool_id, improvements in IMPROVEMENTS_PHASE3.items():
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 更新描述
            if "description" in improvements:
                old_desc = tool.get("description", "")
                tool["description"] = improvements["description"]
                print(f"OK {tool_id}: Description updated ({len(old_desc)}->{len(improvements['description'])} chars)")
            
            # 添加参数
            if "parameters" in improvements:
                tool["parameters"] = improvements["parameters"]
                print(f"   Params: {len(improvements['parameters'])}")
            
            # 添加示例
            if "examples" in improvements:
                tool["examples"] = improvements["examples"]
                print(f"   Examples: {len(improvements['examples'])}")
            
            # 更新时间戳
            tool["improved_at"] = datetime.now().isoformat()
            tool["improvement_version"] = "1.3.0"
            
            improved_count += 1
        else:
            print(f"WARNING {tool_id}: Tool not found")
    
    # 更新工具库
    registry["tools"] = tools
    registry["updated_at"] = datetime.now().isoformat()
    registry["improvement_record_phase3"] = {
        "improved_at": datetime.now().isoformat(),
        "improved_count": improved_count,
        "target": "tool_quality_improvement_phase3"
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\nImprovement Statistics:")
    print(f"  Tools improved: {improved_count}")
    print(f"  Total improved: 8 + 12 + {improved_count} = {8 + 12 + improved_count} tools")
    
    # 保存改进记录
    record_file = Path("flow-archive/20260318-universal-workflow-001/flow-quality-improvement/improvement-record-phase3.json")
    record_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump({
            "improved_at": datetime.now().isoformat(),
            "improved_tools": list(IMPROVEMENTS_PHASE3.keys()),
            "count": improved_count
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Record saved to: {record_file}")
    
    return improved_count


if __name__ == '__main__':
    improve_phase3()
