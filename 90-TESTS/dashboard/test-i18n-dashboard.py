#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test i18n Dashboard API
测试双语仪表盘 API

Author: Claw 🐾
"""

import requests
import json

BASE_URL = "http://localhost:8448"


def test_endpoint(endpoint: str, params: dict = None, method: str = 'GET'):
    """Test an endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=5)
        else:
            response = requests.post(url, json=params, timeout=5)
        
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        if params:
            print(f"Params: {params}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("\n" + "="*80)
    print("Testing i18n Dashboard API | 测试双语仪表盘 API")
    print("="*80)
    
    # Test 1: Health check
    print("\n[Test 1] Health Check | 健康检查")
    test_endpoint("/health")
    
    # Test 2: Supported languages
    print("\n[Test 2] Supported Languages | 支持的语言")
    test_endpoint("/api/i18n/languages")
    
    # Test 3: All personas (Chinese)
    print("\n[Test 3] All Personas (Chinese) | 所有人格 (中文)")
    test_endpoint("/api/personas", params={'lang': 'zh'})
    
    # Test 4: All personas (English)
    print("\n[Test 4] All Personas (English) | 所有人格 (英文)")
    test_endpoint("/api/personas", params={'lang': 'en'})
    
    # Test 5: Single persona (Chinese)
    print("\n[Test 5] Single Persona - planner (Chinese) | 单个人格 - 规划者 (中文)")
    test_endpoint("/api/personas/planner", params={'lang': 'zh'})
    
    # Test 6: Single persona (English)
    print("\n[Test 6] Single Persona - planner (English) | 单个人格 - Planner (英文)")
    test_endpoint("/api/personas/planner", params={'lang': 'en'})
    
    # Test 7: Dashboard summary (Chinese)
    print("\n[Test 7] Dashboard Summary (Chinese) | 仪表板汇总 (中文)")
    test_endpoint("/api/dashboard", params={'lang': 'zh'})
    
    # Test 8: Dashboard summary (English)
    print("\n[Test 8] Dashboard Summary (English) | 仪表板汇总 (英文)")
    test_endpoint("/api/dashboard", params={'lang': 'en'})
    
    # Test 9: Statistics (Chinese)
    print("\n[Test 9] Statistics (Chinese) | 统计信息 (中文)")
    test_endpoint("/api/personas/statistics", params={'lang': 'zh'})
    
    # Test 10: Statistics (English)
    print("\n[Test 10] Statistics (English) | 统计信息 (英文)")
    test_endpoint("/api/personas/statistics", params={'lang': 'en'})
    
    # Test 11: System health (bilingual)
    print("\n[Test 11] System Health (Bilingual) | 系统健康 (双语)")
    test_endpoint("/api/health/system", params={'lang': 'en'})
    
    # Test 12: Translations
    print("\n[Test 12] All Translations (English) | 所有翻译 (英文)")
    test_endpoint("/api/i18n/translations", params={'lang': 'en'})
    
    print("\n" + "="*80)
    print("✅ All tests completed! | 所有测试完成!")
    print("="*80)


if __name__ == '__main__':
    main()
