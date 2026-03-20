import subprocess
import json

# 获取 7f1c44e 版本的 registry
result = subprocess.run(
    ["git", "show", "7f1c44e:30-scripts-tools/tools_registry.json"],
    capture_output=True,
    text=True,
    encoding="utf-8"
, timeout=60)

if result.returncode == 0:
    registry = json.loads(result.stdout)
    tools = registry.get("tools", {})
    print(f"版本：7f1c44e")
    print(f"Registry 版本：{registry.get('version', 'N/A')}")
    print(f"工具总数：{len(tools)}")
    
    # 显示前 10 个工具
    print(f"\n前 10 个工具:")
    for i, (tool_id, info) in enumerate(list(tools.items())[:10], 1):
        print(f"  {i}. {tool_id}")
else:
    print(f"错误：{result.stderr}")
