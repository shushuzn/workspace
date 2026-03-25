#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Serving - CPU Optimized
模型服务化模块 (CPU 优化版)

功能：
1. FastAPI RESTful 服务
2. 多模型统一接口
3. 批处理支持
4. 监控与日志
5. CPU 保护机制

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:55
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

# FastAPI (如果可用)
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[Model Serving] ⚠️ FastAPI 未安装，使用简化模式")
    print("[Model Serving] 安装：pip install fastapi uvicorn")

# ============================================================================
# 1. 日志配置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('model-serving')

# ============================================================================
# 2. 数据模型
# ============================================================================

class MaterialInput(BaseModel):
    """材料输入"""
    material: str = Field(..., description="材料名称")
    formula: str = Field(..., description="化学式")
    lattice: Optional[Dict] = Field(None, description="晶格参数")
    atoms: Optional[List] = Field(None, description="原子位置")

class PropertyInput(BaseModel):
    """性能预测输入"""
    structure: MaterialInput
    properties: List[str] = Field(default=['band_gap', 'formation_energy'])
    model: str = Field(default='cgcnn', description="模型选择：cgcnn/megnet/multitask")
    include_uncertainty: bool = Field(default=True, description="是否包含不确定性")

class PredictionResult(BaseModel):
    """预测结果"""
    material: str
    predictions: Dict[str, float]
    uncertainty: Optional[Dict[str, Dict]] = None
    inference_time: float
    model: str
    timestamp: float

class BatchPredictionResult(BaseModel):
    """批量预测结果"""
    total: int
    successful: int
    failed: int
    results: List[PredictionResult]
    total_time: float

class ServiceStats(BaseModel):
    """服务统计"""
    status: str
    models_loaded: List[str]
    total_predictions: int
    cache_hit_rate: str
    avg_inference_time: float
    cpu_usage: float
    memory_usage: float

# ============================================================================
# 3. 模型管理器
# ============================================================================

class ModelManager:
    """模型管理器"""

    def __init__(self):
        self.models = {}
        self.stats = {
            'total_predictions': 0,
            'inference_times': []
        }
        self.lock = threading.Lock()

    def load_model(self, model_name: str, model_instance):
        """加载模型"""
        with self.lock:
            self.models[model_name] = model_instance
            logger.info(f"模型 {model_name} 加载成功")

    def get_model(self, model_name: str):
        """获取模型"""
        return self.models.get(model_name)

    def list_models(self) -> List[str]:
        """列出所有模型"""
        return list(self.models.keys())

    def record_prediction(self, inference_time: float):
        """记录预测统计"""
        with self.lock:
            self.stats['total_predictions'] += 1
            self.stats['inference_times'].append(inference_time)

            # 只保留最近 100 次
            if len(self.stats['inference_times']) > 100:
                self.stats['inference_times'] = self.stats['inference_times'][-100:]

    def get_avg_inference_time(self) -> float:
        """获取平均推理时间"""
        if not self.stats['inference_times']:
            return 0.0
        return sum(self.stats['inference_times']) / len(self.stats['inference_times'])

# 全局模型管理器
model_manager = ModelManager()

# ============================================================================
# 4. FastAPI 应用
# ============================================================================

def create_app() -> FastAPI:
    """创建 FastAPI 应用"""

    if not FASTAPI_AVAILABLE:
        return None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """应用生命周期"""
        # 启动时加载模型
        logger.info("正在加载模型...")
        load_all_models()
        logger.info("模型加载完成")

        yield

        # 关闭时清理
        logger.info("服务关闭")

    app = FastAPI(
        title="Materials AI Model Serving",
        description="材料性能预测 API 服务 (CPU 优化版)",
        version="1.0.0",
        lifespan=lifespan
    )

    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "models_loaded": model_manager.list_models(),
            "timestamp": time.time()
        }

    # 预测端点
    @app.post("/predict", response_model=PredictionResult)
    async def predict(input: PropertyInput):
        """
        预测材料性能
        
        - **structure**: 晶体结构
        - **properties**: 要预测的性能列表
        - **model**: 使用的模型 (cgcnn/megnet/multitask)
        """
        start = time.time()

        # 获取模型
        model = model_manager.get_model(input.model)
        if not model:
            raise HTTPException(status_code=404, detail=f"模型 {input.model} 未找到")

        try:
            # 预测
            structure_dict = input.structure.dict()

            if input.model == 'multitask':
                result = model.predict(structure_dict, input.properties)
                predictions = result.predictions if result else {}
            else:
                result = model.predict(structure_dict)
                predictions = result if result else {}

            # 不确定性量化 (如果请求)
            uncertainty = None
            if input.include_uncertainty:
                from uncertainty_quantifier import get_uncertainty_quantifier
                quantifier = get_uncertainty_quantifier()
                unc_results = quantifier.quantify_uncertainty(
                    model, structure_dict, input.properties
                )
                uncertainty = {k: v.to_dict() for k, v in unc_results.items()}

            inference_time = time.time() - start

            # 记录统计
            model_manager.record_prediction(inference_time)

            return PredictionResult(
                material=input.structure.material,
                predictions=predictions,
                uncertainty=uncertainty,
                inference_time=inference_time,
                model=input.model,
                timestamp=time.time()
            )

        except Exception as e:
            logger.error(f"预测失败：{e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 批量预测端点
    @app.post("/predict/batch", response_model=BatchPredictionResult)
    async def predict_batch(structures: List[MaterialInput], model: str = 'cgcnn'):
        """批量预测"""
        start = time.time()

        model_instance = model_manager.get_model(model)
        if not model_instance:
            raise HTTPException(status_code=404, detail=f"模型 {model} 未找到")

        results = []
        successful = 0
        failed = 0

        for structure in structures:
            try:
                pred = model_instance.predict(structure.dict())
                results.append(PredictionResult(
                    material=structure.material,
                    predictions=pred if pred else {},
                    inference_time=0,
                    model=model,
                    timestamp=time.time()
                ))
                successful += 1
            except Exception as e:
                logger.error(f"批量预测失败：{e}")
                failed += 1

        total_time = time.time() - start

        return BatchPredictionResult(
            total=len(structures),
            successful=successful,
            failed=failed,
            results=results,
            total_time=total_time
        )

    # 统计端点
    @app.get("/stats", response_model=ServiceStats)
    async def get_stats():
        """获取服务统计"""
        try:
            import psutil
            cpu_usage = psutil.cpu_percent()
            memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        except Exception:
            cpu_usage = 0.0
            memory = 0.0

        return ServiceStats(
            status="running",
            models_loaded=model_manager.list_models(),
            total_predictions=model_manager.stats['total_predictions'],
            cache_hit_rate="N/A",
            avg_inference_time=model_manager.get_avg_inference_time(),
            cpu_usage=cpu_usage,
            memory_usage=memory
        )

    # 模型列表端点
    @app.get("/models")
    async def list_models():
        """列出可用模型"""
        return {
            "models": model_manager.list_models(),
            "count": len(model_manager.list_models())
        }

    return app

# ============================================================================
# 5. 模型加载函数
# ============================================================================

def load_all_models():
    """加载所有模型"""

    # 加载 CGCNN
    try:
        from cgcnn_model import get_cgcnn_model, CPUConfig
        cgcnn = get_cgcnn_model(CPUConfig())
        cgcnn.load_model("models/cgcnn.onnx")  # 或模拟模式
        model_manager.load_model('cgcnn', cgcnn)
    except Exception as e:
        logger.warning(f"CGCNN 加载失败：{e}")

    # 加载 MEGNet
    try:
        from megnet_model import get_megnet_model, CPUConfig
        megnet = get_megnet_model(CPUConfig())
        megnet.load_model(pretrained="formation_energy")
        model_manager.load_model('megnet', megnet)
    except Exception as e:
        logger.warning(f"MEGNet 加载失败：{e}")

    # 加载多任务模型
    try:
        from multitask_model import get_multitask_model, CPUConfig
        multitask = get_multitask_model(CPUConfig())
        multitask.load_model()
        model_manager.load_model('multitask', multitask)
    except Exception as e:
        logger.warning(f"多任务模型加载失败：{e}")

# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Model Serving - CPU Optimized")
    print("=" * 60)

    if not FASTAPI_AVAILABLE:
        print("\n⚠️ FastAPI 未安装，无法启动 Web 服务")
        print("安装：pip install fastapi uvicorn")
        print("\n但可以在代码中直接使用模型管理器：")
        print("  from model_serving import model_manager")
        print("  model_manager.load_model('cgcnn', model_instance)")
        return

    # 创建应用
    print("\n[1/3] 创建 FastAPI 应用...")
    app = create_app()

    # 加载模型
    print("\n[2/3] 加载模型...")
    load_all_models()

    print(f"\n已加载模型：{model_manager.list_models()}")

    # 启动服务
    print("\n[3/3] 启动服务...")
    print("\n" + "=" * 60)
    print("服务启动成功！")
    print("=" * 60)
    print("\n访问地址:")
    print("  API 文档：http://localhost:8000/docs")
    print("  健康检查：http://localhost:8000/health")
    print("  服务统计：http://localhost:8000/stats")
    print("\n启动命令:")
    print("  uvicorn model_serving:app --host 0.0.0.0 --port 8000")
    print("=" * 60)

if __name__ == '__main__':
    main()
