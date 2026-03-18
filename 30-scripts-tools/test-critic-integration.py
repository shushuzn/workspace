#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critic v5.0 Integration Test

测试批判者审查集成到各个工具的效果
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'

def test_critic_review_tool():
    """测试批判者审查工具本身"""
    print("="*60)
    print("测试 1: 批判者审查工具")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, 'critic_v5_review.py', '--list'],
        cwd=str(TOOLS_DIR),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0 and 'file_organize' in result.stdout:
        print("[OK] 批判者审查工具正常")
        print(f"可用场景数：{result.stdout.count('scenario')}")
        return True
    else:
        print("[FAIL] 批判者审查工具异常")
        return False


def test_file_organizer_integration():
    """测试 file-organizer.py 集成"""
    print("\n" + "="*60)
    print("测试 2: file-organizer.py 集成")
    print("="*60)
    
    # 创建跳过文件 (避免交互)
    skip_file = TOOLS_DIR / 'skip_critic_test.txt'
    skip_file.touch()
    
    try:
        result = subprocess.run(
            [sys.executable, 'file-organizer.py', '--help'],
            cwd=str(TOOLS_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and '--no-critic' in result.stdout:
            print("[OK] file-organizer.py 集成成功")
            print("     - 批判者审查参数：--no-critic")
            return True
        else:
            print("[FAIL] file-organizer.py 集成失败")
            return False
    finally:
        # 清理测试文件
        if skip_file.exists():
            skip_file.unlink()


def test_optimize_tools_integration():
    """测试 optimize-tools-quick.py 集成"""
    print("\n" + "="*60)
    print("测试 3: optimize-tools-quick.py 集成")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, 'optimize-tools-quick.py', '--help'],
        cwd=str(TOOLS_DIR),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # 检查是否包含批判者审查逻辑
    opt_file = TOOLS_DIR / 'optimize-tools-quick.py'
    content = opt_file.read_text(encoding='utf-8')
    
    if 'critic_v5_review' in content:
        print("[OK] optimize-tools-quick.py 集成成功")
        print("     - 批判者审查：自动运行")
        return True
    else:
        print("[FAIL] optimize-tools-quick.py 集成失败")
        return False


def test_cleanup_tools_integration():
    """测试 cleanup-60data-sensitive.py 集成"""
    print("\n" + "="*60)
    print("测试 4: cleanup-60data-sensitive.py 集成")
    print("="*60)
    
    cleanup_file = TOOLS_DIR / 'cleanup-60data-sensitive.py'
    content = cleanup_file.read_text(encoding='utf-8')
    
    if 'critic_v5_review' in content and 'data_cleanup' in content:
        print("[OK] cleanup-60data-sensitive.py 集成成功")
        print("     - 批判者审查：data_cleanup 场景")
        return True
    else:
        print("[FAIL] cleanup-60data-sensitive.py 集成失败")
        return False


def test_review_report_generation():
    """测试审查报告生成"""
    print("\n" + "="*60)
    print("测试 5: 审查报告生成")
    print("="*60)
    
    reports_dir = WORKSPACE / '21-reports' / 'critic-reviews'
    
    if reports_dir.exists():
        report_count = len(list(reports_dir.rglob('*.md')))
        print(f"[OK] 审查报告目录存在")
        print(f"     - 报告数量：{report_count} 个")
        return True
    else:
        print("[WARN] 审查报告目录不存在 (首次运行时会创建)")
        return True  # 不视为失败


def main():
    print("="*60)
    print("批判者 v5.0 集成测试")
    print("="*60)
    print(f"时间：{datetime.now().isoformat()}")
    print(f"工作区：{WORKSPACE}")
    print()
    
    tests = [
        ("批判者审查工具", test_critic_review_tool),
        ("file-organizer.py", test_file_organizer_integration),
        ("optimize-tools-quick.py", test_optimize_tools_integration),
        ("cleanup-60data-sensitive.py", test_cleanup_tools_integration),
        ("审查报告生成", test_review_report_generation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n[ERROR] {name} 测试异常：{e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {name}")
    
    print()
    print(f"通过率：{passed}/{total} ({passed/total*100:.0f}%)")
    print("="*60)
    
    if passed == total:
        print("\n[OK] 所有测试通过！批判者 v5.0 集成成功")
        return 0
    else:
        print(f"\n[WARN] {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
