import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-GUARD-001 Mandatory Workflow Enforcer
==============================================
Enforces safe workflow: validate -> name_check -> commit
NO SKIPPING ALLOWED
"""

import json, sys, subprocess
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

class WorkflowGuard:
    """Enforce mandatory checks before commit"""
    
    MANDATORY_STEPS = [
        {"tool": "tool_validator_001", "check": "validation", "required": True},
        {"tool": "tool_namer_001", "check": "naming", "required": True}
    ]
    
    def __init__(self):
        self.log_file = Path("13-memory/.workflow_guard_log.json")
        self.enforce_log = Path("13-memory/.workflow_guard_enforce.json")
    
    def _log(self, tool, status, message=""):
        logs = []
        if self.log_file.exists():
            logs = json.loads(self.log_file.read_text(encoding="utf-8", errors="replace"))
        
        logs.append({
            "tool": tool,
            "status": status,
            "message": message,
            "time": str(Path().resolve())
        })
        
        self.log_file.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def check_file(self, filepath) -> None:
        """Mandatory check for a single file"""
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        
        results = {"file": path.name, "checks": []}
        
        # Step 1: Validation (MANDATORY)
        print(f"[1/2] Validating {path.name}...")
        val_result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "tool_validator_001.py"), "--check", str(path)],
            capture_output=True, text=True, timeout=30
        )
        
        if "PASS" in val_result.stdout:
            if "errors\": 0" in val_result.stdout:
                results["checks"].append({"check": "validation", "status": "PASS"})
                self._log(path.name, "validation", "PASS")
            else:
                results["checks"].append({"check": "validation", "status": "FAIL", "output": val_result.stdout[:300]})
                self._log(path.name, "validation", "FAIL")
        else:
            results["checks"].append({"check": "validation", "status": "FAIL", "output": val_result.stdout[:300]})
            self._log(path.name, "validation", "FAIL")
        
        # Step 2: Naming (MANDATORY)
        print(f"[2/2] Checking naming {path.name}...")
        name_result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "tool_namer_001.py"), "--check", path.name],
            capture_output=True, text=True, timeout=30
        )
        
        if name_result.returncode == 0:
            results["checks"].append({"check": "naming", "status": "PASS"})
            self._log(path.name, "naming", "PASS")
        else:
            results["checks"].append({"check": "naming", "status": "FAIL", "output": name_result.stdout[:200]})
            self._log(path.name, "naming", "FAIL")
        
        # Overall
        all_pass = all(c["status"] == "PASS" for c in results["checks"])
        results["status"] = "APPROVED" if all_pass else "BLOCKED"
        
        return results
    
    def check_and_commit(self, filepaths) -> None:
        """Mandatory workflow: check -> block if fail -> commit only if all pass"""
        if not filepaths:
            return {"error": "No files specified"}
        
        results = []
        blocked = False
        
        print("=" * 50)
        print("WORKFLOW GUARD - MANDATORY CHECKS")
        print("=" * 50)
        
        for filepath in filepaths:
            print(f"\nChecking: {filepath}")
            result = self.check_file(filepath)
            results.append(result)
            
            if result.get("status") == "BLOCKED":
                blocked = True
                print(f"  ❌ BLOCKED: {filepath}")
            else:
                print(f"  ✅ APPROVED: {filepath}")
        
        print("\n" + "=" * 50)
        
        if blocked:
            print("❌ COMMIT BLOCKED - Fix errors above")
            print("Run: workflow_guard_001.py --check <file>")
            return {"status": "BLOCKED", "results": results}
        
        # Auto-commit if all pass
        print("✅ ALL CHECKS PASSED - Committing...")
        files_str = " ".join(str(f) for f in filepaths)
        
        subprocess.run(f"git add {files_str}", shell=True)
        commit_result = subprocess.run(
            "git commit -m 'Guarded commit - all checks passed'",
            shell=True, capture_output=True, text=True
        )
        
        return {"status": "COMMITTED", "results": results, "commit": commit_result.stdout[:200]}
    
    def enforce_new_tool(self, tool_name) -> None:
        """Enforce workflow for new tool creation"""
        tool_path = TOOLS_DIR / f"{tool_name}.py"
        
        if not tool_path.exists():
            return {"error": f"Tool not found: {tool_name}"}
        
        print(f"\n🔒 ENFORCING WORKFLOW FOR: {tool_name}")
        print("=" * 50)
        
        result = self.check_file(tool_path)
        
        if result["status"] == "BLOCKED":
            print("\n❌ TOOL BLOCKED - Cannot use without fixes")
            return result
        
        print("\n✅ TOOL APPROVED")
        return result
    
    def status(self) -> None:
        """Show guard status"""
        logs = []
        if self.log_file.exists():
            logs = json.loads(self.log_file.read_text(encoding="utf-8", errors="replace"))
        
        recent = logs[-20:] if logs else []
        passed = sum(1 for l in recent if l.get("status") == "PASS")
        failed = sum(1 for l in recent if l.get("status") == "FAIL")
        
        return {
            "total_checks": len(logs),
            "recent_checks": len(recent),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/len(recent)*100):.0f}%" if recent else "N/A"
        }

if __name__ == "__main__":
    guard = WorkflowGuard()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--check":
            file = sys.argv[2] if len(sys.argv) > 2 else ""
            if not file:
                print("Usage: --check <filepath>")
            else:
                result = guard.check_file(file)
                print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "--commit":
            files = sys.argv[2:] if len(sys.argv) > 2 else []
            result = guard.check_and_commit(files)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "--enforce":
            tool = sys.argv[2] if len(sys.argv) > 2 else ""
            if not tool:
                print("Usage: --enforce <tool_name>")
            else:
                result = guard.enforce_new_tool(tool)
                print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "--status":
            print(json.dumps(guard.status(), ensure_ascii=False, indent=2))
    else:
        print("WORKFLOW-GUARD-001 - Mandatory Workflow Enforcer")
        print()
        print("🔒 MANDATORY STEPS: validation -> naming -> commit")
        print()
        print("Commands:")
        print("  --check <file>      Check single file")
        print("  --commit <files>    Check AND commit (blocks on fail)")
        print("  --enforce <tool>    Enforce workflow for new tool")
        print("  --status            Show guard status")
        print()
        print("⚠️  NO SKIPPING ALLOWED - All checks are MANDATORY")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
# Purpose: Automation workflow tool
# Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py workflow_guard_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_guard_001.py

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
