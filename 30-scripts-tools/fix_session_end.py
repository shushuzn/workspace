import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 修复 session_end 的命令（移除 ${args}）
if 'session_end' in registry['tools']:
    registry['tools']['session_end']['command'] = 'py 30-scripts-tools/session_end.py auto'
    print("✓ session_end 命令已修复")

with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print("\n[OK] 工具配置已更新")
