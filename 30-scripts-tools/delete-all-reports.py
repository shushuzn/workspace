#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除所有报告文件 (备份后删除)
"""

import sys
import io
import shutil
from pathlib import Path
from datetime import datetime

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
BACKUP_DIR = WORKSPACE / "99-backups" / f"report-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# 允许保留的报告 (白名单)
ALLOWED_REPORTS = [
    "21-reports/README.md",
    "21-reports/INDEX.md",
]

def main():
    print("=" * 60)
    print("删除报告文件 (批量清理)")
    print("=" * 60)
    
    # 创建备份目录
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n备份目录：{BACKUP_DIR}")
    
    # 扫描报告文件
    print("\n扫描报告文件...")
    report_patterns = [
        "*-report-*.md",
        "*-REPORT-*.md",
        "REP_*.md",
        "*report*.md",
    ]
    
    all_reports = []
    for pattern in report_patterns:
        all_reports.extend(WORKSPACE.rglob(pattern))
    
    # 去重
    all_reports = list(set(all_reports))
    
    # 过滤允许的报告
    reports_to_delete = []
    for report in all_reports:
        rel_path = str(report.relative_to(WORKSPACE)).replace('\\', '/')
        
        # 跳过白名单
        if any(rel_path.endswith(allowed) for allowed in ALLOWED_REPORTS):
            continue
        
        # 跳过备份目录
        if '99-backups' in str(report):
            continue
        
        # 跳过 node_modules
        if 'node_modules' in str(report):
            continue
        
        reports_to_delete.append(report)
    
    print(f"\n发现 {len(reports_to_delete)} 个报告文件 (排除白名单和备份)")
    
    if len(reports_to_delete) == 0:
        print("✅ 无需清理")
        return
    
    print("\n按 Ctrl+C 取消，或等待 3 秒后继续...")
    import time
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # 删除文件
    deleted = 0
    errors = 0
    
    for report in reports_to_delete:
        try:
            # 备份
            rel_path = report.relative_to(WORKSPACE)
            backup_path = BACKUP_DIR / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(report, backup_path)
            
            # 删除
            report.unlink()
            deleted += 1
            
            if deleted <= 20:
                print(f"  🗑️ {rel_path}")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ⚠️ 删除失败 {report}: {e}")
    
    print(f"\n删除完成:")
    print(f"  ✅ 成功：{deleted} 个")
    print(f"  ❌ 失败：{errors} 个")
    print(f"\n备份位置：{BACKUP_DIR}")

if __name__ == "__main__":
    main()
