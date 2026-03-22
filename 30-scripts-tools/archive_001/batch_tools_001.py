import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BATCH-TOOLS-001 Batch Tools Executor
【批量工具执行器】

功能:
  - 批量执行多个工具
  - 并行/串行执行模式
  - 结果汇总
  - 错误处理
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


BATCH_DIR = Path("60-DATA/batch_tools_001")
BATCH_HISTORY = BATCH_DIR / "history.json"


class BatchExecutor:
    """批量工具执行器"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.dir = BATCH_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = BATCH_HISTORY
    
    def run_single(self, tool_path: str, args: list = None) -> dict:
        """运行单个工具"""
        cmd = ["py", tool_path]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd="D:/OpenClaw/workspace"
            )
            
            return {
                "tool": tool_path,
                "status": "SUCCESS" if result.returncode == 0 else "FAILED",
                "returncode": result.returncode,
                "stdout": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "tool": tool_path,
                "status": "TIMEOUT",
                "error": "Execution timeout (>120s)"
            }
        except Exception as e:
            return {
                "tool": tool_path,
                "status": "ERROR",
                "error": str(e)
            }
    
    def run_sequential(self, tools: list) -> dict:
        """串行执行"""
        results = []
        
        for tool in tools:
            print(f"Running: {tool}...")
            result = self.run_single(tool)
            results.append(result)
            
            # 失败停止
            if result["status"] == "FAILED":
                print(f"  Failed! Stopping...")
                break
        
        success_count = sum(1 for r in results if r["status"] == "SUCCESS")
        
        return {
            "mode": "sequential",
            "total": len(tools),
            "success": success_count,
            "failed": len(tools) - success_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_parallel(self, tools: list) -> dict:
        """并行执行"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.run_single, tool): tool for tool in tools}
            
            for future in as_completed(futures):
                tool = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"Completed: {tool} -> {result['status']}")
                except Exception as e:
                    results.append({
                        "tool": tool,
                        "status": "ERROR",
                        "error": str(e)
                    })
        
        success_count = sum(1 for r in results if r["status"] == "SUCCESS")
        
        return {
            "mode": "parallel",
            "total": len(tools),
            "success": success_count,
            "failed": len(tools) - success_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_batch(self, tools: list, mode: str = "sequential") -> dict:
        """批量执行"""
        if mode == "parallel":
            result = self.run_parallel(tools)
        else:
            result = self.run_sequential(tools)
        
        # 保存历史
        self._save_history(result)
        
        return result
    
    def _save_history(self, result: dict):
        history = []
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        
        history.append({
            "mode": result["mode"],
            "total": result["total"],
            "success": result["success"],
            "timestamp": result["timestamp"]
        })
        
        history = history[-20:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_history(self, limit: int = 5):
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        return history[-limit:]


# 预设工具集
TOOL_SETS = {
    "health": [
        "30-scripts-tools/health_001_checker.py",
        "30-scripts-tools/test_001_runner.py",
        "30-scripts-tools/auto_001_automator.py --validate"
    ],
    "report": [
        "30-scripts-tools/roadmap_001_manager.py --status",
        "30-scripts-tools/next_001_advisor.py --analyze",
        "30-scripts-tools/workflow_optimizer_001.py --analyze"
    ],
    "commit": [
        "30-scripts-tools/health_001_checker.py --check",
        "30-scripts-tools/test_001_runner.py --run"
    ],
    "dev": [
        "30-scripts-tools/health_001_checker.py --tools",
        "30-scripts-tools/health_001_checker.py --registry",
        "30-scripts-tools/health_001_checker.py --workflow"
    ]
}


logging.basicConfig(level=logging.INFO)
def main():
    executor = BatchExecutor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run":
            # 解析工具列表 - 直接检查是否是预设
            tools_input = sys.argv[2] if len(sys.argv) > 2 else ""
            
            mode = "sequential"
            tools = []
            
            # 检查预设
            if tools_input in TOOL_SETS:
                tools = TOOL_SETS[tools_input]
                print(f"Using preset: {tools_input}")
            elif tools_input:
                # 作为工具路径
                tools = sys.argv[2:]
                # 检查第一个是否是mode
                if tools and tools[0] in ["parallel", "sequential"]:
                    mode = tools[0]
                    tools = tools[1:]
            
            result = executor.run_batch(tools, mode)
            print(json.dumps({
                "mode": result["mode"],
                "success": result["success"],
                "total": result["total"],
                "failed": result["failed"]
            }, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--preset":
            preset = sys.argv[2] if len(sys.argv) > 2 else None
            if preset and preset in TOOL_SETS:
                print(json.dumps(TOOL_SETS[preset], ensure_ascii=False, indent=2))
            else:
                print(json.dumps(TOOL_SETS, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--history":
            history = executor.get_history()
            print(json.dumps(history, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--single":
            tool = sys.argv[2] if len(sys.argv) > 2 else ""
            if tool:
                result = executor.run_single(tool)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("BATCH-TOOLS-001 Batch Tools Executor")
    print("Usage:")
    print("  py batch_tools_001.py --run [parallel|sequential] <tools...>  # Run batch")
    print("  py batch_tools_001.py --run health                                  # Run health preset")
    print("  py batch_tools_001.py --run report                                  # Run report preset")
    print("  py batch_tools_001.py --preset [name]                               # List presets")
    print("  py batch_tools_001.py --single <tool>                              # Run single tool")
    print("  py batch_tools_001.py --history                                     # View history")
    print("\nPresets:")
    print("  health  - health checker + test runner + automator validate")
    print("  report  - roadmap + next advisor + workflow optimizer")
    print("  commit  - health check + test run")
    print("  dev     - tool/registry/workflow validation")
    return 0
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
# py batch_tools_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py batch_tools_001.py

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




if __name__ == "__main__":
    import sys
    sys.exit(main())