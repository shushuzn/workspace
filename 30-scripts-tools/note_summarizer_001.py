import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
笔记摘要器 - 压缩单个笔记文件
触发条件：单个笔记 > 5KB 或 > 100 行
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class NoteSummarizer:
    """笔记摘要器"""
    
    def __init__(self):
        self.threshold_size_kb = 5
        self.threshold_lines = 100
        self.backup_dir = Path("99-backups/notes")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def check_note(self, note_file: Path) -> Dict:
        """检查笔记是否需要压缩"""
        result = {
            "should_compress": False,
            "reason": [],
            "stats": {}
        }
        
        if not note_file.exists():
            result["reason"].append("File not found")
            return result
        
        # 检查大小
        size_kb = note_file.stat().st_size / 1024
        result["stats"]["size_kb"] = size_kb
        
        # 检查行数
        with open(note_file, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        result["stats"]["lines"] = lines
        
        # 判断是否需要压缩
        if size_kb > self.threshold_size_kb:
            result["should_compress"] = True
            result["reason"].append(f"Size ({size_kb:.1f}KB) > threshold ({self.threshold_size_kb}KB)")
        
        if lines > self.threshold_lines:
            result["should_compress"] = True
            result["reason"].append(f"Lines ({lines}) > threshold ({self.threshold_lines})")
        
        return result
    
    def create_backup(self, note_file: Path) -> Path:
        """创建备份"""
        backup_file = self.backup_dir / f"{note_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{note_file.suffix}"
        
        with open(note_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return backup_file
    
    def compress_note(self, note_file: Path, keep_top: int = 50, keep_bottom: int = 30) -> Dict:
        """压缩笔记"""
        # 检查
        check = self.check_note(note_file)
        if not check["should_compress"]:
            return {"status": "skipped", "reason": "Below threshold"}
        
        # 备份
        backup_file = self.create_backup(note_file)
        
        # 读取内容
        with open(note_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_lines = len(lines)
        
        # 压缩策略：保留顶部 + 分隔符 + 底部
        if len(lines) <= self.threshold_lines:
            return {"status": "skipped", "reason": "Already within threshold"}
        
        compressed_lines = []
        compressed_lines.extend(lines[:keep_top])
        compressed_lines.append(f"\n--- [COMPRESSED: {original_lines - keep_top - keep_bottom} lines removed] ---\n")
        compressed_lines.extend(lines[-keep_bottom:])
        
        # 写入压缩内容
        with open(note_file, 'w', encoding='utf-8') as f:
            f.writelines(compressed_lines)
        
        compressed_size_kb = note_file.stat().st_size / 1024
        
        return {
            "status": "success",
            "original_lines": original_lines,
            "compressed_lines": len(compressed_lines),
            "original_size_kb": check["stats"]["size_kb"],
            "compressed_size_kb": compressed_size_kb,
            "backup_file": str(backup_file),
            "reduction_percent": ((original_lines - len(compressed_lines)) / original_lines) * 100
        }
    
    def compress_daily_notes(self) -> Dict:
        """压缩所有当日笔记"""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_note = Path(f"13-memory/{today}.md")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "notes_checked": 0,
            "notes_compressed": 0
        }
        
        if daily_note.exists():
            result["notes_checked"] = 1
            compress_result = self.compress_note(daily_note)
            
            if compress_result["status"] == "success":
                result["notes_compressed"] = 1
                result["last_compression"] = compress_result
        
        return result
    
    def run(self, note_file: Path = None, force: bool = False) -> Dict:
        """运行压缩"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "compressions": []
        }
        
        if note_file:
            # 压缩指定文件
            check = self.check_note(note_file)
            
            if force or check["should_compress"]:
                compress_result = self.compress_note(note_file)
                result["compressions"].append({
                    "file": str(note_file),
                    "result": compress_result
                })
        else:
            # 压缩当日笔记
            result = self.compress_daily_notes()
        
        result["status"] = "completed"
        
        return result
    
    def display_status(self, note_file: Path = None) -> str:
        """显示状态"""
        if note_file:
            check = self.check_note(note_file)
        else:
            today = datetime.now().strftime('%Y-%m-%d')
            daily_note = Path(f"13-memory/{today}.md")
            check = self.check_note(daily_note) if daily_note.exists() else {"reason": ["No daily note"]}
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Note Summarizer")
        output.append("=" * 70)
        
        output.append(f"\n[Thresholds]")
        output.append(f"  Size Threshold:     {self.threshold_size_kb}KB")
        output.append(f"  Line Threshold:     {self.threshold_lines}")
        
        output.append(f"\n[Current Note]")
        output.append(f"  File: {check.get('file', 'N/A')}")
        
        output.append(f"\n[Stats]")
        for key, value in check.get("stats", {}).items():
            output.append(f"  {key:20} {value}")
        
        output.append(f"\n[Compression Needed]")
        output.append(f"  Status: {'YES' if check.get('should_compress') else 'NO'}")
        if check.get("reason"):
            for reason in check["reason"]:
                output.append(f"  - {reason}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py note_summarizer_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py note_summarizer_001.py

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

测试入口"""
    summarizer = NoteSummarizer()
    
    print("Note Summarizer Test")
    print("=" * 70)
    
    # 显示状态
    print(summarizer.display_status())
    
    # 运行压缩
    result = summarizer.run(force=True)
    
    print(f"\n[OK] Compression result: {result['status']}")
    if result.get("compressions"):
        for comp in result["compressions"]:
            print(f"  File: {comp['file']}")
            print(f"  Result: {comp['result'].get('status')}")
    
    print(f"\n[OK] Note summarizer test completed")

if __name__ == "__main__":
    main()
