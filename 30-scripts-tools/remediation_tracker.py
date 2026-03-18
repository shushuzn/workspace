#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remediation Tracker - 整改跟踪器 (Auto-Critic v7.0 组件)

管理问题整改闭环，防止"问题提了没人改"。

功能:
1. 为 FAIL 项生成唯一标识
2. 创建整改任务
3. 跟踪整改进度
4. 到期自动提醒
5. 超期升级机制
6. 生成整改台账

使用:
    py remediation_tracker.py --create --fail-items critic_review.json
    py remediation_tracker.py --status
    py remediation_tracker.py --remind --overdue
    py remediation_tracker.py --report
"""

import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class TaskStatus(Enum):
    """任务状态"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    CLOSED = "closed"
    OVERDUE = "overdue"


class SeverityLevel(Enum):
    """严重级别"""
    BLOCKER = "blocker"  # 阻断项
    WARNING = "warning"  # 警告项
    INFO = "info"        # 提示项


@dataclass
class RemediationTask:
    """整改任务"""
    task_id: str                          # 唯一标识 UUID
    fail_item_id: str                     # 关联 FAIL 项 ID
    source: str                           # 来源 (critic_review.json)
    title: str                            # 任务标题
    description: str                      # 任务描述
    severity: str                         # blocker/warning
    created_at: str                       # 创建时间
    deadline: str                         # 截止时间
    assignee: str                         # 负责人
    status: str                           # 任务状态
    linked_commit: Optional[str]          # 修复提交 SHA
    verification_result: Optional[dict]   # 验证结果
    reminder_count: int                   # 提醒次数
    last_reminder: Optional[str]          # 最后提醒时间
    notes: List[str]                      # 备注
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class RemediationLog:
    """整改台账"""
    version: str
    created_at: str
    last_updated: str
    tasks: Dict[str, RemediationTask]
    statistics: dict


class RemediationTracker:
    """整改跟踪器"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.log_file = workspace / '30-scripts-tools' / 'remediation_log.json'
        self.tasks = {}
        self._load()
    
    def _load(self):
        """加载整改台账"""
        if self.log_file.exists():
            try:
                data = json.loads(self.log_file.read_text(encoding='utf-8'))
                self.tasks = {
                    tid: RemediationTask.from_dict(t) 
                    for tid, t in data.get('tasks', {}).items()
                }
            except Exception as e:
                print(f"[WARN] Failed to load remediation log: {e}")
                self.tasks = {}
    
    def _save(self):
        """保存整改台账"""
        # 统计
        stats = self._calculate_statistics()
        
        log = RemediationLog(
            version="1.0",
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            tasks={tid: t.to_dict() for tid, t in self.tasks.items()},
            statistics=stats
        )
        
        self.log_file.write_text(
            json.dumps(asdict(log), indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def _calculate_statistics(self) -> dict:
        """计算统计信息"""
        total = len(self.tasks)
        by_status = {}
        by_severity = {}
        overdue = 0
        
        for task in self.tasks.values():
            by_status[task.status] = by_status.get(task.status, 0) + 1
            by_severity[task.severity] = by_severity.get(task.severity, 0) + 1
            
            # 检查是否超期
            if task.status not in ['verified', 'closed']:
                deadline = datetime.fromisoformat(task.deadline)
                if datetime.now() > deadline:
                    overdue += 1
        
        return {
            'total_tasks': total,
            'by_status': by_status,
            'by_severity': by_severity,
            'overdue_count': overdue,
            'completion_rate': round((by_status.get('verified', 0) + by_status.get('closed', 0)) / total * 100, 1) if total > 0 else 0
        }
    
    def create_tasks(self, fail_items: List[dict], source: str, assignee: str = "claw") -> List[str]:
        """创建整改任务"""
        created_ids = []
        
        for item in fail_items:
            # 生成唯一 ID
            task_id = f"REM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            # 确定严重级别
            severity = "blocker" if item.get('level') == 'BLOCKER' else "warning"
            
            # 计算截止时间
            if severity == "blocker":
                deadline = datetime.now() + timedelta(hours=24)  # 24 小时
            else:
                deadline = datetime.now() + timedelta(days=7)  # 7 天
            
            task = RemediationTask(
                task_id=task_id,
                fail_item_id=item.get('id', 'unknown'),
                source=source,
                title=item.get('item', 'Unknown Item'),
                description=item.get('notes', ''),
                severity=severity,
                created_at=datetime.now().isoformat(),
                deadline=deadline.isoformat(),
                assignee=assignee,
                status=TaskStatus.OPEN.value,
                linked_commit=None,
                verification_result=None,
                reminder_count=0,
                last_reminder=None,
                notes=[]
            )
            
            self.tasks[task_id] = task
            created_ids.append(task_id)
        
        self._save()
        return created_ids
    
    def update_status(self, task_id: str, status: str, commit_sha: str = None):
        """更新任务状态"""
        if task_id not in self.tasks:
            print(f"[ERROR] Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        task.status = status
        
        if commit_sha:
            task.linked_commit = commit_sha
        
        self._save()
        return True
    
    def verify_task(self, task_id: str, verification_result: dict) -> bool:
        """验证任务"""
        if task_id not in self.tasks:
            print(f"[ERROR] Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        if verification_result.get('passed'):
            task.status = TaskStatus.VERIFIED.value
            task.verification_result = verification_result
        else:
            task.status = TaskStatus.IN_PROGRESS.value
            task.notes.append(f"Verification failed: {verification_result.get('message', '')}")
        
        self._save()
        return task.status == TaskStatus.VERIFIED.value
    
    def get_overdue_tasks(self) -> List[RemediationTask]:
        """获取超期任务"""
        overdue = []
        
        for task in self.tasks.values():
            if task.status in [TaskStatus.OPEN.value, TaskStatus.IN_PROGRESS.value]:
                deadline = datetime.fromisoformat(task.deadline)
                if datetime.now() > deadline:
                    task.status = TaskStatus.OVERDUE.value
                    overdue.append(task)
        
        return overdue
    
    def send_reminders(self, task_ids: List[str] = None) -> int:
        """发送提醒"""
        if task_ids is None:
            # 默认提醒所有未完成任务
            task_ids = [
                tid for tid, t in self.tasks.items()
                if t.status in [TaskStatus.OPEN.value, TaskStatus.IN_PROGRESS.value, TaskStatus.OVERDUE.value]
            ]
        
        reminded = 0
        for task_id in task_ids:
            if task_id not in self.tasks:
                continue
            
            task = self.tasks[task_id]
            
            # 检查是否需要提醒 (每 3 天提醒一次)
            if task.last_reminder:
                last = datetime.fromisoformat(task.last_reminder)
                if datetime.now() - last < timedelta(days=3):
                    continue
            
            # 更新提醒记录
            task.reminder_count += 1
            task.last_reminder = datetime.now().isoformat()
            
            # 超期升级
            if task.status == TaskStatus.OVERDUE.value and task.severity == "warning":
                task.severity = "blocker"
                task.notes.append(f"Upgraded to BLOCKER due to overdue (reminder #{task.reminder_count})")
            
            reminded += 1
        
        self._save()
        return reminded
    
    def generate_report(self) -> dict:
        """生成整改报告"""
        stats = self._calculate_statistics()
        
        # 按严重级别分组
        blockers = [t for t in self.tasks.values() if t.severity == "blocker"]
        warnings = [t for t in self.tasks.values() if t.severity == "warning"]
        
        # 按状态分组
        open_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.OPEN.value]
        in_progress = [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS.value]
        overdue = [t for t in self.tasks.values() if t.status == TaskStatus.OVERDUE.value]
        
        return {
            'statistics': stats,
            'blockers': [t.to_dict() for t in blockers],
            'warnings': [t.to_dict() for t in warnings],
            'open_tasks': [t.to_dict() for t in open_tasks],
            'in_progress': [t.to_dict() for t in in_progress],
            'overdue_tasks': [t.to_dict() for t in overdue],
            'generated_at': datetime.now().isoformat()
        }


def print_report(report: dict):
    """打印整改报告"""
    print("\n" + "=" * 60)
    print("Remediation Tracker Report")
    print("=" * 60)
    
    stats = report['statistics']
    
    print(f"\n[Overview]")
    print(f"  Total Tasks:       {stats['total_tasks']}")
    print(f"  Completion Rate:   {stats['completion_rate']}%")
    print(f"  Overdue:           {stats['overdue_count']}")
    
    print(f"\n[By Status]")
    for status, count in stats['by_status'].items():
        print(f"  {status:15s}: {count}")
    
    print(f"\n[By Severity]")
    for severity, count in stats['by_severity'].items():
        print(f"  {severity:15s}: {count}")
    
    if report['overdue_tasks']:
        print(f"\n[Overdue Tasks ({len(report['overdue_tasks'])})]")
        for task in report['overdue_tasks'][:5]:
            print(f"\n  🔴 {task['task_id']}: {task['title']}")
            print(f"      Deadline: {task['deadline']}")
            print(f"      Assignee: {task['assignee']}")
    
    if report['blockers']:
        print(f"\n[Blockers ({len(report['blockers'])})]")
        for task in report['blockers'][:5]:
            print(f"\n  🚨 {task['task_id']}: {task['title']}")
            print(f"      Status: {task['status']}")
            print(f"      Deadline: {task['deadline']}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remediation Tracker')
    parser.add_argument('--create', action='store_true', help='创建整改任务')
    parser.add_argument('--fail-items', type=str, help='FAIL 项 JSON 文件')
    parser.add_argument('--assignee', type=str, default='claw', help='负责人')
    parser.add_argument('--status', action='store_true', help='查看状态')
    status_group = parser.add_argument_group('Status options')
    status_group.add_argument('--task-id', type=str, help='任务 ID')
    status_group.add_argument('--new-status', type=str, help='新状态')
    parser.add_argument('--remind', action='store_true', help='发送提醒')
    parser.add_argument('--overdue', action='store_true', help='仅超期任务')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--resolve', type=str, help='解决任务 (task_id)')
    parser.add_argument('--commit', type=str, help='关联提交 SHA')
    parser.add_argument('--progress', type=str, help='标记为进行中 (task_id)')
    
    args = parser.parse_args()
    
    workspace = Path(__file__).parent.parent
    tracker = RemediationTracker(workspace)
    
    # 创建任务
    if args.create and args.fail_items:
        fail_file = Path(args.fail_items)
        if not fail_file.exists():
            print(f"[ERROR] File not found: {fail_file}")
            return 1
        
        try:
            data = json.loads(fail_file.read_text(encoding='utf-8'))
            fail_items = data.get('failed_items', [])
            
            if not fail_items:
                # 尝试从 critic review 格式解析 (v7.0)
                checks = data.get('checks', [])
                fail_items = [
                    {
                        'id': c.get('id', 'unknown'),
                        'item': c.get('item', 'Unknown'),
                        'level': 'BLOCKER' if c.get('blocking') else 'WARNING',
                        'notes': c.get('notes', ''),
                        'evidence': c.get('evidence', '')
                    }
                    for c in checks if not c.get('checked', True)
                ]
            
            if not fail_items:
                # 尝试从 checklist 格式解析 (v6.0)
                checklist = data.get('checklist', [])
                fail_items = [i for i in checklist if not i.get('checked', True)]
            
            task_ids = tracker.create_tasks(fail_items, str(fail_file), args.assignee)
            print(f"Created {len(task_ids)} remediation tasks:")
            for tid in task_ids:
                print(f"  • {tid}")
            
            return 0
        
        except Exception as e:
            print(f"[ERROR] Failed to create tasks: {e}")
            return 1
    
    # 更新状态
    if args.task_id and args.new_status:
        if tracker.update_status(args.task_id, args.new_status):
            print(f"Updated task {args.task_id} to {args.new_status}")
            return 0
        else:
            return 1
    
    # 发送提醒
    if args.remind:
        if args.overdue:
            overdue = tracker.get_overdue_tasks()
            task_ids = [t.task_id for t in overdue]
        else:
            task_ids = None
        
        reminded = tracker.send_reminders(task_ids)
        print(f"Sent {reminded} reminders")
        return 0
    
    # 生成报告
    if args.report:
        report = tracker.generate_report()
        
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print_report(report)
        
        return 0
    
    # 解决任务
    if args.resolve:
        task_id = args.resolve
        if task_id not in tracker.tasks:
            print(f"[ERROR] Task not found: {task_id}")
            return 1
        
        task = tracker.tasks[task_id]
        task.status = TaskStatus.RESOLVED.value
        if args.commit:
            task.linked_commit = args.commit
        
        tracker._save()
        print(f"Resolved task {task_id}")
        print(f"  Title: {task.title}")
        print(f"  Status: {task.status}")
        print(f"  Commit: {args.commit or 'N/A'}")
        return 0
    
    # 标记为进行中
    if args.progress:
        task_id = args.progress
        if task_id not in tracker.tasks:
            print(f"[ERROR] Task not found: {task_id}")
            return 1
        
        task = tracker.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS.value
        if args.commit:
            task.linked_commit = args.commit
        
        tracker._save()
        print(f"Task {task_id} marked as in_progress")
        print(f"  Title: {task.title}")
        print(f"  Status: {task.status}")
        return 0
    
    # 默认显示状态
    report = tracker.generate_report()
    print_report(report)
    return 0


if __name__ == '__main__':
    sys.exit(main())
