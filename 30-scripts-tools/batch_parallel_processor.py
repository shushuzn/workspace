#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch Parallel Processor - 批量操作并行处理器

将批量操作并行执行，提升速度 3-5x
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from typing import Callable, List, Any, Dict

class BatchParallelProcessor:
    """批量并行处理器"""
    
    def __init__(self, max_workers=10, use_processes=False):
        """
        初始化并行处理器
        
        Args:
            max_workers: 最大 worker 数量
            use_processes: 是否使用多进程 (CPU 密集型) vs 多线程 (I/O 密集型)
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        
        if use_processes:
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        self.stats = {
            'tasks_processed': 0,
            'total_time_ms': 0,
            'avg_time_per_task_ms': 0,
            'speedup': 0
        }
    
    def process_sequential(self, items: List[Any], processor: Callable) -> List[Any]:
        """
        顺序处理
        
        Args:
            items: 待处理项列表
            processor: 处理函数
        
        Returns:
            处理结果列表
        """
        start = time.perf_counter()
        
        results = []
        for item in items:
            result = processor(item)
            results.append(result)
        
        elapsed = (time.perf_counter() - start) * 1000
        
        self.stats['tasks_processed'] += len(items)
        self.stats['total_time_ms'] += elapsed
        self.stats['avg_time_per_task_ms'] = elapsed / len(items) if items else 0
        
        return results
    
    def process_parallel(self, items: List[Any], processor: Callable) -> List[Any]:
        """
        并行处理
        
        Args:
            items: 待处理项列表
            processor: 处理函数
        
        Returns:
            处理结果列表
        """
        start = time.perf_counter()
        
        # 提交所有任务
        futures = {self.executor.submit(processor, item): i for i, item in enumerate(items)}
        
        # 收集结果 (保持顺序)
        results = [None] * len(items)
        for future in as_completed(futures):
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as e:
                results[index] = {'error': str(e)}
        
        elapsed = (time.perf_counter() - start) * 1000
        
        # 计算加速比
        sequential_time = self.stats.get('last_sequential_time', elapsed)
        speedup = sequential_time / elapsed if elapsed > 0 else 1
        
        self.stats['tasks_processed'] += len(items)
        self.stats['total_time_ms'] += elapsed
        self.stats['avg_time_per_task_ms'] = elapsed / len(items) if items else 0
        self.stats['speedup'] = speedup
        self.stats['last_parallel_time'] = elapsed
        
        return results
    
    async def process_parallel_async(self, items: List[Any], processor: Callable) -> List[Any]:
        """
        异步并行处理
        
        Args:
            items: 待处理项列表
            processor: 异步处理函数
        
        Returns:
            处理结果列表
        """
        start = time.perf_counter()
        
        # 创建任务
        tasks = [processor(item) for item in items]
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = (time.perf_counter() - start) * 1000
        
        self.stats['tasks_processed'] += len(items)
        self.stats['total_time_ms'] += elapsed
        self.stats['avg_time_per_task_ms'] = elapsed / len(items) if items else 0
        
        return results
    
    def process_batch_files(self, file_paths: List[str], processor: Callable) -> Dict:
        """
        批量处理文件
        
        Args:
            file_paths: 文件路径列表
            processor: 文件处理函数 (接收文件内容)
        
        Returns:
            处理结果字典
        """
        def process_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result = processor(content)
                return {'file': file_path, 'result': result, 'status': 'success'}
            except Exception as e:
                return {'file': file_path, 'result': None, 'status': 'failed', 'error': str(e)}
        
        return self.process_parallel(file_paths, process_file)
    
    def get_stats(self):
        """获取统计信息"""
        return {
            **self.stats,
            'max_workers': self.max_workers,
            'executor_type': 'ProcessPool' if self.use_processes else 'ThreadPool'
        }
    
    def shutdown(self):
        """关闭执行器"""
        self.executor.shutdown(wait=True)


async def benchmark_parallel_processing():
    """基准测试并行处理性能"""
    print("\n" + "=" * 60)
    print("Batch Parallel Processor Benchmark - 批量并行处理基准测试")
    print("=" * 60)
    
    # 模拟 I/O 密集型任务
    def io_bound_task(item):
        time.sleep(0.01)  # 模拟 10ms I/O 延迟
        return item * 2
    
    # 模拟 CPU 密集型任务
    def cpu_bound_task(item):
        result = 0
        for i in range(100000):
            result += i
        return result
    
    processor = BatchParallelProcessor(max_workers=10, use_processes=False)
    
    # 测试 1: 顺序处理 (I/O 密集型)
    print("\n[1/4] 顺序处理测试 (I/O 密集型)...")
    items = list(range(50))
    
    start = time.perf_counter()
    sequential_results = processor.process_sequential(items, io_bound_task)
    sequential_time = (time.perf_counter() - start) * 1000
    
    processor.stats['last_sequential_time'] = sequential_time
    print(f"✅ 顺序处理 50 项：{sequential_time:.2f}ms")
    
    # 测试 2: 并行处理 (I/O 密集型)
    print("\n[2/4] 并行处理测试 (I/O 密集型)...")
    
    start = time.perf_counter()
    parallel_results = processor.process_parallel(items, io_bound_task)
    parallel_time = (time.perf_counter() - start) * 1000
    
    print(f"✅ 并行处理 50 项：{parallel_time:.2f}ms")
    
    # 计算加速比
    io_speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
    io_improvement = ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0
    
    print(f"\n📊 I/O 密集型性能:")
    print(f"  顺序时间：{sequential_time:.2f}ms")
    print(f"  并行时间：{parallel_time:.2f}ms")
    print(f"  加速比：{io_speedup:.2f}x")
    print(f"  提升：{io_improvement:.1f}%")
    
    # 测试 3: 顺序处理 (CPU 密集型)
    print("\n[3/4] 顺序处理测试 (CPU 密集型)...")
    items = list(range(20))
    
    start = time.perf_counter()
    sequential_results = processor.process_sequential(items, cpu_bound_task)
    sequential_time_cpu = (time.perf_counter() - start) * 1000
    
    print(f"✅ 顺序处理 20 项：{sequential_time_cpu:.2f}ms")
    
    # 测试 4: 多进程处理 (CPU 密集型)
    print("\n[4/4] 多进程处理测试 (CPU 密集型)...")
    
    cpu_processor = BatchParallelProcessor(max_workers=4, use_processes=True)
    
    start = time.perf_counter()
    parallel_results = cpu_processor.process_parallel(items, cpu_bound_task)
    parallel_time_cpu = (time.perf_counter() - start) * 1000
    
    print(f"✅ 多进程处理 20 项：{parallel_time_cpu:.2f}ms")
    
    cpu_speedup = sequential_time_cpu / parallel_time_cpu if parallel_time_cpu > 0 else float('inf')
    cpu_improvement = ((sequential_time_cpu - parallel_time_cpu) / sequential_time_cpu * 100) if sequential_time_cpu > 0 else 0
    
    print(f"\n📊 CPU 密集型性能:")
    print(f"  顺序时间：{sequential_time_cpu:.2f}ms")
    print(f"  并行时间：{parallel_time_cpu:.2f}ms")
    print(f"  加速比：{cpu_speedup:.2f}x")
    print(f"  提升：{cpu_improvement:.1f}%")
    
    # 显示统计
    stats = processor.get_stats()
    print(f"\n📊 处理器统计:")
    print(f"  处理任务数：{stats['tasks_processed']}")
    print(f"  总时间：{stats['total_time_ms']:.2f}ms")
    print(f"  平均时间：{stats['avg_time_per_task_ms']:.2f}ms/任务")
    print(f"  加速比：{stats['speedup']:.2f}x")
    print(f"  Worker 类型：{stats['executor_type']}")
    
    # 清理
    processor.shutdown()
    cpu_processor.shutdown()
    
    print("\n" + "=" * 60)
    print("✅ 批量并行处理基准测试完成!")
    print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("Batch Parallel Processor v1.0 - 批量操作并行化")
    print("=" * 60)
    
    import asyncio
    asyncio.run(benchmark_parallel_processing())
    
    print("\n" + "=" * 60)
    print("✅ 批量操作并行化完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
