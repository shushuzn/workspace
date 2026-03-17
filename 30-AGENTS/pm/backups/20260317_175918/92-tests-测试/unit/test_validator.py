#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Input Validator
输入验证器单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.input_validator import InputValidator, ValidationError

class TestInputValidator(unittest.TestCase):
    """输入验证器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.validator = InputValidator()
    
    def test_validate_date_valid(self):
        """测试有效日期"""
        result = self.validator.validate_date("2026-03-05")
        self.assertTrue(result)
    
    def test_validate_date_invalid(self):
        """测试无效日期"""
        with self.assertRaises(ValidationError):
            self.validator.validate_date("invalid-date")
    
    def test_validate_arxiv_id_valid(self):
        """测试有效 arXiv ID"""
        result = self.validator.validate_arxiv_id("2603.00267")
        self.assertTrue(result)
        
        result = self.validator.validate_arxiv_id("arXiv:2603.00267")
        self.assertTrue(result)
    
    def test_validate_arxiv_id_invalid(self):
        """测试无效 arXiv ID"""
        with self.assertRaises(ValidationError):
            self.validator.validate_arxiv_id("invalid")
        
        with self.assertRaises(ValidationError):
            self.validator.validate_arxiv_id("2603.267")
    
    def test_validate_email_valid(self):
        """测试有效邮箱"""
        result = self.validator.validate_email("test@example.com")
        self.assertTrue(result)
    
    def test_validate_email_invalid(self):
        """测试无效邮箱"""
        with self.assertRaises(ValidationError):
            self.validator.validate_email("invalid-email")
    
    def test_validate_api_key_valid(self):
        """测试有效 API Key"""
        result = self.validator.validate_api_key("valid-key-123")
        self.assertTrue(result)
    
    def test_validate_api_key_invalid(self):
        """测试无效 API Key"""
        with self.assertRaises(ValidationError):
            self.validator.validate_api_key("")
        
        with self.assertRaises(ValidationError):
            self.validator.validate_api_key("short")
    
    def test_validate_integer_valid(self):
        """测试有效整数"""
        result = self.validator.validate_integer("42", min_value=0, max_value=100)
        self.assertEqual(result, 42)
    
    def test_validate_integer_invalid(self):
        """测试无效整数"""
        with self.assertRaises(ValidationError):
            self.validator.validate_integer("not-a-number")
        
        with self.assertRaises(ValidationError):
            self.validator.validate_integer(150, min_value=0, max_value=100)
    
    def test_validate_string_valid(self):
        """测试有效字符串"""
        result = self.validator.validate_string("test", min_length=2, max_length=10)
        self.assertEqual(result, "test")
    
    def test_validate_string_invalid(self):
        """测试无效字符串"""
        with self.assertRaises(ValidationError):
            self.validator.validate_string("a", min_length=2)
        
        with self.assertRaises(ValidationError):
            self.validator.validate_string("very long string", max_length=5)
    
    def test_validate_list_valid(self):
        """测试有效列表"""
        result = self.validator.validate_list([1, 2, 3], item_type=int)
        self.assertEqual(result, [1, 2, 3])
    
    def test_validate_list_invalid(self):
        """测试无效列表"""
        with self.assertRaises(ValidationError):
            self.validator.validate_list("not-a-list")
        
        with self.assertRaises(ValidationError):
            self.validator.validate_list([1, "two", 3], item_type=int)

if __name__ == '__main__':
    unittest.main(verbosity=2)
