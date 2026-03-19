#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量注册工具到 tools_registry.json
扫描所有 .py 文件并自动注册
"""

import json
import os
import sys
import io
from pathlib import Path
from datetime import datetime

# 修复中文乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "30-scripts-tools"
REGISTRY_FILE = SCRIPTS_DIR / "tools_registry.json"

# 已有关键工具（不要重复注册）
EXCLUDE_FILES = [
    'tool_executor.py', 'workflow_enforcer.py', 'auto_execute_workflow.py',
    'workflow_interactive.py', 'check_tools.py', 'check_workflow_steps.py',
    'check_flow_manager.py', 'register_tools.py'
]

# 工具分类映射
TOOL_CATEGORIES = {
    'auto-critic': {'category': 'quality', 'desc': '自动批判者 - 代码/方案审查'},
    'auto-critic_v7': {'category': 'quality', 'desc': '批判者 v7 - 终极审查'},
    'flow_manager': {'category': 'workflow', 'desc': 'Flow ID 管理器 - 创建/快照/恢复'},
    'session_end': {'category': 'session', 'desc': '会话结束处理 - 压缩/保存'},
    'post_session_compress': {'category': 'session', 'desc': '会话压缩 - 对话摘要'},
    'pre-session-hook': {'category': 'session', 'desc': '会话前钩子 - 上下文检查'},
    'quality_gate_check': {'category': 'quality', 'desc': '质量门禁检查'},
    'context_search': {'category': 'context', 'desc': '上下文搜索 - 快速检索'},
    'context_compressor': {'category': 'context', 'desc': '上下文压缩器'},
    'memory_search': {'category': 'memory', 'desc': '记忆搜索 - 语义检索'},
    'memory_distill': {'category': 'memory', 'desc': '记忆蒸馏 - 提炼要点'},
    'memory_cleanup': {'category': 'memory', 'desc': '记忆清理 - 删除冗余'},
    'brainstorm': {'category': 'brainstorm', 'desc': '头脑风暴工具'},
    'critic': {'category': 'quality', 'desc': '批判者工具'},
    'workflow': {'category': 'workflow', 'desc': '工作流工具'},
    'tool_': {'category': 'tool', 'desc': '工具管理'},
    'git': {'category': 'git', 'desc': 'Git 操作工具'},
    'security': {'category': 'security', 'desc': '安全检查/修复'},
    'cache': {'category': 'performance', 'desc': '缓存优化'},
    'dashboard': {'category': 'ui', 'desc': '仪表板'},
    'monitor': {'category': 'monitoring', 'desc': '监控工具'},
    'report': {'category': 'reporting', 'desc': '报告生成'},
    'feishu': {'category': 'integration', 'desc': '飞书集成'},
    'knowledge_graph': {'category': 'kg', 'desc': '知识图谱'},
    'kg_': {'category': 'kg', 'desc': '知识图谱工具'},
}

def get_category(filename):
    """根据文件名推断分类"""
    name_lower = filename.lower().replace('.py', '').replace('-', '_')
    
    for key, info in TOOL_CATEGORIES.items():
        if key in name_lower:
            return info['category'], info['desc']
    
    return 'general', f'{filename.replace(".py", "")} 工具'

def generate_tool_id(filename):
    """从文件名生成 tool_id"""
    name = filename.replace('.py', '').replace('-', '_')
    return name

def get_command(filename):
    """生成执行命令"""
    name = filename.replace('.py', '')
    # 处理带横杠的文件名
    return f"py 30-scripts-tools/{name}.py ${{args}}"

def load_registry():
    """加载工具注册表"""
    if not REGISTRY_FILE.exists():
        return {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "tools": {}
        }
    
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_registry(registry):
    """保存工具注册表"""
    registry['updated_at'] = datetime.now().isoformat()
    
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 注册表已保存：{REGISTRY_FILE}")

def register_tool(registry, filename):
    """注册单个工具"""
    if filename in EXCLUDE_FILES:
        return False
    
    tool_id = generate_tool_id(filename)
    
    # 检查是否已存在
    if tool_id in registry['tools']:
        return False
    
    category, description = get_category(filename)
    command = get_command(filename)
    
    registry['tools'][tool_id] = {
        "tool_id": tool_id,
        "command": command,
        "description": description,
        "version": "1.0.0",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "parameters": {
            "args": {
                "type": "string",
                "description": "工具参数",
                "required": False
            }
        },
        "examples": [
            f"py 30-scripts-tools/{filename} --help"
        ],
        "validation": {
            "workspace_check": True
        },
        "output": {
            "format": "console",
            "log_to_flow": True
        }
    }
    
    return True

def main():
    print("="*60)
    print("批量工具注册")
    print("="*60)
    
    # 加载现有注册表
    registry = load_registry()
    existing_count = len(registry['tools'])
    print(f"\n[INFO] 当前已注册工具数：{existing_count}")
    
    # 扫描所有 .py 文件
    py_files = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py') and not f.startswith('_')]
    print(f"[INFO] 扫描到 .py 文件数：{len(py_files)}")
    
    # 批量注册
    registered = 0
    skipped = 0
    
    for filename in sorted(py_files):
        if register_tool(registry, filename):
            registered += 1
            print(f"  ✓ {filename} → {generate_tool_id(filename)}")
        else:
            skipped += 1
    
    # 保存注册表
    save_registry(registry)
    
    # 统计
    print(f"\n{'='*60}")
    print(f"[OK] 注册完成！")
    print(f"  新增工具：{registered}")
    print(f"  跳过：{skipped}")
    print(f"  总计：{len(registry['tools'])}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
