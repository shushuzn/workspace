#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update tools_registry.json with new stock analysis tools"""

import json
from datetime import datetime

# Load registry
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# New tools to add
new_tools = {
    "sa_005_indicator_calculator": {
        "tool_id": "sa_005_indicator_calculator",
        "name": "Technical Indicator Calculator",
        "description": "Stock Analysis Phase 2 - Calculate 11+ technical indicators (MA, MACD, RSI, KDJ, BOLL, ATR, CCI, etc.) with trading signals",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"},
            "indicators": {"type": "list", "required": False, "description": "List of indicators to calculate"}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_indicators/{symbol}_indicators.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_005_indicator_calculator.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    },
    "sa_006_pattern_recognition": {
        "tool_id": "sa_006_pattern_recognition",
        "name": "Pattern Recognition",
        "description": "Stock Analysis Phase 2 - Automatic K-line pattern detection (Head & Shoulders, Double Top/Bottom, Triangles, Flags)",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"},
            "patterns": {"type": "list", "required": False, "description": "Specific patterns to detect"}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_patterns/{symbol}_patterns.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_006_pattern_recognition.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    },
    "sa_007_trend_analysis": {
        "tool_id": "sa_007_trend_analysis",
        "name": "Trend Analysis",
        "description": "Stock Analysis Phase 2 - Multi-timeframe trend analysis (short/medium/long), ADX indicator, MA analysis",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"},
            "timeframes": {"type": "list", "required": False, "description": "Timeframes to analyze"}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_trends/{symbol}_trend.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_007_trend_analysis.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    },
    "sa_008_support_resistance": {
        "tool_id": "sa_008_support_resistance",
        "name": "Support & Resistance Analyzer",
        "description": "Stock Analysis Phase 2 - Automatic S&R level detection (Pivot Points, Fibonacci, Price Clusters, Volume Profile)",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_sr_levels/{symbol}_sr_levels.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_008_support_resistance.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    }
}

# Add new tools
tools = registry.get('tools', {})
for tool_id, tool_data in new_tools.items():
    tools[tool_id] = tool_data
    print(f"[OK] Added {tool_id}")

registry['tools'] = tools
registry['version'] = '1.11.31'
registry['last_updated'] = datetime.now().isoformat()

# Save registry
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Registry updated to v{registry['version']}")
print(f"Total tools: {len(tools)}")
print(f"Stock analysis tools: {[k for k in tools.keys() if k.startswith('sa_')]}")
