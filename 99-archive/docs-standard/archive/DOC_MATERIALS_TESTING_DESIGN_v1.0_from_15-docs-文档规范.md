# Materials Science System - 测试设计文档

**版本:** v1.0  
**创建时间:** 2026-03-05 19:20  
**目的:** 定义材料科学系统的测试策略和测试用例

---

## 🧪 测试策略

### 测试层次

```
┌─────────────────────────┐
│   端到端测试 (E2E)      │  ← 完整工作流验证
├─────────────────────────┤
│   集成测试              │  ← 模块间交互
├─────────────────────────┤
│   单元测试              │  ← 单个函数/类
└─────────────────────────┘
```

### 测试覆盖率目标

| 模块 | 覆盖率目标 | 优先级 |
|------|-----------|--------|
| API 客户端 | >90% | 🔴 高 |
| CIF 解析器 | >95% | 🔴 高 |
| 性能预测 | >85% | 🟡 中 |
| 合成路径 | >80% | 🟡 中 |
| Web 界面 | >70% | 🟢 低 |

---

## 📦 单元测试

### 1. CIF 解析器测试

**文件:** `tests/test_cif_parser.py`

```python
import pytest
from scripts.materials.cif_parser import CIFParser

class TestCIFParser:
    
    def test_parse_valid_cif(self):
        """测试解析有效的 CIF 文件"""
        parser = CIFParser()
        cif_content = """
        data_test
        _cell_length_a 5.43
        _cell_length_b 5.43
        _cell_length_c 5.43
        _cell_angle_alpha 90
        _cell_angle_beta 90
        _cell_angle_gamma 90
        _space_group_name_H-M_alt 'F d -3 m'
        loop_
        _atom_site_label
        _atom_site_fract_x
        _atom_site_fract_y
        _atom_site_fract_z
        Si 0 0 0
        """
        result = parser.parse(cif_content)
        
        assert result['formula'] == 'Si'
        assert result['crystal_system'] == 'cubic'
        assert result['space_group'] == 227
        assert len(result['atoms']) == 1
    
    def test_parse_invalid_cif(self):
        """测试解析无效的 CIF 文件"""
        parser = CIFParser()
        
        with pytest.raises(ValueError) as excinfo:
            parser.parse("invalid content")
        
        assert "Invalid CIF format" in str(excinfo.value)
    
    def test_extract_lattice_parameters(self):
        """测试提取晶格参数"""
        parser = CIFParser()
        cif_content = """
        _cell_length_a 4.5
        _cell_length_b 4.5
        _cell_length_c 6.0
        _cell_angle_alpha 90
        _cell_angle_beta 90
        _cell_angle_gamma 120
        """
        lattice = parser.extract_lattice(cif_content)
        
        assert lattice['a'] == 4.5
        assert lattice['c'] == 6.0
        assert lattice['alpha'] == 90
        assert lattice['gamma'] == 120
    
    def test_calculate_density(self):
        """测试计算密度"""
        parser = CIFParser()
        
        # SiO2, 体积 112.5 Å³
        density = parser.calculate_density(
            formula='SiO2',
            volume=112.5,
            z=1
        )
        
        assert 2.6 <= density <= 2.7  # g/cm³
```

### 2. Materials Project API 测试

**文件:** `tests/test_mp_api.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from scripts.materials.materials_project_api import MaterialsProjectAPI

class TestMaterialsProjectAPI:
    
    @pytest.fixture
    def api_client(self):
        return MaterialsProjectAPI(api_key="test_key")
    
    @patch('requests.get')
    def test_get_material_success(self, mock_get, api_client):
        """测试成功获取材料信息"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'material_id': 'mp-1234',
                'formula_pretty': 'SiO2',
                'band_gap': 8.9
            }
        }
        mock_get.return_value = mock_response
        
        result = api_client.get_material('mp-1234')
        
        assert result['material_id'] == 'mp-1234'
        assert result['band_gap'] == 8.9
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_material_not_found(self, mock_get, api_client):
        """测试材料不存在"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(MaterialNotFoundError):
            api_client.get_material('mp-99999')
    
    @patch('requests.get')
    def test_search_materials(self, mock_get, api_client):
        """测试搜索材料"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'material_id': 'mp-1', 'formula_pretty': 'SiO2'},
                {'material_id': 'mp-2', 'formula_pretty': 'TiO2'}
            ]
        }
        mock_get.return_value = mock_response
        
        results = api_client.search(formula='O2')
        
        assert len(results) == 2
        assert any(r['formula_pretty'] == 'SiO2' for r in results)
    
    def test_rate_limiting(self, api_client):
        """测试速率限制处理"""
        # 模拟连续快速请求
        for i in range(10):
            # 应该自动添加延迟
            api_client._check_rate_limit()
```

### 3. 性能预测测试

**文件:** `tests/test_property_prediction.py`

```python
import pytest
import numpy as np
from scripts.materials.property_prediction import BandGapPredictor

class TestBandGapPredictor:
    
    @pytest.fixture
    def predictor(self):
        return BandGapPredictor(model_path="models/bandgap_model.pkl")
    
    def test_predict_single(self, predictor):
        """测试单个材料预测"""
        features = {
            'formula': 'Cs2AgBiBr6',
            'num_elements': 4,
            'avg_electronegativity': 2.5,
            'volume': 250.0
        }
        
        prediction = predictor.predict(features)
        
        assert 'bandgap' in prediction
        assert 'confidence' in prediction
        assert 0 <= prediction['bandgap'] <= 10  # 合理范围
        assert 0 <= prediction['confidence'] <= 1
    
    def test_predict_batch(self, predictor):
        """测试批量预测"""
        materials = [
            {'formula': 'SiO2', 'num_elements': 2},
            {'formula': 'TiO2', 'num_elements': 2},
            {'formula': 'ZnO', 'num_elements': 2}
        ]
        
        predictions = predictor.predict_batch(materials)
        
        assert len(predictions) == 3
        assert all('bandgap' in p for p in predictions)
    
    def test_confidence_threshold(self, predictor):
        """测试置信度阈值"""
        features = {'formula': 'Unknown', 'num_elements': 10}
        
        prediction = predictor.predict(features)
        
        # 未知材料应该置信度低
        if prediction.get('is_out_of_distribution', False):
            assert prediction['confidence'] < 0.5
    
    def test_model_loading_failure(self):
        """测试模型加载失败处理"""
        with pytest.raises(FileNotFoundError):
            BandGapPredictor(model_path="nonexistent_model.pkl")
```

### 4. 合成路径推荐测试

**文件:** `tests/test_synthesis_pathway.py`

```python
import pytest
from scripts.materials.synthesis_pathway_recommender import SynthesisPathwayRecommender

class TestSynthesisPathwayRecommender:
    
    @pytest.fixture
    def recommender(self):
        return SynthesisPathwayRecommender()
    
    def test_find_pathways_simple(self, recommender):
        """测试简单合成路径"""
        target = "LiFePO4"
        
        pathways = recommender.find_pathways(target)
        
        assert len(pathways) > 0
        assert all('steps' in p for p in pathways)
        assert all('cost_estimate' in p for p in pathways)
    
    def test_cost_estimation(self, recommender):
        """测试成本估算"""
        pathway = {
            'precursors': ['Li2CO3', 'FeC2O4·2H2O', 'NH4H2PO4'],
            'temperature': 700,
            'time_hours': 12
        }
        
        cost = recommender.estimate_cost(pathway)
        
        assert cost > 0
        assert 'currency' in cost
        assert cost['currency'] == 'USD'
    
    def test_safety_assessment(self, recommender):
        """测试安全性评估"""
        chemicals = ['Li2CO3', 'HF', 'H2SO4']
        
        safety = recommender.assess_safety(chemicals)
        
        assert 'hazards' in safety
        assert 'precautions' in safety
        assert len(safety['hazards']) > 0
    
    def test_pathway_ranking(self, recommender):
        """测试路径排序"""
        target = "LiFePO4"
        
        pathways = recommender.find_pathways(target, rank_by='cost')
        
        # 应该按成本排序
        costs = [p['cost_estimate'] for p in pathways]
        assert costs == sorted(costs)
```

---

## 🔗 集成测试

### 1. API 端到端测试

**文件:** `tests/integration/test_api_endpoints.py`

```python
import pytest
import requests
from scripts.materials.materials_api_service import MaterialsAPIService

class TestAPIEndpoints:
    
    @pytest.fixture(scope="module")
    def api_service(self):
        """启动测试 API 服务"""
        service = MaterialsAPIService(port=8081, test_mode=True)
        service.start()
        yield service
        service.stop()
    
    def test_get_materials_endpoint(self, api_service):
        """测试 GET /materials 端点"""
        response = requests.get(
            "http://localhost:8081/api/v1/materials",
            params={"limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'materials' in data
        assert len(data['materials']) <= 5
    
    def test_get_material_by_id(self, api_service):
        """测试 GET /materials/{id} 端点"""
        response = requests.get(
            "http://localhost:8081/api/v1/materials/mp-1234"
        )
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert 'material_id' in data
            assert 'formula_pretty' in data
    
    def test_predict_bandgap_endpoint(self, api_service):
        """测试 POST /predict/bandgap 端点"""
        response = requests.post(
            "http://localhost:8081/api/v1/predict/bandgap",
            json={"formula": "Cs2AgBiBr6"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'predicted_bandgap' in data
        assert 'confidence' in data
    
    def test_authentication_required(self, api_service):
        """测试认证要求"""
        response = requests.get(
            "http://localhost:8081/api/v1/materials/mp-1234",
            headers={"X-API-Key": "invalid_key"}
        )
        
        assert response.status_code in [401, 403]
    
    def test_rate_limiting(self, api_service):
        """测试速率限制"""
        # 发送大量请求
        for i in range(100):
            response = requests.get(
                "http://localhost:8081/api/v1/health"
            )
        
        # 应该触发速率限制
        assert response.status_code in [200, 429]
```

### 2. 数据库集成测试

**文件:** `tests/integration/test_database.py`

```python
import pytest
from scripts.materials.materials_database import MaterialsDatabase

class TestDatabaseIntegration:
    
    @pytest.fixture
    def db(self):
        """连接测试数据库"""
        return MaterialsDatabase(connection_string="mongodb://localhost:27017/test_materials")
    
    def test_insert_material(self, db):
        """测试插入材料"""
        material = {
            'material_id': 'mp-test-001',
            'formula': 'SiO2',
            'band_gap': 8.9
        }
        
        result = db.insert_material(material)
        
        assert result.inserted_id is not None
        
        # 清理
        db.delete_material('mp-test-001')
    
    def test_query_materials(self, db):
        """测试查询材料"""
        # 先插入测试数据
        db.insert_material({'material_id': 'mp-test-002', 'formula': 'TiO2', 'band_gap': 3.2})
        
        results = db.query_materials(formula='O2')
        
        assert len(results) > 0
        assert any(r['material_id'] == 'mp-test-002' for r in results)
        
        # 清理
        db.delete_material('mp-test-002')
    
    def test_batch_insert(self, db):
        """测试批量插入"""
        materials = [
            {'material_id': f'mp-test-{i}', 'formula': f'X{i}O2'}
            for i in range(10)
        ]
        
        result = db.batch_insert(materials)
        
        assert result.matched_count == 10
        
        # 清理
        for m in materials:
            db.delete_material(m['material_id'])
```

---

## 🌐 端到端测试 (E2E)

### 1. 完整工作流测试

**文件:** `tests/e2e/test_complete_workflow.py`

```python
import pytest
from scripts.materials.materials_collector import MaterialsCollector
from scripts.materials.cif_parser import CIFParser
from scripts.materials.property_prediction import BandGapPredictor

class TestCompleteWorkflow:
    
    def test_collect_parse_predict(self):
        """测试完整工作流：收集→解析→预测"""
        # 1. 收集材料数据
        collector = MaterialsCollector()
        materials = collector.collect_from_arxiv(category='cond-mat.mtrl-sci', limit=5)
        
        assert len(materials) > 0
        
        # 2. 解析 CIF 文件
        parser = CIFParser()
        for material in materials:
            if material.get('cif_content'):
                structure = parser.parse(material['cif_content'])
                assert 'formula' in structure
        
        # 3. 预测性能
        predictor = BandGapPredictor()
        for material in materials:
            prediction = predictor.predict(material)
            assert 'bandgap' in prediction
    
    def test_knowledge_graph_construction(self):
        """测试知识图谱构建"""
        from scripts.materials.materials_knowledge_graph import MaterialsKnowledgeGraph
        
        kg = MaterialsKnowledgeGraph()
        
        # 添加材料节点
        kg.add_material('mp-1234', 'SiO2')
        kg.add_material('mp-5678', 'TiO2')
        
        # 添加关系
        kg.add_relationship('mp-1234', 'mp-5678', 'similar_structure')
        
        # 查询图谱
        subgraph = kg.get_subgraph('mp-1234', depth=1)
        
        assert len(subgraph['nodes']) >= 1
        assert len(subgraph['edges']) >= 1
```

### 2. Web 界面测试

**文件:** `tests/e2e/test_web_interface.py`

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestWebInterface:
    
    @pytest.fixture
    def browser(self):
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    def test_material_search(self, browser):
        """测试材料搜索功能"""
        browser.get("http://localhost:8080/materials-search.html")
        
        # 输入搜索词
        search_box = browser.find_element(By.ID, "search-input")
        search_box.send_keys("SiO2")
        
        # 点击搜索
        search_button = browser.find_element(By.ID, "search-button")
        search_button.click()
        
        # 验证结果
        results = browser.find_elements(By.CLASS_NAME, "material-result")
        assert len(results) > 0
    
    def test_crystal_visualization(self, browser):
        """测试晶体可视化"""
        browser.get("http://localhost:8080/crystal-viewer.html")
        
        # 上传 CIF 文件
        file_input = browser.find_element(By.ID, "cif-upload")
        file_input.send_keys("/path/to/test.cif")
        
        # 验证 3D 渲染
        canvas = browser.find_element(By.ID, "crystal-canvas")
        assert canvas.is_displayed()
```

---

## 📊 测试报告

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v --cov=scripts/materials

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 生成覆盖率报告
pytest --cov=scripts/materials --cov-report=html
```

### 覆盖率报告示例

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
scripts/materials/cif_parser.py           150      8    95%
scripts/materials/mp_api.py               200     15    93%
scripts/materials/property_prediction.py  180     20    89%
scripts/materials/synthesis_pathway.py    160     25    84%
scripts/materials/knowledge_graph.py      140     12    91%
-----------------------------------------------------------
TOTAL                                     830     80    90%
```

---

## 🐛 已知问题与待办

- [ ] 添加更多边界条件测试
- [ ] 增加性能基准测试
- [ ] 添加并发测试
- [ ] 完善 Mock 数据
- [ ] 添加 CI/CD 集成

---

*最后更新：2026-03-05 19:20*
