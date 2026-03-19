#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Register SA-003 and SA-004 tools"""

import json
from datetime import datetime

# Load registry
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f"Current version: {registry['version']}")
print(f"Current tool count: {len(registry['tools'])}")

# Add SA-003 and SA-004
new_tools = {
    "SA-003": {
        "tool_id": "SA-003",
        "name": "sa_003_financial_collector",
        "description": "Financial statement data collector (quarterly/annual)",
        "category": "stock_analysis",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/sa_003_financial_collector.py",
        "size_kb": 14.5,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 5,
            "passed": 5,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Quarterly and annual reports",
            "Income statement, balance sheet, cash flow",
            "Financial ratios calculation",
            "Period-over-period comparison",
            "Growth rate analysis"
        ],
        "config": {
            "data_dir": "60-DATA/stock_financials",
            "default_report_type": "quarterly",
            "default_periods": 4
        }
    },
    "SA-004": {
        "tool_id": "SA-004",
        "name": "sa_004_sentiment_monitor",
        "description": "News and sentiment monitoring with multi-source support",
        "category": "stock_analysis",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/sa_004_sentiment_monitor.py",
        "size_kb": 14.7,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 4,
            "passed": 4,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Multi-source monitoring (Sina, Xueqiu, Seeking Alpha, Twitter)",
            "Sentiment analysis (positive/neutral/negative)",
            "Sentiment scoring (-1.0 to +1.0)",
            "Trend analysis over time",
            "Article caching"
        ],
        "config": {
            "data_dir": "60-DATA/stock_news",
            "default_hours": 24,
            "default_limit": 50
        }
    }
}

# Add tools
for tool_id, tool in new_tools.items():
    registry['tools'][tool_id] = tool
    print(f"Added: {tool_id} - {tool['name']}")

# Update version
registry['version'] = '1.11.27'
registry['last_updated'] = datetime.now().isoformat()

# Save registry
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\nUpdated version: {registry['version']}")
print(f"Updated tool count: {len(registry['tools'])}")
print("\n[OK] Tools registry updated successfully")
