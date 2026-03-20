import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
if registry_file.exists():
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    print(f"工具总数：{len(tools)}")
    print("\n工具列表 (前 50 个):")
    for i, (tool_id, info) in enumerate(list(tools.items())[:50], 1):
        path = info.get("path", "N/A")
        print(f"  {i}. {tool_id}: {path}")
    
    if len(tools) > 50:
        print(f"\n... 还有 {len(tools)-50} 个工具")
else:
    print("ERROR: tools_registry.json 不存在")
