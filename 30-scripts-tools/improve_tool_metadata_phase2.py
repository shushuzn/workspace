#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improve Tool Metadata Phase 2 - 完善工具元数据第 2 批

继续改进剩余低分工具
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 第 2 批改进工具
IMPROVEMENTS_PHASE2 = {
    "auto_execute_workflow": {
        "description": "自动执行工作流工具 - 根据工作流配置自动执行各个步骤，支持进度跟踪和错误处理",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "start_step", "type": "int", "required": False, "description": "起始步骤"},
            {"name": "dry_run", "type": "boolean", "required": False, "description": "是否仅模拟执行"}
        ],
        "examples": [
            "py auto_execute_workflow.py --flow_id \"20260318-universal-workflow-001\"",
            "py auto_execute_workflow.py --flow_id \"xxx\" --start_step 5 --dry_run true"
        ]
    },
    "workflow_interactive": {
        "description": "交互式工作流工具 - 提供交互式工作流执行界面，支持用户输入和实时反馈",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "interactive_mode", "type": "boolean", "required": False, "description": "是否交互模式"}
        ],
        "examples": [
            "py workflow_interactive.py --flow_id \"20260318-universal-workflow-001\" --interactive_mode true"
        ]
    },
    "register_core_tools": {
        "description": "核心工具注册工具 - 批量注册核心工具到工具库，包括工作流/内存/批判者类工具",
        "parameters": [
            {"name": "tool_list", "type": "list", "required": True, "description": "工具列表"},
            {"name": "category", "type": "string", "required": False, "description": "工具类别"}
        ],
        "examples": [
            "py register_core_tools.py --tool_list \"[\"workflow-enforcer\", \"memory-checker\"]\"",
            "py register_core_tools.py --tool_list \"[...]\" --category \"workflow\""
        ]
    },
    "check_core_tools": {
        "description": "核心工具检查工具 - 验证核心工具是否已注册且文件存在，确保工作流正常运行",
        "parameters": [
            {"name": "tool_ids", "type": "list", "required": False, "description": "要检查的工具 ID 列表"},
            {"name": "check_file", "type": "boolean", "required": False, "description": "是否检查文件存在"}
        ],
        "examples": [
            "py check_core_tools.py",
            "py check_core_tools.py --tool_ids \"[\"workflow-enforcer\"]\" --check_file true"
        ]
    },
    "check_flow_manager": {
        "description": "工作流管理器检查工具 - 检查工作流管理器状态，包括配置、进度、执行历史",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "check_type", "type": "string", "required": False, "description": "检查类型：config/progress/history"}
        ],
        "examples": [
            "py check_flow_manager.py --flow_id \"20260318-universal-workflow-001\"",
            "py check_flow_manager.py --flow_id \"xxx\" --check_type progress"
        ]
    },
    "context_verify": {
        "description": "上下文验证工具 - 验证加载的上下文是否完整正确，包括 7 个核心文件检查",
        "parameters": [
            {"name": "strict_mode", "type": "boolean", "required": False, "description": "严格模式：是/否"},
            {"name": "output_detail", "type": "boolean", "required": False, "description": "是否输出详情"}
        ],
        "examples": [
            "py context_verify.py",
            "py context_verify.py --strict_mode true --output_detail true"
        ]
    },
    "critical-issue-detector": {
        "description": "关键问题检测工具 - 自动检测工作流执行中的关键问题和风险，提前预警",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "sensitivity", "type": "string", "required": False, "description": "敏感度：high/medium/low"}
        ],
        "examples": [
            "py critical_issue_detector.py --flow_id \"20260318-universal-workflow-001\"",
            "py critical_issue_detector.py --flow_id \"xxx\" --sensitivity high"
        ]
    },
    "critical-checks": {
        "description": "关键检查工具 - 执行关键质量检查，包括代码质量、文档完整性、测试覆盖率",
        "parameters": [
            {"name": "check_items", "type": "list", "required": True, "description": "检查项列表"},
            {"name": "threshold", "type": "float", "required": False, "description": "通过阈值 (0-1)"}
        ],
        "examples": [
            "py critical_checks.py --check_items \"[\"code_quality\", \"documentation\"]\"",
            "py critical_checks.py --check_items \"[...]\" --threshold 0.8"
        ]
    },
    "analyze_memory_scripts": {
        "description": "内存脚本分析工具 - 分析内存相关脚本的使用情况和性能，提供优化建议",
        "parameters": [
            {"name": "script_dir", "type": "string", "required": True, "description": "脚本目录"},
            {"name": "include_usage", "type": "boolean", "required": False, "description": "是否包含使用统计"}
        ],
        "examples": [
            "py analyze_memory_scripts.py --script_dir \"30-scripts-tools\"",
            "py analyze_memory_scripts.py --script_dir \"xxx\" --include_usage true"
        ]
    },
    "analyze_memory_tools": {
        "description": "内存工具分析工具 - 分析内存相关工具的效果和使用频率，识别改进机会",
        "parameters": [
            {"name": "time_range", "type": "string", "required": False, "description": "时间范围：day/week/month"},
            {"name": "output_format", "type": "string", "required": False, "description": "输出格式：json/md"}
        ],
        "examples": [
            "py analyze_memory_tools.py --time_range week",
            "py analyze_memory_tools.py --time_range month --output_format md"
        ]
    },
    "critic_daily_note_pollution": {
        "description": "批判者每日笔记污染检测工具 - 检测每日笔记中的冗余和污染内容，保持笔记简洁",
        "parameters": [
            {"name": "date", "type": "string", "required": False, "description": "日期 (YYYY-MM-DD)"},
            {"name": "auto_clean", "type": "boolean", "required": False, "description": "是否自动清理"}
        ],
        "examples": [
            "py critic_daily_note_pollution.py --date \"2026-03-20\"",
            "py critic_daily_note_pollution.py --auto_clean true"
        ]
    },
    "memory_fix_tools": {
        "description": "内存修复工具 - 修复内存相关工具的问题，包括数据损坏、索引错误等",
        "parameters": [
            {"name": "issue_type", "type": "string", "required": True, "description": "问题类型：corruption/index/backup"},
            {"name": "backup_first", "type": "boolean", "required": False, "description": "是否先备份"}
        ],
        "examples": [
            "py memory_fix_tools.py --issue_type corruption --backup_first true",
            "py memory_fix_tools.py --issue_type index"
        ]
    }
}

def improve_phase2():
    """改进第 2 批工具"""
    
    print("=" * 70)
    print("🔧 完善工具元数据 - 第 2 批")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    improved_count = 0
    
    for tool_id, improvements in IMPROVEMENTS_PHASE2.items():
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 更新描述
            if "description" in improvements:
                old_desc = tool.get("description", "")
                tool["description"] = improvements["description"]
                print(f"✅ {tool_id}: 描述已更新 ({len(old_desc)}→{len(improvements['description'])}字)")
            
            # 添加参数
            if "parameters" in improvements:
                tool["parameters"] = improvements["parameters"]
                print(f"   参数：{len(improvements['parameters'])} 个")
            
            # 添加示例
            if "examples" in improvements:
                tool["examples"] = improvements["examples"]
                print(f"   示例：{len(improvements['examples'])} 个")
            
            # 更新时间戳
            tool["improved_at"] = datetime.now().isoformat()
            tool["improvement_version"] = "1.2.0"
            
            improved_count += 1
        else:
            print(f"⚠️  {tool_id}: 工具不存在")
    
    # 更新工具库
    registry["tools"] = tools
    registry["updated_at"] = datetime.now().isoformat()
    registry["improvement_record_phase2"] = {
        "improved_at": datetime.now().isoformat(),
        "improved_count": improved_count,
        "target": "tool_quality_improvement_phase2"
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 改进统计:")
    print(f"  改进工具数：{improved_count}")
    print(f"  累计改进：8 + {improved_count} = {8 + improved_count} 个")
    
    # 保存改进记录
    record_file = Path("flow-archive/20260318-universal-workflow-001/flow-quality-improvement/improvement-record-phase2.json")
    record_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump({
            "improved_at": datetime.now().isoformat(),
            "improved_tools": list(IMPROVEMENTS_PHASE2.keys()),
            "count": improved_count
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📁 改进记录已保存：{record_file}")
    
    return improved_count


if __name__ == '__main__':
    improve_phase2()
