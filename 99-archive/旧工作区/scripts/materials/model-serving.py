#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Serving - Production Version
模型服务化模块 (生产版)

使用真实数据：
1. FastAPI RESTful 服务
2. 集成 MP API 获取真实数据
3. 多模型统一接口
4. 无模拟数据

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:55
更新：2026-03-05 23:20 - 移除模拟数据
"""

import os
import sys
import json
import time
import logging
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
from contextlib import asynccontextmanager
import threading

# FastAPI
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[Model Serving] FastAPI not installed")
    print("[Model Serving] Install: pip install fastapi uvicorn")

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('model-serving')


# ============================================================================
# 1. 数据模型
# ============================================================================

class MaterialInput(BaseModel):
    """材料输入"""
    material_id: Optional[str] = Field(None, description="MP 材料 ID")
    formula: Optional[str] = Field(None, description="化学式")
    material_name: Optional[str] = Field(None, description="材料名称")


class PropertyInput(BaseModel):
    """性能预测输入"""
    material: MaterialInput
    properties: List[str] = Field(default=['band_gap', 'formation_energy'])
    model: str = Field(default='mp_api', description="模型：mp_api/cgcnn/megnet")
    include_uncertainty: bool = Field(default=True)


class PredictionResult(BaseModel):
    """预测结果"""
    material_id: Optional[str]
    formula: Optional[str]
    predictions: Dict[str, Optional[float]]
    uncertainty: Optional[Dict] = None
    inference_time: float
    model: str
    source: str
    timestamp: float


class ServiceStats(BaseModel):
    """服务统计"""
    status: str
    models_loaded: List[str]
    mp_api_available: bool
    total_predictions: int
    cache_hit_rate: str


# ============================================================================
# 2. 模型管理器 (使用真实数据)
# ============================================================================

class ModelManager:
    """模型管理器 - 使用真实 MP API 数据"""

    def __init__(self):
        self.models = {}
        self.mp_client = None
        self.cache = {}
        self.total_predictions = 0
        self.cache_hits = 0

        logger.info("ModelManager initialized (real data only)")

    def load_mp_client(self):
        """加载 MP API 客户端"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "mp_api_v2",
                Path(__file__).parent / "materials-project-api-v2.py"
            )
            if spec and spec.loader:
                mp_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mp_module)
                self.mp_client = mp_module.MaterialsProjectClient()
                logger.info("MP API client loaded")
                return True
        except Exception as e:
            logger.error(f"Failed to load MP API: {e}")
        return False

    def load_model(self, model_name: str, model_path: Optional[str] = None):
        """加载模型 (可选)"""
        import importlib.util

        if model_name == 'cgcnn':
            try:
                spec = importlib.util.spec_from_file_location("cgcnn", Path(__file__).parent / "cgcnn-model.py")
                if spec and spec.loader:
                    cgcnn_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(cgcnn_module)
                    get_cgcnn_model = cgcnn_module.get_cgcnn_model
                    model = get_cgcnn_model()
                    if self.mp_client:
                        model.set_mp_client(self.mp_client)
                    if model_path:
                        model.load_model(model_path)
                    self.models['cgcnn'] = model
                    logger.info(f"CGCNN model loaded: {model_path or 'MP_API only'}")
            except Exception as e:
                logger.error(f"Failed to load CGCNN: {e}")

        elif model_name == 'megnet':
            try:
                spec = importlib.util.spec_from_file_location("megnet", Path(__file__).parent / "megnet-model.py")
                if spec and spec.loader:
                    megnet_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(megnet_module)
                    get_megnet_model = megnet_module.get_megnet_model
                    model = get_megnet_model()
                    if self.mp_client:
                        model.set_mp_client(self.mp_client)
                    if model_path:
                        model.load_model(model_path)
                    self.models['megnet'] = model
                    logger.info(f"MEGNet model loaded: {model_path or 'MP_API only'}")
            except Exception as e:
                logger.error(f"Failed to load MEGNet: {e}")

    def predict(self, input_data: PropertyInput) -> PredictionResult:
        """预测材料性能"""
        start_time = time.time()

        # 缓存检查
        cache_key = f"{input_data.material.material_id or input_data.material.formula}:{input_data.model}"
        if cache_key in self.cache:
            self.cache_hits += 1
            cached = self.cache[cache_key]
            cached['inference_time'] = time.time() - start_time
            return PredictionResult(**cached)

        # 使用 MP API (默认)
        if input_data.model == 'mp_api' and self.mp_client:
            try:
                mat = input_data.material

                if mat.material_id:
                    summary = self.mp_client.get_material_summary(mat.material_id)
                elif mat.formula:
                    results = self.mp_client.search_by_formula(mat.formula, limit=1)
                    summary = results[0] if results else None
                else:
                    raise HTTPException(status_code=400, detail="material_id or formula required")

                if summary:
                    predictions = {}
                    for prop in input_data.properties:
                        if prop == 'band_gap':
                            predictions[prop] = summary.get('band_gap')
                        elif prop == 'formation_energy':
                            predictions[prop] = summary.get('formation_energy_per_atom')
                        elif prop == 'e_above_hull':
                            predictions[prop] = summary.get('energy_above_hull')

                    result = {
                        'material_id': summary.get('material_id'),
                        'formula': summary.get('formula', {}).get('pretty', str(summary.get('formula'))),
                        'predictions': predictions,
                        'uncertainty': None,
                        'inference_time': time.time() - start_time,
                        'model': 'mp_api',
                        'source': 'MP_API',
                        'timestamp': time.time()
                    }

                    # 缓存
                    self.cache[cache_key] = result
                    self.total_predictions += 1

                    return PredictionResult(**result)

            except Exception as e:
                logger.error(f"MP API prediction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # 使用其他模型
        elif input_data.model in self.models:
            model = self.models[input_data.model]
            try:
                result = model.predict(
                    material_id=input_data.material.material_id,
                    formula=input_data.material.formula
                )

                if result:
                    prediction_result = PredictionResult(
                        material_id=result.get('material_id'),
                        formula=result.get('formula'),
                        predictions={'band_gap': result.get('band_gap'), 'formation_energy': result.get('formation_energy')},
                        uncertainty=None,
                        inference_time=time.time() - start_time,
                        model=input_data.model,
                        source=result.get('source', 'MODEL'),
                        timestamp=time.time()
                    )

                    self.cache[cache_key] = prediction_result.dict()
                    self.total_predictions += 1

                    return prediction_result

            except Exception as e:
                logger.error(f"Model prediction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        else:
            raise HTTPException(status_code=400, detail=f"Model {input_data.model} not available")

        raise HTTPException(status_code=500, detail="Prediction failed")

    def get_stats(self) -> ServiceStats:
        """获取服务统计"""
        cache_hit_rate = f"{(self.cache_hits / self.total_predictions * 100):.1f}%" if self.total_predictions > 0 else "0%"

        return ServiceStats(
            status="online" if self.mp_client else "degraded",
            models_loaded=list(self.models.keys()),
            mp_api_available=self.mp_client is not None,
            total_predictions=self.total_predictions,
            cache_hit_rate=cache_hit_rate,
        )


# ============================================================================
# 3. FastAPI 应用
# ============================================================================

def create_app() -> Optional[FastAPI]:
    """创建 FastAPI 应用"""
    if not FASTAPI_AVAILABLE:
        return None

    manager = ModelManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logger.info("Starting Model Serving Service...")
        manager.load_mp_client()
        # 可选加载模型文件
        # manager.load_model('cgcnn', 'models/cgcnn.onnx')
        yield
        # Shutdown
        logger.info("Shutting down Model Serving Service...")

    app = FastAPI(
        title="Materials Property Prediction Service",
        description="Predict material properties using real MP API data",
        version="1.0.0",
        lifespan=lifespan
    )

    @app.post("/predict", response_model=PredictionResult)
    async def predict(input_data: PropertyInput):
        """预测材料性能"""
        return manager.predict(input_data)

    @app.post("/predict/batch")
    async def predict_batch(inputs: List[PropertyInput]):
        """批量预测"""
        results = []
        for inp in inputs:
            try:
                result = manager.predict(inp)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        return {"total": len(inputs), "results": results}

    @app.get("/stats", response_model=ServiceStats)
    async def get_stats():
        """服务统计"""
        return manager.get_stats()

    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy" if manager.mp_client else "degraded",
            "mp_api": manager.mp_client is not None,
            "models": list(manager.models.keys())
        }

    return app


# ============================================================================
# 4. 主函数 (测试模式)
# ============================================================================

def main():
    """测试模型服务"""
    print("=" * 60)
    print("Model Serving - Production Version")
    print("=" * 60)

    manager = ModelManager()

    # 加载 MP API
    print("\nLoading MP API client...")
    if manager.load_mp_client():
        print("[OK] MP API loaded")
    else:
        print("[FAIL] MP API not available")
        return

    # 测试预测
    print("\nTesting predictions...")

    test_inputs = [
        PropertyInput(material=MaterialInput(material_id='mp-dqobo')),
        PropertyInput(material=MaterialInput(formula='SiO2')),
        PropertyInput(material=MaterialInput(formula='TiO2')),
    ]

    for inp in test_inputs:
        try:
            result = manager.predict(inp)
            print(f"\n  {inp.material.material_id or inp.material.formula}:")
            print(f"    Band Gap: {result.predictions.get('band_gap', 'N/A')} eV")
            print(f"    Formation Energy: {result.predictions.get('formation_energy', 'N/A')} eV/atom")
            print(f"    Source: {result.source}")
            print(f"    Time: {result.inference_time*1000:.1f}ms")
        except Exception as e:
            print(f"\n  {inp.material.material_id or inp.material.formula}: Error - {e}")

    # 统计
    print("\nService Statistics:")
    stats = manager.get_stats()
    print(f"  Status: {stats.status}")
    print(f"  MP API: {stats.mp_api_available}")
    print(f"  Predictions: {stats.total_predictions}")
    print(f"  Cache Hit Rate: {stats.cache_hit_rate}")

    print("\n" + "=" * 60)
    print("Model serving ready (real data only)")
    print("=" * 60)

    if FASTAPI_AVAILABLE:
        print("\nTo start API server:")
        print("  uvicorn model-serving:app --host 0.0.0.0 --port 8000")


if __name__ == '__main__':
    main()
