#!/usr/bin/env python3
"""
工作区初始化 - 强制设置正确的默认路径
用法：在会话开始时运行

效果：设置环境变量，确保所有工具使用 D 盘作为默认工作目录
"""

import os
import sys
from pathlib import Path

# 定义工作区
WORKSPACE = str(Path(__file__).parent.parent)
CONFIG = r"C:\Users\华为\.copaw"

def init_workspace():
    """初始化工作区环境变量"""
    
    print("=" * 60)
    print("[OpenClaw] Workspace Initialization")
    print("=" * 60)
    
    # 设置环境变量
    os.environ['OPENCLAW_WORKSPACE'] = WORKSPACE
    os.environ['OPENCLAW_CONFIG'] = CONFIG
    
    # 尝试修改当前工作目录
    try:
        os.chdir(WORKSPACE)
        print(f"[OK] 工作目录：{os.getcwd()}")
    except Exception as e:
        print(f"[WARN] 无法切换工作目录：{e}")
    
    # 显示环境变量
    print(f"\n环境变量:")
    print(f"  OPENCLAW_WORKSPACE = {os.environ.get('OPENCLAW_WORKSPACE')}")
    print(f"  OPENCLAW_CONFIG = {os.environ.get('OPENCLAW_CONFIG')}")
    print(f"  HOMEDRIVE = {os.environ.get('HOMEDRIVE')}")
    print(f"  HOMEPATH = {os.environ.get('HOMEPATH')}")
    print(f"  PWD = {os.getcwd()}")
    
    # 创建必要目录
    dirs = [
        WORKSPACE,
        f"{WORKSPACE}\\30-scripts-tools",
        f"{WORKSPACE}\\20-data-reports",
        f"{WORKSPACE}\\13-memory-记忆系统",
        f"{WORKSPACE}\\00-人格系统",
    ]
    
    print(f"\n目录检查:")
    for d in dirs:
        exists = os.path.exists(d)
        status = "[OK]" if exists else "[WARN]"
        print(f"  {status} {d}")
        if not exists:
            try:
                os.makedirs(d, exist_ok=True)
                print(f"     → 已创建")
            except Exception as e:
                print(f"     → 创建失败：{e}")
    
    print("\n" + "=" * 60)
    print("[OK] 工作区初始化完成！")
    print("=" * 60)
    
    # 返回工作区路径
    return WORKSPACE

def get_workspace():
    """获取工作区路径"""
    return os.environ.get('OPENCLAW_WORKSPACE', WORKSPACE)

def get_config():
    """获取配置区路径"""
    return os.environ.get('OPENCLAW_CONFIG', CONFIG)

if __name__ == "__main__":
    workspace = init_workspace()
    
    # 如果作为模块导入，自动执行
    print(f"\n[INFO] 提示：在 Python 脚本中使用:")
    print(f"   from workspace_init import get_workspace")
    print(f"   workspace = get_workspace()")
    print(f"   # {workspace}")
