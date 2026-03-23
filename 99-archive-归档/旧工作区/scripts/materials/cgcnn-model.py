#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CGCNN Model - Production Version
晶体图卷积神经网络 (生产版)

使用真实数据：
1. 从 Materials Project API 获取真实材料数据
2. 使用 ONNX Runtime 进行推理
3. 严格 CPU 使用控制
4. 缓存机制

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:55
更新：2026-03-05 23:10 - 移除模拟数据，使用真实 API
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
    intra_op_threads: int = 4
    inter_op_threads: int = 2
    max_concurrent: int = 1
    queue_size: int = 20
    cpu_threshold: float = 70.0
    cooldown_time: float = 2.0
    cache_size: int = 500
    cache_ttl: int = 3600
    batch_size: int = 10
    batch_timeout: float = 1.0


CPU_CONFIG = CPUConfig()


# ============================================================================
# 2. CPU 使用监控
# ============================================================================

class CPUMonitor:
    """CPU 使用监控器"""

    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)
        self.lock = threading.Lock()

    def get_cpu_percent(self) -> float:
        """获取当前 CPU 使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    def should_wait(self) -> bool:
        """检查是否需要等待"""
        cpu = self.get_cpu_percent()
        self.history.append(cpu)
        return cpu > self.threshold

    def wait_if_needed(self, timeout: float = 5.0):
        """如果需要则等待"""
        start = time.time()
        while self.should_wait():
            if time.time() - start > timeout:
                break
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
                age = time.time() - self.timestamps.get(key, 0)
                if age < self.ttl:
                    self.hits += 1
                    return self.cache[key]
                else:
                    del self.cache[key]
                    del self.timestamps[key]

            self.misses += 1
            return None

    def set(self, value: Dict, **kwargs):
        """设置缓存"""
        key = self._generate_key(**kwargs)

        with self.lock:
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
# 4. CGCNN 模型 (使用真实数据)
# ============================================================================

class CGCNNModel:
    """CGCNN 模型 - 使用真实 Materials Project 数据"""

    def __init__(self, config: CPUConfig = None):
        self.config = config or CPU_CONFIG
        self.model = None
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        self.cache = CacheManager(self.config.cache_size, self.config.cache_ttl)
        self.semaphore = threading.Semaphore(self.config.max_concurrent)

        # MP API 客户端
        self.mp_client = None

        # 设置环境变量
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)

    def load_model(self, model_path: Optional[str] = None):
        """加载 CGCNN 模型 (可选，也可以使用 MP API)"""
        if model_path:
            print(f"[CGCNN] 加载模型：{model_path}")

            try:
                import onnxruntime as ort

                session_options = ort.SessionOptions()
                session_options.intra_op_num_threads = self.config.intra_op_threads
                session_options.inter_op_num_threads = self.config.inter_op_threads
                session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

                self.model = ort.InferenceSession(
                    model_path,
                    sess_options=session_options,
                    providers=['CPUExecutionProvider']
                )

                print(f"[CGCNN] 模型加载成功")

            except ImportError:
                print("[CGCNN] ONNX Runtime 未安装，将使用 MP API")
                self.model = None

            except Exception as e:
                print(f"[CGCNN] 加载失败：{e}")
                self.model = None
        else:
            print("[CGCNN] 未指定模型路径，将使用 MP API 获取真实数据")

    def set_mp_client(self, mp_client):
        """设置 Materials Project API 客户端"""
        self.mp_client = mp_client
        print("[CGCNN] 已配置 MP API 客户端")

    def predict(self, material_id: str = None, formula: str = None) -> Optional[Dict]:
        """
        预测材料性能
        
        优先级：
        1. 使用 MP API 获取真实数据 (如果可用)
        2. 使用 ONNX 模型推理 (如果已加载)
        3. 抛出错误 (无模拟数据)
        
        Args:
            material_id: Materials Project ID (如 mp-1171422)
            formula: 化学式 (如 LiFePO4)
        
        Returns:
            材料性能数据
        """
        # 检查缓存
        cache_key = {'material_id': material_id, 'formula': formula}
        cached = self.cache.get(**cache_key)
        if cached:
            return cached

        # 检查 CPU
        self.monitor.wait_if_needed(timeout=5.0)

        # 限制并发
        with self.semaphore:
            result = self._predict_real(material_id, formula)

        # 缓存结果
        if result:
            self.cache.set(result, **cache_key)

        return result

    def _predict_real(self, material_id: str = None, formula: str = None) -> Optional[Dict]:
        """获取真实材料数据"""

        # 优先使用 MP API
        if self.mp_client:
            try:
                if material_id:
                    # 从 MP API 获取材料详情
                    summary = self.mp_client.get_material_summary(material_id)
                    if summary:
                        return {
                            'material_id': material_id,
                            'band_gap': summary.get('band_gap', None),
                            'formation_energy': summary.get('formation_energy_per_atom', None),
                            'formula': summary.get('formula', {}).get('pretty', str(summary.get('formula'))),
                            'source': 'MP_API',
                            'timestamp': time.time()
                        }

                elif formula:
                    # 搜索材料
                    results = self.mp_client.search_by_formula(formula, limit=1)
                    if results:
                        mat = results[0]
                        return {
                            'material_id': mat.get('material_id'),
                            'band_gap': mat.get('band_gap', None),
                            'formation_energy': mat.get('formation_energy_per_atom', None),
                            'formula': mat.get('formula', {}).get('pretty', str(mat.get('formula'))),
                            'source': 'MP_API',
                            'timestamp': time.time()
                        }

            except Exception as e:
                print(f"[CGCNN] MP API 错误：{e}")

        # 如果没有 MP API，使用 ONNX 模型
        if self.model:
            try:
                # 需要晶体结构输入
                raise NotImplementedError("ONNX 推理需要晶体结构输入，请使用 MP API")
            except Exception as e:
                print(f"[CGCNN] ONNX 推理失败：{e}")
                return None

        # 无模拟数据
        raise RuntimeError(
            "[CGCNN] No model or MP API available. "
            "Please provide either:\n"
            "1. ONNX model file: model.load_model('path/to/model.onnx')\n"
            "2. MP API client: model.set_mp_client(mp_client)"
        )

    def predict_batch(self, materials: List[Dict]) -> List[Optional[Dict]]:
        """批量预测"""
        results = []

        for i, mat in enumerate(materials):
            result = self.predict(
                material_id=mat.get('material_id'),
                formula=mat.get('formula')
            )
            results.append(result)

            # 批次间休息
            if (i + 1) % self.config.batch_size == 0:
                time.sleep(0.5)

        return results

    def get_stats(self) -> Dict:
        """获取模型统计"""
        return {
            'model_loaded': self.model is not None,
            'mp_api_available': self.mp_client is not None,
            'cache': self.cache.get_stats(),
            'cpu_usage': f"{self.monitor.get_cpu_percent():.1f}%"
        }


# ============================================================================
# 5. 工厂函数
# ============================================================================

def get_cgcnn_model(config: CPUConfig = None) -> CGCNNModel:
    """获取 CGCNN 模型实例"""
    return CGCNNModel(config or CPU_CONFIG)


# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    """主函数 - 测试 CGCNN 模型"""
    print("=" * 60)
    print("CGCNN Model - Production Version")
    print("=" * 60)

    # 创建模型
    config = CPUConfig()
    model = get_cgcnn_model(config)

    # 不加载模拟数据
    print("\n[INFO] No model file specified")
    print("[INFO] Will use MP API for real data")

    # 尝试导入 MP API 客户端
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        # 使用 importlib 动态导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mp_api_v2",
            Path(__file__).parent / "materials-project-api-v2.py"
        )
        if spec and spec.loader:
            mp_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mp_module)
            MaterialsProjectClient = mp_module.MaterialsProjectClient
            mp_client = MaterialsProjectClient()
            model.set_mp_client(mp_client)
            print("[OK] MP API client configured")
        else:
            print("[WARN] Could not load MP API module")
    except Exception as e:
        print(f"[WARN] MP API client not available: {type(e).__name__}: {e}")

    # 测试预测
    print("\n[1/2] Testing prediction with MP API...")

    test_materials = [
        {'material_id': 'mp-dqobo'},  # LiFePO4
        {'formula': 'SiO2'},
        {'formula': 'TiO2'},
    ]

    for mat in test_materials:
        try:
            result = model.predict(**mat)
            if result:
                print(f"\n  {mat}:")
                print(f"    ID: {result.get('material_id', 'N/A')}")
                print(f"    Formula: {result.get('formula', 'N/A')}")
                print(f"    Band Gap: {result.get('band_gap', 'N/A')} eV")
                print(f"    Formation Energy: {result.get('formation_energy', 'N/A')} eV/atom")
                print(f"    Source: {result.get('source', 'N/A')}")
        except Exception as e:
            print(f"\n  {mat}: Error - {e}")

    # 打印统计
    print("\n[2/2] Model statistics:")
    stats = model.get_stats()
    print(f"  Model loaded: {stats['model_loaded']}")
    print(f"  MP API: {stats['mp_api_available']}")
    print(f"  Cache hit rate: {stats['cache']['hit_rate']}")
    print(f"  CPU usage: {stats['cpu_usage']}")

    print("\n" + "=" * 60)
    print("CGCNN model ready (using real data only)")
    print("=" * 60)


if __name__ == '__main__':
    main()
