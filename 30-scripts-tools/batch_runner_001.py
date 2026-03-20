#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BATCH-001 Batch Task Runner
【通用批量任务运行器】

功能:
  - 批量执行命令
  - 并行/串行执行
  - 进度追踪
  - 结果汇总

通用性: 适用于任何命令行任务
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 配置
BATCH_DIR = Path("60-DATA/batch_001")
CONFIG_FILE = Path("30-scripts-tools/batch_001_config.json")


class BatchRunner:
    """批量任务运行器"""
    
    def __init__(self):
        self.batch_dir = BATCH_DIR
        self.config = self._load_config()
        
        self.batch_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_file = self.batch_dir / "batch_results.json"
        self.queue_file = self.batch_dir / "task_queue.json"
    
    def _load_config(self) -> dict:
        default = {
            "max_workers": 4,
            "timeout": 60,
            "retry_failed": False,
            "max_retries": 2
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def run_command(self, cmd: str, timeout: int = None) -> dict:
        """执行单个命令"""
        if timeout is None:
            timeout = self.config.get("timeout", 60)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path("D:/OpenClaw/workspace"))
            )
            
            return {
                "command": cmd,
                "status": "SUCCESS" if result.returncode == 0 else "FAILED",
                "returncode": result.returncode,
                "stdout": result.stdout[:1000] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "command": cmd,
                "status": "TIMEOUT",
                "error": f"Command timed out after {timeout}s",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "command": cmd,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_batch(self, commands: list, parallel: bool = False) -> dict:
        """批量执行命令"""
        results = []
        
        if parallel:
            # 并行执行
            max_workers = self.config.get("max_workers", 4)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_cmd = {executor.submit(self.run_command, cmd): cmd for cmd in commands}
                
                for future in as_completed(future_to_cmd):
                    result = future.result()
                    results.append(result)
        else:
            # 串行执行
            for cmd in commands:
                result = self.run_command(cmd)
                results.append(result)
        
        # 汇总
        success = sum(1 for r in results if r.get("status") == "SUCCESS")
        failed = sum(1 for r in results if r.get("status") in ["FAILED", "ERROR"])
        timeout = sum(1 for r in results if r.get("status") == "TIMEOUT")
        
        summary = {
            "total": len(commands),
            "success": success,
            "failed": failed,
            "timeout": timeout,
            "pass_rate": round(success / len(commands) * 100, 1) if commands else 0,
            "parallel": parallel,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存
        self._save_results(results, summary)
        
        return {
            "summary": summary,
            "results": results
        }
    
    def run_from_file(self, file_path: str, parallel: bool = False) -> dict:
        """从文件读取命令批量执行"""
        p = Path(file_path)
        
        if not p.exists():
            return {"status": "error", "message": "File not found"}
        
        commands = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    commands.append(line)
        
        return self.run_batch(commands, parallel)
    
    def _save_results(self, results: list, summary: dict):
        data = {
            "summary": summary,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_results(self) -> dict:
        if not self.results_file.exists():
            return {"status": "error", "message": "No results"}
        
        with open(self.results_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def add_to_queue(self, commands: list):
        """添加到任务队列"""
        queue = []
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r", encoding="utf-8") as f:
                    queue = json.load(f)
            except:
                pass
        
        queue.extend(commands)
        
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "queued": len(commands), "total": len(queue)}
    
    def run_queue(self, parallel: bool = False) -> dict:
        """执行任务队列"""
        if not self.queue_file.exists():
            return {"status": "error", "message": "No queue"}
        
        with open(self.queue_file, "r", encoding="utf-8") as f:
            commands = json.load(f)
        
        if not commands:
            return {"status": "error", "message": "Empty queue"}
        
        result = self.run_batch(commands, parallel)
        
        # 清空队列
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        
        return result


def main():
    runner = BatchRunner()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run":
            # 从参数读取命令
            commands = sys.argv[2].split(";;") if len(sys.argv) > 2 else []
            if not commands:
                return 1
            result = runner.run_batch(commands)
            print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--file":
            file_path = sys.argv[2] if len(sys.argv) > 2 else "commands.txt"
            parallel = "--parallel" in sys.argv
            result = runner.run_from_file(file_path, parallel)
            print(json.dumps(result.get("summary", {}), ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--queue":
            parallel = "--parallel" in sys.argv
            result = runner.run_queue(parallel)
            print(json.dumps(result.get("summary", {}), ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--add":
            commands = sys.argv[2].split(";;") if len(sys.argv) > 2 else []
            result = runner.add_to_queue(commands)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--results":
            result = runner.get_results()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("BATCH-001 Batch Task Runner")
    print("Usage:")
    print("  py batch_001_runner.py --run 'cmd1;;cmd2;;cmd3'     # Run commands")
    print("  py batch_001_runner.py --file commands.txt          # From file")
    print("  py batch_001_runner.py --queue                      # Run queue")
    print("  py batch_001_runner.py --add 'cmd1;;cmd2'          # Add to queue")
    print("  py batch_001_runner.py --results                    # Get results")
    print("")
    print("Options:")
    print("  --parallel           # Run in parallel")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())