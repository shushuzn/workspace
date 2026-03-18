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
    """加载批判者审查模板 - 通用版"""
    return {
        # ===== 任务前审查 (所有任务通用) =====
        "pre_task": [
            "任务目标清晰可衡量 (有明确验收标准)",
            "任务必要性已论证 (为什么做这个)",
            "已有方案调研 (≥3 个参考/竞品/文献)",
            "风险评估完成 (技术/时间/依赖)",
            "资源需求明确 (时间/工具/权限)",
            "成功标准定义 (如何算完成)"
        ],
        
        # ===== 任务中审查 (所有任务通用) =====
        "mid_task": [
            "进度正常 (每 30% 检查一次)",
            "无致命问题阻塞",
            "偏离目标已记录并调整",
            "关键决策已文档化"
        ],
        
        # ===== 任务后审查 - 通用项 (所有任务) =====
        "post_task_common": [
            "致命问题 0 个",
            "严重问题≤2 个",
            "一般问题≤10 个",
            "验收标准 100% 满足",
            "代码/文档已提交 Git",
            "关键决策已记录到 MEMORY.md"
        ],
        
        # ===== 任务后审查 - 工具开发类 =====
        "post_task_tool": [
            "工具已创建并在实际工作流中使用",
            "使用次数≥1 次 (有证据证明)",
            "价值已量化 (时间节省/效率提升)",
            "使用案例已文档化",
            "工具文档完整 (README/使用说明)",
            "错误处理完善 (边界情况测试)"
        ],
        
        # ===== 任务后审查 - 研究分析类 =====
        "post_task_research": [
            "置信区间报告 (所有指标 95% CI)",
            "效应量报告 (Cohen's f² 或等价指标)",
            "统计功效分析 (Power≥0.8)",
            "多重共线性检验 (VIF<5)",
            "外部验证 (独立样本或交叉验证)",
            "可复现性 (代码 + 数据公开)"
        ],
        
        # ===== 任务后审查 - 文档编写类 =====
        "post_task_documentation": [
            "文档结构清晰 (目录/标题层级)",
            "关键信息前置 (执行摘要)",
            "示例/代码片段完整",
            "引用来源可验证",
            "格式统一 (命名/术语一致)",
            "长度适中 (<100 行或分页)"
        ],
        
        # ===== 任务后审查 - 代码优化类 =====
        "post_task_code": [
            "代码通过测试 (单元测试/集成测试)",
            "无安全漏洞 (敏感信息/注入风险)",
            "性能优化已验证 (基准测试)",
            "代码注释完整 (复杂逻辑说明)",
            "遵循代码规范 (PEP8/项目规范)",
            "无冗余代码 (DRY 原则)"
        ]
    }


def get_task_type(task_name: str, context: dict = None) -> str:
    """根据任务名称和上下文判断任务类型"""
    task_lower = task_name.lower()
    
    # 研究分析类 (优先匹配，避免与 tool 混淆)
    research_keywords = ['research', 'analysis', 'study', 'experiment', 'model', 'prediction', 'cnt-', 'conductivity']
    if any(kw in task_lower for kw in research_keywords):
        return 'research'
    
    # 文档编写类
    doc_keywords = ['doc', 'readme', 'guide', 'manual', 'note', 'memory', 'summary', 'index']
    if any(kw in task_lower for kw in doc_keywords):
        return 'documentation'
    
    # 工具开发类
    tool_keywords = ['tool', 'generator', 'search', 'auto-', 'script', 'utility', 'critic']
    if any(kw in task_lower for kw in tool_keywords):
        return 'tool'
    
    # 代码优化类
    code_keywords = ['optimize', 'refactor', 'fix', 'bug', 'performance', 'cleanup', 'hook']
    if any(kw in task_lower for kw in code_keywords):
        return 'code'
    
    # 默认：通用任务
    return 'general'


def generate_critic_review(task_name: str, phase: str, context: dict = None) -> dict:
    """生成批判者审查报告"""
    template = load_critic_template()
    task_type = get_task_type(task_name, context)
    
    review = {
        "task": task_name,
        "phase": phase,
        "task_type": task_type,
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
        # 通用检查项 (所有任务)
        checklist_items = template["post_task_common"].copy()
        
        # 根据任务类型添加专项检查项
        type_specific_key = f"post_task_{task_type}"
        if type_specific_key in template:
            checklist_items.extend(template[type_specific_key])
        
        review["checklist"] = [
            {"item": item, "checked": False, "notes": ""}
            for item in checklist_items
        ]
        review["status"] = "REQUIRES_REVIEW"
        review["message"] = "⚠️ 任务完成后必须完成批判者最终审查"
        review["task_type_info"] = f"任务类型：{task_type} (已加载专项检查项)"
    
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
    print(f"Task Type: {review.get('task_type', 'general')} (通用版)")
    print(f"Time: {review['timestamp'][:19]}")
    print(f"Status: {review['status']}")
    print(f"Checklist Items: {len(review['checklist'])}")
    print(f"\nReview saved to: {filepath}")
    
    if 'task_type_info' in review:
        print(f"\n📋 {review['task_type_info']}")
    
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
