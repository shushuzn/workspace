# Materials Science System - API 设计文档

**版本:** v1.0  
**创建时间:** 2026-03-05 19:15  
**目的:** 定义材料科学系统的 RESTful API 接口规范

---

## 📡 API 概览

**基础 URL:** `http://localhost:8080/api/v1`  
**认证方式:** API Key (Header: `X-API-Key`)  
**响应格式:** JSON

---

## 🔑 核心端点

### 1. 材料查询

#### GET /materials
查询材料列表，支持分页和过滤

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 (默认 1) |
| limit | int | 否 | 每页数量 (默认 20, 最大 100) |
| formula | string | 否 | 化学式模糊匹配 |
| space_group | int | 否 | 空间群编号 |
| energy_above_hull | float | 否 | 最大能量 (eV/atom) |
| band_gap | object | 否 | 带隙范围 {min, max} |

**响应:**
```json
{
  "total": 1250,
  "page": 1,
  "limit": 20,
  "materials": [
    {
      "id": "mp-1234",
      "formula": "SiO2",
      "space_group": 183,
      "energy_above_hull": 0.05,
      "band_gap": 8.9,
      "crystal_system": "hexagonal"
    }
  ]
}
```

#### GET /materials/{id}
获取单个材料详情

**响应:**
```json
{
  "id": "mp-1234",
  "formula": "SiO2",
  "formula_pretty": "SiO₂",
  "nelements": 2,
  "elements": ["Si", "O"],
  "space_group": {
    "number": 183,
    "symbol": "P6_3/mmc"
  },
  "crystal_system": "hexagonal",
  "energy_above_hull": 0.05,
  "formation_energy": -9.8,
  "band_gap": 8.9,
  "band_gap_type": "indirect",
  "density": 2.65,
  "volume": 112.5,
  "cif_url": "/api/v1/materials/mp-1234/cif",
  "structure": {
    "lattice": {...},
    "positions": [...]
  }
}
```

#### GET /materials/{id}/cif
获取 CIF 文件

**响应:** `text/plain` CIF 格式内容

---

### 2. 性能预测

#### POST /predict/bandgap
预测材料带隙

**请求:**
```json
{
  "formula": "Cs2AgBiBr6",
  "structure": "optional CIF content"
}
```

**响应:**
```json
{
  "predicted_bandgap": 2.15,
  "confidence": 0.87,
  "method": "GNN",
  "similar_materials": [
    {"id": "mp-5678", "bandgap": 2.08},
    {"id": "mp-9012", "bandgap": 2.22}
  ]
}
```

#### POST /predict/elastic
预测弹性性能

**请求:**
```json
{
  "material_id": "mp-1234"
}
```

**响应:**
```json
{
  "bulk_modulus": 35.2,
  "shear_modulus": 28.5,
  "young_modulus": 68.3,
  "poisson_ratio": 0.25,
  "elastic_tensor": [[...]],
  "is_stable": true
}
```

#### POST /predict/stability
预测材料稳定性

**响应:**
```json
{
  "is_stable": true,
  "energy_above_hull": 0.05,
  "decomposition": ["SiO2", "H2O"],
  "temperature_stability": {
    "max_temp": 1800,
    "unit": "K"
  }
}
```

---

### 3. 合成路径

#### GET /synthesize/{target_formula}
获取目标材料的合成路径推荐

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| max_steps | int | 否 | 最大反应步骤 (默认 5) |
| include_cost | bool | 否 | 包含成本估算 (默认 true) |

**响应:**
```json
{
  "target": "LiFePO4",
  "pathways": [
    {
      "id": 1,
      "steps": [
        {
          "reaction": "Li2CO3 + FeC2O4·2H2O → 2LiFePO4 + ...",
          "temperature": 700,
          "time": 12,
          "atmosphere": "Ar"
        }
      ],
      "yield": 0.92,
      "cost_estimate": 45.5,
      "difficulty": "medium",
      "references": ["doi:10.1021/..."]
    }
  ]
}
```

---

### 4. 知识图谱

#### GET /knowledge-graph/material/{id}
获取材料相关的知识图谱子图

**响应:**
```json
{
  "material_id": "mp-1234",
  "nodes": [
    {"id": "mp-1234", "type": "material", "label": "SiO2"},
    {"id": "prop-1", "type": "property", "label": "band_gap"},
    {"id": "paper-1", "type": "paper", "label": "Smith et al. 2025"}
  ],
  "edges": [
    {"source": "mp-1234", "target": "prop-1", "relation": "has_property"},
    {"source": "paper-1", "target": "mp-1234", "relation": "studies"}
  ]
}
```

#### GET /knowledge-graph/search
搜索知识图谱

**参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| query | string | 搜索关键词 |
| node_types | array | 过滤节点类型 |
| max_depth | int | 最大关系深度 |

---

### 5. 批量操作

#### POST /materials/batch
批量查询材料信息

**请求:**
```json
{
  "ids": ["mp-1234", "mp-5678", "mp-9012"],
  "fields": ["formula", "band_gap", "formation_energy"]
}
```

#### POST /predict/batch
批量性能预测

---

### 6. 系统状态

#### GET /health
健康检查

**响应:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "ml_models": "loaded",
    "cache": "active"
  },
  "uptime": 86400
}
```

#### GET /stats
系统统计

**响应:**
```json
{
  "total_materials": 150000,
  "predictions_today": 1250,
  "cache_hit_rate": 0.85,
  "avg_response_time_ms": 120
}
```

---

## 🔐 认证与安全

### API Key 管理

**请求头:**
```
X-API-Key: your_api_key_here
```

**速率限制:**
- 普通用户：100 请求/分钟
- 高级用户：1000 请求/分钟
- 批量操作：10 请求/分钟

### 错误响应

**标准错误格式:**
```json
{
  "error": {
    "code": "MATERIAL_NOT_FOUND",
    "message": "Material mp-99999 not found in database",
    "details": {...}
  }
}
```

**HTTP 状态码:**
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/API Key 无效 |
| 404 | 资源不存在 |
| 429 | 速率限制 |
| 500 | 服务器内部错误 |

---

## 📦 数据模型

### Material
```typescript
interface Material {
  id: string;           // Materials Project ID
  formula: string;      // 简化化学式
  formula_pretty: string; // 格式化化学式
  elements: string[];   // 元素列表
  space_group: number;  // 空间群编号
  crystal_system: string;
  energy_above_hull: number;
  formation_energy: number;
  band_gap: number;
  density: number;
  volume: number;
}
```

### Prediction
```typescript
interface Prediction {
  material_id: string;
  property: string;
  value: number;
  confidence: number;
  method: string;
  timestamp: string;
}
```

---

## 🧪 测试示例

### cURL 示例

```bash
# 查询材料
curl -X GET "http://localhost:8080/api/v1/materials/mp-1234" \
  -H "X-API-Key: your_key"

# 预测带隙
curl -X POST "http://localhost:8080/api/v1/predict/bandgap" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"formula": "Cs2AgBiBr6"}'

# 获取 CIF
curl -X GET "http://localhost:8080/api/v1/materials/mp-1234/cif" \
  -H "X-API-Key: your_key"
```

### Python 示例

```python
import requests

API_BASE = "http://localhost:8080/api/v1"
API_KEY = "your_key"

headers = {"X-API-Key": API_KEY}

# 查询材料
response = requests.get(f"{API_BASE}/materials/mp-1234", headers=headers)
material = response.json()

# 预测性能
response = requests.post(f"{API_BASE}/predict/bandgap", 
                        headers=headers,
                        json={"formula": "Cs2AgBiBr6"})
prediction = response.json()
```

---

## 📈 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-03-05 | 初始版本 |

---

*最后更新：2026-03-05 19:15*
