#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Critic v5.0 - 日常笔记污染问题分析

问题：2026-03-18.md 包含历史总结 (457 行 → 38 行)
目标：防止再次发生
"""

import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'

print("="*60)
print("批判者 v5.0 - 日常笔记污染问题分析")
print("="*60)
print()

# 问题根因分析
print("【问题根因】")
print("-"*60)
print()

root_causes = [
    ("AI 偷懒", "直接复制 previous-summary 而非重新整理"),
    ("规则不清", "SOUL.md 未明确禁止历史总结"),
    ("无自动检查", "无工具验证日常笔记格式"),
    ("无大小限制", "未设置日常笔记行数/大小阈值"),
    ("概念混淆", "日常笔记 vs MEMORY.md 职责不清"),
]

for i, (cause, desc) in enumerate(root_causes, 1):
    print(f"{i}. {cause}: {desc}")

print()
print("【防护方案】")
print("-"*60)
print()

# 防护方案
solutions = [
    ("方案 1: Git Hook 检查", [
        "检查日常笔记行数 (>100 行警告)",
        "检查是否包含'历史总结'关键词",
        "检查是否包含'Previous Summary'关键词",
    ]),
    ("方案 2: pre-session-hook 增强", [
        "会话前检查昨日常笔记大小",
        "超过阈值自动警告",
        "提供清理建议",
    ]),
    ("方案 3: 日常笔记模板", [
        "创建 YYYY-MM-DD-template.md",
        "包含标准结构",
        "限制最大行数",
    ]),
    ("方案 4: SOUL.md 规则强化", [
        "明确禁止历史总结",
        "明确日常笔记职责",
        "添加示例对比",
    ]),
    ("方案 5: 自动清理工具", [
        "scan-daily-notes.py",
        "检测污染笔记",
        "提供清理建议",
    ]),
]

for solution, steps in solutions:
    print(f"【{solution}】")
    for step in steps:
        print(f"  - {step}")
    print()

print("【推荐实施顺序】")
print("-"*60)
print()
print("1. SOUL.md 规则强化 (立即)")
print("2. 日常笔记模板创建 (立即)")
print("3. pre-session-hook 增强 (今天)")
print("4. Git Hook 检查 (本周)")
print("5. 自动清理工具 (按需)")
print()

print("【批判者评分】")
print("-"*60)
print()
print(f"问题严重性：8/10 (违反核心原则)")
print(f"复发风险：7/10 (无防护会再次发生)")
print(f"防护必要性：9/10 (必须立即实施)")
print()

print("【立即行动】")
print("-"*60)
print()
print("1. 更新 SOUL.md - 添加日常笔记规则")
print("2. 创建日常笔记模板")
print("3. 增强 pre-session-hook.py")
print()
