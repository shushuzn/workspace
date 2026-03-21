import logging
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, '30-scripts-tools')

from tool_wrapper import before_tool_call, after_tool_call

print("测试工具包装器:\n")

print("测试 1: 无 session 时调用工具")
try:
    if before_tool_call('test_tool', {'param': 'value'}):
        print("  结果：允许执行")
        after_tool_call('test_tool', {'param': 'value'}, 'success')
    else:
        print("  结果：拒绝执行 ✓")
except Exception as e:
    print(f"  异常：{e}")
