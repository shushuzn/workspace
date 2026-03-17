#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Performance Profiler - Analyze memory retrieval speed
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'

class MemoryProfiler:
    """Profile memory retrieval performance"""
    
    def __init__(self):
        self.results = []
    
    def profile_file_read(self, file_path: Path) -> Dict:
        """Profile file read time"""
        if not file_path.exists():
            return {'error': 'File not found'}
        
        # Warm up
        for _ in range(3):
            _ = file_path.read_text(encoding='utf-8')
        
        # Measure
        times = []
        for _ in range(10):
            start = time.perf_counter()
            content = file_path.read_text(encoding='utf-8')
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        file_size = file_path.stat().st_size
        
        return {
            'file': str(file_path.name),
            'size_kb': file_size / 1024,
            'avg_ms': round(avg_time, 2),
            'min_ms': round(min_time, 2),
            'max_ms': round(max_time, 2),
            'speed_mb_s': round(file_size / 1024 / 1024 / (avg_time / 1000), 2)
        }
    
    def profile_search(self, query: str, max_results: int = 5) -> Dict:
        """Profile memory search time"""
        from context_search import ContextSearcher
        
        searcher = ContextSearcher()
        
        # Warm up
        _ = searcher.search("test", max_results=1)
        
        # Measure
        times = []
        for _ in range(5):
            start = time.perf_counter()
            results = searcher.search(query, max_results=max_results)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        avg_time = sum(times) / len(times)
        
        return {
            'query': query,
            'results': len(results),
            'avg_ms': round(avg_time, 2),
            'min_ms': round(min(times), 2),
            'max_ms': round(max(times), 2)
        }
    
    def profile_memory_distiller(self) -> Dict:
        """Profile memory distillation time"""
        distiller_path = WORKSPACE / '30-scripts-tools' / 'memory-distiller.py'
        
        if not distiller_path.exists():
            return {'error': 'Distiller not found'}
        
        # Measure import time
        start = time.perf_counter()
        import importlib.util
        spec = importlib.util.spec_from_file_location("memory_distiller", distiller_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import_time = (time.perf_counter() - start) * 1000
        
        return {
            'tool': 'memory-distiller.py',
            'import_ms': round(import_time, 2),
            'lines': len(distiller_path.read_text(encoding='utf-8').split('\n'))
        }
    
    def run_full_profile(self) -> Dict:
        """Run complete performance profile"""
        print("\n🔍 Memory Performance Profile")
        print("=" * 80)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'file_reads': {},
            'search': {},
            'tools': {},
            'recommendations': []
        }
        
        # 1. Profile MEMORY.md read
        print("\n1️⃣  MEMORY.md Read Performance...")
        memory_file = MEMORY_DIR / 'MEMORY.md'
        if memory_file.exists():
            result = self.profile_file_read(memory_file)
            results['file_reads']['MEMORY.md'] = result
            print(f"   Size: {result['size_kb']:.1f} KB")
            print(f"   Avg Read: {result['avg_ms']:.2f} ms")
            print(f"   Speed: {result['speed_mb_s']:.2f} MB/s")
            
            if result['size_kb'] > 500:
                results['recommendations'].append(
                    "⚠️  MEMORY.md too large (>500KB). Consider splitting."
                )
        else:
            print("   ❌ Not found")
        
        # 2. Profile TODO.md read
        print("\n2️⃣  TODO.md Read Performance...")
        todo_file = WORKSPACE / 'TODO.md'
        if todo_file.exists():
            result = self.profile_file_read(todo_file)
            results['file_reads']['TODO.md'] = result
            print(f"   Size: {result['size_kb']:.1f} KB")
            print(f"   Avg Read: {result['avg_ms']:.2f} ms")
        
        # 3. Profile search performance
        print("\n3️⃣  Search Performance...")
        queries = ['memory', 'security', 'workflow']
        for query in queries:
            result = self.profile_search(query)
            results['search'][query] = result
            print(f"   Query '{query}': {result['avg_ms']:.2f} ms ({result['results']} results)")
        
        # 4. Profile tool import
        print("\n4️⃣  Tool Import Performance...")
        result = self.profile_memory_distiller()
        results['tools']['distiller'] = result
        print(f"   {result['tool']}: {result['import_ms']:.2f} ms ({result['lines']} lines)")
        
        # 5. Recommendations
        print("\n💡 Recommendations:")
        if not results['recommendations']:
            # Auto-generate based on metrics
            if results['file_reads'].get('MEMORY.md', {}).get('size_kb', 0) > 200:
                results['recommendations'].append(
                    "📦 Consider lazy-loading MEMORY.md sections"
                )
            if any(r['avg_ms'] > 100 for r in results['search'].values()):
                results['recommendations'].append(
                    "🔍 Search is slow - add caching or use memory_search tool"
                )
            results['recommendations'].append(
                "⚡ Use context_cache for frequently accessed data"
            )
            results['recommendations'].append(
                "🗂️  Split MEMORY.md by category (security/memory/tools/etc.)"
            )
        
        for rec in results['recommendations']:
            print(f"   {rec}")
        
        # Save report
        report_file = WORKSPACE / 'data' / 'memory_performance_report.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")
        
        return results

def main():
    profiler = MemoryProfiler()
    results = profiler.run_full_profile()
    
    print("\n" + "=" * 80)
    print("📊 Summary:")
    
    if 'MEMORY.md' in results['file_reads']:
        mem = results['file_reads']['MEMORY.md']
        print(f"   MEMORY.md: {mem['size_kb']:.1f} KB, {mem['avg_ms']:.2f} ms read")
    
    if results['search']:
        avg_search = sum(r['avg_ms'] for r in results['search'].values()) / len(results['search'])
        print(f"   Search: {avg_search:.2f} ms average")
    
    if results['recommendations']:
        print(f"\n🎯 Top Priority:")
        print(f"   {results['recommendations'][0]}")

if __name__ == "__main__":
    main()
