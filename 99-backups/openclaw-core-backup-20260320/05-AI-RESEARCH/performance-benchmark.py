#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Benchmark v1
性能基准测试
"""

import time
import statistics
from typing import Dict, List
import requests

class PerformanceBenchmark:
    """性能基准测试"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: Dict[str, List[float]] = {}

    def test_endpoint(self, endpoint: str, method: str = "GET", iterations: int = 10) -> Dict:
        """测试端点性能"""
        url = f"{self.base_url}{endpoint}"
        latencies = []

        for i in range(iterations):
            try:
                start = time.time()
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.post(url, json={}, timeout=5)
                end = time.time()

                if response.status_code == 200:
                    latencies.append((end - start) * 1000)  # 转换为毫秒
            except Exception as e:
                print(f"  Iteration {i +1} failed: {e}")

        if not latencies:
            return {"status": "error", "message": "No successful requests"}

        self.results[endpoint] = latencies

        return {
            "status": "success",
            "endpoint": endpoint,
            "iterations": len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "avg_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
        }

    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/materials", "GET"),
            ("/materials/stats", "GET"),
            ("/kg/stats", "GET"),
        ]

        results = {}
        for endpoint, method in endpoints:
            print(f"\n🧪 Testing {endpoint}...")
            result = self.test_endpoint(endpoint, method)
            results[endpoint] = result

            if result["status"] == "success":
                print(f"  ✅ Avg: {result['avg_ms']:.2f}ms, Median: {result['median_ms']:.2f}ms")
            else:
                print(f"  ❌ {result.get('message', 'Unknown error')}")

        return results

    def get_summary(self) -> Dict:
        """获取测试摘要"""
        if not self.results:
            return {"status": "error", "message": "No test results"}

        all_latencies = []
        for latencies in self.results.values():
            all_latencies.extend(latencies)

        if not all_latencies:
            return {"status": "error", "message": "No successful requests"}

        return {
            "total_endpoints": len(self.results),
            "total_requests": len(all_latencies),
            "min_ms": min(all_latencies),
            "max_ms": max(all_latencies),
            "avg_ms": statistics.mean(all_latencies),
            "median_ms": statistics.median(all_latencies)
        }

def demo():
    """演示使用"""
    print("=" * 60)
    print("Performance Benchmark v1 Demo")
    print("=" * 60)

    benchmark = PerformanceBenchmark()

    # 运行所有测试
    print("\n🚀 Running all tests...")
    results = benchmark.run_all_tests()

    # 获取摘要
    print("\n📊 Test Summary:")
    summary = benchmark.get_summary()

    if summary["status"] == "success":
        print(f"  Total Endpoints: {summary['total_endpoints']}")
        print(f"  Total Requests: {summary['total_requests']}")
        print(f"  Min Latency: {summary['min_ms']:.2f}ms")
        print(f"  Max Latency: {summary['max_ms']:.2f}ms")
        print(f"  Avg Latency: {summary['avg_ms']:.2f}ms")
        print(f"  Median Latency: {summary['median_ms']:.2f}ms")
    else:
        print(f"  {summary.get('message', 'Unknown error')}")

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
