#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时蒸馏工具 v3.0 - 单元测试
"""

import unittest
import os
import sys
import tempfile
import shutil

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_time_distill_v3 import extract_key_insights, generate_memory_entry

class TestRealTimeDistill(unittest.TestCase):
    """实时蒸馏工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_note.md')
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_extract_normal_insights(self):
        """测试正常提取洞察"""
        content = """
## 测试内容

### [MEM-001] 实时蒸馏测试

这是测试内容。

### [MEM-002] 第二个测试

这是第二个测试。
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        insights = extract_key_insights(self.test_file)
        
        self.assertEqual(len(insights), 2)
        self.assertEqual(insights[0]['id'], 'MEM-001')
        self.assertEqual(insights[1]['id'], 'MEM-002')
    
    def test_extract_no_insights(self):
        """测试无洞察情况"""
        content = """
## 测试内容

没有洞察标记的普通内容。
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        insights = extract_key_insights(self.test_file)
        
        self.assertEqual(len(insights), 0)
    
    def test_extract_duplicate_id(self):
        """测试重复 ID 去重"""
        content = """
## 测试内容

### [MEM-001] 第一个标题

内容 1。

### [MEM-001] 第二个标题

内容 2。
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        insights = extract_key_insights(self.test_file)
        
        # 应该只保留第一个
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]['title'], '第一个标题')
    
    def test_extract_invalid_title(self):
        """测试无效标题过滤"""
        content = """
## 测试内容

### [MEM-001] )

这是无效标题。

### [MEM-002] 有效标题

这是有效标题。
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        insights = extract_key_insights(self.test_file)
        
        # 应该只提取有效标题
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]['id'], 'MEM-002')
    
    def test_file_not_found(self):
        """测试文件不存在情况"""
        with self.assertRaises(FileNotFoundError):
            extract_key_insights('/nonexistent/path/file.md')
    
    def test_generate_memory_entry(self):
        """测试记忆条目生成"""
        insight = {
            'id': 'TEST-001',
            'title': '测试标题',
            'source': 'test.md',
            'extracted_at': '2026-03-18 14:00'
        }
        
        entry = generate_memory_entry(insight, '')
        
        self.assertIn('[TEST-001]', entry)
        self.assertIn('测试标题', entry)
        self.assertIn('实时蒸馏 v3.0', entry)
    
    def test_extract_chinese_title(self):
        """测试中文标题提取"""
        content = """
## 测试内容

### [MEM-003] 记忆系统优化

这是中文标题测试。
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        insights = extract_key_insights(self.test_file)
        
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]['title'], '记忆系统优化')
    
    def test_extract_mixed_content(self):
        """测试混合内容提取"""
        content = """
# 日常笔记 2026-03-18

## 会话内容

一些普通内容。

### [MEM-004] 新洞察

新洞察内容。

## 其他内容

更多普通内容。

### [MEM-005] 另一个洞察

另一个洞察内容。
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        insights = extract_key_insights(self.test_file)
        
        self.assertEqual(len(insights), 2)
        self.assertEqual(insights[0]['id'], 'MEM-004')
        self.assertEqual(insights[1]['id'], 'MEM-005')

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
