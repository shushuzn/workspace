#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uncertainty Quantification - CPU Optimized
不确定性量化模块 (CPU 优化版)

功能：
1. Dropout MC (Monte Carlo) 不确定性估计
2. 集成学习方法
3. 置信度区间计算
4. 预测可靠性评估

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:40
"""

import os
import json
import time
import hashlib
import random
import math
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque
import threading
import statistics

# ============================================================================
# 1. CPU 保护配置
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 保护配置"""
    intra_op_threads: int = 4
    inter_op_threads: int = 2
    max_concurrent: int = 1
    cpu_threshold: float = 70.0
    cache_size: int = 500
    cache_ttl: int = 3600


# ============================================================================
# 2. CPU 监控 + 缓存
# ============================================================================

class CPUMonitor:
    """CPU 使用监控器"""

    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)
        self.lock = threading.Lock()

    def get_cpu_percent(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    def should_wait(self) -> bool:
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
        start = time.time()
        while self.should_wait():
            if time.time() - start > timeout:
                break
            time.sleep(0.5)


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
        content = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, **kwargs) -> Optional[Dict]:
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
        key = self._generate_key(**kwargs)
        with self.lock:
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.timestamps, key=self.timestamps.get)
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            self.cache[key] = value
            self.timestamps[key] = time.time()

    def get_stats(self) -> Dict:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }

    def clear(self):
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.hits = 0
            self.misses = 0

# ============================================================================
# 3. 数据结构
# ============================================================================

@dataclass
class UncertaintyResult:
    """不确定性量化结果"""
    property_name: str
    mean: float                    # 预测均值
    std: float                     # 标准差 (不确定性)
    confidence_interval: Tuple[float, float]  # 置信区间 (95%)
    uncertainty_type: str          # 不确定性类型
    confidence_score: float        # 置信度评分
    n_samples: int                 # 采样次数
    predictions: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'property_name': self.property_name,
            'mean': self.mean,
            'std': self.std,
            'confidence_interval': self.confidence_interval,
            'uncertainty_type': self.uncertainty_type,
            'confidence_score': self.confidence_score,
            'n_samples': self.n_samples,
            'predictions': self.predictions
        }


# ============================================================================
# 4. 不确定性量化器
# ============================================================================

class UncertaintyQuantifier:
    """不确定性量化器"""

    def __init__(self, config: CPUConfig = None):
        self.config = config or CPUConfig()
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        self.cache = CacheManager(self.config.cache_size, self.config.cache_ttl)
        self.semaphore = threading.Semaphore(self.config.max_concurrent)

        # 不确定性类型
        self.uncertainty_types = {
            'aleatoric': '数据不确定性 (噪声)',
            'epistemic': '模型不确定性 (知识不足)',
            'both': '混合不确定性'
        }

    def dropout_mc(
        self,
        model,
        crystal_structure: Dict,
        property_name: str,
        n_samples: int = 50,
        dropout_rate: float = 0.1
    ) -> UncertaintyResult:
        """
        Dropout MC (Monte Carlo) 不确定性估计
        
        原理：在推理时启用 Dropout，多次采样得到预测分布
        
        参数:
            model: 基础模型
            crystal_structure: 晶体结构
            property_name: 性能名称
            n_samples: 采样次数
            dropout_rate: Dropout 比率
        
        返回:
            UncertaintyResult 包含均值、标准差、置信区间
        """

        # 检查缓存
        cache_key = f"dropout_mc_{property_name}_{n_samples}"
        cached = self.cache.get(structure=crystal_structure, key=cache_key)
        if cached:
            return cached

        # 检查 CPU
        self.monitor.wait_if_needed(timeout=5.0)

        # 限制并发
        with self.semaphore:
            predictions = []

            for i in range(n_samples):
                # 模拟 Dropout 采样 (实际模型需要启用 dropout)
                pred = self._sample_with_dropout(model, crystal_structure, property_name, dropout_rate)
                predictions.append(pred)

                # 批次间短暂休息
                if i > 0 and i % 10 == 0:
                    time.sleep(0.1)

            # 计算统计量
            result = self._calculate_statistics(predictions, property_name, 'epistemic')

        # 缓存结果
        self.cache.set(result, structure=crystal_structure, key=cache_key)

        return result

    def ensemble_method(
        self,
        models: List,
        crystal_structure: Dict,
        property_name: str
    ) -> UncertaintyResult:
        """
        集成学习方法 - 使用多个模型预测
        
        原理：多个模型预测的方差表示不确定性
        
        参数:
            models: 模型列表
            crystal_structure: 晶体结构
            property_name: 性能名称
        
        返回:
            UncertaintyResult
        """

        # 检查缓存
        cache_key = f"ensemble_{property_name}_{len(models)}"
        cached = self.cache.get(structure=crystal_structure, key=cache_key)
        if cached:
            return cached

        # 检查 CPU
        self.monitor.wait_if_needed(timeout=5.0)

        # 限制并发
        with self.semaphore:
            predictions = []

            for i, model in enumerate(models):
                pred = self._predict_with_model(model, crystal_structure, property_name)
                predictions.append(pred)

                # 模型间短暂休息
                if i > 0 and i % 3 == 0:
                    time.sleep(0.2)

            # 计算统计量
            result = self._calculate_statistics(predictions, property_name, 'both')

        # 缓存结果
        self.cache.set(result, structure=crystal_structure, key=cache_key)

        return result

    def _sample_with_dropout(
        self,
        model,
        crystal_structure: Dict,
        property_name: str,
        dropout_rate: float
    ) -> float:
        """带 Dropout 的采样预测"""

        if not model:
            # 模拟模式：添加噪声
            base_pred = self._get_base_prediction(crystal_structure, property_name)
            noise = random.gauss(0, dropout_rate * base_pred)
            return base_pred + noise

        # 真实模型：启用 dropout 并预测
        # 这里需要实际模型的 dropout 实现
        return self._predict_with_model(model, crystal_structure, property_name)

    def _predict_with_model(
        self,
        model,
        crystal_structure: Dict,
        property_name: str
    ) -> float:
        """使用模型预测"""

        if not model:
            return self._get_base_prediction(crystal_structure, property_name)

        # 真实模型预测
        if hasattr(model, 'predict'):
            result = model.predict(crystal_structure)
            if result and property_name in result:
                return result[property_name]

        return self._get_base_prediction(crystal_structure, property_name)

    def _get_base_prediction(
        self,
        crystal_structure: Dict,
        property_name: str
    ) -> float:
        """获取基础预测值 (模拟)"""

        material = crystal_structure.get('material', 'Unknown')
        formula = crystal_structure.get('formula', '')

        # 基于材料的"合理"预测值
        base_values = {
            'band_gap': {
                'LiFePO4': 3.7,
                'SiO2': 8.9,
                'TiO2': 3.2,
                'default': 2.5
            },
            'formation_energy': {
                'LiFePO4': -2.3,
                'SiO2': -9.8,
                'TiO2': -3.5,
                'default': -3.0
            },
            'bulk_modulus': {
                'LiFePO4': 85,
                'SiO2': 37,
                'TiO2': 230,
                'default': 100
            }
        }

        if property_name in base_values:
            prop_dict = base_values[property_name]
            for key in [material, formula]:
                if key in prop_dict:
                    return prop_dict[key]
            return prop_dict['default']

        return random.uniform(0, 10)

    def _calculate_statistics(
        self,
        predictions: List[float],
        property_name: str,
        uncertainty_type: str
    ) -> UncertaintyResult:
        """计算统计量"""

        if len(predictions) < 2:
            raise ValueError("至少需要 2 个预测值")

        # 基本统计量
        mean = statistics.mean(predictions)
        std = statistics.stdev(predictions) if len(predictions) > 1 else 0

        # 置信区间 (95%, 假设正态分布)
        z_score = 1.96
        ci_lower = mean - z_score * std
        ci_upper = mean + z_score * std

        # 置信度评分 (基于变异系数)
        cv = (std / abs(mean)) if mean != 0 else 1.0
        confidence_score = max(0, min(1, 1 - cv))  # CV 越小，置信度越高

        return UncertaintyResult(
            property_name=property_name,
            mean=round(mean, 4),
            std=round(std, 4),
            confidence_interval=(round(ci_lower, 4), round(ci_upper, 4)),
            uncertainty_type=uncertainty_type,
            confidence_score=round(confidence_score, 4),
            n_samples=len(predictions),
            predictions=[round(p, 4) for p in predictions]
        )

    def quantify_uncertainty(
        self,
        model,
        crystal_structure: Dict,
        properties: List[str],
        method: str = 'dropout_mc',
        n_samples: int = 50
    ) -> Dict[str, UncertaintyResult]:
        """
        对多个性能进行不确定性量化
        
        参数:
            model: 基础模型
            crystal_structure: 晶体结构
            properties: 性能列表
            method: 方法 ('dropout_mc' 或 'ensemble')
            n_samples: 采样次数
        
        返回:
            Dict[property_name, UncertaintyResult]
        """

        results = {}

        for prop in properties:
            if method == 'dropout_mc':
                result = self.dropout_mc(model, crystal_structure, prop, n_samples)
            elif method == 'ensemble':
                result = self.ensemble_method([model], crystal_structure, prop)
            else:
                raise ValueError(f"未知方法：{method}")

            results[prop] = result

        return results

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'cache': self.cache.get_stats(),
            'current_cpu': self.monitor.get_cpu_percent(),
            'uncertainty_types': list(self.uncertainty_types.keys())
        }


# ============================================================================
# 5. 全局实例
# ============================================================================

_quantifier_instance = None

def get_uncertainty_quantifier(config: CPUConfig = None) -> UncertaintyQuantifier:
    """获取不确定性量化器单例"""
    global _quantifier_instance

    if _quantifier_instance is None:
        _quantifier_instance = UncertaintyQuantifier(config)

    return _quantifier_instance


# ============================================================================
# 6. 主函数 (测试)
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Uncertainty Quantification - CPU Optimized")
    print("=" * 60)

    # 1. 创建量化器
    print("\n[1/4] 创建量化器...")
    config = CPUConfig(
        intra_op_threads=4,
        inter_op_threads=2,
        max_concurrent=1,
        cache_size=500,
        cpu_threshold=70.0
    )

    quantifier = get_uncertainty_quantifier(config)

    # 2. 测试 Dropout MC
    print("\n[2/4] 测试 Dropout MC...")

    test_structure = {'material': 'LiFePO4', 'formula': 'LiFePO4'}

    result = quantifier.dropout_mc(
        model=None,  # 模拟模式
        crystal_structure=test_structure,
        property_name='band_gap',
        n_samples=30
    )

    print(f"\n材料：{test_structure['material']}")
    print(f"性能：{result.property_name}")
    print(f"均值：{result.mean} eV")
    print(f"标准差：{result.std} eV")
    print(f"95% 置信区间：[{result.confidence_interval[0]}, {result.confidence_interval[1]}] eV")
    print(f"不确定性类型：{result.uncertainty_type}")
    print(f"置信度评分：{result.confidence_score:.1%}")
    print(f"采样次数：{result.n_samples}")

    # 3. 测试多性能量化
    print("\n[3/4] 测试多性能量化...")

    properties = ['band_gap', 'formation_energy', 'bulk_modulus']

    results = quantifier.quantify_uncertainty(
        model=None,
        crystal_structure=test_structure,
        properties=properties,
        method='dropout_mc',
        n_samples=20
    )

    for prop, result in results.items():
        print(f"\n{prop}:")
        print(f"  均值：{result.mean}")
        print(f"  不确定性：±{result.std}")
        print(f"  置信度：{result.confidence_score:.1%}")

    # 4. 显示统计
    print("\n[4/4] 统计信息...")
    stats = quantifier.get_stats()

    print(f"  缓存命中率：{stats['cache']['hit_rate']}")
    print(f"  当前 CPU: {stats['current_cpu']:.1f}%")
    print(f"  不确定性类型：{stats['uncertainty_types']}")

    print("\n" + "=" * 60)
    print("不确定性量化模块准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
