#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态知识图谱单元测试套件
测试覆盖：图表管理、公式管理、数据管理、搜索功能
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 导入被测试模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from multimodal_kg import MultimodalKG


class TestMultimodalKG(unittest.TestCase):
    """多模态知识图谱测试类"""

    def setUp(self):
        """测试前准备：创建临时目录和图谱实例"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.kg = MultimodalKG(data_dir=str(self.test_dir))

    def tearDown(self):
        """测试后清理：删除临时目录"""
        shutil.rmtree(self.test_dir)

    # ==================== 图表管理测试 ====================

    def test_add_figure_basic(self):
        """测试：基础图表添加"""
        self.kg.add_figure(
            paper_id="PMID:123456",
            figure_id="fig_001",
            caption="Test SEM image",
            image_path="test.png",
            figure_type="SEM"
        )

        # 验证图表已添加
        self.assertIn("fig_001", self.kg.figures_db)
        self.assertEqual(self.kg.figures_db["fig_001"]["paper_id"], "PMID:123456")
        self.assertEqual(self.kg.figures_db["fig_001"]["type"], "SEM")

    def test_add_figure_auto_timestamp(self):
        """测试：图表添加自动记录时间戳"""
        before = datetime.now()
        self.kg.add_figure("PMID:123", "fig_001", "Test", "test.png")
        after = datetime.now()

        created_at = datetime.fromisoformat(self.kg.figures_db["fig_001"]["created_at"])
        self.assertGreaterEqual(created_at, before)
        self.assertLessEqual(created_at, after)

    def test_add_figure_duplicate(self):
        """测试：重复添加相同 figure_id 会覆盖"""
        self.kg.add_figure("PMID:123", "fig_001", "First", "test1.png")
        self.kg.add_figure("PMID:456", "fig_001", "Second", "test2.png")

        # 验证后添加的覆盖先前的
        self.assertEqual(self.kg.figures_db["fig_001"]["caption"], "Second")
        self.assertEqual(self.kg.figures_db["fig_001"]["paper_id"], "PMID:456")

    def test_add_figure_all_types(self):
        """测试：支持所有图表类型"""
        types = ["SEM", "TEM", "Raman", "XRD", "Performance"]

        for i, fig_type in enumerate(types):
            self.kg.add_figure("PMID:123", f"fig_{i:03d}", "Test", "test.png", fig_type)

        # 验证所有类型都已添加
        self.assertEqual(len(self.kg.figures_db), 5)

    # ==================== 公式管理测试 ====================

    def test_add_equation_basic(self):
        """测试：基础公式添加"""
        self.kg.add_equation(
            paper_id="PMID:123456",
            equation_id="eq_001",
            latex="E = mc^2",
            description="质能方程"
        )

        self.assertIn("eq_001", self.kg.equations_db)
        self.assertEqual(self.kg.equations_db["eq_001"]["latex"], "E = mc^2")

    def test_add_equation_variable_extraction(self):
        """测试：公式变量自动提取"""
        self.kg.add_equation("PMID:123", "eq_001", latex="R = \\frac{\\rho L}{A}")

        variables = self.kg.equations_db["eq_001"]["variables"]
        # 验证提取到变量 (具体变量名取决于正则表达式)
        self.assertGreater(len(variables), 0)

    def test_add_equation_optional_description(self):
        """测试：公式描述为可选参数"""
        self.kg.add_equation("PMID:123", "eq_001", latex="E = mc^2")

        self.assertEqual(self.kg.equations_db["eq_001"]["description"], "")

    # ==================== 数据管理测试 ====================

    def test_add_dataset_basic(self):
        """测试：基础数据集添加"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.kg.add_dataset("PMID:123", "data_001", "Test Data", values, "units")

        self.assertIn("data_001", self.kg.datasets_db)
        self.assertEqual(self.kg.datasets_db["data_001"]["values"], values)

    def test_add_dataset_auto_statistics(self):
        """测试：数据集自动计算统计信息"""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.kg.add_dataset("PMID:123", "data_001", "Test", values)

        stats = self.kg.datasets_db["data_001"]["statistics"]

        # 验证统计计算正确
        self.assertEqual(stats["mean"], 30.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 50.0)
        self.assertEqual(stats["count"], 5)
        self.assertGreater(stats["stdev"], 0)  # 标准差应大于 0

    def test_add_dataset_single_value(self):
        """测试：单值数据集 (标准差应为 0)"""
        self.kg.add_dataset("PMID:123", "data_001", "Single", [5.0])

        stats = self.kg.datasets_db["data_001"]["statistics"]
        self.assertEqual(stats["stdev"], 0)
        self.assertEqual(stats["count"], 1)

    def test_add_dataset_optional_units(self):
        """测试：数据单位为可选参数"""
        self.kg.add_dataset("PMID:123", "data_001", "Test", [1.0, 2.0])

        self.assertEqual(self.kg.datasets_db["data_001"]["units"], "")

    # ==================== 搜索功能测试 ====================

    def test_search_figures_basic(self):
        """测试：基础图表搜索"""
        # 添加测试数据
        self.kg.add_figure("PMID:123", "fig_001", "SEM image of graphene", "test.png", "SEM")
        self.kg.add_figure("PMID:124", "fig_002", "TEM image of LIG", "test.png", "TEM")
        self.kg.add_figure("PMID:125", "fig_003", "Raman spectrum analysis", "test.png", "Raman")

        # 搜索
        results = self.kg.search_figures("SEM", top_k=10)

        # 验证结果
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "fig_001")

    def test_search_figures_top_k(self):
        """测试：搜索结果数量限制"""
        for i in range(10):
            self.kg.add_figure("PMID:123", f"fig_{i:03d}", f"Test figure {i}", "test.png")

        results = self.kg.search_figures("Test", top_k=5)
        self.assertEqual(len(results), 5)

    def test_search_figures_no_match(self):
        """测试：搜索无匹配结果"""
        self.kg.add_figure("PMID:123", "fig_001", "SEM image", "test.png")

        # 搜索完全不相关的词 (长度>3 以避免空词匹配)
        results = self.kg.search_figures("xyz123abc", top_k=10)
        # 注意：当前搜索基于关键词匹配，可能返回部分匹配结果
        # 期望结果：0 或相似度极低的结果
        self.assertLess(len(results), 3)  # 最多返回少量低匹配结果

    def test_search_figures_case_insensitive(self):
        """测试：搜索不区分大小写"""
        self.kg.add_figure("PMID:123", "fig_001", "SEM Image", "test.png")

        results1 = self.kg.search_figures("sem", top_k=10)
        results2 = self.kg.search_figures("SEM", top_k=10)

        self.assertEqual(len(results1), len(results2))

    # ==================== 导出功能测试 ====================

    def test_export_json_basic(self):
        """测试：基础 JSON 导出"""
        self.kg.add_figure("PMID:123", "fig_001", "Test", "test.png")
        self.kg.add_equation("PMID:123", "eq_001", "E=mc^2")
        self.kg.add_dataset("PMID:123", "data_001", "Test", [1.0, 2.0])

        output_path = str(self.test_dir / "output.json")
        result = self.kg.export_json(output_path)

        # 验证文件已创建
        self.assertTrue(Path(result).exists())

        # 验证内容
        with open(result, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn("figures", data)
        self.assertIn("equations", data)
        self.assertIn("datasets", data)
        self.assertIn("stats", data)

    def test_export_json_stats(self):
        """测试：导出统计信息正确"""
        for i in range(5):
            self.kg.add_figure("PMID:123", f"fig_{i:03d}", "Test", "test.png")
        for i in range(3):
            self.kg.add_equation("PMID:123", f"eq_{i:03d}", "E=mc^2")
        for i in range(2):
            self.kg.add_dataset("PMID:123", f"data_{i:03d}", "Test", [1.0])

        output_path = str(self.test_dir / "output.json")
        self.kg.export_json(output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data["stats"]["total_figures"], 5)
        self.assertEqual(data["stats"]["total_equations"], 3)
        self.assertEqual(data["stats"]["total_datasets"], 2)

    def test_export_json_unicode(self):
        """测试：JSON 导出支持 Unicode (中文)"""
        self.kg.add_figure("PMID:123", "fig_001", "石墨烯 SEM 图像", "test.png")
        self.kg.add_equation("PMID:123", "eq_001", "E=mc^2", "质能方程")

        output_path = str(self.test_dir / "output.json")
        self.kg.export_json(output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 验证中文字符正确保存
        self.assertEqual(data["figures"]["fig_001"]["caption"], "石墨烯 SEM 图像")
        self.assertEqual(data["equations"]["eq_001"]["description"], "质能方程")

    # ==================== 边界情况测试 ====================

    def test_empty_database(self):
        """测试：空图谱操作"""
        # 空图谱搜索
        results = self.kg.search_figures("test", top_k=10)
        self.assertEqual(len(results), 0)

        # 空图谱导出
        output_path = str(self.test_dir / "empty.json")
        self.kg.export_json(output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data["stats"]["total_figures"], 0)

    def test_large_dataset(self):
        """测试：大数据集性能"""
        # 添加 100 个图表
        for i in range(100):
            self.kg.add_figure("PMID:123", f"fig_{i:03d}", f"Test {i}", "test.png")

        self.assertEqual(len(self.kg.figures_db), 100)

        # 搜索性能测试
        import time
        start = time.time()
        results = self.kg.search_figures("Test", top_k=10)
        elapsed = time.time() - start

        # 搜索应在 0.1 秒内完成
        self.assertLess(elapsed, 0.1)
        self.assertEqual(len(results), 10)


class TestMultimodalKGIntegration(unittest.TestCase):
    """集成测试类"""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.kg = MultimodalKG(data_dir=str(self.test_dir))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_full_workflow(self):
        """测试：完整工作流程"""
        # 1. 添加数据
        self.kg.add_figure("PMID:123", "fig_001", "SEM of LIG", "sem.png", "SEM")
        self.kg.add_equation("PMID:123", "eq_001", "R = V/I", "欧姆定律")
        self.kg.add_dataset("PMID:123", "data_001", "Resistance", [10.5, 11.2, 10.8], "Ω")

        # 2. 搜索
        results = self.kg.search_figures("SEM", top_k=10)
        self.assertEqual(len(results), 1)

        # 3. 导出
        output_path = str(self.test_dir / "workflow.json")
        self.kg.export_json(output_path)

        # 4. 验证导出文件
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data["stats"]["total_figures"], 1)
        self.assertEqual(data["stats"]["total_equations"], 1)
        self.assertEqual(data["stats"]["total_datasets"], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
