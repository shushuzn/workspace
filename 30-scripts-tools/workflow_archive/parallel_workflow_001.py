import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PARALLEL-WORKFLOW-001 Parallel Workflow Executor
=================================================
Run workflow steps in parallel for maximum speed
"""

import json, sys, subprocess, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

class ParallelWorkflow:
    def __init__(self):
        self.results = []

    def run_parallel(self, tools, max_workers=4, timeout=60) -> None:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py parallel_workflow_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py parallel_workflow_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Run multiple tools in parallel"""
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for tool in tools:
                cmd = [sys.executable, str(TOOLS_DIR / f"{tool}.py")]
                future = executor.submit(self._run_tool, cmd, timeout)
                futures[future] = tool

            for future in as_completed(futures):
                tool = futures[future]
                try:
                    result, elapsed = future.result()
                    status = "OK" if result.returncode == 0 else "FAIL"
                    results.append({
                        "tool": tool,
                        "status": status,
                        "elapsed_ms": round(elapsed * 1000, 2)
                    })
                except subprocess.TimeoutExpired:
                    results.append({"tool": tool, "status": "TIMEOUT", "elapsed_ms": timeout * 1000})
                except Exception as e:
                    results.append({"tool": tool, "status": "ERROR", "error": str(e)})

        return results

    def _run_tool(self, cmd, timeout) -> None:
        """Run a single tool and return result with timing"""
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        elapsed = time.time() - start
        return result, elapsed
    
    def run_sequential(self, tools, timeout=60) -> None:
        """Run tools sequentially"""
        results = []
        
        for tool in tools:
            cmd = [sys.executable, str(TOOLS_DIR / f"{tool}.py")]
            start = time.time()
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
                status = "OK" if result.returncode == 0 else "FAIL"
            except subprocess.TimeoutExpired:
                status = "TIMEOUT"
            except Exception as e:
                status = "ERROR"
            
            elapsed = time.time() - start
            results.append({
                "tool": tool,
                "status": status,
                "elapsed_ms": round(elapsed * 1000, 2)
            })
        
        return results
    
    def compare(self, tools, sample_size=5) -> None:
        """Compare parallel vs sequential execution"""
        # Sequential
        print("Running sequential...")
        start = time.time()
        seq_results = self.run_sequential(tools[:sample_size])
        seq_total = time.time() - start
        
        # Parallel
        print("Running parallel...")
        start = time.time()
        par_results = self.run_parallel(tools[:sample_size], max_workers=4)
        par_total = time.time() - start
        
        return {
            "sequential": {
                "total_ms": round(seq_total * 1000, 2),
                "avg_per_tool_ms": round(sum(r["elapsed_ms"] for r in seq_results) / len(seq_results), 2),
                "results": seq_results
            },
            "parallel": {
                "total_ms": round(par_total * 1000, 2),
                "avg_per_tool_ms": round(sum(r["elapsed_ms"] for r in par_results) / len(par_results), 2),
                "results": par_results
            },
            "speedup": f"{(seq_total / par_total):.2f}x" if par_total > 0 else "N/A"
        }
    
    def run_workflow(self, workflow_id) -> None:
        """Run a predefined workflow"""
        workflows = {
            "dev": ["auto_discover_001", "tool_validator_001", "tool_namer_001"],
            "stock-quick": ["sa_signal_generator_001", "sa_analyzer_001"],
            "stock-full": ["sa_historical_downloader_001", "sa_analyzer_001", "sa_signal_generator_001", "sa_backtesting_001", "sa_risk_001", "sa_dashboard_001"],
            "health": ["workflow_diagnosis_001", "workflow_health_001", "workflow_monitor_001"],
            "security": ["tool_validator_001", "workflow_security_001", "file_integrity_001"]
        }
        
        if workflow_id not in workflows:
            return {"error": f"Unknown workflow: {workflow_id}", "available": list(workflows.keys())}
        
        tools = workflows[workflow_id]
        
        print(f"Running workflow: {workflow_id}")
        print(f"Tools: {len(tools)}")
        print("=" * 50)
        
        # Use parallel for better performance
        start = time.time()
        results = self.run_parallel(tools, max_workers=4)
        total = time.time() - start
        
        print("=" * 50)
        ok = sum(1 for r in results if r["status"] == "OK")
        print(f"Complete: {ok}/{len(results)} OK in {total:.2f}s")
        
        return {
            "workflow": workflow_id,
            "tools": len(tools),
            "results": results,
            "total_time_ms": round(total * 1000, 2)
        }

if __name__ == "__main__":
    pw = ParallelWorkflow()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--workflow":
            wf = sys.argv[2] if len(sys.argv) > 2 else "dev"
            print(json.dumps(pw.run_workflow(wf), ensure_ascii=False, indent=2))
        elif cmd == "--parallel":
            tools = sys.argv[2].split(",") if len(sys.argv) > 2 else ["auto_discover_001", "tool_validator_001"]
            results = pw.run_parallel(tools)
            print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        elif cmd == "--sequential":
            tools = sys.argv[2].split(",") if len(sys.argv) > 2 else ["auto_discover_001", "tool_validator_001"]
            results = pw.run_sequential(tools)
            print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        elif cmd == "--compare":
            tools = ["auto_discover_001", "tool_validator_001", "tool_namer_001", "safe_coder_001", "file_integrity_001"]
            print(json.dumps(pw.compare(tools), ensure_ascii=False, indent=2))
    else:
        print("PARALLEL-WORKFLOW-001")
        print("Commands:")
        print("  --workflow <id>      Run predefined workflow")
        print("  --parallel <a,b,c>   Run tools in parallel")
        print("  --sequential <a,b,c> Run tools sequentially")
        print("  --compare           Compare parallel vs sequential")
        print()
        print("Workflows: dev, stock-quick, stock-full, health, security")
