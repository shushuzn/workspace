#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Plugin System
插件系统单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.plugin_system import PluginManager, BasePlugin

class TestPluginManager(unittest.TestCase):
    """插件管理器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.manager = PluginManager()
    
    def test_discover_plugins(self):
        """测试发现插件"""
        plugins = self.manager.discover_plugins()
        # 应该发现示例插件
        self.assertIn('example', plugins)
        self.assertIn('data_enrichment', plugins)
    
    def test_load_plugin(self):
        """测试加载插件"""
        result = self.manager.load_plugin("example", {"setting": "value"})
        self.assertTrue(result)
        self.assertIn("example", self.manager.plugins)
    
    def test_unload_plugin(self):
        """测试卸载插件"""
        # 先加载
        self.manager.load_plugin("example")
        
        # 卸载
        result = self.manager.unload_plugin("example")
        self.assertTrue(result)
        self.assertNotIn("example", self.manager.plugins)
    
    def test_process_all(self):
        """测试处理所有插件"""
        # 加载插件
        self.manager.load_plugin("example")
        self.manager.load_plugin("data_enrichment")
        
        # 处理数据
        data = {"input": "test"}
        result = self.manager.process_all(data)
        
        # 检查处理结果
        self.assertIn("processed_by", result)
        self.assertIn("enriched_at", result)
    
    def test_get_plugin_info(self):
        """测试获取插件信息"""
        self.manager.load_plugin("example", {"config": "value"})
        
        info = self.manager.get_plugin_info("example")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'example')
        self.assertEqual(info['config'], {'config': 'value'})
    
    def test_list_plugins(self):
        """测试列出插件"""
        self.manager.load_plugin("example")
        
        plugins = self.manager.list_plugins()
        
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]['name'], 'example')
    
    def test_get_stats(self):
        """测试获取统计"""
        self.manager.load_plugin("example")
        
        stats = self.manager.get_stats()
        
        self.assertEqual(stats['total_plugins'], 1)
        self.assertIn("example", stats['plugins'])

class TestBasePlugin(unittest.TestCase):
    """插件基类测试"""
    
    def test_base_plugin_abstract(self):
        """测试基类抽象方法"""
        # 不能直接实例化抽象类
        with self.assertRaises(TypeError):
            BasePlugin()

if __name__ == '__main__':
    unittest.main(verbosity=2)
