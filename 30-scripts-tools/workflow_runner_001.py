import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-RUNNER-001 Workflow Chain Runner
"""

import json, sys, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

CHAINS = {
    "full-workflow": [
        {"tool": "workflow_market_001", "args": ["--list"]},
        {"tool": "nl_workflow_001", "args": ["--intent", "optimize"]},
        {"tool": "workflow_scheduler_001", "args": ["--list"]},
        {"tool": "workflow_dashboard_001", "args": []},
        {"tool": "workflow_logger_001", "args": ["--stats"]}
    ],
    "discover-optimize": [
        {"tool": "auto_discover_001", "args": ["--scan"]},
        {"tool": "tool_validator_001", "args": ["--check", "30-scripts-tools/safe_coder_001.py"]},
        {"tool": "workflow_logger_001", "args": ["--log", "discover-optimize", "0", "ok"]}
    ],
    "generate-tool": [
        {"tool": "safe_coder_001", "args": ["--gen", "cli", "NewTool"]},
        {"tool": "tool_validator_001", "args": ["--check", "NewTool.py"]},
        {"tool": "workflow_logger_001", "args": ["--log", "generate-tool", "0", "ok"]}
    ]
}

class ChainRunner:
    def run(self, chain_name):
        if chain_name not in CHAINS:
            return {"error": f"Chain not found: {chain_name}", "available": list(CHAINS.keys())}
        
        chain = CHAINS[chain_name]
        results = []
        
        for i, step in enumerate(chain):
            tool = step["tool"]
            args = step["args"]
            cmd = [sys.executable, str(TOOLS_DIR / f"{tool}.py")] + args
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
                results.append({
                    "step": i + 1,
                    "tool": tool,
                    "status": "ok" if result.returncode == 0 else "fail",
                    "output": result.stdout[:200] if result.stdout else ""
                })
            except Exception as e:
                results.append({"step": i + 1, "tool": tool, "status": "error", "error": str(e)})
        
        return {"chain": chain_name, "steps": len(chain), "results": results}
    
    def list_chains(self):
        return [{"id": k, "steps": len(v), "tools": [s["tool"] for s in v]} for k, v in CHAINS.items()]

if __name__ == "__main__":
    runner = ChainRunner()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--run":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            if not name:
                print("Usage: --run <chain_name>")
            else:
                print(json.dumps(runner.run(name), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(runner.list_chains(), ensure_ascii=False, indent=2))
    else:
        print("WORKFLOW-RUNNER-001 Chain Runner")
        print("Commands:")
        print("  --list              Show all chains")
        print("  --run <chain_name>  Run a chain")
