#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TOOL-VALIDATOR-001 Tool Validator
[Tool Validator]
"""

import json
import sys
import ast
import re
from pathlib import Path
from typing import Dict, List

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


COMMON_PATTERNS = {
    "print_chinese": {
        "pattern": r'print\s*\(\s*["\'].*[\u4e00-\u9fff]',
        "severity": "warning",
        "message": "Direct Chinese in print() may cause encoding issues"
    },
    "except_no_detail": {
        "pattern": r'except\s*:\s*(?!.*(?:log|print|raise|return))',
        "severity": "warning",
        "message": "Bare except: without logging may hide errors"
    },
    "sys_argv_no_check": {
        "pattern": r'sys\.argv\s*\[\s*[2-9]',
        "severity": "warning",
        "message": "sys.argv[X] without len(sys.argv) check may cause IndexError"
    }
}


class ToolValidator:
    """Tool Validator"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
    
    def check_syntax(self, filepath: str) -> Dict:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            return {"status": "ok", "errors": []}
        except SyntaxError as e:
            return {"status": "error", "errors": [{"line": e.lineno, "message": str(e)}]}
        except Exception as e:
            return {"status": "error", "errors": [{"message": str(e)}]}
    
    def check_patterns(self, filepath: str) -> List[Dict]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, OSError, UnicodeDecodeError):
            return [{"error": "Cannot read file"}]
        
        issues = []
        lines = content.split("\n")
        
        for name, info in COMMON_PATTERNS.items():
            for i, line in enumerate(lines, 1):
                if re.search(info["pattern"], line):
                    issues.append({
                        "type": name,
                        "line": i,
                        "severity": info["severity"],
                        "message": info["message"]
                    })
        
        return issues
    
    def check_encoding(self, filepath: str) -> Dict:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            has_unicode = any(ord(c) > 127 for c in content)
            has_codecs = "import io" in content and "sys.stdout" in content
            if has_unicode and not has_codecs:
                return {"status": "warning", "issues": ["Missing Unicode fix for Windows"]}
            return {"status": "ok", "issues": []}
        except (IOError, OSError, UnicodeDecodeError):
            return {"status": "error", "issues": ["Cannot read file"]}
    
    def validate(self, filepath: str) -> Dict:
        path = Path(filepath)
        if not path.exists():
            return {"status": "error", "reason": "File not found"}
        
        syntax = self.check_syntax(filepath)
        patterns = self.check_patterns(filepath)
        encoding = self.check_encoding(filepath)
        
        errors = sum(1 for p in patterns if p.get("severity") == "error")
        warnings = sum(1 for p in patterns if p.get("severity") == "warning")
        
        return {
            "file": str(path),
            "syntax": syntax,
            "patterns": patterns,
            "encoding": encoding,
            "summary": {
                "syntax_ok": syntax["status"] == "ok",
                "errors": errors,
                "warnings": warnings,
                "status": "PASS" if errors == 0 and syntax["status"] == "ok" else "FAIL"
            }
        }
    
    def check(self, filepath: str) -> Dict:
        result = self.validate(filepath)
        summary = result.get("summary", {})
        return {
            "status": "PASS" if summary.get("status") == "PASS" else "FAIL",
            "errors": summary.get("errors", 0),
            "warnings": summary.get("warnings", 0)
        }


def main():
    validator = ToolValidator()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        filepath = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not filepath:
            print("Usage: py tool_validator_001.py --check <file.py>")
            return 1
        
        if cmd == "--check":
            result = validator.check(filepath)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] == "PASS" else 1
        
        if cmd == "--validate":
            result = validator.validate(filepath)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["summary"]["status"] == "PASS" else 1
    
    print("TOOL-VALIDATOR-001 Tool Validator")
    print("Usage:")
    print("  py tool_validator_001.py --check <file.py>")
    print("  py tool_validator_001.py --validate <file.py>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
