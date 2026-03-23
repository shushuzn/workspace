import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HEALTH-001 System Health Checker
【系统健康检查器】

功能:
  - 检查工具完整性
  - 验证注册状态
  - 测试连接
  - 生成健康报告
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# 配置
HEALTH_DIR = Path("60-DATA/health_001")
REGISTRY_FILE = Path("30-scripts-tools/tools_registry.json")


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.health_dir = HEALTH_DIR
        self.registry_file = REGISTRY_FILE

        self.health_dir.mkdir(parents=True, exist_ok=True)

        self.report_file = self.health_dir / "health_report.json"
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if not self.registry_file.exists():
            return {}

        with open(self.registry_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_tools(self) -> dict:
        """检查工具文件是否存在"""
        tools = self.registry.get("tools", {})

        results = []
        missing = []
        exists = []

        for tool_id, tool_info in tools.items():
            file_path = Path(tool_info.get("file_path", ""))

            if file_path.exists():
                exists.append(tool_id)
            else:
                missing.append(tool_id)
                results.append({
                    "tool_id": tool_id,
                    "status": "MISSING",
                    "file": str(file_path)
                })

        return {
            "total": len(tools),
            "exists": len(exists),
            "missing": len(missing),
            "missing_tools": missing
        }

    def check_registry(self) -> dict:
        """检查注册表状态"""
        tools = self.registry.get("tools", {})

        active = sum(1 for t in tools.values() if t.get("status") == "active")
        inactive = sum(1 for t in tools.values() if t.get("status") != "active")

        # 检查必填字段
        invalid = []
        for tool_id, tool_info in tools.items():
            required = ["tool_id", "name", "file_path", "category"]
            missing = [f for f in required if f not in tool_info]

            if missing:
                invalid.append({
                    "tool_id": tool_id,
                    "missing_fields": missing
                })

        return {
            "total_tools": len(tools),
            "active": active,
            "inactive": inactive,
            "invalid": len(invalid),
            "invalid_tools": invalid
        }

    def check_workflow(self) -> dict:
        """检查工作流文件"""
        workflow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
        roadmap_file = Path("flow-archive/stock-analysis-roadmap.json")

        checks = []

        if workflow_file.exists():
            checks.append({"file": "workflow.json", "status": "OK"})
        else:
            checks.append({"file": "workflow.json", "status": "MISSING"})

        if roadmap_file.exists():
            checks.append({"file": "roadmap.json", "status": "OK"})
        else:
            checks.append({"file": "roadmap.json", "status": "MISSING"})

        return {
            "files": checks,
            "all_present": all(c["status"] == "OK" for c in checks)
        }

    def check_protection(self) -> dict:
        """检查保护系统"""
        protection_files = [
            "30-scripts-tools/copaw_entry.py",
            "30-scripts-tools/tool_executor.py",
            "30-scripts-tools/auto_protection_layer.py",
            ".STOP_FLAG",
            ".lockdown_active"
        ]

        results = []

        for f in protection_files:
            p = Path(f)
            results.append({
                "file": f,
                "exists": p.exists(),
                "status": "OK" if p.exists() else "MISSING"
            })

        return {
            "files": results,
            "all_present": all(r["exists"] for r in results)
        }

    def run_full_check(self) -> dict:
        """运行完整健康检查"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "tools": self.check_tools(),
            "registry": self.check_registry(),
            "workflow": self.check_workflow(),
            "protection": self.check_protection()
        }

        # 计算总体健康分
        scores = []

        # 工具存在性
        tool_score = report["tools"]["exists"] / report["tools"]["total"] * 100 if report["tools"]["total"] > 0 else 0
        scores.append(("tools", tool_score))

        # 注册有效性
        reg_score = (1 - report["registry"]["invalid"] / report["registry"]["total_tools"]) * 100 if report["registry"]["total_tools"] > 0 else 0
        scores.append(("registry", reg_score))

        # 工作流
        workflow_score = 100 if report["workflow"]["all_present"] else 50
        scores.append(("workflow", workflow_score))

        # 保护系统
        protection_score = 100 if report["protection"]["all_present"] else 0
        scores.append(("protection", protection_score))

        avg_score = sum(s[1] for s in scores) / len(scores)

        report["health_score"] = round(avg_score, 1)
        report["score_breakdown"] = dict(scores)

        if avg_score >= 90:
            report["status"] = "HEALTHY"
        elif avg_score >= 70:
            report["status"] = "WARNING"
        else:
            report["status"] = "CRITICAL"

        # 保存
        self._save_report(report)

        return report

    def _save_report(self, report: dict):
        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def get_last_report(self) -> dict:
        if not self.report_file.exists():
            return {"status": "error", "message": "No report"}

        with open(self.report_file, "r", encoding="utf-8") as f:
            return json.load(f)


logging.basicConfig(level=logging.INFO)
def main():
    checker = HealthChecker()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            result = checker.run_full_check()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--tools":
            result = checker.check_tools()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--registry":
            result = checker.check_registry()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--workflow":
            result = checker.check_workflow()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--protection":
            result = checker.check_protection()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--report":
            result = checker.get_last_report()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

    print("HEALTH-001 System Health Checker")
    print("Usage:")
    print("  py health_001_checker.py --check       # Full health check")
    print("  py health_001_checker.py --tools       # Check tool files")
    print("  py health_001_checker.py --registry    # Check registry")
    print("  py health_001_checker.py --workflow    # Check workflow files")
    print("  py health_001_checker.py --protection  # Check protection system")
    print("  py health_001_checker.py --report      # Get last report")
    return 0
# ==============================================================================
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# Purpose: 系统健康检查工具
# Data Flow: system_check -> health_report -> recommendations
# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py health_checker_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py health_checker_001.py

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