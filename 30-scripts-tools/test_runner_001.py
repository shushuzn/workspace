import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST-001 Test Runner
【自动化测试运行器】

功能:
  - 批量运行测试
  - 测试结果汇总
  - 失败重试
  - 报告生成

依赖: pytest (optional)
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
TEST_DIR = Path("60-DATA/test_001")
CONFIG_FILE = Path("30-scripts-tools/test_001_config.json")


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_dir = TEST_DIR
        self.config = self._load_config()
        
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_file = self.test_dir / "test_results.json"
        self.test_map = self._load_test_map()
    
    def _load_config(self) -> dict:
        default = {
            "max_retries": 2,
            "timeout": 30,
            "parallel": False
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (Exception,):
                return default
        return default
    
    def _load_test_map(self) -> dict:
        """加载测试映射"""
        return {
            "sa-029-ai-signal": "30-scripts-tools/sa_029_ai_signal.py --analyze AAPL",
            "sa-030-sentiment": "30-scripts-tools/sa_030_sentiment.py --analyze AAPL",
            "sa-031-report": "30-scripts-tools/sa_031_report.py --generate AAPL daily",
            "sa-032-strategy": "30-scripts-tools/sa_032_strategy.py --recommend",
            "roadmap-001-manager": "30-scripts-tools/roadmap_001_manager.py --status",
            "next-001-advisor": "30-scripts-tools/next_001_advisor.py --quick"
        }
    
    def run_test(self, tool_id: str) -> dict:
        """运行单个测试"""
        if tool_id not in self.test_map:
            return {"status": "error", "message": f"Unknown tool: {tool_id}"}
        
        cmd = self.test_map[tool_id]
        
        try:
            # Windows: use py to run Python scripts
            if cmd.startswith("30-scripts-tools/"):
                cmd = "py " + cmd
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.get("timeout", 30),
                cwd=str(Path("D:/OpenClaw/workspace"))
            )
            
            success = result.returncode == 0
            
            return {
                "tool_id": tool_id,
                "command": cmd,
                "status": "PASS" if success else "FAIL",
                "returncode": result.returncode,
                "stdout": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "tool_id": tool_id,
                "command": cmd,
                "status": "TIMEOUT",
                "error": "Test timed out",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "tool_id": tool_id,
                "command": cmd,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all(self) -> dict:
        """运行所有测试"""
        results = []
        
        for tool_id in self.test_map:
            result = self.run_test(tool_id)
            results.append({
                "tool_id": tool_id,
                "status": result.get("status"),
                "timestamp": result.get("timestamp")
            })
        
        # 汇总
        passed = sum(1 for r in results if r.get("status") == "PASS")
        failed = sum(1 for r in results if r.get("status") in ["FAIL", "ERROR"])
        timeout = sum(1 for r in results if r.get("status") == "TIMEOUT")
        
        summary = {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "timeout": timeout,
            "pass_rate": round(passed / len(results) * 100, 1) if results else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存
        self._save_results(results, summary)
        
        return {
            "summary": summary,
            "results": results
        }
    
    def _save_results(self, results: list, summary: dict):
        """保存结果"""
        data = {
            "summary": summary,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_results(self) -> dict:
        """获取上次测试结果"""
        if not self.results_file.exists():
            return {"status": "error", "message": "No test results"}
        
        with open(self.results_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_tools(self) -> dict:
        """列出可测试的工具"""
        return {
            "status": "success",
            "count": len(self.test_map),
            "tools": list(self.test_map.keys())
        }
    
    def add_test(self, tool_id: str, command: str):
        """添加测试"""
        self.test_map[tool_id] = command
        return {"status": "success", "message": f"Added test for {tool_id}"}


logging.basicConfig(level=logging.INFO)
def main():
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run":
            result = runner.run_all()
            print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--test":
            tool_id = sys.argv[2] if len(sys.argv) > 2 else "sa-029-ai-signal"
            result = runner.run_test(tool_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--list":
            result = runner.list_tools()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--results":
            result = runner.get_results()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("TEST-001 Test Runner")
    print("Usage:")
    print("  py test_001_runner.py --run        # Run all tests")
    print("  py test_001_runner.py --test <id> # Run single test")
    print("  py test_001_runner.py --list      # List testable tools")
    print("  py test_001_runner.py --results   # Get last results")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())