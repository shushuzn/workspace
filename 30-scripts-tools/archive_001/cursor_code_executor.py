#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenClaw Cursor Mode - 代码执行增强器
提供 Cursor 级别的编程体验：自动执行、错误修复、多文件修改
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置
WORKSPACE = r"D:\OpenClaw\workspace"
CONFIG_DIR = Path.home() / ".copaw"
BACKUP_DIR = WORKSPACE / ".copaw-backups"
LOG_DIR = WORKSPACE / ".copaw-logs"

# 自动执行的命令白名单
AUTO_EXECUTE_COMMANDS = [
    "python", "python3", "pip", "pip3",
    "npm", "pnpm", "yarn", "node", "npx", "bun", "deno",
    "git", "cargo", "go", "rustc", "javac", "java", "mvn", "gradle",
    "cd", "dir", "ls", "type", "cat", "echo", "copy", "xcopy", "robocopy",
    "mkdir", "rmdir", "del", "rm", "mv", "cp",
    "pytest", "unittest", "jest", "mocha", "vitest",
    "eslint", "prettier", "black", "flake8", "pylint",
    "tsc", "webpack", "vite", "rollup",
    "docker", "kubectl", "helm",
]

#  blocked 命令
BLOCKED_COMMANDS = [
    "format", "shutdown", "shutdown.exe",
    "del /F /Q /S", "rm -rf /", "rm -rf /*",
]


class CursorCodeExecutor:
    """Cursor 模式代码执行器"""

    def __init__(self):
        self.workspace = Path(WORKSPACE)
        self.config_dir = CONFIG_DIR
        self.backup_dir = Path(BACKUP_DIR)
        self.log_dir = Path(LOG_DIR)
        self.config = self._load_config()
        self.execution_log = []

        # 创建必要目录
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = self.config_dir / "config-cursor.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _backup_file(self, file_path: Path) -> Optional[Path]:
        """备份文件"""
        if not file_path.exists():
            return None

        backup_path = self.backup_dir / file_path.relative_to(self.workspace)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def _log_execution(self, action: str, details: Dict):
        """记录执行日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.execution_log.append(log_entry)

        # 保存到文件
        log_file = self.log_dir / f"exec-{datetime.now().strftime('%Y%m%d')}.json"
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def can_auto_execute(self, command: str) -> bool:
        """检查命令是否可以自动执行"""
        # 检查黑名单
        for blocked in BLOCKED_COMMANDS:
            if blocked in command:
                return False

        # 检查白名单
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False

        base_cmd = cmd_parts[0].lower()

        # 处理路径情况
        if base_cmd.endswith('.py') or base_cmd.endswith('.js'):
            return True

        for allowed in AUTO_EXECUTE_COMMANDS:
            if base_cmd == allowed or base_cmd.startswith(allowed + " "):
                return True

        return False

    def execute_command(self, command: str, auto_retry: bool = True, max_retries: int = 3) -> Dict:
        """执行命令，支持自动重试"""
        result = {
            "success": False,
            "command": command,
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "retries": 0
        }

        self._log_execution("command_execute", {"command": command})

        for attempt in range(max_retries if auto_retry else 1):
            result["retries"] = attempt

            try:
                proc = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=str(self.workspace),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                stdout, stderr = proc.communicate(timeout=self.config.get('agents', {}).get('running', {}).get('timeout', 300))

                result["stdout"] = stdout
                result["stderr"] = stderr
                result["returncode"] = proc.returncode
                result["success"] = (proc.returncode == 0)

                if result["success"]:
                    break

            except subprocess.TimeoutExpired:
                result["stderr"] = f"命令执行超时 (>{self.config.get('agents', {}).get('running', {}).get('timeout', 300)}秒)"
                proc.kill()
            except Exception as e:
                result["stderr"] = str(e)

        self._log_execution("command_result", result)
        return result

    def read_file(self, file_path: str, auto_read_related: bool = True) -> Dict:
        """读取文件，支持自动读取相关文件"""
        path = self.workspace / file_path
        result = {
            "success": False,
            "content": "",
            "error": "",
            "related_files": []
        }

        if not path.exists():
            result["error"] = f"文件不存在：{file_path}"
            return result

        try:
            with open(path, 'r', encoding='utf-8') as f:
                result["content"] = f.read()
            result["success"] = True

            # 自动读取相关文件
            if auto_read_related:
                result["related_files"] = self._find_related_files(path)

        except Exception as e:
            result["error"] = str(e)

        self._log_execution("read_file", {"file": file_path, "success": result["success"]})
        return result

    def _find_related_files(self, file_path: Path) -> List[str]:
        """查找相关文件（导入、引用等）"""
        related = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找 import/require
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
                r'require\([\'"](.+?)[\'"]\)',
                r'from\s+(.+?)\s+import',
            ]

            import re
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # 转换为实际路径
                    if match.startswith('.'):
                        rel_path = (file_path.parent / match).resolve()
                    else:
                        rel_path = self.workspace / match

                    # 尝试不同扩展名
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

        return related[:10]  # 限制数量

    def write_file(self, file_path: str, content: str, auto_backup: bool = True) -> Dict:
        """写入文件，支持自动备份"""
        path = self.workspace / file_path
        result = {
            "success": False,
            "error": "",
            "backup_path": None
        }

        # 备份现有文件
        if auto_backup and path.exists():
            backup_path = self._backup_file(path)
            if backup_path:
                result["backup_path"] = str(backup_path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        self._log_execution("write_file", {"file": file_path, "success": result["success"]})
        return result

    def edit_file(self, file_path: str, old_text: str, new_text: str, auto_retry: bool = True) -> Dict:
        """编辑文件，支持自动重试"""
        result = {
            "success": False,
            "error": "",
            "replacements": 0
        }

        path = self.workspace / file_path

        if not path.exists():
            result["error"] = f"文件不存在：{file_path}"
            return result

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 备份
            self._backup_file(path)

            # 替换
            new_content = content.replace(old_text, new_text)

            if new_content == content:
                result["error"] = "未找到匹配文本，请检查 old_text 是否精确匹配"
                return result

            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            result["success"] = True
            result["replacements"] = content.count(old_text)

        except Exception as e:
            result["error"] = str(e)

        self._log_execution("edit_file", {"file": file_path, "success": result["success"]})
        return result

    def grep_search(self, pattern: str, path: str = ".", context_lines: int = 3) -> List[Dict]:
        """搜索文件内容"""
        results = []
        search_path = self.workspace / path

        try:
            import re
            regex = re.compile(pattern)

            for file_path in search_path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.md', '.json', '.txt', '.html', '.css']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        for i, line in enumerate(lines):
                            if regex.search(line):
                                context_start = max(0, i - context_lines)
                                context_end = min(len(lines), i + context_lines + 1)

                                results.append({
                                    "file": str(file_path.relative_to(self.workspace)),
                                    "line": i + 1,
                                    "content": line.strip(),
                                    "context": ''.join(lines[context_start:context_end])
                                })
                    except Exception:
                        pass

        except Exception as e:
            pass

        return results[:100]  # 限制结果数量

    def run_tests(self, test_command: str = None) -> Dict:
        """运行测试"""
        if not test_command:
            # 自动检测测试命令
            if (self.workspace / "pytest.ini").exists() or (self.workspace / "pyproject.toml").exists():
                test_command = "python -m pytest"
            elif (self.workspace / "package.json").exists():
                test_command = "npm test"
            elif (self.workspace / "Cargo.toml").exists():
                test_command = "cargo test"
            else:
                return {"success": False, "error": "未找到测试配置"}

        return self.execute_command(test_command)

    def get_project_structure(self, max_depth: int = 3) -> str:
        """获取项目结构"""
        structure = []

        def scan_dir(path: Path, depth: int, prefix: str = ""):
            if depth > max_depth:
                return

            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

            for i, item in enumerate(items):
                if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv', '.git']:
                    continue

                is_last = (i == len(items) - 1)
                connector = "└── " if is_last else "├── "
                structure.append(f"{prefix}{connector}{item.name}")

                if item.is_dir():
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    scan_dir(item, depth + 1, next_prefix)

        scan_dir(self.workspace, 0)
        return "\n".join(structure)


# 主函数 - 供外部调用
def main():
    """主入口"""
    executor = CursorCodeExecutor()

    if len(sys.argv) < 2:
        print("用法：python cursor_code_executor.py <command> [args...]")
        print("命令：execute, read, write, edit, search, test, structure")
        sys.exit(1)

    command = sys.argv[1]

    if command == "execute":
        cmd = " ".join(sys.argv[2:])
        result = executor.execute_command(cmd)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "read":
        file_path = sys.argv[2] if len(sys.argv) > 2 else ""
        result = executor.read_file(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "write":
        if len(sys.argv) < 4:
            print("用法：write <file> <content>")
            sys.exit(1)
        file_path = sys.argv[2]
        content = sys.argv[3]
        result = executor.write_file(file_path, content)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "structure":
        print(executor.get_project_structure())

    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
