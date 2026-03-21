#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-OPTIMIZER-001 Self-Optimization System
Automatically optimizes tools based on pattern analysis
"""
import json, re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")
OPT_LOG = Path("13-memory/.auto_optimizer_log.json")

OPTIMIZATIONS = {
    "add_logging": [
        (r'(import\s+sys)', r'\1\nimport logging\nlogger = logging.getLogger(__name__)'),
        (r'def main\(\):', r'logging.basicConfig(level=logging.INFO)\ndef main():'),
    ],
    "add_type_hints": [
        (r'def (\w+)\(([^)]*)\):', r'def \1(\2) -> None:'),
    ],
    "remove_bare_except": [
        (r'except\s*:', r'except Exception as e:\n            logger.error(f"Error: {e}")'),
    ],
    "add_docstring": [
        (r'#!/usr/bin/env python', r'#!/usr/bin/env python\n"""\nTODO: Add description\n"""'),
    ],
}

class AutoOptimizer:
    def __init__(self):
        self.log = {"optimizations": [], "fixed": [], "skipped": []}
        self.load_log()
    
    def load_log(self):
        if OPT_LOG.exists():
            self.log = json.loads(OPT_LOG.read_text(encoding="utf-8", errors="replace"))
    
    def save_log(self):
        OPT_LOG.write_text(json.dumps(self.log, indent=2, ensure_ascii=False))
    
    def analyze_tool(self, path):
        issues = []
        content = path.read_text(encoding="utf-8", errors="replace")
        
        # Check for missing logging
        if "print(" in content and "logging" not in content:
            issues.append(("add_logging", "Uses print, no logging"))
        
        # Check for bare except
        if re.search(r'except\s*:', content):
            issues.append(("remove_bare_except", "Uses bare except"))
        
        # Check for missing type hints
        func_defs = re.findall(r'def (\w+)\([^)]*\):', content)
        type_hints = re.findall(r'def \w+\([^)]*\) -> ', content)
        if len(func_defs) > len(type_hints) and len(func_defs) > 3:
            issues.append(("add_type_hints", "Missing type hints"))
        
        # Check for missing docstrings
        if '"""' not in content[:500] and "'''" not in content[:500]:
            issues.append(("add_docstring", "Missing docstring"))
        
        return issues
    
    def optimize_tool(self, path, opt_type):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            original = content
            
            if opt_type == "add_logging":
                if "import logging" not in content:
                    content = "import logging\nlogger = logging.getLogger(__name__)\n\n" + content
                if "logging.basicConfig" not in content:
                    content = content.replace("def main():", "logging.basicConfig(level=logging.INFO)\ndef main():")
            
            elif opt_type == "remove_bare_except":
                content = re.sub(r'except\s*:', 'except Exception as e:\n    logger.error(f"Error: {e}")', content)
            
            elif opt_type == "add_type_hints":
                content = re.sub(r'def (\w+)\(([^)]*)\):(\s*\n\s*""")', 
                    r'def \1(\2) -> None:\3', content)
            
            if content != original:
                path.write_text(content, encoding="utf-8")
                return True
            return False
        except Exception as e:
            return False
    
    def optimize_all(self, dry_run=True):
        print(f"\n[AUTO-OPTIMIZER-001] Self-Optimization")
        print("=" * 50)
        print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        
        results = {"fixed": [], "skipped": [], "issues": defaultdict(list)}
        
        for f in TOOLS_DIR.glob("*_001.py"):
            if f.name.startswith("__"):
                continue
            
            issues = self.analyze_tool(f)
            
            if issues:
                print(f"\n[{f.name}]")
                for opt_type, desc in issues:
                    print(f"  - {desc}")
                    results["issues"][opt_type].append(f.name)
                    
                    if not dry_run:
                        if self.optimize_tool(f, opt_type):
                            results["fixed"].append(f.name)
                            print(f"    [FIXED]")
                        else:
                            results["skipped"].append(f.name)
                            print(f"    [SKIPPED]")
        
        # Summary
        print(f"\n" + "=" * 50)
        print(f"[SUMMARY]")
        print(f"  Tools analyzed: {len(list(TOOLS_DIR.glob('*_001.py')))}")
        print(f"  Issues found: {sum(len(v) for v in results['issues'].values())}")
        
        if not dry_run:
            self.log["optimizations"].append({
                "timestamp": datetime.now().isoformat(),
                "fixed": results["fixed"],
                "skipped": results["skipped"]
            })
            self.save_log()
            print(f"  Fixed: {len(results['fixed'])}")
            print(f"  Skipped: {len(results['skipped'])}")
        else:
            print(f"  Would fix: {sum(len(v) for v in results['issues'].values())}")
        
        return results

def main():
    optimizer = AutoOptimizer()
    
    if "--optimize" in sys.argv:
        optimizer.optimize_all(dry_run=False)
    elif "--dry" in sys.argv:
        optimizer.optimize_all(dry_run=True)
    elif "--report" in sys.argv:
        print("\n[OPTIMIZATION REPORT]")
        print(f"  Total runs: {len(optimizer.log['optimizations'])}")
        fixed = sum(len(x["fixed"]) for x in optimizer.log["optimizations"])
        print(f"  Total fixed: {fixed}")
    else:
        print("\n[AUTO-OPTIMIZER-001]")
        print("  --dry        Preview changes")
        print("  --optimize   Apply optimizations")
        print("  --report     Show report")
        print("\n[Running dry run...]")
        optimizer.optimize_all(dry_run=True)

if __name__ == "__main__":
    main()
