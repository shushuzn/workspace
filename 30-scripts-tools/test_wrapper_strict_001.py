import logging
logger = logging.getLogger(__name__)

import sys
from pathlib import Path
import shutil

sys.path.insert(0, '30-scripts-tools')

# 临时移除所有 state 文件
state_files = list(Path("flow-archive").glob("*/execution-state.json"))
print(f"找到 {len(state_files)} 个 state 文件")
for f in state_files:
    print(f"  临时移除：{f}")
    shutil.move(str(f), str(f) + ".backup")

print("\n" + "="*70)
print("测试工具包装器（无 session）:\n")

# 重新导入（确保没有缓存）
if 'tool_wrapper' in sys.modules:
    del sys.modules['tool_wrapper']

from tool_wrapper import ToolWrapper

wrapper = ToolWrapper()

print("调用 before_tool_call...")
allowed = wrapper.before_tool_call('test_tool', {'param': 'value'})
print(f"\n结果：{'允许' if allowed else '拒绝'}")

if not allowed:
    print("\n[PASS] 防护生效：无 session 时拒绝工具调用")
else:
    print("\n[FAIL] 防护失效：无 session 时仍然允许")

print("="*70)

# 恢复 state 文件
print("\n恢复 state 文件:")
for f in Path("flow-archive").glob("*/execution-state.json.backup"):
    print(f"  恢复：{f}")
    shutil.move(str(f), str(f).replace('.backup', ''))

print("\n已完成测试")
