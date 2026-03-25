#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户确认门 - 高风险操作前必须用户确认
"""
import sys
import json
from datetime import datetime

def request_confirmation(operation: str, risk_level: str, reasons: list):
    """请求用户确认"""

    print("=" * 60)
    print("高风险操作确认")
    print("=" * 60)
    print(f"\n操作：{operation}")
    print(f"风险等级：{risk_level}")

    if reasons:
        print("\n风险原因:")
        for r in reasons:
            print(f"  - {r}")

    print("\n" + "=" * 60)
    print("此操作已记录到日志，等待用户确认...")
    print("=" * 60)

    # 记录到日志
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "risk_level": risk_level,
        "reasons": reasons,
        "status": "pending_confirmation"
    }

    # 追加到确认日志
    try:
        with open("30-scripts-tools/confirmation_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # 返回需要确认的信号
    return {
        "status": "pending",
        "message": "需要用户确认",
        "log_entry": log_entry
    }

def main():
    if len(sys.argv) < 3:
        print("用法：py confirmation_gate.py <operation> <risk_level> [reasons_json]")
        sys.exit(1)

    operation = sys.argv[1]
    risk_level = sys.argv[2]
    reasons = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []

    result = request_confirmation(operation, risk_level, reasons)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 高风险返回非零，表示需要确认
    sys.exit(1 if result["status"] == "pending" else 0)

if __name__ == "__main__":
    main()
