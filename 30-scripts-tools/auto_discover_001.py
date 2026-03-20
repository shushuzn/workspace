#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-DISCOVER-001 Tool Auto Discovery
[Tool Auto Discovery - Scan and Register]

Usage:
  py auto_discover_001.py --scan
  py auto_discover_001.py --register
  py auto_discover_001.py --status
  py auto_discover_001.py --sync
"""

import json
import os
import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class ToolAutoDiscover:
    """Tool Auto Discovery"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        self.registry_file = self.tools_dir / "tools_registry.json"
        self.discover_file = self.workspace / "13-memory/.tool_discover.json"
        
        self._ensure_registry()
    
    def _ensure_registry(self):
        if not self.registry_file.exists():
            self.registry_file.write_text(
                json.dumps({"tools": {}}, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
    
    def _load_registry(self) -> dict:
        with open(self.registry_file, encoding="utf-8") as f:
            return json.load(f)
    
    def _save_registry(self, data: dict):
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_metadata(self, file_path: Path) -> Optional[dict]:
        try:
            content = file_path.read_text(encoding="utf-8")
            
            name_match = re.search(r'["\'](\w+-\d{3})["\']', content)
            tool_id = name_match.group(1) if name_match else file_path.stem
            
            desc_match = re.search(r'["\']([^"\']{10,100})["\']', content)
            description = desc_match.group(1) if desc_match else "Auto-discovered tool"
            
            category = "auto"
            if "test" in file_path.name.lower():
                category = "testing"
            elif "brainstorm" in file_path.name.lower():
                category = "brainstorm"
            elif "optim" in file_path.name.lower():
                category = "optimization"
            elif "export" in file_path.name.lower():
                category = "export"
            
            return {
                "tool_id": tool_id,
                "name": tool_id.replace("-", " ").title(),
                "description": description,
                "file_path": str(file_path.relative_to(self.workspace)),
                "category": category,
                "status": "auto_discovered",
                "discovered_at": datetime.now().isoformat(),
                "auto_discovery": True
            }
        except Exception:
            return None
    
    def scan_tools(self) -> Dict:
        discovered = []
        
        for file_path in self.tools_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            if file_path.name.startswith("test_"):
                continue
            
            metadata = self.extract_metadata(file_path)
            if metadata:
                discovered.append(metadata)
        
        for file_path in self.tools_dir.glob("*.bat"):
            discovered.append({
                "tool_id": file_path.stem.replace("-", "_"),
                "name": file_path.name,
                "description": f"Script: {file_path.name}",
                "file_path": str(file_path.relative_to(self.workspace)),
                "category": "script",
                "status": "auto_discovered",
                "discovered_at": datetime.now().isoformat(),
                "auto_discovery": True
            })
        
        self.discover_file.parent.mkdir(parents=True, exist_ok=True)
        self.discover_file.write_text(
            json.dumps({
                "discovered": discovered,
                "scanned_at": datetime.now().isoformat(),
                "total": len(discovered)
            }, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return {
            "status": "success",
            "discovered": len(discovered)
        }
    
    def register_all(self) -> Dict:
        if not self.discover_file.exists():
            return {"status": "error", "reason": "Run --scan first"}
        
        discover_data = json.loads(self.discover_file.read_text(encoding="utf-8"))
        registry = self._load_registry()
        
        registered = 0
        skipped = 0
        
        for tool in discover_data["discovered"]:
            tool_id = tool["tool_id"]
            
            if tool_id in registry.get("tools", {}):
                skipped += 1
                continue
            
            if "tools" not in registry:
                registry["tools"] = {}
            
            registry["tools"][tool_id] = tool
            registered += 1
        
        self._save_registry(registry)
        
        return {
            "status": "success",
            "registered": registered,
            "skipped": skipped,
            "total": len(registry.get("tools", {}))
        }
    
    def status(self) -> Dict:
        if not self.discover_file.exists():
            return {"status": "error", "reason": "Run --scan first"}
        
        discover_data = json.loads(self.discover_file.read_text(encoding="utf-8"))
        registry = self._load_registry()
        
        registered_ids = set(registry.get("tools", {}).keys())
        discovered_ids = set(t["tool_id"] for t in discover_data["discovered"])
        
        return {
            "scanned_at": discover_data["scanned_at"],
            "total_discovered": discover_data["total"],
            "total_registered": len(registry.get("tools", {})),
            "auto_discovered_count": len([t for t in discover_data["discovered"] if t.get("auto_discovery")]),
            "unregistered": list(discovered_ids - registered_ids)[:10]
        }
    
    def sync(self) -> Dict:
        scan_result = self.scan_tools()
        reg_result = self.register_all()
        
        return {
            "scan": scan_result,
            "register": reg_result
        }


def main():
    discover = ToolAutoDiscover()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--scan":
            result = discover.scan_tools()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--register":
            result = discover.register_all()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--status":
            result = discover.status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--sync":
            result = discover.sync()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("AUTO-DISCOVER-001 Tool Auto Discovery")
    print("Usage:")
    print("  py auto_discover_001.py --scan      # Scan tools")
    print("  py auto_discover_001.py --register  # Register discovered")
    print("  py auto_discover_001.py --status    # View status")
    print("  py auto_discover_001.py --sync      # Scan + Register")
    return 0


if __name__ == "__main__":
    sys.exit(main())
