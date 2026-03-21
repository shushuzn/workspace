#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HEALTH-REPORTER-001 Automated Health Report Generator
Generates and saves daily health reports
"""
import json, sys
from pathlib import Path
from datetime import datetime

TOOLS_DIR = Path("30-scripts-tools")
LOGS_DIR = Path("13-memory/.workflow_logs")
REPORT_DIR = Path("13-memory/reports")

def get_health_status():
    """Get current health status"""
    # Tool count
    tools = list(TOOLS_DIR.glob("*_001.py"))
    compliant = sum(1 for t in tools if "_001.py" in t.name)
    
    # Log status
    log_file = LOGS_DIR / "master.json"
    runs = success = 0
    if log_file.exists():
        try:
            log = json.loads(log_file.read_text(encoding="utf-8", errors="replace"))
            runs = len(log.get("runs", []))
            success = sum(1 for r in log.get("runs", []) if r.get("status") == "ok")
        except:
            pass
    
    score = 100
    if compliant < len(tools):
        score -= 10
    if runs > 0 and success / runs < 0.95:
        score -= 20
    
    return {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "tools": {"total": len(tools), "compliant": compliant},
        "workflows": {"runs": runs, "success": success}
    }

def generate_report():
    """Generate health report"""
    health = get_health_status()
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": health["timestamp"],
        "health_score": health["score"],
        "status": "HEALTHY" if health["score"] >= 80 else "WARNING" if health["score"] >= 50 else "CRITICAL",
        "metrics": {
            "tools": f"{health['tools']['compliant']}/{health['tools']['total']}",
            "workflows": f"{health['workflows']['success']}/{health['workflows']['runs']}",
            "compliance_rate": f"{health['tools']['compliant']/health['tools']['total']*100:.1f}%",
            "success_rate": f"{health['workflows']['success']/max(1,health['workflows']['runs'])*100:.1f}%"
        }
    }
    
    return report

def main():
    print("\n[HEALTH-REPORTER-001] Daily Health Report")
    print("=" * 50)
    
    report = generate_report()
    
    print(f"Date: {report['date']}")
    print(f"Status: [{report['status']}] Score: {report['health_score']}")
    print(f"Tools: {report['metrics']['tools']} ({report['metrics']['compliance_rate']})")
    print(f"Workflows: {report['metrics']['workflows']} ({report['metrics']['success_rate']})")
    
    # Save report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"health_{report['date']}.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n[Saved] {report_file}")
    
    # Save latest
    latest_file = REPORT_DIR / "latest.json"
    latest_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    return report

if __name__ == "__main__":
    main()
