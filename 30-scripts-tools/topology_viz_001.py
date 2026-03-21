#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TOPOLOGY-VIZ-001 Real-time Tool Topology Visualizer
Shows tool relationships, dependencies, and health status
"""
import json, re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TOOLS_DIR = Path("30-scripts-tools")
LOGS_DIR = Path("13-memory/.workflow_logs")

def scan_dependencies():
    """Scan tools for dependencies"""
    deps = defaultdict(list)
    categories = defaultdict(list)
    
    for f in TOOLS_DIR.glob("*_001.py"):
        if f.name.startswith("__"):
            continue
        
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except:
            continue
        
        # Find imports
        imports = re.findall(r'import (\w+)', content)
        for imp in imports:
            if imp in ["json", "sys", "pathlib", "datetime", "subprocess", "re"]:
                continue
            deps[f.name].append(imp)
        
        # Categorize by prefix
        prefix = f.stem.split("_")[0] if "_" in f.stem else f.stem
        categories[prefix].append(f.name)
    
    return deps, categories

def get_health_status():
    """Get workflow health status"""
    log_file = LOGS_DIR / "master.json"
    if log_file.exists():
        try:
            log = json.loads(log_file.read_text(encoding="utf-8", errors="replace"))
            runs = log.get("runs", [])
            success = sum(1 for r in runs if r.get("status") == "ok")
            return {"total": len(runs), "success": success, "rate": success/max(1,len(runs))*100}
        except:
            pass
    return {"total": 0, "success": 0, "rate": 100}

def generate_ascii_topology():
    """Generate ASCII visualization"""
    deps, categories = scan_dependencies()
    health = get_health_status()
    tools = list(TOOLS_DIR.glob("*_001.py"))
    
    # Count categories
    cat_counts = {k: len(v) for k, v in categories.items()}
    top_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    
    output = []
    output.append("\n" + "=" * 60)
    output.append("  TOPOLOGY-VIZ-001 工具拓扑可视化")
    output.append("=" * 60)
    output.append(f"  Updated: {datetime.now().strftime('%H:%M:%S')}")
    output.append("")
    
    # Health bar
    rate = health["rate"]
    bar_len = int(rate / 5)
    bar = "#" * bar_len + "-" * (20 - bar_len)
    output.append(f"  健康状态: [{bar}] {rate:.0f}%")
    output.append(f"  工作流: {health['success']}/{health['total']} 成功")
    output.append("")
    
    # Category distribution
    output.append("  [工具分类分布]")
    output.append("  " + "-" * 40)
    for cat, count in top_cats:
        pct = count / len(tools) * 100
        bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
        output.append(f"  {cat[:15]:15} {bar} {count:3} ({pct:4.1f}%)")
    
    # Dependency graph
    output.append("")
    output.append("  [核心依赖关系]")
    output.append("  " + "-" * 40)
    
    # Show top dependencies
    dep_counts = {k: len(v) for k, v in deps.items()}
    top_deps = sorted(dep_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for tool, count in top_deps:
        deps_list = deps.get(tool, [])[:3]
        output.append(f"  {tool[:25]:25} → {', '.join(deps_list[:3]) or '独立'}")
    
    # Mini graph
    output.append("")
    output.append("  [拓扑结构]")
    output.append("  " + "-" * 40)
    output.append("       [CORE]")
    output.append("          |")
    output.append("    [PLANNER]←→[EXECUTOR]")
    output.append("          |")
    output.append("      [CRITIC]")
    output.append("          |")
    output.append("    [COORDINATOR]")
    output.append("          |")
    output.append("  [LEARNER] [INNOVATOR]")
    output.append("")
    output.append("=" * 60)
    
    return "\n".join(output)

def generate_json_topology():
    """Generate JSON topology data"""
    deps, categories = scan_dependencies()
    health = get_health_status()
    tools = list(TOOLS_DIR.glob("*_001.py"))
    
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tools": len(tools),
            "health_score": health["rate"],
            "workflows": health
        },
        "categories": {k: len(v) for k, v in categories.items()},
        "dependencies": dict(deps),
        "top_tools": {
            "most_depended": sorted([(k, len(v)) for k, v in deps.items()], 
                                    key=lambda x: x[1], reverse=True)[:10]
        }
    }

def main():
    import time
    
    if "--json" in sys.argv:
        print(json.dumps(generate_json_topology(), indent=2, ensure_ascii=False))
    elif "--watch" in sys.argv:
        print("[TOPOLOGY-VIZ-001] Real-time monitoring (Ctrl+C to exit)")
        print("=" * 60)
        while True:
            try:
                print(generate_ascii_topology())
                time.sleep(10)
            except KeyboardInterrupt:
                print("\n[EXIT]")
                break
    else:
        print(generate_ascii_topology())
        
        # Save JSON for API
        Path("13-memory/.topology.json").write_text(
            json.dumps(generate_json_topology(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

if __name__ == "__main__":
    main()
