import json
with open("flow-archive/20260318-universal-workflow-001/execution-state.json", "r", encoding="utf-8") as f:
    e = json.load(f)
print("Session ID:", e.get("session_id", "NOT FOUND"))
