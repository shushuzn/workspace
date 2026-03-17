#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uncertainty Quantification - Production Version
不确定性量化模块 (生产版)

使用真实数据：
1. 基于 MP API 真实数据的不确定性估计
2. 使用数据分布计算置信度
3. 无模拟数据

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:40
更新：2026-03-05 23:15 - 移除模拟数据
"""

import os
import json
import time
import hashlib
import math
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque
import threading
import statistics


# ============================================================================
# 1. 配置
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 配置"""
    intra_op_threads: int = 4
    max_concurrent: int = 1
    cpu_threshold: float = 70.0
    cache_size: int = 500


# ============================================================================
# 2. CPU 监控 + 缓存
# ============================================================================

class CPUMonitor:
    """CPU 监控"""
    
    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)
        self.lock = threading.Lock()
    
    def get_cpu_percent(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def should_wait(self) -> bool:
        current = self.get_cpu_percent()
        with self.lock:
            self.history.append(current)
            return current > self.threshold
    
    def wait_if_needed(self, timeout: float = 5.0):
        start = time.time()
        while self.should_wait():
            if time.time() - start > timeout:
                break
            time.sleep(0.5)


class CacheManager:
    """缓存管理"""
    
    def __init__(self, max_size: int = 500, ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def _generate_key(self, **kwargs) -> str:
        content = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, **kwargs) -> Optional[Dict]:
        key = self._generate_key(**kwargs)
        with self.lock:
            if key in self.cache:
                age = time.time() - self.timestamps.get(key, 0)
                if age < self.ttl:
                    return self.cache[key]
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


# ============================================================================
# 3. 不确定性量化 (使用真实数据)
# ============================================================================

class UncertaintyQuantifier:
    """不确定性量化 - 基于真实 MP 数据"""
    
    def __init__(self, config: CPUConfig = None):
        self.config = config or CPUConfig()
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        self.cache = CacheManager(self.config.cache_size)
        
        # MP API 客户端
        self.mp_client = None
        
        # 参考数据 (从 MP API 获取)
        self.reference_data = {}
    
    def set_mp_client(self, mp_client):
        """设置 MP API 客户端"""
        self.mp_client = mp_client
        print("[UQ] 已配置 MP API 客户端")
        self._load_reference_data()
    
    def _load_reference_data(self):
        """从 MP API 加载参考数据用于不确定性估计"""
        if not self.mp_client:
            return
        
        print("[UQ] 加载参考数据...")
        
        # 获取一些常见材料的性能分布
        common_formulas = ['SiO2', 'TiO2', 'LiFePO4', 'LiCoO2', 'Al2O3']
        
        for formula in common_formulas:
            try:
                results = self.mp_client.search_by_formula(formula, limit=10)
                if results:
                    band_gaps = [r.get('band_gap') for r in results if r.get('band_gap') is not None]
                    formation_energies = [r.get('formation_energy_per_atom') for r in results if r.get('formation_energy_per_atom') is not None]
                    
                    self.reference_data[formula] = {
                        'band_gap': {
                            'mean': statistics.mean(band_gaps) if band_gaps else None,
                            'stdev': statistics.stdev(band_gaps) if len(band_gaps) > 1 else None,
                            'min': min(band_gaps) if band_gaps else None,
                            'max': max(band_gaps) if band_gaps else None,
                            'count': len(band_gaps)
                        },
                        'formation_energy': {
                            'mean': statistics.mean(formation_energies) if formation_energies else None,
                            'stdev': statistics.stdev(formation_energies) if len(formation_energies) > 1 else None,
                            'min': min(formation_energies) if formation_energies else None,
                            'max': max(formation_energies) if formation_energies else None,
                            'count': len(formation_energies)
                        }
                    }
            except Exception as e:
                print(f"[UQ] 加载 {formula} 参考数据失败：{e}")
        
        print(f"[UQ] 已加载 {len(self.reference_data)} 个材料的参考数据")
    
    def quantify(self, material_id: str = None, formula: str = None,
                 predicted_value: float = None, property_name: str = 'band_gap') -> Dict:
        """
        量化预测的不确定性
        
        Args:
            material_id: MP 材料 ID
            formula: 化学式
            predicted_value: 预测值
            property_name: 性能名称 ('band_gap', 'formation_energy')
        
        Returns:
            不确定性量化结果
        """
        # 缓存检查
        cache_key = {'material_id': material_id, 'formula': formula, 'property': property_name}
        cached = self.cache.get(**cache_key)
        if cached:
            return cached
        
        # CPU 检查
        self.monitor.wait_if_needed(timeout=5.0)
        
        # 量化不确定性
        result = self._quantify_real(material_id, formula, predicted_value, property_name)
        
        # 缓存
        if result:
            self.cache.set(result, **cache_key)
        
        return result
    
    def _quantify_real(self, material_id: str = None, formula: str = None,
                       predicted_value: float = None, property_name: str = 'band_gap') -> Dict:
        """基于真实数据量化不确定性"""
        
        # 从 MP API 获取真实值
        true_value = None
        if self.mp_client:
            try:
                if material_id:
                    summary = self.mp_client.get_material_summary(material_id)
                elif formula:
                    results = self.mp_client.search_by_formula(formula, limit=1)
                    summary = results[0] if results else None
                else:
                    summary = None
                
                if summary:
                    if property_name == 'band_gap':
                        true_value = summary.get('band_gap')
                    elif property_name == 'formation_energy':
                        true_value = summary.get('formation_energy_per_atom')
            except Exception as e:
                print(f"[UQ] 获取真实值失败：{e}")
        
        # 计算不确定性
        result = {
            'material_id': material_id,
            'formula': formula,
            'property': property_name,
            'predicted_value': predicted_value,
            'true_value': true_value,
            'uncertainty': None,
            'confidence': None,
            'confidence_interval_95': None,
            'source': 'MP_API',
            'timestamp': time.time()
        }
        
        # 如果有预测值和真实值，计算误差
        if predicted_value is not None and true_value is not None:
            error = abs(predicted_value - true_value)
            result['error'] = error
            result['relative_error'] = error / abs(true_value) if true_value != 0 else None
            
            # 简单置信度 (基于相对误差)
            relative_error = result['relative_error']
            if relative_error is not None:
                # 相对误差越小，置信度越高
                result['confidence'] = max(0.0, 1.0 - relative_error)
        
        # 使用参考数据估计不确定性
        if formula and formula in self.reference_data:
            ref = self.reference_data[formula].get(property_name, {})
            if ref.get('stdev'):
                result['uncertainty'] = ref['stdev']
                result['confidence_interval_95'] = [
                    ref['mean'] - 1.96 * ref['stdev'],
                    ref['mean'] + 1.96 * ref['stdev']
                ]
        
        return result
    
    def quantify_batch(self, materials: List[Dict], 
                       property_name: str = 'band_gap') -> List[Dict]:
        """批量不确定性量化"""
        results = []
        for mat in materials:
            result = self.quantify(
                material_id=mat.get('material_id'),
                formula=mat.get('formula'),
                predicted_value=mat.get('predicted_value'),
                property_name=property_name
            )
            results.append(result)
        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            'mp_api_available': self.mp_client is not None,
            'reference_materials': len(self.reference_data),
            'cache_size': len(self.cache.cache)
        }


# ============================================================================
# 4. 工厂函数
# ============================================================================

def get_uncertainty_quantifier(config: CPUConfig = None) -> UncertaintyQuantifier:
    """工厂函数"""
    return UncertaintyQuantifier(config or CPUConfig())


# ============================================================================
# 5. 主函数
# ============================================================================

def main():
    """测试"""
    print("=" * 60)
    print("Uncertainty Quantification - Production")
    print("=" * 60)
    
    config = CPUConfig()
    quantifier = get_uncertainty_quantifier(config)
    
    # 配置 MP API
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mp_api_v2",
            Path(__file__).parent / "materials-project-api-v2.py"
        )
        if spec and spec.loader:
            mp_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mp_module)
            mp_client = mp_module.MaterialsProjectClient()
            quantifier.set_mp_client(mp_client)
    except Exception as e:
        print(f"[WARN] MP API not available: {e}")
    
    # 测试
    print("\nQuantifying uncertainty...")
    
    test_cases = [
        {'formula': 'SiO2', 'predicted_value': 5.5, 'property': 'band_gap'},
        {'formula': 'TiO2', 'predicted_value': 2.8, 'property': 'band_gap'},
        {'formula': 'LiFePO4', 'predicted_value': 3.5, 'property': 'band_gap'},
    ]
    
    for case in test_cases:
        result = quantifier.quantify(
            formula=case['formula'],
            predicted_value=case['predicted_value'],
            property_name=case['property']
        )
        
        print(f"\n  {case['formula']} ({case['property']}):")
        print(f"    Predicted: {case['predicted_value']} eV")
        print(f"    True Value: {result.get('true_value', 'N/A')} eV")
        if result.get('error') is not None:
            print(f"    Error: {result['error']:.3f} eV ({result.get('relative_error', 0)*100:.1f}%)")
        print(f"    Confidence: {result.get('confidence', 'N/A'):.1%}" if result.get('confidence') else "    Confidence: N/A")
        print(f"    Uncertainty: ±{result.get('uncertainty', 'N/A'):.3f} eV" if result.get('uncertainty') else "    Uncertainty: N/A")
    
    print("\n" + "=" * 60)
    print("Uncertainty quantifier ready (real data)")
    print("=" * 60)


if __name__ == '__main__':
    main()
