#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Scheduler - 工作流模板调度器

功能:
1. 加载模板库
2. 根据任务类型自动选择模板
3. 调度子工作流执行
4. 模板状态管理

Usage:
    py workflow_scheduler.py --list-templates          # 列出所有模板
    py workflow_scheduler.py --select <template_id>    # 选择模板
    py workflow_scheduler.py --auto <task_type>        # 自动选择
    py workflow_scheduler.py --show <template_id>      # 显示模板详情
"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
TEMPLATE_DIR = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001" / "templates"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def load_template(template_id):
    """加载模板"""
    template_file = TEMPLATE_DIR / f"{template_id}.json"
    
    if not template_file.exists():
        return None
    
    with open(template_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_templates():
    """列出所有模板"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}工作流模板库{Colors.RESET}")
    print("=" * 70)
    
    if not TEMPLATE_DIR.exists():
        print(f"{Colors.RED}❌ 模板目录不存在{Colors.RESET}")
        return
    
    templates = []
    for file in TEMPLATE_DIR.glob("*.json"):
        template = load_template(file.stem)
        if template:
            templates.append(template)
    
    if not templates:
        print(f"{Colors.YELLOW}⚠️  暂无模板{Colors.RESET}")
        return
    
    for t in templates:
        print(f"\n{Colors.BOLD}{t['template_id']}{Colors.RESET} - {t['name']}")
        print(f"  描述：{t['description']}")
        print(f"  步骤：{t['total_steps']} 步")
        print(f"  预计：{t['estimated_time']}")
        print(f"  交付物：{len(t['deliverables'])} 个")
    
    print(f"\n{Colors.GREEN}✅ 共 {len(templates)} 个模板{Colors.RESET}")
    print("=" * 70)

def show_template(template_id):
    """显示模板详情"""
    template = load_template(template_id)
    
    if not template:
        print(f"{Colors.RED}❌ 模板不存在：{template_id}{Colors.RESET}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{template['name']}{Colors.RESET}")
    print(f"ID: {template['template_id']}")
    print(f"版本：{template['version']}")
    print(f"描述：{template['description']}")
    print(f"步骤：{template['total_steps']} 步")
    print(f"预计：{template['estimated_time']}")
    
    print(f"\n{Colors.BOLD}步骤清单:{Colors.RESET}")
    print("-" * 70)
    for step in template['steps']:
        blocker = "🔴" if step['blocker'] else "🟢"
        print(f"  Step {step['step']}: {step['name']} {blocker}")
        print(f"           工具：{step.get('tool', 'N/A')}")
        print(f"           说明：{step['description']}")
    
    print(f"\n{Colors.BOLD}质量门禁:{Colors.RESET}")
    qg = template.get('quality_gates', {})
    for step_id, gates in qg.items():
        print(f"  Step {step_id}:")
        print(f"    致命问题：0 个")
        print(f"    严重问题：≤{gates.get('severe_issues', 'N/A')} 个")
        print(f"    一般问题：≤{gates.get('minor_issues', 'N/A')} 个")
        print(f"    最低评分：≥{gates.get('min_score', 'N/A')}")
    
    print(f"\n{Colors.BOLD}交付物:{Colors.RESET}")
    for item in template['deliverables']:
        print(f"  - {item}")
    
    print()

def auto_select(task_type):
    """根据任务类型自动选择模板"""
    # 任务类型映射
    task_mapping = {
        'research': 'research-001',
        'study': 'research-001',
        'analysis': 'research-001',
        'experiment': 'research-001',
        'project': 'project-001',
        'develop': 'project-001',
        'code': 'project-001',
        'fix': 'project-001',
        'feature': 'project-001',
        'doc': 'doc-001',
        'document': 'doc-001',
        'report': 'doc-001',
        'article': 'doc-001',
        'write': 'doc-001',
    }
    
    # 查找匹配
    template_id = None
    for key, tid in task_mapping.items():
        if key in task_type.lower():
            template_id = tid
            break
    
    if template_id:
        template = load_template(template_id)
        if template:
            print(f"\n{Colors.GREEN}✅ 自动匹配模板：{template['name']}{Colors.RESET}")
            print(f"   ID: {template['template_id']}")
            print(f"   步骤：{template['total_steps']} 步")
            print(f"   预计：{template['estimated_time']}")
            return template_id
    
    print(f"\n{Colors.YELLOW}⚠️  未找到匹配模板，使用默认工作流{Colors.RESET}")
    return None

def select_template(template_id):
    """选择模板"""
    template = load_template(template_id)
    
    if not template:
        print(f"{Colors.RED}❌ 模板不存在：{template_id}{Colors.RESET}")
        return False
    
    print(f"\n{Colors.GREEN}✅ 已选择模板：{template['name']}{Colors.RESET}")
    print(f"   ID: {template['template_id']}")
    print(f"   步骤：{template['total_steps']} 步")
    print(f"   预计：{template['estimated_time']}")
    
    # 保存选择
    checkpoint_file = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001" / "checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        checkpoint['selected_template'] = template_id
        checkpoint['template_name'] = template['name']
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Colors.GREEN}✅ 模板选择已保存{Colors.RESET}")
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Scheduler - 模板调度器')
    parser.add_argument('--list-templates', action='store_true', help='列出所有模板')
    parser.add_argument('--select', type=str, help='选择模板')
    parser.add_argument('--auto', type=str, help='自动选择模板')
    parser.add_argument('--show', type=str, help='显示模板详情')
    
    args = parser.parse_args()
    
    if args.list_templates:
        list_templates()
    elif args.select:
        select_template(args.select)
    elif args.auto:
        auto_select(args.auto)
    elif args.show:
        show_template(args.show)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
