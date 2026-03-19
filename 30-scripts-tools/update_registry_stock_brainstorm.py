#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Register stock analysis brainstorm tools"""

import json
from datetime import datetime

# Load registry
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f"Current version: {registry['version']}")
print(f"Current tool count: {len(registry['tools'])}")

# Add stock analysis brainstorm tools
new_tools = {
    "BRAIN-STOCK-001": {
        "tool_id": "BRAIN-STOCK-001",
        "name": "brainstorm_stock_analysis",
        "description": "Stock analysis workflow brainstorm - AI idea generation",
        "category": "brainstorm",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/brainstorm_stock_analysis.py",
        "size_kb": 11.3,
        "status": "active",
        "tested": True,
        "output": {
            "components": 24,
            "p0_count": 18,
            "p1_count": 6,
            "total_effort_hours": 153
        }
    },
    "BRAIN-STOCK-002": {
        "tool_id": "BRAIN-STOCK-002",
        "name": "stock_analysis_mindmap",
        "description": "Stock analysis workflow mind map visualization",
        "category": "brainstorm",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/stock-analysis-mindmap.md",
        "size_kb": 4.6,
        "status": "active",
        "tested": True,
        "output": {
            "format": "markdown",
            "has_dependency_graph": True,
            "has_implementation_phases": True
        }
    },
    "BRAIN-STOCK-003": {
        "tool_id": "BRAIN-STOCK-003",
        "name": "stock_analysis_quality_predictor",
        "description": "Quality prediction for stock analysis workflow",
        "category": "brainstorm",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/stock_analysis_quality_predictor.py",
        "size_kb": 5.9,
        "status": "active",
        "tested": True,
        "output": {
            "quality_score": 98.5,
            "grade": "A - Excellent",
            "dimensions": 5
        }
    }
}

# Add tools
for tool_id, tool in new_tools.items():
    registry['tools'][tool_id] = tool
    print(f"Added: {tool_id} - {tool['name']}")

# Update version
registry['version'] = '1.11.25'
registry['last_updated'] = datetime.now().isoformat()

# Save registry
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\nUpdated version: {registry['version']}")
print(f"Updated tool count: {len(registry['tools'])}")
print("\n[OK] Tools registry updated successfully")
