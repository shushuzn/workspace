#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Unified CLI - Single entry point for all workspace tools

Usage:
    openclaw <command> [subcommand] [options]

Commands:
    memory          Memory management tools
    collect         Data collection tools
    dashboard       Dashboard management
    cache           Cache management
    health          Health checks
    review          Code/paper review
    knowledge       Knowledge graph tools
    notify          Notification tools

Examples:
    openclaw memory maintain --daily
    openclaw memory fix --strict
    openclaw collect github --language python
    openclaw collect medium --topic ai
    openclaw collect arxiv --query "AI agent"
    openclaw dashboard health --push
    openclaw cache stats
    openclaw cache cleanup
    openclaw health check
    openclaw review code --path ./30-scripts-tools
    openclaw review paper --path ./13-memory
    openclaw knowledge update
    openclaw notify task --name "Backup" --status success
"""

import sys
import argparse
from pathlib import Path

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "30-scripts-tools"
COLLECTORS_DIR = WORKSPACE / "40-collectors"
PERSONA_DIR = WORKSPACE / "00-persona-system"

# Command mapping
COMMANDS = {
    'memory': {
        'maintain': 'memory-maintenance.py',
        'fix': 'memory_auto_fix.py',
        'distill': 'memory-distiller.py',
        'health': 'memory_health_monitor.py',
    },
    'collect': {
        'github': 'github_trending_collector.py',
        'medium': 'medium_article_collector.py',
        'arxiv': 'arxiv_collector.py',
    },
    'dashboard': {
        'health': 'dashboard_health_widget.py',
        'timeline': 'dashboard_decision_timeline.py',
        'anomaly': 'dashboard_anomaly_alerts.py',
    },
    'cache': {
        'stats': 'cache_manager.py',
        'cleanup': 'cache_manager.py',
        'clear': 'cache_manager.py',
    },
    'health': {
        'check': 'health_check.py',
    },
    'review': {
        'code': 'code_reviewer.py',
        'paper': 'paper_summarizer.py',
        'quality': 'quality_scorer.py',
    },
    'knowledge': {
        'update': 'knowledge_graph_updater.py',
        'build': 'knowledge-graph-builder.py',
    },
    'notify': {
        'task': 'feishu_notification.py',
        'test': 'feishu_notification.py',
    },
    'heal': {
        'scan': 'self_healing.py',
        'auto': 'self_healing.py',
        'history': 'self_healing.py',
        'stats': 'self_healing.py',
    },
}

# Default arguments for each command
DEFAULT_ARGS = {
    ('cache', 'stats'): ['--stats'],
    ('cache', 'cleanup'): ['--cleanup'],
    ('cache', 'clear'): ['--clear'],
    ('dashboard', 'health'): ['--push'],
    ('health', 'check'): ['--all'],
    ('knowledge', 'update'): ['--auto'],
    ('heal', 'scan'): ['--scan'],
    ('heal', 'auto'): ['--auto-heal'],
    ('heal', 'history'): ['--history'],
    ('heal', 'stats'): ['--stats'],
}


def run_command(script_path: Path, args: list) -> int:
    """Run a script with arguments"""
    import subprocess
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return 1
    
    cmd = [sys.executable, str(script_path)] + args
    print(f"🔧 Running: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=WORKSPACE)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw Unified CLI',
        prog='openclaw'
    )
    
    parser.add_argument('command', nargs='?', help='Main command')
    parser.add_argument('subcommand', nargs='?', help='Subcommand')
    parser.add_argument('args', nargs='*', help='Additional arguments')
    
    # Parse known args to handle subcommand-specific options
    args, unknown = parser.parse_known_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Check command exists
    if args.command not in COMMANDS:
        print(f"❌ Unknown command: {args.command}")
        print(f"Available commands: {', '.join(COMMANDS.keys())}")
        return 1
    
    command_map = COMMANDS[args.command]
    
    # If no subcommand, show available subcommands
    if not args.subcommand:
        print(f"Command: {args.command}")
        print(f"Available subcommands: {', '.join(command_map.keys())}")
        return 0
    
    # Check subcommand exists
    if args.subcommand not in command_map:
        print(f"❌ Unknown subcommand: {args.subcommand}")
        print(f"Available subcommands: {', '.join(command_map.keys())}")
        return 1
    
    # Get script path
    script_name = command_map[args.subcommand]
    
    # Search in multiple directories
    script_path = None
    search_dirs = [SCRIPTS_DIR, COLLECTORS_DIR, PERSONA_DIR, WORKSPACE]
    
    for search_dir in search_dirs:
        candidate = search_dir / script_name
        if candidate.exists():
            script_path = candidate
            break
    
    if not script_path:
        print(f"❌ Script not found: {script_name}")
        return 1
    
    # Build arguments
    final_args = args.args + unknown
    
    # Add default arguments if no args provided
    if not final_args:
        default = DEFAULT_ARGS.get((args.command, args.subcommand), [])
        final_args = default + final_args
    
    # Run command
    return run_command(script_path, final_args)


if __name__ == '__main__':
    sys.exit(main())
