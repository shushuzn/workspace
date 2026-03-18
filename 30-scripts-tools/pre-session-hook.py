#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-Session Hook v2 - 会话前检查 + 自动压缩

功能:
- 检查上下文加载规则
- 检查上次会话是否压缩
- 自动压缩未压缩的会话
- 强制 AI 遵守规则
"""

import sys
import io
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

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
COMPRESS_SCRIPT = WORKSPACE / "30-scripts-tools" / "post_session_compress.py"


def check_contextignore() -> bool:
    """检查.contextignore 是否存在"""
    if not CONTEXTIGNORE.exists():
        print("[WARN] .contextignore 不存在！创建中...")
        create_contextignore()
        return False
    print("[OK] .contextignore 存在")
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
    print("[OK] .contextignore 已创建")


def check_core_files() -> tuple:
    """检查核心文件"""
    print("\n核心文件检查:")
    total_size = 0
    missing = []
    
    for file in CORE_FILES:
        path = WORKSPACE / file
        if path.exists():
            size = path.stat().st_size
            total_size += size
            status = "[OK]" if size < 50*1024 else "[WARN]"
            print(f"  {status} {file}: {size/1024:.1f}KB")
        else:
            print(f"  [ERROR] {file}: 不存在")
            missing.append(file)
    
    # 检查今日笔记
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = WORKSPACE / "13-memory" / f"{today}.md"
    if daily_file.exists():
        size = daily_file.stat().st_size
        total_size += size
        print(f"  [OK] 13-memory/{today}.md: {size/1024:.1f}KB")
    else:
        print(f"  [WARN] 13-memory/{today}.md: 不存在 (将自动创建)")
    
    print(f"\n总大小：{total_size/1024:.1f}KB")
    
    if total_size / 1024 > MAX_SIZE_KB:
        print(f"[ERROR] 超过限制 ({MAX_SIZE_KB}KB)!")
        return False, total_size / 1024
    
    print(f"[OK] 在限制内 (<{MAX_SIZE_KB}KB)")
    return len(missing) == 0, total_size / 1024


def check_forbidden_dirs() -> bool:
    """检查.gitignore 是否包含禁止目录"""
    print("\n.gitignore 检查:")
    gitignore = WORKSPACE / ".gitignore"
    
    if not gitignore.exists():
        print("[WARN] .gitignore 不存在")
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
        print(f"[WARN] .gitignore 缺少：{', '.join(missing)}")
        return False
    
    print("[OK] .gitignore 配置正确")
    return True


def check_session_compressed() -> tuple:
    """检查上次会话是否已压缩"""
    print("\n会话压缩检查:")
    
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = WORKSPACE / "13-memory" / f"{today}.md"
    
    if not daily_file.exists():
        print("[INFO] 今日笔记不存在 (首次会话)")
        return True, None  # 首次会话，无需压缩
    
    content = daily_file.read_text(encoding='utf-8')
    
    # 检查是否有 Session Summary
    has_summary = "## Session Summary" in content or "## Session Context" in content
    
    if has_summary:
        # 提取最近的摘要时间
        pattern = r"## Session (?:Summary|Context) \((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\)"
        matches = re.findall(pattern, content)
        if matches:
            last_compress = matches[-1]
            print(f"[OK] 已压缩：{last_compress}")
            return True, last_compress
        else:
            print("[OK] 已压缩 (未检测到时间戳)")
            return True, None
    else:
        print("[WARN] 未压缩：缺少 Session Summary/Context")
        return False, None


def auto_compress_session() -> bool:
    """自动压缩会话"""
    print("\n自动压缩会话:")
    
    if not COMPRESS_SCRIPT.exists():
        print("[ERROR] 压缩脚本不存在：{COMPRESS_SCRIPT}")
        return False
    
    print(f"[INFO] 运行：{COMPRESS_SCRIPT}")
    
    # 创建临时会话数据
    temp_file = WORKSPACE / "30-scripts-tools" / "session_temp.json"
    temp_data = {
        "timestamp": datetime.now().isoformat(),
        "topics": ["Auto-compressed session"],
        "decisions": ["Auto-compressed by pre-session-hook"],
        "tools_created": [],
        "files_modified": [],
        "metrics": {},
        "next_actions": []
    }
    
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(temp_data, f, indent=2, ensure_ascii=False)
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(COMPRESS_SCRIPT), "--auto"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] 自动压缩完成")
            return True
        else:
            print(f"[ERROR] 压缩失败：{result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] 压缩异常：{e}")
        return False
    finally:
        # 清理临时文件
        if temp_file.exists():
            temp_file.unlink()


def save_session_state(passed: bool, auto_compressed: bool = False):
    """保存会话状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 计算核心文件大小
    core_size = sum(
        (WORKSPACE / f).stat().st_size / 1024
        for f in CORE_FILES
        if (WORKSPACE / f).exists()
    )
    
    # 添加今日笔记大小
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = WORKSPACE / "13-memory" / f"{today}.md"
    if daily_file.exists():
        core_size += daily_file.stat().st_size / 1024
    
    state = {
        "timestamp": datetime.now().isoformat(),
        "checks_passed": passed,
        "auto_compressed": auto_compressed,
        "core_files_size_kb": round(core_size, 2),
        "context_limit_kb": MAX_SIZE_KB,
    }
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"\n会话状态已保存：{STATE_FILE}")


def main():
    print("=" * 60)
    print("Pre-Session Hook v2 - 会话前检查 + 自动压缩")
    print("=" * 60)
    
    # 基础检查
    checks = [
        (".contextignore", check_contextignore()),
        ("核心文件", check_core_files()[0]),
        ("禁止目录", check_forbidden_dirs()),
    ]
    
    # 会话压缩检查 (关键)
    compressed, last_time = check_session_compressed()
    checks.append(("会话压缩", compressed))
    
    # 如果未压缩，自动执行
    auto_compressed = False
    if not compressed:
        print("\n[INFO] 检测到未压缩会话，正在自动压缩...")
        if auto_compress_session():
            auto_compressed = True
            # 重新检查
            compressed, last_time = check_session_compressed()
            checks[-1] = ("会话压缩 (已自动)", compressed)
    
    # 显示结果
    print("\n" + "=" * 60)
    print("检查结果:")
    all_passed = True
    for name, passed in checks:
        status = "[OK]" if passed else "[ERROR]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[OK] 所有检查通过！可以开始会话")
    else:
        print("\n[WARN] 有检查未通过！请纠正后再开始")
    
    save_session_state(all_passed, auto_compressed)
    
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
