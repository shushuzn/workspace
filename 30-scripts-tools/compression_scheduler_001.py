import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一压缩调度器 - 协调会话/记忆/笔记三个独立压缩通道
策略：分别检查阈值，独立触发压缩
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# 导入三个压缩器
from session_compressor import SessionCompressor
from memory_distiller import MemoryDistiller
from note_summarizer import NoteSummarizer

class CompressionScheduler:
    """统一压缩调度器"""
    
    def __init__(self):
        self.session_compressor = SessionCompressor()
        self.memory_distiller = MemoryDistiller()
        self.note_summarizer = NoteSummarizer()
        self.log_file = Path("13-memory/compression_log.json")
    
    def check_all_thresholds(self) -> Dict:
        """检查所有压缩阈值"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session": self.session_compressor.check_threshold(),
            "memory": self.memory_distiller.check_threshold(),
            "note": self.note_summarizer.check_note(Path(f"13-memory/{datetime.now().strftime('%Y-%m-%d')}.md"))
        }
    
    def run_compression(self, channel: str = "all", force: bool = False) -> Dict:
        """运行压缩
        
        Args:
            channel: "session", "memory", "note", or "all"
            force: 强制压缩，忽略阈值
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "forced": force,
            "results": {}
        }
        
        if channel in ["session", "all"]:
            result["results"]["session"] = self.session_compressor.run(force=force)
        
        if channel in ["memory", "all"]:
            result["results"]["memory"] = self.memory_distiller.run(force=force)
        
        if channel in ["note", "all"]:
            result["results"]["note"] = self.note_summarizer.run(force=force)
        
        # 记录日志
        self._log_compression(result)
        
        return result
    
    def _log_compression(self, result: Dict):
        """记录压缩日志"""
        logs = []
        
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(result)
        
        # 保留最近 100 条记录
        logs = logs[-100:]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> Dict:
        """获取压缩统计"""
        stats = {
            "total_compressions": 0,
            "session_compressions": 0,
            "memory_distillations": 0,
            "note_summaries": 0,
            "total_size_saved_kb": 0
        }
        
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            stats["total_compressions"] = len(logs)
            
            for log in logs:
                results = log.get("results", {})
                
                if results.get("session", {}).get("status") == "success":
                    stats["session_compressions"] += 1
                
                if results.get("memory", {}).get("status") == "success":
                    stats["memory_distillations"] += 1
                
                if results.get("note", {}).get("status") == "success":
                    stats["note_summaries"] += 1
                    # 计算节省空间
                    note_result = results["note"]
                    if note_result.get("last_compression"):
                        orig = note_result["last_compression"].get("original_size_kb", 0)
                        comp = note_result["last_compression"].get("compressed_size_kb", 0)
                        stats["total_size_saved_kb"] += (orig - comp)
        
        return stats
    
    def display_status(self) -> str:
        """显示状态"""
        thresholds = self.check_all_thresholds()
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Unified Compression Scheduler")
        output.append("=" * 70)
        
        output.append(f"\n[Compression Strategy]")
        output.append(f"  Session:  Independent (tokens > 10000 OR lines > 200)")
        output.append(f"  Memory:   Independent (size > 50KB OR unprocessed > 10)")
        output.append(f"  Note:     Independent (size > 5KB OR lines > 100)")
        
        output.append(f"\n[Threshold Status]")
        
        # Session
        session = thresholds["session"]
        output.append(f"  Session:  {'NEEDS COMPRESS' if session['should_compress'] else 'OK'}")
        if session.get("reason"):
            for reason in session["reason"]:
                output.append(f"            - {reason}")
        
        # Memory
        memory = thresholds["memory"]
        output.append(f"  Memory:   {'NEEDS DISTILL' if memory['should_distill'] else 'OK'}")
        if memory.get("reason"):
            for reason in memory["reason"]:
                output.append(f"            - {reason}")
        
        # Note
        note = thresholds["note"]
        output.append(f"  Note:     {'NEEDS SUMMARY' if note['should_compress'] else 'OK'}")
        if note.get("reason"):
            for reason in note["reason"]:
                output.append(f"            - {reason}")
        
        output.append(f"\n[Historical Stats]")
        output.append(f"  Total Compressions:     {stats['total_compressions']}")
        output.append(f"  Session Compressions:   {stats['session_compressions']}")
        output.append(f"  Memory Distillations:   {stats['memory_distillations']}")
        output.append(f"  Note Summaries:         {stats['note_summaries']}")
        output.append(f"  Total Size Saved:       {stats['total_size_saved_kb']:.1f}KB")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)
    
    def run(self, auto: bool = True) -> Dict:
        """运行调度器
        
        Args:
            auto: True=检查阈值后决定，False=强制全部压缩
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "mode": "auto" if auto else "forced",
            "actions_taken": []
        }
        
        thresholds = self.check_all_thresholds()
        
        # 独立检查每个通道
        if auto:
            if thresholds["session"]["should_compress"]:
                result["actions_taken"].append("session")
                result["results"]["session"] = self.session_compressor.run(force=False)
            
            if thresholds["memory"]["should_distill"]:
                result["actions_taken"].append("memory")
                result["results"]["memory"] = self.memory_distiller.run(force=False)
            
            if thresholds["note"]["should_compress"]:
                result["actions_taken"].append("note")
                result["results"]["note"] = self.note_summarizer.run(force=False)
        else:
            # 强制全部压缩
            result = self.run_compression(channel="all", force=True)
        
        result["status"] = "completed"
        result["channels_triggered"] = len(result.get("actions_taken", []))
        
        # 记录日志
        self._log_compression(result)
        
        return result

logging.basicConfig(level=logging.INFO)
def main():
    """测试入口"""
    scheduler = CompressionScheduler()
    
    print("Unified Compression Scheduler Test")
    print("=" * 70)
    
    # 显示状态
    print(scheduler.display_status())
    
    # 运行自动调度
    print("\n[Running Auto Scheduler...]")
    result = scheduler.run(auto=True)
    
    print(f"\n[OK] Scheduler result: {result['status']}")
    print(f"  Mode: {result['mode']}")
    print(f"  Channels Triggered: {result['channels_triggered']}")
    if result.get("actions_taken"):
        print(f"  Actions: {', '.join(result['actions_taken'])}")
    
    print(f"\n[OK] Scheduler test completed")

if __name__ == "__main__":
    main()
