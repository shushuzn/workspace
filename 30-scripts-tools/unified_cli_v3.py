#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified CLI v3 - Central command-line interface for all tools

Features:
- Natural language commands
- Tool discovery and execution
- Workflow orchestration
- Interactive mode
- Command history
- Auto-completion support
"""

import os
import sys
import json
import subprocess
import shlex
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'

# Command aliases (natural language → tool command)
COMMAND_ALIASES = {
    # Registry commands
    'scan tools': 'tool_registry.py --scan',
    'list tools': 'tool_registry.py --list',
    'tool stats': 'tool_registry.py --stats',
    'tool health': 'tool_registry.py --health',
    'search tool': 'tool_registry.py --search',
    
    # Analytics commands
    'analyze tools': 'tool_analytics.py --analyze',
    'tool report': 'tool_analytics.py --report',
    'tool dashboard': 'tool_analytics.py --dashboard',
    
    # Orchestrator commands
    'run workflow': 'tool_orchestrator.py --execute',
    'list workflows': 'tool_orchestrator.py --list',
    'create workflow': 'tool_orchestrator.py --create',
    
    # Memory search
    'search memory': 'ultimate_memory_search_v3.py --demo',
    'memory search': 'ultimate_memory_search_v3.py --demo',
    
    # Cache management
    'cache stats': 'cache_observability.py --stats',
    'cache dashboard': 'cache_observability.py --dashboard',
    
    # Workflow
    'workflow visualizer': 'workflow_visualizer.py',
    'workflow engine': 'workflow_engine.py --demo',
    
    # Knowledge graph
    'knowledge graph': 'knowledge_graph_enhanced.py --visualize',
    'kg update': 'knowledge_graph_enhanced.py --update',
    
    # System
    'system health': 'system_health_checker.py --check',
    'deploy': 'auto_deployer.py',
    'performance': 'performance_analyzer.py',
    
    # File Organization (新增)
    'scan files': 'file-organizer.py --scan',
    'clean duplicates': 'clean-duplicates-safe.py',
    'organize root': 'organize-root-files-v2.py',
    'compress tiff': 'compress-tiff-to-png.py',
    
    # Backup & Recovery (新增)
    'backup restructure': 'backup-strategy-restructure.py',
    'disaster cleanup': 'disaster-recovery-cleanup.py',
    
    # Git Hooks (新增)
    'install hooks': 'install-git-hooks.py',
    'setup hooks': 'setup-git-hooks.py',
    'test hook': 'pre_commit_hook.py --test',
    
    # Security (新增)
    'security scan': 'security_auditor.py',
    'security fix': 'security_auto_fixer.py',
    
    # Monitoring (新增)
    'monitor': 'real_time_monitor.py',
    'anomaly detect': 'anomaly_detector_pro.py',
    'error analyze': 'error_analyzer.py',
    
    # ArXiv (新增)
    'arxiv scan': 'arxiv_collector_v2.py',
    'arxiv workflow': 'arxiv_workflow.py',
    
    # Feishu (新增)
    'feishu notify': 'feishu_notification.py',
    'feishu analytics': 'feishu-analytics-dashboard.py',
    
    # Auto tools (新增)
    'auto distill': 'auto_distill.py',
    'auto test': 'auto_test_runner.py',
    'auto deploy': 'auto_deploy.py',
    
    # Smart tools (新增)
    'smart doc': 'smart_doc_generator.py',
    'smart scheduler': 'smart_scheduler.py',
    'smart workflow': 'smart_workflow_optimizer.py',
    
    # Workspace (新增)
    'workspace init': 'workspace_init.py',
    'workspace check': 'workspace.py',
    
    # Research (新增)
    'research cnt': 'cnt-research-runner.py',
    'research arxiv': 'arxiv_workflow.py',
    'critic check': 'critic_auto_fix.py',
    
    # Data (新增)
    'data scan': 'tool_registry.py --scan',
    'data clean': 'clean-duplicates-safe.py',
    
    # Persona (新增)
    'persona list': 'memory_persona.py --list',
    'persona status': 'meta_cognition_monitor.py',
    
    # Memory (新增)
    'memory distill': 'auto_distill.py',
    'memory search': 'ultimate_memory_search_v3.py --demo',
    'memory quality': 'memory_quality_assessor.py',
    
    # Experiment (新增)
    'experiment run': 'experiment_platform.py',
    'experiment analyze': 'data_sync_enhancer.py',
    
    # Documentation (新增)
    'doc generate': 'doc_generator.py',
    'doc update': 'unified_doc_generator.py',
    
    # Cleanup (新增)
    'cleanup reports': 'cleanup_reports.py',
    'cleanup cache': 'cache_manager.py --clean',
    'cleanup temp': 'file-organizer.py --clean',
    
    # Visualization (新增)
    'visualize workflow': 'workflow_visualizer_web.py',
    'visualize kg': 'knowledge_graph_builder.py --visualize',
    'dashboard': 'phase4_dashboard.py',
    
    # Quick Access (快速访问)
    'quick health': 'system_health_checker.py --quick',
    'quick scan': 'file-organizer.py --scan',
    'recent': 'memory_recent.py',
    'status': 'session-check.py',
}

# Command categories
COMMAND_CATEGORIES = {
    'registry': ['scan', 'list', 'stats', 'health', 'search'],
    'analytics': ['analyze', 'report', 'dashboard'],
    'orchestrator': ['workflow', 'run', 'create'],
    'memory': ['memory', 'search', 'distill', 'quality'],
    'cache': ['cache'],
    'workflow': ['workflow', 'visualizer', 'engine'],
    'knowledge': ['knowledge', 'kg', 'doc'],
    'system': ['system', 'health', 'deploy', 'performance'],
    'files': ['scan files', 'clean', 'organize', 'compress'],
    'backup': ['backup', 'disaster', 'recovery'],
    'git': ['hooks', 'install', 'setup', 'test'],
    'security': ['security', 'scan', 'fix'],
    'monitor': ['monitor', 'anomaly', 'error'],
    'arxiv': ['arxiv'],
    'feishu': ['feishu'],
    'auto': ['auto', 'distill', 'deploy'],
    'smart': ['smart', 'scheduler'],
    'workspace': ['workspace'],
    'research': ['research', 'cnt', 'critic'],
    'data': ['data'],
    'persona': ['persona'],
    'experiment': ['experiment'],
    'cleanup': ['cleanup'],
    'visualization': ['visualize', 'dashboard'],
    'quick': ['quick', 'recent', 'status'],
}


class UnifiedCLI:
    """
    Unified command-line interface
    
    Features:
    - Natural language parsing
    - Tool execution
    - Command history
    - Auto-suggestions
    """
    
    def __init__(self):
        self.history: List[Dict] = []
        self.history_file = WORKSPACE / 'data' / 'cli' / 'history.json'
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load history
        self._load_history()
    
    def _load_history(self):
        """Load command history"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
    
    def _save_history(self):
        """Save command history"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history[-100:], f, indent=2, ensure_ascii=False)  # Keep last 100
    
    def show_history(self, limit: int = 10) -> str:
        """Show command history"""
        if not self.history:
            return "\n📭 暂无历史记录\n"
        
        history_text = f"\n📜 最近 {min(limit, len(self.history))} 条命令历史\n"
        history_text += "=" * 60 + "\n\n"
        
        for i, entry in enumerate(reversed(self.history[-limit:]), 1):
            timestamp = entry.get('timestamp', 'Unknown')[:16].replace('T', ' ')
            command = entry.get('command', 'Unknown')
            success = '✅' if entry.get('success', False) else '❌'
            duration = entry.get('duration_seconds', 0)
            
            history_text += f"{i:2d}. {success} {command}\n"
            history_text += f"    ⏱️  {duration:.2f}s | 🕐 {timestamp}\n\n"
        
        return history_text
    
    def show_stats(self) -> str:
        """Show command statistics"""
        if not self.history:
            return "\n📭 暂无统计数据\n"
        
        total = len(self.history)
        success = sum(1 for h in self.history if h.get('success', False))
        failed = total - success
        success_rate = (success / total * 100) if total > 0 else 0
        
        # Most used commands
        command_count = {}
        for h in self.history:
            cmd = h.get('command', 'Unknown')
            command_count[cmd] = command_count.get(cmd, 0) + 1
        
        top_commands = sorted(command_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Average duration
        avg_duration = sum(h.get('duration_seconds', 0) for h in self.history) / total
        
        stats_text = "\n📊 命令统计\n"
        stats_text += "=" * 60 + "\n\n"
        stats_text += f"总命令数：{total}\n"
        stats_text += f"成功：{success} ({success_rate:.1f}%)\n"
        stats_text += f"失败：{failed} ({100-success_rate:.1f}%)\n"
        stats_text += f"平均执行时间：{avg_duration:.2f}s\n\n"
        stats_text += "🔥 最常用命令:\n"
        for i, (cmd, count) in enumerate(top_commands, 1):
            stats_text += f"  {i}. {cmd} ({count}次)\n"
        
        return stats_text
    
    def parse_command(self, user_input: str) -> Optional[str]:
        """
        Parse natural language input to tool command
        
        Args:
            user_input: User's natural language input
        
        Returns:
            Tool command string or None
        """
        input_lower = user_input.lower().strip()
        
        # Direct alias match
        if input_lower in COMMAND_ALIASES:
            return COMMAND_ALIASES[input_lower]
        
        # Partial match
        for alias, command in COMMAND_ALIASES.items():
            if alias in input_lower or input_lower in alias:
                return command
        
        # Try to detect tool name
        tool_match = re.search(r'(\w+(?:_\w+)*)\.py', input_lower)
        if tool_match:
            tool_name = tool_match.group(1)
            tool_path = TOOLS_DIR / f"{tool_name}.py"
            if tool_path.exists():
                # Extract arguments
                args = input_lower.replace(f"{tool_name}.py", "").strip()
                return f"{tool_name}.py {args}".strip()
        
        # Category-based suggestion
        for category, keywords in COMMAND_CATEGORIES.items():
            if any(kw in input_lower for kw in keywords):
                # Return category help
                return f"help {category}"
        
        return None
    
    def execute(self, command: str, args: List[str] = None) -> Dict:
        """
        Execute a tool command
        
        Args:
            command: Tool command
            args: Additional arguments
        
        Returns:
            Execution result
        """
        start_time = datetime.now()
        
        # Build full command - always use Python interpreter
        if command.endswith('.py'):
            tool_path = TOOLS_DIR / command
            if not tool_path.exists():
                return {
                    'success': False,
                    'error': f'Tool not found: {command}',
                }
            
            full_cmd = [sys.executable, str(tool_path)] + (args or [])
        else:
            # Check if it's a tool name without .py
            tool_name = command.split()[0]
            tool_args = command.split()[1:]
            tool_path = TOOLS_DIR / f"{tool_name}.py"
            if tool_path.exists():
                full_cmd = [sys.executable, str(tool_path)] + tool_args + (args or [])
            else:
                # Shell command
                full_cmd = command.split() + (args or [])
        
        try:
            # Execute - use shell=True on Windows
            if sys.platform == 'win32':
                # On Windows, use shell=True and pass command as string
                cmd_str = ' '.join(full_cmd)
                result = subprocess.run(
                    cmd_str,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    encoding='utf-8',
                    errors='replace',
                    cwd=str(TOOLS_DIR),
                    shell=True,
                )
            else:
                result = subprocess.run(
                    full_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    encoding='utf-8',
                    errors='replace',
                    cwd=str(TOOLS_DIR),
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Record history
            self.history.append({
                'command': command,
                'args': args,
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'exit_code': result.returncode,
                'success': result.returncode == 0,
            })
            self._save_history()
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'duration_seconds': duration,
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Timeout after 300s',
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def suggest(self, partial: str) -> List[str]:
        """Get command suggestions"""
        suggestions = []
        partial_lower = partial.lower()
        
        # Match aliases
        for alias in COMMAND_ALIASES.keys():
            if partial_lower in alias:
                suggestions.append(f"{alias} → {COMMAND_ALIASES[alias]}")
        
        # Match tool files
        for tool_file in TOOLS_DIR.glob('*.py'):
            if partial_lower in tool_file.stem.lower():
                suggestions.append(tool_file.name)
        
        return suggestions[:10]
    
    def get_help(self, category: str = None) -> str:
        """Get help text"""
        if category:
            # Category-specific help
            commands = [
                (alias, cmd) for alias, cmd in COMMAND_ALIASES.items()
                if any(kw in alias for kw in COMMAND_CATEGORIES.get(category, []))
            ]
            
            help_text = f"\n📚 {category.upper()} Commands\n"
            help_text += "=" * 60 + "\n\n"
            
            for alias, cmd in commands[:15]:
                help_text += f"  {alias}\n"
                help_text += f"    → {cmd}\n\n"
            
            return help_text
        
        # General help
        help_text = "\n🎯 Unified CLI v3 - 工作区统一命令行界面\n"
        help_text += "=" * 60 + "\n\n"
        
        help_text += "用法:\n"
        help_text += "  py unified_cli_v3.py <命令> [参数]\n"
        help_text += "  py unified_cli_v3.py --interactive  (交互模式)\n"
        help_text += "  py unified_cli_v3.py --suggest <关键词>  (获取建议)\n"
        help_text += "  py unified_cli_v3.py --history  (查看历史)\n"
        help_text += "  py unified_cli_v3.py --stats  (查看统计)\n\n"
        
        help_text += "常用命令:\n"
        help_text += "  工具管理:\n"
        help_text += "    scan tools          - 扫描 302 个工具\n"
        help_text += "    list tools          - 列出所有工具\n"
        help_text += "    tool stats          - 工具统计\n"
        help_text += "    history             - 查看命令历史\n\n"
        
        help_text += "  文件整理:\n"
        help_text += "    scan files          - 扫描文件问题\n"
        help_text += "    clean duplicates    - 清理重复文件\n"
        help_text += "    organize root       - 整理根目录\n\n"
        
        help_text += "  系统监控:\n"
        help_text += "    system health       - 系统健康检查\n"
        help_text += "    monitor             - 实时监控\n"
        help_text += "    security scan       - 安全扫描\n\n"
        
        help_text += "  研究相关:\n"
        help_text += "    research cnt        - CNT 研究\n"
        help_text += "    critic check        - 批判者检查\n"
        help_text += "    arxiv scan          - arXiv 扫描\n\n"
        
        help_text += "  备份恢复:\n"
        help_text += "    backup restructure  - 备份重构\n"
        help_text += "    disaster cleanup    - 灾难清理\n\n"
        
        help_text += "  Git Hooks:\n"
        help_text += "    install hooks       - 安装 Git Hooks\n"
        help_text += "    test hook           - 测试 Hook\n\n"
        
        help_text += "  快速访问:\n"
        help_text += "    quick health        - 快速健康检查\n"
        help_text += "    quick scan          - 快速文件扫描\n"
        help_text += "    status              - 会话状态\n"
        help_text += "    --stats             - 命令统计\n\n"
        
        help_text += "命令分类:\n"
        for category in COMMAND_CATEGORIES.keys():
            help_text += f"  {category}\n"
        
        help_text += "\n使用 'help <分类>' 查看分类命令。\n"
        help_text += "\n示例:\n"
        help_text += "  py unified_cli_v3.py \"scan tools\"\n"
        help_text += "  py unified_cli_v3.py \"system health\"\n"
        help_text += "  py unified_cli_v3.py --interactive\n"
        
        return help_text
    
    def interactive_mode(self):
        """Run interactive mode"""
        print("\n🎯 Unified CLI v3 - Interactive Mode")
        print("=" * 60)
        print("Type commands or 'quit' to exit")
        print("Use 'help' for available commands\n")
        
        while True:
            try:
                user_input = input("claw> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                if user_input.lower() == 'help':
                    print(self.get_help())
                    continue
                
                if user_input.lower().startswith('help '):
                    category = user_input.split(' ', 1)[1]
                    print(self.get_help(category))
                    continue
                
                # Parse command
                command = self.parse_command(user_input)
                
                if not command:
                    print(f"⚠️  Unknown command: {user_input}")
                    print("   Try 'help' for available commands\n")
                    continue
                
                print(f"\n▶️  Executing: {command}\n")
                
                # Execute
                result = self.execute(command)
                
                if result['success']:
                    print(result.get('stdout', ''))
                else:
                    print(f"❌ Error: {result.get('error', result.get('stderr', 'Unknown error'))}")
                
                print(f"\n⏱️  Duration: {result.get('duration_seconds', 0):.2f}s\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified CLI v3")
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Additional arguments')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--suggest', type=str, help='Get suggestions')
    parser.add_argument('--help-category', type=str, help='Help for category')
    parser.add_argument('--history', action='store_true', help='Show command history')
    parser.add_argument('--history-limit', type=int, default=10, help='History limit')
    parser.add_argument('--stats', action='store_true', help='Show command statistics')
    args = parser.parse_args()
    
    cli = UnifiedCLI()
    
    if args.interactive:
        cli.interactive_mode()
    
    elif args.suggest:
        suggestions = cli.suggest(args.suggest)
        print(f"\n💡 Suggestions for '{args.suggest}':\n")
        for s in suggestions:
            print(f"  {s}")
    
    elif args.history:
        print(cli.show_history(args.history_limit))
    
    elif args.stats:
        print(cli.show_stats())
    
    elif args.help_category:
        print(cli.get_help(args.help_category))
    
    elif args.command:
        # Handle 'help <category>' syntax
        if args.command.lower() == 'help' and args.args:
            print(cli.get_help(args.args[0]))
            sys.exit(0)
        
        # Handle 'history' command
        if args.command.lower() == 'history':
            limit = int(args.args[0]) if args.args else 10
            print(cli.show_history(limit))
            sys.exit(0)
        
        command = cli.parse_command(args.command)
        
        if not command:
            print(f"⚠️  Unknown command: {args.command}")
            print("\nTry 'python unified_cli_v3.py --help' for usage")
            sys.exit(1)
        
        print(f"▶️  Executing: {command}\n")
        
        result = cli.execute(command, args.args)
        
        if result['success']:
            print(result.get('stdout', ''))
            sys.exit(0)
        else:
            print(f"❌ Error: {result.get('error', result.get('stderr', 'Unknown error'))}")
            sys.exit(1)
    
    else:
        print(cli.get_help())

if __name__ == "__main__":
    main()
