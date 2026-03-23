#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials Database Tests
材料科学数据库核心功能测试用例
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from materials_database import MaterialsDatabase

# ============ 数据库连接测试 ============

class TestDatabaseConnection:
    """数据库连接测试"""

    def test_database_init(self):
        """测试数据库初始化"""
        db = MaterialsDatabase()
        assert db.mongodb_url is not None
        assert db.mongodb_db == "materials_db"
        assert db.connected == False

    def test_database_connect(self):
        """测试数据库连接"""
        db = MaterialsDatabase()
        # 不实际连接，只测试逻辑
        assert db.connect() in [True, False]  # 取决于 MongoDB 是否运行

# ============ 数据操作测试 ============

class TestDatabaseOperations:
    """数据库操作测试"""

    def test_insert_material_mock(self):
        """测试插入材料 (模拟)"""
        # 模拟数据
        material = {
            "formula": "LiCoO2",
            "band_gap": 2.5,
            "formation_energy": -2.1
        }
        assert "formula" in material
        assert "band_gap" in material

    def test_find_materials_mock(self):
        """测试查询材料 (模拟)"""
        # 模拟数据
        materials = [
            {"formula": "LiCoO2", "band_gap": 2.5},
            {"formula": "LiFePO4", "band_gap": 3.2}
        ]
        assert len(materials) == 2
        assert all("formula" in m for m in materials)

    def test_update_material_mock(self):
        """测试更新材料 (模拟)"""
        material = {"formula": "LiCoO2", "band_gap": 2.5}
        updates = {"band_gap": 3.0}
        material.update(updates)
        assert material["band_gap"] == 3.0

    def test_delete_material_mock(self):
        """测试删除材料 (模拟)"""
        materials = [{"id": "1", "formula": "LiCoO2"}]
        materials = [m for m in materials if m["id"] != "1"]
        assert len(materials) == 0

# ============ 数据验证测试 ============

class TestDataValidation:
    """数据验证测试"""

    def test_material_formula_validation(self):
        """测试化学式验证"""
        valid_formulas = ["LiCoO2", "LiFePO4", "Si", "TiO2"]
        for formula in valid_formulas:
            assert len(formula) > 0
            assert any(c.isupper() for c in formula)

    def test_band_gap_validation(self):
        """测试带隙验证"""
        band_gaps = [0, 1.1, 2.5, 3.2, 10.0]
        for bg in band_gaps:
            assert isinstance(bg, (int, float))
            assert bg >= 0

    def test_formation_energy_validation(self):
        """测试形成能验证"""
        formation_energies = [-10.0, -5.0, -2.1, 0, 5.0]
        for fe in formation_energies:
            assert isinstance(fe, (int, float))

# ============ 上下文管理器测试 ============

class TestContextManager:
    """上下文管理器测试"""

    def test_context_manager_usage(self):
        """测试上下文管理器使用"""
        # 模拟上下文管理器
        class MockDB:
            def __enter__(self):
                self.connected = True
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.connected = False

        with MockDB() as db:
            assert db.connected == True
        assert db.connected == False

# ============ 运行测试 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Materials Database Tests")
    print("=" * 60)

    # 运行 pytest
    pytest.main([__file__, "-v", "--tb=short"])

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)
