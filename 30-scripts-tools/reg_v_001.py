import logging
logger = logging.getLogger(__name__)

import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "permission-matrix",
        "name": "Permission Matrix",
        "description": "权限矩阵配置 - 定义工具风险等级和角色权限",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/permission_matrix.json",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "permission-validator",
        "name": "Permission Validator",
        "description": "权限验证器 - 基于最小权限原则的工具调用权限控制",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/permission_validator.py",
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

registry["version"] = "1.11.54-least-privilege-v10.1"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"工具总数：{len(registry['tools'])}")
print(f"新增工具：{added}")
