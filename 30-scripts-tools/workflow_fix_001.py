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
        
        # Add encoding to json.loads
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
        
        # Add timeout to subprocess.run without timeout
        if "subprocess.run" in content:
            content = re.sub(
                r'subprocess\.run\(([^)]+)\)',
                lambda m: self._add_timeout(m.group(0)),
                content
            )
        
        if content != original:
            p.write_text(content, encoding="utf-8")
            return {"file": p.name, "fixed": "timeout"}
        return {"file": p.name, "fixed": "none"}
    
    def _add_timeout(self, match):
        if "timeout=" in match:
            return match
        return match.rstrip(")") + ", timeout=60)"
    
    def batch_fix(self, dry_run=True):
        files = list(TOOLS_DIR.glob("*_001.py"))
        results = []
        
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                
                # Check issues
                has_encoding_issue = "json.loads" in content and 'encoding="utf-8"' not in content
                has_timeout_issue = "subprocess.run" in content and "timeout=" not in content
                
                if not dry_run:
                    fixed_encoding = self.fix_encoding(f)
                    fixed_timeout = self.fix_timeout(f)
                    fixed = fixed_encoding["fixed"] if "fixed" in fixed_encoding else ""
                else:
                    fixed = []
                    if has_encoding_issue: fixed.append("encoding")
                    if has_timeout_issue: fixed.append("timeout")
                
                results.append({
                    "file": f.name,
                    "issues": fixed if dry_run else [],
                    "status": "fixed" if (not dry_run and (has_encoding_issue or has_timeout_issue)) else "ok"
                })
            except Exception as e:
                results.append({"file": f.name, "error": str(e)})
        
        return results

if __name__ == "__main__":
    fixer = WorkflowFix()
    dry = "--dry" not in sys.argv
    
    if "--dry" in sys.argv:
        sys.argv.remove("--dry")
    
    print(f"Mode: {'DRY' if not dry else 'LIVE'}")
    results = fixer.batch_fix(dry)
    
    fixed = sum(1 for r in results if r.get("status") == "fixed")
    print(f"Fixed: {fixed}/{len(results)}")
    
    if dry:
        print("\nFiles to fix:")
        for r in results[:10]:
            if r.get("issues"):
                print(f"  {r['file']}: {', '.join(r['issues'])}")
