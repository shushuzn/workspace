#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Stats - 工作流执行统计面板
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class WorkflowStats:
    """工作流统计面板"""
    
    def __init__(self, flow_id: str = "20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.flow_dir = Path(f"flow-archive/{flow_id}")
        self.archive_dir = Path("flow-archive")
        
    def get_all_flows(self):
        """获取所有工作流"""
        flows = {}
        for d in self.archive_dir.iterdir():
            if d.is_dir() and d.name.startswith("20260"):
                state_file = d / "execution-state.json"
                if state_file.exists():
                    with open(state_file, 'r', encoding='utf-8') as f:
                        flows[d.name] = json.load(f)
        return flows
    
    def show_overview(self):
        """显示总览"""
        flows = self.get_all_flows()
        
        print("\n" + "=" * 60)
        print("📊 工作流执行统计面板")
        print("=" * 60)
        print(f"\n总工作流数: {len(flows)}")
        
        # 统计
        total_steps = 0
        completed = 0
        in_progress = 0
        failed = 0
        
        for name, state in flows.items():
            total = state.get('total_steps', 0)
            current = state.get('current_step', 0)
            status = state.get('status', 'unknown')
            
            total_steps += total
            completed += current
            
            if status == 'failed':
                failed += 1
            elif status in ['in_progress', 'initializing']:
                in_progress += 1
        
        print(f"\n📈 统计数据:")
        print(f"  - 总步骤数: {total_steps}")
        print(f"  - 已完成步骤: {completed}")
        print(f"  - 进行中: {in_progress}")
        print(f"  - 失败: {failed}")
        
        if total_steps > 0:
            avg_progress = completed / total_steps * 100
            print(f"  - 平均进度: {avg_progress:.1f}%")
        
        return flows
    
    def show_recent(self, limit: int = 5):
        """显示最近工作流"""
        flows = self.get_all_flows()
        
        # 按时间排序
        sorted_flows = sorted(
            flows.items(),
            key=lambda x: x[1].get('started_at', ''),
            reverse=True
        )[:limit]
        
        print(f"\n📋 最近 {len(sorted_flows)} 个工作流:")
        print("-" * 60)
        
        for name, state in sorted_flows:
            task = state.get('task', 'N/A')[:30]
            current = state.get('current_step', 0)
            total = state.get('total_steps', 0)
            percent = state.get('completion_percentage', 0)
            status = state.get('status', 'unknown')
            
            # 状态图标
            status_icon = {
                'completed': '✅',
                'failed': '❌',
                'in_progress': '⏳',
                'initializing': '🔄'
            }.get(status, '❓')
            
            print(f"{status_icon} {task}")
            print(f"   进度: {current}/{total} ({percent:.0f}%)")
        
        print("-" * 60)
    
    def show_summary(self):
        """显示完整摘要"""
        flows = self.show_overview()
        self.show_recent(5)
        
        print("\n" + "=" * 60)
        print("💡 提示:")
        print("  workflow_menu.py status  - 查看当前状态")
        print("  workflow_menu.py next    - 完成下一步")
        print("  copaw_entry.py           - 启动新工作流")
        print("=" * 60)


def main():
    stats = WorkflowStats()
    stats.show_summary()


if __name__ == "__main__":
    main()