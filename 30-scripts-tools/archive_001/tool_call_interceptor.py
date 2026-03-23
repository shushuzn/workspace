#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenClaw Cursor Mode - 工具调用拦截器
自动优化工具调用，实现 Cursor 级别的智能体验
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

WORKSPACE = Path(r"D:\OpenClaw\workspace")


class ToolCallInterceptor:
    """工具调用拦截器 - 优化和自动执行"""

    def __init__(self):
        self.workspace = WORKSPACE
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = Path.home() / ".copaw" / "config-cursor.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def intercept_execute_shell_command(self, params: Dict) -> Dict:
        """拦截并优化 shell 命令执行"""
        command = params.get('command', '')

        # 自动添加工作目录
        if 'cwd' not in params or params['cwd'] is None:
            params['cwd'] = str(self.workspace)

        # 自动增加超时时间对于长时间运行的命令
        long_running_patterns = ['npm install', 'pip install', 'cargo build', 'webpack', 'tsc']
        for pattern in long_running_patterns:
            if pattern in command.lower():
                params['timeout'] = max(params.get('timeout', 60), 300)
                break

        # 自动捕获 stderr
        params['capture_stderr'] = True

        return params

    def intercept_read_file(self, params: Dict) -> Dict:
        """拦截并优化文件读取"""
        file_path = params.get('file_path', '')

        # 自动读取相关文件
        if self.config.get('agents', {}).get('code_mode', {}).get('auto_read_related', True):
            related_files = self._find_related_files(file_path)
            if related_files:
                params['related_files'] = related_files

        return params

    def _find_related_files(self, file_path: str) -> List[str]:
        """查找相关文件"""
        related = []
        path = self.workspace / file_path

        if not path.exists():
            return related

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找导入语句
            patterns = [
                r'import.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)',
                r'from\s+([^\'"]+)\s+import',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.startswith('.'):
                        rel_path = (path.parent / match).resolve()
                    else:
                        rel_path = self.workspace / match

                    for ext in ['', '.py', '.js', '.ts', '.jsx', '.tsx']:
                        test_path = Path(str(rel_path) + ext)
                        if test_path.exists():
                            try:
                                related.append(str(test_path.relative_to(self.workspace)))
                            except ValueError:
                                pass
                            break

        except Exception:
            pass

        return related[:10]

    def intercept_edit_file(self, params: Dict) -> Dict:
        """拦截并优化文件编辑"""
        # 自动重试配置
        params['auto_retry'] = self.config.get('tools', {}).get('builtin_tools', {}).get('edit_file', {}).get('auto_retry', True)
        params['max_retries'] = self.config.get('tools', {}).get('builtin_tools', {}).get('edit_file', {}).get('max_retries', 3)

        return params

    def optimize_for_cursor_mode(self, tool_name: str, params: Dict) -> Dict:
        """针对 Cursor 模式优化参数"""
        interceptors = {
            'execute_shell_command': self.intercept_execute_shell_command,
            'read_file': self.intercept_read_file,
            'edit_file': self.intercept_edit_file,
        }

        if tool_name in interceptors:
            return interceptors[tool_name](params)

        return params

    def should_auto_execute(self, tool_name: str, params: Dict) -> bool:
        """判断是否应该自动执行"""
        auto_execute_tools = self.config.get('tools', {}).get('auto_execute_tools', [])
        return tool_name in auto_execute_tools

    def get_context_files(self, task_description: str) -> List[str]:
        """根据任务描述获取相关上下文文件"""
        context_files = []

        # 智能识别任务类型
        task_lower = task_description.lower()

        # 代码相关任务
        if any(kw in task_lower for kw in ['代码', 'code', '编程', 'bug', '修复', '功能', 'feature']):
            # 读取项目结构
            src_dirs = ['src', 'lib', 'js', 'py', 'scripts', '30-scripts-tools']
            for src_dir in src_dirs:
                src_path = self.workspace / src_dir
                if src_path.exists():
                    for file in src_path.rglob('*'):
                        if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                            context_files.append(str(file.relative_to(self.workspace)))

        # 配置相关任务
        if any(kw in task_lower for kw in ['配置', 'config', '设置', 'setup']):
            config_files = ['package.json', 'pyproject.toml', 'Cargo.toml', 'tsconfig.json', '.env']
            for cf in config_files:
                if (self.workspace / cf).exists():
                    context_files.append(cf)

        # 测试相关任务
        if any(kw in task_lower for kw in ['测试', 'test', 'pytest', 'jest']):
            for file in self.workspace.rglob('*test*'):
                if file.is_file():
                    context_files.append(str(file.relative_to(self.workspace)))

        return context_files[:20]  # 限制数量


# 主函数
def main():
    """测试入口"""
    interceptor = ToolCallInterceptor()

    if len(sys.argv) < 2:
        print("用法：python tool_call_interceptor.py <tool_name> <params_json>")
        sys.exit(1)

    tool_name = sys.argv[1]
    params_json = sys.argv[2] if len(sys.argv) > 2 else '{}'
    params = json.loads(params_json)

    optimized = interceptor.optimize_for_cursor_mode(tool_name, params)
    print(json.dumps(optimized, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
