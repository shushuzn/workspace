#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Subdivide General Category - 细分 general 类

将 222 个 general 类工具细分为更具体的分类
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 细分规则 (关键词 → 新分类)
SUBDIVISION_RULES = {
    # 报告相关
    "report": "reporting",
    "summary": "reporting",
    "changelog": "reporting",
    "document": "documentation",
    "doc": "documentation",
    
    # 监控相关
    "monitor": "monitoring",
    "health": "monitoring",
    "check": "quality",
    "verify": "quality",
    "validate": "quality",
    "quality": "quality",
    "critic": "quality",
    "review": "quality",
    
    # Git 相关
    "git": "git",
    "commit": "git",
    "push": "git",
    
    # 会话相关
    "session": "session",
    "compress": "memory",
    "distill": "memory",
    "memory": "memory",
    "memo": "memory",
    
    # 优化相关
    "optimize": "optimization",
    "performance": "performance",
    "speed": "performance",
    "cache": "cache",
    "accelerate": "optimization",
    
    # 工作流相关
    "workflow": "workflow",
    "flow": "workflow",
    "pipeline": "workflow",
    "stage": "workflow",
    "step": "workflow",
    
    # 自动化相关
    "auto": "automation",
    "batch": "automation",
    "schedule": "automation",
    "trigger": "automation",
    
    # 分析相关
    "analyze": "analysis",
    "scan": "analysis",
    "detect": "analysis",
    "inspect": "analysis",
    
    # 工具相关
    "tool": "tool",
    "util": "utility",
    "helper": "utility",
    "manage": "utility",
    "register": "utility",
    
    # UI 相关
    "ui": "ui",
    "dashboard": "ui",
    "visual": "ui",
    "display": "ui",
    
    # 集成相关
    "integration": "integration",
    "connect": "integration",
    "sync": "integration",
    "import": "integration",
    "export": "integration",
    
    # 安全相关
    "security": "security",
    "auth": "security",
    "permission": "security",
    
    # 任务相关
    "task": "task",
    "job": "task",
    
    # 头脑风暴相关
    "brainstorm": "brainstorm",
    "ideate": "brainstorm",
    
    # 知识图谱相关
    "kg": "kg",
    "knowledge": "kg",
    "graph": "kg",
    
    # 执行相关
    "execute": "execution",
    "run": "execution",
    "invoke": "execution",
    
    # 上下文相关
    "context": "context",
    "load": "context",
    
    # 测试相关
    "test": "testing",
    "debug": "testing",
    
    # 备份相关
    "backup": "backup",
    "restore": "backup",
    
    # 交互相关
    "interact": "interaction",
    "prompt": "interaction",
    
    # 学习相关
    "learn": "learning",
    "train": "learning",
    "adapt": "learning",
}

def subdivide_general():
    """细分 general 类"""
    
    print("=" * 70)
    print("📂 细分 general 类")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 找到 general 类工具
    general_tools = []
    for tool_id, tool in tools.items():
        if tool.get("category") == "general":
            general_tools.append({
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "description": tool.get("description", "")
            })
    
    print(f"\n📊 general 类工具：{len(general_tools)} 个")
    
    # 重新分类
    reclassified = 0
    new_categories = {}
    
    for tool in general_tools:
        tool_id = tool["tool_id"]
        text = f"{tool_id} {tool['name']} {tool['description']}".lower()
        
        # 找到最佳匹配
        best_category = None
        best_score = 0
        
        for keyword, category in SUBDIVISION_RULES.items():
            if keyword in text:
                score = text.count(keyword)
                if score > best_score:
                    best_score = score
                    best_category = category
        
        # 如果有匹配，更新分类
        if best_category:
            tools[tool_id]["category"] = best_category
            tools[tool_id]["recategorized_at"] = datetime.now().isoformat()
            tools[tool_id]["recategorized_from"] = "general"
            
            new_categories[best_category] = new_categories.get(best_category, 0) + 1
            reclassified += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.7.9"
    registry["updated_at"] = datetime.now().isoformat()
    
    # 统计新分布
    category_counts = {}
    for tool in tools.values():
        cat = tool.get("category", "uncategorized")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    registry["category_distribution"] = category_counts
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("📊 重新分类统计")
    print("=" * 70)
    
    print(f"\n重新分类：{reclassified}/{len(general_tools)} 个 ({reclassified/len(general_tools)*100:.1f}%)")
    
    print(f"\n新分类分布 (Top 15):")
    for cat, count in sorted(new_categories.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {cat}: {count} 个")
    
    # 计算剩余 general 类
    remaining_general = category_counts.get("general", 0)
    print(f"\n📊 general 类变化：{len(general_tools)} → {remaining_general} (-{len(general_tools) - remaining_general}, {-(len(general_tools) - remaining_general)/len(general_tools)*100:.1f}%)")
    
    # 保存报告
    report = {
        "subdivision_date": datetime.now().isoformat(),
        "original_general_count": len(general_tools),
        "reclassified_count": reclassified,
        "remaining_general": remaining_general,
        "new_categories": new_categories,
        "reduction_percentage": (len(general_tools) - remaining_general) / len(general_tools) * 100
    }
    
    report_path = Path("flow-archive/20260318-universal-workflow-001/general-subdivision.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存")
    
    print("\n" + "=" * 70)
    print("✅ general 类细分完成!")
    print("=" * 70)
    
    return report

if __name__ == '__main__':
    subdivide_general()
