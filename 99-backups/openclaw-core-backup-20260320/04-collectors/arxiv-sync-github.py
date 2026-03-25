#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian Sync to GitHub
Sync arxiv papers to github.com/shushuzn/obsidian-sync

功能:
- 检查 git 状态
- 添加新文件
- 生成提交信息
- 推送到 GitHub
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ==================== 配置 ====================

VAULT_PATH = Path(r"D:\obsidian\Vault")
ARXIV_PATH = VAULT_PATH / "arxiv"
GITHUB_REPO = "https://github.com/shushuzn/obsidian-sync"

# ==================== 工具函数 ====================

def run_git(args, cwd=VAULT_PATH):
    """运行 git 命令"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_setup():
    """检查 git 是否配置"""
    print("[1/5] 检查 Git 配置...")

    # 检查是否是 git 仓库
    success, out, err = run_git(["rev-parse", "--git-dir"])
    if not success:
        print(f"  [WARN] 不是 git 仓库，需要初始化")
        return False

    # 检查远程
    success, out, err = run_git(["remote", "-v"])
    if success and out:
        print(f"  [OK] 远程仓库已配置")
        print(f"  {out.strip()}")
        return True
    else:
        print(f"  [WARN] 未配置远程仓库")
        return False

def init_git():
    """初始化 git 仓库"""
    print("\n[2/5] 初始化 Git...")

    # 初始化
    success, out, err = run_git(["init"])
    if not success:
        print(f"  [FAIL] 初始化失败：{err}")
        return False
    print(f"  [OK] Git 仓库已初始化")

    # 配置用户信息
    run_git(["config", "user.name", "华为"])
    run_git(["config", "user.email", "user@example.com"])
    print(f"  [OK] 用户信息已配置")

    # 添加远程
    success, out, err = run_git(["remote", "add", "origin", GITHUB_REPO])
    if success:
        print(f"  [OK] 远程仓库已添加：{GITHUB_REPO}")
    else:
        print(f"  [INFO] 远程可能已存在：{err}")

    return True

def get_new_files():
    """获取新文件列表"""
    print("\n[3/5] 扫描新文件...")

    success, out, err = run_git(["status", "--porcelain"])
    if not success:
        print(f"  [FAIL] 无法获取状态：{err}")
        return []

    new_files = []
    for line in out.strip().split('\n'):
        if line.startswith('?? '):
            filepath = line[3:].strip()
            if filepath.startswith('arxiv/'):
                new_files.append(filepath)

    print(f"  发现 {len(new_files)} 个新文件")
    if new_files[:5]:
        print(f"  示例:")
        for f in new_files[:5]:
            print(f"    - {f}")
        if len(new_files) > 5:
            print(f"    ... 还有 {len(new_files) - 5} 个")

    return new_files

def add_and_commit(files):
    """添加文件并提交"""
    if not files:
        print("\n[4/5] 没有新文件需要提交")
        return True

    print(f"\n[4/5] 添加并提交 {len(files)} 个文件...")

    # 添加 arxiv 目录
    success, out, err = run_git(["add", "arxiv/"])
    if not success:
        print(f"  [FAIL] 添加失败：{err}")
        return False
    print(f"  [OK] 文件已添加到暂存区")

    # 生成提交信息
    date_str = datetime.now().strftime('%Y-%m-%d')
    commit_msg = f"chore: sync arxiv papers ({date_str})\n\n- 新增论文：{len(files)} 篇\n- 自动同步 by arxiv-sync"

    success, out, err = run_git(["commit", "-m", commit_msg])
    if not success:
        print(f"  [FAIL] 提交失败：{err}")
        return False
    print(f"  [OK] 提交成功")
    print(f"  提交信息：{commit_msg.split(chr(10))[0]}")

    return True

def push_to_github():
    """推送到 GitHub"""
    print("\n[5/5] 推送到 GitHub...")

    success, out, err = run_git(["push", "-u", "origin", "master"])
    if not success:
        if "Authentication" in err or "authentication" in err.lower():
            print(f"  [WARN] 认证失败，需要配置凭证")
            print(f"  提示:")
            print(f"    1. 生成 GitHub Personal Access Token")
            print(f"    2. 运行：git config --global credential.helper store")
            print(f"    3. 再次推送")
            return False
        else:
            print(f"  [FAIL] 推送失败：{err}")
            return False

    print(f"  [OK] 推送成功")
    print(f"  仓库：{GITHUB_REPO}")

    return True

# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("Obsidian Sync to GitHub")
    print("同步 arxiv 论文到 github.com/shushuzn/obsidian-sync")
    print("=" * 60)

    # 检查 git 配置
    if not check_git_setup():
        if not init_git():
            print("\n[ERROR] Git 初始化失败")
            return False

    # 获取新文件
    new_files = get_new_files()

    # 添加并提交
    if not add_and_commit(new_files):
        print("\n[ERROR] 提交失败")
        return False

    # 推送
    if new_files:
        if not push_to_github():
            print("\n[WARN] 推送失败，可以稍后手动执行：git push")
            return False

    # 完成
    print("\n" + "=" * 60)
    print("[SUCCESS] 同步完成")
    print(f"  仓库：{GITHUB_REPO}")
    print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
