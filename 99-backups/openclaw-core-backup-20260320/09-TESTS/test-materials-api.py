#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials API Tests
材料科学 API 核心功能测试用例
"""

import pytest
import requests
import json

BASE_URL = "http://localhost:8000"

# ============ 基础端点测试 ============

class TestBasicEndpoints:
    """基础端点测试"""

    def test_root(self):
        """测试根路径"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_health(self):
        """测试健康检查"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

# ============ 材料查询测试 ============

class TestMaterialsEndpoints:
    """材料查询端点测试"""

    def test_get_materials(self):
        """测试获取材料列表"""
        response = requests.get(f"{BASE_URL}/materials")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_material_by_id(self):
        """测试按 ID 获取材料"""
        response = requests.get(f"{BASE_URL}/materials/MP-1234")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "MP-1234"
        assert "formula" in data

    def test_get_material_not_found(self):
        """测试材料未找到"""
        response = requests.get(f"{BASE_URL}/materials/MP-9999")
        assert response.status_code == 404

    def test_search_materials_by_formula(self):
        """测试按化学式搜索"""
        response = requests.get(f"{BASE_URL}/materials?formula=Li")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for mat in data:
            assert "Li" in mat.get("formula", "")

    def test_advanced_search(self):
        """测试高级搜索"""
        payload = {"formula": "Li", "band_gap_min": 2.0, "limit": 5}
        response = requests.post(f"{BASE_URL}/materials/search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for mat in data:
            assert mat.get("band_gap", 0) >= 2.0

    def test_get_materials_stats(self):
        """测试材料统计"""
        response = requests.get(f"{BASE_URL}/materials/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "band_gap_range" in data

# ============ 性能预测测试 ============

class TestPredictionEndpoints:
    """性能预测端点测试"""

    def test_predict_bandgap(self):
        """测试带隙预测"""
        payload = {"material_id": "MP-1234", "property": "bandgap"}
        response = requests.post(f"{BASE_URL}/predict/bandgap", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "unit" in data
        assert "confidence" in data

    def test_predict_formation_energy(self):
        """测试形成能预测"""
        payload = {"material_id": "MP-1234", "property": "formation_energy"}
        response = requests.post(f"{BASE_URL}/predict/formation-energy", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert data["unit"] == "eV/atom"

    def test_predict_elastic(self):
        """测试弹性性能预测"""
        payload = {"material_id": "MP-1234", "property": "elastic"}
        response = requests.post(f"{BASE_URL}/predict/elastic", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "bulk_modulus" in data
        assert "shear_modulus" in data
        assert "young_modulus" in data

    def test_predict_all(self):
        """测试所有性能预测"""
        payload = {"material_id": "MP-1234", "property": "all"}
        response = requests.post(f"{BASE_URL}/predict/all", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "bandgap" in data
        assert "formation_energy" in data
        assert "elastic" in data

# ============ 合成路径测试 ============

class TestSynthesisEndpoints:
    """合成路径端点测试"""

    def test_get_synthesis_pathway(self):
        """测试获取合成路径"""
        response = requests.get(f"{BASE_URL}/synthesize/LiCoO2")
        assert response.status_code == 200
        data = response.json()
        assert data["target"] == "LiCoO2"
        assert "pathways" in data
        assert len(data["pathways"]) > 0

    def test_recommend_synthesis(self):
        """测试推荐合成路径"""
        payload = {"target": "LiCoO2", "optimize": "cost"}
        response = requests.post(f"{BASE_URL}/synthesize", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "target" in data
        assert "pathways" in data

    def test_get_synthesis_cost(self):
        """测试获取合成成本"""
        response = requests.get(f"{BASE_URL}/synthesize/LiCoO2/cost")
        assert response.status_code == 200
        data = response.json()
        assert "target" in data
        assert "cost" in data

    def test_get_synthesis_safety(self):
        """测试获取安全性评分"""
        response = requests.get(f"{BASE_URL}/synthesize/LiCoO2/safety")
        assert response.status_code == 200
        data = response.json()
        assert "target" in data
        assert "safety_score" in data

# ============ 知识图谱测试 ============

class TestKnowledgeGraphEndpoints:
    """知识图谱端点测试"""

    def test_get_material_kg(self):
        """测试获取材料知识图谱"""
        response = requests.get(f"{BASE_URL}/kg/materials/MP-1234")
        assert response.status_code == 200
        data = response.json()
        assert "material" in data
        assert "entities" in data
        assert "relations" in data

    def test_get_element_kg(self):
        """测试获取元素知识图谱"""
        response = requests.get(f"{BASE_URL}/kg/elements/Li")
        assert response.status_code == 200
        data = response.json()
        assert "element" in data
        assert "materials" in data

    def test_get_kg_stats(self):
        """测试获取知识图谱统计"""
        response = requests.get(f"{BASE_URL}/kg/stats")
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data
        assert "relations" in data

# ============ 运行测试 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Materials API Tests")
    print("=" * 60)

    # 运行 pytest
    pytest.main([__file__, "-v", "--tb=short"])

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)
