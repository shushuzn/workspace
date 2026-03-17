#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer v1
系统性能优化工具
"""

import psutil
import os
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\System-Optimization")

def check_system_resources():
    """检查系统资源"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('D:').percent,
    }

def check_process_resources():
    """检查进程资源"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] is not None and pinfo['memory_percent'] is not None:
                processes.append(pinfo)
        except:
            continue
    
    # 按 CPU 使用率排序
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    return processes[:10]  # 前 10 个

def generate_optimization_report(resources, processes):
    """生成优化报告"""
    recommendations = []
    
    if resources['cpu_percent'] > 70:
        recommendations.append("CPU 使用率高，考虑关闭不必要的进程")
    if resources['memory_percent'] > 80:
        recommendations.append("内存使用率高，考虑清理缓存或增加内存")
    if resources['disk_percent'] > 90:
        recommendations.append("磁盘空间不足，建议清理或扩容")
    
    return {
        'generated_at': datetime.now().isoformat(),
        'resources': resources,
        'top_processes': processes,
        'recommendations': recommendations,
    }

def save_optimization_report(report):
    """保存优化报告"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    md_file = OUTPUT_DIR / f"performance-{date_str}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 性能优化报告 - {date_str}\n\n")
        f.write(f"**生成时间:** {report['generated_at']}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 系统资源\n\n")
        res = report['resources']
        f.write(f"- **CPU:** {res['cpu_percent']:.1f}%\n")
        f.write(f"- **内存:** {res['memory_percent']:.1f}%\n")
        f.write(f"- **磁盘:** {res['disk_percent']:.1f}%\n\n")
        f.write("---\n\n")
        
        f.write("## 🔝 占用最高的进程\n\n")
        f.write("| 进程 | PID | CPU% | 内存% |\n")
        f.write("|------|-----|------|-------|\n")
        for proc in report['top_processes'][:5]:
            f.write(f"| {proc['name']} | {proc['pid']} | {proc['cpu_percent'] or 0:.1f} | {proc['memory_percent'] or 0:.1f} |\n")
        f.write("\n---\n\n")
        
        f.write("## 💡 优化建议\n\n")
        if report['recommendations']:
            for i, rec in enumerate(report['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        else:
            f.write("系统运行良好，无需优化\n")
    
    print(f"[OK] Saved optimization report to {md_file}")
    return md_file

def optimize():
    """主流程"""
    print("=" * 60)
    print("Performance Optimizer v1")
    print("=" * 60)
    
    print("\n[1/3] Checking system resources...")
    resources = check_system_resources()
    print(f"  CPU: {resources['cpu_percent']:.1f}%, Memory: {resources['memory_percent']:.1f}%")
    
    print("\n[2/3] Checking process resources...")
    processes = check_process_resources()
    print(f"  Top process: {processes[0]['name'] if processes else 'N/A'}")
    
    print("\n[3/3] Generating report...")
    report = generate_optimization_report(resources, processes)
    save_optimization_report(report)
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    optimize()
