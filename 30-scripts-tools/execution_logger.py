#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Execution Logger - 执行日志记录

功能:
- 记录工具调用和执行结果
- 保存到日志文件
- 支持查询和过滤
"""

import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("D:\\OpenClaw\\workspace\\logs\\execution")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_execution(tool_name, status, details=None, cwd="D:\\OpenClaw\\workspace"):
    """记录执行日志"""
    
    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    log_entry = {
        "timestamp": timestamp,
        "tool_name": tool_name,
        "status": status,  # "success" | "failed" | "skipped"
        "details": details or {}
    }
    
    # 保存到每日日志
    log_file = LOG_DIR / f"execution_{date_str}.json"
    
    logs = []
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    print(f"📝 日志已记录：{tool_name} - {status}")
    
    return True

def get_logs(date=None, tool_name=None, status=None):
    """获取日志"""
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    log_file = LOG_DIR / f"execution_{date}.json"
    
    if not log_file.exists():
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        return []
    
    # 过滤
    filtered = []
    for log in logs:
        if tool_name and tool_name not in log.get("tool_name", ""):
            continue
        if status and status != log.get("status"):
            continue
        filtered.append(log)
    
    return filtered

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: py execution_logger.py <tool_name> [status] [details]")
        print("Example: py execution_logger.py \"tool_executor\" success")
        return
    
    tool_name = sys.argv[1]
    status = sys.argv[2] if len(sys.argv) > 2 else "success"
    details = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = log_execution(tool_name, status, {"args": details})
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
