from pathlib import Path
import shutil

# 临时移除 state 文件
state_files = list(Path("flow-archive").glob("*/execution-state.json"))
print(f"找到 {len(state_files)} 个 state 文件:")
for f in state_files:
    print(f"  - {f}")
    shutil.move(str(f), str(f) + ".backup")

# 再次检查
state_files_after = list(Path("flow-archive").glob("*/execution-state.json"))
print(f"\n移除后：{len(state_files_after)} 个 state 文件")

# 恢复
for f in Path("flow-archive").glob("*/execution-state.json.backup"):
    shutil.move(str(f), str(f).replace('.backup', ''))
print(f"\n已恢复 state 文件")
