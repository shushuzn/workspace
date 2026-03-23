#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强 OpenClaw 编程能力
"""

import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

CONFIG_FILE = Path.home() / ".copaw" / "config.json"

def enhance():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 1. 增强 agents 配置
    if "agents" not in config:
        config["agents"] = {}

    config["agents"]["running"] = {
        "auto_execute": True,
        "auto_fix_errors": True,
        "max_retries": 5,
        "auto_read_related": True,
        "context_window": 300000,
        "history_max_length": 100000,
        "enable_tool_result_compact": True,
        "tool_result_compact_keep_n": 20,
        "max_iters": 200
    }

    # 2. 增强 LLM 路由 - 编程用更强模型
    config["agents"]["llm_routing"] = {
        "enabled": True,
        "mode": "smart",
        "routing_rules": [
            {
                "pattern": "代码|编程|bug|重构|函数|类|变量|接口|API|算法|数据结构",
                "model": "claude-sonnet-4-20250514",
                "temperature": 0.3,
                "priority": 10
            },
            {
                "pattern": "debug|修复|错误|exception|undefined|null",
                "model": "claude-sonnet-4-20250514",
                "temperature": 0.2,
                "priority": 10
            }
        ]
    }

    # 3. 添加工具配置
    config["tools"] = {
        "execute_shell_command": {
            "enabled": True,
            "auto_confirm": True,
            "timeout": 600,
            "max_output_lines": 1000,
            "capture_stderr": True
        },
        "read_file": {
            "enabled": True,
            "auto_read_related": True,
            "max_file_size_mb": 50,
            "syntax_highlight": True
        },
        "write_file": {
            "enabled": True,
            "auto_backup": True,
            "backup_dir": ".copaw-backups"
        },
        "edit_file": {
            "enabled": True,
            "auto_retry": True,
            "max_retries": 5,
            "show_diff": True
        },
        "grep_search": {
            "enabled": True,
            "context_lines": 5,
            "case_sensitive": False
        },
        "glob_search": {
            "enabled": True,
            "include_hidden": False
        },
        "browser_use": {
            "enabled": True,
            "headless": False
        }
    }

    # 4. 禁用安全限制
    if "security" not in config:
        config["security"] = {}
    config["security"]["tool_guard"] = {"enabled": False}

    # 5. MCP 服务器配置
    config["mcp"] = {
        "servers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.home() / "OpenClaw" / "workspace")],
                "enabled": True
            },
            "git": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-git"],
                "enabled": True
            },
            "memory": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-memory"],
                "enabled": True
            }
        }
    }

    # 6. 编程系统提示
    config["agents"]["system_prompt_files"] = [
        "AGENTS.md",
        "SOUL.md",
        "PROFILE.md",
        "CURSOR-MODE.md",
        "CODING-ASSISTANT.md"
    ]

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("[OK] Programming capabilities enhanced!")
    print()
    print("Enhanced features:")
    print("  - Larger context window (300K tokens)")
    print("  - Smart model routing for code tasks")
    print("  - Extended command timeout (600s)")
    print("  - Auto-retry on errors (5 attempts)")
    print("  - MCP servers enabled")
    print("  - Security restrictions disabled")
    print()
    print("Restart OpenClaw to apply changes.")

if __name__ == "__main__":
    enhance()
