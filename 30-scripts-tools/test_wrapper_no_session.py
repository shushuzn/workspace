import sys
import os
from pathlib import Path
sys.path.insert(0, '30-scripts-tools')

# 删除 state 文件模拟无 session
import shutil
state_dir = Path("flow-archive/20260318-universal-workflow-001")
if state_dir.exists():
    for f in state_dir.glob("execution-state.json"):
        print(f"临时移除：{f}")
        shutil.move(str(f), str(f) + ".backup")

from pathlib import Path
from tool_wrapper import ToolWrapper

print("测试工具包装器（无 session）:\n")

wrapper = ToolWrapper()

print("调用 before_tool_call...")
allowed = wrapper.before_tool_call('test_tool', {'param': 'value'})
print(f"\n结果：{'允许' if allowed else '拒绝'}")

# 恢复 state 文件
if state_dir.exists():
    for f in state_dir.glob("execution-state.json.backup"):
        print(f"\n恢复：{f}")
        shutil.move(str(f), str(f).replace('.backup', ''))
