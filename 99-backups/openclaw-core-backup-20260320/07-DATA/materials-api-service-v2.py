#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials API Service v2 - Extended
材料科学 REST API 服务实现 (扩展版 - 20+ 端点)
"""

from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

# 创建 FastAPI 应用
app = FastAPI(
    title="Materials Science API v2",
    description="材料科学 REST API 服务 (扩展版 - 20+ 端点)",
    version="2.0.0"
)

# ============ 数据模型 ============

class Material(BaseModel):
    id: Optional[str] = None
    formula: str
    band_gap: Optional[float] = None
    formation_energy: Optional[float] = None
    space_group: Optional[str] = None

class MaterialSearch(BaseModel):
    formula: Optional[str] = None
    band_gap_min: Optional[float] = None
    band_gap_max: Optional[float] = None
    limit: int = 10

class PredictionRequest(BaseModel):
    material_id: str
    property: str

class PredictionResponse(BaseModel):
    prediction: float
    unit: str
    confidence: float

class SynthesisPathway(BaseModel):
    reactants: List[str]
    conditions: Dict[str, Any]
    cost: float
    safety_score: int
    yield_rate: float

class KnowledgeGraphEntity(BaseModel):
    id: str
    type: str
    name: str

class KnowledgeGraphRelation(BaseModel):
    source: str
    target: str
    type: str

# ============ 模拟数据库 ============

MATERIALS_DB = [
    {"id": "MP-1234", "formula": "LiCoO2", "band_gap": 2.5, "formation_energy": -2.1, "space_group": "R-3m"},
    {"id": "MP-5678", "formula": "LiFePO4", "band_gap": 3.2, "formation_energy": -2.5, "space_group": "Pnma"},
    {"id": "MP-9012", "formula": "Si", "band_gap": 1.1, "formation_energy": -4.6, "space_group": "Fd-3m"},
    {"id": "MP-3456", "formula": "Graphene", "band_gap": 0, "formation_energy": -7.5, "space_group": "P6/mmm"},
    {"id": "MP-7890", "formula": "TiO2", "band_gap": 3.0, "formation_energy": -9.8, "space_group": "P4_2/mnm"},
]

# ============ 基础端点 (6 个) ============

@app.get("/")
def root():
    """API 根路径"""
    return {"name": "Materials Science API", "version": "2.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": "2026-03-05T14:30:00"}

@app.get("/materials", response_model=List[Material], tags=["Materials"])
def search_materials(
    formula: Optional[str] = Query(None, description="化学式搜索"),
    limit: int = Query(10, description="返回数量限制")
):
    """搜索材料"""
    results = MATERIALS_DB[:limit]
    if formula:
        results = [m for m in results if formula.lower() in m["formula"].lower()]
    return results

@app.get("/materials/{material_id}", tags=["Materials"])
def get_material(material_id: str):
    """获取材料详情"""
    for mat in MATERIALS_DB:
        if mat["id"] == material_id:
            return mat
    raise HTTPException(status_code=404, detail="Material not found")

@app.post("/predict/bandgap", response_model=PredictionResponse, tags=["Predictions"])
def predict_bandgap(request: PredictionRequest):
    """预测带隙"""
    return PredictionResponse(prediction=2.5, unit="eV", confidence=0.92)

@app.get("/synthesize/{target}", tags=["Synthesis"])
def get_synthesis_pathway(target: str):
    """获取合成路径"""
    return {"target": target, "pathways": [{"reactants": ["Li2CO3", "CoCO3"], "conditions": {"temperature": 900, "time": 12, "atmosphere": "air"}, "cost": 50.0, "safety_score": 85, "yield_rate": 0.95}]}

# ============ 扩展端点 (16 个) ============

# Materials - 材料查询 (4 个)

@app.post("/materials/search", response_model=List[Material], tags=["Materials"])
def advanced_search_materials(search: MaterialSearch):
    """高级材料搜索"""
    results = MATERIALS_DB
    if search.formula:
        results = [m for m in results if search.formula.lower() in m["formula"].lower()]
    if search.band_gap_min is not None:
        results = [m for m in results if m.get("band_gap", 0) >= search.band_gap_min]
    if search.band_gap_max is not None:
        results = [m for m in results if m.get("band_gap", 10) <= search.band_gap_max]
    return results[:search.limit]

@app.get("/materials/formula/{formula}", tags=["Materials"])
def get_material_by_formula(formula: str):
    """按化学式获取材料"""
    for mat in MATERIALS_DB:
        if mat["formula"].lower() == formula.lower():
            return mat
    raise HTTPException(status_code=404, detail="Material not found")

@app.get("/materials/stats", tags=["Materials"])
def get_materials_stats():
    """获取材料统计"""
    return {
        "total": len(MATERIALS_DB),
        "band_gap_range": [min(m.get("band_gap", 0) for m in MATERIALS_DB), max(m.get("band_gap", 10) for m in MATERIALS_DB)],
        "formulas": [m["formula"] for m in MATERIALS_DB]
    }

@app.put("/materials/{material_id}", tags=["Materials"])
def update_material(material_id: str, updates: Dict[str, Any]):
    """更新材料"""
    for mat in MATERIALS_DB:
        if mat["id"] == material_id:
            mat.update(updates)
            return {"status": "success", "material": mat}
    raise HTTPException(status_code=404, detail="Material not found")

# Predictions - 性能预测 (4 个)

@app.post("/predict/formation-energy", response_model=PredictionResponse, tags=["Predictions"])
def predict_formation_energy(request: PredictionRequest):
    """预测形成能"""
    return PredictionResponse(prediction=-2.1, unit="eV/atom", confidence=0.88)

@app.post("/predict/elastic", tags=["Predictions"])
def predict_elastic_properties(request: PredictionRequest):
    """预测弹性性能"""
    return {"bulk_modulus": 150.5, "shear_modulus": 80.2, "young_modulus": 200.1, "unit": "GPa", "confidence": 0.85}

@app.post("/predict/thermal", tags=["Predictions"])
def predict_thermal_properties(request: PredictionRequest):
    """预测热学性能"""
    return {"thermal_conductivity": 50.0, "thermal_expansion": 10.5, "unit": "W/mK", "confidence": 0.82}

@app.post("/predict/all", tags=["Predictions"])
def predict_all_properties(request: PredictionRequest):
    """预测所有性能"""
    return {
        "bandgap": {"prediction": 2.5, "unit": "eV", "confidence": 0.92},
        "formation_energy": {"prediction": -2.1, "unit": "eV/atom", "confidence": 0.88},
        "elastic": {"bulk_modulus": 150.5, "shear_modulus": 80.2, "young_modulus": 200.1, "unit": "GPa", "confidence": 0.85}
    }

# Synthesis - 合成路径 (4 个)

@app.post("/synthesize", response_model=Dict[str, Any], tags=["Synthesis"])
def recommend_synthesis(target: str = Body(...), optimize: str = Body("cost")):
    """推荐合成路径"""
    return {"target": target, "optimize": optimize, "pathways": [{"reactants": ["Li2CO3", "CoCO3"], "conditions": {"temperature": 900, "time": 12, "atmosphere": "air"}, "cost": 50.0, "safety_score": 85, "yield_rate": 0.95}]}

@app.get("/synthesize/{target}/cost", tags=["Synthesis"])
def get_synthesis_cost(target: str):
    """获取合成成本"""
    return {"target": target, "cost": 50.0, "unit": "¥/g"}

@app.get("/synthesize/{target}/safety", tags=["Synthesis"])
def get_synthesis_safety(target: str):
    """获取合成安全性评分"""
    return {"target": target, "safety_score": 85, "max_score": 100}

@app.get("/synthesize/{target}/yield", tags=["Synthesis"])
def get_synthesis_yield(target: str):
    """获取合成产率"""
    return {"target": target, "yield_rate": 0.95, "unit": "%"}

# Knowledge Graph - 知识图谱 (4 个)

@app.get("/kg/materials/{material_id}", tags=["KnowledgeGraph"])
def get_material_kg(material_id: str):
    """获取材料知识图谱"""
    return {"material": material_id, "entities": [{"id": "elem_Li", "type": "Element", "name": "Li"}, {"id": "elem_Co", "type": "Element", "name": "Co"}], "relations": [{"source": material_id, "target": "elem_Li", "type": "contains"}, {"source": material_id, "target": "elem_Co", "type": "contains"}]}

@app.get("/kg/elements/{element}", tags=["KnowledgeGraph"])
def get_element_kg(element: str):
    """获取元素知识图谱"""
    return {"element": element, "materials": ["LiCoO2", "LiFePO4"], "properties": ["atomic_number", "atomic_weight"]}

@app.get("/kg/properties/{property}", tags=["KnowledgeGraph"])
def get_property_kg(property: str):
    """获取性能知识图谱"""
    return {"property": property, "materials": ["LiCoO2", "Si"], "range": [0, 10]}

@app.get("/kg/stats", tags=["KnowledgeGraph"])
def get_kg_stats():
    """获取知识图谱统计"""
    return {"entities": 100, "relations": 250, "materials": 50, "elements": 30}

# ============ 启动服务 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Materials Science API Service v2.0 - Extended")
    print("=" * 60)
    print("\n端点总数：22 个")
    print("  - 基础端点：6 个")
    print("  - 扩展端点：16 个")
    print("\n启动服务...")
    print("API 文档：http://localhost:8000/docs")
    print("健康检查：http://localhost:8000/health")
    print("-" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
