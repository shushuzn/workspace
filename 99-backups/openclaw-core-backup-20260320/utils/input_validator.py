#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input Validator
输入验证器
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

class ValidationError(Exception):
    """验证失败异常"""
    pass

class InputValidator:
    """输入验证器"""

    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            format: 日期格式
            
        Returns:
            是否有效
            
        Raises:
            ValidationError: 验证失败
        """
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            raise ValidationError(f"Invalid date format: {date_str}. Expected: {format}")

    @staticmethod
    def validate_arxiv_id(arxiv_id: str) -> bool:
        """
        验证 arXiv ID 格式
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            是否有效
            
        Raises:
            ValidationError: 验证失败
        """
        # 格式：YYMM.NNNNN 或 arXiv:YYMM.NNNNN
        pattern = r'^(arXiv:)?\d{4}\.\d{4,5}$'
        if not re.match(pattern, arxiv_id):
            raise ValidationError(f"Invalid arXiv ID format: {arxiv_id}")
        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否有效
            
        Raises:
            ValidationError: 验证失败
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError(f"Invalid email format: {email}")
        return True

    @staticmethod
    def validate_api_key(api_key: str, min_length: int = 8) -> bool:
        """
        验证 API Key
        
        Args:
            api_key: API Key
            min_length: 最小长度
            
        Returns:
            是否有效
            
        Raises:
            ValidationError: 验证失败
        """
        if not api_key:
            raise ValidationError("API key is required")
        if len(api_key) < min_length:
            raise ValidationError(f"API key too short (min {min_length} characters)")
        return True

    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = False) -> Path:
        """
        验证文件路径
        
        Args:
            file_path: 文件路径
            must_exist: 是否必须存在
            
        Returns:
            Path 对象
            
        Raises:
            ValidationError: 验证失败
        """
        try:
            path = Path(file_path)

            if must_exist and not path.exists():
                raise ValidationError(f"File not found: {file_path}")

            return path
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Invalid file path: {file_path}")

    @staticmethod
    def validate_json(data: Any, required_fields: List[str] = None) -> bool:
        """
        验证 JSON 数据
        
        Args:
            data: JSON 数据
            required_fields: 必填字段列表
            
        Returns:
            是否有效
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        if required_fields:
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {missing_fields}")

        return True

    @staticmethod
    def validate_integer(value: Any, min_value: int = None, max_value: int = None) -> int:
        """
        验证整数
        
        Args:
            value: 值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            整数值
            
        Raises:
            ValidationError: 验证失败
        """
        try:
            int_value = int(value)

            if min_value is not None and int_value < min_value:
                raise ValidationError(f"Value too small (min {min_value})")
            if max_value is not None and int_value > max_value:
                raise ValidationError(f"Value too large (max {max_value})")

            return int_value
        except ValueError:
            raise ValidationError(f"Invalid integer: {value}")

    @staticmethod
    def validate_string(value: Any, min_length: int = None, max_length: int = None, pattern: str = None) -> str:
        """
        验证字符串
        
        Args:
            value: 值
            min_length: 最小长度
            max_length: 最大长度
            pattern: 正则表达式模式
            
        Returns:
            字符串值
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(value, str):
            raise ValidationError(f"Invalid string: {value}")

        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"String too short (min {min_length} characters)")
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")

        if pattern is not None and not re.match(pattern, value):
            raise ValidationError(f"String does not match pattern: {pattern}")

        return value

    @staticmethod
    def validate_list(value: Any, item_type: type = None, min_length: int = None, max_length: int = None) -> list:
        """
        验证列表
        
        Args:
            value: 值
            item_type: 项类型
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            列表值
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(value, list):
            raise ValidationError(f"Invalid list: {value}")

        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"List too short (min {min_length} items)")
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"List too long (max {max_length} items)")

        if item_type is not None:
            for i, item in enumerate(value):
                if not isinstance(item, item_type):
                    raise ValidationError(f"Invalid item type at index {i}: expected {item_type}, got {type(item)}")

        return value

# 示例用法
if __name__ == "__main__":
    validator = InputValidator()

    # 测试日期验证
    try:
        validator.validate_date("2026-03-05")
        print("✓ Date validation passed")
    except ValidationError as e:
        print(f"✗ Date validation failed: {e}")

    # 测试 arXiv ID 验证
    try:
        validator.validate_arxiv_id("2603.00267")
        print("✓ arXiv ID validation passed")
    except ValidationError as e:
        print(f"✗ arXiv ID validation failed: {e}")

    # 测试整数验证
    try:
        validator.validate_integer("42", min_value=0, max_value=100)
        print("✓ Integer validation passed")
    except ValidationError as e:
        print(f"✗ Integer validation failed: {e}")

    # 测试字符串验证
    try:
        validator.validate_string("test", min_length=2, max_length=10)
        print("✓ String validation passed")
    except ValidationError as e:
        print(f"✗ String validation failed: {e}")
