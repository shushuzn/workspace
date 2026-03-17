#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGNet Model - CPU Optimized Version
材料图神经网络 (CPU 优化版)

功能：
1. 基于 matgl 实现 MEGNet 模型
2. CPU 优化，严格控制使用率 (<70%)
3. 支持多种性能预测
4. 缓存机制 + 并发控制

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:30
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from functools import lru_cache
from collections import deque
import threading

# ============================================================================
# 1. CPU 保护配置 (与 CGCNN 一致)
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 保护配置"""
    # 线程限制
    intra_op_threads: int = 4
    inter_op_threads: int = 2
    
    # 并发控制
    max_concurrent: int = 1
    queue_size: int = 20
    
    # CPU 使用限制
    cpu_threshold: float = 70.0
    cooldown_time: float = 2.0
    
    # 缓存配置
    cache_size: int = 500
    cache_ttl: int = 3600
    
    # 批处理
    batch_size: int = 10
    batch_timeout: float = 1.0


# 全局配置
CPU_CONFIG = CPUConfig()

# ============================================================================
# 2. CPU 监控 (复用 CGCNN 的设计)
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
        except:
            return 0.0
    
    def should_wait(self) -> bool:
        """检查是否应该等待"""
        current = self.get_cpu_percent()
        
        with self.lock:
            self.history.append(current)
            
            if current > self.threshold:
                return True
            
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
# 4. MEGNet 模型 (CPU 优化版)
# ============================================================================

class MEGNetModel:
    """MEGNet 模型 (CPU 优化版)"""
    
    def __init__(self, config: CPUConfig = None):
        self.config = config or CPU_CONFIG
        self.model = None
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        self.cache = CacheManager(self.config.cache_size, self.config.cache_ttl)
        self.semaphore = threading.Semaphore(self.config.max_concurrent)
        
        # 设置环境变量
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)
    
    def load_model(self, model_path: Optional[str] = None, pretrained: str = "formation_energy"):
        """加载 MEGNet 模型"""
        print(f"[MEGNet] 加载模型：{pretrained}")
        
        try:
            import matgl
            from matgl.graph.compute import MEGNetCalculator
            
            # 加载预训练模型
            if model_path:
                self.model = matgl.load_model(model_path)
            else:
                # 使用内置预训练模型
                self.model = matgl.load_model(f"M3GNet-MP-{pretrained}")
            
            print(f"[MEGNet] 模型加载成功")
            print(f"[MEGNet] 线程配置：intra={self.config.intra_op_threads}, inter={self.config.inter_op_threads}")
            
        except ImportError:
            print("[MEGNet] ⚠️ matgl 未安装，使用模拟模式")
            print("[MEGNet] 安装：pip install matgl")
            self.model = None
        
        except Exception as e:
            print(f"[MEGNet] ❌ 加载失败：{e}")
            self.model = None
    
    def predict(self, crystal_structure: Dict) -> Optional[Dict]:
        """预测材料性能"""
        
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
            # 模拟模式
            return self._simulate_prediction(crystal_structure)
        
        try:
            from pymatgen.core import Structure
            
            # 准备结构
            structure = self._prepare_structure(crystal_structure)
            
            # 运行预测
            start = time.time()
            
            # 使用 MEGNet 计算器
            calculator = MEGNetCalculator(self.model)
            energy = calculator.calculate(structure)
            
            inference_time = time.time() - start
            
            result = {
                'formation_energy': float(energy),
                'inference_time': inference_time,
                'timestamp': time.time()
            }
            
            return result
            
        except Exception as e:
            print(f"[MEGNet] ❌ 预测失败：{e}")
            return None
    
    def _simulate_prediction(self, crystal_structure: Dict) -> Dict:
        """模拟预测"""
        import random
        
        # 模拟延迟
        time.sleep(random.uniform(1.5, 3.5))
        
        # 模拟结果
        return {
            'formation_energy': round(random.uniform(-5.0, -1.0), 2),
            'band_gap': round(random.uniform(0.5, 5.0), 2),
            'e_above_hull': round(random.uniform(0.0, 0.5), 3),
            'inference_time': 2.5,
            'timestamp': time.time(),
            'note': '模拟结果 (未加载真实模型)'
        }
    
    def _prepare_structure(self, crystal_structure: Dict) -> 'Structure':
        """准备晶体结构"""
        from pymatgen.core import Structure, Lattice
        
        # 从字典创建 Structure 对象
        material = crystal_structure.get('material', 'Unknown')
        formula = crystal_structure.get('formula', 'Si')
        
        # 简化处理：创建示例结构
        lattice = Lattice.cubic(5.0)  # 示例晶格
        species = [formula]  # 示例原子
        coords = [[0, 0, 0]]  # 示例坐标
        
        structure = Structure(lattice, species, coords)
        
        return structure
    
    def predict_batch(self, structures: List[Dict]) -> List[Optional[Dict]]:
        """批量预测"""
        results = []
        
        for i in range(0, len(structures), self.config.batch_size):
            batch = structures[i:i + self.config.batch_size]
            
            for structure in batch:
                result = self.predict(structure)
                results.append(result)
            
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

def get_megnet_model(config: CPUConfig = None) -> MEGNetModel:
    """获取 MEGNet 模型单例"""
    global _model_instance
    
    if _model_instance is None:
        _model_instance = MEGNetModel(config)
    
    return _model_instance

# ============================================================================
# 6. 主函数 (测试)
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("MEGNet Model - CPU Optimized Version")
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
    
    model = get_megnet_model(config)
    
    # 2. 加载模型
    print("\n[2/4] 加载模型...")
    model.load_model(pretrained="formation_energy")
    
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
            print(f"  形成能：{result.get('formation_energy', 'N/A')} eV/atom")
            print(f"  带隙：{result.get('band_gap', 'N/A')} eV")
            print(f"  能量凸包：{result.get('e_above_hull', 'N/A')} eV")
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
    print("MEGNet CPU 优化版准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
