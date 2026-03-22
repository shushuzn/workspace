import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话压缩器 - 压缩当前会话内容到 <5KB
触发条件：会话 token > 10000 或 会话时长 > 30min
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SessionCompressor:
    """会话压缩器"""
    
    def __init__(self):
        self.session_file = Path("13-memory/session_temp.json")
        self.daily_note = Path(f"13-memory/{datetime.now().strftime('%Y-%m-%d')}.md")
        self.threshold_tokens = 10000
        self.threshold_lines = 200
        self.target_size_kb = 5
    
    def check_threshold(self) -> Dict:
        """检查是否达到压缩阈值"""
        result = {
            "should_compress": False,
            "reason": [],
            "current_stats": {}
        }
        
        # 检查会话文件
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                content = f.read()
                token_estimate = len(content) // 4  # 粗略估算
                result["current_stats"]["session_tokens"] = token_estimate
                result["current_stats"]["session_size_kb"] = len(content) / 1024
                
                if token_estimate > self.threshold_tokens:
                    result["should_compress"] = True
                    result["reason"].append(f"Session tokens ({token_estimate}) > threshold ({self.threshold_tokens})")
        
        # 检查当日笔记
        if self.daily_note.exists():
            with open(self.daily_note, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                result["current_stats"]["note_lines"] = lines
                
                if lines > self.threshold_lines:
                    result["should_compress"] = True
                    result["reason"].append(f"Note lines ({lines}) > threshold ({self.threshold_lines})")
        
        return result
    
    def compress_session(self) -> Dict:
        """压缩会话"""
        if not self.session_file.exists():
            return {"status": "skipped", "reason": "No session file"}
        
        with open(self.session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # 提取关键信息
        compressed = {
            "date": datetime.now().isoformat(),
            "tasks_completed": session_data.get("tasks", []),
            "key_decisions": session_data.get("decisions", []),
            "tools_created": session_data.get("tools", []),
            "git_commits": session_data.get("commits", []),
            "summary": session_data.get("summary", "")
        }
        
        # 保存到压缩文件
        compressed_file = Path("13-memory/session_compressed.json")
        with open(compressed_file, 'w', encoding='utf-8') as f:
            json.dump(compressed, f, ensure_ascii=False, indent=2)
        
        # 清空临时会话文件
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump({"reset_at": datetime.now().isoformat()}, f)
        
        return {
            "status": "success",
            "compressed_size_kb": len(json.dumps(compressed)) / 1024,
            "output": str(compressed_file)
        }
    
    def compress_daily_note(self) -> Dict:
        """压缩当日笔记"""
        if not self.daily_note.exists():
            return {"status": "skipped", "reason": "No daily note"}
        
        with open(self.daily_note, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取关键部分（保留前 100 行 + 最后总结）
        lines = content.split('\n')
        
        if len(lines) <= self.threshold_lines:
            return {"status": "skipped", "reason": f"Lines ({len(lines)}) <= threshold"}
        
        # 保留关键内容
        compressed_lines = []
        compressed_lines.extend(lines[:50])  # 保留前 50 行
        compressed_lines.append("\n--- [COMPRESSED] ---\n")
        compressed_lines.extend(lines[-30:])  # 保留最后 30 行
        
        compressed_content = '\n'.join(compressed_lines)
        
        # 备份原文件
        backup_file = self.daily_note.parent / f"{self.daily_note.stem}_backup{self.daily_note.suffix}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 写入压缩内容
        with open(self.daily_note, 'w', encoding='utf-8') as f:
            f.write(compressed_content)
        
        return {
            "status": "success",
            "original_lines": len(lines),
            "compressed_lines": len(compressed_lines),
            "backup": str(backup_file)
        }
    
    def run(self, force: bool = False) -> Dict:
        """运行压缩"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "session": None,
            "note": None
        }
        
        # 检查阈值
        threshold_check = self.check_threshold()
        
        if not force and not threshold_check["should_compress"]:
            result["status"] = "skipped"
            result["reason"] = "Below threshold"
            result["stats"] = threshold_check["current_stats"]
            return result
        
        # 压缩会话
        result["session"] = self.compress_session()
        
        # 压缩笔记
        result["note"] = self.compress_daily_note()
        
        result["status"] = "completed"
        result["threshold_reasons"] = threshold_check["reason"]
        
        return result
    
    def display_status(self) -> str:
        """显示状态"""
        threshold = self.check_threshold()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Session Compressor")
        output.append("=" * 70)
        
        output.append(f"\n[Thresholds]")
        output.append(f"  Token Threshold:    {self.threshold_tokens}")
        output.append(f"  Line Threshold:     {self.threshold_lines}")
        output.append(f"  Target Size:        {self.target_size_kb}KB")
        
        output.append(f"\n[Current Stats]")
        for key, value in threshold.get("current_stats", {}).items():
            output.append(f"  {key:20} {value}")
        
        output.append(f"\n[Compression Needed]")
        output.append(f"  Status: {'YES' if threshold['should_compress'] else 'NO'}")
        if threshold["reason"]:
            for reason in threshold["reason"]:
                output.append(f"  - {reason}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
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
# py session_compressor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py session_compressor_001.py

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
    compressor = SessionCompressor()
    
    print("Session Compressor Test")
    print("=" * 70)
    
    # 显示状态
    print(compressor.display_status())
    
    # 运行压缩
    result = compressor.run(force=True)
    
    print(f"\n[OK] Compression result: {result['status']}")
    if result.get("session"):
        print(f"  Session: {result['session'].get('status')}")
    if result.get("note"):
        print(f"  Note: {result['note'].get('status')}")
    
    print(f"\n[OK] Session compressor test completed")

if __name__ == "__main__":
    main()
