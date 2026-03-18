#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Define - 问题定义工具

目标：清晰定义头脑风暴的主题和边界
输出：brainstorm_topic.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置 UTF-8 输出
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 配置
OUTPUT_DIR = Path("30-scripts-tools")
TOPIC_FILE = OUTPUT_DIR / "brainstorm_topic.json"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"[{text}]")
    print(f"{'='*60}\n")

def define_topic():
    """定义头脑风暴主题"""
    print_header("🎯 头脑风暴问题定义")
    
    # 检查是否已有定义
    if TOPIC_FILE.exists():
        print(f"⚠️  已存在主题定义：{TOPIC_FILE}")
        print("   是否重新定义？(y/n): ", end='')
        response = input().strip().lower()
        if response != 'y':
            print("✅ 使用现有主题定义")
            return load_topic()
    
    # 交互式定义
    print("请回答以下问题：\n")
    
    topic = input("1. 头脑风暴主题 (一句话): ").strip()
    if not topic:
        print("❌ 主题不能为空")
        return None
    
    background = input("2. 背景信息 (为什么做这个): ").strip()
    
    constraints = input("3. 约束条件 (时间/资源/技术等): ").strip()
    
    expected_output = input("4. 期望产出 (想法清单/方案/大纲等): ").strip()
    
    participants = input("5. 参与者 (个人/团队): ").strip() or "个人"
    
    time_limit = input("6. 时间限制 (分钟): ").strip() or "30"
    
    # 构建主题定义
    topic_def = {
        "topic": topic,
        "background": background,
        "constraints": constraints,
        "expected_output": expected_output,
        "participants": participants,
        "time_limit_minutes": int(time_limit),
        "created_at": datetime.now().isoformat(),
        "flow_id": "20260318-brainstorm-001",
        "status": "defined"
    }
    
    # 保存
    with open(TOPIC_FILE, 'w', encoding='utf-8') as f:
        json.dump(topic_def, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 主题定义已保存：{TOPIC_FILE}")
    print(f"   主题：{topic}")
    print(f"   时间限制：{time_limit} 分钟")
    
    return topic_def

def load_topic():
    """加载现有主题定义"""
    if not TOPIC_FILE.exists():
        return None
    
    with open(TOPIC_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_topic(topic_def):
    """验证主题定义质量"""
    checks = []
    passed = 0
    
    # 检查项
    checks.append(("主题清晰", len(topic_def.get('topic', '')) > 5))
    checks.append(("背景信息", len(topic_def.get('background', '')) > 10))
    checks.append(("约束条件", len(topic_def.get('constraints', '')) > 0))
    checks.append(("期望产出", len(topic_def.get('expected_output', '')) > 0))
    checks.append(("时间限制", topic_def.get('time_limit_minutes', 0) > 0))
    
    for name, passed_check in checks:
        status = "✅" if passed_check else "❌"
        print(f"  {status} {name}")
        if passed_check:
            passed += 1
    
    return passed, len(checks)

def main():
    topic_def = define_topic()
    
    if not topic_def:
        print("\n❌ 主题定义失败")
        sys.exit(1)
    
    print_header("验证主题定义")
    passed, total = validate_topic(topic_def)
    
    print(f"\n验证结果：{passed}/{total} 通过")
    
    if passed == total:
        print("✅ 主题定义完整")
        sys.exit(0)
    else:
        print("⚠️  主题定义不完整，但可以继续")
        sys.exit(0)

if __name__ == "__main__":
    main()
