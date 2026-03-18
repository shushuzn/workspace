#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Dashboard Health Widget - 记忆健康状态推送到 Innovator Dashboard

功能:
- 读取 memory_health_monitor.py 生成的健康报告
- 生成 Dashboard 兼容的 JSON 格式
- 支持推送到云服务器 Dashboard
- 本地预览模式

使用示例:
    python dashboard_health_widget.py --preview  # 本地预览
    python dashboard_health_widget.py --push     # 推送到 Dashboard

作者：Claw [PAW] (Innovator Agent)
日期：2026-03-14
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import cache manager
try:
    from cache_manager import CacheManager
    CACHE_ENABLED = True
    cache = CacheManager()
except ImportError:
    CACHE_ENABLED = False
    cache = None

# 配置
HEALTH_REPORT_JSON = Path(r"D:\OpenClaw\workspace\00-persona-system\memory-health-report.json")
DASHBOARD_OUTPUT = Path(r"D:\OpenClaw\workspace\00-persona-system\dashboard-health-widget.json")
CLOUD_DASHBOARD_URL = "https://felixxii.xyz/api/health"

def load_health_report() -> dict:
    """加载健康报告 (with caching)"""
    if CACHE_ENABLED and cache:
        # Cache health report for 10 minutes
        return cache.get('dashboard_health', _load_health_report_raw, ttl=600)
    else:
        return _load_health_report_raw()

def _load_health_report_raw() -> dict:
    """Load health report (raw, no cache)"""
    if not HEALTH_REPORT_JSON.exists():
        return {
            'error': 'Health report not found',
            'message': 'Run memory_health_monitor.py first'
        }
    
    with open(HEALTH_REPORT_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_dashboard_widget(health_data: dict) -> dict:
    """生成 Dashboard 组件数据"""
    status_emoji = {
        'healthy': '[OK]',
        'warning': '[WARN]',
        'critical': '🚨',
        'unknown': '❓'
    }
    
    status = health_data.get('status', 'unknown')
    workspace = health_data.get('workspace_memory', {})
    config = health_data.get('config_memory', {})
    
    widget = {
        'widget': 'memory_health',
        'version': '1.0',
        'updated_at': datetime.now().isoformat(),
        'status': {
            'value': status,
            'emoji': status_emoji.get(status, '❓'),
            'message': f'Memory System {status.title()}'
        },
        'metrics': {
            'workspace_memory': {
                'size_kb': workspace.get('size_kb', 0),
                'lines': workspace.get('lines', 0),
                'status': '[OK]' if workspace.get('exists') else '[FAIL]'
            },
            'config_memory': {
                'size_kb': config.get('size_kb', 0),
                'lines': config.get('lines', 0),
                'status': '[OK]' if config.get('exists') else '[FAIL]'
            }
        },
        'issues_count': len(health_data.get('issues', [])),
        'next_check': health_data.get('checked_at', ''),
        'architecture': {
            'description': 'Dual MEMORY.md architecture',
            'workspace': 'Research Insights (49KB)',
            'config': 'Agent Configuration (14KB)'
        }
    }
    
    return widget

def save_widget(widget: dict):
    """保存组件数据"""
    with open(DASHBOARD_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(widget, f, indent=2, ensure_ascii=False)
    
    print(f"[DASHBOARD] Widget saved: {DASHBOARD_OUTPUT}")

def preview_widget(widget: dict):
    """本地预览"""
    print("\n" + "="*60)
    print("[DASHBOARD] HEALTH WIDGET PREVIEW")
    print("="*60)
    status_msg = widget['status']['message']
    print(f"Status: {status_msg}")
    print(f"Updated: {widget['updated_at']}")
    print("-"*60)
    ws = widget['metrics']['workspace_memory']
    cfg = widget['metrics']['config_memory']
    print(f"Workspace Memory: {ws['size_kb']} KB ({ws['lines']} lines)")
    print(f"Config Memory:    {cfg['size_kb']} KB ({cfg['lines']} lines)")
    print("-"*60)
    print(f"Issues: {widget['issues_count']}")
    print(f"Architecture: {widget['architecture']['description']}")
    print("="*60)

def push_to_cloud(widget: dict):
    """推送到云服务器（未来功能）"""
    print(f"[DASHBOARD] Future: Push to {CLOUD_DASHBOARD_URL}")
    print(f"[DASHBOARD] Token: Use SSH to upload to 8.208.30.28:8444")
    # TODO: 实现 SSH 上传或 API 推送

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Dashboard Health Widget')
    parser.add_argument('--preview', action='store_true', help='Preview widget')
    parser.add_argument('--push', action='store_true', help='Push to cloud dashboard')
    
    args = parser.parse_args()
    
    # 加载健康报告
    health_data = load_health_report()
    
    # 生成组件
    widget = generate_dashboard_widget(health_data)
    
    # 保存
    save_widget(widget)
    
    # 预览或推送
    if args.preview or not args.push:
        preview_widget(widget)
    
    if args.push:
        push_to_cloud(widget)

if __name__ == '__main__':
    main()
