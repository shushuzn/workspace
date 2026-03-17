#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Framework - Run All Tests
测试框架 - 运行所有测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Running All Tests")
    print("=" * 60)
    
    # 发现测试
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    
    suite = loader.discover(start_dir=str(start_dir), pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
