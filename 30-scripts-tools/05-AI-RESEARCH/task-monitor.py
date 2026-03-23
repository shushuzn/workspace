#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Monitor v1
定时任务监控与告警系统
"""

import json
from datetime import datetime
from pathlib import Path

# 配置
LOG_DIR = Path(r"D:\OpenClaw\workspace\logs")
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\System-Monitor")

# 监控的定时任务
TASKS = [
    'arXiv-Collect',
    'Security-Audit',
    'Medium-Watcher',
    'Memory-Distiller',
    'Daily-Collect',
]

def check_task_logs():
    """检查任务日志"""
    results = []

    for task in TASKS:
        log_file = LOG_DIR / f"{task.lower()}.log"
        status = 'unknown'
        last_run = 'N/A'

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]  # 最后 10 行
                    last_line = lines[-1] if lines else ''

                    if 'SUCCESS' in last_line or 'OK' in last_line:
                        status = 'success'
                    elif 'ERROR' in last_line or 'FAIL' in last_line:
                        status = 'failed'
                    else:
                        status = 'running'

                    last_run = datetime.now().strftime('%Y-%m-%d %H:%M')
            except:
                status = 'error'

        results.append({
            'task': task,
            'status': status,
            'last_run': last_run,
        })

    return results

def generate_monitor_report(results):
    """生成监控报告"""
    return {
        'generated_at': datetime.now().isoformat(),
        'tasks': results,
        'summary': {
            'total': len(results),
            'success': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'unknown': len([r for r in results if r['status'] == 'unknown']),
        }
    }

def save_monitor_report(report):
    """保存监控报告"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON 格式
    json_file = OUTPUT_DIR / f"monitor-report-{date_str}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Markdown 格式
    md_file = OUTPUT_DIR / f"monitor-report-{date_str}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 系统监控报告 - {date_str}\n\n")
        f.write(f"**生成时间:** {report['generated_at']}\n\n")
        f.write("---\n\n")

        f.write("## 📊 运行摘要\n\n")
        summary = report['summary']
        f.write(f"- **总任务数:** {summary['total']}\n")
        f.write(f"- **成功:** {summary['success']}\n")
        f.write(f"- **失败:** {summary['failed']}\n")
        f.write(f"- **未知:** {summary['unknown']}\n\n")
        f.write("---\n\n")

        f.write("## 📋 任务状态\n\n")
        f.write("| 任务 | 状态 | 最后运行 |\n")
        f.write("|------|------|----------|\n")
        for task in report['tasks']:
            status_icon = {'success': '✅', 'failed': '❌', 'running': '🟡', 'unknown': '❓'}.get(task['status'], '❓')
            f.write(f"| {task['task']} | {status_icon} {task['status']} | {task['last_run']} |\n")

    print(f"[OK] Saved monitor report to {md_file}")
    return md_file

def monitor():
    """主流程"""
    print("=" * 60)
    print("Task Monitor v1 - System Check")
    print("=" * 60)

    print("\n[1/3] Checking task logs...")
    results = check_task_logs()

    print("\n[2/3] Generating report...")
    report = generate_monitor_report(results)

    print("\n[3/3] Saving report...")
    save_monitor_report(report)

    print("-" * 60)
    print(f"[COMPLETE] Success: {report['summary']['success']}/{report['summary']['total']}")
    print("=" * 60)

if __name__ == "__main__":
    monitor()
