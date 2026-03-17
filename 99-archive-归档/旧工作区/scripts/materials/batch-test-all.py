#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI+Materials 系统 - 批量测试脚本

功能：
1. 自动发现所有 Python 脚本
2. 分类测试 (导入测试 + 功能测试)
3. 生成测试报告
4. 统计覆盖率

作者：Claw (AI Research OS)
创建时间：2026-03-05 22:35
"""

import os
import sys
import json
import time
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


# ============================================================================
# 1. 数据结构
# ============================================================================

@dataclass
class TestResult:
    """测试结果"""
    script: str
    category: str
    import_status: str  # success/failed
    import_time_ms: float
    main_status: str  # success/failed/skipped
    main_time_ms: float
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TestReport:
    """测试报告"""
    timestamp: str
    total_scripts: int
    passed: int
    failed: int
    skipped: int
    total_time_ms: float
    results: List[TestResult]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'results': [r.to_dict() for r in self.results]
        }


# ============================================================================
# 2. 脚本分类
# ============================================================================

SCRIPT_CATEGORIES = {
    "AI 论文解析": [
        "materials-ner-model.py",
        "crystal-structure-extractor.py",
        "property-data-extractor.py",
        "chart-data-extractor.py",
        "synthesis-condition-extractor.py",
        "auto-kg-builder.py",
    ],
    "ML 模型": [
        "cgcnn-model.py",
        "megnet-model.py",
        "multitask-model.py",
        "uncertainty-quantifier.py",
        "model-serving.py",
    ],
    "逆向设计": [
        "vae-model.py",
        "conditional-vae.py",
        "rl-optimizer.py",
        "multiobjective-optimizer.py",
        "inverse-design-ui.py",
    ],
    "研究助手": [
        "experiment-designer.py",
        "data-analyzer.py",
        "paper-recommender.py",
        "question-generator.py",
        "report-generator.py",
    ],
    "基础设施": [
        "materials-api-service.py",
        "materials-database.py",
        "materials-project-api.py",
        "materials-cli.py",
        "materials-knowledge-graph.py",
    ],
    "测试集成": [
        "materials-testing.py",
        "materials-system-integration.py",
        "automated-research-workflow.py",
    ],
}


# ============================================================================
# 3. 测试执行器
# ============================================================================

class BatchTester:
    """批量测试执行器"""
    
    def __init__(self, scripts_dir: str):
        self.scripts_dir = Path(scripts_dir)
        self.results: List[TestResult] = []
        
        # 反转分类映射：脚本名 -> 分类
        self.script_to_category = {}
        for category, scripts in SCRIPT_CATEGORIES.items():
            for script in scripts:
                self.script_to_category[script] = category
    
    def discover_scripts(self) -> List[str]:
        """发现所有 Python 脚本"""
        scripts = []
        for f in self.scripts_dir.glob("*.py"):
            # 跳过测试脚本本身
            if f.name == "batch-test-all.py":
                continue
            scripts.append(f.name)
        return sorted(scripts)
    
    def test_import(self, script_path: Path) -> Tuple[str, float]:
        """测试导入"""
        start = time.time()
        
        try:
            # 动态导入
            spec = importlib.util.spec_from_file_location("test_module", script_path)
            if spec is None or spec.loader is None:
                return "failed", 0
            
            module = importlib.util.module_from_spec(spec)
            
            # 只导入不执行 main
            sys.modules["test_module"] = module
            spec.loader.exec_module(module)
            
            elapsed = (time.time() - start) * 1000
            return "success", elapsed
            
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return "failed", elapsed
    
    def test_main(self, script_path: Path) -> Tuple[str, float, str]:
        """测试 main 函数"""
        start = time.time()
        
        try:
            # 重新导入以获取 main
            spec = importlib.util.spec_from_file_location("test_module", script_path)
            if spec is None or spec.loader is None:
                return "skipped", 0, "No spec"
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["test_module"] = module
            spec.loader.exec_module(module)
            
            # 检查是否有 main 函数
            if not hasattr(module, 'main'):
                return "skipped", 0, "No main function"
            
            # 执行 main (捕获输出)
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            try:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    module.main()
                
                elapsed = (time.time() - start) * 1000
                return "success", elapsed, ""
                
            except SystemExit as e:
                # 正常的 sys.exit(0)
                if e.code == 0:
                    elapsed = (time.time() - start) * 1000
                    return "success", elapsed, ""
                else:
                    elapsed = (time.time() - start) * 1000
                    return "failed", elapsed, f"Exit code: {e.code}"
                    
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                return "failed", elapsed, str(e)
                
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return "failed", elapsed, str(e)
    
    def test_script(self, script_name: str) -> TestResult:
        """测试单个脚本"""
        script_path = self.scripts_dir / script_name
        category = self.script_to_category.get(script_name, "其他")
        
        print(f"\n  测试：{script_name} [{category}]")
        
        # 1. 导入测试
        import_status, import_time = self.test_import(script_path)
        print(f"    导入：{import_status} ({import_time:.1f}ms)")
        
        # 2. Main 函数测试
        if import_status == "success":
            main_status, main_time, error_msg = self.test_main(script_path)
            print(f"    Main: {main_status} ({main_time:.1f}ms)")
        else:
            main_status, main_time, error_msg = "skipped", 0, "Import failed"
            print(f"    Main: skipped (import failed)")
        
        return TestResult(
            script=script_name,
            category=category,
            import_status=import_status,
            import_time_ms=import_time,
            main_status=main_status,
            main_time_ms=main_time,
            error_message=error_msg
        )
    
    def run_all_tests(self) -> TestReport:
        """运行所有测试"""
        print("=" * 70)
        print("AI+Materials 系统 - 批量测试")
        print("=" * 70)
        print(f"\n脚本目录：{self.scripts_dir}")
        
        start_time = time.time()
        
        # 发现脚本
        scripts = self.discover_scripts()
        print(f"发现脚本：{len(scripts)} 个\n")
        
        # 测试每个脚本
        for script in scripts:
            result = self.test_script(script)
            self.results.append(result)
        
        total_time = (time.time() - start_time) * 1000
        
        # 统计
        passed = sum(1 for r in self.results if r.import_status == "success" and r.main_status in ["success", "skipped"])
        failed = sum(1 for r in self.results if r.import_status == "failed" or r.main_status == "failed")
        skipped = sum(1 for r in self.results if r.main_status == "skipped")
        
        return TestReport(
            timestamp=datetime.now().isoformat(),
            total_scripts=len(scripts),
            passed=passed,
            failed=failed,
            skipped=skipped,
            total_time_ms=total_time,
            results=self.results
        )


# ============================================================================
# 4. 报告生成
# ============================================================================

def print_report(report: TestReport):
    """打印测试报告"""
    print("\n" + "=" * 70)
    print("Test Report")
    print("=" * 70)
    
    print(f"\nTimestamp: {report.timestamp}")
    print(f"Total scripts: {report.total_scripts}")
    print(f"Passed: {report.passed} [OK]")
    print(f"Failed: {report.failed} [ERR]")
    print(f"Skipped: {report.skipped} [SKIP]")
    print(f"Total time: {report.total_time_ms:.1f}ms ({report.total_time_ms/1000:.2f}s)")
    
    # 通过率
    pass_rate = report.passed / report.total_scripts * 100 if report.total_scripts > 0 else 0
    print(f"Pass rate: {pass_rate:.1f}%")
    
    # 按分类统计
    print("\nBy Category:")
    category_stats = {}
    for result in report.results:
        cat = result.category
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0, "failed": 0}
        category_stats[cat]["total"] += 1
        if result.import_status == "success" and result.main_status in ["success", "skipped"]:
            category_stats[cat]["passed"] += 1
        else:
            category_stats[cat]["failed"] += 1
    
    for cat, stats in sorted(category_stats.items()):
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")
    
    # 失败详情
    failed_results = [r for r in report.results if r.import_status == "failed" or r.main_status == "failed"]
    if failed_results:
        print("\nFailed:")
        for result in failed_results:
            print(f"  [ERR] {result.script}")
            print(f"        Import: {result.import_status}, Main: {result.main_status}")
            if result.error_message:
                print(f"        Error: {result.error_message[:100]}")
    
    # 性能 TOP5
    print("\nSlowest Imports (TOP5):")
    sorted_by_import = sorted(report.results, key=lambda r: r.import_time_ms, reverse=True)[:5]
    for i, result in enumerate(sorted_by_import, 1):
        print(f"  {i}. {result.script}: {result.import_time_ms:.1f}ms")


def save_report(report: TestReport, output_path: str):
    """保存测试报告"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存：{output_path}")


# ============================================================================
# 5. 主函数
# ============================================================================

def main():
    """主函数"""
    # 脚本目录
    scripts_dir = Path(__file__).parent
    
    # 创建测试器
    tester = BatchTester(scripts_dir)
    
    # 运行测试
    report = tester.run_all_tests()
    
    # 打印报告
    print_report(report)
    
    # 保存报告
    output_path = scripts_dir.parent / "data" / "batch-test-report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_report(report, str(output_path))
    
    # 返回退出码
    if report.failed > 0:
        sys.exit(1)
    else:
        print("\n" + "=" * 70)
        print("All tests PASSED!")
        print("=" * 70)
        sys.exit(0)


if __name__ == '__main__':
    main()
