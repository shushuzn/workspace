#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance Benchmark - 性能基准测试

测试系统性能并生成报告
"""

import os
import time
import json
import statistics
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
BENCHMARK_DIR = "21-reports\\benchmarks"

def benchmark_file_read():
    """文件读取性能测试"""
    results = []
    test_file = os.path.join(WORKSPACE, "SOUL.md")
    
    for i in range(10):
        start = time.perf_counter()
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        end = time.perf_counter()
        results.append((end - start) * 1000)  # ms
    
    return {
        "test": "File Read (SOUL.md)",
        "iterations": 10,
        "mean_ms": statistics.mean(results),
        "median_ms": statistics.median(results),
        "std_dev_ms": statistics.stdev(results) if len(results) > 1 else 0,
        "min_ms": min(results),
        "max_ms": max(results)
    }

def benchmark_json_parse():
    """JSON 解析性能测试"""
    results = []
    test_file = os.path.join(WORKSPACE, "30-scripts-tools", "tools_registry.json")
    
    for i in range(10):
        start = time.perf_counter()
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        end = time.perf_counter()
        results.append((end - start) * 1000)
    
    return {
        "test": "JSON Parse (tools_registry.json)",
        "iterations": 10,
        "mean_ms": statistics.mean(results),
        "median_ms": statistics.median(results),
        "std_dev_ms": statistics.stdev(results) if len(results) > 1 else 0,
        "min_ms": min(results),
        "max_ms": max(results)
    }

def benchmark_workflow_load():
    """工作流加载性能测试"""
    results = []
    test_file = os.path.join(WORKSPACE, "flow-archive", "20260318-universal-workflow-001", "workflow.json")
    
    for i in range(10):
        start = time.perf_counter()
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        end = time.perf_counter()
        results.append((end - start) * 1000)
    
    return {
        "test": "Workflow Load (workflow.json)",
        "iterations": 10,
        "mean_ms": statistics.mean(results),
        "median_ms": statistics.median(results),
        "std_dev_ms": statistics.stdev(results) if len(results) > 1 else 0,
        "min_ms": min(results),
        "max_ms": max(results)
    }

def benchmark_context_load():
    """上下文加载性能测试"""
    results = []
    core_files = [
        "SOUL.md",
        "USER.md",
        "AGENTS.md",
        "TOOLS.md",
        "HEARTBEAT.md",
        "13-memory\\MEMORY.md",
    ]
    
    for i in range(5):
        start = time.perf_counter()
        total_size = 0
        for file in core_files:
            file_path = os.path.join(WORKSPACE, file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    total_size += len(content.encode('utf-8'))
        end = time.perf_counter()
        results.append({
            "time_ms": (end - start) * 1000,
            "size_kb": total_size / 1024
        })
    
    times = [r["time_ms"] for r in results]
    sizes = [r["size_kb"] for r in results]
    
    return {
        "test": "Context Load (7 core files)",
        "iterations": 5,
        "mean_time_ms": statistics.mean(times),
        "median_time_ms": statistics.median(times),
        "mean_size_kb": statistics.mean(sizes),
        "total_size_kb": sizes[0]
    }

def benchmark_tool_execution():
    """工具执行性能测试 (模拟)"""
    results = []
    
    for i in range(5):
        start = time.perf_counter()
        # 模拟工具执行
        time.sleep(0.01)  # 10ms
        end = time.perf_counter()
        results.append((end - start) * 1000)
    
    return {
        "test": "Tool Execution (simulated)",
        "iterations": 5,
        "mean_ms": statistics.mean(results),
        "median_ms": statistics.median(results),
        "std_dev_ms": statistics.stdev(results) if len(results) > 1 else 0,
        "min_ms": min(results),
        "max_ms": max(results)
    }

def generate_report(results):
    """生成性能报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 📊 性能基准测试报告

**生成时间:** {timestamp}

## 测试概览

| 测试项 | 平均时间 | 中位数 | 标准差 | 最小值 | 最大值 |
|--------|----------|--------|--------|--------|--------|
"""
    
    for result in results:
        test_name = result.get('test', 'Unknown')
        mean_val = result.get('mean_ms', result.get('mean_time_ms', 0))
        median_val = result.get('median_ms', result.get('median_time_ms', 0))
        std_val = result.get('std_dev_ms', 0)
        min_val = result.get('min_ms', 0)
        max_val = result.get('max_ms', 0)
        
        report += f"| {test_name} | {mean_val:.2f}ms | {median_val:.2f}ms | {std_val:.2f}ms | {min_val:.2f}ms | {max_val:.2f}ms |\n"
    
    report += f"""
## 详细结果

"""
    
    for result in results:
        report += f"""### {result.get('test', 'Unknown')}

- **迭代次数:** {result.get('iterations', 0)}
- **平均值:** {result.get('mean_ms', result.get('mean_time_ms', 0)):.2f} ms
- **中位数:** {result.get('median_ms', result.get('median_time_ms', 0)):.2f} ms
- **标准差:** {result.get('std_dev_ms', 0):.2f} ms
- **最小值:** {result.get('min_ms', 0):.2f} ms
- **最大值:** {result.get('max_ms', 0):.2f} ms

"""
    
    # 性能评估
    report += """## 性能评估

"""
    
    context_load = next((r for r in results if 'Context Load' in r.get('test', '')), None)
    if context_load:
        load_time = context_load.get('mean_time_ms', 0)
        if load_time < 100:
            evaluation = "✅ 优秀 (<100ms)"
        elif load_time < 500:
            evaluation = "✅ 良好 (<500ms)"
        elif load_time < 1000:
            evaluation = "⚠️ 一般 (<1000ms)"
        else:
            evaluation = "❌ 需要优化 (>1000ms)"
        
        report += f"""- **上下文加载:** {load_time:.2f}ms - {evaluation}
"""
    
    report += f"""
## 建议

"""
    
    # 根据结果生成建议
    if context_load and context_load.get('mean_time_ms', 0) > 500:
        report += "- ⚠️ 上下文加载较慢，考虑优化文件读取或减少加载文件数\n"
    
    report += """
---

*本报告由 performance_benchmark.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Performance Benchmark v1.0 - 性能基准测试")
    print("=" * 60)
    
    # 创建报告目录
    report_dir = os.path.join(WORKSPACE, BENCHMARK_DIR)
    os.makedirs(report_dir, exist_ok=True)
    
    # 执行测试
    results = []
    
    print("\n[1/5] 文件读取测试...")
    results.append(benchmark_file_read())
    print(f"✅ 平均：{results[-1]['mean_ms']:.2f}ms")
    
    print("\n[2/5] JSON 解析测试...")
    results.append(benchmark_json_parse())
    print(f"✅ 平均：{results[-1]['mean_ms']:.2f}ms")
    
    print("\n[3/5] 工作流加载测试...")
    results.append(benchmark_workflow_load())
    print(f"✅ 平均：{results[-1]['mean_ms']:.2f}ms")
    
    print("\n[4/5] 上下文加载测试...")
    results.append(benchmark_context_load())
    print(f"✅ 平均：{results[-1]['mean_time_ms']:.2f}ms ({results[-1]['mean_size_kb']:.1f}KB)")
    
    print("\n[5/5] 工具执行测试...")
    results.append(benchmark_tool_execution())
    print(f"✅ 平均：{results[-1]['mean_ms']:.2f}ms")
    
    # 生成报告
    print("\n生成报告...")
    report = generate_report(results)
    
    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"benchmark_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存 JSON 结果
    json_path = os.path.join(report_dir, f"benchmark_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 报告已保存：{report_path}")
    print(f"✅ JSON 已保存：{json_path}")
    
    print("\n" + "=" * 60)
    print("✅ 性能基准测试完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
