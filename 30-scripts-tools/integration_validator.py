#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration Validator - 工具集成验证器

验证新创建的工具是否:
1. 已注册到 tools_registry.json
2. 已集成到 tool_executor.py
3. 有实际调用场景

Usage:
    py integration_validator.py --tool <tool_name>
    py integration_validator.py --all
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
TOOLS_REGISTRY = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
TOOL_EXECUTOR = WORKSPACE / "30-scripts-tools" / "tool_executor.py"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"

def check_registration(tool_name: str) -> bool:
    """检查工具是否注册到 tools_registry.json"""
    if not TOOLS_REGISTRY.exists():
        print(f"{Colors.RED}❌ tools_registry.json 不存在{Colors.RESET}")
        return False
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 检查 tool_id
    tool_id = tool_name.replace(".py", "").replace("_", "-")
    if tool_id in tools:
        print(f"{Colors.GREEN}✅ 已注册：{tool_id}{Colors.RESET}")
        return True
    
    # 检查文件名
    if tool_name in tools:
        print(f"{Colors.GREEN}✅ 已注册：{tool_name}{Colors.RESET}")
        return True
    
    # 模糊匹配
    for tid in tools.keys():
        if tool_name.replace(".py", "") in tid or tid.replace("-", "_") in tool_name:
            print(f"{Colors.GREEN}✅ 已注册：{tid}{Colors.RESET}")
            return True
    
    print(f"{Colors.RED}❌ 未注册：{tool_name}{Colors.RESET}")
    return False

def check_tool_executor(tool_name: str) -> bool:
    """检查工具是否集成到 tool_executor.py"""
    if not TOOL_EXECUTOR.exists():
        print(f"{Colors.RED}❌ tool_executor.py 不存在{Colors.RESET}")
        return False
    
    with open(TOOL_EXECUTOR, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否导入
    tool_module = tool_name.replace(".py", "")
    if tool_module in content:
        print(f"{Colors.GREEN}✅ 已集成到 tool_executor.py (导入){Colors.RESET}")
        return True
    
    # 检查工具名
    if tool_name.replace(".py", "") in content:
        print(f"{Colors.GREEN}✅ 已集成到 tool_executor.py (引用){Colors.RESET}")
        return True
    
    print(f"{Colors.YELLOW}⚠️ 未集成到 tool_executor.py{Colors.RESET}")
    return False

def check_call_scenarios(tool_name: str) -> bool:
    """检查是否有实际调用场景"""
    # 检查工作流配置
    workflow_file = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001" / "workflow.json"
    
    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        steps = workflow.get("steps", [])
        for step in steps:
            tool_id = step.get("tool_id", "")
            if tool_name.replace(".py", "").replace("_", "-") in tool_id:
                print(f"{Colors.GREEN}✅ 在工作流中被调用：{step.get('name', 'unknown')}{Colors.RESET}")
                return True
    
    # 检查其他脚本
    scripts_dir = WORKSPACE / "30-scripts-tools"
    for script in scripts_dir.glob("*.py"):
        if script.name == tool_name:
            continue
        
        with open(script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if tool_name.replace(".py", "") in content:
            print(f"{Colors.GREEN}✅ 在 {script.name} 中被调用{Colors.RESET}")
            return True
    
    print(f"{Colors.YELLOW}⚠️ 未发现调用场景{Colors.RESET}")
    return False

def validate_tool(tool_name: str) -> dict:
    """验证工具集成状态"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}验证工具：{tool_name}{Colors.RESET}")
    print("=" * 70)
    
    results = {
        "tool_name": tool_name,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "registration": check_registration(tool_name),
            "tool_executor": check_tool_executor(tool_name),
            "call_scenarios": check_call_scenarios(tool_name)
        }
    }
    
    # 总结
    print(f"\n{Colors.BOLD}验证结果:{Colors.RESET}")
    passed = sum(1 for v in results["checks"].values() if v)
    total = len(results["checks"])
    
    if passed == total:
        print(f"{Colors.GREEN}✅ 全部通过 ({passed}/{total}){Colors.RESET}")
        results["passed"] = True
    else:
        print(f"{Colors.YELLOW}⚠️ 部分通过 ({passed}/{total}){Colors.RESET}")
        results["passed"] = False
    
    print("=" * 70)
    
    return results

def validate_all_new_tools():
    """验证所有新创建的工具"""
    # 检查今天创建的工具
    today = datetime.now().strftime("%Y-%m-%d")
    
    new_tools = [
        "long_term_memory.py",
        "task_decomposer.py",
        "proactive_agent.py",
        "multimodal_agent.py",
        "workflow_anomaly_detector.py",
        "workflow_recovery.py",
        "workflow_cache.py"
    ]
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}批量验证新工具{Colors.RESET}")
    print("=" * 70)
    
    all_results = []
    for tool in new_tools:
        result = validate_tool(tool)
        all_results.append(result)
    
    # 总结
    print(f"\n{Colors.BOLD}{Colors.CYAN}总体验证结果{Colors.RESET}")
    print("=" * 70)
    
    passed = sum(1 for r in all_results if r["passed"])
    total = len(all_results)
    
    print(f"通过：{passed}/{total}")
    
    for r in all_results:
        status = "✅" if r["passed"] else "⚠️"
        print(f"  {status} {r['tool_name']}")
    
    print("=" * 70)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "results": all_results
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Integration Validator - 工具集成验证')
    parser.add_argument('--tool', type=str, help='验证指定工具')
    parser.add_argument('--all', action='store_true', help='验证所有新工具')
    
    args = parser.parse_args()
    
    if args.tool:
        result = validate_tool(args.tool)
        sys.exit(0 if result["passed"] else 1)
    elif args.all:
        result = validate_all_new_tools()
        sys.exit(0 if result["passed"] == result["total"] else 1)
    else:
        # 默认验证所有
        result = validate_all_new_tools()
        sys.exit(0 if result["passed"] == result["total"] else 1)

if __name__ == '__main__':
    main()
