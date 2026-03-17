#!/usr/bin/env python3
"""
会话启动检查 - 确保新会话防护生效
用法：每次会话开始时运行
"""

import os
import sys
from pathlib import Path

WORKSPACE = str(Path(__file__).parent.parent)
CONFIG = r"C:\Users\华为\.copaw"

def check_session_protection():
    """检查会话防护是否生效"""
    print("=" * 60)
    print("[OpenClaw] Session Protection Check")
    print("=" * 60)
    
    issues = []
    
    # 检查 1: 工作目录
    cwd = os.getcwd()
    if cwd == WORKSPACE:
        print(f"[OK] Working directory: {cwd}")
    else:
        print(f"[WARN] Working directory: {cwd}")
        print(f"       Expected: {WORKSPACE}")
        issues.append("工作目录不正确")
    
    # 检查 2: 环境变量
    env_workspace = os.environ.get('OPENCLAW_WORKSPACE')
    if env_workspace == WORKSPACE:
        print(f"[OK] OPENCLAW_WORKSPACE: {env_workspace}")
    else:
        print(f"[WARN] OPENCLAW_WORKSPACE: {env_workspace}")
        issues.append("环境变量未设置")
    
    # 检查 3: sitecustomize
    if 'sitecustomize' in sys.modules:
        print(f"[OK] sitecustomize: loaded")
    else:
        print(f"[INFO] sitecustomize: not loaded (optional)")
    
    # 检查 4: 路径保护工具
    try:
        from path_interceptor import PathInterceptor
        print(f"[OK] PathInterceptor: available")
    except:
        print(f"[WARN] PathInterceptor: not available")
        issues.append("路径拦截器未加载")
    
    # 检查 5: safe_write
    try:
        from safe_write import safe_write
        print(f"[OK] safe_write: available")
    except:
        print(f"[WARN] safe_write: not available")
    
    # 总结
    print()
    if issues:
        print(f"[WARN] Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        print()
        print("[INFO] Running in protected mode anyway...")
        
        # 尝试修复
        os.environ['OPENCLAW_WORKSPACE'] = WORKSPACE
        os.chdir(WORKSPACE)
        print(f"[OK] Fixed: Working directory = {os.getcwd()}")
    else:
        print("[OK] All protections active!")
    
    print("=" * 60)
    return len(issues) == 0

if __name__ == "__main__":
    check_session_protection()
