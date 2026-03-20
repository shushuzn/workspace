#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update tools_registry.json with SA-009 to SA-012"""

import json
from datetime import datetime

# Load registry
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# New tools to add
new_tools = {
    "sa_009_risk_management": {
        "tool_id": "sa_009_risk_management",
        "name": "Risk Management",
        "description": "Stock Analysis Phase 2 - Position sizing, stop-loss, take-profit, risk-reward calculation",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"},
            "account_size": {"type": "number", "required": False, "description": "Account size", "default": 100000},
            "risk_per_trade": {"type": "number", "required": False, "description": "Risk per trade", "default": 0.02}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_risk/{symbol}_risk_analysis.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_009_risk_management.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    },
    "sa_010_signal_generator": {
        "tool_id": "sa_010_signal_generator",
        "name": "Signal Generator",
        "description": "Stock Analysis Phase 2 - Confluence-based trading signals from MA, MACD, RSI, KDJ, BOLL",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_signals/{symbol}_signals.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_010_signal_generator.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    },
    "sa_011_backtesting": {
        "tool_id": "sa_011_backtesting",
        "name": "Backtesting Engine",
        "description": "Stock Analysis Phase 2 - Historical strategy backtesting with performance metrics",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"},
            "initial_capital": {"type": "number", "required": False, "description": "Initial capital", "default": 100000}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_backtests/{symbol}_backtest.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_011_backtesting.py"],
        "quality_score": 61.5,
        "quality_details": {
            "functionality": "有独特功能描述",
            "code_quality": "文件存在且可运行",
            "documentation": "描述:True, 参数:True, 示例:True",
            "usage": "低频使用 (1 次)",
            "maintenance": "有时间戳"
        }
    },
    "sa_012_report_generator": {
        "tool_id": "sa_012_report_generator",
        "name": "Report Generator",
        "description": "Stock Analysis Phase 2 - Comprehensive analysis reports with rating and recommendation",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {
            "symbol": {"type": "string", "required": False, "description": "Stock symbol", "default": "TEST"}
        },
        "validation": {"workspace_check": True, "output_file": "60-DATA/stock_reports/{symbol}_report_*.json"},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": ["sa_012_report_generator.py"],
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
registry['version'] = '1.11.32'
registry['last_updated'] = datetime.now().isoformat()

# Save registry
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Registry updated to v{registry['version']}")
print(f"Total tools: {len(tools)}")
print(f"Stock analysis tools: {[k for k in tools.keys() if k.startswith('sa_')]}")
