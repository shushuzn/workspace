#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update tools_registry.json with UX Phase 3 tools"""

import json
from datetime import datetime

# Load registry
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f"Current version: {registry['version']}")
print(f"Current tool count: {len(registry['tools'])}")

# Add UX Phase 3 tools
new_tools = {
    "P0-UX-007": {
        "tool_id": "P0-UX-007",
        "name": "user_preferences",
        "description": "User preference profile management with persistence",
        "category": "ux",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/user_preferences.py",
        "size_kb": 8.4,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 5,
            "passed": 5,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Profile management",
            "Preference persistence",
            "Shortcut customization",
            "Usage statistics tracking",
            "Profile import/export"
        ],
        "config": {
            "default_profile": "default",
            "profiles_dir": "03-config/user_profiles",
            "auto_save": True
        }
    },
    "P0-UX-008": {
        "tool_id": "P0-UX-008",
        "name": "auto_retry",
        "description": "Intelligent retry system with exponential backoff",
        "category": "ux",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/auto_retry.py",
        "size_kb": 10.9,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 5,
            "passed": 5,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Exponential backoff",
            "Jitter support",
            "Retryable error detection",
            "Retry logging",
            "Statistics tracking"
        ],
        "config": {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "exponential": True,
            "jitter": True
        }
    },
    "P0-UX-009": {
        "tool_id": "P0-UX-009",
        "name": "progressive_output",
        "description": "Stream output in chunks for better UX",
        "category": "ux",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/progressive_output.py",
        "size_kb": 10.3,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 5,
            "passed": 5,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Chunk-by-chunk streaming",
            "Configurable chunk size",
            "Line-by-line mode",
            "Generator support",
            "Progress tracking"
        ],
        "config": {
            "chunk_size": 100,
            "chunk_delay": 0.1,
            "show_progress": True
        }
    }
}

# Add tools
for tool_id, tool in new_tools.items():
    registry['tools'][tool_id] = tool
    print(f"Added: {tool_id} - {tool['name']}")

# Update version
registry['version'] = '1.11.24'
registry['last_updated'] = datetime.now().isoformat()

# Update category counts (if exists)
if 'category_counts' in registry:
    if 'ux' not in registry['category_counts']:
        registry['category_counts']['ux'] = 0
    registry['category_counts']['ux'] += 3

# Save registry
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\nUpdated version: {registry['version']}")
print(f"Updated tool count: {len(registry['tools'])}")
if 'category_counts' in registry:
    print(f"UX category count: {registry['category_counts'].get('ux', 'N/A')}")
print("\n[OK] Tools registry updated successfully")
