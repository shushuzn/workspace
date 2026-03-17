#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Retry Manager
重试管理器单元测试
"""

import unittest
import sys
from pathlib import Path
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.retry_manager import retry, RetryManager, RetryError

class TestRetryDecorator(unittest.TestCase):
    """重试装饰器测试"""
    
    def test_retry_success(self):
        """测试重试成功"""
        call_count = [0]
        
        @retry(max_attempts=3, delay_seconds=0.1)
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary error")
            return "Success"
        
        result = flaky_function()
        self.assertEqual(result, "Success")
        self.assertEqual(call_count[0], 3)
    
    def test_retry_failure(self):
        """测试重试失败"""
        @retry(max_attempts=3, delay_seconds=0.1)
        def always_fails():
            raise ValueError("Always fails")
        
        with self.assertRaises(RetryError):
            always_fails()
    
    def test_retry_with_backoff(self):
        """测试指数退避"""
        call_times = []
        
        @retry(max_attempts=3, delay_seconds=0.1, backoff_factor=2)
        def slow_fails():
            call_times.append(time.time())
            raise ValueError("Fails")
        
        with self.assertRaises(RetryError):
            slow_fails()
        
        # 检查退避时间
        self.assertEqual(len(call_times), 3)
        # 第二次调用应该比第一次晚至少 0.1 秒
        self.assertGreater(call_times[1] - call_times[0], 0.1)
        # 第三次调用应该比第二次晚至少 0.2 秒
        self.assertGreater(call_times[2] - call_times[1], 0.2)

class TestRetryManager(unittest.TestCase):
    """重试管理器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.manager = RetryManager(max_attempts=3, delay_seconds=0.1)
    
    def test_execute_success(self):
        """测试执行成功"""
        def success_function():
            return "Success"
        
        result = self.manager.execute(success_function)
        self.assertEqual(result, "Success")
        self.assertEqual(self.manager.stats['successful_calls'], 1)
    
    def test_execute_failure(self):
        """测试执行失败"""
        def fail_function():
            raise ValueError("Fails")
        
        with self.assertRaises(RetryError):
            self.manager.execute(fail_function)
        
        self.assertEqual(self.manager.stats['failed_calls'], 1)
    
    def test_execute_with_retries(self):
        """测试执行带重试"""
        call_count = [0]
        
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary error")
            return "Success"
        
        result = self.manager.execute(flaky_function)
        self.assertEqual(result, "Success")
        self.assertEqual(call_count[0], 3)
    
    def test_get_stats(self):
        """测试获取统计"""
        def success():
            return "OK"
        
        def fail():
            raise ValueError("Fail")
        
        # 执行成功
        self.manager.execute(success)
        
        # 执行失败
        try:
            self.manager.execute(fail)
        except:
            pass
        
        stats = self.manager.get_stats()
        self.assertIn('total_calls', stats)
        self.assertIn('successful_calls', stats)
        self.assertIn('failed_calls', stats)
        self.assertIn('total_retries', stats)

if __name__ == '__main__':
    unittest.main(verbosity=2)
