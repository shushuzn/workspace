#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
执行防护强化任务 - 通过 tool_executor
"""
import sys
import json
from pathlib import Path

# 添加工具目录到路径
sys.path.insert(0, str(Path("30-scripts-tools").resolve()))

from tool_executor import ToolExecutor

def main():
    print("=" * 70)
    print("防护强化任务 - 通过 tool_executor 执行")
    print("=" * 70)

    # 创建执行器
    executor = ToolExecutor()

    # 测试执行一个已注册的工具
    print("\n[测试] 执行 risk-assessor 工具")
    result = executor.execute("risk-assessor", {"command": "echo 防护检查"})
    print(f"结果：{result}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
