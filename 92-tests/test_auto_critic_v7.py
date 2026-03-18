#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Auto-Critic v7.0

测试 Auto-Critic v7.0 核心功能
"""

import unittest
import json
from pathlib import Path
from datetime import datetime

# 导入被测试模块
import sys
SCRIPTS_DIR = Path(__file__).parent.parent / '30-scripts-tools'
sys.path.insert(0, str(SCRIPTS_DIR))


class TestRemediationTracker(unittest.TestCase):
    """测试整改跟踪器"""
    
    def test_task_creation(self):
        """测试任务创建"""
        from remediation_tracker import RemediationTracker, TaskStatus
        
        tracker = RemediationTracker(SCRIPTS_DIR.parent)
        
        # 创建测试任务
        fail_items = [{
            'id': 'test-001',
            'item': 'Test Item',
            'level': 'warning',
            'notes': 'Test notes',
            'evidence': 'Test evidence'
        }]
        
        task_ids = tracker.create_tasks(fail_items, 'test', 'claw')
        
        self.assertEqual(len(task_ids), 1)
        self.assertTrue(task_ids[0].startswith('REM-'))
        
        # 验证任务存在
        self.assertIn(task_ids[0], tracker.tasks)
    
    def test_task_status_update(self):
        """测试任务状态更新"""
        from remediation_tracker import RemediationTracker, TaskStatus
        
        tracker = RemediationTracker(SCRIPTS_DIR.parent)
        
        # 创建任务
        fail_items = [{
            'id': 'test-002',
            'item': 'Test Item 2',
            'level': 'warning',
            'notes': '',
            'evidence': ''
        }]
        
        task_ids = tracker.create_tasks(fail_items, 'test', 'claw')
        task_id = task_ids[0]
        
        # 更新状态
        tracker.update_status(task_id, TaskStatus.IN_PROGRESS.value)
        
        self.assertEqual(tracker.tasks[task_id].status, TaskStatus.IN_PROGRESS.value)
    
    def test_statistics_calculation(self):
        """测试统计计算"""
        from remediation_tracker import RemediationTracker
        
        tracker = RemediationTracker(SCRIPTS_DIR.parent)
        stats = tracker._calculate_statistics()
        
        self.assertIn('total_tasks', stats)
        self.assertIn('by_status', stats)
        self.assertIn('by_severity', stats)


class TestQualityGate(unittest.TestCase):
    """测试质量门禁"""
    
    def test_complexity_calculation(self):
        """测试圈复杂度计算"""
        import ast
        from quality_gate import QualityGateChecker
        
        # 简单函数
        code = """
def simple():
    if True:
        return 1
    return 0
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        checker = QualityGateChecker(SCRIPTS_DIR.parent)
        complexity = checker._calculate_complexity(func_node)
        
        # if 语句增加 1 个复杂度，基础复杂度 1
        self.assertEqual(complexity, 2)
    
    def test_complexity_with_loops(self):
        """测试带循环的复杂度"""
        import ast
        from quality_gate import QualityGateChecker
        
        code = """
def complex():
    for i in range(10):
        if i > 5:
            while True:
                break
    return 0
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        checker = QualityGateChecker(SCRIPTS_DIR.parent)
        complexity = checker._calculate_complexity(func_node)
        
        # for(1) + if(1) + while(1) + base(1) = 4
        self.assertEqual(complexity, 4)


class TestIssueScanner(unittest.TestCase):
    """测试问题扫描器"""
    
    def test_scanner_initialization(self):
        """测试扫描器初始化"""
        from issue_scanner import IssueScanner
        
        scanner = IssueScanner(SCRIPTS_DIR.parent)
        
        self.assertIsNotNone(scanner.workspace)
        self.assertEqual(len(scanner.issues), 0)


class TestCriticalIssueDetector(unittest.TestCase):
    """测试严重问题检测器"""
    
    def test_detector_initialization(self):
        """测试检测器初始化"""
        from critical_issue_detector import CriticalIssueDetector
        
        detector = CriticalIssueDetector(SCRIPTS_DIR.parent)
        
        self.assertIsNotNone(detector.workspace)


if __name__ == '__main__':
    unittest.main()
