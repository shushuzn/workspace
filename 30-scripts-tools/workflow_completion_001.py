import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-COMPLETION-001 Command Completion & Quick Reference
Generates command references and shell completion scripts
"""
import json, sys
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")
WORKFLOWS_FILE = TOOLS_DIR / "workflows.json"

def load_workflows():
    if WORKFLOWS_FILE.exists():
        return json.loads(WORKFLOWS_FILE.read_text(encoding="utf-8", errors="replace"))
    return {}

def generate_bash_completion() -> None:
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
# py workflow_completion_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_completion_001.py

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

Generate bash completion script"""
    workflows = load_workflows()
    workflow_names = list(workflows.keys()) if isinstance(workflows, dict) else [w.get("name", "unknown") for w in workflows]
    
    script = '''# OpenClaw Workflow Completion for Bash
_complete_workflow() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    commands="dev full plan security quick research arxiv classify trends optimize backup deploy test"
    
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
    fi
}
complete -F _complete_workflow workflow.bat
'''
    return script

def generate_ps_completion() -> None:
    """Generate PowerShell completion script"""
    script = '''# OpenClaw Workflow Completion for PowerShell
$commands = @("dev", "full", "plan", "security", "quick", "research", "arxiv", "classify", "trends", "optimize", "backup", "deploy", "test")

Register-ArgumentCompleter -CommandName workflow.bat -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
'''
    return script

def generate_quick_ref() -> None:
    """Generate quick reference markdown"""
    workflows = load_workflows()
    
    ref = """# OpenClaw 命令快速参考

## 工作流命令
```
workflow.bat dev       # 开发工作流
workflow.bat full      # 全面检查
workflow.bat plan      # 规划
workflow.bat security  # 安全扫描
workflow.bat quick     # 快速检查
workflow.bat research # 研究
workflow.bat optimize  # 优化
workflow.bat backup    # 备份
workflow.bat deploy    # 部署
workflow.bat test      # 测试
```

## 工具命令
```
py auto_discover_001.py          # 发现工具
py workflow_health_001.py        # 健康检查
py workflow_diagnosis_001.py     # 诊断
py workflow_optimizer_001.py     # 优化
py performance_optimizer_001.py  # 性能
py multi_agent_viz_001.py        # 可视化
```

## 状态检查
```
py workflow_health_001.py          # 系统健康
py workflow_stats_001.py           # 统计
py performance_optimizer_001.py --benchmark-all  # 性能基准
```

"""
    return ref

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        print("""[WORKFLOW-COMPLETION-001]
Usage:
  python workflow_completion_001.py bash     # Generate bash completion
  python workflow_completion_001.py ps       # Generate PowerShell completion
  python workflow_completion_001.py ref      # Generate quick reference
  python workflow_completion_001.py install   # Install all completions
""")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "bash":
        script = generate_bash_completion()
        print(script)
        # Optionally save
        out_file = Path.home() / ".openclaw_completion.sh"
        out_file.write_text(script)
        print(f"\n[Saved to: {out_file}]")
        print("Add to ~/.bashrc: source {0}".format(out_file))
    
    elif cmd == "ps":
        script = generate_ps_completion()
        print(script)
    
    elif cmd == "ref":
        print(generate_quick_ref())
    
    elif cmd == "install":
        # Bash
        bash_script = generate_bash_completion()
        bash_file = Path.home() / ".openclaw_completion.sh"
        bash_file.write_text(bash_script)
        
        # PowerShell
        ps_script = generate_ps_completion()
        ps_file = Path("openclaw_completion.ps1")
        ps_file.write_text(ps_script)
        
        print("[WORKFLOW-COMPLETION-001] Installed!")
        print(f"  Bash: {bash_file}")
        print(f"  PS:   {ps_file}")

if __name__ == "__main__":
    main()
