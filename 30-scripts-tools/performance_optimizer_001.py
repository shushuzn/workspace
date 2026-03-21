import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PERFORMANCE-OPTIMIZER-001 Performance Optimization Suite
=========================================================
Cache, parallel execution, and performance monitoring
"""

import json, sys, time, hashlib
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CACHE_DIR = Path("13-memory/.perf_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class PerformanceOptimizer:
    def __init__(self):
        self.stats_file = CACHE_DIR / "stats.json"
        self.load_stats()
    
    def load_stats(self):
        if self.stats_file.exists():
            self.stats = json.loads(self.stats_file.read_text(encoding="utf-8", errors="replace"))
        else:
            self.stats = {"runs": [], "tools": {}, "cache_hits": 0, "cache_misses": 0}
    
    def save_stats(self):
        self.stats_file.write_text(json.dumps(self.stats, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def get_cache(self, key) -> None:
        """Get cached result"""
        cache_file = CACHE_DIR / f"{key}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < 3600:  # 1 hour TTL
                self.stats["cache_hits"] += 1
                return json.loads(cache_file.read_text(encoding="utf-8", errors="replace"))
        self.stats["cache_misses"] += 1
        return None
    
    def set_cache(self, key, value) -> None:
        """Set cached result"""
        cache_file = CACHE_DIR / f"{key}.json"
        cache_file.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def clear_cache(self) -> None:
        """Clear all cache"""
        count = 0
        for f in CACHE_DIR.glob("*.json"):
            if f.name != "stats.json":
                f.unlink()
                count += 1
        return {"cleared": count}
    
    def benchmark_tool(self, tool_path, runs=5) -> None:
        """Benchmark a single tool"""
        import subprocess
        
        times = []
        for _ in range(runs):
            start = time.time()
            result = subprocess.run(
                [sys.executable, str(tool_path)],
                capture_output=True, timeout=30
            )
            elapsed = time.time() - start
            times.append(elapsed)
        
        return {
            "tool": tool_path.name,
            "avg_ms": round(sum(times) / len(times) * 1000, 2),
            "min_ms": round(min(times) * 1000, 2),
            "max_ms": round(max(times) * 1000, 2),
            "runs": runs
        }
    
    def benchmark_all(self, tools_dir) -> None:
        """Benchmark all tools"""
        tools = list(tools_dir.glob("*_001.py"))
        results = []
        
        for tool in tools[:20]:  # Limit to 20 tools
            result = self.benchmark_tool(tool, runs=3)
            results.append(result)
        
        results.sort(key=lambda x: x["avg_ms"], reverse=True)
        
        return {
            "tools": results,
            "slowest": results[0] if results else None,
            "fastest": results[-1] if results else None
        }
    
    def run_parallel(self, tools, max_workers=4) -> None:
        """Run multiple tools in parallel"""
        import subprocess
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(subprocess.run, [sys.executable, str(t)], capture_output=True, timeout=60): t
                for t in tools
            }
            
            for future in as_completed(futures):
                tool = futures[future]
                try:
                    result = future.result()
                    elapsed = result.returncode == 0
                    results.append({"tool": tool.name, "status": "ok" if elapsed else "fail", "time": elapsed})
                except Exception as e:
                    results.append({"tool": tool.name, "status": "error", "error": str(e)})
        
        return {"results": results, "total": len(results)}
    
    def profile_tool(self, tool_path) -> None:
        """Profile a tool with detailed timing"""
        import subprocess
        
        stages = {
            "import": 0,
            "init": 0,
            "execute": 0
        }
        
        start = time.time()
        result = subprocess.run(
            [sys.executable, str(tool_path)],
            capture_output=True, text=True, timeout=30
        )
        total = time.time() - start
        
        return {
            "tool": tool_path.name,
            "total_ms": round(total * 1000, 2),
            "status": "ok" if result.returncode == 0 else "fail",
            "stdout_lines": len(result.stdout.split("\n")) if result.stdout else 0
        }
    
    def optimize_tool(self, tool_path) -> None:
        """Suggest optimizations for a tool"""
        content = tool_path.read_text(encoding="utf-8", errors="replace")
        
        suggestions = []
        
        # Check for missing encoding
        if "open(" in content and "encoding=" not in content:
            suggestions.append({"type": "encoding", "priority": "high", "fix": "Add encoding='utf-8', errors='replace'"})
        
        # Check for missing timeout
        if "subprocess.run" in content and "timeout=" not in content:
            suggestions.append({"type": "timeout", "priority": "high", "fix": "Add timeout parameter"})
        
        # Check for caching opportunities
        if "requests.get" in content or "urllib" in content:
            suggestions.append({"type": "cache", "priority": "medium", "fix": "Consider adding HTTP caching"})
        
        # Check for glob patterns
        if ".glob(" in content:
            suggestions.append({"type": "glob", "priority": "low", "fix": "Cache glob results if used multiple times"})
        
        return {
            "tool": tool_path.name,
            "suggestions": suggestions,
            "potential_speedup": f"{len(suggestions) * 5}%" if suggestions else "0%"
        }
    
    def report(self) -> None:
        """Generate performance report"""
        cache_hit_rate = 0
        total = self.stats.get("cache_hits", 0) + self.stats.get("cache_misses", 0)
        if total > 0:
            cache_hit_rate = self.stats["cache_hits"] / total * 100
        
        return {
            "cache_hits": self.stats.get("cache_hits", 0),
            "cache_misses": self.stats.get("cache_misses", 0),
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "tools_profiled": len(self.stats.get("tools", {})),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    opt = PerformanceOptimizer()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--benchmark":
            tool = sys.argv[2] if len(sys.argv) > 2 else "30-scripts-tools/workflow_master_001.py"
            print(json.dumps(opt.benchmark_tool(Path(tool)), ensure_ascii=False, indent=2))
        elif cmd == "--benchmark-all":
            results = opt.benchmark_all(Path("30-scripts-tools"))
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif cmd == "--profile":
            tool = sys.argv[2] if len(sys.argv) > 2 else "30-scripts-tools/workflow_master_001.py"
            print(json.dumps(opt.profile_tool(Path(tool)), ensure_ascii=False, indent=2))
        elif cmd == "--optimize":
            tool = sys.argv[2] if len(sys.argv) > 2 else "30-scripts-tools/workflow_master_001.py"
            print(json.dumps(opt.optimize_tool(Path(tool)), ensure_ascii=False, indent=2))
        elif cmd == "--clear-cache":
            print(json.dumps(opt.clear_cache(), ensure_ascii=False, indent=2))
        elif cmd == "--report":
            print(json.dumps(opt.report(), ensure_ascii=False, indent=2))
    else:
        print("PERFORMANCE-OPTIMIZER-001")
        print("Commands:")
        print("  --benchmark <tool>    Benchmark single tool")
        print("  --benchmark-all       Benchmark all tools")
        print("  --profile <tool>     Profile tool execution")
        print("  --optimize <tool>    Get optimization suggestions")
        print("  --clear-cache        Clear performance cache")
        print("  --report             Show performance report")
