#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-ARGV-FIX-001 Auto-fix missing argv validation
Adds sys.argv parameter checks to CLI tools
"""
import json, re, sys
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")

def has_argv_check(content):
    """Check if file has argv validation"""
    return bool(re.search(r'if\s+len\(sys\.argv\)\s*[<>=]', content))

def add_argv_check(content, filepath):
    """Add argv validation to tool"""
    # Find where to insert (after imports, before main class/def)
    lines = content.split("\n")
    
    # Find insertion point (after last import)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_idx = i + 1
    
    # Check if already has check
    if has_argv_check(content):
        return {"file": filepath.name, "status": "skip", "reason": "Already has check"}
    
    check_code = '''
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)
'''
    
    # Find main block
    main_found = False
    for i, line in enumerate(lines):
        if re.match(r'^if __name__ == "__main__":', line):
            # Insert before this
            lines.insert(i, check_code)
            main_found = True
            break
    
    if not main_found:
        # Append at end
        lines.append(check_code)
    
    new_content = "\n".join(lines)
    
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return {"file": filepath.name, "status": "fixed"}
    
    return {"file": filepath.name, "status": "skip"}

def main():
    dry_run = "--dry-run" in sys.argv
    
    print(f"\n[AUTO-ARGV-FIX-001] {'Dry-run' if dry_run else 'Fixing'}")
    print("=" * 50)
    
    results = []
    
    for f in TOOLS_DIR.glob("*_001.py"):
        if f.name.startswith("auto_argv"):
            continue
        
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except (IOError, OSError):
            continue
        
        # Check if has sys.argv but no validation
        if "sys.argv" in content and not has_argv_check(content):
            if dry_run:
                results.append({"file": f.name, "status": "would_fix"})
            else:
                result = add_argv_check(content, f)
                results.append(result)
    
    print(f"\n[RESULT] {len(results)} files need fix")
    for r in results[:10]:
        print(f"  - {r['file']}: {r['status']}")
    
    Path("13-memory/.argv_fix_report.json").write_text(json.dumps({
        "results": results,
        "total": len(results)
    }, indent=2))

if __name__ == "__main__":
    main()
