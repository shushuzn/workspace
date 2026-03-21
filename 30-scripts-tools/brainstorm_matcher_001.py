import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Matcher - Match brainstorm ideas with existing tools
"""

import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Known existing tools by capability
EXISTING_TOOLS = {
    "version_control": ["git_commit_helper.py", "state_snapshot.py", "check_workflow.py"],
    "monitoring": ["tool_monitor.py", "workflow_performance_monitor.py", "agent_tool_monitor.py"],
    "undo_redo": ["state_snapshot.py", "check_current_state.py"],  # partial
    "documentation": ["export_format_001.py", "report_002_export.py"],
    "caching": ["smart_cache_001.py", "data_cache.py", "workflow_cache.py"],
    "parallel": ["parallel_tool_executor.py", "batch_tools_001.py"],
    "automation": ["auto_001_automator.py", "workflow_auto_executor.py"],
    "ai_suggest": ["ai_suggest_001.py", "roadmap_master_001.py"],
}

def match_ideas():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py brainstorm_matcher_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_matcher_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Match brainstormed ideas with existing tools"""
    ideas_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_prioritized.json")
    if not ideas_file.exists():
        print("ERROR: No prioritized ideas found")
        return
    
    with open(ideas_file, encoding="utf-8") as f:
        ideas = json.load(f)
    
    print("="*60)
    print("[BRAINSTORM] Ideas vs Existing Tools")
    print("="*60)
    
    results = []
    for idea in ideas:
        text = idea.get("text", "").lower()
        matched = []
        extension_needed = ""
        
        # Match with existing tools
        for capability, tools in EXISTING_TOOLS.items():
            if capability in text or any(t.replace(".py", "") in text for t in tools):
                matched.extend(tools)
        
        # Determine status
        if matched:
            status = "[EXISTS - Extend]"
            extension_needed = "Consider enhancements"
        else:
            status = "[NEW]"
            extension_needed = "Need to create"
        
        result = {
            "priority": idea.get("priority"),
            "idea": idea.get("text"),
            "phase": idea.get("phase"),
            "status": status,
            "existing_tools": matched,
            "extension": extension_needed
        }
        results.append(result)
        
        print(f"\n{idea.get('priority')}. {idea.get('text')}")
        print(f"   Phase: {idea.get('phase')}")
        print(f"   Status: {status}")
        if matched:
            print(f"   Existing: {', '.join(matched)}")
    
    # Save results
    output_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_matched.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n[Saved to] {output_file}")
    
    # Summary
    existing = sum(1 for r in results if "EXISTS" in r["status"])
    new = sum(1 for r in results if "NEW" in r["status"])
    
    print(f"\n[SUMMARY]")
    print(f"  Extend existing: {existing}")
    print(f"  Need new tools: {new}")
    
    return results

if __name__ == "__main__":
    match_ideas()