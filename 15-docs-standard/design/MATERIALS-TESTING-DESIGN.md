# 材料学自动化测试 - 设计文档

**版本:** v0.1  
**创建时间:** 2026-03-05 13:34  
**目的:** 材料科学系统测试方案

---

## 🧪 测试范围

### 1. 单元测试

**测试对象:**
- CIF 文件解析器
- 材料描述符计算
- 性能预测模型
- 合成路径算法

**测试框架:** pytest

**示例:**
```python
def test_cif_parser():
    structure = Structure.from_file("test.cif")
    assert structure.formula == "LiCoO2"
    assert len(structure) == 4

def test_bandgap_prediction():
    model = load_model("bandgap_v1")
    prediction = model.predict(test_structure)
    assert 0 < prediction < 10  # 合理范围

def test_synthesis_path():
    pathway = find_pathway("LiCoO2")
    assert len(pathway) > 0
    assert pathway[0]['temperature'] > 0
```

---

### 2. 集成测试

**测试场景:**
1. **端到端材料查询**
   - 输入化学式 → 查询数据库 → 返回结果

2. **性能预测流程**
   - 上传 CIF → 计算描述符 → 预测性能 → 返回结果

3. **合成路径推荐**
   - 输入目标材料 → 搜索反应数据库 → 推荐路径 → 成本估算

**测试框架:** pytest + requests

**示例:**
```python
def test_material_search_api():
    response = requests.get(
        "http://localhost:8000/materials",
        params={"formula": "LiCoO2"}
    )
    assert response.status_code == 200
    assert len(response.json()["materials"]) > 0

def test_prediction_pipeline():
    with open("test.cif") as f:
        response = requests.post(
            "http://localhost:8000/predict/bandgap",
            json={"cif": f.read()}
        )
    assert response.status_code == 200
    assert "prediction" in response.json()
```

---

### 3. 性能测试

**测试指标:**
- API 响应时间 (<500ms)
- 并发处理能力 (>100 请求/秒)
- 数据库查询效率 (<100ms)
- 模型预测速度 (<1s/材料)

**测试工具:** locust, wrk

**示例:**
```python
# locustfile.py
from locust import HttpUser, task

class MaterialsUser(HttpUser):
    @task
    def search_material(self):
        self.client.get("/materials?formula=LiCoO2")
    
    @task(3)
    def predict_bandgap(self):
        self.client.post("/predict/bandgap", json={
            "cif": "test_cif_content"
        })
```

---

### 4. 数据验证测试

**测试内容:**
1. **数据完整性**
   - 必填字段是否存在
   - 数据格式是否正确

2. **数据一致性**
   - 数据库与 API 返回一致
   - 不同端点数据一致

3. **边界条件**
   - 极端性能值处理
   - 异常输入处理

**示例:**
```python
def test_data_completeness():
    material = get_material("MP-1234")
    assert "formula" in material
    assert "structure" in material
    assert "properties" in material

def test_edge_cases():
    # 测试极端带隙值
    response = predict_bandgap(extreme_structure)
    assert response["prediction"] >= 0
    
    # 测试无效输入
    response = predict_bandgap(invalid_cif)
    assert response["error"] is not None
```

---

## 📊 测试覆盖率目标

| 模块 | 目标覆盖率 |
|------|------------|
| 核心功能 | >90% |
| API 接口 | >85% |
| 数据解析 | >95% |
| ML 模型 | >80% |
| **总体** | **>85%** |

---

## 📅 实施计划

| 任务 | 用时 | 日期 |
|------|------|------|
| 单元测试编写 | 4 小时 | 03-31 |
| 集成测试编写 | 3 小时 | 03-31 |
| 性能测试配置 | 2 小时 | 04-01 |
| 数据验证测试 | 2 小时 | 04-01 |
| CI/CD 集成 | 3 小时 | 04-02 |
| **总计** | **14 小时** | - |

---

*最后更新：2026-03-05 13:34*
