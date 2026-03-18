#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Critic v7.0 - Enhanced with Issue Detection & Remediation

核心升级 (vs v6.0):
1. 主动问题检测 - 不再依赖假设，使用 issue_scanner 和 critical_issue_detector
2. 检查项分级 - BLOCKER (阻断) / WARNING (警告) / INFO (提示)
3. 整改闭环 - 自动创建整改任务，跟踪进度
4. 质量门禁 - 代码质量、安全、复杂度检查
5. 规则适配 - 区分新增工具和存量工具

Usage:
    py auto-critic_v7.py -t "Task-Name" -p start|mid|final
    py auto-critic_v7.py -t "Task-Name" --create-remediation
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import re

# 导入新组件
sys.path.insert(0, str(Path(__file__).parent))
try:
    from issue_scanner import IssueScanner
    from critical_issue_detector import CriticalIssueDetector
    from remediation_tracker import RemediationTracker
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Components not available: {e}")
    COMPONENTS_AVAILABLE = False

# 内存目录
MEMORY_DIR = Path("13-memory")
SCRIPTS_DIR = Path("30-scripts-tools")
DOCS_DIR = Path("15-docs")
WORKSPACE = Path(__file__).parent.parent


# ============== v7.0 检查项定义 ==============

CHECKLIST_V7 = {
    # BLOCKER 红线项 (必须通过，否则阻断)
    "blocker": [
        {
            "id": "blocker-001",
            "item": "致命问题 0 个",
            "check": "check_fatal_issues",
            "blocking": True
        },
        {
            "id": "blocker-002",
            "item": "工作区正确性 (D:\\OpenClaw\\workspace)",
            "check": "check_workspace",
            "blocking": True
        },
        {
            "id": "blocker-003",
            "item": "代码/文档已提交 Git",
            "check": "check_git_commit",
            "blocking": True
        },
        {
            "id": "blocker-004",
            "item": "【USER-004】批判者自动调用",
            "check": "check_critic_auto_called",
            "blocking": True
        },
        {
            "id": "blocker-005",
            "item": "【ZS-001】无工具多份定义",
            "check": "check_unique_tool_ids",
            "blocking": True
        },
        {
            "id": "blocker-006",
            "item": "【ZS-002】工作流无硬编码命令",
            "check": "check_no_hardcoded_commands",
            "blocking": True
        },
    ],
    
    # WARNING 警告项 (不阻断，但需整改)
    "warning": [
        {
            "id": "warning-001",
            "item": "严重问题≤2 个",
            "check": "check_critical_issues_count",
            "blocking": False,
            "remediation_days": 3
        },
        {
            "id": "warning-002",
            "item": "一般问题≤10 个",
            "check": "check_minor_issues_count",
            "blocking": False,
            "remediation_days": 7
        },
        {
            "id": "warning-003",
            "item": "【AGENTS.md】当日笔记压缩 (<100 行)",
            "check": "check_daily_note_lines",
            "blocking": False,
            "remediation_days": 1
        },
        {
            "id": "warning-004",
            "item": "【AGENTS.md】会话压缩执行",
            "check": "check_session_compression",
            "blocking": False,
            "remediation_days": 1
        },
        {
            "id": "warning-005",
            "item": "【ZS-006】工具有效使用 (新增工具)",
            "check": "check_new_tool_usage",
            "blocking": False,
            "remediation_days": 2
        },
        {
            "id": "warning-006",
            "item": "代码质量检查 (pylint/flake8)",
            "check": "check_code_quality",
            "blocking": False,
            "remediation_days": 7
        },
        {
            "id": "warning-007",
            "item": "安全检查 (无高危漏洞)",
            "check": "check_security_scan",
            "blocking": False,
            "remediation_days": 3
        },
    ],
    
    # INFO 提示项 (不强制)
    "info": [
        {
            "id": "info-001",
            "item": "文档结构清晰",
            "check": "check_documentation_structure",
            "blocking": False
        },
        {
            "id": "info-002",
            "item": "单元测试覆盖率",
            "check": "check_test_coverage",
            "blocking": False
        },
    ]
}


# ============== 检查函数 ==============

def check_workspace() -> tuple:
    """检查是否在正确的工作区"""
    cwd = os.getcwd()
    passed = "D:\\OpenClaw\\workspace" in cwd or "D:/OpenClaw/workspace" in cwd
    evidence = f"os.getcwd() = {cwd}"
    return passed, evidence

def check_fatal_issues() -> tuple:
    """检查致命问题 (使用 critical_issue_detector)"""
    if not COMPONENTS_AVAILABLE:
        return False, "Components not available"
    
    detector = CriticalIssueDetector(WORKSPACE)
    result = detector.detect_all()
    
    passed = result.critical_count == 0
    evidence = f"Critical issues: {result.critical_count}"
    return passed, evidence

def check_git_commit() -> tuple:
    """检查 Git 提交"""
    try:
        # 检查未提交更改
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10
        )
        
        uncommitted = [line for line in result.stdout.strip().split('\n') if line and not line.startswith('??')]
        
        # 检查最近提交
        result = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10
        )
        
        last_commit = result.stdout.strip()
        
        passed = len(uncommitted) == 0
        evidence = f"Uncommitted: {len(uncommitted)} | Last commit: {last_commit}"
        return passed, evidence
    
    except Exception as e:
        return False, f"Error: {e}"

def check_critic_auto_called() -> tuple:
    """检查批判者是否自动调用"""
    # 检查 critic review 文件
    critic_files = list(SCRIPTS_DIR.glob("critic-auto-*.json"))
    
    if not critic_files:
        return False, "No critic review file found"
    
    # 检查最新文件
    latest = max(critic_files, key=lambda f: f.stat().st_mtime)
    
    try:
        data = json.loads(latest.read_text(encoding='utf-8'))
        passed = data.get('status') != 'FAIL' or data.get('score', 0) >= 95
        evidence = f"Latest review: {latest.name}, Score: {data.get('score', 'N/A')}"
        return passed, evidence
    except:
        return False, f"Failed to read {latest.name}"

def check_unique_tool_ids() -> tuple:
    """检查工具 ID 唯一性"""
    registry_file = SCRIPTS_DIR / "tools_registry.json"
    
    if not registry_file.exists():
        return False, "tools_registry.json not found"
    
    try:
        data = json.loads(registry_file.read_text(encoding='utf-8'))
        tools = data.get('tools', {})
        tool_ids = list(tools.keys())
        
        # 检查重复
        unique_ids = set(tool_ids)
        passed = len(tool_ids) == len(unique_ids)
        evidence = f"Unique tool_ids: {len(unique_ids)}"
        return passed, evidence
    except Exception as e:
        return False, f"Error: {e}"

def check_no_hardcoded_commands() -> tuple:
    """检查工作流无硬编码命令"""
    workflow_files = list((SCRIPTS_DIR / "workflows").glob("*.json"))
    
    hardcoded_found = []
    for wf in workflow_files:
        try:
            content = wf.read_text(encoding='utf-8')
            if re.search(r"py\s+30-scripts", content):
                hardcoded_found.append(wf.name)
        except:
            continue
    
    passed = len(hardcoded_found) == 0
    evidence = f"Hardcoded commands: {len(hardcoded_found)}" + (f" in {hardcoded_found}" if hardcoded_found else "")
    return passed, evidence

def check_critical_issues_count() -> tuple:
    """检查严重问题数量"""
    if not COMPONENTS_AVAILABLE:
        return False, "Components not available"
    
    detector = CriticalIssueDetector(WORKSPACE)
    result = detector.detect_all()
    
    passed = result.high_count <= 2
    evidence = f"High risk issues: {result.high_count}"
    return passed, evidence

def check_minor_issues_count() -> tuple:
    """检查一般问题数量"""
    if not COMPONENTS_AVAILABLE:
        return False, "Components not available"
    
    scanner = IssueScanner(WORKSPACE)
    result = scanner.scan_all()
    
    passed = result.minor_count <= 10
    evidence = f"Minor issues: {result.minor_count}"
    return passed, evidence

def check_daily_note_lines() -> tuple:
    """检查当日笔记行数"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_note = MEMORY_DIR / f"{today}.md"
    
    if not daily_note.exists():
        return False, "Daily note not found"
    
    lines = daily_note.read_text(encoding='utf-8').split('\n')
    passed = len(lines) < 100
    evidence = f"File: {daily_note.name} | Lines: {len(lines)}"
    return passed, evidence

def check_session_compression() -> tuple:
    """检查会话压缩执行"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_note = MEMORY_DIR / f"{today}.md"
    
    if not daily_note.exists():
        return False, "Daily note not found"
    
    content = daily_note.read_text(encoding='utf-8')
    passed = "Session Summary" in content or "session_summary" in content.lower()
    evidence = "Has session summary" if passed else "No session summary found"
    return passed, evidence

def check_new_tool_usage() -> tuple:
    """检查新增工具使用情况"""
    # 获取最近提交中新增的工具
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-status', 'HEAD~3'],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10
        )
        
        new_tools = []
        for line in result.stdout.split('\n'):
            if line.startswith('A') and '30-scripts-tools/' in line and line.endswith('.py'):
                tool_name = Path(line.split('\t')[1]).stem
                new_tools.append(tool_name)
        
        if not new_tools:
            return True, "No new tools in recent commits"
        
        # 检查工作流引用
        workflow_files = list((SCRIPTS_DIR / "workflows").glob("*.json"))
        used_tools = set()
        
        for wf in workflow_files:
            try:
                data = json.loads(wf.read_text(encoding='utf-8'))
                for step in data.get('steps', []):
                    if 'tool_id' in step:
                        used_tools.add(step['tool_id'])
            except:
                continue
        
        # 检查新增工具是否被使用
        unused = [t for t in new_tools if t.replace('_', '-') not in used_tools]
        passed = len(unused) == 0
        evidence = f"New tools: {new_tools} | Used: {list(used_tools & set(new_tools))}" + (f" | Unused: {unused}" if unused else "")
        return passed, evidence
    
    except Exception as e:
        return False, f"Error: {e}"

def check_code_quality() -> tuple:
    """检查代码质量"""
    if not COMPONENTS_AVAILABLE:
        return False, "Components not available"
    
    scanner = IssueScanner(WORKSPACE / "30-scripts-tools")
    result = scanner.scan_all()
    
    # 检查 pylint/flake8 问题
    quality_issues = [i for i in result.issues if i.category in ['pylint', 'flake8']]
    passed = len(quality_issues) <= 5
    evidence = f"Quality issues: {len(quality_issues)}"
    return passed, evidence

def check_security_scan() -> tuple:
    """安全检查"""
    if not COMPONENTS_AVAILABLE:
        return False, "Components not available"
    
    detector = CriticalIssueDetector(WORKSPACE)
    result = detector.detect_all()
    
    security_issues = [i for i in result.issues if i.category == 'security' and i.risk_level in ['critical', 'high']]
    passed = len(security_issues) == 0
    evidence = f"Security issues: {len(security_issues)}"
    return passed, evidence

def check_documentation_structure() -> tuple:
    """检查文档结构"""
    # 简化检查：查找 markdown 文件中的标题
    doc_files = list(DOCS_DIR.glob("*.md"))
    
    if not doc_files:
        return False, "No documentation files found"
    
    passed = True
    evidence = f"Documentation files: {len(doc_files)}"
    return passed, evidence

def check_test_coverage() -> tuple:
    """检查测试覆盖率"""
    # 简化：检查是否有测试文件
    test_files = list((WORKSPACE / "92-tests").glob("*.py"))
    
    passed = len(test_files) > 0
    evidence = f"Test files: {len(test_files)}"
    return passed, evidence


# ============== 主执行逻辑 ==============

def run_checks(phase: str) -> dict:
    """执行检查"""
    results = []
    
    # 根据阶段选择检查项
    if phase == "start":
        checks = CHECKLIST_V7["blocker"][:3]  # 前期只检查关键项
    elif phase == "mid":
        checks = CHECKLIST_V7["blocker"] + CHECKLIST_V7["warning"][:2]
    else:  # final
        checks = CHECKLIST_V7["blocker"] + CHECKLIST_V7["warning"] + CHECKLIST_V7["info"]
    
    for check_def in checks:
        check_func_name = check_def["check"]
        check_func = globals().get(check_func_name)
        
        if not check_func:
            results.append({
                **check_def,
                "checked": False,
                "notes": f"Check function not found: {check_func_name}",
                "evidence": "N/A"
            })
            continue
        
        try:
            passed, evidence = check_func()
            results.append({
                **check_def,
                "checked": passed,
                "notes": "OK" if passed else "FAIL",
                "evidence": evidence
            })
        except Exception as e:
            results.append({
                **check_def,
                "checked": False,
                "notes": f"Error: {e}",
                "evidence": str(e)
            })
    
    return {
        "phase": phase,
        "timestamp": datetime.now().isoformat(),
        "checks": results
    }

def calculate_score(results: list) -> int:
    """计算分数"""
    total = len(results)
    passed = sum(1 for r in results if r["checked"])
    
    # BLOCKER 失败直接 0 分
    blocker_failures = sum(1 for r in results if r.get("blocking") and not r["checked"])
    if blocker_failures > 0:
        return 0
    
    return int(passed / total * 100) if total > 0 else 0

def create_remediation_tasks(results: list, task_name: str):
    """创建整改任务"""
    if not COMPONENTS_AVAILABLE:
        return
    
    tracker = RemediationTracker(WORKSPACE)
    
    # 筛选失败的项
    failed_items = [
        {
            "id": r["id"],
            "item": r["item"],
            "level": "BLOCKER" if r.get("blocking") else "WARNING",
            "notes": r.get("notes", ""),
            "evidence": r.get("evidence", "")
        }
        for r in results if not r["checked"]
    ]
    
    if failed_items:
        task_ids = tracker.create_tasks(failed_items, f"critic-{task_name}", "claw")
        print(f"\n[Remediation] Created {len(task_ids)} tasks:")
        for tid in task_ids:
            print(f"  • {tid}")

def print_results(results: dict, score: int):
    """打印结果"""
    print("\n" + "=" * 60)
    print(f"[CRITIC v7.0] {'FULLY AUTOMATED' if COMPONENTS_AVAILABLE else 'BASIC MODE'} - {results['phase'].upper()}")
    print("=" * 60)
    
    # 统计
    total = len(results["checks"])
    passed = sum(1 for r in results["checks"] if r["checked"])
    blocker_failures = sum(1 for r in results["checks"] if r.get("blocking") and not r["checked"])
    warning_failures = sum(1 for r in results["checks"] if not r.get("blocking") and not r["checked"])
    
    status = "PASS" if score >= 95 else ("NEEDS_ATTENTION" if blocker_failures == 0 else "BLOCKED")
    
    print(f"\nTask: \"{results.get('task', 'Unknown')}\"")
    print(f"Phase: {results['phase']}")
    print(f"Time: {results['timestamp']}")
    print(f"Status: {status}")
    print(f"Score: {score}/100")
    print(f"Checklist Items: {total}")
    
    print(f"\n{'X' if blocker_failures > 0 else '✓'} Blocker failures: {blocker_failures}")
    print(f"{'⚠' if warning_failures > 0 else '✓'} Warning failures: {warning_failures}")
    
    print("\nChecklist:")
    for i, r in enumerate(results["checks"], 1):
        status_icon = "OK" if r["checked"] else "FAIL"
        blocking_marker = "🚨" if r.get("blocking") and not r["checked"] else ("⚠" if not r.get("blocking") and not r["checked"] else "")
        print(f"  [{status_icon}] {i}. {r['item']}")
        print(f"      Notes: {r['notes']}")
        print(f"      Evidence: {r['evidence'][:100]}")
        if blocking_marker:
            print(f"      {blocking_marker} {'BLOCKER' if r.get('blocking') else 'WARNING'} failure")
    
    # 失败项汇总
    failed = [r for r in results["checks"] if not r["checked"]]
    if failed:
        print("\n" + "=" * 60)
        print("FAILED ITEMS (需要修复):")
        for r in failed:
            blocking = "🚨 BLOCKER" if r.get("blocking") else "⚠ WARNING"
            print(f"  - {r['item']} ({blocking})")
        print("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Critic v7.0')
    parser.add_argument('-t', '--task', type=str, required=True, help='任务名称')
    parser.add_argument('-p', '--phase', type=str, default='final', 
                       choices=['start', 'mid', 'final'], help='审查阶段')
    parser.add_argument('--create-remediation', action='store_true', 
                       help='创建整改任务')
    
    args = parser.parse_args()
    
    # 执行检查
    results = run_checks(args.phase)
    results['task'] = args.task
    
    # 计算分数
    score = calculate_score(results["checks"])
    
    # 打印结果
    print_results(results, score)
    
    # 创建整改任务
    if args.create_remediation:
        create_remediation_tasks(results["checks"], args.task)
    
    # 保存结果 (清理任务名中的特殊字符)
    safe_task_name = re.sub(r'[^\w\s-]', '', args.task).strip().replace(' ', '-')
    output_file = SCRIPTS_DIR / f"critic-auto-{safe_task_name}-v7.json"
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nReview saved to: {output_file}")
    
    # 返回码
    blocker_failures = sum(1 for r in results["checks"] if r.get("blocking") and not r["checked"])
    return 1 if blocker_failures > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
