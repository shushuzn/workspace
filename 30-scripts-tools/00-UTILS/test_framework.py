"""
Generic Test Framework
通用测试框架

Date: 2026-03-07
Author: Claw (@OpenClaw)
Version: v0.1.0
"""

import time
import json
import statistics
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """测试状态"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """测试结果"""
    name: str
    status: TestStatus
    duration: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceMetrics:
    """性能指标"""
    name: str
    iterations: int
    mean: float
    median: float
    std_dev: float
    min: float
    max: float
    p95: float
    p99: float


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.results: List[TestResult] = []

    def run_test(self, name: str, test_fn: Callable, **kwargs) -> TestResult:
        """运行单个测试"""
        start_time = time.perf_counter()

        try:
            test_fn(**kwargs)
            status = TestStatus.PASSED
            error = None
        except Exception as e:
            status = TestStatus.FAILED
            error = str(e)

        end_time = time.perf_counter()
        duration = end_time - start_time

        result = TestResult(
            name=name,
            status=status,
            duration=duration,
            error=error,
            metadata=kwargs
        )

        self.results.append(result)
        return result

    def run_tests(self, tests: List[Dict]) -> List[TestResult]:
        """运行多个测试"""
        results = []

        for test in tests:
            result = self.run_test(
                name=test["name"],
                test_fn=test["fn"],
                **test.get("kwargs", {})
            )
            results.append(result)

        return results

    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": passed / total * 100 if total > 0 else 0
        }

    def print_results(self):
        """打印测试结果"""
        print("\n" + "=" * 60)
        print("Test Results")
        print("=" * 60)

        for result in self.results:
            icon = "[PASS]" if result.status == TestStatus.PASSED else "[FAIL]"
            print(f"{icon} {result.name}: {result.duration*1000:.2f}ms")

            if result.error:
                print(f"   Error: {result.error}")

        summary = self.get_summary()
        print("\n" + "-" * 60)
        print(f"Total: {summary['total']} | Passed: {summary['passed']} | Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print("=" * 60)


class PerformanceTester:
    """性能测试器"""

    @staticmethod
    def benchmark(
        name: str,
        fn: Callable,
        iterations: int = 100,
        **kwargs
    ) -> PerformanceMetrics:
        """性能基准测试"""
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            fn(**kwargs)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        # Calculate metrics
        sorted_times = sorted(times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        metrics = PerformanceMetrics(
            name=name,
            iterations=iterations,
            mean=statistics.mean(times),
            median=statistics.median(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            min=min(times),
            max=max(times),
            p95=sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0,
            p99=sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
        )

        return metrics

    @staticmethod
    def print_metrics(metrics: PerformanceMetrics):
        """打印性能指标"""
        print("\n" + "=" * 60)
        print(f"Performance: {metrics.name}")
        print("=" * 60)
        print(f"Iterations: {metrics.iterations}")
        print(f"Mean: {metrics.mean:.2f}ms")
        print(f"Median: {metrics.median:.2f}ms")
        print(f"Std Dev: {metrics.std_dev:.2f}ms")
        print(f"Min: {metrics.min:.2f}ms")
        print(f"Max: {metrics.max:.2f}ms")
        print(f"P95: {metrics.p95:.2f}ms")
        print(f"P99: {metrics.p99:.2f}ms")
        print("=" * 60)
        print("[OK] Performance test complete")


class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def generate_html_report(
        results: List[TestResult],
        output_file: str = "test_report.html"
    ):
        """生成 HTML 报告"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <table>
        <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Duration (ms)</th>
            <th>Error</th>
        </tr>
"""

        for result in results:
            status_class = "passed" if result.status == TestStatus.PASSED else "failed"
            error_text = file.error if result.error else ""
            html += f"""
        <tr>
            <td>{result.name}</td>
            <td class="{status_class}">{result.status.value}</td>
            <td>{result.duration*1000:.2f}</td>
            <td>{error_text}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[OK] HTML report generated: {output_file}")


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Generic Test Framework - Demo")
    print("=" * 60)

    # 示例 1: 运行测试
    print("\n[Example 1] Running Tests")
    runner = TestRunner()

    def test_addition():
        assert 1 + 1 == 2

    def test_subtraction():
        assert 5 - 3 == 2

    def test_failure():
        assert 1 == 2  # This will fail

    runner.run_test("test_addition", test_addition)
    runner.run_test("test_subtraction", test_subtraction)
    runner.run_test("test_failure", test_failure)

    runner.print_results()

    # 示例 2: 性能测试
    print("\n[Example 2] Performance Test")

    def slow_function():
        time.sleep(0.01)  # Simulate work
        return sum(range(100))

    metrics = PerformanceTester.benchmark(
        "slow_function",
        slow_function,
        iterations=50
    )

    PerformanceTester.print_metrics(metrics)

    # 示例 3: 生成报告
    print("\n[Example 3] Generate Report")
    ReportGenerator.generate_html_report(runner.results, "demo_report.html")

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
