#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Brainstorm - Generate next tool ideas
"""
import json
from pathlib import Path
from datetime import datetime

# Define topic
topic = {
    "topic": "What tools should we create next for OpenClaw?",
    "context": "We have 354 tools already, 9 dimensions at 100%",
    "constraints": "Focus on high-impact, feasible tools",
    "created_at": datetime.now().isoformat()
}

# Save
output_dir = Path("flow-archive/brainstorm-current")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "brainstorm_topic.json", "w", encoding="utf-8") as f:
    json.dump(topic, f, indent=2, ensure_ascii=False)

print("Topic saved!")
print(json.dumps(topic, indent=2, ensure_ascii=False))