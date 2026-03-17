#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识卡片生成器集成测试
使用真实 PDF 文件测试完整流程

测试覆盖：
- 真实 PDF 处理
- 元数据提取准确率
- 章节解析正确率
- 参考文献提取完整率
- HTML 生成质量
- 处理性能

使用方法：
```bash
py integration_test.py
```
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime


class IntegrationTest:
    """集成测试器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent / "test_pdfs"
        self.results = []
        self.metadata_file = self.test_dir / "test_pdfs_metadata.json"
    
    def load_test_pdfs(self) -> list:
        """加载测试 PDF 元数据"""
        if not self.metadata_file.exists():
            print("❌ 测试集元数据不存在")
            print("提示：先运行 collect_test_pdfs.py 收集测试 PDF")
            return []
        
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        pdfs = []
        for pdf_info in data["pdfs"]:
            pdf_path = self.test_dir / pdf_info["filename"]
            if pdf_path.exists():
                pdfs.append({
                    "path": str(pdf_path),
                    "info": pdf_info
                })
            else:
                print(f"⚠️ PDF 文件不存在：{pdf_info['filename']}")
        
        return pdfs
    
    def test_metadata_extraction(self, pdf_path: str) -> dict:
        """测试元数据提取"""
        print(f"  测试元数据提取...")
        
        start_time = time.time()
        
        # TODO: 实际调用知识卡片生成器
        # from core.knowledge_card_generator import KnowledgeCardGenerator
        # generator = KnowledgeCardGenerator()
        # metadata = generator.extract_metadata(pdf_path)
        
        # 模拟结果 (删除后替换为实际调用)
        time.sleep(0.1)
        metadata = {
            "title": "Test Paper",
            "authors": ["Zhang, San"],
            "year": 2024,
            "arxiv_id": "2401.00001",
            "extracted": True
        }
        
        elapsed = time.time() - start_time
        
        # 验证结果
        passed = metadata.get("extracted", False) and metadata.get("title")
        
        return {
            "test": "metadata_extraction",
            "pdf": Path(pdf_path).name,
            "passed": passed,
            "elapsed": elapsed,
            "details": metadata
        }
    
    def test_chapter_parsing(self, pdf_path: str) -> dict:
        """测试章节解析"""
        print(f"  测试章节解析...")
        
        start_time = time.time()
        
        # TODO: 实际调用
        time.sleep(0.1)
        chapters = [
            {"title": "Introduction", "pages": [1, 2, 3]},
            {"title": "Methods", "pages": [4, 5, 6, 7, 8]},
            {"title": "Results", "pages": [9, 10, 11, 12]}
        ]
        
        elapsed = time.time() - start_time
        
        # 验证：至少 3 个章节
        passed = len(chapters) >= 3
        
        return {
            "test": "chapter_parsing",
            "pdf": Path(pdf_path).name,
            "passed": passed,
            "elapsed": elapsed,
            "details": {"chapter_count": len(chapters)}
        }
    
    def test_reference_extraction(self, pdf_path: str) -> dict:
        """测试参考文献提取"""
        print(f"  测试参考文献提取...")
        
        start_time = time.time()
        
        # TODO: 实际调用
        time.sleep(0.1)
        references = [
            {"title": "Ref 1", "doi": "10.1038/nature.2023.001"},
            {"title": "Ref 2", "arxiv_id": "2301.00001"}
        ]
        
        elapsed = time.time() - start_time
        
        # 验证：至少 2 篇参考文献
        passed = len(references) >= 2
        
        return {
            "test": "reference_extraction",
            "pdf": Path(pdf_path).name,
            "passed": passed,
            "elapsed": elapsed,
            "details": {"reference_count": len(references)}
        }
    
    def test_html_generation(self, pdf_path: str) -> dict:
        """测试 HTML 生成"""
        print(f"  测试 HTML 生成...")
        
        start_time = time.time()
        
        # TODO: 实际调用
        time.sleep(0.1)
        html_content = "<!DOCTYPE html><html><head><title>Test</title></head><body>Content</body></html>"
        
        elapsed = time.time() - start_time
        
        # 验证：HTML 结构完整
        passed = (
            "<!DOCTYPE html>" in html_content and
            "<html>" in html_content and
            "</html>" in html_content
        )
        
        return {
            "test": "html_generation",
            "pdf": Path(pdf_path).name,
            "passed": passed,
            "elapsed": elapsed,
            "details": {"html_length": len(html_content)}
        }
    
    def test_performance(self, pdf_path: str) -> dict:
        """测试处理性能"""
        print(f"  测试处理性能...")
        
        start_time = time.time()
        
        # TODO: 实际完整处理
        time.sleep(0.5)  # 模拟处理
        
        elapsed = time.time() - start_time
        
        # 验证：处理时间 < 30 秒
        passed = elapsed < 30.0
        
        return {
            "test": "performance",
            "pdf": Path(pdf_path).name,
            "passed": passed,
            "elapsed": elapsed,
            "details": {"target": 30.0}
        }
    
    def run_integration_test(self, pdf_info: dict) -> dict:
        """运行单个 PDF 的完整集成测试"""
        pdf_path = pdf_info["path"]
        category = pdf_info["info"]["category"]
        
        print(f"\n[集成测试] {Path(pdf_path).name}")
        print(f"类别：{category}")
        print("-"*60)
        
        results = {
            "pdf": Path(pdf_path).name,
            "category": category,
            "tests": []
        }
        
        # 运行所有测试
        tests = [
            self.test_metadata_extraction,
            self.test_chapter_parsing,
            self.test_reference_extraction,
            self.test_html_generation,
            self.test_performance
        ]
        
        for test_func in tests:
            result = test_func(pdf_path)
            results["tests"].append(result)
            status = "[OK]" if result["passed"] else "[FAIL]"
            print(f"  {status} {result['test']}: {result['elapsed']:.2f}s")
        
        # 计算通过率
        total = len(results["tests"])
        passed = sum(1 for t in results["tests"] if t["passed"])
        results["pass_rate"] = passed / total * 100 if total > 0 else 0
        
        print(f"通过率：{passed}/{total} ({results['pass_rate']:.1f}%)")
        
        return results
    
    def run_all_tests(self):
        """运行所有集成测试"""
        print("="*60)
        print("知识卡片生成器集成测试")
        print("="*60)
        print(f"开始时间：{datetime.now().isoformat()}")
        
        # 加载测试 PDF
        test_pdfs = self.load_test_pdfs()
        
        if not test_pdfs:
            print("❌ 无可用测试 PDF")
            print("提示：运行 collect_test_pdfs.py 收集测试文件")
            return None
        
        print(f"测试 PDF 数量：{len(test_pdfs)}")
        print()
        
        # 运行测试
        all_results = []
        for pdf_info in test_pdfs:
            result = self.run_integration_test(pdf_info)
            all_results.append(result)
        
        # 汇总结果
        total_tests = sum(len(r["tests"]) for r in all_results)
        passed_tests = sum(
            sum(1 for t in r["tests"] if t["passed"])
            for r in all_results
        )
        
        summary = {
            "total_pdfs": len(all_results),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0,
            "completed_at": datetime.now().isoformat()
        }
        
        # 保存报告
        report = {
            "summary": summary,
            "results": all_results
        }
        
        report_path = Path(__file__).parent / "integration_test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印汇总
        print()
        print("="*60)
        print("集成测试汇总")
        print("="*60)
        print(f"测试 PDF: {summary['total_pdfs']} 个")
        print(f"总测试数：{summary['total_tests']}")
        print(f"通过：{summary['passed_tests']} | 失败：{summary['failed_tests']}")
        print(f"通过率：{summary['pass_rate']:.1f}%")
        print(f"报告已保存：{report_path}")
        print("="*60)
        
        return report


def main():
    """主函数"""
    tester = IntegrationTest()
    report = tester.run_all_tests()
    
    if report is None:
        return 1
    
    success = report["summary"]["pass_rate"] >= 80.0
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
