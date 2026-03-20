#!/usr/bin/env py
# -*- coding: utf-8 -*-
"""
Unit Tests for Stock Analysis Pipeline

测试股票分析统一管道

作者：Claw
创建：2026-03-20
版本：v1.0.0
"""

import unittest
import sys
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# 添加项目路径
WORKSPACE = Path("D:/OpenClaw/workspace")
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))

from stock_analysis_pipeline import StockAnalysisPipeline


class TestStockAnalysisPipeline(unittest.TestCase):
    """股票分析管道测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_symbol = "TEST"
        self.test_dir = tempfile.mkdtemp()
        self.pipeline = StockAnalysisPipeline(
            symbol=self.test_symbol,
            output_dir=Path(self.test_dir)
        )
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.pipeline.symbol, "TEST")
        self.assertEqual(len(self.pipeline.phase2_tools), 8)
        self.assertIsInstance(self.pipeline.output_dir, Path)
        self.assertTrue(self.pipeline.output_dir.exists())
    
    def test_mock_data_generation(self):
        """测试模拟数据生成"""
        for tool_id in ["SA-005", "SA-006", "SA-007", "SA-008", 
                        "SA-009", "SA-010", "SA-011", "SA-012"]:
            mock_data = self.pipeline._generate_mock_data(tool_id)
            self.assertIsInstance(mock_data, dict)
            self.assertTrue(len(mock_data) > 0)
    
    def test_pipeline_execution(self):
        """测试管道执行"""
        results = self.pipeline.run()
        
        # 验证结果结构
        self.assertIn("symbol", results)
        self.assertIn("timestamp", results)
        self.assertIn("stages", results)
        self.assertEqual(results["symbol"], "TEST")
        
        # 验证所有工具都执行了
        self.assertEqual(len(results["stages"]), 8)
        
        # 验证每个工具都有结果
        for tool_id in ["SA-005", "SA-006", "SA-007", "SA-008",
                        "SA-009", "SA-010", "SA-011", "SA-012"]:
            self.assertIn(tool_id, results["stages"])
            self.assertIn("status", results["stages"][tool_id])
    
    def test_metrics_collection(self):
        """测试指标收集"""
        self.pipeline.run()
        
        metrics = self.pipeline.metrics
        self.assertIn("start_time", metrics)
        self.assertIn("end_time", metrics)
        self.assertIn("total_duration", metrics)
        self.assertIn("stage_times", metrics)
        
        # 验证所有阶段都有时间记录
        self.assertEqual(len(metrics["stage_times"]), 8)
    
    def test_json_report_generation(self):
        """测试 JSON 报告生成"""
        self.pipeline.run()
        
        # 查找生成的 JSON 文件
        json_files = list(self.pipeline.output_dir.glob("*.json"))
        self.assertTrue(len(json_files) > 0)
        
        # 验证 JSON 文件可读
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn("symbol", data)
            self.assertIn("stages", data)
    
    def test_markdown_report_generation(self):
        """测试 Markdown 报告生成"""
        self.pipeline.run()
        
        # 查找生成的 Markdown 文件
        md_files = list(self.pipeline.output_dir.glob("*.md"))
        self.assertTrue(len(md_files) > 0)
        
        # 验证 Markdown 文件内容
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("TEST", content)
            self.assertIn("Stock Analysis Report", content)
    
    def test_html_report_generation(self):
        """测试 HTML 报告生成"""
        self.pipeline.run()
        
        # 查找生成的 HTML 文件
        html_files = list(self.pipeline.output_dir.glob("*.html"))
        self.assertTrue(len(html_files) > 0)
        
        # 验证 HTML 文件内容
        with open(html_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<html", content)
            self.assertIn("</html>", content)
            self.assertIn("TEST", content)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效股票代码
        pipeline = StockAnalysisPipeline(symbol="INVALID_SYMBOL_12345")
        results = pipeline.run()
        
        # 应该仍然能生成报告 (使用模拟数据)
        self.assertIn("symbol", results)
        self.assertEqual(results["symbol"], "INVALID_SYMBOL_12345")
    
    def test_performance(self):
        """测试性能 (所有工具执行时间 < 5 秒)"""
        import time
        start = time.time()
        self.pipeline.run()
        duration = time.time() - start
        
        # 使用模拟数据应该在 1 秒内完成
        self.assertLess(duration, 5.0, "Pipeline execution too slow")
    
    def test_output_directory_creation(self):
        """测试输出目录自动创建"""
        nested_dir = Path(self.test_dir) / "subdir1" / "subdir2"
        pipeline = StockAnalysisPipeline(
            symbol="TEST",
            output_dir=nested_dir
        )
        
        self.assertTrue(nested_dir.exists())
        self.assertTrue(nested_dir.is_dir())


class TestPipelineIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        test_dir = tempfile.mkdtemp()
        try:
            pipeline = StockAnalysisPipeline(
                symbol="AAPL",
                output_dir=Path(test_dir)
            )
            
            results = pipeline.run()
            
            # 验证生成了所有类型的报告
            json_files = list(Path(test_dir).glob("*.json"))
            md_files = list(Path(test_dir).glob("*.md"))
            html_files = list(Path(test_dir).glob("*.html"))
            
            self.assertTrue(len(json_files) > 0)
            self.assertTrue(len(md_files) > 0)
            self.assertTrue(len(html_files) > 0)
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
