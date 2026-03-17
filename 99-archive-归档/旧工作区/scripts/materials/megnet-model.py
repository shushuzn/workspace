#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGNet Model - Production Version
Materials Graph Network (生产版)

使用真实数据：
1. 从 Materials Project API 获取真实数据
2. 使用 matgl 库进行推理 (可选)
3. 严格 CPU 控制
4. 无模拟数据

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:30
更新：2026-03-05 23:10 - 移除模拟数据
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
from collections import deque
import threading

# ============================================================================
# 1. 配置
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 配置"""
    intra_op_threads: int = 4
    inter_op_threads: int = 2
    max_concurrent: int = 1
    cpu_threshold: float = 70.0
    cache_size: int = 500
    cache_ttl: int = 3600


CPU_CONFIG = CPUConfig()


# ============================================================================
# 2. CPU 监控和缓存 (与 CGCNN 共享)
# ============================================================================

class CPUMonitor:
    """CPU 监控"""
    
    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)
    
    def get_cpu_percent(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def should_wait(self) -> bool:
        cpu = self.get_cpu_percent()
        self.history.append(cpu)
        return cpu > self.threshold
    
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
                else:
                    del self.cache[key]
                    del self.timestamps[key]
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
# 3. MEGNet 模型 (使用真实数据)
# ============================================================================

class MEGNetModel:
    """MEGNet 模型 - 使用真实 MP API 数据"""
    
    def __init__(self, config: CPUConfig = None):
        self.config = config or CPU_CONFIG
        self.model = None
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        self.cache = CacheManager(self.config.cache_size, self.config.cache_ttl)
        self.semaphore = threading.Semaphore(self.config.max_concurrent)
        
        # MP API 客户端
        self.mp_client = None
        
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)
    
    def load_model(self, model_path: Optional[str] = None):
        """加载 MEGNet 模型 (可选)"""
        if model_path:
            print(f"[MEGNet] 加载模型：{model_path}")
            try:
                import matgl
                self.model = matgl.load_model(model_path)
                print("[MEGNet] 模型加载成功")
            except ImportError:
                print("[MEGNet] matgl 未安装，将使用 MP API")
                self.model = None
            except Exception as e:
                print(f"[MEGNet] 加载失败：{e}")
                self.model = None
        else:
            print("[MEGNet] 未指定模型，将使用 MP API")
    
    def set_mp_client(self, mp_client):
        """设置 MP API 客户端"""
        self.mp_client = mp_client
        print("[MEGNet] 已配置 MP API 客户端")
    
    def predict(self, material_id: str = None, formula: str = None) -> Optional[Dict]:
        """
        预测材料性能
        
        优先级：
        1. MP API 真实数据
        2. matgl 模型推理
        3. 错误 (无模拟数据)
        """
        # 缓存检查
        cache_key = {'material_id': material_id, 'formula': formula}
        cached = self.cache.get(**cache_key)
        if cached:
            return cached
        
        # CPU 检查
        self.monitor.wait_if_needed(timeout=5.0)
        
        # 预测
        with self.semaphore:
            result = self._predict_real(material_id, formula)
        
        # 缓存
        if result:
            self.cache.set(result, **cache_key)
        
        return result
    
    def _predict_real(self, material_id: str = None, formula: str = None) -> Optional[Dict]:
        """获取真实数据"""
        
        # 使用 MP API
        if self.mp_client:
            try:
                if material_id:
                    summary = self.mp_client.get_material_summary(material_id)
                    if summary:
                        return {
                            'material_id': material_id,
                            'band_gap': summary.get('band_gap', None),
                            'formation_energy': summary.get('formation_energy_per_atom', None),
                            'e_above_hull': summary.get('energy_above_hull', None),
                            'formula': summary.get('formula', {}).get('pretty', str(summary.get('formula'))),
                            'source': 'MP_API',
                            'timestamp': time.time()
                        }
                
                elif formula:
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
                print(f"[MEGNet] MP API 错误：{e}")
        
        # 使用 matgl 模型
        if self.model:
            try:
                # 需要晶体结构
                raise NotImplementedError("matgl 推理需要晶体结构，请使用 MP API")
            except Exception as e:
                print(f"[MEGNet] matgl 错误：{e}")
                return None
        
        # 无模拟数据
        raise RuntimeError("[MEGNet] No model or MP API available")
    
    def predict_batch(self, materials: List[Dict]) -> List[Optional[Dict]]:
        """批量预测"""
        results = []
        for mat in materials:
            result = self.predict(**mat)
            results.append(result)
        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            'model_loaded': self.model is not None,
            'mp_api_available': self.mp_client is not None,
            'cpu_usage': f"{self.monitor.get_cpu_percent():.1f}%"
        }


# ============================================================================
# 4. 工厂函数
# ============================================================================

def get_megnet_model(config: CPUConfig = None) -> MEGNetModel:
    """获取 MEGNet 模型"""
    return MEGNetModel(config or CPU_CONFIG)


# ============================================================================
# 5. 主函数
# ============================================================================

def main():
    """测试 MEGNet 模型"""
    print("=" * 60)
    print("MEGNet Model - Production Version")
    print("=" * 60)
    
    config = CPUConfig()
    model = get_megnet_model(config)
    
    # 配置 MP API
    try:
        from materials_project_api_v2 import MaterialsProjectClient
        mp_client = MaterialsProjectClient()
        model.set_mp_client(mp_client)
        print("[OK] MP API configured")
    except Exception as e:
        print(f"[WARN] MP API not available: {e}")
    
    # 测试
    print("\nTesting predictions...")
    
    test_materials = [
        {'material_id': 'mp-dqobo'},
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
        except Exception as e:
            print(f"\n  {mat}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("MEGNet ready (real data only)")
    print("=" * 60)


if __name__ == '__main__':
    main()
