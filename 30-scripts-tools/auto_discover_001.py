#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-DISCOVER-001 Tool Auto Discovery (OPTIMIZED)
- Added caching
- Parallel file scanning
- Lazy loading
"""

import json, sys, re
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CACHE_FILE = Path("13-memory/.tool_discover_cache.json")
CACHE_TTL = 300  # 5 minutes

class ToolAutoDiscover:
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        self.registry_file = self.tools_dir / "tools_registry.json"
    
    def _get_cache(self):
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8", errors="replace"))
                if datetime.now().timestamp() - data.get("cache_time", 0) < CACHE_TTL:
                    return data.get("results")
            except:
                pass
        return None
    
    def _set_cache(self, results):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps({
            "cache_time": datetime.now().timestamp(),
            "results": results
        }, ensure_ascii=False), encoding="utf-8", errors="replace")
    
    def _extract_metadata(self, file_path):
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            name_match = re.search(r'["\'](\w+-\d{3})["\']', content)
            tool_id = name_match.group(1) if name_match else file_path.stem
            return {
                "tool_id": tool_id,
                "file_path": str(file_path.relative_to(self.workspace)),
                "category": self._get_category(file_path.name),
                "discovered_at": datetime.now().isoformat()
            }
        except:
            return None
    
    def _get_category(self, name):
        name_lower = name.lower()
        for kw, cat in [("test", "testing"), ("brainstorm", "brainstorm"), 
                        ("optim", "optimization"), ("export", "export"),
                        ("workflow", "workflow"), ("stock", "stock")]:
            if kw in name_lower:
                return cat
        return "auto"
    
    def _scan_parallel(self, files, max_workers=4):
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._extract_metadata, f): f for f in files}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        return results
    
    def scan_tools(self, use_cache=True):
        if use_cache:
            cached = self._get_cache()
            if cached:
                return {"status": "success", "discovered": len(cached), "cached": True}
        
        files = [f for f in self.tools_dir.glob("*.py") 
                 if not f.name.startswith("_") and not f.name.startswith("test_")]
        
        discovered = self._scan_parallel(files)
        self._set_cache(discovered)
        
        return {"status": "success", "discovered": len(discovered), "cached": False}
    
    def register_all(self):
        registry = json.loads(self.registry_file.read_text(encoding="utf-8", errors="replace")) if self.registry_file.exists() else {"tools": {}}
        
        if "tools" not in registry:
            registry["tools"] = {}
        
        cached = self._get_cache() or []
        registered = sum(1 for t in cached if t["tool_id"] not in registry["tools"])
        
        for tool in cached:
            if tool["tool_id"] not in registry["tools"]:
                registry["tools"][tool["tool_id"]] = tool
        
        self.registry_file.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8", errors="replace")
        
        return {"status": "success", "registered": registered, "total": len(registry["tools"])}
    
    def status(self):
        cached = self._get_cache() or []
        registry = json.loads(self.registry_file.read_text(encoding="utf-8", errors="replace")) if self.registry_file.exists() else {"tools": {}}
        
        return {
            "total_discovered": len(cached),
            "total_registered": len(registry.get("tools", {})),
            "cached": bool(cached)
        }
    
    def sync(self):
        return {"scan": self.scan_tools(), "register": self.register_all()}

if __name__ == "__main__":
    discover = ToolAutoDiscover()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--scan":
            print(json.dumps(discover.scan_tools(), ensure_ascii=False, indent=2))
        elif cmd == "--register":
            print(json.dumps(discover.register_all(), ensure_ascii=False, indent=2))
        elif cmd == "--status":
            print(json.dumps(discover.status(), ensure_ascii=False, indent=2))
        elif cmd == "--sync":
            print(json.dumps(discover.sync(), ensure_ascii=False, indent=2))
    else:
        print("AUTO-DISCOVER-001 - Optimized Tool Discovery")
        print("  --scan  --register  --status  --sync")
