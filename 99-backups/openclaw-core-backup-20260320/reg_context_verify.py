import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 检查 context_verify 是否存在
if "context_verify" in registry["tools"]:
    print("context_verify 已注册")
else:
    # 添加 context_verify
    registry["tools"]["context_verify"] = {
        "tool_id": "context_verify",
        "name": "Context Verify",
        "description": "上下文验证工具",
        "version": "1.0.0",
        "command": "py 30-scripts-tools\\context_verify.py",
        "path": "30-scripts-tools\\context_verify.py",
        "category": "verification",
        "parameters": {}
    }

    with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print("context_verify 已注册")
