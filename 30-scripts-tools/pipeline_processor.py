#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline Processor - 流水线处理器

将任务拆分为多个阶段，各阶段并行处理不同数据，吞吐量提升 2-3x
"""

import threading
import queue
import time
from pathlib import Path
from datetime import datetime
from typing import Callable, List, Any, Dict
from concurrent.futures import ThreadPoolExecutor

class PipelineStage:
    """流水线阶段"""
    
    def __init__(self, name: str, processor: Callable, output_queue=None):
        """
        初始化流水线阶段
        
        Args:
            name: 阶段名称
            processor: 处理函数
            output_queue: 输出队列
        """
        self.name = name
        self.processor = processor
        self.output_queue = output_queue
        self.input_queue = queue.Queue()
        self.stats = {
            'items_processed': 0,
            'total_time_ms': 0,
            'errors': 0
        }
        self.running = False
        self.thread = None
    
    def start(self):
        """启动阶段"""
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """停止阶段"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _process_loop(self):
        """处理循环"""
        while self.running:
            try:
                item = self.input_queue.get(timeout=0.1)
                
                start = time.perf_counter()
                
                try:
                    result = self.processor(item)
                    
                    if self.output_queue and result is not None:
                        self.output_queue.put(result)
                    
                    elapsed = (time.perf_counter() - start) * 1000
                    self.stats['items_processed'] += 1
                    self.stats['total_time_ms'] += elapsed
                
                except Exception as e:
                    self.stats['errors'] += 1
                
                self.input_queue.task_done()
            
            except queue.Empty:
                continue
    
    def put(self, item):
        """添加输入项"""
        self.input_queue.put(item)
    
    def get_stats(self) -> dict:
        """获取统计"""
        avg_time = (
            self.stats['total_time_ms'] / self.stats['items_processed']
            if self.stats['items_processed'] > 0 else 0
        )
        
        return {
            'name': self.name,
            'items_processed': self.stats['items_processed'],
            'avg_time_ms': round(avg_time, 3),
            'errors': self.stats['errors']
        }


class PipelineProcessor:
    """流水线处理器"""
    
    def __init__(self, stages: List[PipelineStage]):
        """
        初始化流水线
        
        Args:
            stages: 流水线阶段列表
        """
        self.stages = stages
        self.stats = {
            'total_items': 0,
            'completed_items': 0,
            'throughput_per_sec': 0,
            'total_time_ms': 0
        }
        
        # 连接阶段
        for i in range(len(stages) - 1):
            stages[i].output_queue = stages[i + 1].input_queue
    
    def start(self):
        """启动流水线"""
        for stage in self.stages:
            stage.start()
    
    def stop(self):
        """停止流水线"""
        for stage in reversed(self.stages):
            stage.stop()
    
    def process(self, items: List[Any]) -> List[Any]:
        """
        处理数据
        
        Args:
            items: 输入数据列表
        
        Returns:
            处理结果列表
        """
        start = time.perf_counter()
        
        # 收集最终输出
        results = []
        result_queue = queue.Queue()
        self.stages[-1].output_queue = result_queue
        
        # 启动流水线
        self.start()
        
        # 输入数据
        for item in items:
            self.stages[0].put(item)
        
        # 等待所有输入处理完成
        self.stages[0].input_queue.join()
        
        # 收集结果
        time.sleep(0.1)  # 等待最后的结果
        while not result_queue.empty():
            try:
                results.append(result_queue.get_nowait())
            except:
                break
        
        # 停止流水线
        self.stop()
        
        elapsed = (time.perf_counter() - start) * 1000
        
        self.stats['total_items'] = len(items)
        self.stats['completed_items'] = len(results)
        self.stats['total_time_ms'] = elapsed
        self.stats['throughput_per_sec'] = len(results) / (elapsed / 1000) if elapsed > 0 else 0
        
        return results
    
    def process_sequential(self, items: List[Any], processors: List[Callable]) -> List[Any]:
        """
        顺序处理 (用于对比)
        
        Args:
            items: 输入数据列表
            processors: 处理函数列表
        
        Returns:
            处理结果列表
        """
        start = time.perf_counter()
        
        results = []
        for item in items:
            current = item
            for processor in processors:
                current = processor(current)
            results.append(current)
        
        elapsed = (time.perf_counter() - start) * 1000
        
        return results, elapsed
    
    def get_stats(self) -> dict:
        """获取统计"""
        stage_stats = [stage.get_stats() for stage in self.stages]
        
        return {
            **self.stats,
            'stages': len(self.stages),
            'stage_stats': stage_stats
        }


# 示例处理函数
def stage_read(data):
    """阶段 1: 读取数据"""
    time.sleep(0.001)  # 模拟 I/O
    return {'read': data, 'timestamp': time.time()}


def stage_process(data):
    """阶段 2: 处理数据"""
    time.sleep(0.001)  # 模拟计算
    data['processed'] = True
    return data


def stage_write(data):
    """阶段 3: 写入数据"""
    time.sleep(0.001)  # 模拟 I/O
    data['written'] = True
    return data


async def benchmark_pipeline():
    """基准测试流水线性能"""
    print("\n" + "=" * 70)
    print("Pipeline Processor Benchmark - 流水线基准测试")
    print("=" * 70)
    
    items = list(range(100))
    
    # 创建流水线
    stages = [
        PipelineStage("Read", stage_read),
        PipelineStage("Process", stage_process),
        PipelineStage("Write", stage_write)
    ]
    
    pipeline = PipelineProcessor(stages)
    
    # 顺序处理
    print("\n[1/2] 顺序处理测试...")
    processors = [stage_read, stage_process, stage_write]
    
    start = time.perf_counter()
    sequential_results, sequential_time = pipeline.process_sequential(items, processors)
    
    print(f"✅ 顺序处理 100 项：{sequential_time:.2f}ms")
    print(f"✅ 吞吐量：{100 / (sequential_time / 1000):.0f} 项/秒")
    
    # 流水线处理
    print("\n[2/2] 流水线处理测试...")
    
    start = time.perf_counter()
    pipeline_results = pipeline.process(items)
    pipeline_time = pipeline.stats['total_time_ms']
    
    print(f"✅ 流水线处理 {len(pipeline_results)} 项：{pipeline_time:.2f}ms")
    print(f"✅ 吞吐量：{pipeline.stats['throughput_per_sec']:.0f} 项/秒")
    
    # 计算加速比
    speedup = sequential_time / pipeline_time if pipeline_time > 0 else float('inf')
    improvement = ((sequential_time - pipeline_time) / sequential_time * 100) if sequential_time > 0 else 0
    
    print(f"\n📊 流水线性能:")
    print(f"  顺序时间：{sequential_time:.2f}ms")
    print(f"  流水线时间：{pipeline_time:.2f}ms")
    print(f"  加速比：{speedup:.2f}x")
    print(f"  提升：{improvement:.1f}%")
    
    # 显示阶段统计
    stats = pipeline.get_stats()
    print(f"\n📊 阶段统计:")
    for stage_stat in stats['stage_stats']:
        print(f"  {stage_stat['name']}: {stage_stat['items_processed']} 项，{stage_stat['avg_time_ms']:.3f}ms/项")
    
    print(f"\n📊 总体统计:")
    print(f"  阶段数：{stats['stages']}")
    print(f"  总处理：{stats['total_items']} 项")
    print(f"  完成：{stats['completed_items']} 项")
    print(f"  吞吐量：{stats['throughput_per_sec']:.0f} 项/秒")
    
    print("\n" + "=" * 70)
    print("✅ 流水线基准测试完成!")
    print("=" * 70)


def main():
    """主函数"""
    print("=" * 70)
    print("Pipeline Processor v1.0 - 流水线处理器")
    print("=" * 70)
    
    import asyncio
    asyncio.run(benchmark_pipeline())
    
    print("\n" + "=" * 70)
    print("✅ 流水线处理器完成!")
    print("=" * 70)

if __name__ == '__main__':
    main()
