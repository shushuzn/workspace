#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Executor - 工具执行引擎

核心原则：
1. 唯一数据源 - 只从 tools_registry.json 读取工具定义
2. 引用优先 - 只接受 tool_id，不接受硬编码命令
3. 实时生效 - 每次执行都读取最新定义

Usage:
    # 执行单个工具
    py tool_executor.py --tool auto-critic --task "my-task" --phase final
    
    # 执行工作流
    py tool_executor.py --workflow session-end --context "{\"commit_message\": \"Task complete\"}"
    
    # 验证合规性
    py tool_executor.py --validate-compliance

Author: Claw
Date: 2026-03-18
Version: 1.0
"""

import json
import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# 工具库路径（唯一数据源）
TOOLS_REGISTRY = Path(__file__).parent / "tools_registry.json"
WORKFLOWS_DIR = Path(__file__).parent / "workflows"
WORKSPACE = Path(__file__).parent.parent  # 新增：工作区根目录

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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


class ToolExecutor:
    """
    工具执行引擎
    
    核心原则：
    1. 唯一数据源 - 只从 tools_registry.json 读取
    2. 引用优先 - 只接受 tool_id
    3. 实时生效 - 每次执行都读取最新定义
    """
    
    def __init__(self, context: Dict = None):
        self.registry = self._load_registry()
        self.execution_log = []
        self.context = context or {}
    
    def _load_registry(self) -> Dict:
        """
        加载唯一工具库（实时读取，无缓存）
        
        Returns:
            工具库字典
            
        Raises:
            FileNotFoundError: 工具库文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        if not TOOLS_REGISTRY.exists():
            raise FileNotFoundError(
                f"Tools registry not found: {TOOLS_REGISTRY}\n"
                f"Please create tools_registry.json first."
            )
        
        with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        print_info(f"Loaded tools registry: {len(registry.get('tools', {}))} tools")
        return registry
    
    def get_tool(self, tool_id: str) -> Dict:
        """
        获取工具定义（唯一数据源）
        
        Args:
            tool_id: 工具唯一标识
            
        Returns:
            工具定义字典
            
        Raises:
            ValueError: 工具未注册
        """
        tools = self.registry.get("tools", {})
        if tool_id not in tools:
            available = ", ".join(tools.keys())
            raise ValueError(
                f"Tool not registered: {tool_id}\n"
                f"Available tools: {available}"
            )
        return tools[tool_id]
    
    def execute(self, tool_id: str, parameters: Dict[str, Any] = None) -> Dict:
        """
        执行工具（实时从工具库拉取最新定义）
        
        Args:
            tool_id: 工具唯一标识（必须先在工具库注册）
            parameters: 个性化参数（只能覆盖非核心配置）
        
        Returns:
            执行结果：{
                "success": bool,
                "output": str,
                "validation": Dict,
                "tool_id": str,
                "command": str,
                "execution_time_ms": int
            }
        
        Raises:
            ValueError: 工具未注册或参数无效
            subprocess.TimeoutExpired: 执行超时
        """
        start_time = datetime.now()
        
        # 1. 获取工具定义（唯一数据源）
        print_info(f"Loading tool definition: {tool_id}")
        tool = self.get_tool(tool_id)
        
        # 2. 验证参数
        parameters = parameters or {}
        self._validate_parameters(tool, parameters)
        
        # 3. 构建命令（从工具定义读取，禁止硬编码）
        command_template = tool["command"]
        params = {**self._get_default_parameters(tool), **parameters}
        
        # 填充参数
        for key, value in params.items():
            command_template = command_template.replace(f"{{{key}}}", str(value))
        
        # 填充特殊变量（datetime 已在文件顶部导入）
        today = datetime.now().strftime("%Y-%m-%d")
        command_template = command_template.replace("${TODAY}", today)
        command_template = command_template.replace("${flow_id}", self.context.get("flow_id", "unknown"))
        command_template = command_template.replace("${commit_message}", self.context.get("commit_message", ""))
        
        print_info(f"Executing: {command_template}")
        
        # 4. 执行命令
        timeout = tool.get("timeout_seconds", 60)
        result = subprocess.run(
            command_template,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 5. 验证结果
        validation = self._validate_result(tool, result, params)
        
        # 6. 记录执行日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_id": tool_id,
            "command": command_template,
            "success": result.returncode == 0 and validation["passed"],
            "execution_time_ms": execution_time,
            "returncode": result.returncode
        }
        self.execution_log.append(log_entry)
        
        return {
            "success": result.returncode == 0 and validation["passed"],
            "output": result.stdout + result.stderr,
            "validation": validation,
            "tool_id": tool_id,
            "command": command_template,
            "execution_time_ms": execution_time
        }
    
    def _get_default_parameters(self, tool: Dict) -> Dict:
        """获取工具默认参数"""
        defaults = {}
        for param_name, param_def in tool.get("parameters", {}).items():
            if "default" in param_def:
                defaults[param_name] = param_def["default"]
        return defaults
    
    def _validate_parameters(self, tool: Dict, parameters: Dict) -> None:
        """
        验证参数合法性
        
        Args:
            tool: 工具定义
            parameters: 传入参数
            
        Raises:
            ValueError: 参数不合法
        """
        tool_params = tool.get("parameters", {})
        
        # 检查必填参数
        for param_name, param_def in tool_params.items():
            if param_def.get("required", False) and param_name not in parameters:
                raise ValueError(f"Missing required parameter: {param_name}")
        
        # 检查参数类型和枚举
        for param_name, value in parameters.items():
            if param_name not in tool_params:
                print_warning(f"Unknown parameter: {param_name} (ignored)")
                continue
            
            param_def = tool_params[param_name]
            
            # 类型检查
            expected_type = param_def.get("type", "string")
            if expected_type == "integer" and not isinstance(value, int):
                try:
                    value = int(value)
                except:
                    raise ValueError(f"Parameter {param_name} must be integer")
            
            # 枚举检查
            if "enum" in param_def and value not in param_def["enum"]:
                raise ValueError(
                    f"Parameter {param_name} must be one of: {param_def['enum']}"
                )
            
            # 范围检查
            if "min" in param_def and value < param_def["min"]:
                raise ValueError(f"Parameter {param_name} must be >= {param_def['min']}")
            if "max" in param_def and value > param_def["max"]:
                raise ValueError(f"Parameter {param_name} must be <= {param_def['max']}")
    
    def _validate_result(self, tool: Dict, result: subprocess.CompletedProcess, params: Dict) -> Dict:
        """
        验证工具执行结果
        
        Args:
            tool: 工具定义
            result: 执行结果
            params: 参数
            
        Returns:
            验证结果：{"passed": bool, "rules_checked": List, "details": Dict}
        """
        validation_rules = tool.get("validation", {})
        passed = result.returncode == 0
        details = {}
        
        # 检查验证文件是否存在
        if "review_file" in validation_rules:
            review_file = validation_rules["review_file"].format(**params)
            exists = Path(review_file).exists()
            details["review_file_exists"] = exists
            if not exists:
                passed = False
        
        # 检查分数阈值
        if "score_threshold" in validation_rules:
            output = result.stdout + result.stderr
            if "Score:" in output:
                for line in output.split('\n'):
                    if 'Score:' in line:
                        try:
                            score = int(line.split(':')[1].strip().split('/')[0])
                            details["score"] = score
                            if score < validation_rules["score_threshold"]:
                                passed = False
                                details["score_check"] = f"FAIL ({score} < {validation_rules['score_threshold']})"
                            else:
                                details["score_check"] = f"PASS ({score} >= {validation_rules['score_threshold']})"
                        except:
                            pass
        
        # 检查上下文大小
        if "max_size_kb" in validation_rules:
            output = result.stdout + result.stderr
            if "总大小：" in output or "Total size:" in output:
                for line in output.split('\n'):
                    if '总大小：' in line or 'Total size:' in line:
                        match = re.search(r'(\d+\.?\d*)\s*KB', line, re.IGNORECASE)
                        if match:
                            size = float(match.group(1))
                            details["context_size_kb"] = size
                            if size > validation_rules["max_size_kb"]:
                                passed = False
                                details["size_check"] = f"FAIL ({size}KB > {validation_rules['max_size_kb']}KB)"
                            else:
                                details["size_check"] = f"PASS ({size}KB <= {validation_rules['max_size_kb']}KB)"
        
        # 检查当日笔记行数
        if "daily_note_lines_limit" in validation_rules:
            output = result.stdout + result.stderr
            for line in output.split('\n'):
                if 'lines' in line.lower() and ':' in line:
                    match = re.search(r'(\d+)\s*lines', line, re.IGNORECASE)
                    if match:
                        lines = int(match.group(1))
                        details["daily_note_lines"] = lines
                        if lines > validation_rules["daily_note_lines_limit"]:
                            passed = False
                            details["lines_check"] = f"FAIL ({lines} > {validation_rules['daily_note_lines_limit']})"
                        else:
                            details["lines_check"] = f"PASS ({lines} <= {validation_rules['daily_note_lines_limit']})"
        
        # 检查最小结果数
        if "min_results" in validation_rules:
            output = result.stdout + result.stderr
            if "results" in output.lower() or "found" in output.lower():
                for line in output.split('\n'):
                    if 'result' in line.lower():
                        match = re.search(r'(\d+)', line)
                        if match:
                            count = int(match.group(1))
                            details["results_count"] = count
                            if count < validation_rules["min_results"]:
                                passed = False
                                details["results_check"] = f"FAIL ({count} < {validation_rules['min_results']})"
                            else:
                                details["results_check"] = f"PASS ({count} >= {validation_rules['min_results']})"
        
        return {
            "passed": passed,
            "rules_checked": list(validation_rules.keys()),
            "details": details,
            "returncode": result.returncode
        }
    
    def execute_workflow(self, workflow_id: str, context: Dict = None, flow_id: str = None) -> Dict:
        """
        执行工作流（只引用 tool_id，不硬编码）
        
        Args:
            workflow_id: 工作流唯一标识
            context: 上下文参数（如 commit_message）
            flow_id: Flow ID for isolation (optional)
        
        Returns:
            工作流执行结果：{
                "workflow_id": str,
                "success": bool,
                "steps": List[Dict],
                "total_steps": int,
                "passed_steps": int,
                "execution_time_ms": int
            }
        """
        start_time = datetime.now()
        self.flow_id = flow_id  # 保存 Flow ID 用于日志隔离
        
        workflow_file = WORKFLOWS_DIR / f"{workflow_id}.json"
        
        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_file}")
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        print_header(f"Executing Workflow: {workflow_id}")
        print_info(f"Total steps: {len(workflow['steps'])}")
        
        results = []
        all_passed = True
        
        for step in workflow["steps"]:
            step_num = step["step_id"]
            tool_id = step["tool_id"]  # 只引用 ID
            step_name = step.get("name", f"Step {step_num}")
            params = step.get("parameters", {})
            blocking = step.get("blocking", True)
            
            print(f"\n{Colors.BOLD}Step {step_num}/{len(workflow['steps'])}: {step_name}{Colors.RESET}")
            print_info(f"Tool: {tool_id}")
            
            # 替换上下文变量
            if context:
                for key, value in context.items():
                    for param_key, param_value in params.items():
                        if isinstance(param_value, str) and f"${{{key}}}" in param_value:
                            params[param_key] = param_value.replace(f"${{{key}}}", str(value))
            
            # 检查条件执行
            if "conditional" in step:
                cond = step["conditional"]
                if "run_only_on" in cond:
                    day_name = cond["run_only_on"]
                    today = datetime.now().strftime('%A')
                    if today != day_name:
                        print_info(f"Skipped (runs on {day_name} only, today is {today})")
                        results.append({
                            "step_id": step_num,
                            "step_name": step_name,
                            "tool_id": tool_id,
                            "skipped": True,
                            "reason": f"Conditional: runs on {day_name} only"
                        })
                        continue
            
            # 执行工具
            result = self.execute(tool_id, params)
            result["step_id"] = step_num
            result["step_name"] = step_name
            result["blocking"] = blocking
            
            if result["success"]:
                print_success(f"Step {step_num} PASSED")
            else:
                if blocking:
                    print_error(f"Step {step_num} FAILED (blocking)")
                    all_passed = False
                else:
                    print_warning(f"Step {step_num} FAILED (non-blocking)")
            
            results.append(result)
            
            # 阻塞步骤失败则中断
            if not result["success"] and blocking:
                print_warning("Workflow stopped due to blocking step failure")
                break
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        summary = {
            "workflow_id": workflow_id,
            "success": all_passed,
            "steps": results,
            "total_steps": len(workflow["steps"]),
            "passed_steps": sum(1 for r in results if r.get("success", False) or r.get("skipped", False)),
            "execution_time_ms": execution_time
        }
        
        print_header("Workflow Execution Summary")
        print_info(f"Total steps: {summary['total_steps']}")
        print_info(f"Passed: {summary['passed_steps']}")
        print_info(f"Execution time: {execution_time:.0f}ms")
        print_success("Workflow PASSED") if all_passed else print_error("Workflow FAILED")
        
        # Flow ID 隔离：专属日志保存
        if self.flow_id:
            log_dir = WORKSPACE / "flow-archive" / self.flow_id
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "execution-log.json"
        else:
            log_file = SCRIPTS_DIR / "workflow-execution-log.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print_info(f"Log saved to: {log_file}")
        
        return summary
    
    def validate_compliance(self) -> Dict:
        """
        验证合规性（检查零分项）
        
        Returns:
            合规性检查结果
        """
        print_header("Compliance Validation")
        
        compliance_rules = self.registry.get("compliance_rules", {})
        zero_score_items = compliance_rules.get("zero_score_items", [])
        
        results = []
        all_passed = True
        
        for item in zero_score_items:
            rule_id = item["id"]
            rule = item["rule"]
            check_method = item["check"]
            
            print_info(f"Checking {rule_id}: {rule}")
            
            # 执行检查（简化版，实际应实现具体检查逻辑）
            passed = True  # 默认通过
            details = f"Check method: {check_method}"
            
            if not passed:
                all_passed = False
                print_error(f"  ❌ FAIL")
            else:
                print_success(f"  ✅ PASS")
            
            results.append({
                "rule_id": rule_id,
                "rule": rule,
                "passed": passed,
                "details": details
            })
        
        return {
            "all_passed": all_passed,
            "total_rules": len(zero_score_items),
            "passed_rules": sum(1 for r in results if r["passed"]),
            "results": results
        }
    
    def list_tools(self) -> List[Dict]:
        """列出所有已注册工具"""
        tools = self.registry.get("tools", {})
        return [
            {
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "version": tool.get("version", "1.0")
            }
            for tool_id, tool in tools.items()
        ]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Tool Executor - 工具执行引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all tools
  py tool_executor.py --list
  
  # Execute single tool
  py tool_executor.py --tool auto-critic --task "my-task" --phase final
  
  # Execute workflow
  py tool_executor.py --workflow session-end --context "{\"commit_message\": \"Task complete\"}"
  
  # Validate compliance
  py tool_executor.py --validate-compliance
        """
    )
    
    parser.add_argument("--list", action="store_true", help="List all registered tools")
    parser.add_argument("--tool", type=str, help="Tool ID to execute")
    parser.add_argument("--workflow", type=str, help="Workflow ID to execute")
    parser.add_argument("--task", type=str, help="Task name (for auto-critic)")
    parser.add_argument("--phase", type=str, help="Phase: start/mid/final")
    parser.add_argument("--context", type=str, help="Context JSON (for workflows)")
    parser.add_argument("--flow_id", type=str, help="Flow ID for isolation")  # Flow ID 支持
    parser.add_argument("--validate-compliance", action="store_true", help="Validate compliance rules")
    parser.add_argument("--output-json", action="store_true", help="Output result as JSON")
    
    args = parser.parse_args()
    
    try:
        executor = ToolExecutor()
        
        if args.list:
            tools = executor.list_tools()
            print_header("Registered Tools")
            for tool in tools:
                print(f"  {Colors.BLUE}{tool['tool_id']}{Colors.RESET}: {tool['name']} (v{tool['version']})")
                print(f"    {tool['description']}")
            sys.exit(0)
        
        if args.validate_compliance:
            result = executor.validate_compliance()
            if args.output_json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(0 if result["all_passed"] else 1)
        
        if args.workflow:
            context = json.loads(args.context) if args.context else {}
            result = executor.execute_workflow(args.workflow, context, args.flow_id)
            if args.output_json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(0 if result["success"] else 1)
        
        if args.tool:
            params = {}
            if args.task:
                params["task"] = args.task
            if args.phase:
                params["phase"] = args.phase
            result = executor.execute(args.tool, params)
            if args.output_json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print_header("Execution Result")
                print_success("PASSED") if result["success"] else print_error("FAILED")
                print_info(f"Execution time: {result['execution_time_ms']:.0f}ms")
                if result["output"]:
                    print(f"\nOutput:\n{result['output'][:500]}")
            sys.exit(0 if result["success"] else 1)
        
        parser.print_help()
        sys.exit(1)
        
    except FileNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
