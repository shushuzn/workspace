#!/usr/bin/env python3
# setup-scheduled-task.py - 配置每日简报定时任务
# 用法：py setup-scheduled-task.py

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("D:/OpenClaw/workspace")
SCRIPT_PATH = WORKSPACE / "30-scripts" / "daily-brief.py"
TASK_NAME = "DailyBrief-Feishu"

print("=" * 60)
print("📅 配置每日简报定时任务")
print("=" * 60)
print(f"  任务名称：{TASK_NAME}")
print(f"  脚本路径：{SCRIPT_PATH}")
print(f"  触发时间：每工作日 08:00")
print()

# 使用 schtasks 命令创建任务
# 注意：/d 参数仅用于 ONCE 类型，DAILY 类型使用 /MO 修饰符
cmd = [
    "schtasks", "/create",
    "/tn", TASK_NAME,
    "/tr", f'py "{SCRIPT_PATH}" --send',
    "/sc", "weekly",  # 使用 weekly 而非 daily
    "/st", "08:00",
    "/d", "MON,TUE,WED,THU,FRI",
    "/mo", "1",  # 每 1 周
    "/ru", "SYSTEM",
    "/f"  # 强制覆盖已存在的任务
]

print(f"执行命令：{' '.join(cmd)}")
print()

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
    
    if result.returncode == 0:
        print("✅ 定时任务创建成功！")
        print()
        print("📋 管理命令:")
        print(f"  查看任务：schtasks /query /tn \"{TASK_NAME}\"")
        print(f"  手动触发：schtasks /run /tn \"{TASK_NAME}\"")
        print(f"  删除任务：schtasks /delete /tn \"{TASK_NAME}\" /f")
        print(f"  禁用任务：schtasks /change /tn \"{TASK_NAME}\" /disable")
        print(f"  启用任务：schtasks /change /tn \"{TASK_NAME}\" /enable")
    else:
        print(f"⚠️ 创建失败 (返回码：{result.returncode})")
        if result.stderr:
            print(f"错误信息：{result.stderr}")
        print()
        print("💡 提示:")
        print("  1. 请以管理员身份运行 PowerShell 后重试")
        print("  2. 或手动执行上述 schtasks 命令")
        
except FileNotFoundError:
    print("❌ schtasks 命令未找到")
    print("  请确保在 Windows 系统上运行")
except Exception as e:
    print(f"❌ 异常：{e}")

print()
print("=" * 60)
