import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-SECURITY-001 Security Scanner for Tools
"""

import json, sys, re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

DANGEROUS_PATTERNS = [
    (r"os\.system\s*\(", "os.system call"),
    (r"subprocess\.call\s*\(\s*sys\.argv", "unsafe subprocess with argv"),
    (r"eval\s*\(", "eval usage"),
    (r"exec\s*\(", "exec usage"),
    (r"__import__\s*\(", "dynamic import"),
    (r"pickle\.load", "pickle deserialization"),
    (r"requests\.\w+\([^)]*timeout\s*=\s*None", "no timeout in requests"),
]

class WorkflowSecurity:
    def scan(self, tool_name=None):
        results = []
        tools = [TOOLS_DIR / f"{tool_name}.py"] if tool_name else TOOLS_DIR.glob("*_001.py")
        
        for tool in tools:
            if not tool.exists():
                continue
            
            content = tool.read_text(encoding="utf-8", errors="replace")
            issues = []
            
            for pattern, desc in DANGEROUS_PATTERNS:
                if re.search(pattern, content):
                    issues.append(desc)
            
            results.append({
                "tool": tool.stem,
                "safe": len(issues) == 0,
                "issues": issues
            })
        
        safe_count = sum(1 for r in results if r["safe"])
        return {
            "total": len(results),
            "safe": safe_count,
            "unsafe": len(results) - safe_count,
            "tools": results
        }

if __name__ == "__main__":
    scanner = WorkflowSecurity()
    tool = sys.argv[2] if len(sys.argv) > 1 and sys.argv[1] == "--check" else None
    print(json.dumps(scanner.scan(tool), ensure_ascii=False, indent=2))
