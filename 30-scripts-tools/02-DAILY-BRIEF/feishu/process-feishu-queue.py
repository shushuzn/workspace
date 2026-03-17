#!/usr/bin/env python3
# process-feishu-queue.py - 处理 Feishu 发送队列
# 用法：py process-feishu-queue.py
# 定时任务：每 5 分钟检查一次

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
QUEUE_FILE = WORKSPACE / "13-memory" / "feishu-queue.json"
LOG_FILE = WORKSPACE / "21-reports" / "feishu-send-log.jsonl"

def log_send(result, content_preview=""):
    """记录发送日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "success": result,
        "preview": content_preview[:100] if content_preview else ""
    }
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def send_via_sessions_send(content, file_path):
    """通过 sessions_send 发送到 Feishu"""
    # 使用 OpenClaw sessions_send 工具
    # 这需要调用 OpenClaw 的内部 API
    
    # 方法：创建一个临时会话消息文件，由 OpenClaw 处理
    message_file = WORKSPACE / "13-memory" / f"feishu-msg-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    
    message = {
        "action": "send",
        "channel": "feishu",
        "message": content[:2000],  # 限制长度
        "filePath": str(file_path)
    }
    
    message_file.write_text(json.dumps(message, ensure_ascii=False, indent=2), encoding="utf-8")
    return message_file

def process_queue():
    """处理发送队列"""
    if not QUEUE_FILE.exists():
        print("✅ 队列为空")
        return 0
    
    try:
        queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except:
        print("⚠️ 队列文件损坏，清空重建")
        QUEUE_FILE.unlink()
        return 0
    
    if not queue:
        print("✅ 队列为空")
        return 0
    
    print(f"📋 待发送：{len(queue)} 条")
    
    processed = 0
    for item in queue[:]:  # 复制列表以便删除
        try:
            print(f"\n📤 发送：{item.get('type', 'unknown')}")
            
            # 读取文件内容
            file_path = Path(item.get("file", ""))
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
            else:
                content = item.get("content", "")
            
            # 创建消息文件 (由 OpenClaw 处理)
            msg_file = send_via_sessions_send(content, file_path)
            print(f"  └─ 消息文件：{msg_file.name}")
            
            # 记录日志
            log_send(True, content)
            
            # 从队列移除
            queue.remove(item)
            processed += 1
            
        except Exception as e:
            print(f"  └─ ❌ 失败：{e}")
            log_send(False, str(e))
    
    # 更新队列文件
    if queue:
        QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        QUEUE_FILE.unlink()
    
    print(f"\n✅ 处理完成：{processed} 条发送，{len(queue)} 条剩余")
    return processed

if __name__ == "__main__":
    process_queue()
