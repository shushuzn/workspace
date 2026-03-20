import json
from pathlib import Path

d = json.load(open("30-scripts-tools/tools_registry.json", encoding="utf-8"))
cats = {}
for t in d.get("tools", {}).values():
    c = t.get("category", "unknown")
    cats[c] = cats.get(c, 0) + 1

print(json.dumps(cats, indent=2))