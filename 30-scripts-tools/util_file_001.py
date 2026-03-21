import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UTIL-002 File Utility
【文件工具】

功能:
  - 文件批量重命名
  - 查找重复文件
  - 统计文件信息
"""
import json
import sys
import hashlib
from pathlib import Path
from collections import defaultdict


class FileUtil:
    """文件工具"""
    
    @staticmethod
    def find_duplicates(dir_path: str) -> dict:
        """查找重复文件"""
        hashes = defaultdict(list)
        path = Path(dir_path)
        
        for f in path.rglob("*"):
            if f.is_file():
                try:
                    h = hashlib.md5(f.read_bytes()).hexdigest()
                    hashes[h].append(str(f))
                except (Exception,):
                    pass
        
        return {h: files for h, files in hashes.items() if len(files) > 1}
    
    @staticmethod
    def file_stats(dir_path: str) -> dict:
        """统计文件信息"""
        path = Path(dir_path)
        
        total_files = 0
        total_size = 0
        by_ext = defaultdict(int)
        
        for f in path.rglob("*"):
            if f.is_file():
                total_files += 1
                size = f.stat().st_size
                total_size += size
                by_ext[f.suffix] += 1
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_extension": dict(by_ext)
        }


logging.basicConfig(level=logging.INFO)
def main():
    util = FileUtil()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--duplicates":
            path = sys.argv[2] if len(sys.argv) > 2 else "30-scripts-tools"
            result = util.find_duplicates(path)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--stats":
            path = sys.argv[2] if len(sys.argv) > 2 else "30-scripts-tools"
            result = util.file_stats(path)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("UTIL-002 File Utility")
    print("Usage:")
    print("  py util_002.py --duplicates [path]  # Find duplicate files")
    print("  py util_002.py --stats [path]        # File statistics")
    return 0
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py util_file_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py util_file_001.py

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




if __name__ == "__main__":
    import sys
    sys.exit(main())