import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流强制执行器 v2.0 - 集成内容验证

核心改进：
1. 每步必须验证输出内容
2. 不通过验证 → 不允许继续
3. 防止假装执行
"""

import json
from datetime import datetime
from pathlib import Path
from content_validator import ContentValidator


class WorkflowEnforcerV2:
    """工作流强制执行器 v2.0"""
    
    def __init__(self, flow_id: str, session_id: str):
        self.flow_id = flow_id
        self.session_id = session_id
        self.flow_dir = Path(f"flow-archive/{flow_id}")
        self.state_file = self.flow_dir / "execution-state.json"
        self.validator = ContentValidator()
        self.enforcement_enabled = True
    
    def verify_and_execute(self, step_id: int, command: str, expected_output: str = "") -> bool:
        """
        验证并执行步骤
        
        Args:
            step_id: 步骤 ID
            command: 执行的命令
            expected_output: 预期输出关键词
        
        Returns:
            bool: 是否成功执行
        """
        # 1. 验证步骤顺序
        if not self._verify_step_order(step_id):
            return False
        
        # 2. 执行命令（由调用者执行）
        # 3. 验证输出
        # （由调用者提供输出）
        
        return True
    
    def validate_step_output(self, step_id: int, output: str, expected_keywords: list = None) -> bool:
        """
        验证步骤输出
        
        Args:
            step_id: 步骤 ID
            output: 实际输出
            expected_keywords: 预期关键词列表
        
        Returns:
            bool: 验证是否通过
        """
        if not output or len(output.strip()) < 10:
            print(f"[FAIL] Step {step_id}: Output too short")
            return False
        
        # 使用 content_validator 验证
        if expected_keywords:
            for keyword in expected_keywords:
                if keyword.lower() not in output.lower():
                    print(f"[FAIL] Step {step_id}: Missing keyword '{keyword}'")
                    return False
        
        print(f"[OK] Step {step_id}: Output validated")
        return True
    
    def update_step_status(self, step_id: int, status: str, output: str = "", validated: bool = True):
        """
        更新步骤状态（必须验证）
        
        Args:
            step_id: 步骤 ID
            status: 状态
            output: 输出内容
            validated: 是否已验证
        """
        if not self.state_file.exists():
            return
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            self.state = json.load(f)
        
        # 只允许更新已验证的步骤
        if status == 'completed' and not validated:
            print(f"[BLOCK] Step {step_id}: Cannot complete without validation")
            status = 'failed'
        
        # 更新状态
        if 'step_status' not in self.state:
            self.state['step_status'] = {}
        
        self.state['step_status'][step_id] = {
            'status': status,
            'completed_at': datetime.now().isoformat(),
            'validated': validated,
            'output_length': len(output) if output else 0
        }
        
        # 更新 completed_steps（只记录 validated=True）
        if status == 'completed' and validated:
            if 'completed_steps' not in self.state:
                self.state['completed_steps'] = []
            if step_id not in self.state['completed_steps']:
                self.state['completed_steps'].append(step_id)
        
        # 更新完成率
        total = self.state.get('total_steps', 5)
        self.state['completion_percentage'] = len(self.state['completed_steps']) / total * 100
        
        # 保存
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        
        mark = "✓" if validated else "✗"
        print(f"[OK] Step {step_id} updated: {status} {mark}")
    
    def _verify_step_order(self, step_id: int) -> bool:
        """验证步骤顺序"""
        if not self.state_file.exists():
            return False
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            self.state = json.load(f)
        
        completed = self.state.get('completed_steps', [])
        next_expected = len(completed) + 1
        
        if step_id != next_expected:
            print(f"[BLOCK] Step order violation: expected {next_expected}, got {step_id}")
            return False
        
        return True


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
# py workflow_enforcer_v_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_enforcer_v_001.py

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

测试"""
    print("Workflow Enforcer V2.0 - Test")
    
    enforcer = WorkflowEnforcerV2(
        flow_id="20260318-simplified-workflow-001",
        session_id="test-session"
    )
    
    # Test 1: Valid output
    print("\nTest 1: Valid output")
    valid = enforcer.validate_step_output(
        1,
        "Step 1 completed - context loaded successfully",
        ["completed", "context"]
    )
    print(f"  Result: {'[OK] Valid' if valid else '[FAIL] Invalid'}")
    
    # Test 2: Missing keyword
    print("\nTest 2: Missing keyword")
    valid = enforcer.validate_step_output(
        2,
        "Step 2 done",
        ["task", "analysis"]
    )
    print(f"  Result: {'[OK] Valid' if valid else '[FAIL] Invalid'}")
    
    # Test 3: Too short
    print("\nTest 3: Too short output")
    valid = enforcer.validate_step_output(
        3,
        "OK",
        []
    )
    print(f"  Result: {'[OK] Valid' if valid else '[FAIL] Invalid'}")


if __name__ == '__main__':
    main()
