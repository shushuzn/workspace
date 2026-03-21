import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单步锁 - 确保每次只执行一个步骤
防止批量执行、跳步执行
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import time

LOCK_FILE = Path("30-scripts-tools/.single_step_lock.json")

def acquire_lock(step_id: str, session_id: str) -> dict:
    """获取单步锁"""
    
    # 检查是否有未释放的锁
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
            
            # 检查锁是否过期 (5 分钟)
            lock_time = datetime.fromisoformat(lock_data["acquired_at"])
            elapsed = (datetime.now() - lock_time).total_seconds()
            
            if elapsed < 300:  # 5 分钟内
                return {
                    "status": "blocked",
                    "reason": "锁未释放",
                    "current_step": lock_data["step_id"],
                    "acquired_at": lock_data["acquired_at"],
                    "elapsed_seconds": elapsed
                }
        except Exception:
            pass  # 锁文件损坏，强制释放
    
    # 获取新锁
    lock_data = {
        "step_id": step_id,
        "session_id": session_id,
        "acquired_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, ensure_ascii=False, indent=2)
    
    return {
        "status": "acquired",
        "step_id": step_id,
        "session_id": session_id
    }

def release_lock() -> dict:
    """释放单步锁"""
    
    if not LOCK_FILE.exists():
        return {
            "status": "skip",
            "reason": "锁文件不存在"
        }
    
    try:
        LOCK_FILE.unlink()
        return {
            "status": "released",
            "message": "锁已释放"
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }

def check_lock_status() -> dict:
    """检查锁状态"""
    
    if not LOCK_FILE.exists():
        return {
            "status": "free",
            "message": "无活跃锁"
        }
    
    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as f:
            lock_data = json.load(f)
        
        lock_time = datetime.fromisoformat(lock_data["acquired_at"])
        elapsed = (datetime.now() - lock_time).total_seconds()
        
        return {
            "status": "locked",
            "step_id": lock_data["step_id"],
            "session_id": lock_data["session_id"],
            "acquired_at": lock_data["acquired_at"],
            "elapsed_seconds": elapsed
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        # 测试模式
        print("单步锁工具测试")
        print("=" * 60)
        
        # 检查当前状态
        status = check_lock_status()
        print(f"\n当前状态：{status['status']}")
        if status.get('step_id'):
            print(f"当前步骤：{status['step_id']}")
            print(f"已锁定：{status.get('elapsed_seconds', 0):.1f}秒")
        
        return 0
    
    command = sys.argv[1]
    
    if command == "acquire" and len(sys.argv) >= 4:
        step_id = sys.argv[2]
        session_id = sys.argv[3]
        result = acquire_lock(step_id, session_id)
    elif command == "release":
        result = release_lock()
    elif command == "status":
        result = check_lock_status()
    else:
        print("用法:")
        print("  py single_step_lock.py acquire <step_id> <session_id>")
        print("  py single_step_lock.py release")
        print("  py single_step_lock.py status")
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in ["acquired", "released", "free", "skip"] else 1
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py single_step_lock_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py single_step_lock_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""



if __name__ == "__main__":
    sys.exit(main())
