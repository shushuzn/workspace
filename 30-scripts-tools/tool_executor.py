#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Executor with Auto-Step Completion
工具执行器 - 带自动步骤追踪 (方案 A)
"""

import json
import subprocess
import sys
import io
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 导入缓存系统
try:
    from workflow_cache import cache_get, cache_set, init_cache
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False

class WorkflowViolationError(Exception):
    """工作流违规异常"""
    pass

class ToolExecutor:
    def __init__(self, flow_id="20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.checkpoint_file = FLOW_ARCHIVE / flow_id / "checkpoint.json"
        self.current_step = self._load_current_step()
    
    def _load_current_step(self):
        """加载当前步骤"""
        if not self.checkpoint_file.exists():
            return 1
        
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        completed = state.get('completed_steps', [])
        return len(completed) + 1
    
    def _load_workflow_config(self):
        """加载工作流配置"""
        workflow_file = FLOW_ARCHIVE / self.flow_id / "workflow.json"
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_step_tool_mapping(self):
        """获取步骤 - 工具映射"""
        workflow = self._load_workflow_config()
        mapping = {}
        
        for step in workflow.get('steps', []):
            step_id = step['step_id']
            tool_id = step.get('tool_id')
            if tool_id:
                mapping[tool_id] = step_id
        
        return mapping
    
    def execute_tool(self, tool_id, params=None, auto_complete=True, enforce_workflow=True):
        """执行工具并自动完成步骤
        
        方案 A: 自动步骤追踪 - auto_complete=True 时自动标记步骤完成
        方案 C: 工具层强制检查 - enforce_workflow=True 时强制检查工作流状态
        
        Args:
            tool_id: 工具 ID
            params: 工具参数 (用于缓存键生成)
            auto_complete: 是否自动完成步骤 (默认 True)
            enforce_workflow: 是否强制执行工作流检查 (默认 True)
        """
        # 初始化缓存
        if CACHE_ENABLED:
            init_cache()
        
        # 1. 验证工作流状态 (方案 C: 工具层强制检查)
        if enforce_workflow and not self._verify_workflow_active():
            raise WorkflowViolationError(
                "工作流未启动！请先执行：py workflow_enforcer.py --start"
            )
        
        # 2. 检查工具 - 步骤映射 (方案 C: 工具层强制检查)
        if enforce_workflow:
            tool_mapping = self._get_step_tool_mapping()
            expected_step = tool_mapping.get(tool_id)
            
            if expected_step and expected_step != self.current_step:
                raise WorkflowViolationError(
                    f"工具 {tool_id} 不允许在步骤 {self.current_step} 执行\n"
                    f"该工具应该在步骤 {expected_step} 执行\n"
                    f"请先完成步骤 {self.current_step} 到 {expected_step - 1}"
                )
        
        # 3. 检查缓存 (新增功能)
        if CACHE_ENABLED and params:
            cached_result, cache_status = cache_get(tool_id, params)
            if cached_result is not None:
                print(f"\n[Tool Executor] 🗜️ 缓存命中：{tool_id}")
                print(f"     状态：{cache_status}")
                return {
                    "success": True,
                    "cached": True,
                    "result": cached_result,
                    "cache_status": cache_status
                }
        
        # 4. 执行工具
        print(f"\n[Tool Executor] 执行工具：{tool_id}")
        print(f"     当前步骤：{self.current_step}")
        print(f"     自动完成：{auto_complete}")
        print(f"     强制检查：{enforce_workflow}")
        
        result = self._run_tool_command(tool_id)
        
        # 5. 设置缓存 (新增功能)
        if CACHE_ENABLED and result['success'] and params:
            cache_set(tool_id, params, result)
            print(f"     🗜️ 结果已缓存")
        
        # 6. 自动完成步骤 (方案 A: 自动步骤追踪)
        if auto_complete and result['success']:
            self._complete_current_step(tool_id, result)
        
        return result
    
    def _verify_workflow_active(self):
        """验证工作流是否激活"""
        if not self.checkpoint_file.exists():
            return False
        
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return state.get('status') in ['in_progress', 'started']
    
    def _run_tool_command(self, tool_id):
        """执行工具命令"""
        registry_file = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
        
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        tool_config = registry.get('tools', {}).get(tool_id)
        
        if not tool_config:
            return {
                'success': False,
                'error': f"工具未找到：{tool_id}",
                'execution_time_ms': 0
            }
        
        command = tool_config.get('command')
        if not command:
            return {
                'success': False,
                'error': f"工具无命令配置：{tool_id}",
                'execution_time_ms': 0
            }
        
        start_time = datetime.now()
        
        try:
            # 修复中文乱码：使用 chcp 65001 设置 UTF-8 编码
            if sys.platform == 'win32':
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=tool_config.get('timeout_seconds', 60),
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=tool_config.get('timeout_seconds', 60)
                )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            # 打印输出（修复乱码）
            if result.stdout:
                try:
                    print(result.stdout)
                except UnicodeEncodeError:
                    print(result.stdout.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
            if result.stderr:
                try:
                    print(result.stderr, file=sys.stderr)
                except UnicodeEncodeError:
                    print(result.stderr.encode('utf-8', errors='replace').decode('utf-8', errors='replace'), file=sys.stderr)
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time_ms': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"工具执行超时 (>{tool_config.get('timeout_seconds', 60)}s)",
                'execution_time_ms': tool_config.get('timeout_seconds', 60) * 1000
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': 0
            }
    
    def _complete_current_step(self, tool_id, result):
        """自动完成当前步骤"""
        enforcer_script = WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"
        
        command = [
            sys.executable,
            str(enforcer_script),
            "--complete-step",
            str(self.current_step)
        ]
        
        subprocess.run(command, capture_output=True)
        
        self._log_execution(tool_id, result)
        
        self.current_step += 1
        
        print(f"\n[OK] 步骤 {self.current_step - 1} 自动完成")
        print(f"     工具：{tool_id}")
        print(f"     结果：{'成功' if result['success'] else '失败'}")
        print(f"     下一步：{self.current_step}")
    
    def _log_execution(self, tool_id, result):
        """记录执行日志"""
        log_file = FLOW_ARCHIVE / self.flow_id / "execution-log.json"
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)
        else:
            log = {
                'workflow_id': self.flow_id,
                'executions': []
            }
        
        log['executions'].append({
            'step': self.current_step,
            'tool_id': tool_id,
            'timestamp': datetime.now().isoformat(),
            'success': result['success'],
            'execution_time_ms': result.get('execution_time_ms', 0)
        })
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='工具执行器 (方案 A+C: 自动步骤追踪 + 工具层强制)')
    parser.add_argument('tool_id', help='工具 ID')
    parser.add_argument('--flow-id', default='20260318-universal-workflow-001',
                       help='工作流 ID')
    parser.add_argument('--no-auto-complete', action='store_true',
                       help='禁用自动完成步骤')
    parser.add_argument('--no-enforce', action='store_true',
                       help='禁用工作流强制检查 (不推荐)')
    
    args = parser.parse_args()
    
    executor = ToolExecutor(flow_id=args.flow_id)
    
    try:
        result = executor.execute_tool(
            args.tool_id,
            auto_complete=not args.no_auto_complete,
            enforce_workflow=not args.no_enforce
        )
        
        if result['success']:
            print(f"\n[OK] 工具执行成功")
            sys.exit(0)
        else:
            print(f"\n[ERROR] 工具执行失败：{result.get('error', '未知错误')}")
            sys.exit(1)
            
    except WorkflowViolationError as e:
        print(f"\n[BLOCKER] {e}")
        sys.exit(1)
