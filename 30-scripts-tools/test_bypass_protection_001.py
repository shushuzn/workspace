#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试绕过防护 - 验证所有绕过方式都被阻断
"""

import json
import subprocess
import sys
from pathlib import Path

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")

def test(description, test_func):
    """测试函数"""
    print(f"\n{'='*70}")
    print(f"测试：{description}")
    print('='*70)
    
    try:
        result = test_func()
        if result:
            print(f"[PASS] 防护生效")
            return True
        else:
            print(f"[FAIL] 防护失效")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_direct_state_modification():
    """测试 1: 直接修改 state 文件"""
    print("尝试直接修改 execution-state.json...")
    
    # 备份原始状态
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        original_state = json.load(f)
    
    # 尝试修改
    modified_state = original_state.copy()
    modified_state['completion_percentage'] = 100.0
    modified_state['current_step'] = 20
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(modified_state, f, indent=2, ensure_ascii=False)
    
    print("  已修改 completion_percentage 为 100%")
    
    # 尝试验证
    result = subprocess.run(
        ['py', '30-scripts-tools/state_protector.py', '--verify'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    , timeout=60)
    
    # 恢复原始状态
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(original_state, f, indent=2, ensure_ascii=False)
    
    if result.returncode != 0:
        print("  [BLOCK] 签名验证失败 - 防护生效")
        return True
    else:
        print("  [FAIL] 签名验证通过 - 防护失效")
        return False


def test_script_bypass():
    """测试 2: 写脚本跳过步骤"""
    print("尝试写脚本直接更新 state...")
    
    # 创建绕过脚本
    bypass_script = Path("30-scripts-tools/test_bypass_attempt.py")
    bypass_script.write_text('''
import json
from pathlib import Path

state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

state['completion_percentage'] = 100.0
state['current_step'] = 20

with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("State modified")
''', encoding='utf-8')
    
    # 执行绕过脚本
    result = subprocess.run(
        ['py', str(bypass_script, timeout=60)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # 清理
    bypass_script.unlink()
    
    print(f"  脚本输出：{result.stdout.strip()}")
    
    # 尝试验证
    result = subprocess.run(
        ['py', '30-scripts-tools/state_protector.py', '--verify'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    , timeout=60)
    
    if result.returncode != 0:
        print("  [BLOCK] 签名验证失败 - 防护生效")
        return True
    else:
        print("  [FAIL] 签名验证通过 - 防护失效")
        return False


def test_git_commit_bypass():
    """测试 3: git commit 绕过"""
    print("尝试 git commit --no-verify...")
    
    result = subprocess.run(
        ['git', 'commit', '--no-verify', '-m', 'test'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    , timeout=60)
    
    if '[BLOCK]' in result.stdout or '[BLOCK]' in result.stderr or result.returncode != 0:
        print("  [BLOCK] 检测到 --no-verify - 防护生效")
        return True
    else:
        print("  [FAIL] --no-verify 成功 - 防护失效")
        return False


def main():
    print("="*70)
    print("绕过防护测试")
    print("="*70)
    
    results = []
    
    # 测试 1: 直接修改 state
    results.append(test(
        "直接修改 execution-state.json",
        test_direct_state_modification
    ))
    
    # 测试 2: 写脚本跳过步骤
    results.append(test(
        "写脚本直接更新 state",
        test_script_bypass
    ))
    
    # 测试 3: git commit 绕过
    results.append(test(
        "git commit --no-verify",
        test_git_commit_bypass
    ))
    
    # 总结
    print("\n" + "="*70)
    print(f"测试结果：{sum(results)}/{len(results)} 通过")
    print("="*70)
    
    if all(results):
        print("[OK] 所有防护措施生效")
        sys.exit(0)
    else:
        print("[FAIL] 有防护措施未生效")
        sys.exit(1)


if __name__ == '__main__':
    main()
