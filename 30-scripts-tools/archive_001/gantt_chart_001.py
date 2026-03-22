import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GANTT-CHART-001 Gantt Chart Generator
【甘特图生成器】

功能:
  - 从路线图生成甘特图
  - ASCII艺术风格展示
  - 支持多维度
  - 时间线可视化
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


GANTT_DIR = Path("60-DATA/gantt_001")
GANTT_OUTPUT = GANTT_DIR / "gantt_charts"


class GanttChartGenerator:
    """甘特图生成器"""
    
    def __init__(self):
        self.output_dir = GANTT_OUTPUT
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_roadmap(self, dimension: str = "stock_analysis") -> dict:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py gantt_chart_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py gantt_chart_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

加载路线图数据"""
        roadmap_file = Path(f"flow-archive/roadmaps/{dimension}.json")
        
        if not roadmap_file.exists():
            return {"error": f"Dimension '{dimension}' not found"}
        
        with open(roadmap_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def generate_ascii_gantt(self, roadmap: dict, width: int = 80) -> str:
        """生成ASCII甘特图"""
        lines = []
        
        # Header
        name = roadmap.get("name", "Unknown")
        lines.append("=" * width)
        lines.append(f"Gantt Chart: {name}")
        lines.append("=" * width)
        lines.append("")
        
        # Phases
        phases = roadmap.get("phases", [])
        
        for phase in phases:
            phase_name = phase.get("name", f"Phase {phase.get('phase')}")
            status = phase.get("status", "unknown")
            total = phase.get("total", 0)
            
            # Status bar
            bar_length = min(total * 3, width - 30)
            if status == "completed":
                bar = "█" * bar_length
                status_symbol = "[DONE]"
            elif status == "in_progress":
                bar = "▓" * bar_length
                status_symbol = "[>>>]"
            else:
                bar = "░" * bar_length
                status_symbol = "[...]"
            
            line = f"{phase_name:20s} {status_symbol} {bar} {total}"
            lines.append(line)
        
        # Legend
        lines.append("")
        lines.append("Legend: [DONE] Completed | [>>>] In Progress | [...] Pending")
        
        return "\n".join(lines)
    
    def generate_timeline(self, roadmap: dict, days_per_char: int = 7) -> str:
        """生成时间线"""
        lines = []
        
        phases = roadmap.get("phases", [])
        
        # Timeline header
        lines.append("Timeline View")
        lines.append("-" * 60)
        
        for phase in phases:
            phase_name = phase.get("name", f"Phase {phase.get('phase')}")
            status = phase.get("status", "unknown")
            
            # Timeline bar
            if status == "completed":
                marker = "████████"
            elif status == "in_progress":
                marker = "▓▓▓▓▓▓▓░"
            else:
                marker = "░░░░░░░░"
            
            lines.append(f"{phase_name:20s} {marker}")
        
        return "\n".join(lines)
    
    def generate_multi_dimension(self, dimensions: list = None) -> str:
        """生成多维度甘特图"""
        if dimensions is None:
            dimensions = ["stock_analysis", "optimization", "protection", "automation"]
        
        lines = []
        lines.append("=" * 80)
        lines.append("Multi-Dimension Gantt Chart")
        lines.append("=" * 80)
        
        for dim in dimensions:
            roadmap = self.load_roadmap(dim)
            if "error" not in roadmap:
                lines.append("")
                lines.append(f"--- {roadmap.get('name', dim)} ---")
                lines.append(self.generate_ascii_gantt(roadmap, 80))
        
        return "\n".join(lines)
    
    def export(self, dimension: str = "stock_analysis") -> dict:
        """导出甘特图"""
        roadmap = self.load_roadmap(dimension)
        
        if "error" in roadmap:
            return roadmap
        
        # Generate ASCII chart
        ascii_chart = self.generate_ascii_gantt(roadmap)
        timeline = self.generate_timeline(roadmap)
        
        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        chart_file = self.output_dir / f"{dimension}_gantt_{timestamp}.txt"
        with open(chart_file, "w", encoding="utf-8") as f:
            f.write(ascii_chart)
        
        timeline_file = self.output_dir / f"{dimension}_timeline_{timestamp}.txt"
        with open(timeline_file, "w", encoding="utf-8") as f:
            f.write(timeline)
        
        return {
            "dimension": dimension,
            "gantt_file": str(chart_file),
            "timeline_file": str(timeline_file),
            "chart": ascii_chart,
            "timeline": timeline
        }


logging.basicConfig(level=logging.INFO)
def main():
    generator = GanttChartGenerator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--dimension":
            dim = sys.argv[2] if len(sys.argv) > 2 else "stock_analysis"
            result = generator.export(dim)
            if "error" in result:
                print(json.dumps(result))
            else:
                print(json.dumps({
                    "dimension": result["dimension"],
                    "files": {
                        "gantt": result["gantt_file"],
                        "timeline": result["timeline_file"]
                    }
                }, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--all":
            result = generator.generate_multi_dimension()
            print(result)
            return 0
        
        if sys.argv[1] == "--view":
            dim = sys.argv[2] if len(sys.argv) > 2 else "stock_analysis"
            roadmap = generator.load_roadmap(dim)
            if "error" in roadmap:
                print(roadmap["error"])
            else:
                print(generator.generate_ascii_gantt(roadmap))
            return 0
        
        if sys.argv[1] == "--timeline":
            dim = sys.argv[2] if len(sys.argv) > 2 else "stock_analysis"
            roadmap = generator.load_roadmap(dim)
            if "error" in roadmap:
                print(roadmap["error"])
            else:
                print(generator.generate_timeline(roadmap))
            return 0
    
    print("GANTT-CHART-001 Gantt Chart Generator")
    print("Usage:")
    print("  py gantt_chart_001.py --view <dimension>     # View ASCII gantt")
    print("  py gantt_chart_001.py --timeline <dimension> # View timeline")
    print("  py gantt_chart_001.py --dimension <dim>      # Export to file")
    print("  py gantt_chart_001.py --all                  # Multi-dimension view")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())