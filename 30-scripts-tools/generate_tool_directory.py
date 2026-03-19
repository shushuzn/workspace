#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate Tool Directory - 生成工具目录

创建 Markdown 格式的工具目录，按分类组织
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
OUTPUT_DIR = Path("flow-archive/20260318-universal-workflow-001")

def generate_directory():
    """生成工具目录"""
    
    print("=" * 70)
    print("📚 生成工具目录")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 按分类组织
    by_category = {}
    for tool_id, tool in tools.items():
        cat = tool.get("category", "uncategorized")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append({
            "tool_id": tool_id,
            "name": tool.get("name", ""),
            "description": tool.get("description", ""),
            "file": tool.get("file", ""),
            "status": tool.get("status", "active"),
            "usage_count": tool.get("usage_count", 0)
        })
    
    # 生成 Markdown
    md_content = generate_markdown(by_category, registry)
    
    # 保存文件
    output_path = OUTPUT_DIR / "TOOL-DIRECTORY.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✅ 目录已生成：{output_path}")
    
    # 统计
    total_tools = sum(len(tools) for tools in by_category.values())
    total_categories = len(by_category)
    
    print(f"\n📊 统计:")
    print(f"  总工具数：{total_tools}")
    print(f"  总分类数：{total_categories}")
    print(f"  平均每类：{total_tools/total_categories:.1f} 个")
    
    print("\n" + "=" * 70)
    print("✅ 完成!")
    print("=" * 70)
    
    return True

def generate_markdown(by_category, registry):
    """生成 Markdown 内容"""
    
    lines = []
    
    # 标题
    lines.append("# 📚 工具目录 Tool Directory")
    lines.append("")
    lines.append(f"**版本:** {registry.get('version', 'unknown')}")  
    lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**总工具数:** {registry.get('total_tools', 0)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 分类统计
    lines.append("## 📊 分类统计")
    lines.append("")
    lines.append("| 分类 | 工具数 | 占比 |")
    lines.append("|------|--------|------|")
    
    total = sum(len(tools) for tools in by_category.values())
    for cat, cat_tools in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(cat_tools)
        pct = count / total * 100
        lines.append(f"| {cat} | {count} | {pct:.1f}% |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 详细列表
    lines.append("## 📋 工具列表")
    lines.append("")
    
    for cat, cat_tools in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        # 分类标题
        lines.append(f"### {cat} ({len(cat_tools)} 个)")
        lines.append("")
        
        # 按使用次数排序
        cat_tools_sorted = sorted(cat_tools, key=lambda x: x["usage_count"], reverse=True)
        
        # 工具表格
        lines.append("| 工具 ID | 名称 | 描述 | 使用次数 | 状态 |")
        lines.append("|---------|------|------|----------|------|")
        
        for tool in cat_tools_sorted[:50]:  # 每类最多显示 50 个
            tool_id = tool["tool_id"]
            name = tool["name"] or "-"
            desc = (tool["description"] or "-")[:50]
            if len(tool["description"] or "") > 50:
                desc += "..."
            usage = tool["usage_count"]
            status = tool["status"]
            
            # 状态图标
            if status == "active":
                status_icon = "✅"
            elif status == "deprecated_candidate":
                status_icon = "⚠️"
            elif status == "deprecated":
                status_icon = "❌"
            else:
                status_icon = "📦"
            
            lines.append(f"| `{tool_id}` | {name} | {desc} | {usage} | {status_icon} |")
        
        if len(cat_tools) > 50:
            lines.append(f"")
            lines.append(f"*... 还有 {len(cat_tools) - 50} 个工具*")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # 附录
    lines.append("## 📝 说明")
    lines.append("")
    lines.append("### 状态说明")
    lines.append("")
    lines.append("- ✅ active: 活跃工具")
    lines.append("- ⚠️  deprecated_candidate: 废弃候选 (需审查)")
    lines.append("- ❌ deprecated: 已废弃")
    lines.append("- 📦 unknown: 未知状态")
    lines.append("")
    lines.append("### 使用次数")
    lines.append("")
    lines.append("基于代码库扫描统计，反映工具使用频率")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**最后更新:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return "\n".join(lines)

if __name__ == '__main__':
    generate_directory()
