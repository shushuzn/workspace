#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Benchmark
性能基准测试
"""

import time
import requests
import statistics
from pathlib import Path
import json

class PerformanceBenchmark:
    """性能基准测试"""

    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.results = {}

    def benchmark_health(self, iterations=10):
        """健康检查基准测试"""
        times = []

        for i in range(iterations):
            start = time.time()
            response = requests.get(f'{self.base_url}/api/v1/health')
            end = time.time()

            if response.status_code == 200:
                times.append((end - start) * 1000)  # 转换为毫秒

        if times:
            self.results['health'] = {
                'iterations': iterations,
                'min': min(times),
                'max': max(times),
                'avg': statistics.mean(times),
                'p95': self._percentile(times, 95),
                'p99': self._percentile(times, 99)
            }

        return self.results['health']

    def benchmark_papers(self, iterations=10):
        """论文端点基准测试"""
        times = []

        for i in range(iterations):
            start = time.time()
            response = requests.get(f'{self.base_url}/api/v1/papers')
            end = time.time()

            if response.status_code in [200, 404]:
                times.append((end - start) * 1000)

        if times:
            self.results['papers'] = {
                'iterations': iterations,
                'min': min(times),
                'max': max(times),
                'avg': statistics.mean(times),
                'p95': self._percentile(times, 95),
                'p99': self._percentile(times, 99)
            }

        return self.results['papers']

    def benchmark_metrics(self, iterations=10):
        """指标端点基准测试"""
        times = []

        for i in range(iterations):
            start = time.time()
            response = requests.get(f'{self.base_url}/api/v1/metrics')
            end = time.time()

            if response.status_code == 200:
                times.append((end - start) * 1000)

        if times:
            self.results['metrics'] = {
                'iterations': iterations,
                'min': min(times),
                'max': max(times),
                'avg': statistics.mean(times),
                'p95': self._percentile(times, 95),
                'p99': self._percentile(times, 99)
            }

        return self.results['metrics']

    def _percentile(self, data, percentile):
        """计算百分位数"""
        if not data:
            return 0

        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def run_all(self):
        """运行所有基准测试"""
        print("运行性能基准测试...")
        print("=" * 60)

        print("\n[1/3] 健康检查基准测试...")
        health_result = self.benchmark_health()
        print(f"  平均响应时间：{health_result['avg']:.2f}ms")
        print(f"  P95: {health_result['p95']:.2f}ms")
        print(f"  P99: {health_result['p99']:.2f}ms")

        print("\n[2/3] 论文端点基准测试...")
        papers_result = self.benchmark_papers()
        print(f"  平均响应时间：{papers_result['avg']:.2f}ms")
        print(f"  P95: {papers_result['p95']:.2f}ms")
        print(f"  P99: {papers_result['p99']:.2f}ms")

        print("\n[3/3] 指标端点基准测试...")
        metrics_result = self.benchmark_metrics()
        print(f"  平均响应时间：{metrics_result['avg']:.2f}ms")
        print(f"  P95: {metrics_result['p95']:.2f}ms")
        print(f"  P99: {metrics_result['p99']:.2f}ms")

        print("\n" + "=" * 60)
        print("基准测试完成!")

        return self.results

    def save_report(self, output_file='benchmarks/report.json'):
        """保存基准测试报告"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'timestamp': time.time(),
            'base_url': self.base_url,
            'results': self.results
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"报告已保存到：{output_file}")

if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.run_all()
    benchmark.save_report()
