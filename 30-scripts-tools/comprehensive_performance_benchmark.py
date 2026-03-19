#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Performance Benchmark - 综合性能基准测试

对比优化前后的性能，生成详细对比报告
"""

import json
import time
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List

WORKSPACE = "D:\\OpenClaw\\workspace"

class PerformanceBenchmark:
    """综合性能基准测试"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {}
        }
        
        # 导入优化工具
        try:
            from lru_cache_manager import LRUCache
            self.lru_cache = LRUCache(capacity=1000, ttl=3600)
        except:
            self.lru_cache = None
        
        try:
            from multi_level_cache import MultiLevelCache
            self.multi_cache = MultiLevelCache()
        except:
            self.multi_cache = None
        
        try:
            from query_result_cache import QueryResultCache
            self.query_cache = QueryResultCache(ttl=3600)
        except:
            self.query_cache = None
        
        try:
            from batch_parallel_processor import BatchParallelProcessor
            self.parallel_processor = BatchParallelProcessor(max_workers=10)
        except:
            self.parallel_processor = None
        
        try:
            from connection_pool_manager import DatabaseConnectionPool
            self.db_pool = None  # 延迟初始化
        except:
            self.db_pool = None
    
    def run_all_benchmarks(self) -> Dict:
        """运行所有基准测试"""
        print("=" * 70)
        print("Comprehensive Performance Benchmark - 综合性能基准测试")
        print("=" * 70)
        
        tests = [
            ("缓存性能测试", self.benchmark_cache),
            ("查询性能测试", self.benchmark_query),
            ("并行处理测试", self.benchmark_parallel),
            ("I/O 性能测试", self.benchmark_io),
            ("数据结构性能测试", self.benchmark_data_structures)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*70}")
            print(f"运行：{test_name}")
            print(f"{'='*70}")
            
            try:
                result = test_func()
                results[test_name] = result
                self.results['tests'].append({
                    'name': test_name,
                    'result': result,
                    'status': 'pass'
                })
            except Exception as e:
                results[test_name] = {'error': str(e)}
                self.results['tests'].append({
                    'name': test_name,
                    'result': {'error': str(e)},
                    'status': 'fail'
                })
        
        # 生成总结
        self.results['summary'] = self.generate_summary(results)
        
        return results
    
    def benchmark_cache(self) -> Dict:
        """缓存性能测试"""
        result = {
            'lru_cache': {},
            'multi_level_cache': {},
            'comparison': {}
        }
        
        # LRU 缓存测试
        if self.lru_cache:
            print("\n[1/2] LRU 缓存测试...")
            
            # 写入
            start = time.perf_counter()
            for i in range(1000):
                self.lru_cache.set(f"key_{i}", f"value_{i}" * 100)
            write_time = (time.perf_counter() - start) * 1000
            
            # 读取 (hit)
            start = time.perf_counter()
            for i in range(1000):
                self.lru_cache.get(f"key_{i}")
            read_time = (time.perf_counter() - start) * 1000
            
            stats = self.lru_cache.stats()
            
            result['lru_cache'] = {
                'write_1000_ms': round(write_time, 2),
                'read_1000_ms': round(read_time, 2),
                'hit_rate': stats['hit_rate'],
                'ops_per_sec': round(1000 / (read_time / 1000), 0)
            }
            
            print(f"✅ 写入 1000 项：{write_time:.2f}ms")
            print(f"✅ 读取 1000 项：{read_time:.2f}ms")
            print(f"✅ 命中率：{stats['hit_rate']}")
        
        # 多级缓存测试
        if self.multi_cache:
            print("\n[2/2] 多级缓存测试...")
            
            # 写入
            start = time.perf_counter()
            for i in range(1000):
                self.multi_cache.set(f"key_{i}", {"data": f"value_{i}" * 100})
            write_time = (time.perf_counter() - start) * 1000
            
            # L1 读取
            start = time.perf_counter()
            for i in range(1000):
                self.multi_cache.get(f"key_{i}")
            l1_read_time = (time.perf_counter() - start) * 1000
            
            stats = self.multi_cache.get_stats()
            
            result['multi_level_cache'] = {
                'write_1000_ms': round(write_time, 2),
                'l1_read_1000_ms': round(l1_read_time, 2),
                'l1_hit_rate': stats['l1_hit_rate'],
                'overall_hit_rate': stats['overall_hit_rate'],
                'l1_ops_per_sec': round(1000 / (l1_read_time / 1000), 0)
            }
            
            print(f"✅ 写入 1000 项：{write_time:.2f}ms")
            print(f"✅ L1 读取 1000 项：{l1_read_time:.2f}ms")
            print(f"✅ L1 命中率：{stats['l1_hit_rate']}")
        
        # 对比
        if result['lru_cache'] and result['multi_level_cache']:
            result['comparison'] = {
                'lru_vs_multi_write': round(
                    result['lru_cache']['write_1000_ms'] / result['multi_level_cache']['write_1000_ms'],
                    2
                ) if result['multi_level_cache']['write_1000_ms'] > 0 else 0,
                'lru_vs_multi_read': round(
                    result['lru_cache']['read_1000_ms'] / result['multi_level_cache']['l1_read_1000_ms'],
                    2
                ) if result['multi_level_cache']['l1_read_1000_ms'] > 0 else 0
            }
        
        return result
    
    def benchmark_query(self) -> Dict:
        """查询性能测试"""
        result = {
            'query_cache': {},
            'db_pool': {},
            'comparison': {}
        }
        
        # 创建测试数据库
        db_path = f"{WORKSPACE}\\cache\\benchmark_test.db"
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)')
        
        # 插入测试数据
        cursor.execute('SELECT COUNT(*) FROM test')
        count = cursor.fetchone()[0]
        if count < 1000:
            for i in range(1000 - count):
                cursor.execute('INSERT INTO test (value) VALUES (?)', (f'value_{i}',))
            conn.commit()
        conn.close()
        
        # 查询缓存测试
        if self.query_cache:
            print("\n[1/2] 查询缓存测试...")
            
            # 无缓存查询
            start = time.perf_counter()
            for i in range(100):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM test WHERE id = ?', (i % 1000,))
                _ = cursor.fetchone()
                conn.close()
            no_cache_time = (time.perf_counter() - start) * 1000
            
            # 有缓存查询
            start = time.perf_counter()
            for i in range(100):
                query = f"SELECT * FROM test WHERE id = {i % 1000}"
                result_data = self.query_cache.get(query)
                if result_data is None:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute(query)
                    result_data = cursor.fetchone()
                    conn.close()
                    self.query_cache.set(query, None, list(result_data) if result_data else None)
            cache_time = (time.perf_counter() - start) * 1000
            
            stats = self.query_cache.stats()
            
            result['query_cache'] = {
                'no_cache_100_ms': round(no_cache_time, 2),
                'with_cache_100_ms': round(cache_time, 2),
                'speedup': round(no_cache_time / cache_time, 2) if cache_time > 0 else 0,
                'hit_rate': stats['hit_rate']
            }
            
            print(f"✅ 无缓存 100 次：{no_cache_time:.2f}ms")
            print(f"✅ 有缓存 100 次：{cache_time:.2f}ms")
            print(f"✅ 加速比：{result['query_cache']['speedup']:.2f}x")
        
        # 连接池测试
        print("\n[2/2] 连接池测试...")
        
        if self.db_pool is None:
            from connection_pool_manager import DatabaseConnectionPool
            self.db_pool = DatabaseConnectionPool(db_path, pool_size=10)
        
        # 无连接池
        start = time.perf_counter()
        for i in range(100):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM test WHERE id = ?', (i % 1000,))
            _ = cursor.fetchone()
            conn.close()
        no_pool_time = (time.perf_counter() - start) * 1000
        
        # 有连接池
        start = time.perf_counter()
        for i in range(100):
            conn = self.db_pool.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM test WHERE id = ?', (i % 1000,))
                _ = cursor.fetchone()
                self.db_pool.return_connection(conn)
        pool_time = (time.perf_counter() - start) * 1000
        
        pool_stats = self.db_pool.stats()
        
        result['db_pool'] = {
            'no_pool_100_ms': round(no_pool_time, 2),
            'with_pool_100_ms': round(pool_time, 2),
            'speedup': round(no_pool_time / pool_time, 2) if pool_time > 0 else 0,
            'reuse_rate': pool_stats['reuse_rate']
        }
        
        print(f"✅ 无连接池 100 次：{no_pool_time:.2f}ms")
        print(f"✅ 有连接池 100 次：{pool_time:.2f}ms")
        print(f"✅ 加速比：{result['db_pool']['speedup']:.2f}x")
        
        # 清理
        self.db_pool.close_all()
        
        # 总体对比
        if result['query_cache'] and result['db_pool']:
            result['comparison'] = {
                'cache_speedup': result['query_cache']['speedup'],
                'pool_speedup': result['db_pool']['speedup'],
                'combined_speedup': round(
                    (result['query_cache']['speedup'] + result['db_pool']['speedup']) / 2,
                    2
                )
            }
        
        return result
    
    def benchmark_parallel(self) -> Dict:
        """并行处理测试"""
        result = {}
        
        if not self.parallel_processor:
            return {'error': 'Parallel processor not available'}
        
        print("\n[1/1] 并行处理测试...")
        
        # I/O 密集型任务
        def io_task(item):
            time.sleep(0.001)
            return item * 2
        
        items = list(range(100))
        
        # 顺序处理
        start = time.perf_counter()
        self.parallel_processor.process_sequential(items, io_task)
        sequential_time = (time.perf_counter() - start) * 1000
        
        # 并行处理
        start = time.perf_counter()
        self.parallel_processor.process_parallel(items, io_task)
        parallel_time = (time.perf_counter() - start) * 1000
        
        stats = self.parallel_processor.get_stats()
        
        result = {
            'sequential_100_ms': round(sequential_time, 2),
            'parallel_100_ms': round(parallel_time, 2),
            'speedup': round(sequential_time / parallel_time, 2) if parallel_time > 0 else 0,
            'improvement': round((sequential_time - parallel_time) / sequential_time * 100, 1),
            'avg_time_per_task_ms': round(stats['avg_time_per_task_ms'], 3)
        }
        
        print(f"✅ 顺序处理 100 项：{sequential_time:.2f}ms")
        print(f"✅ 并行处理 100 项：{parallel_time:.2f}ms")
        print(f"✅ 加速比：{result['speedup']:.2f}x")
        print(f"✅ 提升：{result['improvement']:.1f}%")
        
        self.parallel_processor.shutdown()
        
        return result
    
    def benchmark_io(self) -> Dict:
        """I/O 性能测试"""
        result = {}
        
        print("\n[1/1] I/O 性能测试...")
        
        # 创建测试文件
        test_dir = Path(f"{WORKSPACE}\\temp\\benchmark_io")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_files = []
        for i in range(50):
            file_path = test_dir / f"test_{i}.txt"
            content = f"Test content {i}\n" * 100
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            test_files.append(str(file_path))
        
        # 同步读取
        start = time.perf_counter()
        for file_path in test_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                _ = f.read()
        sync_time = (time.perf_counter() - start) * 1000
        
        # 缓冲 I/O (Python 默认已缓冲)
        start = time.perf_counter()
        for file_path in test_files:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                _ = f.read()
        buffered_time = (time.perf_counter() - start) * 1000
        
        result = {
            'sync_read_50_ms': round(sync_time, 2),
            'buffered_read_50_ms': round(buffered_time, 2),
            'file_count': len(test_files)
        }
        
        print(f"✅ 同步读取 50 文件：{sync_time:.2f}ms")
        print(f"✅ 缓冲读取 50 文件：{buffered_time:.2f}ms")
        
        # 清理
        for file_path in test_files:
            Path(file_path).unlink()
        test_dir.rmdir()
        
        return result
    
    def benchmark_data_structures(self) -> Dict:
        """数据结构性能测试"""
        result = {}
        
        print("\n[1/1] 数据结构性能测试...")
        
        # 准备数据
        test_list = list(range(10000))
        test_set = set(test_list)
        test_dict = {i: f"value_{i}" for i in range(10000)}
        
        # List 查找
        start = time.perf_counter()
        for i in range(1000):
            _ = 5000 in test_list
        list_time = (time.perf_counter() - start) * 1000
        
        # Set 查找
        start = time.perf_counter()
        for i in range(1000):
            _ = 5000 in test_set
        set_time = (time.perf_counter() - start) * 1000
        
        # Dict 查找
        start = time.perf_counter()
        for i in range(1000):
            _ = 5000 in test_dict
        dict_time = (time.perf_counter() - start) * 1000
        
        result = {
            'list_lookup_1000_ms': round(list_time, 2),
            'set_lookup_1000_ms': round(set_time, 2),
            'dict_lookup_1000_ms': round(dict_time, 2),
            'list_vs_set_speedup': round(list_time / set_time, 2) if set_time > 0 else 0,
            'list_vs_dict_speedup': round(list_time / dict_time, 2) if dict_time > 0 else 0
        }
        
        print(f"✅ List 查找 1000 次：{list_time:.2f}ms")
        print(f"✅ Set 查找 1000 次：{set_time:.2f}ms")
        print(f"✅ Dict 查找 1000 次：{dict_time:.2f}ms")
        print(f"✅ List vs Set 加速：{result['list_vs_set_speedup']:.2f}x")
        print(f"✅ List vs Dict 加速：{result['list_vs_dict_speedup']:.2f}x")
        
        return result
    
    def generate_summary(self, results: Dict) -> Dict:
        """生成总结"""
        summary = {
            'total_tests': len(results),
            'passed_tests': sum(1 for r in results.values() if 'error' not in r),
            'failed_tests': sum(1 for r in results.values() if 'error' in r),
            'key_metrics': {}
        }
        
        # 提取关键指标
        if '缓存性能测试' in results and 'lru_cache' in results['缓存性能测试']:
            lru = results['缓存性能测试']['lru_cache']
            summary['key_metrics']['lru_cache_ops_sec'] = lru.get('ops_per_sec', 0)
        
        if '查询性能测试' in results:
            query = results['查询性能测试']
            if 'query_cache' in query:
                summary['key_metrics']['query_cache_speedup'] = query['query_cache'].get('speedup', 0)
            if 'db_pool' in query:
                summary['key_metrics']['db_pool_speedup'] = query['db_pool'].get('speedup', 0)
        
        if '并行处理测试' in results:
            parallel = results['并行处理测试']
            if 'speedup' in parallel:
                summary['key_metrics']['parallel_speedup'] = parallel['speedup']
        
        if '数据结构性能测试' in results:
            ds = results['数据结构性能测试']
            summary['key_metrics']['set_speedup_vs_list'] = ds.get('list_vs_set_speedup', 0)
        
        # 总体评估
        speedups = [
            summary['key_metrics'].get('query_cache_speedup', 0),
            summary['key_metrics'].get('db_pool_speedup', 0),
            summary['key_metrics'].get('parallel_speedup', 0),
            summary['key_metrics'].get('set_speedup_vs_list', 0)
        ]
        
        avg_speedup = sum(speedups) / len(speedups) if speedups else 0
        summary['overall_speedup'] = round(avg_speedup, 2)
        summary['performance_rating'] = (
            "优秀" if avg_speedup >= 5 else
            "良好" if avg_speedup >= 2 else
            "一般"
        )
        
        return summary
    
    def save_report(self, output_path: str = None):
        """保存报告"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{WORKSPACE}\\21-reports\\performance-benchmark-{timestamp}.json"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """主函数"""
    print("=" * 70)
    print("Comprehensive Performance Benchmark v1.0 - 综合性能基准测试")
    print("=" * 70)
    
    benchmark = PerformanceBenchmark()
    
    # 运行所有测试
    results = benchmark.run_all_benchmarks()
    
    # 保存报告
    output_path = benchmark.save_report()
    print(f"\n✅ 报告已保存：{output_path}")
    
    # 显示总结
    summary = benchmark.results['summary']
    print(f"\n{'='*70}")
    print("测试总结")
    print(f"{'='*70}")
    print(f"总测试数：{summary['total_tests']}")
    print(f"通过：{summary['passed_tests']}")
    print(f"失败：{summary['failed_tests']}")
    print(f"总体加速比：{summary['overall_speedup']:.2f}x")
    print(f"性能评级：{summary['performance_rating']}")
    
    print(f"\n{'='*70}")
    print("✅ 综合性能基准测试完成!")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
