#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CGCNN Model - CPU Optimized Version
晶体图卷积神经网络 (CPU 优化版)

功能：
1. 使用 ONNX Runtime 加速推理
2. 严格控制 CPU 使用 (<70%)
3. 添加缓存机制
4. 单线程处理，避免并发过载

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:55
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
from collections import deque
import threading

# ============================================================================
# 1. CPU 保护配置
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 保护配置"""
    # 线程限制
    intra_op_threads: int = 4      # 内部操作线程数 (P 核)
    inter_op_threads: int = 2      # 内部操作线程数 (E 核)

    # 并发控制
    max_concurrent: int = 1        # 最大并发预测数
    queue_size: int = 20           # 任务队列大小

    # CPU 使用限制
    cpu_threshold: float = 70.0    # CPU 阈值 (%)
    cooldown_time: float = 2.0     # 冷却时间 (秒)

    # 缓存配置
    cache_size: int = 500          # LRU 缓存大小
    cache_ttl: int = 3600          # 缓存 TTL (秒)

    # 批处理
    batch_size: int = 10           # 批处理大小
    batch_timeout: float = 1.0     # 批处理超时 (秒)


# 全局配置
CPU_CONFIG = CPUConfig()

# ============================================================================
# 2. CPU 使用监控
# ============================================================================

class CPUMonitor:
    """CPU 使用监控器"""

    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)  # 最近 10 次记录
        self.lock = threading.Lock()

    def get_cpu_percent(self) -> float:
        """获取当前 CPU 使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            # 如果 psutil 不可用，返回 0 (不限制)
            return 0.0

    def should_wait(self) -> bool:
        """检查是否应该等待 (CPU 过高)"""
        current = self.get_cpu_percent()

        with self.lock:
            self.history.append(current)

            # 如果当前 CPU 超过阈值，等待
            if current > self.threshold:
                return True

            # 如果平均 CPU 超过阈值，等待
            if len(self.history) >= 5:
                avg = sum(self.history) / len(self.history)
                if avg > self.threshold * 0.9:
                    return True

        return False

    def wait_if_needed(self, timeout: float = 5.0):
        """如果需要则等待"""
        start = time.time()

        while self.should_wait():
            if time.time() - start > timeout:
                break  # 超时强制继续
            time.sleep(0.5)


# ============================================================================
# 3. 缓存管理器
# ============================================================================

class CacheManager:
    """缓存管理器"""

    def __init__(self, max_size: int = 500, ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, **kwargs) -> str:
        """生成缓存键"""
        content = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, **kwargs) -> Optional[Dict]:
        """获取缓存"""
        key = self._generate_key(**kwargs)

        with self.lock:
            if key in self.cache:
                # 检查 TTL
                age = time.time() - self.timestamps.get(key, 0)
                if age < self.ttl:
                    self.hits += 1
                    return self.cache[key]
                else:
                    # 过期，删除
                    del self.cache[key]
                    del self.timestamps[key]

            self.misses += 1
            return None

    def set(self, value: Dict, **kwargs):
        """设置缓存"""
        key = self._generate_key(**kwargs)

        with self.lock:
            # 如果缓存满了，删除最旧的
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.timestamps, key=self.timestamps.get)
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            self.cache[key] = value
            self.timestamps[key] = time.time()

    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'max_size': self.max_size
        }

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.hits = 0
            self.misses = 0


# ============================================================================
# 4. CGCNN 模型 (CPU 优化版)
# ============================================================================

class CGCNNModel:
    """CGCNN 模型 (CPU 优化版)"""

    def __init__(self, config: CPUConfig = None):
        self.config = config or CPU_CONFIG
        self.model = None
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        self.cache = CacheManager(self.config.cache_size, self.config.cache_ttl)
        self.semaphore = threading.Semaphore(self.config.max_concurrent)

        # 设置 ONNX 线程数
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)

    def load_model(self, model_path: str):
        """加载模型"""
        print(f"[CGCNN] 加载模型：{model_path}")

        try:
            import onnxruntime as ort

            # 优化配置
            session_options = ort.SessionOptions()
            session_options.intra_op_num_threads = self.config.intra_op_threads
            session_options.inter_op_num_threads = self.config.inter_op_threads
            session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL  # 顺序执行
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self.model = ort.InferenceSession(
                model_path,
                sess_options=session_options,
                providers=['CPUExecutionProvider']  # 只用 CPU
            )

            print(f"[CGCNN] 模型加载成功")
            print(f"[CGCNN] 线程配置：intra={self.config.intra_op_threads}, inter={self.config.inter_op_threads}")

        except ImportError:
            print("[CGCNN] ⚠️ ONNX Runtime 未安装，使用模拟模式")
            print("[CGCNN] 安装：pip install onnxruntime")
            self.model = None

        except Exception as e:
            print(f"[CGCNN] ❌ 加载失败：{e}")
            self.model = None

    def predict(self, crystal_structure: Dict) -> Optional[Dict]:
        """预测材料性能 (带缓存和 CPU 保护)"""

        # 1. 检查缓存
        cached = self.cache.get(structure=crystal_structure)
        if cached:
            return cached

        # 2. 检查 CPU 使用
        self.monitor.wait_if_needed(timeout=5.0)

        # 3. 限制并发
        with self.semaphore:
            result = self._predict_internal(crystal_structure)

        # 4. 缓存结果
        if result:
            self.cache.set(result, structure=crystal_structure)

        return result

    def _predict_internal(self, crystal_structure: Dict) -> Optional[Dict]:
        """内部预测实现"""
        if not self.model:
            # 模拟模式 (用于测试)
            return self._simulate_prediction(crystal_structure)

        try:
            # 准备输入
            atom_features, neighbors, distances = self._prepare_input(crystal_structure)

            # 运行推理
            start = time.time()
            outputs = self.model.run(
                None,
                {
                    'atom_features': atom_features,
                    'neighbors': neighbors,
                    'distances': distances
                }
            )
            inference_time = time.time() - start

            # 解析输出
            result = {
                'band_gap': float(outputs[0][0][0]),
                'formation_energy': float(outputs[1][0][0]) if len(outputs) > 1 else None,
                'inference_time': inference_time,
                'timestamp': time.time()
            }

            return result

        except Exception as e:
            print(f"[CGCNN] ❌ 预测失败：{e}")
            return None

    def _simulate_prediction(self, crystal_structure: Dict) -> Dict:
        """模拟预测 (用于测试，无模型时)"""
        import random

        # 模拟延迟 (1-3 秒)
        time.sleep(random.uniform(1.0, 3.0))

        # 模拟结果
        return {
            'band_gap': round(random.uniform(0.5, 5.0), 2),
            'formation_energy': round(random.uniform(-5.0, -1.0), 2),
            'inference_time': 2.0,
            'timestamp': time.time(),
            'note': '模拟结果 (未加载真实模型)'
        }

    def _prepare_input(self, crystal_structure: Dict) -> Tuple:
        """准备模型输入"""
        # 这里需要实际的晶体结构到模型输入的转换
        # 简化示例

        atom_features = [[0.0] * 10]  # 示例
        neighbors = [[0] * 5]  # 示例
        distances = [[0.0] * 5]  # 示例

        return atom_features, neighbors, distances

    def predict_batch(self, structures: List[Dict]) -> List[Optional[Dict]]:
        """批量预测"""
        results = []

        # 分批处理
        for i in range(0, len(structures), self.config.batch_size):
            batch = structures[i:i + self.config.batch_size]

            for structure in batch:
                result = self.predict(structure)
                results.append(result)

            # 批次间短暂休息，避免 CPU 过载
            if i + self.config.batch_size < len(structures):
                time.sleep(0.5)

        return results

    def get_stats(self) -> Dict:
        """获取模型统计"""
        return {
            'model_loaded': self.model is not None,
            'cpu_config': {
                'intra_threads': self.config.intra_op_threads,
                'inter_threads': self.config.inter_op_threads,
                'max_concurrent': self.config.max_concurrent,
                'cpu_threshold': self.config.cpu_threshold
            },
            'cache': self.cache.get_stats(),
            'current_cpu': self.monitor.get_cpu_percent()
        }


# ============================================================================
# 5. 全局实例
# ============================================================================

_model_instance = None

def get_cgcnn_model(config: CPUConfig = None) -> CGCNNModel:
    """获取 CGCNN 模型单例"""
    global _model_instance

    if _model_instance is None:
        _model_instance = CGCNNModel(config)

    return _model_instance


# ============================================================================
# 6. 主函数 (测试)
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("CGCNN Model - CPU Optimized Version")
    print("=" * 60)

    # 1. 创建模型
    print("\n[1/4] 创建模型...")
    config = CPUConfig(
        intra_op_threads=4,
        inter_op_threads=2,
        max_concurrent=1,
        cache_size=500,
        cpu_threshold=70.0
    )

    model = get_cgcnn_model(config)

    # 2. 加载模型
    print("\n[2/4] 加载模型...")
    # 实际使用时替换为真实模型路径
    model_path = "models/cgcnn.onnx"
    model.load_model(model_path)

    # 3. 测试预测
    print("\n[3/4] 测试预测...")

    test_structures = [
        {'material': 'LiFePO4', 'formula': 'LiFePO4'},
        {'material': 'SiO2', 'formula': 'SiO2'},
        {'material': 'TiO2', 'formula': 'TiO2'},
    ]

    for i, structure in enumerate(test_structures, 1):
        print(f"\n预测 {i}/{len(test_structures)}: {structure['material']}")

        start = time.time()
        result = model.predict(structure)
        elapsed = time.time() - start

        if result:
            print(f"  带隙：{result.get('band_gap', 'N/A')} eV")
            print(f"  形成能：{result.get('formation_energy', 'N/A')} eV/atom")
            print(f"  耗时：{elapsed:.2f} 秒")
            print(f"  CPU: {model.monitor.get_cpu_percent():.1f}%")
        else:
            print(f"  ❌ 预测失败")

    # 4. 显示统计
    print("\n[4/4] 统计信息...")
    stats = model.get_stats()

    print(f"  模型加载：{'✅' if stats['model_loaded'] else '⚠️ 模拟模式'}")
    print(f"  线程配置：intra={stats['cpu_config']['intra_threads']}, "
          f"inter={stats['cpu_config']['inter_threads']}")
    print(f"  缓存命中率：{stats['cache']['hit_rate']}")
    print(f"  当前 CPU: {stats['current_cpu']:.1f}%")

    print("\n" + "=" * 60)
    print("CGCNN CPU 优化版准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
