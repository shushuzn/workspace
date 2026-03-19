import json
from datetime import datetime

REGISTRY_FILE = '30-scripts-tools/tools_registry.json'

# 核心工具定义
CORE_TOOLS = {
    'tool_executor': {
        'tool_id': 'tool_executor',
        'command': 'py 30-scripts-tools/tool_executor.py ${args}',
        'description': '工具执行器 - 统一工具调用入口（唯一合法方式）',
        'category': 'core',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'critical'
    },
    'workflow_enforcer': {
        'tool_id': 'workflow_enforcer',
        'command': 'py 30-scripts-tools/workflow_enforcer.py ${args}',
        'description': '工作流强制检查 - 确保步骤合规',
        'category': 'core',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'critical'
    },
    'auto_execute_workflow': {
        'tool_id': 'auto_execute_workflow',
        'command': 'py 30-scripts-tools/auto_execute_workflow.py',
        'description': '全自动工作流执行 - 零手动干预',
        'category': 'core',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'critical'
    },
    'workflow_interactive': {
        'tool_id': 'workflow_interactive',
        'command': 'py 30-scripts-tools/workflow_interactive.py',
        'description': '交互式工作流执行 - 图形界面',
        'category': 'core',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'high'
    },
    'check_tools': {
        'tool_id': 'check_tools',
        'command': 'py 30-scripts-tools/check_tools.py',
        'description': '工具列表检查',
        'category': 'utility',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'low'
    },
    'check_workflow_steps': {
        'tool_id': 'check_workflow_steps',
        'command': 'py 30-scripts-tools/check_workflow_steps.py',
        'description': '工作流步骤配置检查',
        'category': 'utility',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'low'
    },
    'register_core_tools': {
        'tool_id': 'register_core_tools',
        'command': 'py 30-scripts-tools/register_core_tools.py',
        'description': '注册核心工具',
        'category': 'utility',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'low'
    },
    'check_core_tools': {
        'tool_id': 'check_core_tools',
        'command': 'py 30-scripts-tools/check_core_tools.py',
        'description': '检查核心工具注册状态',
        'category': 'utility',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'low'
    },
    'check_flow_manager': {
        'tool_id': 'check_flow_manager',
        'command': 'py 30-scripts-tools/check_flow_manager.py',
        'description': '检查 flow-manager 工具配置',
        'category': 'utility',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'low'
    },
    'register_tools': {
        'tool_id': 'register_tools',
        'command': 'py 30-scripts-tools/register_tools.py',
        'description': '批量注册工具',
        'category': 'utility',
        'version': '1.0.0',
        'created_at': '2026-03-19',
        'priority': 'low'
    },
}

# 加载注册表
with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 添加核心工具
added = 0
for tool_id, config in CORE_TOOLS.items():
    if tool_id not in registry['tools']:
        registry['tools'][tool_id] = config
        print(f"✓ {tool_id}")
        added += 1
    else:
        print(f"- {tool_id} (已存在)")

# 保存
with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f"\n[OK] 添加 {added} 个核心工具")
