#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify Deliverables - 验证交付物完整性

检查所有交付物是否已完成并符合要求
"""

import json
from pathlib import Path
from datetime import datetime

WORKFLOW_DIR = Path("flow-archive/20260318-universal-workflow-001")

def verify_deliverables():
    """验证交付物完整性"""
    
    print("=" * 70)
    print("✅ 验证交付物完整性")
    print("=" * 70)
    
    # 必需交付物清单
    required_files = {
        "SPEED-OPTIMIZATION-FINAL-SUMMARY.md": "速度优化最终总结报告",
        "SPEED-OPTIMIZATION-GUIDE.md": "优化实施指南",
        "performance-comparison-report.json": "性能对比报告",
        "checkpoint.json": "执行进度检查点",
        "workflow.json": "工作流配置"
    }
    
    verification_results = {
        "timestamp": datetime.now().isoformat(),
        "flow_id": "20260319-speed-optimization-phase3",
        "files_checked": [],
        "all_present": True,
        "issues": []
    }
    
    print(f"\n📊 检查必需交付物 ({len(required_files)} 个):\n")
    
    for filename, description in required_files.items():
        file_path = WORKFLOW_DIR / filename
        
        if file_path.exists():
            size = file_path.stat().st_size
            status = "✅"
            
            # 检查文件大小是否合理
            if filename.endswith('.md') and size < 1000:
                status = "⚠️"
                verification_results["issues"].append(f"{filename} 文件过小 ({size} bytes)")
            
            print(f"  {status} {filename}")
            print(f"      描述：{description}")
            print(f"      大小：{size} bytes")
            
            verification_results["files_checked"].append({
                "filename": filename,
                "exists": True,
                "size": size,
                "status": "pass" if status == "✅" else "warning"
            })
        else:
            print(f"  ❌ {filename}")
            print(f"      描述：{description}")
            print(f"      状态：缺失")
            
            verification_results["files_checked"].append({
                "filename": filename,
                "exists": False,
                "status": "missing"
            })
            verification_results["all_present"] = False
            verification_results["issues"].append(f"{filename} 缺失")
        
        print()
    
    # 检查 checkpoint 进度
    checkpoint_file = WORKFLOW_DIR / "checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        print(f"📊 检查点进度:")
        print(f"  当前步骤：{checkpoint.get('current_step', 0)}/12")
        print(f"  已完成：{checkpoint.get('completed_steps', [])}")
        print(f"  进度：{checkpoint.get('progress_percentage', 0)}%")
        print()
        
        verification_results["checkpoint"] = {
            "current_step": checkpoint.get('current_step', 0),
            "completed_steps": checkpoint.get('completed_steps', []),
            "progress": checkpoint.get('progress_percentage', 0)
        }
    
    # 检查工具库
    tools_file = Path("30-scripts-tools/tools_registry.json")
    if tools_file.exists():
        with open(tools_file, 'r', encoding='utf-8') as f:
            tools = json.load(f)
        
        print(f"📊 工具库状态:")
        print(f"  版本：{tools.get('version', 'N/A')}")
        print(f"  工具数：{tools.get('total_tools', 'N/A')}")
        
        if "quality_assessment" in tools:
            qa = tools["quality_assessment"]
            print(f"  平均质量：{qa.get('average_score', 'N/A')} 分")
        print()
        
        verification_results["tools_registry"] = {
            "version": tools.get('version'),
            "total_tools": tools.get('total_tools')
        }
    
    # 总结
    print("=" * 70)
    if verification_results["all_present"] and not verification_results["issues"]:
        print("✅ 所有交付物验证通过!")
        print("✅ 可以进入下一步：Git 提交")
    else:
        print("⚠️  发现问题:")
        for issue in verification_results["issues"]:
            print(f"  - {issue}")
        print("\n❌ 请先修复问题再继续")
    print("=" * 70)
    
    # 保存验证结果
    result_file = WORKFLOW_DIR / "verification-result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(verification_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 验证结果已保存：{result_file}")
    
    return verification_results["all_present"] and not verification_results["issues"]


if __name__ == '__main__':
    success = verify_deliverables()
    exit(0 if success else 1)
