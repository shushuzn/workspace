import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 使用 embedded-critic 作为 auto_critic_v7 的替代
registry["tools"]["auto_critic_v7"] = {
    "tool_id": "auto_critic_v7",
    "name": "Auto Critic v7",
    "description": "自动批判者 v7.0",
    "version": "7.0.0",
    "command": "py 30-scripts-tools\\embedded_critic.py",
    "path": "30-scripts-tools\\embedded_critic.py",
    "category": "critic",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("auto_critic_v7 已注册 (使用 embedded_critic.py)")
