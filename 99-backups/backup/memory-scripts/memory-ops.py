#!/usr/bin/env python3
"""
Memory Operations Unified Tool

统一 memory 相关操作，替代 7 个独立脚本：
- memory-dashboard.py          → memory-ops.py dashboard
- memory-distiller.py          → memory-ops.py distill
- memory-maintenance.py        → memory-ops.py maintain
- memory-quality-assessor.py   → memory-ops.py assess
- memory-search-v2.py          → memory-ops.py search
- memory_auto_fix.py           → memory-ops.py fix
- memory_health_monitor.py     → memory-ops.py health

使用方式:
    python memory-ops.py <command> [options]

Commands:
    dashboard   - Show memory system dashboard
    distill     - Distill daily notes to MEMORY.md
    maintain    - Daily/weekly maintenance
    assess      - Assess memory quality
    search      - Search memory
    fix         - Auto-fix memory issues
    health      - Health check

[INNOVATOR-026] 工具整合减少维护成本
[INNOVATOR-027] 统一接口简化调用
"""

import sys
import os
import argparse
from pathlib import Path

# 初始化工作目录
WORKSPACE = Path(os.environ.get('OPENCLAW_WORKSPACE', str(Path(__file__).parent.parent)))
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
MEMORY_FILE = MEMORY_DIR / 'MEMORY.md'

def cmd_dashboard(args):
    """Show memory system dashboard"""
    print("="*60)
    print("MEMORY DASHBOARD")
    print("="*60)
    
    # 调用原 memory-dashboard.py
    dashboard_script = WORKSPACE / '30-scripts-tools' / 'memory-dashboard.py'
    if dashboard_script.exists():
        os.system(f'python "{dashboard_script}"')
    else:
        print("[WARN] memory-dashboard.py not found")
        print("Showing basic stats...")
        
        if MEMORY_FILE.exists():
            lines = MEMORY_FILE.read_text(encoding='utf-8').splitlines()
            print(f"MEMORY.md lines: {len(lines)}")
        else:
            print("[ERROR] MEMORY.md not found")
    
    print("="*60)

def cmd_distill(args):
    """Distill daily notes to MEMORY.md"""
    print("="*60)
    print("MEMORY DISTILLER")
    print("="*60)
    
    # 调用原 memory-distiller.py
    distill_script = WORKSPACE / '30-scripts-tools' / 'memory-distiller.py'
    if distill_script.exists():
        cmd = f'python "{distill_script}"'
        if args.weekly:
            cmd += ' --weekly'
        os.system(cmd)
    else:
        print("[WARN] memory-distiller.py not found")
        print("Manual distillation required")
    
    print("="*60)

def cmd_maintain(args):
    """Daily/weekly maintenance"""
    print("="*60)
    print("MEMORY MAINTENANCE")
    print("="*60)
    
    # 调用原 memory-maintenance.py
    maintain_script = WORKSPACE / '30-scripts-tools' / 'memory-maintenance.py'
    if maintain_script.exists():
        cmd = f'python "{maintain_script}"'
        if args.daily:
            cmd += ' --daily'
        if args.weekly:
            cmd += ' --weekly'
        os.system(cmd)
    else:
        print("[WARN] memory-maintenance.py not found")
    
    print("="*60)

def cmd_assess(args):
    """Assess memory quality"""
    print("="*60)
    print("MEMORY QUALITY ASSESSMENT")
    print("="*60)
    
    # 调用原 memory-quality-assessor.py 或 memory_auto_fix.py
    if args.file:
        target = args.file
    else:
        target = str(MEMORY_FILE)
    
    # 优先使用 memory_auto_fix.py (严格模式)
    fix_script = WORKSPACE / '30-scripts-tools' / 'memory_auto_fix.py'
    if fix_script.exists():
        cmd = f'python "{fix_script}" --strict "{target}"'
        os.system(cmd)
    else:
        print("[WARN] memory_auto_fix.py not found")
    
    print("="*60)

def cmd_search(args):
    """Search memory"""
    print("="*60)
    print("MEMORY SEARCH")
    print("="*60)
    
    # 调用原 memory-search-v2.py
    search_script = WORKSPACE / '30-scripts-tools' / 'memory-search-v2.py'
    if search_script.exists():
        cmd = f'python "{search_script}"'
        if args.query:
            cmd += f' "{args.query}"'
        os.system(cmd)
    else:
        print("[WARN] memory-search-v2.py not found")
        print("Manual search required")
    
    print("="*60)

def cmd_fix(args):
    """Auto-fix memory issues"""
    print("="*60)
    print("MEMORY AUTO-FIX")
    print("="*60)
    
    # 调用原 memory_auto_fix.py
    fix_script = WORKSPACE / '30-scripts-tools' / 'memory_auto_fix.py'
    if fix_script.exists():
        cmd = f'python "{fix_script}"'
        if args.strict:
            cmd += ' --strict'
        if args.file:
            cmd += f' "{args.file}"'
        os.system(cmd)
    else:
        print("[WARN] memory_auto_fix.py not found")
    
    print("="*60)

def cmd_health(args):
    """Health check"""
    print("="*60)
    print("MEMORY HEALTH CHECK")
    print("="*60)
    
    # 调用原 memory_health_monitor.py
    health_script = WORKSPACE / '30-scripts-tools' / 'memory_health_monitor.py'
    if health_script.exists():
        os.system(f'python "{health_script}"')
    else:
        print("[WARN] memory_health_monitor.py not found")
        print("Basic health check...")
        
        # 基础检查
        checks = {
            'MEMORY.md exists': MEMORY_FILE.exists(),
            'MEMORY_DIR exists': MEMORY_DIR.exists(),
            'Daily notes dir': (MEMORY_DIR / 'memory').exists(),
        }
        
        for check, passed in checks.items():
            status = '[OK]' if passed else '[FAIL]'
            print(f"{status} {check}")
    
    print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description='Memory Operations Unified Tool',
        epilog='''
Examples:
  python memory-ops.py dashboard
  python memory-ops.py distill --weekly
  python memory-ops.py maintain --daily
  python memory-ops.py assess MEMORY.md
  python memory-ops.py search "query"
  python memory-ops.py fix --strict
  python memory-ops.py health
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # dashboard
    p_dashboard = subparsers.add_parser('dashboard', help='Show memory dashboard')
    p_dashboard.set_defaults(func=cmd_dashboard)
    
    # distill
    p_distill = subparsers.add_parser('distill', help='Distill daily notes')
    p_distill.add_argument('--weekly', action='store_true', help='Weekly distillation')
    p_distill.set_defaults(func=cmd_distill)
    
    # maintain
    p_maintain = subparsers.add_parser('maintain', help='Memory maintenance')
    p_maintain.add_argument('--daily', action='store_true', help='Daily maintenance')
    p_maintain.add_argument('--weekly', action='store_true', help='Weekly maintenance')
    p_maintain.set_defaults(func=cmd_maintain)
    
    # assess
    p_assess = subparsers.add_parser('assess', help='Assess memory quality')
    p_assess.add_argument('file', nargs='?', help='File to assess')
    p_assess.set_defaults(func=cmd_assess)
    
    # search
    p_search = subparsers.add_parser('search', help='Search memory')
    p_search.add_argument('query', nargs='?', help='Search query')
    p_search.set_defaults(func=cmd_search)
    
    # fix
    p_fix = subparsers.add_parser('fix', help='Auto-fix memory issues')
    p_fix.add_argument('--strict', action='store_true', help='Strict mode')
    p_fix.add_argument('file', nargs='?', help='File to fix')
    p_fix.set_defaults(func=cmd_fix)
    
    # health
    p_health = subparsers.add_parser('health', help='Health check')
    p_health.set_defaults(func=cmd_health)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print("\n[INNOVATOR-026] 7 memory tools unified into memory-ops.py")
        print("[INNOVATOR-027] Single interface for all memory operations")
        sys.exit(1)
    
    args.func(args)

if __name__ == '__main__':
    main()
