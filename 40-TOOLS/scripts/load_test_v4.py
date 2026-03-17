#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load Test Script for Dashboard API v4
使用 asyncio 进行高并发压力测试

Author: Claw 🐾
"""

import asyncio
import aiohttp
import time
import statistics
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
import json

# UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

@dataclass
class TestResult:
    request_id: int
    endpoint: str
    status_code: int
    latency_ms: float
    success: bool
    error: str = ""

class LoadTester:
    """高并发压力测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8447"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'latencies': [],
            'start_time': 0,
            'end_time': 0
        }
    
    async def make_request(self, session: aiohttp.ClientSession, 
                          request_id: int, endpoint: str, 
                          method: str = "GET", data: Dict = None) -> TestResult:
        """发送单个请求"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    status = response.status
                    await response.text()
            elif method == "POST":
                async with session.post(url, json=data, 
                                       timeout=aiohttp.ClientTimeout(total=30)) as response:
                    status = response.status
                    await response.text()
            
            latency_ms = (time.time() - start_time) * 1000
            success = 200 <= status < 300
            
            return TestResult(
                request_id=request_id,
                endpoint=endpoint,
                status_code=status,
                latency_ms=latency_ms,
                success=success
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return TestResult(
                request_id=request_id,
                endpoint=endpoint,
                status_code=0,
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )
    
    async def run_load_test(self, num_requests: int = 100, 
                           concurrent_users: int = 10,
                           endpoints: List[str] = None):
        """运行压力测试"""
        if endpoints is None:
            endpoints = [
                "/api/health",
                "/api/sessions",
                "/api/git",
                "/api/memory",
                "/api/dashboard"
            ]
        
        self.stats['start_time'] = time.time()
        
        connector = aiohttp.TCPConnector(limit=concurrent_users)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i in range(num_requests):
                endpoint = endpoints[i % len(endpoints)]
                task = self.make_request(session, i, endpoint)
                tasks.append(task)
            
            # 并发执行所有请求
            self.results = await asyncio.gather(*tasks)
        
        self.stats['end_time'] = time.time()
        self._calculate_stats()
    
    async def run_task_creation_test(self, num_tasks: int = 50, 
                                     concurrent: int = 10):
        """测试任务创建和 WebSocket"""
        self.stats['start_time'] = time.time()
        
        connector = aiohttp.TCPConnector(limit=concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            # 创建任务
            create_tasks = []
            for i in range(num_tasks):
                data = {
                    'task_type': 'workflow',
                    'payload': {'steps': 5},
                    'priority': 5
                }
                task = self.make_request(session, i, "/api/tasks", 
                                        method="POST", data=data)
                create_tasks.append(task)
            
            create_results = await asyncio.gather(*create_tasks)
            self.results.extend(create_results)
            
            # 获取任务列表
            for i in range(10):
                task = self.make_request(session, num_tasks + i, "/api/tasks")
                self.results.append(task)
        
        self.stats['end_time'] = time.time()
        self._calculate_stats()
    
    def _calculate_stats(self):
        """计算统计数据"""
        self.stats['total_requests'] = len(self.results)
        self.stats['successful'] = sum(1 for r in self.results if r.success)
        self.stats['failed'] = self.stats['total_requests'] - self.stats['successful']
        
        latencies = [r.latency_ms for r in self.results if r.success]
        self.stats['latencies'] = latencies
        
        if latencies:
            self.stats['avg_latency'] = statistics.mean(latencies)
            self.stats['min_latency'] = min(latencies)
            self.stats['max_latency'] = max(latencies)
            self.stats['p50_latency'] = statistics.median(latencies)
            self.stats['p95_latency'] = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else self.stats['max_latency']
            self.stats['p99_latency'] = sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else self.stats['max_latency']
        
        duration = self.stats['end_time'] - self.stats['start_time']
        self.stats['duration_seconds'] = duration
        self.stats['requests_per_second'] = self.stats['total_requests'] / duration if duration > 0 else 0
    
    def print_report(self):
        """打印测试报告"""
        print("\n" + "=" * 80)
        print("📊 压力测试报告")
        print("=" * 80)
        
        print(f"\n⏱️  测试时长：{self.stats['duration_seconds']:.2f} 秒")
        print(f"📈 总请求数：{self.stats['total_requests']}")
        print(f"✅ 成功：{self.stats['successful']} ({self.stats['successful']/self.stats['total_requests']*100:.1f}%)")
        print(f"❌ 失败：{self.stats['failed']} ({self.stats['failed']/self.stats['total_requests']*100:.1f}%)")
        print(f"🚀 吞吐量：{self.stats['requests_per_second']:.2f} req/s")
        
        if self.stats['latencies']:
            print(f"\n⚡ 延迟统计:")
            print(f"   平均：{self.stats['avg_latency']:.2f} ms")
            print(f"   最小：{self.stats['min_latency']:.2f} ms")
            print(f"   最大：{self.stats['max_latency']:.2f} ms")
            print(f"   P50:  {self.stats['p50_latency']:.2f} ms")
            print(f"   P95:  {self.stats['p95_latency']:.2f} ms")
            print(f"   P99:  {self.stats['p99_latency']:.2f} ms")
        
        # 错误统计
        errors = [r for r in self.results if not r.success]
        if errors:
            print(f"\n⚠️  错误详情:")
            error_types = {}
            for e in errors:
                error_type = e.error.split(':')[0] if e.error else f"HTTP {e.status_code}"
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"   {error_type}: {count} 次")
        
        print("\n" + "=" * 80)
    
    def save_report(self, filepath: Path = None):
        """保存测试报告"""
        if filepath is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filepath = Path(__file__).parent / f'load_test_report_{timestamp}.json'
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'statistics': {
                'duration_seconds': self.stats['duration_seconds'],
                'total_requests': self.stats['total_requests'],
                'successful': self.stats['successful'],
                'failed': self.stats['failed'],
                'success_rate': self.stats['successful'] / self.stats['total_requests'] * 100 if self.stats['total_requests'] > 0 else 0,
                'requests_per_second': self.stats['requests_per_second'],
                'latency': {
                    'avg_ms': self.stats.get('avg_latency', 0),
                    'min_ms': self.stats.get('min_latency', 0),
                    'max_ms': self.stats.get('max_latency', 0),
                    'p50_ms': self.stats.get('p50_latency', 0),
                    'p95_ms': self.stats.get('p95_latency', 0),
                    'p99_ms': self.stats.get('p99_latency', 0),
                }
            },
            'errors': [
                {'request_id': r.request_id, 'endpoint': r.endpoint, 'error': r.error}
                for r in self.results if not r.success
            ][:20]  # 只保存前 20 个错误
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📁 报告已保存：{filepath}")
        return filepath


async def main():
    """主测试函数"""
    import argparse
    parser = argparse.ArgumentParser(description="Dashboard API v4 Load Tester")
    parser.add_argument('--requests', type=int, default=500, help='总请求数')
    parser.add_argument('--concurrent', type=int, default=50, help='并发用户数')
    parser.add_argument('--url', default='http://localhost:8447', help='API URL')
    parser.add_argument('--task-test', action='store_true', help='运行任务创建测试')
    parser.add_argument('--save', action='store_true', help='保存报告')
    args = parser.parse_args()
    
    print("\n🚀 Dashboard API v4 压力测试")
    print("=" * 60)
    print(f"目标 URL: {args.url}")
    print(f"总请求数：{args.requests}")
    print(f"并发用户：{args.concurrent}")
    print("\n⏳ 开始测试...\n")
    
    tester = LoadTester(args.url)
    
    if args.task_test:
        await tester.run_task_creation_test(
            num_tasks=args.requests // 2,
            concurrent=args.concurrent
        )
    else:
        await tester.run_load_test(
            num_requests=args.requests,
            concurrent_users=args.concurrent
        )
    
    tester.print_report()
    
    if args.save:
        tester.save_report()
    
    # 验证是否通过
    success_rate = tester.stats['successful'] / tester.stats['total_requests'] * 100
    p95_latency = tester.stats.get('p95_latency', 9999)
    rps = tester.stats['requests_per_second']
    
    print("\n🎯 验收标准检查:")
    print(f"  [{'✅' if success_rate >= 99 else '❌'}] 成功率 >= 99%: {success_rate:.1f}%")
    print(f"  [{'✅' if p95_latency <= 100 else '❌'}] P95 延迟 <= 100ms: {p95_latency:.2f}ms")
    print(f"  [{'✅' if rps >= 500 else '❌'}] 吞吐量 >= 500 req/s: {rps:.2f} req/s")
    
    if success_rate >= 99 and p95_latency <= 100 and rps >= 500:
        print("\n✅ 所有验收标准通过!")
        return 0
    else:
        print("\n⚠️  部分验收标准未通过，需要优化")
        return 1


if __name__ == "__main__":
    # 安装依赖检查
    try:
        import aiohttp
    except ImportError:
        print("❌ 缺少依赖：aiohttp")
        print("请运行：pip install aiohttp")
        sys.exit(1)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
