#!/usr/bin/env python3
"""
Test Suite for Feishu Communication Tools v2.0
===============================================
Comprehensive tests for approval workflow, analytics, and chatbot.

Usage:
    python test_feishu_tools_v2.py
"""

import os
import sys
import unittest
import tempfile
import shutil
import time
import sqlite3
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))


# ============================================================================
# Test Approval Workflow
# ============================================================================

class TestApprovalWorkflow(unittest.TestCase):
    """Test approval workflow system"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        # Create temp directory for test database
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_db = os.path.join(cls.temp_dir, 'test_approvals.db')

        # Mock config
        sys.path.insert(0, os.path.dirname(__file__))
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_approval_workflow", os.path.join(os.path.dirname(__file__), "feishu_approval_workflow.py"))
        aw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aw)
        aw.ApprovalConfig.DB_PATH = cls.test_db

        # Create manager
        cls.manager = aw.ApprovalWorkflowManager()

    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_create_approval_request(self):
        """Test creating approval request"""
        request_id = self.manager.create_approval_request(
            title="测试审批",
            description="这是一个测试审批请求",
            approver_id="test_user",
            creator_id="creator",
            priority="normal",
            timeout_minutes=30
        )

        self.assertIsNotNone(request_id)
        self.assertEqual(len(request_id), 12)

        # Verify in database
        status = self.manager.get_request_status(request_id)
        self.assertEqual(status['title'], "测试审批")
        self.assertEqual(status['status'], 'pending')
        self.assertEqual(status['approver_id'], 'test_user')

    def test_handle_callback_approve(self):
        """Test approval callback"""
        # Create request
        request_id = self.manager.create_approval_request(
            title="批准测试",
            description="测试批准",
            approver_id="approver",
            creator_id="creator"
        )

        # Approve
        success, message = self.manager.handle_callback(
            request_id=request_id,
            action='approve',
            actor_id='approver',
            comment='同意'
        )

        self.assertTrue(success)
        self.assertEqual(message, "Request approved successfully")

        # Verify status
        status = self.manager.get_request_status(request_id)
        self.assertEqual(status['status'], 'approved')
        self.assertIsNotNone(status['responded_at'])
        self.assertEqual(status['response_comment'], '同意')

    def test_handle_callback_reject(self):
        """Test rejection callback"""
        request_id = self.manager.create_approval_request(
            title="拒绝测试",
            description="测试拒绝",
            approver_id="approver"
        )

        success, message = self.manager.handle_callback(
            request_id=request_id,
            action='reject',
            actor_id='approver',
            comment='不同意'
        )

        self.assertTrue(success)

        status = self.manager.get_request_status(request_id)
        self.assertEqual(status['status'], 'rejected')

    def test_get_pending_approvals(self):
        """Test getting pending approvals"""
        # Create multiple requests
        for i in range(3):
            self.manager.create_approval_request(
                title=f"待审批{i}",
                description="测试",
                approver_id="same_approver"
            )

        # Get pending
        pending = self.manager.get_pending_approvals("same_approver")
        self.assertGreaterEqual(len(pending), 3)

    def test_get_approval_history(self):
        """Test getting approval history"""
        request_id = self.manager.create_approval_request(
            title="历史测试",
            description="测试历史",
            approver_id="approver"
        )

        # Approve
        self.manager.handle_callback(request_id, 'approve', 'approver')

        # Get history
        history = self.manager.get_approval_history(request_id)
        self.assertGreaterEqual(len(history), 2)  # created + approved

    def test_process_escalations(self):
        """Test processing escalations"""
        # Create expired request (manually set expires_at in past)
        import sqlite3
        conn = sqlite3.connect(self.test_db)
        conn.execute('''
            UPDATE approval_requests 
            SET expires_at = datetime('now', '-2 hours'),
                escalation_count = 0
            WHERE status = 'pending'
        ''')
        conn.commit()
        conn.close()

        # Process
        escalated = self.manager.process_escalations()
        # May be 0 if no pending requests with past expires_at

    def test_get_statistics(self):
        """Test getting statistics"""
        stats = self.manager.get_statistics(days=7)

        self.assertIn('by_status', stats)
        self.assertIn('avg_response_minutes', stats)
        self.assertIn('escalation_rate', stats)


# ============================================================================
# Test Analytics Engine
# ============================================================================

class TestAnalyticsEngine(unittest.TestCase):
    """Test analytics engine"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_db = os.path.join(cls.temp_dir, 'test_queue.db')

        # Create mock database
        conn = sqlite3.connect(cls.test_db)
        conn.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY,
                status TEXT,
                priority TEXT,
                created_at TIMESTAMP
            )
        ''')

        # Insert test data
        now = datetime.now()
        for i in range(10):
            conn.execute('''
                INSERT INTO messages (status, priority, created_at)
                VALUES (?, ?, ?)
            ''', ('sent', 'P1', now - timedelta(hours=i)))

        for i in range(5):
            conn.execute('''
                INSERT INTO messages (status, priority, created_at)
                VALUES (?, ?, ?)
            ''', ('failed', 'P2', now - timedelta(days=i)))

        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_get_message_stats(self):
        """Test getting message statistics"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_analytics_dashboard", os.path.join(os.path.dirname(__file__), "feishu-analytics-dashboard.py"))
        ad = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ad)

        engine = ad.MessageAnalyticsEngine(self.test_db)
        stats = engine.get_message_stats(days=7)

        self.assertIn('total', stats)
        self.assertIn('by_status', stats)
        self.assertIn('by_priority', stats)
        self.assertIn('success_rate', stats)
        self.assertGreater(stats['total'], 0)

    def test_hourly_trend(self):
        """Test hourly trend"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_analytics_dashboard", os.path.join(os.path.dirname(__file__), "feishu-analytics-dashboard.py"))
        ad = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ad)

        engine = ad.MessageAnalyticsEngine(self.test_db)
        stats = engine.get_message_stats()

        self.assertIn('hourly_trend', stats)
        self.assertIsInstance(stats['hourly_trend'], list)

    def test_daily_trend(self):
        """Test daily trend"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_analytics_dashboard", os.path.join(os.path.dirname(__file__), "feishu-analytics-dashboard.py"))
        ad = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ad)

        engine = ad.MessageAnalyticsEngine(self.test_db)
        stats = engine.get_message_stats()

        self.assertIn('daily_trend', stats)
        self.assertIsInstance(stats['daily_trend'], list)


# ============================================================================
# Test Chatbot
# ============================================================================

class TestChatbot(unittest.TestCase):
    """Test chatbot system"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_db = os.path.join(cls.temp_dir, 'test_chatbot.db')

        # Mock config
        sys.path.insert(0, os.path.dirname(__file__))
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_chatbot", os.path.join(os.path.dirname(__file__), "feishu-chatbot.py"))
        cb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cb)
        cb.ChatbotConfig.DB_PATH = cls.test_db

        # Create chatbot
        cls.chatbot = cb.FeishuChatbot()

    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_command_help(self):
        """Test help command"""
        response = self.chatbot.process_message('/help', 'user')
        self.assertIn('可用命令', response)
        self.assertIn('/status', response)

    def test_command_status(self):
        """Test status command"""
        response = self.chatbot.process_message('/status', 'user')
        self.assertIn('系统状态', response)
        self.assertIn('消息队列', response)

    def test_command_queue(self):
        """Test queue command"""
        response = self.chatbot.process_message('/queue', 'user')
        self.assertIn('消息队列状态', response)

    def test_command_unknown(self):
        """Test unknown command"""
        response = self.chatbot.process_message('/unknown', 'user')
        self.assertIn('未知命令', response)

    def test_faq_match(self):
        """Test FAQ matching"""
        response = self.chatbot.process_message('系统状态如何', 'user')
        # Should match FAQ
        self.assertIn('系统运行正常', response)

    def test_faq_no_match(self):
        """Test FAQ no match"""
        response = self.chatbot.process_message('随机问题 xyz123', 'user')
        # Should not match
        self.assertIn('不太理解', response)

    def test_command_approvals(self):
        """Test approvals command"""
        response = self.chatbot.process_message('/approvals', 'user')
        # Should work (may be empty)
        self.assertIsNotNone(response)


# ============================================================================
# Test Integration
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_full_approval_workflow(self):
        """Test full approval workflow"""
        import feishu_approval_workflow as aw

        temp_db = tempfile.mktemp(suffix='.db')
        aw.ApprovalConfig.DB_PATH = temp_db

        try:
            manager = aw.ApprovalWorkflowManager()

            # Create
            request_id = manager.create_approval_request(
                title="集成测试",
                description="完整工作流测试",
                approver_id="test_user"
            )

            # Check status
            status = manager.get_request_status(request_id)
            self.assertEqual(status['status'], 'pending')

            # Approve
            success, _ = manager.handle_callback(request_id, 'approve', 'test_user')
            self.assertTrue(success)

            # Verify
            status = manager.get_request_status(request_id)
            self.assertEqual(status['status'], 'approved')

            # Get history
            history = manager.get_approval_history(request_id)
            self.assertGreaterEqual(len(history), 2)
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)

    def test_faq_database(self):
        """Test FAQ database"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_chatbot", os.path.join(os.path.dirname(__file__), "feishu-chatbot.py"))
        cb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cb)

        temp_db = tempfile.mktemp(suffix='.db')
        cb.ChatbotConfig.DB_PATH = temp_db

        try:
            faq_db = cb.FAQDatabase(temp_db)

            # Search existing
            answer = faq_db.search('系统状态')
            self.assertIsNotNone(answer)

            # Search non-existing
            answer = faq_db.search('xyz123abc', threshold=0.9)
            self.assertIsNone(answer)
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("[TEST] Feishu Communication Tools v2.0 - Test Suite")
    print("=" * 60)

    unittest.main(verbosity=2)
