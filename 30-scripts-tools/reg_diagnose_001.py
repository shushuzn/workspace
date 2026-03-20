import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["diagnose-registry"] = {
    "tool_id": "diagnose-registry",
    "name": "Diagnose Registry",
    "description": "诊断工具注册表问题",
    "version": "1.0.0",
    "command": "py 30-scripts-tools\\diagnose_registry.py",
    "path": "30-scripts-tools\\diagnose_registry.py",
    "category": "diagnostic",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("diagnose-registry 已注册")
