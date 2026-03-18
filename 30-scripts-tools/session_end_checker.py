#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session End Checker - 会话结束检测

功能:
- 检测会话是否即将结束
- 提醒用户压缩会话
- 可选自动压缩

使用:
  py session_end_checker.py --check    # 检查是否需要压缩
  py session_end_checker.py --compress # 直接压缩
  py session_end_checker.py --auto     # 自动模式 (心跳调用)
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / "13-memory"
STATE_FILE = MEMORY_DIR / "session-state.json"
COMPRESS_SCRIPT = WORKSPACE / "30-scripts-tools" / "post_session_compress.py"


def get_session_state() -> dict:
    """获取会话状态"""
    if not STATE_FILE.exists():
        return {}
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_session_compressed() -> tuple:
    """检查会话是否已压缩"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = MEMORY_DIR / f"{today}.md"
    
    if not daily_file.exists():
        return False, "今日笔记不存在"
    
    content = daily_file.read_text(encoding='utf-8')
    
    has_summary = "## Session Summary" in content or "## Session Context" in content
    
    if has_summary:
        # 检查最近一次压缩时间
        import re
        pattern = r"## Session (?:Summary|Context) \((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\)"
        matches = re.findall(pattern, content)
        if matches:
            last_time = datetime.fromisoformat(matches[-1].replace(' ', 'T'))
            time_diff = datetime.now() - last_time
            
            if time_diff.total_seconds() < 300:  # 5 分钟内
                return True, f"已压缩 ({int(time_diff.total_seconds()/60)}分钟前)"
            else:
                return True, f"已压缩 ({int(time_diff.total_seconds()/60)}分钟前)"
        return True, "已压缩"
    else:
        return False, "未压缩 (缺少 Session Summary)"


def check_session_idle() -> tuple:
    """检查会话是否空闲过久"""
    state = get_session_state()
    
    if not state:
        return False, "无会话状态记录"
    
    last_check = state.get("timestamp")
    if not last_check:
        return False, "无上次检查时间"
    
    last_time = datetime.fromisoformat(last_check)
    time_diff = datetime.now() - last_time
    
    hours = time_diff.total_seconds() / 3600
    
    if hours > 2:
        return True, f"会话空闲{hours:.1f}小时"
    elif hours > 1:
        return False, f"会话活跃{hours:.1f}小时前"
    else:
        return False, f"会话活跃{int(hours*60)}分钟前"


def auto_compress() -> bool:
    """自动压缩会话"""
    if not COMPRESS_SCRIPT.exists():
        print("[ERROR] 压缩脚本不存在")
        return False
    
    # 创建临时数据
    temp_file = WORKSPACE / "30-scripts-tools" / "session_temp.json"
    temp_data = {
        "timestamp": datetime.now().isoformat(),
        "topics": ["Auto-compressed by end-checker"],
        "decisions": ["Auto-compressed at session end"],
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
        if temp_file.exists():
            temp_file.unlink()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Session End Checker')
    parser.add_argument('--check', action='store_true', help='检查压缩状态')
    parser.add_argument('--compress', action='store_true', help='直接压缩')
    parser.add_argument('--auto', action='store_true', help='自动模式 (心跳)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Session End Checker - 会话结束检测")
    print("=" * 60)
    
    if args.check or args.auto:
        # 检查压缩状态
        compressed, msg = check_session_compressed()
        print(f"\n压缩状态：{msg}")
        
        # 检查空闲时间
        idle, idle_msg = check_session_idle()
        print(f"空闲状态：{idle_msg}")
        
        if not compressed:
            print("\n[WARN] 会话未压缩！")
            if args.auto:
                print("[INFO] 自动模式：执行压缩...")
                auto_compress()
            else:
                print("\n建议运行：py 30-scripts-tools\\post_session_compress.py --auto")
                print("或使用：end-session.bat")
        else:
            print("\n[OK] 会话已压缩")
        
        if args.auto:
            # 保存检查结果
            state = get_session_state()
            state['last_end_check'] = datetime.now().isoformat()
            state['compressed'] = compressed
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
    
    elif args.compress:
        print("\n手动压缩会话...")
        auto_compress()
    
    else:
        print("\n使用方法:")
        print("  py session_end_checker.py --check    # 检查状态")
        print("  py session_end_checker.py --compress # 直接压缩")
        print("  py session_end_checker.py --auto     # 自动模式")
    
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
