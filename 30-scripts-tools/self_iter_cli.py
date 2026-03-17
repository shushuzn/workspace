#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Self-Iteration CLI - Unified Interface
Single command-line interface for all self-iteration tools
Features: 20 commands, colored output, progress tracking, help system

Usage:
    python self_iter_cli.py --help
    python self_iter_cli.py analyze
    python self_iter_cli.py evolve
    python self_iter_cli.py meta-learn
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Workspace root
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


class SelfIterationCLI:
    """Unified CLI for self-iteration system"""
    
    def __init__(self):
        self.tools_dir = WORKSPACE / "30-scripts-tools"
        self.tools = {
            'self_iteration': self.tools_dir / "self_iteration.py",
            'meta_learning': self.tools_dir / "meta_learning.py",
            'evolution_engine': self.tools_dir / "evolution_engine.py"
        }
    
    def _run_tool(self, tool_name: str, args: list) -> int:
        """Run a tool with arguments"""
        tool_path = self.tools.get(tool_name)
        if not tool_path or not tool_path.exists():
            print_error(f"Tool not found: {tool_name}")
            return 1
        
        cmd = [sys.executable, str(tool_path)] + args
        result = subprocess.run(cmd)
        return result.returncode
    
    def cmd_analyze(self, args):
        """Run system self-analysis"""
        print_header("System Self-Analysis")
        return self._run_tool('self_iteration', ['--analyze'])
    
    def cmd_plan(self, args):
        """Create improvement plan"""
        print_header("Improvement Planning")
        return self._run_tool('self_iteration', ['--plan'])
    
    def cmd_execute(self, args):
        """Execute improvements"""
        print_header("Improvement Execution")
        return self._run_tool('self_iteration', ['--execute'])
    
    def cmd_validate(self, args):
        """Validate improvements"""
        print_header("Improvement Validation")
        return self._run_tool('self_iteration', ['--validate'])
    
    def cmd_iterate(self, args):
        """Run full iteration cycle"""
        print_header("Full Iteration Cycle")
        return self._run_tool('self_iteration', ['--full-cycle'])
    
    def cmd_collect(self, args):
        """Collect learning events"""
        print_header("Learning Event Collection")
        return self._run_tool('meta_learning', ['--collect'])
    
    def cmd_patterns(self, args):
        """Analyze learning patterns"""
        print_header("Learning Pattern Analysis")
        return self._run_tool('meta_learning', ['--analyze'])
    
    def cmd_strategies(self, args):
        """Optimize learning strategies"""
        print_header("Learning Strategy Optimization")
        return self._run_tool('meta_learning', ['--optimize'])
    
    def cmd_meta(self, args):
        """Extract meta-knowledge"""
        print_header("Meta-Knowledge Extraction")
        return self._run_tool('meta_learning', ['--extract'])
    
    def cmd_meta_learn(self, args):
        """Run full meta-learning analysis"""
        print_header("Full Meta-Learning Analysis")
        return self._run_tool('meta_learning', ['--full'])
    
    def cmd_components(self, args):
        """Analyze system components"""
        print_header("Component Analysis")
        return self._run_tool('evolution_engine', ['--analyze'])
    
    def cmd_fitness(self, args):
        """Evaluate fitness"""
        print_header("Fitness Evaluation")
        return self._run_tool('evolution_engine', ['--evaluate'])
    
    def cmd_mutate(self, args):
        """Apply mutations"""
        print_header("Mutation Application")
        return self._run_tool('evolution_engine', ['--mutate'])
    
    def cmd_select(self, args):
        """Select fittest"""
        print_header("Selection Process")
        return self._run_tool('evolution_engine', ['--select'])
    
    def cmd_evolve(self, args):
        """Run evolution cycle"""
        print_header("Evolution Cycle")
        return self._run_tool('evolution_engine', ['--evolve'])
    
    def cmd_full(self, args):
        """Run complete self-iteration (all systems)"""
        print_header("Complete Self-Iteration")
        
        results = []
        
        # 1. Self-iteration
        print(f"\n{Colors.BOLD}[1/3] Self-Iteration{Colors.ENDC}")
        r1 = self._run_tool('self_iteration', ['--full-cycle'])
        results.append(('Self-Iteration', r1 == 0))
        
        # 2. Meta-learning
        print(f"\n{Colors.BOLD}[2/3] Meta-Learning{Colors.ENDC}")
        r2 = self._run_tool('meta_learning', ['--full'])
        results.append(('Meta-Learning', r2 == 0))
        
        # 3. Evolution
        print(f"\n{Colors.BOLD}[3/3] Evolution{Colors.ENDC}")
        r3 = self._run_tool('evolution_engine', ['--evolve'])
        results.append(('Evolution', r3 == 0))
        
        # Summary
        print_header("Self-Iteration Summary")
        for name, success in results:
            icon = '✅' if success else '❌'
            print(f"{icon} {name}")
        
        all_success = all(s for _, s in results)
        if all_success:
            print_success("All systems completed successfully!")
        else:
            print_warning("Some systems had issues")
        
        return 0 if all_success else 1
    
    def cmd_status(self, args):
        """Show status of all systems"""
        print_header("Self-Iteration System Status")
        
        # Self-iteration status
        print(f"\n{Colors.BOLD}Self-Iteration Engine:{Colors.ENDC}")
        self._run_tool('self_iteration', ['--status'])
        
        # Meta-learning status
        print(f"\n{Colors.BOLD}Meta-Learning System:{Colors.ENDC}")
        self._run_tool('meta_learning', ['--status'])
        
        # Evolution status
        print(f"\n{Colors.BOLD}Evolution Engine:{Colors.ENDC}")
        self._run_tool('evolution_engine', ['--status'])
    
    def cmd_report(self, args):
        """Generate self-iteration report"""
        print_header("Self-Iteration Report Generation")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = WORKSPACE / "20-data-reports" / f"self_iteration_report_{timestamp}.md"
        
        report = f"""# Self-Iteration Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Systems

### 1. Self-Iteration Engine
- Status: Active
- Capabilities: Self-analysis, improvement planning, auto-execution, validation

### 2. Meta-Learning System
- Status: Active
- Capabilities: Learning event collection, pattern analysis, strategy optimization, meta-knowledge extraction

### 3. Evolution Engine
- Status: Active
- Capabilities: Component analysis, fitness evaluation, mutation, selection, retention

## Usage

```bash
# Full self-iteration
python self_iter_cli.py full

# Individual systems
python self_iter_cli.py iterate      # Self-iteration cycle
python self_iter_cli.py meta-learn   # Meta-learning analysis
python self_iter_cli.py evolve       # Evolution cycle

# Status
python self_iter_cli.py status
```

## Files

- `self_iteration.py` - Core iteration engine
- `meta_learning.py` - Meta-learning system
- `evolution_engine.py` - Evolution engine
- `self_iter_cli.py` - Unified CLI

## Next Steps

1. Run `self_iter_cli.py full` for complete self-iteration
2. Review generated reports in `20-data-reports/`
3. Monitor improvement metrics
4. Adjust strategies based on meta-knowledge
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print_success(f"Report saved: {report_file}")
        print(report)
    
    def cmd_help(self, args):
        """Show help"""
        print_header("Self-Iteration CLI")
        
        print(f"""
{Colors.BOLD}Usage:{Colors.ENDC}
  self_iter_cli.py <command> [options]

{Colors.BOLD}Commands:{Colors.ENDC}
  {Colors.OKGREEN}analyze{Colors.ENDC}         Run system self-analysis
  {Colors.OKGREEN}plan{Colors.ENDC}            Create improvement plan
  {Colors.OKGREEN}execute{Colors.ENDC}         Execute improvements
  {Colors.OKGREEN}validate{Colors.ENDC}        Validate improvements
  {Colors.OKGREEN}iterate{Colors.ENDC}         Run full iteration cycle
  {Colors.OKGREEN}collect{Colors.ENDC}         Collect learning events
  {Colors.OKGREEN}patterns{Colors.ENDC}        Analyze learning patterns
  {Colors.OKGREEN}strategies{Colors.ENDC}      Optimize strategies
  {Colors.OKGREEN}meta{Colors.ENDC}            Extract meta-knowledge
  {Colors.OKGREEN}meta-learn{Colors.ENDC}      Full meta-learning analysis
  {Colors.OKGREEN}components{Colors.ENDC}      Analyze components
  {Colors.OKGREEN}fitness{Colors.ENDC}         Evaluate fitness
  {Colors.OKGREEN}mutate{Colors.ENDC}          Apply mutations
  {Colors.OKGREEN}select{Colors.ENDC}          Select fittest
  {Colors.OKGREEN}evolve{Colors.ENDC}          Run evolution cycle
  {Colors.OKGREEN}full{Colors.ENDC}            Complete self-iteration (all 3 systems)
  {Colors.OKGREEN}status{Colors.ENDC}          Show system status
  {Colors.OKGREEN}report{Colors.ENDC}          Generate report
  {Colors.OKGREEN}help{Colors.ENDC}            Show this help

{Colors.BOLD}Examples:{Colors.ENDC}
  self_iter_cli.py full           # Run everything
  self_iter_cli.py iterate        # Self-iteration only
  self_iter_cli.py meta-learn     # Meta-learning only
  self_iter_cli.py evolve         # Evolution only
  self_iter_cli.py status         # Check status
  self_iter_cli.py report         # Generate report
""")


def main():
    parser = argparse.ArgumentParser(description='Self-Iteration CLI', add_help=False)
    parser.add_argument('command', nargs='?', default='help', help='Command')
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    args, unknown = parser.parse_known_args()
    
    cli = SelfIterationCLI()
    
    if args.help or args.command == 'help':
        cli.cmd_help(args)
        return
    
    commands = {
        'analyze': cli.cmd_analyze,
        'plan': cli.cmd_plan,
        'execute': cli.cmd_execute,
        'validate': cli.cmd_validate,
        'iterate': cli.cmd_iterate,
        'collect': cli.cmd_collect,
        'patterns': cli.cmd_patterns,
        'strategies': cli.cmd_strategies,
        'meta': cli.cmd_meta,
        'meta-learn': cli.cmd_meta_learn,
        'components': cli.cmd_components,
        'fitness': cli.cmd_fitness,
        'mutate': cli.cmd_mutate,
        'select': cli.cmd_select,
        'evolve': cli.cmd_evolve,
        'full': cli.cmd_full,
        'status': cli.cmd_status,
        'report': cli.cmd_report
    }
    
    if args.command in commands:
        try:
            result = commands[args.command](args)
            sys.exit(result if isinstance(result, int) else 0)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Interrupted{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Command failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print_error(f"Unknown command: {args.command}")
        print_info("Use 'self_iter_cli.py help' for available commands")
        sys.exit(1)


if __name__ == "__main__":
    main()
