import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动会话压缩器 v1.0

功能：
1. 每 2 小时自动检查会话是否需要压缩
2. 自动执行 post_session_compress.py
3. 验证压缩效果 (<100KB)
4. 记录压缩日志

使用：
  py auto_session_compressor.py --auto
  py auto_session_compressor.py --check
  py auto_session_compressor.py --compress
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


class AutoSessionCompressor:
    """自动会话压缩器"""
    
    def __init__(self):
        self.workspace = Path("D:/OpenClaw/workspace")
        self.compress_script = self.workspace / "30-scripts-tools/post_session_compress.py"
        self.checker_script = self.workspace / "30-scripts-tools/session_end_checker.py"
        self.log_file = self.workspace / "13-memory/session-compression-log.jsonl"
        self.config = {
            "check_interval_hours": 2,
            "max_context_size_kb": 100,
            "target_size_kb": 5,
            "compression_rate_min": 0.8
        }
    
    def check_compression_needed(self) -> dict:
        """
        检查是否需要压缩
        
        Returns:
            dict: 检查结果
        """
        result = {
            "needs_compression": False,
            "current_size_kb": 0,
            "last_compression": None,
            "hours_since_last": 0
        }
        
        # 检查今日笔记文件
        today = datetime.now().strftime("%Y-%m-%d")
        daily_note = self.workspace / f"13-memory/{today}.md"
        
        if daily_note.exists():
            size_kb = daily_note.stat().st_size / 1024
            result["current_size_kb"] = round(size_kb, 2)
            
            if size_kb > self.config["max_context_size_kb"]:
                result["needs_compression"] = True
        
        # 检查上次压缩时间
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    result["last_compression"] = last_entry.get("timestamp")
                    
                    last_time = datetime.fromisoformat(last_entry["timestamp"])
                    hours_since = (datetime.now() - last_time).total_seconds() / 3600
                    result["hours_since_last"] = round(hours_since, 1)
                    
                    # 如果超过检查间隔，需要压缩
                    if hours_since >= self.config["check_interval_hours"]:
                        result["needs_compression"] = True
        
        return result
    
    def execute_compression(self) -> dict:
        """
        执行压缩
        
        Returns:
            dict: 压缩结果
        """
        result = {
            "success": False,
            "before_size_kb": 0,
            "after_size_kb": 0,
            "compression_rate": 0,
            "message": ""
        }
        
        # 检查压缩前大小
        today = datetime.now().strftime("%Y-%m-%d")
        daily_note = self.workspace / f"13-memory/{today}.md"
        
        if daily_note.exists():
            result["before_size_kb"] = round(daily_note.stat().st_size / 1024, 2)
        
        # 执行压缩脚本
        try:
            cmd = [sys.executable, str(self.compress_script), "--auto"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.workspace)
            )
            
            if proc.returncode == 0:
                result["success"] = True
                
                # 检查压缩后大小
                if daily_note.exists():
                    result["after_size_kb"] = round(daily_note.stat().st_size / 1024, 2)
                    
                    if result["before_size_kb"] > 0:
                        result["compression_rate"] = round(
                            1 - (result["after_size_kb"] / result["before_size_kb"]),
                            2
                        )
                
                result["message"] = "压缩成功"
            else:
                result["message"] = f"压缩失败：{proc.stderr}"
                
        except subprocess.TimeoutExpired:
            result["message"] = "压缩超时 (60s)"
        except Exception as e:
            result["message"] = str(e)
        
        # 记录日志
        self._log_compression(result)
        
        return result
    
    def _log_compression(self, result: dict) -> None:
        """记录压缩日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "before_size_kb": result.get("before_size_kb", 0),
            "after_size_kb": result.get("after_size_kb", 0),
            "compression_rate": result.get("compression_rate", 0),
            "success": result.get("success", False),
            "message": result.get("message", "")
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[WARN] 记录日志失败：{e}")
    
    def run_auto_check(self) -> None:
        """自动检查模式"""
        print("=" * 70)
        print(" " * 20 + "自动会话压缩检查")
        print("=" * 70)
        
        check_result = self.check_compression_needed()
        
        print(f"\n当前大小：{check_result['current_size_kb']:.2f} KB")
        print(f"限制大小：{self.config['max_context_size_kb']} KB")
        print(f"上次压缩：{check_result['last_compression'] or '无'}")
        print(f"距上次：{check_result['hours_since_last']:.1f} 小时")
        print(f"检查间隔：{self.config['check_interval_hours']} 小时")
        
        if check_result['needs_compression']:
            print("\n[NEEDS COMPRESSION] 需要压缩")
            print("\n执行压缩...")
            compress_result = self.execute_compression()
            
            print(f"\n压缩前：{compress_result['before_size_kb']:.2f} KB")
            print(f"压缩后：{compress_result['after_size_kb']:.2f} KB")
            print(f"压缩率：{compress_result['compression_rate']:.0%}")
            print(f"状态：{'✅ 成功' if compress_result['success'] else '❌ 失败'}")
        else:
            print("\n[OK] 不需要压缩")
    
    def run_manual_compress(self) -> None:
        """手动压缩模式"""
        print("=" * 70)
        print(" " * 20 + "手动会话压缩")
        print("=" * 70)
        
        print("\n执行压缩...")
        result = self.execute_compression()
        
        print(f"\n压缩前：{result['before_size_kb']:.2f} KB")
        print(f"压缩后：{result['after_size_kb']:.2f} KB")
        print(f"压缩率：{result['compression_rate']:.0%}")
        print(f"状态：{'✅ 成功' if result['success'] else '❌ 失败'}")
        print(f"消息：{result['message']}")


logging.basicConfig(level=logging.INFO)
def main() -> None:
    """主函数"""
    compressor = AutoSessionCompressor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--auto':
            compressor.run_auto_check()
        elif sys.argv[1] == '--compress':
            compressor.run_manual_compress()
        elif sys.argv[1] == '--check':
            result = compressor.check_compression_needed()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("用法：py auto_session_compressor.py [--auto|--compress|--check]")
    else:
        # 默认自动检查
        compressor.run_auto_check()


if __name__ == '__main__':
    main()
