#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPTIMAP-001 Optimization Roadmap Manager
【优化路线图管理器】

功能:
  - 查看优化工具进度
  - 状态更新
  - 下一步建议
  - 统计与分析
"""
import json
import sys
from pathlib import Path
from datetime import datetime


ROADMAP_FILE = Path("flow-archive/optimization-roadmap.json")


class OptimizationRoadmapManager:
    """优化路线图管理器"""
    
    def __init__(self):
        self.file = ROADMAP_FILE
        self._ensure_roadmap()
    
    def _ensure_roadmap(self):
        if not self.file.exists():
            default = {
                "roadmap_id": "opt-v1.0.0",
                "name": "工作流优化工具路线图",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "total_tools": 0,
                "completed_tools": 0,
                "progress_pct": 0.0,
                "phases": {},
                "tools": {}
            }
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
    
    def _load(self) -> dict:
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save(self, data: dict):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def status(self) -> dict:
        """查看状态"""
        data = self._load()
        
        return {
            "roadmap_id": data["roadmap_id"],
            "name": data["name"],
            "version": data["version"],
            "total_tools": data["total_tools"],
            "completed_tools": data["completed_tools"],
            "progress_pct": data["progress_pct"],
            "target": data.get("target", ""),
            "last_updated": data["last_updated"]
        }
    
    def phases(self) -> list:
        """查看所有阶段"""
        data = self._load()
        
        result = []
        for phase_id, phase in data.get("phases", {}).items():
            result.append({
                "phase": phase_id,
                "name": phase["name"],
                "tools": phase["tools"],
                "status": phase["status"],
                "description": phase["description"]
            })
        
        return result
    
    def tools(self) -> dict:
        """查看所有工具"""
        data = self._load()
        return data.get("tools", {})
    
    def add_tool(self, tool_id: str, name: str, file: str, phase: str = "1") -> dict:
        """添加工具"""
        data = self._load()
        
        # 添加工具
        data["tools"][tool_id] = {
            "name": name,
            "file": file,
            "status": "completed",
            "added_at": datetime.now().isoformat()
        }
        
        # 更新统计
        data["total_tools"] = len(data["tools"])
        data["completed_tools"] = sum(1 for t in data["tools"].values() if t.get("status") == "completed")
        data["progress_pct"] = (data["completed_tools"] / data["total_tools"] * 100) if data["total_tools"] > 0 else 0
        data["last_updated"] = datetime.now().isoformat()
        
        self._save(data)
        
        return {
            "status": "added",
            "tool_id": tool_id,
            "total": data["total_tools"],
            "progress": f"{data['progress_pct']:.1f}%"
        }
    
    def update_status(self, tool_id: str, status: str) -> dict:
        """更新状态"""
        data = self._load()
        
        if tool_id in data["tools"]:
            data["tools"][tool_id]["status"] = status
            data["last_updated"] = datetime.now().isoformat()
            
            # 重新计算进度
            data["completed_tools"] = sum(1 for t in data["tools"].values() if t.get("status") == "completed")
            data["progress_pct"] = (data["completed_tools"] / data["total_tools"] * 100) if data["total_tools"] > 0 else 0
            
            self._save(data)
            
            return {"status": "updated", "tool_id": tool_id, "new_status": status}
        
        return {"status": "error", "message": "Tool not found"}
    
    def next_steps(self) -> list:
        """获取下一步建议"""
        data = self._load()
        
        suggestions = data.get("next_steps", [])
        completed = data.get("completed_tools", 0)
        total = data.get("total_tools", 0)
        
        if completed >= total and total > 0:
            return ["All optimization tools completed!", "Consider integration with core workflow"]
        
        return suggestions
    
    def metrics(self) -> dict:
        """获取指标"""
        data = self._load()
        return data.get("metrics", {})


def main():
    manager = OptimizationRoadmapManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            result = manager.status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--phases":
            result = manager.phases()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--tools":
            result = manager.tools()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--next":
            result = manager.next_steps()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--metrics":
            result = manager.metrics()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--all":
            result = {
                "status": manager.status(),
                "phases": manager.phases(),
                "tools": manager.tools(),
                "next_steps": manager.next_steps(),
                "metrics": manager.metrics()
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("OPTIMAP-001 Optimization Roadmap Manager")
    print("Usage:")
    print("  py optimap_001_manager.py --status    # View roadmap status")
    print("  py optimap_001_manager.py --phases    # View all phases")
    print("  py optimap_001_manager.py --tools      # View all tools")
    print("  py optimap_001_manager.py --next       # Get next steps")
    print("  py optimap_001_manager.py --metrics   # View metrics")
    print("  py optimap_001_manager.py --all        # Full overview")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())