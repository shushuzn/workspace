#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BENCHMARK-001 Performance Benchmark Tool
Benchmarks workflow and tool execution times
"""
import json, sys, time, subprocess
from pathlib import Path
from datetime import datetime

BENCHMARK_FILE = Path("13-memory/.benchmark_results.json")

def benchmark_tool(tool_path, runs=5):
    """Benchmark a single tool"""
    times = []
    for _ in range(runs):
        start = time.time()
        try:
            result = subprocess.run(
                ["python", str(tool_path)],
                capture_output=True, timeout=30
            )
            elapsed = time.time() - start
            times.append(elapsed)
        except:
            times.append(999)
    return {
        "min": min(times) if times else 999,
        "max": max(times) if times else 999,
        "avg": sum(times) / len(times) if times else 999,
        "runs": runs
    }

def run_benchmark():
    """Run full benchmark suite"""
    tools_to_test = [
        "30-scripts-tools/auto_discover_001.py",
        "30-scripts-tools/workflow_health_001.py",
        "30-scripts-tools/workflow_diagnosis_001.py",
        "30-scripts-tools/multi_agent_router_001.py",
        "30-scripts-tools/multi_agent_viz_001.py"
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {}
    }
    
    print("\n[BENCHMARK-001 Performance Benchmark]")
    print("=" * 50)
    
    for tool in tools_to_test:
        tool_path = Path(tool)
        if tool_path.exists():
            print(f"Benchmarking: {tool_path.name}...", end=" ")
            result = benchmark_tool(tool_path)
            results["benchmarks"][tool_path.name] = result
            print(f"Avg: {result['avg']*1000:.1f}ms")
        else:
            print(f"Skip: {tool_path.name} (not found)")
    
    # Save results
    BENCHMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print("\n[TOP 3 FASTEST TOOLS]")
    sorted_tools = sorted(results["benchmarks"].items(), key=lambda x: x[1]["avg"])
    for i, (name, data) in enumerate(sorted_tools[:3], 1):
        print(f"  {i}. {name}: {data['avg']*1000:.1f}ms")
    
    print(f"\n[Results saved to: {BENCHMARK_FILE}]")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    run_benchmark()
