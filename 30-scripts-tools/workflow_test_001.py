import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-TEST-001 Test All Workflow Tools
"""

import json, sys, subprocess
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

class WorkflowTest:
    def test_all(self):
        results = []
        
        # Test core workflow tools
        core_tools = [
            "workflow_master_001",
            "workflow_diagnosis_001",
            "workflow_monitor_001",
            "workflow_report_001",
            "workflow_logger_001",
            "workflow_runner_001",
            "workflow_dashboard_001",
            "workflow_optimizer_001",
            "workflow_backup_001",
            "workflow_deploy_001",
            "workflow_alert_001",
            "workflow_schedule_001"
        ]
        
        for tool in core_tools:
            path = TOOLS_DIR / f"{tool}.py"
            if not path.exists():
                results.append({"tool": tool, "status": "missing"})
                continue
            
            try:
                result = subprocess.run(
                    [sys.executable, str(path)],
                    capture_output=True, text=True, timeout=30
                )
                status = "ok" if result.returncode == 0 else "fail"
                results.append({"tool": tool, "status": status})
            except Exception as e:
                results.append({"tool": tool, "status": "error", "error": str(e)})
        
        ok = sum(1 for r in results if r.get("status") == "ok")
        return {"total": len(results), "ok": ok, "fail": len(results) - ok, "results": results}

if __name__ == "__main__":
    test = WorkflowTest()
    result = test.test_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))
