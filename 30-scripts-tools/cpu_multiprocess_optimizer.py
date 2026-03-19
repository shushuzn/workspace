#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CPU Multiprocess Optimizer - CPU 密集型任务多进程优化器

将计算密集型任务分配到多进程执行，利用多核 CPU，计算速度提升 2-4x
"""

import multiprocessing as mp
from multiprocessing import Pool, cpu_count
import time
from pathlib import Path
from datetime import datetime
from typing import Callable, List, Any
import math

class CPUMultiprocessOptimizer:
    """CPU 密集型任务多进程优化器"""
    
    def __init__(self, processes=None):
        """
        初始化多进程优化器
        
        Args:
            processes: 进程数 (默认 CPU 核心数)
        """
        if processes is None:
            processes = cpu_count()
        
        self.processes = processes
        self.stats = {
            'tasks_processed': 0,
            'total_time_ms': 0,
            'speedup': 0,
            'cpu_cores_used': 0
        }
    
    def compute_sequential(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        顺序计算
        
        Args:
            func: 计算函数
            items: 输入数据列表
        
        Returns:
            计算结果列表
        """
        start = time.perf_counter()
        
        results = []
        for item in items:
            result = func(item)
            results.append(result)
        
        elapsed = (time.perf_counter() - start) * 1000
        
        self.stats['tasks_processed'] += len(items)
        self.stats['total_time_ms'] += elapsed
        
        return results
    
    def compute_parallel(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        并行计算 (多进程)
        
        Args:
            func: 计算函数
            items: 输入数据列表
        
        Returns:
            计算结果列表
        """
        start = time.perf_counter()
        
        with Pool(processes=self.processes) as pool:
            results = pool.map(func, items)
        
        elapsed = (time.perf_counter() - start) * 1000
        
        # 计算加速比
        sequential_time = self.stats.get('last_sequential_time', elapsed)
        speedup = sequential_time / elapsed if elapsed > 0 else 1
        
        self.stats['tasks_processed'] += len(items)
        self.stats['total_time_ms'] += elapsed
        self.stats['speedup'] = speedup
        self.stats['cpu_cores_used'] = self.processes
        self.stats['last_parallel_time'] = elapsed
        
        return results
    
    def compute_parallel_async(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        异步并行计算
        
        Args:
            func: 计算函数
            items: 输入数据列表
        
        Returns:
            计算结果列表
        """
        start = time.perf_counter()
        
        with Pool(processes=self.processes) as pool:
            results_async = [pool.apply_async(func, (item,)) for item in items]
            results = [r.get() for r in results_async]
        
        elapsed = (time.perf_counter() - start) * 1000
        
        self.stats['tasks_processed'] += len(items)
        self.stats['total_time_ms'] += elapsed
        
        return results
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            'available_cpus': cpu_count(),
            'processes_used': self.processes
        }


# CPU 密集型计算示例函数
def heavy_computation(n):
    """重型计算示例"""
    result = 0
    for i in range(n):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result


def prime_check(n):
    """质数检查"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def fibonacci(n):
    """斐波那契数列"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


async def benchmark_multiprocess():
    """基准测试多进程性能"""
    print("\n" + "=" * 70)
    print("CPU Multiprocess Benchmark - CPU 多进程基准测试")
    print("=" * 70)
    
    optimizer = CPUMultiprocessOptimizer(processes=4)
    
    # 测试 1: 重型计算
    print("\n[1/3] 重型计算测试...")
    items = [10000] * 20  # 20 个重型计算任务
    
    # 顺序计算
    start = time.perf_counter()
    sequential_results = optimizer.compute_sequential(heavy_computation, items)
    sequential_time = (time.perf_counter() - start) * 1000
    optimizer.stats['last_sequential_time'] = sequential_time
    
    print(f"✅ 顺序计算 20 项：{sequential_time:.2f}ms")
    
    # 并行计算
    start = time.perf_counter()
    parallel_results = optimizer.compute_parallel(heavy_computation, items)
    parallel_time = (time.perf_counter() - start) * 1000
    
    print(f"✅ 并行计算 20 项：{parallel_time:.2f}ms")
    
    # 计算加速比
    speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
    improvement = ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0
    
    print(f"\n📊 重型计算性能:")
    print(f"  顺序时间：{sequential_time:.2f}ms")
    print(f"  并行时间：{parallel_time:.2f}ms")
    print(f"  加速比：{speedup:.2f}x")
    print(f"  提升：{improvement:.1f}%")
    
    # 测试 2: 质数检查
    print("\n[2/3] 质数检查测试...")
    items = list(range(100000, 100100))  # 100 个数字
    
    # 顺序
    start = time.perf_counter()
    sequential_primes = optimizer.compute_sequential(prime_check, items)
    sequential_time = (time.perf_counter() - start) * 1000
    optimizer.stats['last_sequential_time'] = sequential_time
    
    # 并行
    start = time.perf_counter()
    parallel_primes = optimizer.compute_parallel(prime_check, items)
    parallel_time = (time.perf_counter() - start) * 1000
    
    speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
    
    print(f"✅ 顺序检查 100 项：{sequential_time:.2f}ms")
    print(f"✅ 并行检查 100 项：{parallel_time:.2f}ms")
    print(f"✅ 加速比：{speedup:.2f}x")
    
    # 测试 3: 斐波那契
    print("\n[3/3] 斐波那契计算测试...")
    items = [1000] * 50  # 50 个斐波那契计算
    
    # 顺序
    start = time.perf_counter()
    sequential_fib = optimizer.compute_sequential(fibonacci, items)
    sequential_time = (time.perf_counter() - start) * 1000
    optimizer.stats['last_sequential_time'] = sequential_time
    
    # 并行
    start = time.perf_counter()
    parallel_fib = optimizer.compute_parallel(fibonacci, items)
    parallel_time = (time.perf_counter() - start) * 1000
    
    speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
    
    print(f"✅ 顺序计算 50 项：{sequential_time:.2f}ms")
    print(f"✅ 并行计算 50 项：{parallel_time:.2f}ms")
    print(f"✅ 加速比：{speedup:.2f}x")
    
    # 显示统计
    stats = optimizer.get_stats()
    print(f"\n📊 多进程统计:")
    print(f"  可用 CPU 核心：{stats['available_cpus']}")
    print(f"  使用进程数：{stats['processes_used']}")
    print(f"  处理任务数：{stats['tasks_processed']}")
    print(f"  总时间：{stats['total_time_ms']:.2f}ms")
    print(f"  平均加速比：{stats['speedup']:.2f}x")
    
    print("\n" + "=" * 70)
    print("✅ CPU 多进程基准测试完成!")
    print("=" * 70)


def main():
    """主函数"""
    print("=" * 70)
    print("CPU Multiprocess Optimizer v1.0 - CPU 密集型任务多进程优化器")
    print("=" * 70)
    
    import asyncio
    asyncio.run(benchmark_multiprocess())
    
    print("\n" + "=" * 70)
    print("✅ CPU 多进程优化器完成!")
    print("=" * 70)

if __name__ == '__main__':
    mp.freeze_support()  # Windows 支持
    main()
