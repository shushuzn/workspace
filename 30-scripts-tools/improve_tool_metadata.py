#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improve Tool Metadata - 完善工具元数据

为低分工具添加描述、参数、示例
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 工具改进模板
IMPROVEMENTS = {
    "brainstorm-define": {
        "description": "头脑风暴定义工具 - 帮助定义问题范围、目标和约束条件，生成结构化的问题定义文档",
        "parameters": [
            {"name": "topic", "type": "string", "required": True, "description": "头脑风暴主题"},
            {"name": "constraints", "type": "list", "required": False, "description": "约束条件列表"}
        ],
        "examples": [
            "py brainstorm_define.py --topic \"AI  Agent 自主性提升\"",
            "py brainstorm_define.py --topic \"工具库优化\" --constraints \"[\"时间<1 小时\", \"不影响核心功能\"]\""
        ]
    },
    "brainstorm-prioritize": {
        "description": "头脑风暴优先级排序工具 - 对头脑风暴产生的想法进行优先级排序，使用影响/努力矩阵评估",
        "parameters": [
            {"name": "ideas", "type": "list", "required": True, "description": "想法列表"},
            {"name": "criteria", "type": "dict", "required": False, "description": "评估标准"}
        ],
        "examples": [
            "py brainstorm_prioritize.py --ideas \"[\"想法 1\", \"想法 2\"]\"",
            "py brainstorm_prioritize.py --ideas \"[...]\" --criteria \"{\"impact\": 0.6, \"effort\": 0.4}\""
        ]
    },
    "brainstorm-action": {
        "description": "头脑风暴行动规划工具 - 将头脑风暴结果转化为可执行的行动计划，包含步骤、时间、负责人",
        "parameters": [
            {"name": "prioritized_ideas", "type": "list", "required": True, "description": "已排序的想法"},
            {"name": "timeline", "type": "string", "required": False, "description": "时间线 (如\"本周\", \"本月\")"}
        ],
        "examples": [
            "py brainstorm_action.py --prioritized_ideas \"[...]\" --timeline \"本周\""
        ]
    },
    "check_tools": {
        "description": "工具检查工具 - 检查工具库健康状态，包括文件存在性、注册状态、使用情况",
        "parameters": [
            {"name": "check_type", "type": "string", "required": False, "description": "检查类型：all/files/usage"},
            {"name": "output_format", "type": "string", "required": False, "description": "输出格式：json/md/text"}
        ],
        "examples": [
            "py check_tools.py",
            "py check_tools.py --check_type files --output_format md"
        ]
    },
    "check_workflow_steps": {
        "description": "工作流步骤检查工具 - 验证工作流步骤执行情况，检查是否有跳步或未完成步骤",
        "parameters": [
            {"name": "flow_id", "type": "string", "required": True, "description": "工作流 ID"},
            {"name": "strict_mode", "type": "boolean", "required": False, "description": "严格模式：是/否"}
        ],
        "examples": [
            "py check_workflow_steps.py --flow_id \"20260318-universal-workflow-001\"",
            "py check_workflow_steps.py --flow_id \"xxx\" --strict_mode true"
        ]
    },
    "session_compress": {
        "description": "会话压缩工具 - 将完整会话日志压缩为结构化摘要，减少 96% token 使用",
        "parameters": [
            {"name": "session_file", "type": "string", "required": True, "description": "会话文件路径"},
            {"name": "compression_ratio", "type": "float", "required": False, "description": "目标压缩率 (0-1)"}
        ],
        "examples": [
            "py session_compress.py --session_file \"session.json\"",
            "py session_compress.py --session_file \"xxx.json\" --compression_ratio 0.96"
        ]
    },
    "git_workflow": {
        "description": "Git 工作流工具 - 自动化 Git 提交流程，包括 add/commit/push，支持自定义提交信息",
        "parameters": [
            {"name": "message", "type": "string", "required": True, "description": "提交信息"},
            {"name": "auto_push", "type": "boolean", "required": False, "description": "是否自动推送"}
        ],
        "examples": [
            "py git_workflow.py --message \"feat: add new tool\"",
            "py git_workflow.py --message \"fix: bug fix\" --auto_push true"
        ]
    },
    "context_db": {
        "description": "上下文数据库工具 - 管理会话上下文数据，支持存储、查询、删除上下文记录",
        "parameters": [
            {"name": "action", "type": "string", "required": True, "description": "操作类型：store/query/delete"},
            {"name": "key", "type": "string", "required": True, "description": "上下文键"},
            {"name": "value", "type": "any", "required": False, "description": "上下文值"}
        ],
        "examples": [
            "py context_db.py --action store --key \"user_pref\" --value \"{...}\"",
            "py context_db.py --action query --key \"user_pref\""
        ]
    }
}

def improve_tool_metadata():
    """改进工具元数据"""
    
    print("=" * 70)
    print("🔧 完善工具元数据")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    improved_count = 0
    
    for tool_id, improvements in IMPROVEMENTS.items():
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
            tool["improvement_version"] = "1.1.0"
            
            improved_count += 1
        else:
            print(f"⚠️  {tool_id}: 工具不存在")
    
    # 更新工具库
    registry["tools"] = tools
    registry["updated_at"] = datetime.now().isoformat()
    registry["improvement_record"] = {
        "improved_at": datetime.now().isoformat(),
        "improved_count": improved_count,
        "target": "tool_quality_improvement_phase1"
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 改进统计:")
    print(f"  改进工具数：{improved_count}")
    print(f"  工具库版本：{registry.get('version', 'N/A')}")
    
    # 重新评分
    print(f"\n📊 重新评分...")
    
    # 保存改进记录
    record_file = Path("flow-archive/20260318-universal-workflow-001/flow-quality-improvement/improvement-record-phase1.json")
    record_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump({
            "improved_at": datetime.now().isoformat(),
            "improved_tools": list(IMPROVEMENTS.keys()),
            "count": improved_count
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📁 改进记录已保存：{record_file}")
    
    return improved_count


if __name__ == '__main__':
    improve_tool_metadata()
