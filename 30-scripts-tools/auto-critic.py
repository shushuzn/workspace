#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Critic v5.0 - 自动批判者调用工具

功能:
- 任务开始时自动调用批判者审查
- 任务进行中自动监控 (每 30%)
- 任务完成后自动最终审查
- 生成批判者报告并保存到 daily note

使用:
  py auto-critic.py --task "任务名称" --phase start|mid|final
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'
MEMORY_DIR = WORKSPACE / '13-memory'


def load_critic_template() -> dict:
    """加载批判者审查模板"""
    return {
        "pre_task": [
            "研究问题有科学意义 (≥3 篇文献支持)",
            "样本量先验功效分析 (Power≥0.95)",
            "特征文献依据 (每个≥3 篇)",
            "VIF 预分析 (<3)",
            "验证方案 (5×5×5 嵌套 CV+10000Bootstrap)",
            "外部验证方案 (真正独立≥50 样本)"
        ],
        "mid_task": [
            "数据质量 (缺失值<2%, VIF<3)",
            "进度正常 (每 30% 检查一次)",
            "无致命问题"
        ],
        "post_task": [
            "致命问题 0 个",
            "严重问题≤2 个",
            "一般问题≤10 个",
            "置信区间报告 (所有指标 95% CI)",
            "效应量报告 (Cohen's f²)",
            "统计功效 (Power≥0.95)",
            "VIF 检验 (全部<3)",
            "外部验证 (真正独立≥50 样本)",
            "SHAP 分析 (p<0.001+95%CI)",
            "GitHub 公开 + 第三方复现"
        ],
        "tool_usage": [
            "工具已创建并在实际工作流中使用",
            "使用时间≥1 次",
            "价值已量化 (时间节省/效率提升)",
            "使用案例已文档化"
        ]
    }


def generate_critic_review(task_name: str, phase: str, context: dict = None) -> dict:
    """生成批判者审查报告"""
    template = load_critic_template()
    
    review = {
        "task": task_name,
        "phase": phase,
        "timestamp": datetime.now().isoformat(),
        "checklist": [],
        "score": 0,
        "status": "PENDING"
    }
    
    if phase == "start":
        review["checklist"] = [
            {"item": item, "checked": False, "notes": ""}
            for item in template["pre_task"]
        ]
        review["status"] = "REQUIRES_REVIEW"
        review["message"] = "⚠️ 任务开始前必须完成批判者设计审查"
        
    elif phase == "mid":
        review["checklist"] = [
            {"item": item, "checked": False, "notes": ""}
            for item in template["mid_task"]
        ]
        review["status"] = "REQUIRES_REVIEW"
        review["message"] = "⚠️ 任务进行中必须完成批判者中期检查"
        
    elif phase == "final":
        review["checklist"] = [
            {"item": item, "checked": False, "notes": ""}
            for item in template["post_task"] + template["tool_usage"]
        ]
        review["status"] = "REQUIRES_REVIEW"
        review["message"] = "⚠️ 任务完成后必须完成批判者最终审查"
    
    return review


def save_critic_review(review: dict, task_name: str) -> Path:
    """保存批判者审查报告"""
    # 清理任务名称中的非法字符
    safe_name = task_name.replace(" ", "-").replace('"', '').replace("'", '').lower()[:50]
    filename = f"critic-auto-{safe_name}.json"
    filepath = SCRIPTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(review, f, indent=2, ensure_ascii=False)
    
    return filepath


def update_daily_note(review: dict, daily_note_path: Path):
    """更新当日笔记添加批判者审查记录"""
    if not daily_note_path.exists():
        return
    
    content = daily_note_path.read_text(encoding='utf-8')
    
    # 检查是否已有批判者审查部分
    critic_section = f"""
---

## 🎯 Critic v5.0 Auto-Review

**Task:** {review['task']}
**Phase:** {review['phase']}
**Time:** {review['timestamp'][:19]}
**Status:** {review['status']}

**Checklist:**
"""
    
    for item in review['checklist']:
        checked = "✅" if item['checked'] else "❌"
        critic_section += f"- [{checked}] {item['item']}\n"
    
    if 'message' in review:
        critic_section += f"\n**Message:** {review['message']}\n"
    
    # 添加到笔记末尾
    content = content.rstrip() + "\n" + critic_section
    
    daily_note_path.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Auto-Critic v5.0')
    parser.add_argument('--task', '-t', required=True, help='任务名称')
    parser.add_argument('--phase', '-p', required=True, choices=['start', 'mid', 'final'], help='审查阶段')
    parser.add_argument('--context', '-c', help='上下文 JSON 文件')
    parser.add_argument('--auto-update-daily', action='store_true', help='自动更新当日笔记')
    
    args = parser.parse_args()
    
    # 加载上下文 (如果有)
    context = None
    if args.context:
        context_path = Path(args.context)
        if context_path.exists():
            with open(context_path, 'r', encoding='utf-8') as f:
                context = json.load(f)
    
    # 生成批判者审查
    review = generate_critic_review(args.task, args.phase, context)
    
    # 保存审查报告
    filepath = save_critic_review(review, args.task)
    
    # 输出结果
    print("=" * 60)
    print(f"[CRITIC v5.0] Auto-Review - {args.phase.upper()}")
    print("=" * 60)
    print(f"\nTask: {review['task']}")
    print(f"Phase: {review['phase']}")
    print(f"Time: {review['timestamp'][:19]}")
    print(f"Status: {review['status']}")
    print(f"\nReview saved to: {filepath}")
    
    if 'message' in review:
        print(f"\n⚠️  {review['message']}")
    
    print("\nChecklist:")
    for i, item in enumerate(review['checklist'], 1):
        checked = "✓" if item['checked'] else " "
        print(f"  [{checked}] {i}. {item['item']}")
    
    # 自动更新当日笔记
    if args.auto_update_daily:
        today = datetime.now().strftime('%Y-%m-%d')
        daily_note = MEMORY_DIR / f"{today}.md"
        update_daily_note(review, daily_note)
        print(f"\n[OK] Updated daily note: {daily_note}")
    
    print("\n" + "=" * 60)
    print("[USER-004] 批判者审查已自动调用 - 必须完成所有检查项")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
