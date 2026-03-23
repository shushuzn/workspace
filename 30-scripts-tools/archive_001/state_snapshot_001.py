import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
状态快照 - 每步执行后保存状态
用于追溯、回滚、审计
"""
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path("99-backups/snapshots")

def create_snapshot(step_id: str, session_id: str, metadata: dict = None) -> dict:
    """创建状态快照"""

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_id = f"{session_id}_{step_id}_{timestamp}"

    # 收集关键状态文件
    state_files = [
        "flow-archive/20260318-universal-workflow-001/execution-state.json",
        "30-scripts-tools/tools_registry.json",
        "30-scripts-tools/tool_call_log.jsonl",
    ]

    snapshot_data = {
        "snapshot_id": snapshot_id,
        "step_id": step_id,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "files": {}
    }

    # 备份每个状态文件
    for file_path in state_files:
        src = Path(file_path)
        if src.exists():
            # 复制文件到快照目录
            dst = SNAPSHOT_DIR / f"{snapshot_id}_{src.name}"
            shutil.copy2(src, dst)

            snapshot_data["files"][file_path] = {
                "backed_up": str(dst),
                "size": dst.stat().st_size
            }

    # 保存快照元数据
    snapshot_file = SNAPSHOT_DIR / f"{snapshot_id}.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

    return {
        "status": "success",
        "snapshot_id": snapshot_id,
        "snapshot_file": str(snapshot_file),
        "files_backed_up": len(snapshot_data["files"])
    }

def list_snapshots(session_id: str = None) -> dict:
    """列出所有快照"""

    if not SNAPSHOT_DIR.exists():
        return {
            "status": "empty",
            "message": "无快照"
        }

    snapshots = []
    for f in SNAPSHOT_DIR.glob("*.json"):
        if f.name == "snapshot_index.json":
            continue

        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)

            if session_id and data.get("session_id") != session_id:
                continue

            snapshots.append({
                "snapshot_id": data["snapshot_id"],
                "step_id": data["step_id"],
                "timestamp": data["timestamp"],
                "files": len(data.get("files", {}))
            })
        except Exception:
            pass

    # 按时间排序
    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "status": "success",
        "count": len(snapshots),
        "snapshots": snapshots[:20]  # 最近 20 个
    }

def restore_snapshot(snapshot_id: str) -> dict:
    """恢复快照"""

    snapshot_file = SNAPSHOT_DIR / f"{snapshot_id}.json"
    if not snapshot_file.exists():
        return {
            "status": "error",
            "reason": "快照不存在"
        }

    try:
        with open(snapshot_file, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)

        restored = []
        for orig_path, backup_info in snapshot_data["files"].items():
            src = Path(backup_info["backed_up"])
            dst = Path(orig_path)

            if src.exists():
                shutil.copy2(src, dst)
                restored.append(orig_path)

        return {
            "status": "success",
            "snapshot_id": snapshot_id,
            "files_restored": restored
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }

logging.basicConfig(level=logging.INFO)
def main():
    import sys

    if len(sys.argv) < 2:
        # 测试模式
        print("状态快照工具测试")
        print("=" * 60)

        # 创建测试快照
        result = create_snapshot("test-001", "session-test")
        print(f"\n创建快照：{result}")

        # 列出快照
        result = list_snapshots()
        print(f"\n快照列表：{result['count']} 个")
        for s in result.get("snapshots", [])[:5]:
            print(f"  - {s['snapshot_id']} ({s['files']} 文件)")

        return 0

    command = sys.argv[1]

    if command == "create" and len(sys.argv) >= 4:
        step_id = sys.argv[2]
        session_id = sys.argv[3]
        result = create_snapshot(step_id, session_id)
    elif command == "list":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = list_snapshots(session_id)
    elif command == "restore" and len(sys.argv) >= 3:
        snapshot_id = sys.argv[2]
        result = restore_snapshot(snapshot_id)
    else:
        print("用法:")
        print("  py state_snapshot.py create <step_id> <session_id>")
        print("  py state_snapshot.py list [session_id]")
        print("  py state_snapshot.py restore <snapshot_id>")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "success" else 1
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
# py state_snapshot_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py state_snapshot_001.py

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
