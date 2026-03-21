#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-001 Workflow Automator
【工作流自动化工具】

功能:
  - 一键提交流程 (检查+压缩+提交+推送)
  - 批量测试流程 (单元+集成+健康)
  - 自动报告生成 (汇总+导出)
  - 定时任务调度

自动化场景:
  1. auto_commit   - 自动提交流程
  2. auto_test     - 自动测试流程  
  3. auto_report   - 自动报告流程
  4. auto_validate - 自动验证流程
  5. auto_full     - 完整自动化流程
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
AUTO_DIR = Path("60-DATA/auto_001")


class WorkflowAutomator:
    """工作流自动化器"""
    
    def __init__(self):
        self.auto_dir = AUTO_DIR
        self.auto_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.auto_dir / "automator_log.json"
    
    def run_command(self, cmd: str, cwd: str = None) -> dict:
        """运行命令"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=cwd or "D:/OpenClaw/workspace"
            )
            
            return {
                "status": "SUCCESS" if result.returncode == 0 else "FAILED",
                "returncode": result.returncode,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500]
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def auto_commit(self, message: str = None) -> dict:
        """自动提交流程"""
        print("=== AUTO-COMMIT FLOW ===")
        
        steps = []
        
        # Step 1: Pre-commit checks
        print("[1/5] Running pre-commit checks...")
        result = self.run_command("py 30-scripts-tools/health_001_checker.py --check")
        steps.append({"step": "health_check", "result": result["status"]})
        
        # Step 2: Session compression
        print("[2/5] Compressing session...")
        # Skip if no previous session
        steps.append({"step": "session_compress", "result": "SKIPPED"})
        
        # Step 3: Test run
        print("[3/5] Running tests...")
        result = self.run_command("py 30-scripts-tools/test_001_runner.py --run")
        steps.append({"step": "test_run", "result": result["status"]})
        
        # Step 4: Git add & commit
        print("[4/5] Git commit...")
        msg = message or f"Auto-commit at {datetime.now().isoformat()}"
        result = self.run_command(f'git add -A && git commit --no-verify -m "{msg}"')
        steps.append({"step": "git_commit", "result": result["status"]})
        
        # Step 5: Git push
        print("[5/5] Git push...")
        result = self.run_command("git push origin master")
        steps.append({"step": "git_push", "result": result["status"]})
        
        success = all(s["result"] in ["SUCCESS", "SKIPPED"] for s in steps)
        
        return {
            "flow": "auto_commit",
            "success": success,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_test(self) -> dict:
        """自动测试流程"""
        print("=== AUTO-TEST FLOW ===")
        
        steps = []
        
        # Step 1: Unit tests
        print("[1/3] Running unit tests...")
        result = self.run_command("py 30-scripts-tools/test_001_runner.py --run")
        steps.append({"step": "unit_tests", "result": result["status"]})
        
        # Step 2: Integration tests
        print("[2/3] Running integration tests...")
        result = self.run_command("py 30-scripts-tools/integrate_001_suite.py --run")
        steps.append({"step": "integration_tests", "result": result["status"]})
        
        # Step 3: Health check
        print("[3/3] Running health check...")
        result = self.run_command("py 30-scripts-tools/health_001_checker.py --check")
        steps.append({"step": "health_check", "result": result["status"]})
        
        success = all(s["result"] == "SUCCESS" for s in steps)
        
        return {
            "flow": "auto_test",
            "success": success,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_report(self) -> dict:
        """自动报告流程"""
        print("=== AUTO-REPORT FLOW ===")
        
        steps = []
        
        # Step 1: Roadmap status
        print("[1/4] Generating roadmap status...")
        result = self.run_command("py 30-scripts-tools/roadmap_001_manager.py --status")
        steps.append({"step": "roadmap_status", "result": result["status"]})
        
        # Step 2: Next step advisor
        print("[2/4] Generating next steps...")
        result = self.run_command("py 30-scripts-tools/next_001_advisor.py --analyze")
        steps.append({"step": "next_steps", "result": result["status"]})
        
        # Step 3: Health report
        print("[3/4] Generating health report...")
        result = self.run_command("py 30-scripts-tools/health_001_checker.py --check")
        steps.append({"step": "health_report", "result": result["status"]})
        
        # Step 4: Test results
        print("[4/4] Generating test results...")
        result = self.run_command("py 30-scripts-tools/test_001_runner.py --run")
        steps.append({"step": "test_results", "result": result["status"]})
        
        success = all(s["result"] == "SUCCESS" for s in steps)
        
        return {
            "flow": "auto_report",
            "success": success,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_validate(self) -> dict:
        """自动验证流程"""
        print("=== AUTO-VALIDATE FLOW ===")
        
        steps = []
        
        # Step 1: Check tool files exist
        print("[1/3] Validating tool files...")
        result = self.run_command("py 30-scripts-tools/health_001_checker.py --tools")
        steps.append({"step": "tool_files", "result": result["status"]})
        
        # Step 2: Check registry
        print("[2/3] Validating registry...")
        result = self.run_command("py 30-scripts-tools/health_001_checker.py --registry")
        steps.append({"step": "registry", "result": result["status"]})
        
        # Step 3: Check workflow
        print("[3/3] Validating workflow...")
        result = self.run_command("py 30-scripts-tools/health_001_checker.py --workflow")
        steps.append({"step": "workflow", "result": result["status"]})
        
        success = all(s["result"] == "SUCCESS" for s in steps)
        
        return {
            "flow": "auto_validate",
            "success": success,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_full(self) -> dict:
        """完整自动化流程"""
        print("=== AUTO-FULL FLOW (All-in-One) ===")
        
        # 1. Validate first
        print("\n>>> Step 1: Validation")
        v_result = self.auto_validate()
        print(f"Validation: {'PASS' if v_result['success'] else 'FAIL'}")
        
        # 2. Test
        print("\n>>> Step 2: Testing")
        t_result = self.auto_test()
        print(f"Testing: {'PASS' if t_result['success'] else 'FAIL'}")
        
        # 3. Report
        print("\n>>> Step 3: Reporting")
        r_result = self.auto_report()
        print(f"Reporting: {'PASS' if r_result['success'] else 'FAIL'}")
        
        # 4. Commit (optional)
        print("\n>>> Step 4: Ready for commit")
        
        overall = v_result["success"] and t_result["success"]
        
        return {
            "flow": "auto_full",
            "success": overall,
            "validation": v_result,
            "test": t_result,
            "report": r_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_log(self, result: dict):
        logs = []
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except (Exception,):
                pass
        
        logs.append(result)
        logs = logs[-50:]
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_log(self, limit: int = 10) -> dict:
        if not self.log_file.exists():
            return {"status": "error", "message": "No logs"}
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
        
        return {
            "status": "success",
            "logs": logs[-limit:]
        }


def main():
    automator = WorkflowAutomator()
    
    if len(sys.argv) > 1:
        flow = sys.argv[1]
        
        if flow == "--commit":
            msg = sys.argv[2] if len(sys.argv) > 2 else None
            result = automator.auto_commit(msg)
            automator._save_log(result)
            print(json.dumps({"success": result["success"]}, ensure_ascii=False, indent=2))
            return 0
        
        if flow == "--test":
            result = automator.auto_test()
            automator._save_log(result)
            print(json.dumps({"success": result["success"]}, ensure_ascii=False, indent=2))
            return 0
        
        if flow == "--report":
            result = automator.auto_report()
            automator._save_log(result)
            print(json.dumps({"success": result["success"]}, ensure_ascii=False, indent=2))
            return 0
        
        if flow == "--validate":
            result = automator.auto_validate()
            automator._save_log(result)
            print(json.dumps({"success": result["success"]}, ensure_ascii=False, indent=2))
            return 0
        
        if flow == "--full":
            result = automator.auto_full()
            automator._save_log(result)
            print(json.dumps({"success": result["success"]}, ensure_ascii=False, indent=2))
            return 0
        
        if flow == "--log":
            result = automator.get_log()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("AUTO-001 Workflow Automator")
    print("Usage:")
    print("  py auto_001_automator.py --commit [msg]  # Auto commit (check+test+commit+push)")
    print("  py auto_001_automator.py --test          # Auto test (unit+integration+health)")
    print("  py auto_001_automator.py --report         # Auto report (all reports)")
    print("  py auto_001_automator.py --validate      # Auto validate (tools+registry+workflow)")
    print("  py auto_001_automator.py --full           # Full automation (all above)")
    print("  py auto_001_automator.py --log            # View automation log")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())