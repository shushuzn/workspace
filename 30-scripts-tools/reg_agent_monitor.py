import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tool = {
    "tool_id": "agent-tool-monitor",
    "name": "Agent Tool Monitor",
    "description": "Agent 工具监控器 - 检测并阻止绕过防护的行为",
    "version": "1.0.0",
    "file_path": "30-scripts-tools/agent_tool_monitor.py",
    "category": "protection",
    "status": "active",
    "usage_count": 0,
    "created_at": datetime.now().isoformat()
}

tool_id = new_tool["tool_id"]
if tool_id not in registry["tools"]:
    registry["tools"][tool_id] = new_tool
    print(f"[ADD] {tool_id}")

registry["version"] = "1.11.47-agent-monitor-v4"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
