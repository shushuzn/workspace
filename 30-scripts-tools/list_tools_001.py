import logging
logger = logging.getLogger(__name__)

import os
from pathlib import Path

tools_dir = Path("30-scripts-tools")
keywords = ['context', 'task', 'tool', 'flow', 'workflow', 'executor']

print("现有工具文件:")
for f in sorted(tools_dir.glob("*.py")):
    name = f.stem.lower()
    if any(kw in name for kw in keywords):
        print(f"  - {f.name}")
