import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FILE-INTEGRITY-001 File Integrity Checker
"""

import json, sys, ast
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_file(f):
    p = Path(f)
    if not p.exists(): return {"file": f, "status": "error", "reason": "Not found"}
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        ast.parse(content)
        lines = len(content.split("\n"))
        # Check for common truncation markers
        truncated = content.rstrip().endswith((":", "{", "(", ",", "+", "\\"))
        return {"file": f, "lines": lines, "truncated": truncated, "status": "PASS" if not truncated else "FAIL"}
    except SyntaxError as e: return {"file": f, "status": "FAIL", "syntax": str(e)}
    except Exception as e: return {"file": f, "status": "error", "reason": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = check_file(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: py file_integrity_001.py <file>")
