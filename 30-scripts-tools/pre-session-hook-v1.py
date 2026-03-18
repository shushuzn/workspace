#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-Session Hook - 会话前检查
强制 AI 遵守上下文加载规则
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
CONTEXTIGNORE = WORKSPACE / ".contextignore"
CORE_FILES = [
    "SOUL.md",
    "USER.md",
    "AGENTS.md",
    "TOOLS.md",
    "HEARTBEAT.md",
    "13-memory/MEMORY.md",
]
MAX_SIZE_KB = 100
STATE_FILE = WORKSPACE / "13-memory" / "session-state.json"

def check_contextignore():
    """检查.contextignore 是否存在"""
    if not CONTEXTIGNORE.exists():
        print("❌ .contextignore 不存在！创建中...")
        create_contextignore()
        return False
    print("✅ .contextignore 存在")
    return True

def create_contextignore():
    """创建.contextignore"""
    content = """# AI Context Ignore Rules
# Tell AI which directories NOT to scan

# Sub-repositories (independent context)
80-PROJECTS/
80-PROJECTS/rl-trading/
80-PROJECTS/cnt-research/

# Data collectors (auto-scanned content)
40-arxiv/
41-medium/
42-hackernews/
60-DATA/
08-collectors/

# Archive directories
99-archive-归档/
90-archive/
91-logs/

# Backup directories
99-backups/

# Large documents
*.md
!README.md
!AGENTS.md
!SOUL.md
!USER.md
!TOOLS.md
!HEARTBEAT.md
!MEMORY.md
!13-memory/*.md

# Test and temp files
92-tests/
*.tmp
*.log

# Node modules and venv
node_modules/
venv/
__pycache__/
*.pyc

# Research papers full content
**/deep/*-full.md
**/Archive/**/*.md

# Old workspace
99-workspace-archive/
"""
    with open(CONTEXTIGNORE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ .contextignore 已创建")

def check_core_files():
    """检查核心文件"""
    print("\n核心文件检查:")
    total_size = 0
    missing = []
    
    for file in CORE_FILES:
        path = WORKSPACE / file
        if path.exists():
            size = path.stat().st_size
            total_size += size
            status = "✅" if size < 50*1024 else "⚠️"
            print(f"  {status} {file}: {size/1024:.1f}KB")
        else:
            print(f"  ❌ {file}: 不存在")
            missing.append(file)
    
    # 检查今日笔记
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = WORKSPACE / "13-memory" / f"{today}.md"
    if daily_file.exists():
        size = daily_file.stat().st_size
        total_size += size
        print(f"  ✅ 13-memory/{today}.md: {size/1024:.1f}KB")
    
    print(f"\n总大小：{total_size/1024:.1f}KB")
    
    if total_size / 1024 > MAX_SIZE_KB:
        print(f"❌ 超过限制 ({MAX_SIZE_KB}KB)!")
        return False
    
    print(f"✅ 在限制内 (<{MAX_SIZE_KB}KB)")
    return len(missing) == 0

def check_forbidden_dirs():
    """检查.gitignore 是否包含禁止目录"""
    print("\n.gitignore 检查:")
    gitignore = WORKSPACE / ".gitignore"
    
    if not gitignore.exists():
        print("⚠️  .gitignore 不存在")
        return False
    
    with open(gitignore, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required = [
        "80-PROJECTS/",
        "99-backups/",
        "node_modules/",
        "__pycache__/",
    ]
    
    missing = []
    for pattern in required:
        if pattern not in content:
            missing.append(pattern)
    
    if missing:
        print(f"⚠️  .gitignore 缺少：{', '.join(missing)}")
        return False
    
    print("✅ .gitignore 配置正确")
    return True

def save_session_state(passed):
    """保存会话状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "timestamp": datetime.now().isoformat(),
        "checks_passed": passed,
        "core_files_size_kb": sum(
            (WORKSPACE / f).stat().st_size / 1024
            for f in CORE_FILES
            if (WORKSPACE / f).exists()
        ),
    }
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f"\n会话状态已保存：{STATE_FILE}")

def main():
    print("=" * 60)
    print("Pre-Session Hook - 会话前检查")
    print("=" * 60)
    
    checks = [
        (".contextignore", check_contextignore()),
        ("核心文件", check_core_files()),
        ("禁止目录", check_forbidden_dirs()),
    ]
    
    print("\n" + "=" * 60)
    print("检查结果:")
    all_passed = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ 所有检查通过！可以开始会话")
    else:
        print("❌ 有检查未通过！请纠正后再开始")
    
    save_session_state(all_passed)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
