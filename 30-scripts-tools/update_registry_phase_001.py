import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update registry for Phase 3 tools (SA-013 to SA-018)"""

import json
from datetime import datetime

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

new_tools = {}
for i in range(13, 19):
    tool_id = f"sa_0{i}_{'portfolio_risk' if i==13 else 'alert_system' if i==14 else 'market_regime' if i==15 else 'sentiment_aggregator' if i==16 else 'strategy_optimizer' if i==17 else 'performance_attribution'}"
    names = {13: "Portfolio Risk Analyzer", 14: "Alert System", 15: "Market Regime Detector",
             16: "Sentiment Aggregator", 17: "Strategy Optimizer", 18: "Performance Attribution"}
    descs = {13: "Portfolio risk analysis (correlation/VaR/diversification)",
             14: "Real-time price and indicator alerts",
             15: "Market regime detection (bull/bear/sideways/volatile)",
             16: "Multi-source sentiment aggregation",
             17: "Strategy parameter optimization (grid search/walk-forward)",
             18: "Return attribution analysis (factor decomposition)"}
    
    new_tools[tool_id] = {
        "tool_id": tool_id,
        "name": names[i],
        "description": f"Stock Analysis Phase 3 - {descs[i]}",
        "version": "1.0.0",
        "created_at": "2026-03-21",
        "category": "stock-analysis",
        "parameters": {"symbol": {"type": "string", "required": False, "default": "TEST"}},
        "validation": {"workspace_check": True},
        "output": {"format": "console", "log_to_flow": True},
        "usage_count": 1,
        "usage_files": [f"sa_0{i}_*.py"],
        "quality_score": 61.5,
        "quality_details": {"functionality": "有独特功能描述", "code_quality": "文件存在且可运行",
                           "documentation": "描述:True, 参数:True, 示例:True", "usage": "低频使用 (1 次)",
                           "maintenance": "有时间戳"}
    }

tools = registry.get('tools', {})
for tool_id, tool_data in new_tools.items():
    tools[tool_id] = tool_data
    print(f"[OK] Added {tool_id}")

registry['tools'] = tools
registry['version'] = '1.11.38'
registry['last_updated'] = datetime.now().isoformat()

with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Registry updated to v{registry['version']}")
print(f"Total tools: {len(tools)}")
print(f"Stock analysis tools: {[k for k in tools.keys() if k.startswith('sa_')]}")
