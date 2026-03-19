#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Timeout Optimizer - 超时优化

功能:
- 根据任务类型优化超时设置
- 避免过长等待
- 提供超时建议
"""

from datetime import datetime

# 任务类型超时配置 (秒)
TIMEOUT_CONFIG = {
    "default": 60,
    "quick": 10,
    "standard": 60,
    "long": 300,
    "very_long": 1800,
    
    # 具体任务类型
    "file_read": 10,
    "file_write": 30,
    "git_operation": 60,
    "web_request": 30,
    "code_execution": 120,
    "model_inference": 300,
    "batch_processing": 600,
    "session_compress": 60,
    "workflow_execution": 1800
}

def get_timeout(task_type="default"):
    """获取超时设置"""
    return TIMEOUT_CONFIG.get(task_type, TIMEOUT_CONFIG["default"])

def optimize_timeout(task_description, current_timeout=None):
    """根据任务描述优化超时"""
    
    task_lower = task_description.lower()
    
    # 识别任务类型
    if any(kw in task_lower for kw in ["read", "list", "show", "check"]):
        suggested_type = "quick"
    elif any(kw in task_lower for kw in ["write", "create", "update"]):
        suggested_type = "standard"
    elif any(kw in task_lower for kw in ["git", "commit", "push"]):
        suggested_type = "git_operation"
    elif any(kw in task_lower for kw in ["web", "http", "api", "fetch"]):
        suggested_type = "web_request"
    elif any(kw in task_lower for kw in ["execute", "run", "compile"]):
        suggested_type = "code_execution"
    elif any(kw in task_lower for kw in ["model", "inference", "generate"]):
        suggested_type = "model_inference"
    elif any(kw in task_lower for kw in ["batch", "bulk", "multiple"]):
        suggested_type = "batch_processing"
    elif any(kw in task_lower for kw in ["compress", "distill", "summarize"]):
        suggested_type = "session_compress"
    elif any(kw in task_lower for kw in ["workflow", "pipeline", "full"]):
        suggested_type = "workflow_execution"
    else:
        suggested_type = "default"
    
    suggested_timeout = get_timeout(suggested_type)
    
    analysis = {
        "task": task_description,
        "current_timeout": current_timeout,
        "suggested_type": suggested_type,
        "suggested_timeout": suggested_timeout,
        "timestamp": datetime.now().isoformat()
    }
    
    # 判断是否需要优化
    if current_timeout is None:
        analysis["recommendation"] = f"设置超时为 {suggested_timeout} 秒"
    elif current_timeout > suggested_timeout * 2:
        analysis["recommendation"] = f"当前超时 {current_timeout} 秒过长，建议减少到 {suggested_timeout} 秒"
    elif current_timeout < suggested_timeout / 2:
        analysis["recommendation"] = f"当前超时 {current_timeout} 秒过短，建议增加到 {suggested_timeout} 秒"
    else:
        analysis["recommendation"] = "当前超时设置合理"
    
    return analysis

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: py timeout_optimizer.py <task_description> [current_timeout]")
        print("Example: py timeout_optimizer.py \"git commit and push\" 120")
        return
    
    task = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 else " ".join(sys.argv[1:])
    current_timeout = int(sys.argv[-1]) if len(sys.argv) > 2 and sys.argv[-1].isdigit() else None
    
    analysis = optimize_timeout(task, current_timeout)
    
    print("=" * 70)
    print("⏱️  超时优化分析")
    print("=" * 70)
    
    print(f"\n📝 任务：{analysis['task']}")
    print(f"⏰ 时间：{analysis['timestamp']}")
    print(f"\n📊 当前超时：{analysis['current_timeout']} 秒" if analysis['current_timeout'] else "\n📊 当前超时：未设置")
    print(f"💡 建议类型：{analysis['suggested_type']}")
    print(f"💡 建议超时：{analysis['suggested_timeout']} 秒")
    print(f"\n✅ 建议：{analysis['recommendation']}")
    
    print("\n" + "=" * 70)
    print("📋 超时配置参考:")
    for task_type, timeout in TIMEOUT_CONFIG.items():
        if not task_type.startswith("_"):
            print(f"    {task_type}: {timeout} 秒")
    print("=" * 70)

if __name__ == '__main__':
    main()
