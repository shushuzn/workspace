import logging
logger = logging.getLogger(__name__)

from pathlib import Path
import shutil

state_files = list(Path("flow-archive").glob("*/execution-state.json.backup"))
print(f"找到 {len(state_files)} 个备份文件:")

for f in state_files:
    new_path = str(f).replace('.backup', '')
    shutil.move(str(f), new_path)
    print(f"  恢复：{f.name} -> {Path(new_path).name}")

print("\n恢复完成")
