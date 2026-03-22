#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify Cursor Mode default settings"""

import json
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

CONFIG_FILE = Path.home() / ".copaw" / "config.json"

def check_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 50)
    print("Cursor Mode Default Settings Verification")
    print("=" * 50)
    
    # Check agents/running
    running = config.get("agents", {}).get("running", {})
    
    checks = [
        ("auto_execute", running.get("auto_execute")),
        ("auto_fix_errors", running.get("auto_fix_errors")),
        ("max_retries", running.get("max_retries")),
        ("auto_read_related", running.get("auto_read_related")),
        ("context_window", running.get("context_window")),
        ("history_max_length", running.get("history_max_length")),
    ]
    
    print("\n[Agents/Running Settings]")
    for key, value in checks:
        status = "[OK]" if value else "[FAIL]"
        print(f"  {status} {key}: {value}")
    
    # Check security
    security = config.get("security", {})
    tool_guard = security.get("tool_guard", {})
    tool_guard_enabled = tool_guard.get("enabled", True)
    
    print("\n[Security]")
    print(f"  {'[OK]' if not tool_guard_enabled else '[FAIL]'} tool_guard.enabled: {tool_guard_enabled}")
    
    # Check system_prompt_files
    prompt_files = config.get("agents", {}).get("system_prompt_files", [])
    cursor_mode_included = "CURSOR-MODE.md" in prompt_files
    
    print("\n[System Prompt Files]")
    print(f"  {'[OK]' if cursor_mode_included else '[FAIL]'} CURSOR-MODE.md included")
    print(f"  Files: {prompt_files}")
    
    # Summary
    all_ok = (
        running.get("auto_execute") == True and
        running.get("auto_fix_errors") == True and
        not tool_guard_enabled and
        cursor_mode_included
    )
    
    print("\n" + "=" * 50)
    if all_ok:
        print("[SUCCESS] Cursor Mode is set as default!")
    else:
        print("[WARNING] Some settings may not be applied correctly")
    print("=" * 50)
    
    return all_ok

if __name__ == "__main__":
    check_config()
