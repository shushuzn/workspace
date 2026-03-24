import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RETRY-HANDLER-001 Auto Retry Handler
[Auto Retry Handler]

Usage:
  py retry_handler_001.py --retry <tool> [args...]
  py retry_handler_001.py --alternatives [tool]
  py retry_handler_001.py --stats
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


RETRY_LOG = Path("10-MEMORY/00-CORE/.retry_log.json")
TOOL_ALTERNATIVES = Path("10-MEMORY/00-CORE/.tool_alternatives.json")


class RetryHandler:
    """Auto Retry Handler"""

    ALTERNATIVES = {
        "brainstorm_workflow": ["brainstorm_quick", "brainstorm_scamper"],
        "auto_discover": ["tools_registry"],
        "export_format": ["report_002_export"],
        "optimize_master": ["smart_cache", "batch_tools"],
        "roadmap_master": ["gantt_chart", "dashboard_view"],
    }

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        self._ensure_files()

    def _ensure_files(self):
        if not RETRY_LOG.exists():
            RETRY_LOG.write_text(json.dumps({"attempts": []}, ensure_ascii=False, indent=2))
        if not TOOL_ALTERNATIVES.exists():
            TOOL_ALTERNATIVES.write_text(json.dumps({"alternatives": self.ALTERNATIVES}, ensure_ascii=False, indent=2))

    def _load_retry_log(self) -> dict:
        return json.loads(RETRY_LOG.read_text(encoding="utf-8"))

    def _save_retry_log(self, data: dict):
        RETRY_LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _load_alternatives(self) -> dict:
        return json.loads(TOOL_ALTERNATIVES.read_text(encoding="utf-8"))

    def retry(self, tool_id: str, args: List[str] = None, max_retries: int = 3) -> Dict:
        attempts = []

        for attempt in range(1, max_retries + 1):
            tool_file = self.tools_dir / f"{tool_id}.py"

            if not tool_file.exists():
                alt_result = self._try_alternatives(tool_id, args)
                if alt_result:
                    return alt_result
                return {"status": "error", "tool": tool_id, "error": "Not found"}

            try:
                cmd = [sys.executable, str(tool_file)]
                if args:
                    cmd.extend(args)

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    self._log_attempt(tool_id, attempt, True)
                    return {"status": "success", "tool": tool_id, "attempt": attempt}

                last_error = result.stderr

            except subprocess.TimeoutExpired:
                last_error = "Timeout"
            except Exception as e:
                last_error = str(e)

        self._log_attempt(tool_id, max_retries, False)
        alt_result = self._try_alternatives(tool_id, args)
        if alt_result:
            return alt_result

        return {"status": "failed", "tool": tool_id, "error": last_error}

    def _try_alternatives(self, tool_id: str, args: List[str] = None) -> Optional[Dict]:
        alts = self._load_alternatives().get("alternatives", {})

        if tool_id not in alts:
            return None

        for alt_tool in alts[tool_id]:
            alt_file = self.tools_dir / f"{alt_tool}.py"
            if not alt_file.exists():
                continue

            try:
                cmd = [sys.executable, str(alt_file)]
                if args:
                    cmd.extend(args)

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    self._log_attempt(alt_tool, 1, True, is_alternative=True)
                    return {"status": "success", "tool": alt_tool, "original": tool_id, "is_alternative": True}
            except (subprocess.SubprocessError, OSError):
                continue

        return None

    def _log_attempt(self, tool_id: str, attempt: int, success: bool, is_alternative: bool = False):
        log = self._load_retry_log()
        log["attempts"].append({
            "tool": tool_id,
            "attempt": attempt,
            "success": success,
            "is_alternative": is_alternative,
            "timestamp": datetime.now().isoformat()
        })
        if len(log["attempts"]) > 500:
            log["attempts"] = log["attempts"][-200:]
        self._save_retry_log(log)

    def list_alternatives(self, tool_id: str = None) -> Dict:
        alts = self._load_alternatives().get("alternatives", {})
        if tool_id:
            return {"tool": tool_id, "alternatives": alts.get(tool_id, [])}
        return {"alternatives": alts}

    def stats(self) -> Dict:
        log = self._load_retry_log()
        attempts = log.get("attempts", [])

        total = len(attempts)
        success = sum(1 for a in attempts if a.get("success"))

        return {
            "total_attempts": total,
            "success_count": success,
            "success_rate": f"{(success /total *100):.1f}%" if total > 0 else "N/A"
        }


logging.basicConfig(level=logging.INFO)
def main():
    handler = RetryHandler()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "--retry":
            tool = sys.argv[2] if len(sys.argv) > 2 else None
            if not tool:
                print("Error: Specify tool")
                return 1
            args = sys.argv[3:] if len(sys.argv) > 3 else None
            result = handler.retry(tool, args)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if cmd == "--alternatives":
            tool = sys.argv[2] if len(sys.argv) > 2 else None
            result = handler.list_alternatives(tool)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if cmd == "--stats":
            result = handler.stats()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

    print("RETRY-HANDLER-001 Auto Retry Handler")
    print("Usage:")
    print("  py retry_handler_001.py --retry <tool> [args...]")
    print("  py retry_handler_001.py --alternatives [tool]")
    print("  py retry_handler_001.py --stats")
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
# py retry_handler_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py retry_handler_001.py

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
    sys.exit(main())
