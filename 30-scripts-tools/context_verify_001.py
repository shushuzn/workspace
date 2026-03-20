#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Context Verify - 验证 7 个核心文件正确加载
"""
import json
from pathlib import Path
from datetime import datetime

def verify():
    required_files = [
        "SOUL.md",
        "USER.md",
        "AGENTS.md",
        "TOOLS.md",
        "HEARTBEAT.md",
        "13-memory/MEMORY.md",
        "13-memory/2026-03-20.md"
    ]
    
    results = []
    total_size = 0
    
    for file_path in required_files:
        fp = Path(file_path)
        if fp.exists():
            size = fp.stat().st_size
            total_size += size
            results.append({"file": file_path, "status": "ok", "size": size})
        else:
            results.append({"file": file_path, "status": "missing"})
    
    passed = all(r["status"] == "ok" for r in results)
    
    return {
        "status": "pass" if passed else "fail",
        "files_checked": len(results),
        "total_size_kb": round(total_size / 1024, 2),
        "target_kb": 100,
        "result": "通过" if passed else "失败",
        "server_time": datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
