import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPTIMIZE-MASTER-001 优化大师
【整合所有优化工具的统一入口】

功能:
  1. 统一调用各个优化工具
  2. 自动选择最佳优化策略
  3. 一键执行完整优化流程
  4. 记录优化历史和效果

现有优化工具:
  - smart_compress_001.py (智能压缩v2)
  - smart_compress_002.py (超级压缩v3)
  - prompt_optimizer_001.py (提示词优化)
  - brainstorm_optimize_001.py (头脑风暴优化器)
  - workflow_optimizer_001.py (工作流优化)
  - smart_cache_001.py (智能缓存)

使用:
  py optimize_master_001.py --run           # 运行完整优化
  py optimize_master_001.py --compress      # 仅压缩
  py optimize_master_001.py --prompt        # 仅提示词优化
  py optimize_master_001.py --status       # 查看状态
  py optimize_master_001.py --suggest       # 获取优化建议
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class OptimizeMaster:
    """优化大师"""
    
    # 可用优化工具
    OPTIMIZERS = {
        "compress": {
            "script": "smart_compress_002.py",
            "args": ["--compress", "extreme"],
            "description": "压缩文件和会话"
        },
        "prompt": {
            "script": "prompt_optimizer_001.py",
            "args": ["--optimize"],
            "description": "优化提示词"
        },
        "brainstorm": {
            "script": "brainstorm_optimize_001.py",
            "args": ["--list"],
            "description": "头脑风暴优化ideas"
        },
        "workflow": {
            "script": "workflow_optimizer_001.py",
            "args": ["--analyze"],
            "description": "分析工作流"
        }
    }
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        self.log_file = self.workspace / "13-memory/optimization/master_log.json"
        
        self._ensure_log()
    
    def _ensure_log(self):
        """确保日志文件存在"""
        if not self.log_file.exists():
            self.log_file.write_text(json.dumps([], ensure_ascii=False, indent=2))
    
    def _load_log(self) -> List[Dict]:
        """加载日志"""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_log(self, log: List[Dict]):
        """保存日志"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    
    def run_optimizer(self, optimizer_name: str) -> Dict:
        """运行指定的优化器"""
        if optimizer_name not in self.OPTIMIZERS:
            return {"status": "error", "reason": f"Unknown optimizer: {optimizer_name}"}
        
        optimizer = self.OPTIMIZERS[optimizer_name]
        script = self.tools_dir / optimizer["script"]
        
        if not script.exists():
            return {"status": "error", "reason": f"Script not found: {optimizer['script']}"}
        
        try:
            cmd = [sys.executable, str(script)] + optimizer["args"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.workspace)
            )
            
            # 记录
            log = self._load_log()
            log.append({
                "timestamp": datetime.now().isoformat(),
                "optimizer": optimizer_name,
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout[:500] if result.returncode == 0 else result.stderr[:200]
            })
            self._save_log(log)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "optimizer": optimizer_name,
                "output": result.stdout[:500] if result.returncode == 0 else result.stderr[:200]
            }
            
        except subprocess.TimeoutExpired:
            return {"status": "error", "reason": "timeout"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def run_all_optimizers(self) -> Dict:
        """运行所有优化器"""
        results = []
        
        # 1. 压缩优化
        print("[1/4] Running compression optimizer...")
        results.append(("compress", self.run_optimizer("compress")))
        
        # 2. 提示词优化
        print("[2/4] Running prompt optimizer...")
        results.append(("prompt", self.run_optimizer("prompt")))
        
        # 3. 工作流分析
        print("[3/4] Running workflow analyzer...")
        results.append(("workflow", self.run_optimizer("workflow")))
        
        # 4. 头脑风暴ideas
        print("[4/4] Checking brainstorm ideas...")
        results.append(("brainstorm", self.run_optimizer("brainstorm")))
        
        # 汇总
        success = sum(1 for _, r in results if r.get("status") == "success")
        
        return {
            "status": "complete",
            "total": len(results),
            "success": success,
            "results": {name: r.get("status") for name, r in results}
        }
    
    def get_suggestions(self) -> Dict:
        """获取优化建议"""
        suggestions = []
        
        # 检查当前状态
        core_files = ['SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md', 'HEARTBEAT.md', 'MEMORY.md']
        for f in core_files:
            path = self.workspace / f
            if path.exists():
                content = path.read_text(encoding='utf-8')
                tokens = len(content) // 4
                if tokens > 5000:
                    suggestions.append(f"{f}: {tokens} tokens - consider compression")
        
        # 加载优化ideas
        ideas_file = self.workspace / "13-memory/optimization/optimization_ideas.json"
        if ideas_file.exists():
            with open(ideas_file, 'r', encoding='utf-8') as f:
                ideas = json.load(f)
            
            pending = [i for i in ideas if i.get("status") != "completed"]
            if pending:
                suggestions.append(f"Pending optimizations: {len(pending)}")
                for idea in pending[:3]:
                    suggestions.append(f"  - {idea.get('name')}: {idea.get('description')}")
        
        # 检查最近优化日志
        log = self._load_log()
        if log:
            last = log[-1]
            suggestions.append(f"Last optimization: {last.get('timestamp', 'unknown')}")
        
        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    
    def get_status(self) -> Dict:
        """获取优化状态"""
        # 优化工具列表
        tools_status = []
        for name, info in self.OPTIMIZERS.items():
            script = self.tools_dir / info["script"]
            tools_status.append({
                "name": name,
                "available": script.exists(),
                "description": info["description"]
            })
        
        # 最近的优化日志
        log = self._load_log()
        recent = log[-5:] if len(log) > 5 else log
        
        # 优化ideas
        ideas_file = self.workspace / "13-memory/optimization/optimization_ideas.json"
        ideas_status = {"completed": 0, "in_progress": 0, "pending": 0}
        if ideas_file.exists():
            with open(ideas_file, 'r', encoding='utf-8') as f:
                ideas = json.load(f)
            for idea in ideas:
                status = idea.get("status", "pending")
                if status in ideas_status:
                    ideas_status[status] += 1
        
        return {
            "tools": tools_status,
            "recent_log": recent,
            "ideas_status": ideas_status
        }


logging.basicConfig(level=logging.INFO)
def main():
    master = OptimizeMaster()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--run":
            result = master.run_all_optimizers()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--compress":
            result = master.run_optimizer("compress")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--prompt":
            result = master.run_optimizer("prompt")
            print(result.get("output", ""))
            return 0
        
        if cmd == "--status":
            result = master.get_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--suggest":
            result = master.get_suggestions()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("OPTIMIZE-MASTER-001 Optimization Master")
    print("")
    print("Usage:")
    print("  py optimize_master_001.py --run         # Run all optimizers")
    print("  py optimize_master_001.py --compress    # Compression only")
    print("  py optimize_master_001.py --prompt       # Prompt optimization")
    print("  py optimize_master_001.py --status      # View status")
    print("  py optimize_master_001.py --suggest     # Get suggestions")
    return 0


if __name__ == "__main__":
    sys.exit(main())