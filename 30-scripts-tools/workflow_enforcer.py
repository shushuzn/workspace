#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Enforcer - 工作流强制遵守工具

核心功能:
1. 任务开始前加载 workflow.json
2. 生成步骤检查清单
3. 每步执行前验证顺序
4. 完成后验证 12 步全部执行
5. 未通过 → 阻断后续操作
6. **集成 5 层防护系统**

Usage:
    py workflow_enforcer.py --start <flow_id>     # 开始工作流
    py workflow_enforcer.py --check-step <step>   # 检查步骤
    py workflow_enforcer.py --validate            # 验证完成
    py workflow_enforcer.py --status              # 查看状态
    py workflow_enforcer.py --protection-check    # 5 层防护检查
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
FLOW_ARCHIVE = WORKSPACE / "flow-archive"

# 导入 5 层防护系统
try:
    from protection_system import FiveLayerProtectionSystem
    PROTECTION_AVAILABLE = True
except ImportError:
    PROTECTION_AVAILABLE = False

class WorkflowEnforcer:
    def __init__(self, flow_id="20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.workflow_dir = FLOW_ARCHIVE / flow_id
        self.workflow_file = self.workflow_dir / "workflow.json"
        self.checkpoint_file = self.workflow_dir / "checkpoint.json"
        self.enforcement_log = self.workflow_dir / "enforcement-log.json"
        
        self.workflow = None
        self.state = None
        
    def load_workflow(self):
        """强制加载 workflow.json"""
        if not self.workflow_file.exists():
            print(f"[BLOCKER] workflow.json 不存在：{self.workflow_file}")
            return False
        
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            self.workflow = json.load(f)
        
        print(f"[OK] 工作流已加载：{self.workflow.get('name', 'Unknown')}")
        print(f"     版本：v{self.workflow.get('version', 'N/A')}")
        print(f"     总步骤：{self.workflow.get('total_steps', 'N/A')}")
        return True
    
    def start_workflow(self):
        """开始工作流 - 创建初始状态"""
        if not self.load_workflow():
            return False
        
        total_steps = self.workflow.get('total_steps', 0)
        steps = self.workflow.get('steps', [])
        
        self.state = {
            "flow_id": self.flow_id,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "total_steps": total_steps,
            "completed_steps": [],
            "current_step": 1,
            "step_status": {str(s['step_id']): "pending" for s in steps},
            "enforcement_enabled": True,
            "violations": []
        }
        
        self._save_state()
        
        print(f"\n[OK] 工作流已启动：{self.flow_id}")
        print(f"     步骤清单:")
        for step in steps:
            print(f"       Step {step['step_id']}: {step['name']} [{'阻塞' if step['blocking'] else '非阻塞'}]")
        
        print(f"\n[ENFORCEMENT] 强制模式已启用")
        print(f"     - 必须按顺序执行步骤")
        print(f"     - 跳步将被阻断")
        print(f"     - 完成后必须验证")
        
        return True
    
    def check_step(self, step_id: int) -> bool:
        """检查步骤是否可按顺序执行"""
        if not self.state:
            self._load_state()
        
        if not self.state:
            print("[BLOCKER] 工作流未启动！请先执行 --start")
            return False
        
        current = self.state.get('current_step', 1)
        
        if step_id < current:
            print(f"[WARN] 步骤 {step_id} 已完成，无需重复执行")
            return True
        
        if step_id > current:
            print(f"[BLOCKER] 步骤跳跃检测!")
            print(f"     当前步骤：{current}")
            print(f"     尝试执行：{step_id}")
            print(f"     操作被阻断 - 请按顺序执行步骤")
            
            # 记录违规
            self.state['violations'].append({
                "type": "step_skip",
                "attempted_step": step_id,
                "current_step": current,
                "timestamp": datetime.now().isoformat()
            })
            self._save_state()
            return False
        
        print(f"[OK] 步骤 {step_id} 验证通过 - 可以执行")
        return True
    
    def complete_step(self, step_id: int, success: bool = True):
        """标记步骤完成"""
        if not self.state:
            self._load_state()
        
        if not self.state:
            print("[ERROR] 工作流状态不存在")
            return
        
        step_id_str = str(step_id)
        self.state['step_status'][step_id_str] = "completed" if success else "failed"
        
        if success and step_id not in self.state['completed_steps']:
            self.state['completed_steps'].append(step_id)
            self.state['current_step'] = step_id + 1
        
        self._save_state()
        print(f"[OK] 步骤 {step_id} 标记为 {'完成' if success else '失败'}")
    
    def validate_completion(self) -> bool:
        """验证工作流是否全部完成"""
        if not self.state:
            self._load_state()
        
        if not self.state:
            print("[BLOCKER] 工作流状态不存在")
            return False
        
        total = self.state.get('total_steps', 0)
        completed = len(self.state.get('completed_steps', []))
        
        print(f"\n[验证] 工作流完成度检查")
        print(f"     总步骤：{total}")
        print(f"     已完成：{completed}")
        
        if completed < total:
            missing = set(range(1, total + 1)) - set(self.state['completed_steps'])
            print(f"\n[BLOCKER] 工作流未完成!")
            print(f"     缺失步骤：{sorted(missing)}")
            print(f"     Git 提交被阻断")
            return False
        
        violations = len(self.state.get('violations', []))
        if violations > 0:
            print(f"\n[WARN] 检测到 {violations} 次违规")
            for v in self.state['violations']:
                print(f"     - {v['type']}: Step {v.get('attempted_step', 'N/A')}")
        
        print(f"\n[OK] 工作流验证通过 - {total}/{total} 步骤完成")
        
        self.state['status'] = "completed"
        self.state['completed_at'] = datetime.now().isoformat()
        self._save_state()
        
        return True
    
    def can_commit_git(self) -> bool:
        """检查是否可以提交 Git"""
        if not self.validate_completion():
            print("\n[Git Hook] 提交被阻断 - 工作流未完成")
            return False
        
        print("\n[Git Hook] 验证通过 - 允许提交")
        return True
    
    def _load_state(self):
        """加载状态"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
    
    def _save_state(self):
        """保存状态"""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow Enforcer - 工作流强制遵守工具")
    parser.add_argument('--start', action='store_true', help='开始工作流')
    parser.add_argument('--check-step', type=int, metavar='STEP', help='检查步骤是否可执行')
    parser.add_argument('--complete-step', type=int, metavar='STEP', help='标记步骤完成')
    parser.add_argument('--validate', action='store_true', help='验证工作流完成')
    parser.add_argument('--can-commit', action='store_true', help='检查是否可以 Git 提交')
    parser.add_argument('--status', action='store_true', help='查看当前状态')
    parser.add_argument('--protection-check', action='store_true', help='5 层防护系统检查')
    parser.add_argument('--flow-id', type=str, default='20260318-universal-workflow-001', help='Flow ID')
    
    args = parser.parse_args()
    
    enforcer = WorkflowEnforcer(args.flow_id)
    
    if args.start:
        success = enforcer.start_workflow()
        sys.exit(0 if success else 1)
    
    elif args.check_step:
        success = enforcer.check_step(args.check_step)
        sys.exit(0 if success else 1)
    
    elif args.complete_step:
        enforcer.complete_step(args.complete_step)
        sys.exit(0)
    
    elif args.validate:
        success = enforcer.validate_completion()
        sys.exit(0 if success else 1)
    
    elif args.can_commit:
        success = enforcer.can_commit_git()
        sys.exit(0 if success else 1)
    
    elif args.status:
        enforcer._load_state()
        if enforcer.state:
            print(f"Flow ID: {enforcer.state.get('flow_id', 'N/A')}")
            print(f"状态：{enforcer.state.get('status', 'N/A')}")
            print(f"当前步骤：{enforcer.state.get('current_step', 'N/A')}/{enforcer.state.get('total_steps', 'N/A')}")
            print(f"已完成：{enforcer.state.get('completed_steps', [])}")
            print(f"违规次数：{len(enforcer.state.get('violations', []))}")
        else:
            print("[INFO] 工作流未启动")
        sys.exit(0)
    
    elif args.protection_check:
        # 5 层防护系统检查
        if not PROTECTION_AVAILABLE:
            print("❌ 5 层防护系统未安装：protection_system.py")
            sys.exit(1)
        
        system = FiveLayerProtectionSystem()
        success, _ = system.check_all()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
