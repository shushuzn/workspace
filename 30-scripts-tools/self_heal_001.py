#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SELF-HEAL-001 Self-Healing System
Automatically detects and fixes issues without human intervention
"""
import json, re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TOOLS_DIR = Path("30-scripts-tools")

class SelfHealSystem:
    def __init__(self):
        self.health_score = 100
    
    def diagnose_file(self, filepath):
        """Diagnose issues in a single file"""
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (IOError, OSError):
            return []
        
        issues = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            # Check for bare except
            if re.match(r'^\s+except\s*:\s*$', line):
                issues.append({
                    "file": filepath.name,
                    "line": i + 1,
                    "type": "bare_except",
                    "severity": "high",
                    "content": line.strip()
                })
        
        return issues
    
    def heal_file(self, filepath, issues):
        """Auto-heal a file"""
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (IOError, OSError):
            return False
        
        original = content
        lines = content.split("\n")
        
        for issue in issues:
            if issue["type"] == "bare_except":
                line_idx = issue["line"] - 1
                if 0 <= line_idx < len(lines):
                    line = lines[line_idx]
                    indent = len(line) - len(line.lstrip())
                    spaces = " " * indent
                    
                    # Detect context
                    context = "(IOError, OSError)"
                    for j in range(max(0, line_idx-5), line_idx):
                        prev = lines[j] if j < len(lines) else ""
                        if "json" in prev:
                            context = "(json.JSONDecodeError, IOError, OSError)"
                            break
                    
                    new_line = f"{spaces}except {context}:"
                    lines[line_idx] = new_line
        
        new_content = "\n".join(lines)
        if new_content != original:
            filepath.write_text(new_content, encoding="utf-8")
            return True
        return False
    
    def predict_failures(self):
        """Predict which tools might fail"""
        predictions = []
        
        for f in TOOLS_DIR.glob("*_001.py"):
            risk = 0
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                if "bare_except" in content:
                    risk += 30
                if len(content) > 5000:
                    risk += 15
            except (IOError, OSError):
                risk += 50
            
            if risk > 30:
                predictions.append({"file": f.name, "risk": risk})
        
        predictions.sort(key=lambda x: x["risk"], reverse=True)
        return predictions[:10]
    
    def auto_heal(self, dry_run=False):
        """Auto-heal all detected issues"""
        all_issues = []
        
        for f in TOOLS_DIR.glob("*_001.py"):
            issues = self.diagnose_file(f)
            all_issues.extend(issues)
        
        if dry_run:
            return {"mode": "dry-run", "would_heal": len(all_issues), "issues": all_issues}
        
        # Group by file
        by_file = defaultdict(list)
        for issue in all_issues:
            by_file[issue["file"]].append(issue)
        
        healed = []
        for filename, issues in by_file.items():
            filepath = TOOLS_DIR / filename
            if self.heal_file(filepath, issues):
                healed.append({"file": filename, "count": len(issues)})
        
        self.health_score = max(0, 100 - len(all_issues) * 2)
        
        return {
            "healed": healed,
            "remaining": len(all_issues) - sum(i["count"] for i in healed),
            "health_score": self.health_score
        }

def main():
    healer = SelfHealSystem()
    
    print("\n[SELF-HEAL-001] Self-Healing System")
    print("=" * 50)
    
    if "--diagnose" in sys.argv:
        result = healer.auto_heal(dry_run=True)
        print(f"\n[DIAGNOSIS]")
        print(f"  Would heal: {result['would_heal']} issues")
        for issue in result["issues"][:5]:
            print(f"  [{issue['severity']}] {issue['file']}:{issue['line']}")
    
    elif "--predict" in sys.argv:
        predictions = healer.predict_failures()
        print(f"\n[PREDICTIVE ANALYSIS]")
        print(f"  High-risk: {len(predictions)} tools")
        for p in predictions[:5]:
            print(f"  [!] {p['file']} (risk: {p['risk']}%)")
    
    elif "--heal" in sys.argv:
        dry = "--dry-run" in sys.argv
        result = healer.auto_heal(dry_run=dry)
        print(f"\n[HEAL] {'Dry-run' if dry else 'Healing'}")
        if dry:
            print(f"  Would heal: {result['would_heal']} issues")
        else:
            print(f"  Healed: {len(result['healed'])} files")
            print(f"  Health: {result['health_score']}%")
    
    else:
        print("\nUsage:")
        print("  --diagnose  Diagnose all issues")
        print("  --predict   Predict failures")
        print("  --heal      Auto-heal issues")
        print("  --heal --dry-run  Preview heal")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "predictions": healer.predict_failures()
    }
    Path("13-memory/.self_heal_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )

if __name__ == "__main__":
    main()
