#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话前钩子 - 强制检查工作流合规性
每次会话开始前自动运行，确保按主工作流执行
"""

import json
from pathlib import Path
from datetime import datetime
import sys

class WorkflowEnforcer:
    """工作流强制执行器"""
    
    REQUIRED_STEPS = [
        "上下文加载验证",
        "Flow ID 绑定",
        "任务解析",
        "工具/工作流选择",
        "工具执行",
        "工具集成验证",
        "会话压缩保存",
        "Git 提交推送"
    ]
    
    def __init__(self):
        self.flow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
        self.checkpoint_file = Path("flow-archive/20260318-universal-workflow-001/checkpoint.json")
        self.enforcement_log = Path("flow-archive/20260318-universal-workflow-001/enforcement-log.json")
        
        with open(self.flow_file, 'r', encoding='utf-8') as f:
            self.workflow = json.load(f)
    
    def check_workflow_loaded(self) -> bool:
        """检查工作流是否已加载"""
        
        if not self.flow_file.exists():
            print("[FAIL] 主工作流未加载！")
            return False
        
        print(f"[OK] 主工作流已加载：{self.workflow['version']}")
        return True
    
    def check_flow_id_bound(self) -> bool:
        """检查 Flow ID 是否已绑定"""
        
        # 检查是否有当前会话的 Flow ID
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            flow_id = checkpoint.get('flow_id')
            if flow_id:
                print(f"[OK] Flow ID 已绑定：{flow_id}")
                return True
        
        print("[WARN] Flow ID 未绑定，需要在 Step 2 绑定")
        return False
    
    def check_step_completion(self, completed_steps: list) -> dict:
        """检查步骤完成情况"""
        
        missing_steps = []
        for step in self.REQUIRED_STEPS:
            if step not in completed_steps:
                missing_steps.append(step)
        
        if missing_steps:
            print(f"[WARN] 未完成步骤：{len(missing_steps)}")
            for step in missing_steps:
                print(f"  - {step}")
        else:
            print(f"[OK] 所有必需步骤已完成：{len(completed_steps)}")
        
        return {
            "completed": len(completed_steps),
            "missing": len(missing_steps),
            "missing_steps": missing_steps,
            "compliance_rate": len(completed_steps) / len(self.REQUIRED_STEPS) * 100
        }
    
    def enforce_before_task(self, task_description: str) -> bool:
        """任务前强制执行检查"""
        
        print("\n" + "=" * 60)
        print("Workflow Enforcement Check - Pre-Session")
        print("=" * 60)
        
        checks = {
            "workflow_loaded": self.check_workflow_loaded(),
            "flow_id_bound": self.check_flow_id_bound(),
        }
        
        all_passed = all(checks.values())
        
        if not all_passed:
            print("\n[WARN] 检测到未按工作流执行！")
            print("[ACTION] 请立即执行以下步骤:")
            print("  1. Step 1: 上下文加载验证")
            print("  2. Step 2: Flow ID 绑定")
            print("  3. Step 3: 任务解析")
            print("  ...")
            print("\n[BLOCK] 在完成必需步骤前，不允许执行任务！")
            return False
        
        print("\n[OK] 工作流合规性检查通过")
        print("=" * 60)
        return True
    
    def enforce_before_commit(self, completed_steps: list) -> bool:
        """Git 提交前强制执行检查"""
        
        print("\n" + "=" * 60)
        print("Workflow Enforcement Check - Pre-Commit")
        print("=" * 60)
        
        # 检查必需步骤
        result = self.check_step_completion(completed_steps)
        
        if result['missing'] > 0:
            print(f"\n[FAIL] 完成度：{result['compliance_rate']:.1f}%")
            print("[BLOCK] 不允许 Git 提交！")
            print("[ACTION] 请先完成以下缺失步骤:")
            for step in result['missing_steps']:
                print(f"  - {step}")
            return False
        
        # 检查会话压缩
        daily_note = Path("13-memory/2026-03-20.md")
        if daily_note.exists():
            size = daily_note.stat().st_size
            if size > 5120:  # 5KB
                print(f"\n[FAIL] 当日笔记过大：{size} bytes (>5KB)")
                print("[BLOCK] 请先压缩会话笔记！")
                return False
            else:
                print(f"[OK] 当日笔记已压缩：{size/1024:.1f}KB")
        
        print(f"\n[OK] 完成度：{result['compliance_rate']:.1f}%")
        print("[OK] 允许 Git 提交")
        print("=" * 60)
        return True
    
    def log_enforcement(self, action: str, passed: bool, details: dict = None):
        """记录强制执行日志"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "passed": passed,
            "details": details or {}
        }
        
        # 读取或创建日志
        if self.enforcement_log.exists():
            with open(self.enforcement_log, 'r', encoding='utf-8') as f:
                log = json.load(f)
        else:
            log = {"entries": []}
        
        log["entries"].append(log_entry)
        
        # 只保留最近 100 条
        log["entries"] = log["entries"][-100:]
        
        with open(self.enforcement_log, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

def main():
    """测试入口"""
    enforcer = WorkflowEnforcer()
    
    # 测试会话前检查
    print("测试：会话前检查")
    enforcer.enforce_before_task("P1 优化实施")
    
    # 测试提交前检查
    print("\n\n测试：提交前检查")
    completed_steps = [
        "上下文加载验证",
        "Flow ID 绑定",
        "任务解析",
        "工具/工作流选择",
        "工具执行",
        "工具集成验证"
    ]
    enforcer.enforce_before_commit(completed_steps)

if __name__ == "__main__":
    main()
