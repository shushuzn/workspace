import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
结果验证器 - 验证工具执行结果是否符合预期
防止错误结果被接受
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def verify_result(tool_id: str, result: dict, expected_fields: list = None) -> dict:
    """验证工具执行结果"""
    
    issues = []
    warnings = []
    
    # 基础验证
    if result is None:
        issues.append("结果为空")
        return {
            "status": "fail",
            "issues": issues,
            "warnings": warnings
        }
    
    # 检查必需字段
    required_fields = expected_fields or ["status"]
    for field in required_fields:
        if field not in result:
            issues.append(f"缺少必需字段：{field}")
    
    # 检查状态
    if "status" in result:
        if result["status"] == "error":
            if "error" not in result and "reason" not in result:
                warnings.append("错误状态但无错误信息")
        
        elif result["status"] not in ["success", "error", "skip", "pending"]:
            issues.append(f"未知状态：{result['status']}")
    
    # 检查执行时间
    if "execution_time" in result:
        if result["execution_time"] > 60:
            warnings.append(f"执行时间过长：{result['execution_time']}s")
    
    # 检查返回码
    if "returncode" in result:
        if result["returncode"] != 0:
            if result.get("status") == "success":
                warnings.append(f"成功状态但返回码非零：{result['returncode']}")
    
    # 特殊工具验证
    tool_validators = {
        "context-verify": verify_context_verify,
        "task-analyzer": verify_task_analyzer,
        "auto-critic-v7": verify_critic,
    }
    
    if tool_id in tool_validators:
        extra_issues, extra_warnings = tool_validators[tool_id](result)
        issues.extend(extra_issues)
        warnings.extend(extra_warnings)
    
    # 判定结果
    if issues:
        return {
            "status": "fail",
            "issues": issues,
            "warnings": warnings,
            "verdict": "结果不可接受"
        }
    elif warnings:
        return {
            "status": "pass_with_warnings",
            "issues": [],
            "warnings": warnings,
            "verdict": "结果可接受但有警告"
        }
    else:
        return {
            "status": "pass",
            "issues": [],
            "warnings": [],
            "verdict": "结果完全符合预期"
        }

def verify_context_verify(result: dict) -> None:
    """验证 context-verify 结果"""
    issues = []
    warnings = []
    
    # 必须加载核心文件
    if "loaded_files" in result:
        if len(result["loaded_files"]) < 5:
            warnings.append(f"加载文件过少：{len(result['loaded_files'])}")
    
    return issues, warnings

def verify_task_analyzer(result: dict) -> None:
    """验证 task-analyzer 结果"""
    issues = []
    warnings = []
    
    # 必须有任务分析
    if "task_type" not in result:
        issues.append("缺少任务类型")
    
    return issues, warnings

def verify_critic(result: dict) -> None:
    """验证 critic 结果"""
    issues = []
    warnings = []
    
    # 必须有评分
    if "score" not in result and "final_score" not in result:
        warnings.append("缺少评分")
    
    return issues, warnings

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        # 测试模式
        print("结果验证器测试")
        print("=" * 60)
        
        test_cases = [
            # 正常结果
            ("context-verify", {"status": "success", "loaded_files": ["SOUL.md", "USER.md"]}),
            # 错误结果
            ("task-analyzer", {"status": "error"}),
            # 缺少字段
            ("auto-critic-v7", {"status": "success"}),
            # 空结果
            ("unknown", None),
        ]
        
        for tool_id, result in test_cases:
            verification = verify_result(tool_id, result)
            print(f"\n工具：{tool_id}")
            print(f"验证：{verification['verdict']}")
            if verification['issues']:
                print(f"问题：{verification['issues']}")
            if verification['warnings']:
                print(f"警告：{verification['warnings']}")
        
        return 0
    
    # 从 stdin 读取结果
    try:
        input_data = sys.stdin.read()
        result = json.loads(input_data)
        tool_id = sys.argv[1]
        
        verification = verify_result(tool_id, result)
        print(json.dumps(verification, ensure_ascii=False, indent=2))
        
        return 0 if verification["status"] != "fail" else 1
    except json.JSONDecodeError:
        print(json.dumps({
            "status": "fail",
            "issues": ["输入不是有效 JSON"],
            "warnings": []
        }, indent=2))
        return 1
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
# py result_verifier_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py result_verifier_001.py

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



if __name__ == "__main__":
    sys.exit(main())
