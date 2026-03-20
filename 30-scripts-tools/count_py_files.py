import os
from pathlib import Path

scripts_dir = Path("30-scripts-tools")
py_files = list(scripts_dir.glob("*.py"))

print(f"Python 文件总数：{len(py_files)}")
print("\n前 50 个文件:")
for f in list(py_files)[:50]:
    print(f"  - {f.name}")
