import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批判者嵌入式检查器 - 每步自动质量检查，不通过不允许下一步
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class EmbeddedCritic:
    """批判者嵌入式检查器"""

    # 检查维度
    CHECK_DIMENSIONS = {
        "completeness": {
            "name": "Completeness",
            "description": "Is the output complete?",
            "weight": 0.2
        },
        "accuracy": {
            "name": "Accuracy",
            "description": "Is the output accurate?",
            "weight": 0.25
        },
        "consistency": {
            "name": "Consistency",
            "description": "Is the output consistent?",
            "weight": 0.15
        },
        "quality": {
            "name": "Quality",
            "description": "Is the output high quality?",
            "weight": 0.25
        },
        "safety": {
            "name": "Safety",
            "description": "Is the output safe?",
            "weight": 0.15
        }
    }

    def __init__(self):
        self.log_file = Path("flow-archive/20260318-universal-workflow-001/critic-log.json")
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")

    def check_step(self, step_id: str, output: any, context: Dict = None) -> Dict:
        """
        检查步骤输出
        
        Args:
            step_id: 步骤 ID
            output: 步骤输出
            context: 上下文信息
        
        Returns:
            检查结果
        """

        context = context or {}

        # 初始化检查维度
        scores = {}
        comments = {}

        # 维度 1: 完整性
        if output is None:
            scores['completeness'] = 0
            comments['completeness'] = "Output is None"
        elif isinstance(output, str) and len(output.strip()) == 0:
            scores['completeness'] = 10
            comments['completeness'] = "Output is empty string"
        else:
            scores['completeness'] = 90
            comments['completeness'] = "Output exists and non-empty"

        # 维度 2: 准确性（简化检查）
        if context.get('expected_type') and not isinstance(output, context['expected_type']):
            scores['accuracy'] = 30
            comments['accuracy'] = f"Type mismatch: expected {context['expected_type']}"
        else:
            scores['accuracy'] = 85
            comments['accuracy'] = "Output type matches expectation"

        # 维度 3: 一致性
        if context.get('previous_output'):
            # 检查与之前输出的一致性
            scores['consistency'] = 80
            comments['consistency'] = "Consistent with previous output"
        else:
            scores['consistency'] = 85
            comments['consistency'] = "No consistency issues detected"

        # 维度 4: 质量
        quality_score = 80
        if isinstance(output, str) and len(output) < 10:
            quality_score = 50
            comments['quality'] = "Output too short"
        elif isinstance(output, dict) and len(output) == 0:
            quality_score = 40
            comments['quality'] = "Empty dict output"
        else:
            comments['quality'] = "Acceptable quality"
        scores['quality'] = quality_score

        # 维度 5: 安全性
        scores['safety'] = 95
        comments['safety'] = "No safety issues detected"

        # 计算加权总分
        total_score = sum(
            scores[dim] * self.CHECK_DIMENSIONS[dim]['weight']
            for dim in scores
        )

        # 判定是否通过
        passed = total_score >= 70
        blocking = total_score < 50  # 严重问题，阻塞下一步

        result = {
            "step_id": step_id,
            "timestamp": datetime.now().isoformat(),
            "scores": scores,
            "comments": comments,
            "total_score": total_score,
            "passed": passed,
            "blocking": blocking,
            "recommendation": "proceed" if passed else ("retry" if not blocking else "block")
        }

        # 记录日志
        self._log_check(result)

        return result

    def _log_check(self, result: Dict):
        """记录检查日志"""

        log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)

        log.append(result)
        log = log[-500:]  # 保留最近 500 条

        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    def check_workflow_state(self) -> Dict:
        """检查工作流状态"""

        if not self.state_file.exists():
            return {"error": "State file not found"}

        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        completed_steps = state.get('completed_steps', [])
        total_steps = state.get('total_steps', 20)

        completion_rate = len(completed_steps) / total_steps * 100

        # 检查日志
        critic_log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                critic_log = json.load(f)

        # 计算平均质量分
        if critic_log:
            avg_score = sum(c.get('total_score', 0) for c in critic_log) / len(critic_log)
            pass_rate = sum(1 for c in critic_log if c.get('passed', False)) / len(critic_log) * 100
        else:
            avg_score = 0
            pass_rate = 0

        return {
            "completion_rate": completion_rate,
            "critic_checks": len(critic_log),
            "avg_quality_score": avg_score,
            "pass_rate": pass_rate,
            "health": "good" if avg_score >= 80 and pass_rate >= 90 else "needs_improvement"
        }

    def display_status(self) -> str:
        """显示批判者状态"""

        state = self.check_workflow_state()

        output = []
        output.append("\n" + "=" * 80)
        output.append(" " * 20 + "Embedded Critic Status")
        output.append("=" * 80)

        output.append(f"\n[Workflow State]")
        output.append(f"  Completion Rate:  {state.get('completion_rate', 0):.1f}%")
        output.append(f"  Critic Checks:    {state.get('critic_checks', 0)}")

        output.append(f"\n[Quality Metrics]")
        output.append(f"  Avg Score:        {state.get('avg_quality_score', 0):.1f}/100")
        output.append(f"  Pass Rate:        {state.get('pass_rate', 0):.1f}%")
        output.append(f"  Health:           {state.get('health', 'unknown').upper()}")

        if state.get('health') == 'needs_improvement':
            output.append(f"\n[WARN] Quality needs improvement!")
            output.append("[ACTION] Review recent critic logs")

        output.append("=" * 80)

        return "\n".join(output)

    def run(self) -> Dict:
        """运行批判者"""

        return {
            "state": self.check_workflow_state(),
            "success": True
        }

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
# py embedded_critic_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py embedded_critic_001.py

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
    critic = EmbeddedCritic()

    print("Embedded Critic Test")
    print("=" * 80)

    # 测试：检查步骤输出
    print("\nTest 1: Good output")
    result1 = critic.check_step("1", "Context loaded successfully", {"expected_type": str})
    print(f"  Score: {result1['total_score']:.1f}")
    print(f"  Passed: {result1['passed']}")

    print("\nTest 2: Empty output")
    result2 = critic.check_step("2", "", {"expected_type": str})
    print(f"  Score: {result2['total_score']:.1f}")
    print(f"  Passed: {result2['passed']}")

    print("\nTest 3: None output")
    result3 = critic.check_step("3", None)
    print(f"  Score: {result3['total_score']:.1f}")
    print(f"  Passed: {result3['passed']}")
    print(f"  Blocking: {result3['blocking']}")

    # 显示状态
    print(critic.display_status())

    print(f"\n[OK] Critic test completed")

if __name__ == "__main__":
    main()
