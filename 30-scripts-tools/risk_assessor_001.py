import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
风险评级工具 - 评估操作风险等级
🟢 低风险：读取、查询、分析
🟡 中风险：创建、修改
🔴 高风险：删除、覆盖、同步
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# 风险关键词
HIGH_RISK_KEYWORDS = [
    "delete", "remove", "sync", "overwrite", "replace",
    "cleanup", "destroy", "drop", "truncate", "format"
]

MEDIUM_RISK_KEYWORDS = [
    "create", "write", "update", "modify", "edit",
    "add", "insert", "append", "rebuild", "restore",
    "checkout", "reset", "revert"
]

# 高风险文件模式 (ASCII)
HIGH_RISK_PATTERNS = [
    "_registry.json",
    "_state.json",
    ".py",
    "workflow.json",
]

def assess_risk(command: str, file_path: str = None) -> dict:
    """评估操作风险"""
    
    risk_score = 0  # 0-100
    risk_level = "🟢"  # 🟢🟡🔴
    reasons = []
    
    command_lower = command.lower()
    
    # 检查高风险关键词
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in command_lower:
            risk_score += 30
            reasons.append(f"包含高风险关键词：{keyword}")
    
    # 检查中风险关键词
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in command_lower:
            risk_score += 15
            reasons.append(f"包含中风险关键词：{keyword}")
    
    # 检查文件模式
    if file_path:
        for pattern in HIGH_RISK_PATTERNS:
            if pattern.replace("*", "") in file_path:
                risk_score += 20
                reasons.append(f"修改关键文件：{file_path}")
                break
    
    # 确定风险等级
    if risk_score >= 40:
        risk_level = "HIGH"
        requires_confirmation = True
    elif risk_score >= 15:
        risk_level = "MEDIUM"
        requires_confirmation = False
    else:
        risk_level = "LOW"
        requires_confirmation = False
    
    result = {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "requires_confirmation": requires_confirmation,
        "reasons": reasons,
        "command": command,
        "file_path": file_path,
        "timestamp": datetime.now().isoformat()
    }
    
    return result

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        # 测试模式
        test_cases = [
            ("py sync_registry.py", "30-scripts-tools/tools_registry.json"),
            ("py context_verify.py", None),
            ("git checkout HEAD -- file.py", "file.py"),
            ("py check_tool_files.py", None),
        ]
        
        print("=" * 60)
        print("风险评级测试")
        print("=" * 60)
        
        for cmd, path in test_cases:
            result = assess_risk(cmd, path)
            level_cn = {"HIGH": "高风险", "MEDIUM": "中风险", "LOW": "低风险"}
            print(f"\n命令：{cmd}")
            print(f"风险：{level_cn.get(result['risk_level'], result['risk_level'])} (分数：{result['risk_score']})")
            print(f"需要确认：{result['requires_confirmation']}")
            if result['reasons']:
                print("原因:")
                for r in result['reasons']:
                    print(f"  - {r}")
        
        return 0
    
    # 实际评估模式
    command = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = assess_risk(command, file_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 高风险时返回非零退出码
    return 1 if result["requires_confirmation"] else 0

if __name__ == "__main__":
    sys.exit(main())
