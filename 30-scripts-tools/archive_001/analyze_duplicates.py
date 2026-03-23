#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析工具重复 - 识别功能相似的脚本
"""

import os
from pathlib import Path
from collections import defaultdict

def main():
    tools_dir = Path("D:/OpenClaw/workspace/30-scripts-tools")
    files = [f.name for f in tools_dir.glob("*.py")]

    # 按功能分组
    categories = {
        "stock": [],
        "git": [],
        "archive": [],
        "workflow_guard": [],
        "workflow_add": [],
        "workflow_auto": [],
        "ai": [],
        "auto": [],
        "analyze": [],
        "test": [],
        "batch": [],
        "memory": [],
        "report": [],
        "export": [],
        "compare": [],
        "base": [],
        "session": [],
        "other": []
    }

    for f in sorted(files):
        name_lower = f.lower()
        if "stock_pro" in name_lower or "stock" in name_lower:
            categories["stock"].append(f)
        elif "git" in name_lower or "commit" in name_lower:
            categories["git"].append(f)
        elif "archive" in name_lower:
            categories["archive"].append(f)
        elif "guard" in name_lower:
            categories["workflow_guard"].append(f)
        elif name_lower.startswith("add_"):
            categories["workflow_add"].append(f)
        elif name_lower.startswith("auto_"):
            categories["workflow_auto"].append(f)
        elif "ai_" in name_lower or name_lower.startswith("ai_"):
            categories["ai"].append(f)
        elif "analyze" in name_lower:
            categories["analyze"].append(f)
        elif "test" in name_lower:
            categories["test"].append(f)
        elif "batch" in name_lower:
            categories["batch"].append(f)
        elif "memory" in name_lower or "distill" in name_lower:
            categories["memory"].append(f)
        elif "report" in name_lower:
            categories["report"].append(f)
        elif "export" in name_lower:
            categories["export"].append(f)
        elif "compare" in name_lower:
            categories["compare"].append(f)
        elif "base" in name_lower:
            categories["base"].append(f)
        elif "session" in name_lower:
            categories["session"].append(f)
        else:
            categories["other"].append(f)

    print("=" * 70)
    print("TOOL DUPLICATION ANALYSIS")
    print("=" * 70)
    print(f"\nTotal tools: {len(files)}")

    # 按数量排序
    sorted_cats = sorted(categories.items(), key=lambda x: -len(x[1]))

    print("\n" + "-" * 70)
    print("BY CATEGORY (sorted by count)")
    print("-" * 70)

    for cat, tools in sorted_cats:
        if tools:
            print(f"\n[{cat.upper()}] ({len(tools)} tools):")
            for t in tools:
                size = (tools_dir / t).stat().st_size
                print(f"  {t:45} {size:>8} bytes")

    # 找出可疑的重复
    print("\n" + "=" * 70)
    print("POTENTIAL DUPLICATES (需要人工检查)")
    print("=" * 70)

    # 同功能多版本
    for cat, tools in sorted_cats:
        if len(tools) > 2 and cat != "other":
            print(f"\n[WARNING] {cat}: {len(tools)} versions")
            for t in tools:
                print(f"  - {t}")

if __name__ == "__main__":
    main()
