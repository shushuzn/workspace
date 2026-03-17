#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Data Transformer
数据转换插件
"""

from typing import Dict, Any
from scripts.utils.plugin_system import BasePlugin

class DataTransformerPlugin(BasePlugin):
    """数据转换插件"""
    
    name = "data_transformer"
    version = "1.0.0"
    description = "Transform data format"
    
    def __init__(self):
        self.transformations = []
    
    def initialize(self, config: Dict) -> None:
        """初始化插件"""
        self.transformations = config.get('transformations', [])
        print(f"DataTransformerPlugin initialized with {len(self.transformations)} transformations")
    
    def process(self, data: Dict) -> Dict:
        """处理数据 (转换)"""
        result = data.copy()
        
        for transformation in self.transformations:
            transform_type = transformation.get('type')
            
            if transform_type == 'rename':
                old_key = transformation.get('old_key')
                new_key = transformation.get('new_key')
                if old_key in result:
                    result[new_key] = result.pop(old_key)
            
            elif transform_type == 'add_field':
                field_name = transformation.get('field')
                field_value = transformation.get('value')
                result[field_name] = field_value
            
            elif transform_type == 'remove_field':
                field_name = transformation.get('field')
                if field_name in result:
                    del result[field_name]
        
        return result
    
    def shutdown(self) -> None:
        """关闭插件"""
        print("DataTransformerPlugin shutdown")
