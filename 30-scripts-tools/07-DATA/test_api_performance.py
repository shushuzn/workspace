#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 性能测试脚本
测试 todo-036 REST API 响应时间和吞吐量
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查端点"""
    print("="*60)
    print("测试 1: 健康检查")
    print("="*60)
    
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/v1/health")
    elapsed = (time.time() - start) * 1000
    
    print(f"状态码：{response.status_code}")
    print(f"响应时间：{elapsed:.2f}ms")
    print(f"响应：{response.json()}")
    
    passed = response.status_code == 200 and elapsed < 200
    print(f"结果：{'✅ 通过' if passed else '❌ 失败'} (<200ms)\n")
    
    return {'name': 'health', 'passed': passed, 'response_time': elapsed}

def test_pdf_extract():
    """测试 PDF 提取端点"""
    print("="*60)
    print("测试 2: PDF 提取")
    print("="*60)
    
    # 使用测试 PDF 文件
    test_pdf = "D:/OpenClaw/workspace/10-ai-research/02-Models/_assets/2401.00001/2401.00001.pdf"
    
    payload = {
        "file_path": test_pdf,
        "max_pages": 5,
        "output_format": "markdown"
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/pdf/extract", json=payload)
    elapsed = (time.time() - start) * 1000
    
    print(f"状态码：{response.status_code}")
    print(f"响应时间：{elapsed:.2f}ms")
    
    if response.status_code == 200:
        data = response.json()
        print(f"消息：{data.get('message', 'N/A')}")
        print(f"处理页数：{data.get('data', {}).get('pages_processed', 'N/A')}")
    
    passed = response.status_code == 200 and elapsed < 5000
    print(f"结果：{'✅ 通过' if passed else '❌ 失败'} (<5s)\n")
    
    return {'name': 'pdf_extract', 'passed': passed, 'response_time': elapsed}

def test_figure_quality():
    """测试图表质量评估端点"""
    print("="*60)
    print("测试 3: 图表质量评估")
    print("="*60)
    
    # 使用测试图像
    test_image = "D:/OpenClaw/workspace/11-research/cnt-research/figures/active_learning_best_conductivity.png"
    
    payload = {
        "image_path": test_image,
        "auto_enhance": False
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/figure/enhance", json=payload)
    elapsed = (time.time() - start) * 1000
    
    print(f"状态码：{response.status_code}")
    print(f"响应时间：{elapsed:.2f}ms")
    
    if response.status_code == 200:
        data = response.json()
        print(f"消息：{data.get('message', 'N/A')}")
        print(f"建议：{data.get('data', {}).get('recommendation', 'N/A')}")
    
    passed = response.status_code == 200 and elapsed < 2000
    print(f"结果：{'✅ 通过' if passed else '❌ 失败'} (<2s)\n")
    
    return {'name': 'figure_quality', 'passed': passed, 'response_time': elapsed}

def test_throughput():
    """测试吞吐量 (并发请求)"""
    print("="*60)
    print("测试 4: 吞吐量测试 (10 并发健康检查)")
    print("="*60)
    
    start = time.time()
    
    # 发送 10 个并发请求
    import concurrent.futures
    
    def health_check():
        return requests.get(f"{BASE_URL}/api/v1/health")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(health_check) for _ in range(10)]
        results = [f.result() for f in futures]
    
    elapsed = (time.time() - start) * 1000
    avg_time = elapsed / 10
    
    success_count = sum(1 for r in results if r.status_code == 200)
    
    print(f"总耗时：{elapsed:.2f}ms")
    print(f"平均耗时：{avg_time:.2f}ms/请求")
    print(f"成功：{success_count}/10")
    print(f"吞吐量：{1000/avg_time:.1f} 请求/秒")
    
    passed = success_count == 10 and avg_time < 200
    print(f"结果：{'✅ 通过' if passed else '❌ 失败'}\n")
    
    return {'name': 'throughput', 'passed': passed, 'response_time': avg_time, 'requests_per_sec': 1000/avg_time}

def test_api_docs():
    """测试 API 文档"""
    print("="*60)
    print("测试 5: API 文档可用性")
    print("="*60)
    
    endpoints = [
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc"),
        ("/openapi.json", "OpenAPI Schema")
    ]
    
    all_passed = True
    
    for path, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{path}")
            passed = response.status_code == 200
            print(f"  {name}: {'✅' if passed else '❌'} ({response.status_code})")
            all_passed = all_passed and passed
        except Exception as e:
            print(f"  {name}: ❌ ({e})")
            all_passed = False
    
    print(f"\n结果：{'✅ 通过' if all_passed else '❌ 失败'}\n")
    
    return {'name': 'api_docs', 'passed': all_passed}

def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("🧪 OpenClaw API 性能测试 - todo-036")
    print("="*60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址：{BASE_URL}\n")
    
    results = []
    
    # 运行测试
    results.append(test_health())
    results.append(test_api_docs())
    results.append(test_figure_quality())
    results.append(test_pdf_extract())
    results.append(test_throughput())
    
    # 汇总
    print("="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for r in results if r.get('passed', False))
    total = len(results)
    
    for r in results:
        status = "✅" if r.get('passed', False) else "❌"
        print(f"{status} {r['name']}")
    
    print()
    print(f"通过：{passed}/{total}")
    
    # 验收标准检查
    print("\n" + "="*60)
    print("验收标准验证")
    print("="*60)
    
    avg_response = sum(r.get('response_time', 0) for r in results if 'response_time' in r) / len(results)
    
    criteria = [
        ("FastAPI 接口", all(r.get('passed', False) for r in results)),
        ("Swagger 文档", any(r['name'] == 'api_docs' and r.get('passed') for r in results)),
        ("响应时间<200ms", avg_response < 200),
        ("吞吐量>5 请求/秒", any(r.get('requests_per_sec', 0) > 5 for r in results)),
    ]
    
    for name, passed_crit in criteria:
        status = "✅" if passed_crit else "❌"
        print(f"{status} {name}")
    
    all_passed = all(p for _, p in criteria)
    
    print()
    if all_passed:
        print("🎉 所有验收标准通过！")
    else:
        print("⚠️  部分验收标准未通过")
    
    # 保存结果
    report = {
        'timestamp': datetime.now().isoformat(),
        'base_url': BASE_URL,
        'tests': results,
        'passed': passed,
        'total': total,
        'criteria': {name: passed_crit for name, passed_crit in criteria},
        'all_passed': all_passed,
        'avg_response_time': avg_response
    }
    
    report_file = Path(__file__).parent / "API-PERFORMANCE-REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 测试报告：{report_file}")
    
    return all_passed

if __name__ == "__main__":
    from pathlib import Path
    import sys
    
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 错误：无法连接到 API 服务器")
        print(f"   请确保 API 服务器正在运行：uvicorn main:app --reload")
        print(f"   地址：{BASE_URL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        sys.exit(1)
