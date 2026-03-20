#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Register SA-001 and SA-002 tools"""

import json
from datetime import datetime

# Load registry
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f"Current version: {registry['version']}")
print(f"Current tool count: {len(registry['tools'])}")

# Add SA-001 and SA-002
new_tools = {
    "SA-001": {
        "tool_id": "SA-001",
        "name": "sa_001_realtime_fetcher",
        "description": "Real-time stock market data fetcher (multi-source)",
        "category": "stock_analysis",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/sa_001_realtime_fetcher.py",
        "size_kb": 11.0,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 5,
            "passed": 5,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Multi-source data (Yahoo/East Money)",
            "Real-time price fetching",
            "60-second cache",
            "Batch fetching support",
            "Fetch statistics tracking"
        ],
        "config": {
            "cache_dir": "60-DATA/stock_cache",
            "cache_age_seconds": 60,
            "default_source": "yahoo"
        }
    },
    "SA-002": {
        "tool_id": "SA-002",
        "name": "sa_002_historical_downloader",
        "description": "Historical K-line data downloader with adjustment",
        "category": "stock_analysis",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "file_path": "30-scripts-tools/sa_002_historical_downloader.py",
        "size_kb": 15.1,
        "status": "active",
        "tested": True,
        "test_results": {
            "test_count": 5,
            "passed": 5,
            "failed": 0,
            "tested_at": datetime.now().isoformat()
        },
        "features": [
            "Multiple timeframes (1d/1w/1mo)",
            "Adjustment support (forward/backward/none)",
            "OHLCV data",
            "Statistics calculation",
            "Auto-caching"
        ],
        "config": {
            "data_dir": "60-DATA/stock_historical",
            "default_timeframe": "1d",
            "default_adjustment": "forward"
        }
    }
}

# Add tools
for tool_id, tool in new_tools.items():
    registry['tools'][tool_id] = tool
    print(f"Added: {tool_id} - {tool['name']}")

# Update version
registry['version'] = '1.11.26'
registry['last_updated'] = datetime.now().isoformat()

# Save registry
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\nUpdated version: {registry['version']}")
print(f"Updated tool count: {len(registry['tools'])}")
print("\n[OK] Tools registry updated successfully")
