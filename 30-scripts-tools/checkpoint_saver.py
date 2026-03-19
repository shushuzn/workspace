#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Checkpoint Saver - 检查点保存

功能:
- 保存任务执行检查点
- 支持恢复
- 防止中断丢失进度
"""

import json
from pathlib import Path
from datetime import datetime

CHECKPOINT_DIR = Path("D:\\OpenClaw\\workspace\\checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

def save_checkpoint(task_id, step, data=None):
    """保存检查点"""
    
    timestamp = datetime.now().isoformat()
    
    checkpoint = {
        "task_id": task_id,
        "step": step,
        "timestamp": timestamp,
        "data": data or {}
    }
    
    checkpoint_file = CHECKPOINT_DIR / f"{task_id}_checkpoint.json"
    
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    print(f"💾 检查点已保存：{task_id} - Step {step}")
    
    return True

def load_checkpoint(task_id):
    """加载检查点"""
    
    checkpoint_file = CHECKPOINT_DIR / f"{task_id}_checkpoint.json"
    
    if not checkpoint_file.exists():
        return None
    
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        return checkpoint
    except:
        return None

def clear_checkpoint(task_id):
    """清除检查点"""
    
    checkpoint_file = CHECKPOINT_DIR / f"{task_id}_checkpoint.json"
    
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        print(f"🗑️  检查点已清除：{task_id}")
        return True
    
    return False

def list_checkpoints():
    """列出所有检查点"""
    
    checkpoints = []
    
    for checkpoint_file in CHECKPOINT_DIR.glob("*_checkpoint.json"):
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            checkpoints.append(checkpoint)
        except:
            pass
    
    return checkpoints

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: py checkpoint_saver.py <command> [args]")
        print("Commands:")
        print("  save <task_id> <step> - 保存检查点")
        print("  load <task_id> - 加载检查点")
        print("  clear <task_id> - 清除检查点")
        print("  list - 列出所有检查点")
        return
    
    command = sys.argv[1]
    
    if command == "save" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        step = sys.argv[3]
        data = sys.argv[4] if len(sys.argv) > 4 else None
        save_checkpoint(task_id, step, {"data": data})
    
    elif command == "load" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        checkpoint = load_checkpoint(task_id)
        if checkpoint:
            print(f"💾 检查点：{checkpoint}")
        else:
            print("⚠️  未找到检查点")
    
    elif command == "clear" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        clear_checkpoint(task_id)
    
    elif command == "list":
        checkpoints = list_checkpoints()
        print(f"📊 检查点列表 ({len(checkpoints)} 个):")
        for cp in checkpoints:
            print(f"  - {cp['task_id']}: Step {cp['step']} @ {cp['timestamp']}")
    
    else:
        print("⚠️  未知命令或参数不足")

if __name__ == '__main__':
    main()
