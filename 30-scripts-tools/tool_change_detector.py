#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Change Detector - 工具变更检测器

核心功能：
1. 检测 tools_registry.json 的变更
2. 记录变更历史到 change_log.json
3. 标记引用变更工具的工作流
4. 触发合规性重审

Usage:
    # 检测变更
    py tool_change_detector.py --detect
    
    # 查看变更历史
    py tool_change_detector.py --history
    
    # 检查受影响的工作流
    py tool_change_detector.py --check-workflows --tool auto-critic
    
    # 触发合规重审
    py tool_change_detector.py --trigger-review --tool auto-critic

Author: Claw
Date: 2026-03-18
Version: 1.0
"""

import json
import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 文件路径
TOOLS_REGISTRY = Path("30-scripts-tools/tools_registry.json")
CHANGE_LOG = Path("30-scripts-tools/change_log.json")
WORKFLOWS_DIR = Path("30-scripts-tools/workflows")

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


class ToolChangeDetector:
    """工具变更检测器"""
    
    def __init__(self):
        self.registry = self._load_registry()
        self.change_log = self._load_change_log()
    
    def _load_registry(self) -> Dict:
        """加载工具库"""
        if not TOOLS_REGISTRY.exists():
            raise FileNotFoundError(f"Tools registry not found: {TOOLS_REGISTRY}")
        
        with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_change_log(self) -> Dict:
        """加载变更日志"""
        if not CHANGE_LOG.exists():
            return {
                "version": "1.0",
                "changes": [],
                "last_check": None
            }
        
        with open(CHANGE_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_change_log(self):
        """保存变更日志"""
        with open(CHANGE_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.change_log, f, indent=2, ensure_ascii=False)
    
    def _calculate_hash(self, obj: Any) -> str:
        """计算对象的 SHA256 哈希"""
        obj_str = json.dumps(obj, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(obj_str.encode('utf-8')).hexdigest()
    
    def detect_changes(self) -> List[Dict]:
        """
        检测工具变更
        
        Returns:
            变更列表
        """
        print_header("Tool Change Detection")
        
        changes = []
        tools = self.registry.get("tools", {})
        last_changes = self.change_log.get("changes", [])
        
        # 获取上次变更的工具哈希
        last_hashes = {}
        if last_changes:
            last_change = last_changes[-1]
            last_hashes = last_change.get("tool_hashes", {})
        
        # 计算当前工具哈希
        current_hashes = {}
        for tool_id, tool_def in tools.items():
            current_hashes[tool_id] = self._calculate_hash(tool_def)
        
        # 检测变更
        for tool_id, current_hash in current_hashes.items():
            if tool_id not in last_hashes:
                # 新工具
                change = {
                    "type": "NEW",
                    "tool_id": tool_id,
                    "timestamp": datetime.now().isoformat(),
                    "description": f"New tool registered: {tool_id}"
                }
                changes.append(change)
                print_success(f"NEW: {tool_id}")
            elif last_hashes[tool_id] != current_hash:
                # 工具修改
                change = {
                    "type": "MODIFIED",
                    "tool_id": tool_id,
                    "timestamp": datetime.now().isoformat(),
                    "description": f"Tool modified: {tool_id}",
                    "old_hash": last_hashes[tool_id],
                    "new_hash": current_hash
                }
                changes.append(change)
                print_warning(f"MODIFIED: {tool_id}")
        
        # 检测删除的工具
        for tool_id in last_hashes:
            if tool_id not in current_hashes:
                change = {
                    "type": "DELETED",
                    "tool_id": tool_id,
                    "timestamp": datetime.now().isoformat(),
                    "description": f"Tool deleted: {tool_id}"
                }
                changes.append(change)
                print_error(f"DELETED: {tool_id}")
        
        # 记录变更
        if changes:
            change_record = {
                "id": len(self.change_log["changes"]) + 1,
                "timestamp": datetime.now().isoformat(),
                "changes": changes,
                "tool_hashes": current_hashes,
                "registry_version": self.registry.get("version", "unknown")
            }
            self.change_log["changes"].append(change_record)
            self.change_log["last_check"] = datetime.now().isoformat()
            self._save_change_log()
            
            print_header("Change Summary")
            print_info(f"Total changes: {len(changes)}")
            print_info(f"New: {sum(1 for c in changes if c['type'] == 'NEW')}")
            print_info(f"Modified: {sum(1 for c in changes if c['type'] == 'MODIFIED')}")
            print_info(f"Deleted: {sum(1 for c in changes if c['type'] == 'DELETED')}")
        else:
            print_success("No changes detected")
        
        return changes
    
    def find_affected_workflows(self, tool_id: str) -> List[Dict]:
        """
        查找引用指定工具的工作流
        
        Args:
            tool_id: 工具 ID
        
        Returns:
            受影响的工作流列表
        """
        print_info(f"Finding workflows that use tool: {tool_id}")
        
        affected = []
        
        if not WORKFLOWS_DIR.exists():
            print_warning(f"Workflows directory not found: {WORKFLOWS_DIR}")
            return affected
        
        for workflow_file in WORKFLOWS_DIR.glob("*.json"):
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            # 检查工作流步骤是否引用该工具
            steps_using_tool = []
            for step in workflow.get("steps", []):
                if step.get("tool_id") == tool_id:
                    steps_using_tool.append(step.get("step_id"))
            
            if steps_using_tool:
                affected.append({
                    "workflow_id": workflow.get("workflow_id"),
                    "workflow_file": str(workflow_file),
                    "steps_using_tool": steps_using_tool,
                    "workflow_name": workflow.get("name", "")
                })
        
        if affected:
            print_success(f"Found {len(affected)} affected workflow(s):")
            for wf in affected:
                print(f"  - {wf['workflow_id']} (steps: {wf['steps_using_tool']})")
        else:
            print_info(f"No workflows use tool: {tool_id}")
        
        return affected
    
    def trigger_compliance_review(self, tool_id: str) -> Dict:
        """
        触发合规性重审
        
        Args:
            tool_id: 工具 ID
        
        Returns:
            审查结果
        """
        print_header(f"Triggering Compliance Review for: {tool_id}")
        
        # 1. 查找受影响的工作流
        affected_workflows = self.find_affected_workflows(tool_id)
        
        # 2. 运行 auto-critic 审查
        print_info("Running auto-critic compliance review...")
        cmd = f'py 30-scripts-tools\\auto-critic.py -t "tool-change-{tool_id}" -p final'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        
        # 3. 解析审查结果
        review_result = {
            "tool_id": tool_id,
            "timestamp": datetime.now().isoformat(),
            "affected_workflows": affected_workflows,
            "auto_critic_result": {
                "returncode": result.returncode,
                "output": result.stdout[:1000] if result.stdout else "",
                "review_file": f"30-scripts-tools/critic-auto-tool-change-{tool_id}.json"
            }
        }
        
        # 4. 记录审查结果
        if "auto_critic_reviews" not in self.change_log:
            self.change_log["auto_critic_reviews"] = []
        self.change_log["auto_critic_reviews"].append(review_result)
        self._save_change_log()
        
        # 5. 显示结果
        if result.returncode == 0:
            print_success("Compliance review PASSED")
        else:
            print_warning("Compliance review NEEDS ATTENTION")
        
        return review_result
    
    def show_history(self, limit: int = 10) -> List[Dict]:
        """
        显示变更历史
        
        Args:
            limit: 显示最近 N 条
        
        Returns:
            变更历史记录
        """
        print_header("Tool Change History")
        
        changes = self.change_log.get("changes", [])
        recent = changes[-limit:] if len(changes) > limit else changes
        
        if not recent:
            print_info("No change history")
            return []
        
        for record in recent:
            print(f"\n{Colors.BOLD}Change #{record['id']} - {record['timestamp']}{Colors.RESET}")
            print_info(f"Registry version: {record.get('registry_version', 'unknown')}")
            
            for change in record.get("changes", []):
                if change["type"] == "NEW":
                    print_success(f"  + {change['tool_id']} - {change['description']}")
                elif change["type"] == "MODIFIED":
                    print_warning(f"  ~ {change['tool_id']} - {change['description']}")
                elif change["type"] == "DELETED":
                    print_error(f"  - {change['tool_id']} - {change['description']}")
        
        return recent
    
    def validate_all_workflows(self) -> Dict:
        """
        验证所有工作流合规性
        
        Returns:
            验证结果
        """
        print_header("Validating All Workflows")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "workflows": [],
            "total": 0,
            "passed": 0,
            "failed": 0
        }
        
        if not WORKFLOWS_DIR.exists():
            print_warning(f"Workflows directory not found: {WORKFLOWS_DIR}")
            return results
        
        for workflow_file in WORKFLOWS_DIR.glob("*.json"):
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            workflow_id = workflow.get("workflow_id", "unknown")
            print_info(f"Validating workflow: {workflow_id}")
            
            # 检查是否所有 tool_id 都在工具库中注册
            steps = workflow.get("steps", [])
            invalid_tools = []
            
            for step in steps:
                tool_id = step.get("tool_id")
                if tool_id and tool_id not in self.registry.get("tools", {}):
                    invalid_tools.append({
                        "step_id": step.get("step_id"),
                        "tool_id": tool_id
                    })
            
            # 检查是否有硬编码命令
            workflow_str = json.dumps(workflow)
            has_hardcoded = "py 30-scripts" in workflow_str
            
            # 验证结果
            passed = len(invalid_tools) == 0 and not has_hardcoded
            
            workflow_result = {
                "workflow_id": workflow_id,
                "workflow_file": str(workflow_file),
                "passed": passed,
                "issues": {
                    "invalid_tools": invalid_tools,
                    "has_hardcoded_commands": has_hardcoded
                }
            }
            
            results["workflows"].append(workflow_result)
            results["total"] += 1
            
            if passed:
                results["passed"] += 1
                print_success(f"  {workflow_id} - PASSED")
            else:
                results["failed"] += 1
                print_error(f"  {workflow_id} - FAILED")
                if invalid_tools:
                    for issue in invalid_tools:
                        print(f"    - Invalid tool_id: {issue['tool_id']} (step {issue['step_id']})")
                if has_hardcoded:
                    print(f"    - Has hardcoded commands")
        
        # 保存验证结果
        if "workflow_validations" not in self.change_log:
            self.change_log["workflow_validations"] = []
        self.change_log["workflow_validations"].append(results)
        self._save_change_log()
        
        # 显示摘要
        print_header("Validation Summary")
        print_info(f"Total workflows: {results['total']}")
        print_success(f"Passed: {results['passed']}")
        if results["failed"] > 0:
            print_error(f"Failed: {results['failed']}")
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool Change Detector")
    parser.add_argument("--detect", action="store_true", help="Detect tool changes")
    parser.add_argument("--history", action="store_true", help="Show change history")
    parser.add_argument("--check-workflows", type=str, help="Find workflows using specified tool")
    parser.add_argument("--trigger-review", type=str, help="Trigger compliance review for specified tool")
    parser.add_argument("--validate-all", action="store_true", help="Validate all workflows")
    parser.add_argument("--limit", type=int, default=10, help="Limit history display (default: 10)")
    
    args = parser.parse_args()
    
    try:
        detector = ToolChangeDetector()
        
        if args.detect:
            changes = detector.detect_changes()
            sys.exit(0 if not changes else 1)
        
        if args.history:
            detector.show_history(args.limit)
            sys.exit(0)
        
        if args.check_workflows:
            affected = detector.find_affected_workflows(args.check_workflows)
            sys.exit(0 if not affected else 1)
        
        if args.trigger_review:
            result = detector.trigger_compliance_review(args.trigger_review)
            sys.exit(0 if result["auto_critic_result"]["returncode"] == 0 else 1)
        
        if args.validate_all:
            result = detector.validate_all_workflows()
            sys.exit(0 if result["failed"] == 0 else 1)
        
        parser.print_help()
        sys.exit(1)
        
    except FileNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
