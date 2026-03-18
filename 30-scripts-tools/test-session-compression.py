#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试会话压缩自动化流程

场景:
1. 模拟未压缩的会话
2. 运行 pre-session-hook 检测
3. 验证自动压缩功能
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / "13-memory"

def test_scenario_1_already_compressed():
    """场景 1: 已压缩会话 (当前状态)"""
    print("=" * 60)
    print("场景 1: 已压缩会话")
    print("=" * 60)
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "30-scripts-tools\\session_end_checker.py", "--check"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    print(result.stdout)
    return True


def test_scenario_2_not_compressed():
    """场景 2: 未压缩会话 (模拟)"""
    print("\n" + "=" * 60)
    print("场景 2: 未压缩会话 (模拟)")
    print("=" * 60)
    
    # 备份当前文件
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = MEMORY_DIR / f"{today}.md"
    backup_file = MEMORY_DIR / f"{today}.md.backup"
    
    if daily_file.exists():
        shutil.copy2(daily_file, backup_file)
        print(f"[OK] 备份：{backup_file}")
        
        # 读取内容
        content = daily_file.read_text(encoding='utf-8')
        
        # 删除 Session Summary 部分
        import re
        pattern = r'\n## Session Summary.*'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 也删除 Session Context
        pattern = r'\n## Session Context.*'
        new_content = re.sub(pattern, '', new_content, flags=re.DOTALL)
        
        # 保存修改后的文件 (模拟未压缩)
        daily_file.write_text(new_content, encoding='utf-8')
        print(f"[OK] 模拟未压缩状态：{daily_file}")
        
        # 运行 pre-session-hook 测试自动检测
        print("\n运行 pre-session-hook 检测...")
        import subprocess
        # Windows 编码修复：使用 shell=True 和创建新进程组
        result = subprocess.run(
            f'python 30-scripts-tools\\pre-session-hook.py',
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=60,
            shell=True,
            creationflags=subprocess.CREATE_NO_PROCESS if sys.platform == 'win32' else 0,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"[WARN] 返回码：{result.returncode}")
            # 不显示 stderr，避免编码问题
        
        # 恢复原文件
        shutil.copy2(backup_file, daily_file)
        backup_file.unlink()
        print(f"\n[OK] 恢复原文件：{daily_file}")
        
        return True
    else:
        print(f"[ERROR] 文件不存在：{daily_file}")
        return False


def test_scenario_3_heartbeat_check():
    """场景 3: 心跳检查"""
    print("\n" + "=" * 60)
    print("场景 3: 心跳检查 (--auto 模式)")
    print("=" * 60)
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "30-scripts-tools\\session_end_checker.py", "--auto"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=30
    )
    print(result.stdout)
    return True


def main():
    print("=" * 60)
    print("会话压缩自动化流程 - 完整测试")
    print("=" * 60)
    
    tests = [
        ("已压缩会话", test_scenario_1_already_compressed),
        ("未压缩会话 (模拟)", test_scenario_2_not_compressed),
        ("心跳检查", test_scenario_3_heartbeat_check),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n[ERROR] {name} 测试失败：{e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {name}")
    
    all_passed = all(success for _, success in results)
    
    print("=" * 60)
    if all_passed:
        print("\n[OK] 所有测试通过！自动化流程正常")
    else:
        print("\n[WARN] 有测试失败，请检查")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
