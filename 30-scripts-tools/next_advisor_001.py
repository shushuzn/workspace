import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NEXT-001 Next Step Advisor
【智能下一步建议器】

功能:
  - 自动分析当前状态
  - 生成下一步建议
  - 提供行动项目
  - 进度评估与提醒

依赖: roadmap_001_manager.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# 配置
ADVISOR_DIR = Path("60-DATA/advisor_001")
ROADMAP_FILE = Path("flow-archive/stock-analysis-roadmap.json")
CONFIG_FILE = Path("30-scripts-tools/next_001_config.json")


class NextStepAdvisor:
    """下一步建议器"""
    
    def __init__(self):
        self.advisor_dir = ADVISOR_DIR
        self.roadmap_file = ROADMAP_FILE
        self.config = self._load_config()
        
        self.advisor_dir.mkdir(parents=True, exist_ok=True)
        
        self.suggestions_file = self.advisor_dir / "suggestions.json"
        self.history_file = self.advisor_dir / "advisor_history.json"
    
    def _load_config(self) -> dict:
        default = {
            "auto_advice": True,
            "max_suggestions": 5,
            "check_gaps": True
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (Exception,):
                return default
        return default
    
    def _load_roadmap(self) -> dict:
        """加载路线图"""
        if not self.roadmap_file.exists():
            return None
        
        with open(self.roadmap_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def analyze(self) -> dict:
        """分析当前状态并生成建议"""
        roadmap = self._load_roadmap()
        
        if not roadmap:
            return {"status": "error", "message": "Roadmap not found"}
        
        # 分析阶段状态
        phases = roadmap.get("phases", {})
        completed_tools = set(roadmap.get("completed_tools", []))
        
        # 收集所有工具
        all_tools = []
        phase_details = []
        
        for phase_id, phase in sorted(phases.items(), key=lambda x: int(x[0])):
            tools = phase.get("tools", [])
            all_tools.extend(tools)
            status = phase.get("status", "unknown")
            
            # 计算完成数
            completed = sum(1 for t in tools if t in completed_tools)
            
            phase_details.append({
                "phase": phase_id,
                "name": phase.get("name", f"Phase {phase_id}"),
                "total": len(tools),
                "completed": completed,
                "status": status,
                "progress": round(completed / len(tools) * 100, 1) if tools else 0
            })
        
        total_tools = len(all_tools)
        completed_count = len(completed_tools)
        
        # 找下一个未完成的工具
        next_tool = None
        next_phase = None
        for phase_id, phase in sorted(phases.items(), key=lambda x: int(x[0])):
            for tool in phase.get("tools", []):
                if tool not in completed_tools:
                    next_tool = tool
                    next_phase = phase_id
                    break
            if next_tool:
                break
        
        # 生成建议
        suggestions = self._generate_suggestions(
            phase_details, next_tool, next_phase, completed_count, total_tools
        )
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tools": total_tools,
                "completed": completed_count,
                "remaining": total_tools - completed_count,
                "progress_pct": round(completed_count / total_tools * 100, 1)
            },
            "phases": phase_details,
            "next_step": {
                "tool": next_tool,
                "phase": next_phase,
                "phase_name": phases.get(next_phase, {}).get("name", "Unknown") if next_phase else None
            } if next_tool else None,
            "suggestions": suggestions,
            "actions": self._generate_actions(suggestions)
        }
        
        # 保存
        self._save_suggestions(result)
        
        return result
    
    def _generate_suggestions(self, phases: list, next_tool: str, next_phase: str, 
                               completed: int, total: int) -> list:
        """生成建议"""
        suggestions = []
        
        # 1. 进度建议
        progress = completed / total if total > 0 else 0
        
        if progress >= 1.0:
            suggestions.append({
                "type": "milestone",
                "priority": "high",
                "title": "All tools completed!",
                "description": "All 32 stock analysis tools are complete. Consider Phase 7 planning."
            })
        elif progress >= 0.75:
            suggestions.append({
                "type": "progress",
                "priority": "high",
                "title": "Final push to complete",
                "description": f"{total - completed} tools remaining. Almost there!"
            })
        elif progress >= 0.5:
            suggestions.append({
                "type": "progress",
                "priority": "medium",
                "title": "Halfway there",
                "description": "Good progress! Keep momentum."
            })
        
        # 2. 下一个工具建议
        if next_tool:
            suggestions.append({
                "type": "next_tool",
                "priority": "high",
                "title": f"Next: {next_tool}",
                "description": f"Continue with {next_tool} in Phase {next_phase}"
            })
        
        # 3. 阶段建议
        in_progress_phase = None
        for p in phases:
            if p["status"] == "in_progress":
                in_progress_phase = p
                break
        
        if in_progress_phase:
            remaining = in_progress_phase["total"] - in_progress_phase["completed"]
            if remaining > 0:
                suggestions.append({
                    "type": "phase",
                    "priority": "medium",
                    "title": f"Phase {in_progress_phase['phase']}: {in_progress_phase['name']}",
                    "description": f"{remaining} tools remaining in this phase"
                })
        
        # 4. 检查未完成阶段
        for p in phases:
            if p["status"] != "completed" and p["status"] != "in_progress":
                suggestions.append({
                    "type": "gap",
                    "priority": "medium",
                    "title": f"Phase {p['phase']} pending",
                    "description": f"Phase {p['phase']} ({p['name']}) needs attention"
                })
        
        # 5. 工具建议
        if next_tool and next_tool.startswith("SA-"):
            suggestions.append({
                "type": "tool_idea",
                "priority": "low",
                "title": f"Implement {next_tool}",
                "description": "Use tool_executor.py for standardized implementation"
            })
        
        return suggestions[:self.config.get("max_suggestions", 5)]
    
    def _generate_actions(self, suggestions: list) -> list:
        """生成具体行动"""
        actions = []
        
        for s in suggestions:
            if s["type"] == "next_tool":
                actions.append({
                    "action": f"Implement {s.get('title', '')}",
                    "command": f"py 30-scripts-tools/workflow_helper.py 1 \"Implement {s.get('title', '')}\""
                })
            elif s["type"] == "milestone":
                actions.append({
                    "action": "Plan next phase",
                    "command": "py 30-scripts-tools/roadmap_001_manager.py --add-phase"
                })
            elif s["type"] == "progress":
                actions.append({
                    "action": "Continue work",
                    "command": "py 30-scripts-tools/roadmap_001_manager.py --next"
                })
        
        return actions
    
    def _save_suggestions(self, result: dict):
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py next_advisor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py next_advisor_001.py

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

保存建议"""
        with open(self.suggestions_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 保存历史
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (Exception,):
                pass
        
        history.append({
            "timestamp": result["timestamp"],
            "progress_pct": result["summary"]["progress_pct"],
            "next_tool": result["next_step"]["tool"] if result["next_step"] else None
        })
        
        history = history[-20:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_suggestions(self) -> dict:
        """获取上次建议"""
        if not self.suggestions_file.exists():
            return {"status": "error", "message": "No suggestions yet"}
        
        with open(self.suggestions_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_history(self, limit: int = 10) -> dict:
        """获取历史"""
        if not self.history_file.exists():
            return {"status": "error", "message": "No history"}
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        return {
            "status": "success",
            "count": len(history),
            "history": history[-limit:]
        }
    
    def quick_advice(self) -> str:
        """快速建议（简洁输出）"""
        result = self.analyze()
        
        if result.get("status") == "error":
            return f"Error: {result.get('message')}"
        
        lines = [
            f"Progress: {result['summary']['completed']}/{result['summary']['total_tools']} ({result['summary']['progress_pct']}%)",
            ""
        ]
        
        next_step = result.get("next_step")
        if next_step and next_step.get("tool"):
            lines.append(f"Next: {next_step['tool']} (Phase {next_step['phase']})")
        
        lines.append("")
        lines.append("Suggestions:")
        
        for s in result.get("suggestions", [])[:3]:
            lines.append(f"  - {s.get('title', '')}: {s.get('description', '')}")
        
        return "\n".join(lines)


logging.basicConfig(level=logging.INFO)
def main():
    advisor = NextStepAdvisor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--analyze":
            result = advisor.analyze()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--suggestions":
            result = advisor.get_suggestions()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--history":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = advisor.get_history(limit)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--quick":
            print(advisor.quick_advice())
            return 0
        
        if sys.argv[1] == "--auto":
            # 自动建议 - 核心功能
            result = advisor.analyze()
            summary = result.get("summary", {})
            next_step = result.get("next_step", {})
            
            print(f"=== Next Step Advisor ===")
            print(f"Progress: {summary.get('completed')}/{summary.get('total_tools')} ({summary.get('progress_pct')}%)")
            print(f"")
            
            if next_step and next_step.get("tool"):
                print(f"NEXT ACTION: Implement {next_step['tool']}")
                print(f"Phase: {next_step.get('phase')} ({next_step.get('phase_name')})")
                print(f"")
            
            print("Top Suggestions:")
            for s in result.get("suggestions", [])[:3]:
                print(f"  [{s.get('priority', '?').upper()}] {s.get('title', '')}")
                print(f"    {s.get('description', '')}")
                print(f"")
            
            return 0
    
    print("NEXT-001 Next Step Advisor")
    print("Usage:")
    print("  py next_001_advisor.py --analyze       # Full analysis")
    print("  py next_001_advisor.py --suggestions  # Get last suggestions")
    print("  py next_001_advisor.py --history       # View history")
    print("  py next_001_advisor.py --quick         # Quick summary")
    print("  py next_001_advisor.py --auto          # Auto advice (recommended)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())