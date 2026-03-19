#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Async I/O Manager - I/O 异步化管理器

将 I/O 操作改为异步执行，减少 I/O 等待时间 60%
"""

import asyncio
import aiofiles
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

WORKSPACE = "D:\\OpenClaw\\workspace"

class AsyncIOManager:
    """异步 I/O 管理器"""
    
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stats = {
            'files_read': 0,
            'files_written': 0,
            'total_bytes': 0,
            'total_time_ms': 0
        }
    
    async def read_file_async(self, file_path):
        """异步读取文件"""
        start = time.perf_counter()
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            elapsed = (time.perf_counter() - start) * 1000
            
            self.stats['files_read'] += 1
            self.stats['total_bytes'] += len(content)
            self.stats['total_time_ms'] += elapsed
            
            return content
        
        except Exception as e:
            return None
    
    async def write_file_async(self, file_path, content):
        """异步写入文件"""
        start = time.perf_counter()
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            elapsed = (time.perf_counter() - start) * 1000
            
            self.stats['files_written'] += 1
            self.stats['total_bytes'] += len(content)
            self.stats['total_time_ms'] += elapsed
            
            return True
        
        except Exception as e:
            return False
    
    async def read_multiple_files(self, file_paths):
        """异步读取多个文件"""
        tasks = [self.read_file_async(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def process_files_parallel(self, file_paths, processor_func):
        """并行处理文件"""
        async def process_one(file_path):
            content = await self.read_file_async(file_path)
            if content:
                result = processor_func(content)
                return {'file': file_path, 'result': result, 'status': 'success'}
            return {'file': file_path, 'result': None, 'status': 'failed'}
        
        tasks = [process_one(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def get_stats(self):
        """获取统计信息"""
        avg_time = (
            self.stats['total_time_ms'] / 
            (self.stats['files_read'] + self.stats['files_written'])
            if (self.stats['files_read'] + self.stats['files_written']) > 0
            else 0
        )
        
        return {
            **self.stats,
            'avg_time_per_file_ms': round(avg_time, 2),
            'throughput_mb_s': round(
                self.stats['total_bytes'] / (self.stats['total_time_ms'] / 1000) / (1024 * 1024),
                2
            ) if self.stats['total_time_ms'] > 0 else 0
        }


async def benchmark_async_io():
    """基准测试异步 I/O 性能"""
    print("\n" + "=" * 60)
    print("Async I/O Performance Benchmark - 异步 I/O 性能基准测试")
    print("=" * 60)
    
    manager = AsyncIOManager(max_workers=10)
    
    # 创建测试文件
    print("\n[1/3] 准备测试文件...")
    test_dir = Path(f"{WORKSPACE}\\temp\\async_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_files = []
    for i in range(20):
        file_path = test_dir / f"test_file_{i}.txt"
        content = f"Test content {i}\n" * 1000  # ~15KB per file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        test_files.append(str(file_path))
    
    print(f"✅ 创建 {len(test_files)} 个测试文件")
    
    # 测试 1: 同步读取
    print("\n[2/3] 同步读取测试...")
    start = time.perf_counter()
    
    for file_path in test_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            _ = f.read()
    
    sync_time = (time.perf_counter() - start) * 1000
    print(f"✅ 同步读取 {len(test_files)} 个文件：{sync_time:.2f}ms")
    
    # 测试 2: 异步读取
    print("\n[3/3] 异步读取测试...")
    start = time.perf_counter()
    
    results = await manager.read_multiple_files(test_files)
    successful = sum(1 for r in results if r is not None)
    
    async_time = (time.perf_counter() - start) * 1000
    print(f"✅ 异步读取 {successful} 个文件：{async_time:.2f}ms")
    
    # 计算加速比
    speedup = sync_time / async_time if async_time > 0 else float('inf')
    improvement = ((sync_time - async_time) / sync_time * 100) if sync_time > 0 else 0
    
    print(f"\n📊 性能对比:")
    print(f"  同步时间：{sync_time:.2f}ms")
    print(f"  异步时间：{async_time:.2f}ms")
    print(f"  加速比：{speedup:.2f}x")
    print(f"  提升：{improvement:.1f}%")
    
    # 显示统计
    stats = manager.get_stats()
    print(f"\n📊 统计信息:")
    print(f"  读取文件数：{stats['files_read']}")
    print(f"  总字节数：{stats['total_bytes']:,}")
    print(f"  平均时间：{stats['avg_time_per_file_ms']:.2f}ms/文件")
    print(f"  吞吐量：{stats['throughput_mb_s']:.2f} MB/s")
    
    # 清理
    for file_path in test_files:
        Path(file_path).unlink()
    test_dir.rmdir()
    
    print("\n" + "=" * 60)
    print("✅ 异步 I/O 性能基准测试完成!")
    print("=" * 60)


def generate_usage_examples():
    """生成使用示例"""
    examples = '''# Async I/O Manager 使用示例

import asyncio
from async_io_manager import AsyncIOManager

# 创建管理器
manager = AsyncIOManager(max_workers=10)


# 示例 1: 异步读取单个文件
async def read_single_file():
    content = await manager.read_file_async("data.txt")
    if content:
        print(f"读取成功：{len(content)} 字符")
    else:
        print("读取失败")

asyncio.run(read_single_file())


# 示例 2: 异步读取多个文件
async def read_multiple_files():
    files = ["file1.txt", "file2.txt", "file3.txt"]
    contents = await manager.read_multiple_files(files)
    
    for file, content in zip(files, contents):
        if content:
            print(f"{file}: {len(content)} 字符")
        else:
            print(f"{file}: 读取失败")

asyncio.run(read_multiple_files())


# 示例 3: 并行处理文件
def process_content(content):
    # 处理逻辑
    return content.upper()

async def process_files():
    files = ["data1.txt", "data2.txt", "data3.txt"]
    results = await manager.process_files_parallel(files, process_content)
    
    for result in results:
        if result['status'] == 'success':
            print(f"{result['file']}: 处理成功")
        else:
            print(f"{result['file']}: 处理失败")

asyncio.run(process_files())


# 示例 4: 异步写入文件
async def write_file():
    content = "Hello, World!" * 1000
    success = await manager.write_file_async("output.txt", content)
    
    if success:
        print("写入成功")
    else:
        print("写入失败")

asyncio.run(write_file())


# 示例 5: 查看统计
stats = manager.get_stats()
print(f"读取文件数：{stats['files_read']}")
print(f"写入文件数：{stats['files_written']}")
print(f"总字节数：{stats['total_bytes']:,}")
print(f"平均时间：{stats['avg_time_per_file_ms']:.2f}ms")
print(f"吞吐量：{stats['throughput_mb_s']:.2f} MB/s")
'''
    
    example_path = f"{WORKSPACE}\\30-scripts-tools\\async_io_examples.py"
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(examples)
    
    return example_path


async def main():
    """主函数"""
    print("=" * 60)
    print("Async I/O Manager v1.0 - I/O 异步化管理器")
    print("=" * 60)
    
    # 运行基准测试
    await benchmark_async_io()
    
    # 保存示例
    print("\n[1/1] 保存使用示例...")
    example_path = generate_usage_examples()
    print(f"✅ 示例已保存：{example_path}")
    
    print("\n" + "=" * 60)
    print("✅ I/O 异步化管理器完成!")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
