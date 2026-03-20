#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check tools_registry.json structure"""

import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f"Type of 'tools': {type(registry.get('tools'))}")
print(f"Keys: {list(registry.keys())[:10]}")

if isinstance(registry.get('tools'), dict):
    print(f"Tools dict keys (first 5): {list(registry['tools'].keys())[:5]}")
    print(f"Total tools: {len(registry['tools'])}")
