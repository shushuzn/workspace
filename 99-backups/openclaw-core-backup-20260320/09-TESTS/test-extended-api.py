#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Extended API
测试扩展 API 端点
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Extended API Endpoint Test")
print("=" * 60)

# 测试端点列表
endpoints = [
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/materials"),
    ("GET", "/materials/MP-1234"),
    ("GET", "/materials/formula/LiCoO2"),
    ("GET", "/materials/stats"),
    ("POST", "/materials/search", {"formula": "Li", "limit": 5}),
    ("GET", "/predict/bandgap", {"material_id": "MP-1234", "property": "bandgap"}),
    ("GET", "/predict/formation-energy", {"material_id": "MP-1234", "property": "formation_energy"}),
    ("GET", "/predict/elastic", {"material_id": "MP-1234", "property": "elastic"}),
    ("GET", "/predict/thermal", {"material_id": "MP-1234", "property": "thermal"}),
    ("GET", "/predict/all", {"material_id": "MP-1234", "property": "all"}),
    ("GET", "/synthesize/LiCoO2"),
    ("GET", "/synthesize/LiCoO2/cost"),
    ("GET", "/synthesize/LiCoO2/safety"),
    ("GET", "/synthesize/LiCoO2/yield"),
    ("GET", "/kg/materials/MP-1234"),
    ("GET", "/kg/elements/Li"),
    ("GET", "/kg/properties/band_gap"),
    ("GET", "/kg/stats"),
]

print(f"\n[TEST] Testing {len(endpoints)} endpoints...\n")

success_count = 0
fail_count = 0

for method, endpoint, *data in endpoints:
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data[0] if data else {}, timeout=5)

        if response.status_code == 200:
            print(f"[OK] {method} {endpoint}")
            success_count += 1
        else:
            print(f"[WARN] {method} {endpoint} - {response.status_code}")
            fail_count += 1
    except Exception as e:
        print(f"[FAIL] {method} {endpoint} - {e}")
        fail_count += 1

print("\n" + "=" * 60)
print(f"Test Results: {success_count} passed, {fail_count} failed")
print("=" * 60)

if fail_count == 0:
    print("\n[SUCCESS] All endpoints passed!")
else:
    print(f"\n[WARN] {fail_count} endpoints failed, please check if API service is running")
