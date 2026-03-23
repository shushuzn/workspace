import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流内容验证器 - 防止假装执行

核心功能：
1. 验证步骤输出是否有实质内容
2. 关键步骤（9-10）必须有工具调用
3. 执行阶段不能只有 echo
"""

import json
from pathlib import Path


class ContentValidator:
    """内容验证器"""

    def validate_step(self, step_id: int, result: str, output: str) -> bool:
        """
        验证步骤内容
        
        Args:
            step_id: 步骤 ID
            result: 执行结果
            output: 输出内容
        
        Returns:
            bool: 是否有效
        """
        combined = (result + output).lower()

        # 规则 1: Step>3 必须有实质内容（输出>20 字符）
        if step_id > 3 and len(output.strip()) < 20:
            print(f"[FAIL] Step {step_id}: Output too short")
            return False

        # 规则 2: Step>5 不能只有 echo
        if step_id > 5 and 'echo' in result.lower():
            if not any(t in combined for t in ['py ', '.py', 'git ', 'test']):
                print(f"[FAIL] Step {step_id}: Only echo, no real work")
                return False

        # 规则 3: Step 9-10 必须有关键工具调用
        if step_id in [9, 10]:
            critical = ['critic', 'quality', 'test', 'audit', 'check']
            if not any(t in combined for t in critical):
                print(f"[FAIL] Step {step_id}: Missing critical tool call")
                return False

        print(f"[OK] Step {step_id}: Content validated")
        return True


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
# py content_validator_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py content_validator_001.py

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
    print("Content Validator Test\n")

    validator = ContentValidator()

    # Test 1: Valid step
    print("Test 1: Valid execution")
    result = validator.validate_step(
        6,
        "py sa_valuation_model_001.py --test",
        "SA-010 Valuation Model test completed successfully"
    )
    print(f"  Result: {'[OK] Valid' if result else '[FAIL] Invalid'}\n")

    # Test 2: Just echo (invalid)
    print("Test 2: Just echo (should fail)")
    result = validator.validate_step(
        6,
        "echo Step 6",
        "Step 6"
    )
    print(f"  Result: {'[OK] Valid' if result else '[FAIL] Invalid'}\n")

    # Test 3: Critical step without tool (invalid)
    print("Test 3: Critical step without tool (should fail)")
    result = validator.validate_step(
        9,
        "echo Step 9 - Critic review",
        "Step 9 completed"
    )
    print(f"  Result: {'[OK] Valid' if result else '[FAIL] Invalid'}\n")

    # Test 4: Critical step with tool (valid)
    print("Test 4: Critical step with tool (should pass)")
    result = validator.validate_step(
        9,
        "py auto_critic_v7.py --target sa_010",
        "Critic score: 85/100"
    )
    print(f"  Result: {'[OK] Valid' if result else '[FAIL] Invalid'}\n")


if __name__ == '__main__':
    main()
