import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ROADMAP-001 路线图管理器
功能:
  - 标准化路线图更新
  - 阶段/工具状态管理
  - 进度追踪
  - 下一个工具推荐

使用方法:
  py roadmap_001_manager.py --status           查看状态
  py roadmap_001_manager.py --complete <tool>  标记完成
  py roadmap_001_manager.py --next             下一个工具
  py roadmap_001_manager.py --plan <phase>      规划阶段
  py roadmap_001_manager.py --export           导出报告
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 配置
ROADMAP_FILE = Path("flow-archive/stock-analysis-roadmap.json")
CONFIG_FILE = Path("30-scripts-tools/roadmap_001_config.json")


class RoadmapManager:
    """路线图管理器"""
    
    def __init__(self):
        self.roadmap_file = ROADMAP_FILE
        self.config = self._load_config()
        
        self.roadmap = self._load_roadmap()
    
    def _load_config(self) -> dict:
        default = {
            "current_version": "v2.1.0",
            "total_tools": 28,
            "next_phase": 6
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (Exception,):
                return default
        return default
    
    def _load_roadmap(self) -> dict:
        """加载或初始化路线图"""
        if self.roadmap_file.exists():
            try:
                with open(self.roadmap_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (Exception,):
                pass
        
        # 初始化
        return {
            "version": self.config["current_version"],
            "last_updated": datetime.now().isoformat(),
            "phases": {
                "1": {"name": "数据获取", "tools": ["SA-001", "SA-002", "SA-003", "SA-004"], "status": "completed"},
                "2": {"name": "技术分析", "tools": ["SA-005", "SA-006", "SA-007", "SA-008", "SA-009", "SA-010", "SA-011", "SA-012"], "status": "completed"},
                "3": {"name": "风险与信号", "tools": ["SA-013", "SA-014", "SA-015", "SA-016", "SA-017", "SA-018"], "status": "completed"},
                "4": {"name": "可视化与自动化", "tools": ["SA-019", "SA-020", "SA-021", "SA-022", "SA-023", "SA-024"], "status": "completed"},
                "5": {"name": "真实数据增强", "tools": ["SA-025", "SA-026", "SA-027", "SA-028"], "status": "completed"}
            },
            "completed_tools": [],
            "next_tool": "SA-029",
            "next_phase": 6
        }
    
    def _save_roadmap(self):
        """保存路线图"""
        with open(self.roadmap_file, "w", encoding="utf-8") as f:
            json.dump(self.roadmap, f, ensure_ascii=False, indent=2)
    
    def _get_completed_count(self) -> int:
        """获取已完成工具数"""
        return sum(len(p["tools"]) for p in self.roadmap["phases"].values() 
                  if p["status"] == "completed")
    
    def get_status(self) -> dict:
        """获取状态"""
        phases = []
        total = 0
        completed = 0
        
        for phase_id, phase in self.roadmap["phases"].items():
            phase_completed = len(phase["tools"]) if phase["status"] == "completed" else 0
            phases.append({
                "phase": phase_id,
                "name": phase["name"],
                "tools": phase["tools"],
                "status": phase["status"],
                "completed": phase_completed,
                "total": len(phase["tools"])
            })
            total += len(phase["tools"])
            completed += phase_completed
        
        return {
            "version": self.roadmap["version"],
            "last_updated": self.roadmap["last_updated"],
            "total_tools": total,
            "completed_tools": completed,
            "progress_pct": round(completed / total * 100, 1) if total > 0 else 0,
            "phases": phases,
            "next_tool": self.roadmap.get("next_tool"),
            "next_phase": self.roadmap.get("next_phase")
        }
    
    def mark_complete(self, tool_id: str) -> dict:
        """标记工具完成"""
        # 查找工具所在阶段
        found = False
        for phase_id, phase in self.roadmap["phases"].items():
            if tool_id in phase["tools"]:
                found = True
                if tool_id not in self.roadmap.get("completed_tools", []):
                    if "completed_tools" not in self.roadmap:
                        self.roadmap["completed_tools"] = []
                    self.roadmap["completed_tools"].append(tool_id)
                    
                    # 检查阶段是否完成
                    all_complete = all(
                        t in self.roadmap["completed_tools"] 
                        for t in phase["tools"]
                    )
                    if all_complete:
                        phase["status"] = "completed"
                        
                        # 更新版本
                        next_p = int(phase_id) + 1
                        self.roadmap["next_phase"] = next_p
                        self.roadmap["version"] = f"v2.{next_p - 1}.0"
                    
                    self.roadmap["last_updated"] = datetime.now().isoformat()
                    self._save_roadmap()
                    
                    return {
                        "status": "success",
                        "tool": tool_id,
                        "phase": phase_id,
                        "phase_completed": all_complete,
                        "next_tool": self._get_next_tool()
                    }
                else:
                    return {"status": "info", "message": f"{tool_id} already completed"}
        
        if not found:
            # 新工具 - 添加到下一阶段
            next_phase = str(self.roadmap.get("next_phase", 6))
            if next_phase not in self.roadmap["phases"]:
                self.roadmap["phases"][next_phase] = {
                    "name": f"Phase {next_phase}",
                    "tools": [],
                    "status": "in_progress"
                }
            
            self.roadmap["phases"][next_phase]["tools"].append(tool_id)
            self.roadmap["next_tool"] = self._get_next_tool()
            self.roadmap["last_updated"] = datetime.now().isoformat()
            self._save_roadmap()
            
            return {
                "status": "success",
                "tool": tool_id,
                "added_to_phase": next_phase,
                "next_tool": self.roadmap["next_tool"]
            }
    
    def _get_next_tool(self) -> str:
        """获取下一个工具 ID - 跳过已完成的"""
        completed = set(self.roadmap.get("completed_tools", []))
        
        # 收集所有工具，找第一个未完成的
        for phase in self.roadmap["phases"].values():
            for tool in phase["tools"]:
                if tool not in completed:
                    return tool
        
        # 如果都完成了，返回下一个新编号
        max_num = 0
        for phase in self.roadmap["phases"].values():
            for tool in phase["tools"]:
                if tool.startswith("SA-"):
                    try:
                        num = int(tool.split("-")[1])
                        max_num = max(max_num, num)
                    except (Exception,):
                        pass
        
        return f"SA-{max_num + 1:03d}"
    
    def add_phase(self, phase_name: str, tools: list) -> dict:
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
# py roadmap_manager_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py roadmap_manager_001.py

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

添加新阶段"""
        next_phase = str(self.roadmap.get("next_phase", 6))
        
        self.roadmap["phases"][next_phase] = {
            "name": phase_name,
            "tools": tools,
            "status": "planned"
        }
        
        self.roadmap["next_phase"] = int(next_phase) + 1
        self.roadmap["last_updated"] = datetime.now().isoformat()
        self._save_roadmap()
        
        return {
            "status": "success",
            "phase": next_phase,
            "name": phase_name,
            "tools": tools
        }
    
    def get_next(self) -> dict:
        """获取下一步"""
        next_tool = self._get_next_tool()
        
        # 计算下一工具属于哪个阶段
        next_phase = None
        for phase_id, phase in self.roadmap["phases"].items():
            if next_tool in phase["tools"]:
                next_phase = int(phase_id)
                break
        
        # 如果没找到，使用 current_phase 或 6
        if not next_phase:
            next_phase = self.roadmap.get("current_phase", 6)
        
        return {
            "next_tool": next_tool,
            "next_phase": next_phase,
            "version": self.roadmap["version"]
        }
    
    def export_markdown(self) -> str:
        """导出 Markdown 格式"""
        status = self.get_status()
        
        md = f"""# Stock Analysis Pipeline - 路线图

**当前版本:** {status['version']}  
**最后更新:** {status['last_updated']}  
**完成进度:** {status['completed_tools']}/{status['total_tools']} ({status['progress_pct']}%)

---

## 进度概览

| 阶段 | 名称 | 工具 | 状态 |
|------|------|------|------|
"""
        
        for p in status["phases"]:
            md += f"| Phase {p['phase']} | {p['name']} | {p['completed']}/{p['total']} | ✅ 完成 |\n"
        
        md += f"""
---

## 下一阶段

- **下一个工具:** {status['next_tool']}
- **下一阶段:** Phase {status['next_phase']}

---

## 工具列表

"""
        
        for p in status["phases"]:
            md += f"### Phase {p['phase']}: {p['name']}\n\n"
            for tool in p["tools"]:
                md += f"- {tool}\n"
            md += "\n"
        
        return md
    
    def update_version(self, new_version: str) -> dict:
        """更新版本号"""
        self.roadmap["version"] = new_version
        self.roadmap["last_updated"] = datetime.now().isoformat()
        self._save_roadmap()
        
        return {"status": "success", "version": new_version}


logging.basicConfig(level=logging.INFO)
def main():
    mgr = RoadmapManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            result = mgr.get_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--complete":
            if len(sys.argv) < 3:
                print("Usage: --complete <tool_id>")
                return 1
            result = mgr.mark_complete(sys.argv[2].upper())
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--next":
            result = mgr.get_next()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--add-phase":
            if len(sys.argv) < 4:
                print("Usage: --add-phase <name> <tool1,tool2,...>")
                return 1
            name = sys.argv[2]
            tools = sys.argv[3].split(",")
            result = mgr.add_phase(name, tools)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--export":
            print(mgr.export_markdown())
            return 0
        
        if sys.argv[1] == "--version":
            if len(sys.argv) < 3:
                print(f"Current: {mgr.roadmap['version']}")
                return 0
            result = mgr.update_version(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("ROADMAP-001 Roadmap Manager")
    print("Usage:")
    print("  py roadmap_001_manager.py --status           # View status")
    print("  py roadmap_001_manager.py --complete SA-029 # Mark complete")
    print("  py roadmap_001_manager.py --next            # Get next tool")
    print("  py roadmap_001_manager.py --add-phase 'AI Phase' SA-029,SA-030")
    print("  py roadmap_001_manager.py --export          # Export MD")
    print("  py roadmap_001_manager.py --version v3.0.0   # Update version")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())