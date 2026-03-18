#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory System Benchmark - 记忆系统性能测试

Tests:
1. Tag search performance
2. Index generation performance
3. Session compression performance
4. Full-text search performance

Usage:
    py memory_benchmark.py
"""

import subprocess
import time
import json
import sys
import codecs
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_result(test_name, time_ms, target_ms, status):
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{symbol} {test_name}")
    print(f"   Time: {time_ms:.2f}ms (Target: <{target_ms}ms)")
    print(f"   Status: {status}")
    print()

def run_benchmark(name, func, target_ms):
    """Run a benchmark and report results"""
    # Warm up
    for _ in range(3):
        func()
    
    # Measure
    times = []
    for _ in range(5):
        start = time.time()
        func()
        end = time.time()
        times.append((end - start) * 1000)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    status = "PASS" if avg_time < target_ms else "FAIL"
    
    print_result(name, avg_time, target_ms, status)
    print(f"   Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
    
    return {
        "name": name,
        "avg_ms": round(avg_time, 2),
        "min_ms": round(min_time, 2),
        "max_ms": round(max_time, 2),
        "target_ms": target_ms,
        "status": status
    }

# ===== Benchmark Tests =====

def test_tag_search():
    """Test memory_tag_search.py performance"""
    result = subprocess.run(
        ["py", "30-scripts-tools\\memory_tag_search.py", "--tag", "critical"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.returncode

def test_index_generation():
    """Test memory_index_generator.py performance"""
    result = subprocess.run(
        ["py", "30-scripts-tools\\memory_index_generator.py"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.returncode

def test_session_compression():
    """Test post_session_compress.py performance (dry run)"""
    # Don't actually run compression, just measure import time
    code = """
import sys
sys.path.insert(0, '30-scripts-tools')
import post_session_compress
"""
    result = subprocess.run(
        ["py", "-c", code],
        capture_output=True,
        text=True
    )
    return result.returncode

def test_full_search():
    """Test full-text search performance"""
    code = """
import sys
sys.path.insert(0, '30-scripts-tools')
from memory_tag_search import search_memories
results = search_memories(keyword="critic")
print(len(results))
"""
    result = subprocess.run(
        ["py", "-c", code],
        capture_output=True,
        text=True
    )
    return result.returncode

def test_memory_load():
    """Test MEMORY.md load and parse time"""
    code = """
import json
from pathlib import Path
memory_path = Path("13-memory/MEMORY.md")
content = memory_path.read_text(encoding='utf-8')
# Parse sections
sections = content.split("## ")
print(len(sections))
"""
    result = subprocess.run(
        ["py", "-c", code],
        capture_output=True,
        text=True
    )
    return result.returncode

# ===== Main =====

def main():
    print_header("🏁 MEMORY SYSTEM BENCHMARK")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {subprocess.check_output(['py', '--version'], text=True).strip()}")
    print()
    
    results = []
    
    # Test 1: Tag Search
    print_header("TEST 1: Tag Search Performance")
    result = run_benchmark(
        "Tag Search (--tag critical)",
        test_tag_search,
        target_ms=1000  # <1 second
    )
    results.append(result)
    
    # Test 2: Index Generation
    print_header("TEST 2: Index Generation Performance")
    result = run_benchmark(
        "Index Generation",
        test_index_generation,
        target_ms=5000  # <5 seconds
    )
    results.append(result)
    
    # Test 3: Session Compression
    print_header("TEST 3: Session Compression Performance")
    result = run_benchmark(
        "Session Compression (import)",
        test_session_compression,
        target_ms=2000  # <2 seconds
    )
    results.append(result)
    
    # Test 4: Full-Text Search
    print_header("TEST 4: Full-Text Search Performance")
    result = run_benchmark(
        "Full-Text Search (keyword='critic')",
        test_full_search,
        target_ms=1000  # <1 second
    )
    results.append(result)
    
    # Test 5: Memory Load
    print_header("TEST 5: Memory Load & Parse Performance")
    result = run_benchmark(
        "MEMORY.md Load & Parse",
        test_memory_load,
        target_ms=500  # <0.5 seconds
    )
    results.append(result)
    
    # Summary
    print_header("📊 BENCHMARK SUMMARY")
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print()
    
    for r in results:
        symbol = "✅" if r["status"] == "PASS" else "❌"
        print(f"{symbol} {r['name']}: {r['avg_ms']:.2f}ms (target: <{r['target_ms']}ms)")
    
    print()
    
    # Performance rating
    avg_all = sum(r["avg_ms"] for r in results) / len(results)
    
    if avg_all < 1000:
        rating = "EXCELLENT"
        color = Colors.GREEN
    elif avg_all < 3000:
        rating = "GOOD"
        color = Colors.YELLOW
    else:
        rating = "NEEDS_OPTIMIZATION"
        color = Colors.RED
    
    print(f"{color}Overall Performance: {rating}{Colors.RESET}")
    print(f"Average Time: {avg_all:.2f}ms")
    
    # Save results
    benchmark_data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "passed": passed,
            "total": total,
            "avg_ms": round(avg_all, 2),
            "rating": rating
        }
    }
    
    output_file = Path("30-scripts-tools/benchmark_results.json")
    output_file.write_text(json.dumps(benchmark_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nResults saved to: {output_file}")
    
    # Return exit code
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
