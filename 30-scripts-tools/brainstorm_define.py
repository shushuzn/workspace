#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
头脑风暴 Step 1: 问题定义工具
定义头脑风暴的主题、背景、约束和期望产出
"""

import json
import os
from datetime import datetime
from pathlib import Path

def run():
    """执行问题定义"""
    
    print("="*60)
    print("🧠 头脑风暴 Step 1: 问题定义")
    print("="*60)
    
    # 获取用户输入
    topic = input("\n📌 主题 (一句话描述): ").strip()
    if not topic:
        print("❌ 主题不能为空")
        return None
    
    background = input("\n📝 背景信息 (按回车跳过): ").strip()
    constraints = input("\n⚠️ 约束条件 (按回车跳过): ").strip()
    expected = input("\n🎯 期望产出 (按回车跳过): ").strip()
    
    # 构建输出
    result = {
        "step": "problem_definition",
        "topic": topic,
        "background": background or "未提供",
        "constraints": constraints or "无",
        "expected_output": expected or "创意方案清单",
        "created_at": datetime.now().isoformat()
    }
    
    # 保存文件
    output_path = Path("flow-archive/brainstorm-current/brainstorm_topic.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到: {output_path}")
    return result

if __name__ == "__main__":
    run()