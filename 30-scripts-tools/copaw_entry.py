#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CoPaw Entry Point - 强制工作流入口点 (集成自动防护)

所有任务必须通过此入口点启动，确保主工作流被执行。
功能：
1. 初始化 execution-state.json
2. 绑定 Flow ID
3. 验证上下文加载
4. 记录会话开始
5. 强制使用 tool_executor
6. 【新增】自动激活防护层
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入自动防护层
try:
    from auto_protection_layer import create_protection_layer
    AUTO_PROTECTION_ENABLED = True
except ImportError:
    AUTO_PROTECTION_ENABLED = False

class CopawEntry:
    def __init__(self, task_name: str = None):
        self.task_name = task_name or "Unnamed Task"
        self.flow_id = "20260318-universal-workflow-001"
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now()
        self.workflow_dir = Path(f"flow-archive/{self.flow_id}")
        self.state_file = self.workflow_dir / "execution-state.json"
        self.tool_log = Path("30-scripts-tools/tool_call_log.jsonl")
        
        # 【新增】自动防护层
        self.protection = None
        if AUTO_PROTECTION_ENABLED:
            self.protection = create_protection_layer(self.session_id)
        
        print("="*60)
        print("CoPaw Entry Point - 强制工作流入口")
        print("="*60)
        print(f"Task: {self.task_name}")
        print(f"Flow ID: {self.flow_id}")
        print(f"Session ID: {self.session_id}")
        print(f"Start Time: {self.start_time.isoformat()}")
        if AUTO_PROTECTION_ENABLED:
            print(f"[防护] 自动防护层已激活")
        print("="*60)
        print("="*60)
    
    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"session-{timestamp}"
    
    def initialize_state(self) -> dict:
        """初始化 execution-state.json"""
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载 workflow.json 获取步骤
        workflow_file = self.workflow_dir / "workflow.json"
        with open(workflow_file, "r", encoding="utf-8") as f:
            workflow = json.load(f)
        
        total_steps = workflow.get("total_steps", 20)
        
        state = {
            "flow_id": self.flow_id,
            "task": self.task_name,
            "description": f"Task started via copaw_entry.py",
            "started_at": self.start_time.isoformat() + "+08:00",
            "current_step": 0,
            "total_steps": total_steps,
            "status": "initializing",
            "step_status": {},
            "completed_steps": [],
            "completion_percentage": 0,
            "workflow_compliance": False,
            "session_id": self.session_id,
            "entry_point": "copaw_entry.py",
            "mandatory_execution": True
        }
        
        # 保存初始状态
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] execution-state.json 已初始化")
        print(f"  路径：{self.state_file}")
        print(f"  总步骤：{total_steps}")
        
        return state
    
    def verify_context(self) -> bool:
        """Step 1: 验证上下文加载"""
        print(f"\n{'='*60}")
        print("Step 1: 上下文加载验证")
        print(f"{'='*60}")
        
        core_files = [
            "SOUL.md", "USER.md", "AGENTS.md", "TOOLS.md", "HEARTBEAT.md",
            "13-memory/MEMORY.md"
        ]
        
        today = datetime.now().strftime("%Y-%m-%d")
        core_files.append(f"13-memory/{today}.md")
        
        loaded = []
        missing = []
        total_size = 0
        
        for f in core_files:
            p = Path(f)
            if p.exists():
                size = p.stat().st_size
                loaded.append({"file": f, "size": size})
                total_size += size
            else:
                missing.append(f)
        
        valid = total_size < 100 * 1024 and len(missing) == 0
        
        print(f"加载文件：{len(loaded)}/{len(core_files)}")
        print(f"总大小：{total_size/1024:.1f}KB (目标<100KB)")
        print(f"缺失文件：{len(missing)}")
        print(f"验证结果：{'通过' if valid else '失败'}")
        print(f"{'='*60}\n")
        
        return valid
    
    def log_tool_call(self, tool_id: str, params: dict, result: str, duration: float):
        """记录工具调用"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_id": tool_id,
            "params": params,
            "result": result,
            "duration_seconds": duration,
            "session_id": self.session_id
        }
        
        self.tool_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tool_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"[TRACK] {tool_id} - {duration:.2f}s")
    
    def update_step(self, step_id: int, name: str, status: str, result: str):
        """更新步骤状态"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        state["current_step"] = step_id
        state["step_status"][str(step_id)] = {
            "name": name,
            "status": status,
            "started_at": datetime.now().isoformat() + "+08:00",
            "completed_at": datetime.now().isoformat() + "+08:00" if status == "completed" else None,
            "result": result
        }
        
        if status == "completed":
            state["completed_steps"].append(step_id)
            state["completion_percentage"] = int(len(state["completed_steps"]) / state["total_steps"] * 100)
        
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def finalize(self, success: bool = True):
        """会话结束 - 更新最终状态"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        state["status"] = "completed" if success else "failed"
        state["ended_at"] = end_time.isoformat() + "+08:00"
        state["duration_seconds"] = duration
        state["workflow_compliance"] = state["completion_percentage"] == 100
        
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print("会话结束")
        print(f"{'='*60}")
        print(f"状态：{'完成' if success else '失败'}")
        print(f"持续时间：{duration:.1f}s")
        print(f"完成率：{state['completion_percentage']}%")
        print(f"工作流合规：{state['workflow_compliance']}")
        print(f"{'='*60}\n")
    
    def run(self):
        """执行入口点流程"""
        try:
            # 初始化状态
            self.initialize_state()
            
            # Step 1: 验证上下文
            if not self.verify_context():
                print("[FAIL] 上下文验证失败")
                self.finalize(success=False)
                return False
            
            self.update_step(1, "上下文加载验证", "completed", "验证通过")
            
            print("\n[OK] CoPaw Entry 初始化完成")
            print("现在可以开始执行任务...")
            print("所有工具调用将通过 tool_executor 记录")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.finalize(success=False)
            return False


def main():
    """主函数 - 从命令行调用"""
    task_name = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Default Task"
    
    entry = CopawEntry(task_name)
    success = entry.run()
    
    # 保持入口点活跃，等待任务完成
    if success:
        print("\n" + "="*60)
        print("等待任务完成...")
        print("按 Ctrl+C 或调用 entry.finalize() 结束会话")
        print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
