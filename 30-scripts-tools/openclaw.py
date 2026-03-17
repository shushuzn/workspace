#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenClaw CLI v2.0 - Unified Command Interface
Integrates all Phase 4 innovations into single CLI

Usage:
    python openclaw.py --help
    python openclaw.py knowledge build
    python openclaw.py deploy tool.py
    python openclaw.py test run
    python openclaw.py config show
    python openclaw.py analyze errors
    python openclaw.py monitor resources
    python openclaw.py optimize performance
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "30-scripts-tools"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class OpenClawCLI:
    """Unified CLI for all OpenClaw tools"""
    
    def __init__(self):
        self.tools = self._discover_tools()
    
    def _discover_tools(self):
        """Discover available tools"""
        tool_mapping = {
            # Phase 4 Innovations
            'knowledge': {
                'build': 'knowledge_graph_builder.py',
                'view': 'knowledge_graph_viewer.html',
                'update': 'knowledge_graph_updater.py'
            },
            'orchestrate': {
                'run': 'automation_orchestrator.py',
                'schedule': 'smart_scheduler.py'
            },
            'notify': {
                'send': 'smart_notification.py',
                'config': 'notification_router.py'
            },
            'review': {
                'code': 'code_quality_reviewer.py',
                'paper': 'paper_summarizer.py'
            },
            'test': {
                'generate': 'auto_test_generator.py',
                'run': 'auto_test_runner.py',
                'coverage': 'auto_test_runner.py --coverage'
            },
            'docs': {
                'generate': 'smart_doc_generator.py',
                'api': 'smart_doc_generator.py --api'
            },
            'performance': {
                'profile': 'performance_profiler.py',
                'benchmark': 'performance_profiler.py --benchmark',
                'report': 'performance_profiler.py --report'
            },
            'data': {
                'clean': 'auto_data_cleaner.py',
                'collect': 'arxiv_collector.py'
            },
            'resource': {
                'monitor': 'resource_monitor.py',
                'report': 'resource_monitor.py --report',
                'optimize': 'resource_monitor.py --optimize'
            },
            'deploy': {
                'tool': 'auto_deployer.py',
                'status': 'auto_deployer.py --status',
                'rollback': 'auto_deployer.py --rollback'
            },
            'error': {
                'analyze': 'error_analyzer.py',
                'scan': 'error_analyzer.py --scan',
                'report': 'error_analyzer.py --report'
            },
            'config': {
                'show': 'config_manager.py --show',
                'set': 'config_manager.py --set',
                'validate': 'config_manager.py --validate',
                'backup': 'config_manager.py --backup'
            },
            'cache': {
                'stats': 'cache_manager.py --stats',
                'clean': 'cache_manager.py --clean'
            },
            'health': {
                'check': 'health_monitor.py',
                'report': 'health_monitor.py --report'
            },
            'memory': {
                'distill': 'memory-distiller.py',
                'maintain': 'memory-maintenance.py',
                'search': 'memory-search-v2.py'
            },
            'heal': {
                'scan': 'self_healing.py --scan',
                'fix': 'self_healing.py --fix',
                'report': 'self_healing.py --report'
            },
            'feishu': {
                'send': 'feishu_notification.py',
                'test': 'feishu_notification.py --test'
            }
        }
        return tool_mapping
    
    def run_tool(self, tool_name: str, args: list = None):
        """Run a tool with arguments"""
        tool_path = TOOLS_DIR / tool_name
        
        if not tool_path.exists():
            print(f"[ERROR] Tool not found: {tool_name}")
            return False
        
        cmd = ['python', str(tool_path)]
        if args:
            cmd.extend(args)
        
        print(f"[RUN] {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=str(WORKSPACE))
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def show_help(self):
        """Show comprehensive help"""
        help_text = f"""
╔═══════════════════════════════════════════════════════════╗
║           OpenClaw CLI v2.0 - Unified Interface           ║
╠═══════════════════════════════════════════════════════════╣
║  Workspace: {str(WORKSPACE)[:50]:<50} ║
╚═══════════════════════════════════════════════════════════╝

USAGE:
    python openclaw.py <category> <command> [options]

CATEGORIES & COMMANDS:

📊 KNOWLEDGE (Knowledge Graph)
    knowledge build          Build knowledge graph from workspace
    knowledge view           Open interactive knowledge graph viewer
    knowledge update         Incremental knowledge graph update

⚙️  ORCHESTRATE (Task Orchestration)
    orchestrate run          Run automation orchestrator
    orchestrate schedule     Show optimized schedule

🔔 NOTIFY (Notifications)
    notify send <msg>        Send notification
    notify config            Configure notification channels

🔍 REVIEW (Code/Paper Review)
    review code              Auto-review code quality
    review paper <pdf>       Summarize research paper

🧪 TEST (Testing)
    test generate            Auto-generate tests for tools
    test run                 Run all tests
    test coverage            Generate coverage report

📚 DOCS (Documentation)
    docs generate            Auto-generate documentation
    docs api                 Generate API documentation

⚡ PERFORMANCE
    performance profile      Profile tool performance
    performance benchmark    Benchmark all tools
    performance report       Generate performance report

📁 DATA
    data clean               Clean and standardize data
    data collect             Collect data from sources

🖥️  RESOURCE
    resource monitor         Monitor system resources
    resource report          Generate resource report
    resource optimize        Get optimization suggestions

🚀 DEPLOY
    deploy <tool.py>         Deploy a tool
    deploy status            Show deployment status
    deploy rollback <tool>   Rollback to previous version

🐛 ERROR
    error analyze            Analyze error logs
    error scan               Scan for errors
    error report             Generate error report

⚙️  CONFIG
    config show              Show configuration
    config set <K=V>         Set config value
    config validate          Validate configuration
    config backup            Backup configuration

💾 CACHE
    cache stats              Show cache statistics
    cache clean              Clean cache

❤️  HEALTH
    health check             Run health check
    health report            Generate health report

🧠 MEMORY
    memory distill           Distill daily notes to memory
    memory maintain          Run memory maintenance
    memory search <query>    Search memory

🔧 HEAL (Self-Healing)
    heal scan                Scan for issues
    heal fix                 Auto-fix detected issues
    heal report              Generate healing report

📱 FEISHU
    feishu send <msg>        Send Feishu message
    feishu test              Test Feishu integration

EXAMPLES:
    python openclaw.py knowledge build
    python openclaw.py review code
    python openclaw.py test run --parallel
    python openclaw.py config show
    python openclaw.py performance benchmark
    python openclaw.py deploy my_tool.py

VERSION: 2.0 (Phase 4 Integrated)
LAST UPDATED: 2026-03-16
"""
        print(help_text)


def main():
    cli = OpenClawCLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    # Handle --help
    if sys.argv[1] in ['--help', '-h', 'help']:
        cli.show_help()
        return
    
    category = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else None
    args = sys.argv[3:] if len(sys.argv) > 3 else []
    
    # Get tool mapping
    tools = cli.tools
    
    if category not in tools:
        print(f"[ERROR] Unknown category: {category}")
        print(f"Available categories: {', '.join(tools.keys())}")
        return
    
    if not command:
        print(f"[ERROR] Command required for category: {category}")
        print(f"Available commands: {', '.join(tools[category].keys())}")
        return
    
    if command not in tools[category]:
        print(f"[ERROR] Unknown command: {command}")
        print(f"Available commands: {', '.join(tools[category].keys())}")
        return
    
    # Get tool and args
    tool_spec = tools[category][command]
    
    # Parse tool name and additional args
    if ' --' in tool_spec:
        tool_name, extra_args = tool_spec.split(' --', 1)
        args = ['--' + extra_args] + args
    else:
        tool_name = tool_spec
    
    # Run tool
    success = cli.run_tool(tool_name, args)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
