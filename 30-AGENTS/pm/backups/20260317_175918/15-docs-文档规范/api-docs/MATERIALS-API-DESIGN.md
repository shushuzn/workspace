# 材料学 API 服务 - 设计文档

**版本:** v0.1  
**创建时间:** 2026-03-05 13:34  
**目的:** 材料科学 REST API 服务设计

---

## 📋 API 设计

### 基础信息
- **框架:** FastAPI
- **端口:** 8000
- **认证:** API Key (可选)
- **文档:** /docs (Swagger UI)

---

## 🔌 API 端点

### 1. 材料查询

#### GET /materials
```
参数:
- formula: 化学式 (可选)
- property: 性能筛选 (可选)
- limit: 返回数量限制 (默认 10)

响应:
{
  "total": 100,
  "materials": [
    {
      "id": "MP-1234",
      "formula": "LiCoO2",
      "band_gap": 2.5,
      "stability": 0.05
    }
  ]
}
```

#### GET /materials/{id}
```
响应:
{
  "id": "MP-1234",
  "formula": "LiCoO2",
  "structure": {...},
  "properties": {...},
  "synthesis": [...]
}
```

---

### 2. 性能预测

#### POST /predict/bandgap
```
请求:
{
  "cif": "CIF 文件内容或 URL",
  "model": "预训练模型名称"
}

响应:
{
  "prediction": 2.5,
  "unit": "eV",
  "confidence": 0.92,
  "model_version": "v1.0"
}
```

#### POST /predict/elastic
```
请求:
{
  "material_id": "MP-1234"
}

响应:
{
  "bulk_modulus": 150.5,
  "shear_modulus": 80.2,
  "young_modulus": 200.1,
  "unit": "GPa"
}
```

---

### 3. 合成路径

#### POST /synthesize
```
请求:
{
  "target": "LiCoO2",
  "optimize": "cost"  // cost, safety, yield
}

响应:
{
  "pathways": [
    {
      "reactants": ["Li2CO3", "CoCO3"],
      "conditions": {
        "temperature": 900,
        "time": 12,
        "atmosphere": "air"
      },
      "cost": 50.0,
      "safety_score": 85,
      "yield": 0.95
    }
  ]
}
```

---

### 4. 知识图谱

#### GET /kg/materials/{id}
```
响应:
{
  "material": "LiCoO2",
  "relations": [
    {"type": "contains", "target": "Li"},
    {"type": "has_property", "target": "High Voltage"},
    {"type": "used_for", "target": "Battery"}
  ]
}
```

#### GET /kg/search
```
参数:
- query: 搜索关键词
- type: 实体类型 (可选)

响应:
{
  "entities": [...],
  "relations": [...]
}
```

---

## 🔧 技术实现

### 项目结构
```
materials-api/
├── main.py              # FastAPI 应用入口
├── routers/
│   ├── materials.py     # 材料路由
│   ├── predict.py       # 预测路由
│   ├── synthesize.py    # 合成路径路由
│   └── kg.py            # 知识图谱路由
├── models/
│   ├── material.py      # 材料数据模型
│   └── prediction.py    # 预测模型
├── services/
│   ├── database.py      # 数据库服务
│   ├── ml_models.py     # ML 模型服务
│   └── kg_service.py    # 知识图谱服务
├── utils/
│   └── cif_parser.py    # CIF 文件解析
└── config.py            # 配置文件
```

### 依赖库
```requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
pymatgen==2024.0.0
matminer==0.9.0
scikit-learn==1.4.0
torch==2.1.0
pymongo==4.6.0
neo4j==5.16.0
```

---

## 📅 实施计划

| 任务 | 用时 | 日期 |
|------|------|------|
| API 框架搭建 | 2 小时 | 03-28 |
| 材料查询接口 | 3 小时 | 03-28 |
| 性能预测接口 | 4 小时 | 03-29 |
| 合成路径接口 | 3 小时 | 03-29 |
| 知识图谱接口 | 3 小时 | 03-30 |
| API 文档完善 | 2 小时 | 03-30 |
| **总计** | **17 小时** | - |

---

*最后更新：2026-03-05 13:34*
