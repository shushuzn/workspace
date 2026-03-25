import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "tool-interceptor-v2",
        "name": "Tool Call Interceptor v2",
        "description": "工具调用拦截器 v2 - 拦截并验证所有工具调用",
        "version": "2.0.0",
        "file_path": "30-scripts-tools/tool_call_interceptor_v2.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "file-guardian",
        "name": "File Guardian",
        "description": "文件守护进程 - 实时监控防护文件完整性",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/file_guardian.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "session-token-validator",
        "name": "Session Token Validator",
        "description": "会话令牌验证器 - 防止会话劫持和伪造",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/session_token_validator.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    }
]

added = 0
for tool in new_tools:
    tool_id = tool["tool_id"]
    if tool_id not in registry["tools"]:
        registry["tools"][tool_id] = tool
        added += 1
        print(f"[ADD] {tool_id}")

registry["version"] = "1.11.53-ultimate-v10"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"工具总数：{len(registry['tools'])}")
