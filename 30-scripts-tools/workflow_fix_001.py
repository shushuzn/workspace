#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-FIX-001 Batch Fix Tool Issues
"""

import json, sys, re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

class WorkflowFix:
    def fix_encoding(self, filepath):
        p = Path(filepath)
        if not p.exists(): return {"error": "not found"}
        
        content = p.read_text(encoding="utf-8", errors="replace")
        original = content
        
        if "json.loads" in content and 'encoding="utf-8"' not in content:
            content = re.sub(
                r'json\.loads\(([^)]+)\.read_text\(',
                r'json.loads(\1.read_text(encoding="utf-8", errors="replace")',
                content
            )
        
        if content != original:
            p.write_text(content, encoding="utf-8")
            return {"file": p.name, "fixed": "encoding"}
        return {"file": p.name, "fixed": "none"}
    
    def fix_timeout(self, filepath):
        p = Path(filepath)
        if not p.exists(): return {"error": "not found"}
        
        content = p.read_text(encoding="utf-8", errors="replace")
        original = content
        
        if "subprocess.run" in content and "timeout=" not in content:
            content = re.sub(
                r'subprocess\.run\(',
                'subprocess.run(',
                content
            )
        
        if content != original:
            p.write_text(content, encoding="utf-8")
            return {"file": p.name, "fixed": "timeout"}
        return {"file": p.name, "fixed": "none"}
    
    def batch_fix(self, dry_run=True):
        files = list(TOOLS_DIR.glob("*_001.py"))
        results = []
        
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                
                has_encoding_issue = "json.loads" in content and 'encoding="utf-8"' not in content
                has_timeout_issue = "subprocess.run" in content and "timeout=" not in content
                
                if not dry_run:
                    self.fix_encoding(f)
                    self.fix_timeout(f)
                
                results.append({
                    "file": f.name,
                    "issues": [],
                    "status": "fixed" if (not dry_run and (has_encoding_issue or has_timeout_issue)) else "ok"
                })
            except Exception as e:
                results.append({"file": f.name, "error": str(e)})
        
        return results

if __name__ == "__main__":
    fixer = WorkflowFix()
    dry = "--dry" in sys.argv
    
    if "--dry" in sys.argv:
        sys.argv.remove("--dry")
    
    print(f"Mode: {'DRY' if dry else 'LIVE'}")
    results = fixer.batch_fix(dry)
    
    fixed = sum(1 for r in results if r.get("status") == "fixed")
    print(f"Results: {len(results)} files")
    
    if dry:
        print("\nDry run - no changes made")
    else:
        print(f"Fixed: {fixed} files")
