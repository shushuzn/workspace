#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TOOL-NAMER-001 Tool Naming Convention Manager

Naming Convention:
  File:   tool_name_001.py (snake_case + _001)
  Class:  ToolName001 (PascalCase + optional number)
  Method: tool_name (snake_case)
"""

import json, sys, re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

class ToolNamer:
    def __init__(self):
        self.tools_dir = TOOLS_DIR
    
    def _to_snake(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal(self, name):
        return ''.join(word.capitalize() for word in name.replace("-", "_").split("_"))
    
    def suggest_name(self, name):
        """Suggest correct naming"""
        snake = self._to_snake(name)
        return {
            "input": name,
            "file": f"{snake}_001.py",
            "class": f"{self._to_pascal(snake)}001"
        }
    
    def scan(self):
        results = []
        pattern = re.compile(r'^[a-z][a-z0-9_]*_\d+\.py$')
        for f in sorted(self.tools_dir.glob("*.py")):
            is_convention = bool(pattern.match(f.name))
            results.append({
                "file": f.name,
                "status": "PASS" if is_convention else "FAIL"
            })
        return results
    
    def batch_suggest(self):
        """Suggest renames for all non-conforming files"""
        results = []
        pattern = re.compile(r'^[a-z][a-z0-9_]*_\d+\.py$')
        for f in sorted(self.tools_dir.glob("*.py")):
            if not pattern.match(f.name):
                # Generate new name
                base = f.stem
                # Remove existing _001 suffix if present
                base = re.sub(r'_\d+$', '', base)
                # Convert to snake_case and add _001
                words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', base)
                snake = '_'.join(w.lower() for w in words if w)
                new_name = f"{snake}_001.py"
                results.append({
                    "old": f.name,
                    "new": new_name,
                    "class": self._to_pascal(snake) + "001"
                })
        return results

if __name__ == "__main__":
    namer = ToolNamer()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--scan":
            results = namer.scan()
            pass_count = sum(1 for r in results if r["status"] == "PASS")
            print(json.dumps(results, ensure_ascii=False, indent=2))
            print(f"\nTotal: {len(results)}, PASS: {pass_count}, FAIL: {len(results)-pass_count}")
        
        elif cmd == "--suggest":
            results = namer.batch_suggest()
            print(json.dumps(results[:30], ensure_ascii=False, indent=2))
            if len(results) > 30:
                print(f"\n... and {len(results)-30} more")
        
        elif cmd == "--convert":
            name = sys.argv[2] if len(sys.argv) > 2 else "myTool"
            print(json.dumps(namer.suggest_name(name), ensure_ascii=False, indent=2))
    
    else:
        print("TOOL-NAMER-001 Tool Naming Manager")
        print("\nNaming Rules:")
        print("  File:   tool_name_001.py")
        print("  Class:  ToolName001")
        print("\nCommands:")
        print("  --scan        Scan all tools")
        print("  --suggest     Show batch rename suggestions")
        print("  --convert <n> Convert name to convention")
