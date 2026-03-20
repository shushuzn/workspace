import json
with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    r = json.load(f)
r["tools"]["task_analyzer"] = {
    "tool_id": "task_analyzer",
    "name": "Task Analyzer",
    "description": "任务分析工具",
    "version": "1.0.0",
    "path": "30-scripts-tools\\task_analyzer.py",
    "category": "analysis",
    "parameters": {}
}
with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(r, f, ensure_ascii=False, indent=2)
print("[OK] task_analyzer 已注册")
