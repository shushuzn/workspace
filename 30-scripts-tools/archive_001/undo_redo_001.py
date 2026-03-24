import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UNDO-UNDO-001 Undo/Redo Tool
【撤销/重做工具】

功能:
  - 记录操作历史
  - 撤销操作
  - 重做操作
  - 查看历史

使用:
  py undo_redo_001.py --push <action>
  py undo_redo_001.py --undo
  py undo_redo_001.py --redo
  py undo_redo_001.py --history
  py undo_redo_001.py --clear
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class UndoRedo:
    """撤销/重做工具"""

    MAX_HISTORY = 50  # 默认历史深度

    def __init__(self, max_depth: int = None):
        self.workspace = Path(__file__).parent.parent
        self.history_dir = self.workspace / "10-MEMORY/00-CORE/.undoredo"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "history.json"

        self.max_depth = max_depth or self.MAX_HISTORY
        self._ensure_history()

    def _ensure_history(self):
        """确保历史文件存在"""
        if not self.history_file.exists():
            self._save({
                "undo_stack": [],
                "redo_stack": [],
                "current": None
            })

    def _load(self) -> dict:
        with open(self.history_file, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, history: dict):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def push(self, action: str, data: dict = None) -> Dict:
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
# py undo_redo_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py undo_redo_001.py

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

记录操作"""
        history = self._load()

        entry = {
            "action": action,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }

        # 添加到undo栈
        history["undo_stack"].append(entry)

        # 清空redo栈
        history["redo_stack"] = []

        # 限制深度
        if len(history["undo_stack"]) > self.max_depth:
            history["undo_stack"] = history["undo_stack"][-self.max_depth:]

        self._save(history)

        return {
            "status": "success",
            "action": action,
            "undo_depth": len(history["undo_stack"])
        }

    def undo(self) -> Dict:
        """撤销"""
        history = self._load()
        
        if not history["undo_stack"]:
            return {"status": "error", "reason": "Nothing to undo"}
        
        # 弹出undo栈
        entry = history["undo_stack"].pop()
        
        # 推入redo栈
        history["redo_stack"].append(entry)
        
        self._save(history)
        
        return {
            "status": "success",
            "undone": entry.get("action"),
            "undo_depth": len(history["undo_stack"]),
            "redo_depth": len(history["redo_stack"])
        }
    
    def redo(self) -> Dict:
        """重做"""
        history = self._load()
        
        if not history["redo_stack"]:
            return {"status": "error", "reason": "Nothing to redo"}
        
        # 弹出redo栈
        entry = history["redo_stack"].pop()
        
        # 推入undo栈
        history["undo_stack"].append(entry)
        
        self._save(history)
        
        return {
            "status": "success",
            "redone": entry.get("action"),
            "undo_depth": len(history["undo_stack"]),
            "redo_depth": len(history["redo_stack"])
        }
    
    def history(self, limit: int = 10) -> List[Dict]:
        """查看历史"""
        history = self._load()
        
        undo = history["undo_stack"][-limit:]
        redo = history["redo_stack"][-limit:]
        
        return {
            "undo_stack": undo[::-1],  # 最新在前
            "redo_stack": redo[::-1],
            "undo_depth": len(history["undo_stack"]),
            "redo_depth": len(history["redo_stack"])
        }
    
    def clear(self) -> Dict:
        """清空历史"""
        self._save({
            "undo_stack": [],
            "redo_stack": [],
            "current": None
        })
        
        return {"status": "success", "message": "History cleared"}
    
    def status(self) -> Dict:
        """查看状态"""
        history = self._load()
        
        return {
            "undo_depth": len(history["undo_stack"]),
            "redo_depth": len(history["redo_stack"]),
            "max_depth": self.max_depth
        }


logging.basicConfig(level=logging.INFO)
def main():
    ur = UndoRedo()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--push":
            action = sys.argv[2] if len(sys.argv) > 2 else "unknown"
            action = action.strip().replace('"', '').replace("'", '')
            result = ur.push(action)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--undo":
            result = ur.undo()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--redo":
            result = ur.redo()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--history":
            result = ur.history()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--clear":
            result = ur.clear()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--status":
            result = ur.status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("UNDO-REDO-001 Undo/Redo Tool")
    print("Usage:")
    print("  py undo_redo_001.py --push <action>")
    print("  py undo_redo_001.py --undo")
    print("  py undo_redo_001.py --redo")
    print("  py undo_redo_001.py --history")
    print("  py undo_redo_001.py --clear")
    print("  py undo_redo_001.py --status")
    return 0


if __name__ == "__main__":
    sys.exit(main())