import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 修复需要特定参数的工具
fixes = {
    'quality_gate_check': 'py 30-scripts-tools/quality_gate_check.py --all',
    'context_search': 'py 30-scripts-tools/context_search.py --demo',
    'session_end': 'py 30-scripts-tools/session_end.py "工作流自动执行完成"',
}

for tool_id, command in fixes.items():
    if tool_id in registry['tools']:
        registry['tools'][tool_id]['command'] = command
        print(f"✓ {tool_id} 命令已修复")

# 保存
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print("\n[OK] 工具配置已更新")
