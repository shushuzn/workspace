#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Data Validator
数据验证插件 - 验证输入数据的完整性和格式

功能:
- 必填字段验证
- 类型验证 (string/list/int/float/bool)
- 长度验证 (min_length/max_length)
- 值范围验证 (min_value/max_value)
- 自定义规则验证

示例:
    >>> validator = DataValidatorPlugin()
    >>> validator.initialize({
    ...     'required_fields': ['name', 'email'],
    ...     'validation_rules': {
    ...         'name': {'type': 'string', 'min_length': 1},
    ...         'age': {'type': 'int', 'min_value': 0, 'max_value': 150}
    ...     }
    ... })
    >>> result = validator.process({'name': 'Alice', 'age': 25})
    >>> print(result['validation_status'])
    'valid'
"""

from typing import Dict, Any, List, Optional
from scripts.utils.plugin_system import BasePlugin


class DataValidatorPlugin(BasePlugin):
    """数据验证插件 - 提供灵活的数据验证功能"""
    
    name = "data_validator"
    version = "1.1.0"  # 优化版本
    description = "Validate input data with comprehensive rules"
    
    def __init__(self) -> None:
        """初始化验证器"""
        self.required_fields: List[str] = []
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        self._error_count: int = 0
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        初始化插件配置
        
        Args:
            config: 配置字典，包含 required_fields 和 validation_rules
        """
        self.required_fields = config.get('required_fields', [])
        self.validation_rules = config.get('validation_rules', {})
        self._error_count = 0
        print(f"[DataValidator] Initialized: {len(self.required_fields)} required fields, "
              f"{len(self.validation_rules)} validation rules")
    
    def _add_error(self, data: Dict[str, Any], error: str) -> None:
        """
        添加验证错误
        
        Args:
            data: 数据字典
            error: 错误信息
        """
        if 'validation_errors' not in data:
            data['validation_errors'] = []
        data['validation_errors'].append(error)
        self._error_count += 1
    
    def _validate_type(self, field: str, value: Any, rule: Dict[str, Any], 
                       data: Dict[str, Any]) -> bool:
        """
        验证字段类型
        
        Args:
            field: 字段名
            value: 字段值
            rule: 验证规则
            data: 数据字典
            
        Returns:
            bool: 类型是否有效
        """
        type_map = {
            'string': str,
            'str': str,
            'list': list,
            'int': int,
            'integer': int,
            'float': (int, float),
            'number': (int, float),
            'bool': bool,
            'boolean': bool,
            'dict': dict,
        }
        
        expected_type = rule.get('type')
        if not expected_type:
            return True
        
        python_type = type_map.get(expected_type.lower())
        if not python_type:
            return True
        
        if not isinstance(value, python_type):
            self._add_error(data, f"Field '{field}' must be {expected_type}, got {type(value).__name__}")
            return False
        return True
    
    def _validate_constraints(self, field: str, value: Any, rule: Dict[str, Any],
                              data: Dict[str, Any]) -> None:
        """
        验证字段约束 (长度/范围)
        
        Args:
            field: 字段名
            value: 字段值
            rule: 验证规则
            data: 数据字典
        """
        # 长度验证
        if isinstance(value, (str, list, dict)):
            if 'min_length' in rule and len(value) < rule['min_length']:
                self._add_error(data, f"Field '{field}' length must be ≥{rule['min_length']}")
            if 'max_length' in rule and len(value) > rule['max_length']:
                self._add_error(data, f"Field '{field}' length must be ≤{rule['max_length']}")
        
        # 范围验证 (数字)
        if isinstance(value, (int, float)):
            if 'min_value' in rule and value < rule['min_value']:
                self._add_error(data, f"Field '{field}' must be ≥{rule['min_value']}")
            if 'max_value' in rule and value > rule['max_value']:
                self._add_error(data, f"Field '{field}' must be ≤{rule['max_value']}")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理数据验证
        
        Args:
            data: 待验证的数据字典
            
        Returns:
            Dict: 包含 validation_status 和可选 validation_errors 的结果
        """
        self._error_count = 0
        
        # 验证必填字段
        for field in self.required_fields:
            if field not in data:
                self._add_error(data, f"Missing required field: '{field}'")
        
        # 验证规则
        for field, rule in self.validation_rules.items():
            if field not in data:
                continue  # 非必填字段跳过
            
            value = data[field]
            
            # 类型验证
            if not self._validate_type(field, value, rule, data):
                continue  # 类型错误时跳过后续验证
            
            # 约束验证
            self._validate_constraints(field, value, rule, data)
        
        # 添加验证状态和统计
        data['validation_status'] = 'valid' if self._error_count == 0 else 'invalid'
        data['validation_error_count'] = self._error_count
        
        return data
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取验证统计信息
        
        Returns:
            Dict: 包含 required_fields_count 和 rules_count 的统计
        """
        return {
            'required_fields_count': len(self.required_fields),
            'validation_rules_count': len(self.validation_rules),
        }
    
    def shutdown(self) -> None:
        """关闭插件，清理资源"""
        print(f"[DataValidator] Shutdown: processed {self._error_count} errors")
        self.required_fields = []
        self.validation_rules = {}
