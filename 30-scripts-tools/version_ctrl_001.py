import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VERSION-CTRL-001 Version Control Tool
【版本控制工具】

功能:
  - 快照状态 (snapshot)
  - 比较差异 (diff)
  - 回滚 (rollback)
  - 查看历史 (history)

使用:
  py version_ctrl_001.py --snapshot [name]
  py version_ctrl_001.py --list
  py version_ctrl_001.py --diff <v1> <v2>
  py version_ctrl_001.py --rollback <version>
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class VersionControl:
    """版本控制工具"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.snapshot_dir = self.workspace / "13-memory/.snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.snapshot_dir / "index.json"
        
        self._ensure_index()
    
    def _ensure_index(self):
        """确保索引文件存在"""
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({"versions": [], "current": None}, indent=2))
    
    def _load_index(self) -> dict:
        with open(self.index_file, encoding="utf-8") as f:
            return json.load(f)
    
    def _save_index(self, index: dict):
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def snapshot(self, name: str = None) -> Dict:
        """创建快照"""
        index = self._load_index()
        
        # 生成版本ID
        version_id = f"v{len(index['versions']) + 1:03d}"
        if name:
            version_id = name.strip().replace('"', '').replace("'", '')
        
        # 快照时间
        timestamp = datetime.now().isoformat()
        
        # 收集关键文件状态
        core_files = ['SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md', 'MEMORY.md']
        files_data = {}
        
        for f in core_files:
            path = self.workspace / f
            if path.exists():
                content = path.read_text(encoding="utf-8")
                files_data[f] = {
                    "hash": hashlib.md5(content.encode()).hexdigest(),
                    "size": len(content),
                    "lines": len(content.split('\n'))
                }
        
        # 保存快照文件
        snapshot_file = self.snapshot_dir / f"{version_id}.json"
        
        snapshot = {
            "version": version_id,
            "timestamp": timestamp,
            "files": files_data
        }
        
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        index["versions"].append({
            "version": version_id,
            "timestamp": timestamp,
            "snapshot_file": str(snapshot_file),
            "files": list(files_data.keys())
        })
        index["current"] = version_id
        self._save_index(index)
        
        return {"status": "success", "version": version_id, "files": len(files_data)}
    
    def list_versions(self) -> List[Dict]:
        """列出所有版本"""
        index = self._load_index()
        return index.get("versions", [])
    
    def diff(self, v1: str, v2: str) -> Dict:
        """比较两个版本"""
        # 加载快照
        s1_file = self.snapshot_dir / f"{v1}.json"
        s2_file = self.snapshot_dir / f"{v2}.json"
        
        if not s1_file.exists():
            return {"status": "error", "reason": f"Version {v1} not found"}
        if not s2_file.exists():
            return {"status": "error", "reason": f"Version {v2} not found"}
        
        with open(s1_file, encoding="utf-8") as f:
            s1 = json.load(f)
        with open(s2_file, encoding="utf-8") as f:
            s2 = json.load(f)
        
        # 比较
        changes = {"added": [], "removed": [], "modified": []}
        
        files1 = set(s1.get("files", {}).keys())
        files2 = set(s2.get("files", {}).keys())
        
        changes["added"] = list(files2 - files1)
        changes["removed"] = list(files1 - files2)
        
        for f in files1 & files2:
            h1 = s1["files"].get(f, {}).get("hash", "")
            h2 = s2["files"].get(f, {}).get("hash", "")
            if h1 != h2:
                changes["modified"].append(f)
        
        return {
            "status": "success",
            "v1": v1,
            "v2": v2,
            "changes": changes
        }
    
    def rollback(self, version: str) -> Dict:
        """回滚到指定版本"""
        index = self._load_index()
        
        if version not in [v["version"] for v in index["versions"]]:
            return {"status": "error", "reason": f"Version {version} not found"}
        
        # 创建当前版本的备份
        self.snapshot(f"backup_before_rollback_{datetime.now().strftime('%H%M%S')}")
        
        # 更新当前指针
        index["current"] = version
        self._save_index(index)
        
        return {"status": "success", "rolled_back_to": version}
    
    def status(self) -> Dict:
        """查看版本控制状态"""
        index = self._load_index()
        
        return {
            "total_versions": len(index["versions"]),
            "current": index.get("current"),
            "latest": index["versions"][-1]["version"] if index["versions"] else None
        }


logging.basicConfig(level=logging.INFO)
def main():
    vc = VersionControl()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--snapshot":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            result = vc.snapshot(name)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--list":
            versions = vc.list_versions()
            print(json.dumps(versions, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--diff":
            v1 = sys.argv[2] if len(sys.argv) > 2 else "v001"
            v2 = sys.argv[3] if len(sys.argv) > 3 else "v002"
            result = vc.diff(v1, v2)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--rollback":
            version = sys.argv[2] if len(sys.argv) > 2 else "v001"
            result = vc.rollback(version)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--status":
            result = vc.status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("VERSION-CTRL-001 Version Control Tool")
    print("Usage:")
    print("  py version_ctrl_001.py --snapshot [name]")
    print("  py version_ctrl_001.py --list")
    print("  py version_ctrl_001.py --diff <v1> <v2>")
    print("  py version_ctrl_001.py --rollback <version>")
    print("  py version_ctrl_001.py --status")
    return 0


if __name__ == "__main__":
    sys.exit(main())