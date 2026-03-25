#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials Project API Client v1
Materials Project API 客户端实现
"""

import os
import requests
from typing import Dict, List, Optional

# 配置
MP_API_KEY = os.getenv("MP_API_KEY")  # 从.env 文件读取
if not MP_API_KEY:
    raise ValueError("MP_API_KEY not found! Please set it in .env file")
MP_BASE_URL = os.getenv("MP_BASE_URL", "https://api.materialsproject.org")

class MaterialsProjectClient:
    """Materials Project API 客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or MP_API_KEY
        self.base_url = MP_BASE_URL
        self.headers = {"X-API-KEY": self.api_key}

    def search_materials(self, formula: str = None, limit: int = 10) -> List[Dict]:
        """搜索材料"""
        url = f"{self.base_url}/materials/search"
        params = {"formula": formula, "limit": limit} if formula else {"limit": limit}

        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()

        return response.json().get("data", [])

    def get_material_details(self, material_id: str) -> Optional[Dict]:
        """获取材料详情"""
        url = f"{self.base_url}/materials/{material_id}"

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("data")
        return None

    def get_properties(self, material_id: str) -> Optional[Dict]:
        """获取材料性能"""
        data = self.get_material_details(material_id)
        if data:
            return {
                "band_gap": data.get("band_gap", 0),
                "formation_energy": data.get("formation_energy_per_atom", 0),
                "bulk_modulus": data.get("bulk_modulus", 0),
                "shear_modulus": data.get("shear_modulus", 0),
            }
        return None

    def get_structure(self, material_id: str) -> Optional[str]:
        """获取晶体结构 (CIF 格式)"""
        url = f"{self.base_url}/materials/{material_id}/structure/cif"

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        return None

def demo():
    """演示使用"""
    print("=" * 60)
    print("Materials Project API Client Demo")
    print("=" * 60)

    client = MaterialsProjectClient()

    # 搜索材料
    print("\n[1/3] Searching materials...")
    materials = client.search_materials(formula="LiCoO2", limit=5)
    print(f"  Found {len(materials)} materials")

    if materials:
        material_id = materials[0]["material_id"]

        # 获取详情
        print("\n[2/3] Getting material details...")
        details = client.get_material_details(material_id)
        if details:
            print(f"  Formula: {details.get('formula_pretty', 'N/A')}")

        # 获取性能
        print("\n[3/3] Getting properties...")
        properties = client.get_properties(material_id)
        if properties:
            print(f"  Band Gap: {properties.get('band_gap', 'N/A')} eV")
            print(f"  Formation Energy: {properties.get('formation_energy', 'N/A')} eV/atom")

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
