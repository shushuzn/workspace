# Python 启动脚本 - 自动导入路径保护
# 位置：D:\OpenClaw\workspace\python_startup.py
# 用法：在 PYTHONSTARTUP 环境变量中设置

import os
import sys
from pathlib import Path

# 工作区配置
WORKSPACE = str(Path(__file__).parent.parent)
CONFIG = r"C:\Users\华为\.copaw"

# 强制设置环境变量
os.environ['OPENCLAW_WORKSPACE'] = WORKSPACE
os.environ['OPENCLAW_CONFIG'] = CONFIG

# 强制切换工作目录
try:
    os.chdir(WORKSPACE)
except:
    pass

# 添加工具路径到 sys.path
tools_path = os.path.join(WORKSPACE, '30-scripts-tools')
if tools_path not in sys.path:
    sys.path.insert(0, tools_path)

# 自动导入路径保护
try:
    from path_interceptor import PathInterceptor
    from safe_write import safe_write
    from workspace import Workspace
    print(f"[OK] OpenClaw Workspace: {WORKSPACE}")
    print(f"[OK] Path protection enabled")
except Exception as e:
    print(f"[WARN] Path protection not loaded: {e}")

print(f"[INFO] Working directory: {os.getcwd()}")
