#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set Cursor Mode as default configuration"""

import json
import sys
from pathlib import Path

# Fix Unicode for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

CONFIG_FILE = Path.home() / ".copaw" / "config.json"

def main():
    # Read config
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 1. Add CURSOR-MODE.md to system_prompt_files
    if "system_prompt_files" not in config.get("agents", {}):
        if "agents" not in config:
            config["agents"] = {}
        config["agents"]["system_prompt_files"] = []

    if "CURSOR-MODE.md" not in config["agents"]["system_prompt_files"]:
        config["agents"]["system_prompt_files"].append("CURSOR-MODE.md")

    # 2. Set running parameters
    if "running" not in config.get("agents", {}):
        config["agents"]["running"] = {}

    config["agents"]["running"].update({
        "auto_execute": True,
        "auto_fix_errors": True,
        "max_retries": 3,
        "auto_read_related": True,
        "context_window": 200000,
        "memory_compact_ratio": 0.8,
        "history_max_length": 50000,
        "enable_tool_result_compact": True,
        "tool_result_compact_keep_n": 10
    })

    # 3. Disable tool_guard
    if "security" not in config:
        config["security"] = {}

    if "tool_guard" not in config["security"]:
        config["security"]["tool_guard"] = {}

    config["security"]["tool_guard"]["enabled"] = False

    # 4. Set llm_routing
    config["agents"]["llm_routing"] = {
        "enabled": True,
        "mode": "smart"
    }

    # Save config
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("[OK] Cursor Mode set as default")
    print(f"[OK] Config file: {CONFIG_FILE}")

if __name__ == "__main__":
    main()
