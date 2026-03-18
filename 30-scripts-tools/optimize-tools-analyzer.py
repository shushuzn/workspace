#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具优化分析器
扫描 30-scripts-tools，识别重复、冗余、低效工具
"""

import os
import sys
import io
from pathlib import Path
from collections import defaultdict
import hashlib

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path(__file__).parent.parent / "30-scripts-tools"

def scan_tools():
    """扫描所有工具"""
    print("="*60)
    print("🔍 工具优化分析")
    print("="*60)
    
    tools = list(TOOLS_DIR.glob("*.py"))
    print(f"\n📦 总工具数：{len(tools)} 个")
    
    # 1. 按文件大小分析
    print("\n" + "="*60)
    print("📊 按文件大小分类")
    print("="*60)
    
    size_categories = {
        '微型 (<1KB)': [],
        '小型 (1-5KB)': [],
        '中型 (5-20KB)': [],
        '大型 (20-50KB)': [],
        '超大型 (>50KB)': []
    }
    
    for tool in tools:
        size = tool.stat().st_size
        if size < 1024:
            size_categories['微型 (<1KB)'].append((tool, size))
        elif size < 5*1024:
            size_categories['小型 (1-5KB)'].append((tool, size))
        elif size < 20*1024:
            size_categories['中型 (5-20KB)'].append((tool, size))
        elif size < 50*1024:
            size_categories['大型 (20-50KB)'].append((tool, size))
        else:
            size_categories['超大型 (>50KB)'].append((tool, size))
    
    for category, items in size_categories.items():
        print(f"\n{category}: {len(items)} 个")
        if items:
            for tool, size in sorted(items, key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {tool.name} ({size/1024:.1f}KB)")
    
    # 2. 识别重复工具（按功能名）
    print("\n" + "="*60)
    print("🔍 识别重复工具")
    print("="*60)
    
    name_groups = defaultdict(list)
    for tool in tools:
        # 提取基础名称（去掉版本号）
        base_name = tool.stem.lower()
        # 移除 _v1, _v2, _v3, _new, _old, _backup 等后缀
        for suffix in ['_v1', '_v2', '_v3', '_v4', '_v5', '_new', '_old', '_backup', '_fixed', '_final']:
            base_name = base_name.replace(suffix, '')
        base_name = base_name.rstrip('_')
        name_groups[base_name].append(tool)
    
    duplicates = {k: v for k, v in name_groups.items() if len(v) > 1}
    
    print(f"\n发现 {len(duplicates)} 组重复工具:")
    for base_name, tool_list in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  {base_name} ({len(tool_list)} 个版本):")
        for tool in tool_list:
            size = tool.stat().st_size
            print(f"    - {tool.name} ({size/1024:.1f}KB)")
    
    # 3. 识别低效工具（大文件 + 多版本）
    print("\n" + "="*60)
    print("⚠️  低效工具识别")
    print("="*60)
    
    # 超大文件
    large_tools = [(t, t.stat().st_size) for t in tools if t.stat().st_size > 50*1024]
    print(f"\n超大文件 (>50KB): {len(large_tools)} 个")
    for tool, size in sorted(large_tools, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {tool.name} ({size/1024:.1f}KB)")
    
    # 测试文件过多
    test_tools = [t for t in tools if t.name.lower().startswith('test_')]
    print(f"\n测试工具：{len(test_tools)} 个")
    if test_tools:
        print("  建议：合并为少数综合测试文件")
    
    # 4. 优化建议
    print("\n" + "="*60)
    print("💡 优化建议")
    print("="*60)
    
    total_size = sum(t.stat().st_size for t in tools)
    print(f"\n总大小：{total_size/1024:.1f}KB ({total_size/1024/1024:.2f}MB)")
    
    # 计算可节省空间
    potential_savings = 0
    for base_name, tool_list in duplicates.items():
        if len(tool_list) > 1:
            # 保留最大的，其他可删除
            sizes = [t.stat().st_size for t in tool_list]
            potential_savings += sum(sorted(sizes)[:-1])
    
    print(f"\n潜在优化空间:")
    print(f"  - 重复工具可节省：{potential_savings/1024:.1f}KB")
    print(f"  - 建议优先级：")
    print(f"    1. 合并多版本工具 (v1/v2/v3 → 单一版本)")
    print(f"    2. 删除测试文件 (或移到 92-tests/)")
    print(f"    3. 压缩超大文件 (>50KB)")
    
    # 5. 生成优化清单
    print("\n" + "="*60)
    print("📋 优化清单")
    print("="*60)
    
    optimization_list = []
    
    # 多版本合并
    for base_name, tool_list in duplicates.items():
        if len(tool_list) >= 2:
            optimization_list.append({
                'type': '合并版本',
                'target': f"{base_name}_*.py",
                'count': len(tool_list),
                'action': f"保留最新版本，删除旧版本"
            })
    
    # 测试文件迁移
    if len(test_tools) > 5:
        optimization_list.append({
            'type': '迁移测试',
            'target': f"test_*.py ({len(test_tools)}个)",
            'count': len(test_tools),
            'action': f"移动到 92-tests/ 目录"
        })
    
    # 超大文件
    for tool, size in large_tools[:5]:
        optimization_list.append({
            'type': '压缩代码',
            'target': tool.name,
            'count': 1,
            'action': f"重构优化 ({size/1024:.1f}KB)"
        })
    
    for i, opt in enumerate(optimization_list[:15], 1):
        print(f"\n{i}. {opt['type']}: {opt['target']}")
        print(f"   数量：{opt['count']} 个")
        print(f"   行动：{opt['action']}")
    
    print("\n" + "="*60)
    print("✅ 分析完成！")
    print("="*60)

if __name__ == "__main__":
    scan_tools()
