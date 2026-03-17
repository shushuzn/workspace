#!/usr/bin/env python3
"""
Memory Orchestrator - Unified Control System
=============================================
Phase 4 Innovation (P4-1)

Central orchestration engine coordinating all 14 memory evolution tools.

Features:
- Unified CLI interface
- Tool chaining (immune → neural → dark_matter → ...)
- Dependency management
- Result aggregation
- Error handling & recovery

Usage:
```bash
# Run full analysis pipeline
python memory_orchestrator.py run-full "MEMORY.md"

# Run custom pipeline
python memory_orchestrator.py run-pipeline immune,neural,dark_matter "MEMORY.md"

# Check system status
python memory_orchestrator.py status --all

# Run specific tool
python memory_orchestrator.py run-tool memory_immune_system.py "MEMORY.md"
```
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ToolConfig:
    """Configuration for a single tool"""
    name: str
    script: str
    phase: str
    priority: int
    timeout: int = 300  # seconds
    required: bool = False
    dependencies: List[str] = field(default_factory=list)


# Tool registry - all 14 innovation tools
TOOL_REGISTRY: Dict[str, ToolConfig] = {
    # Core Evolution (Phase 0)
    'evolution': ToolConfig(
        name='Memory Evolution Engine',
        script='memory_evolution_engine.py',
        phase='core',
        priority=1,
        timeout=300
    ),
    'quality': ToolConfig(
        name='Memory Quality Scorer',
        script='memory_quality_scorer.py',
        phase='core',
        priority=2,
        timeout=180
    ),
    'forgetting': ToolConfig(
        name='Memory Forgetting',
        script='memory_forgetting.py',
        phase='core',
        priority=3,
        timeout=180
    ),
    'association': ToolConfig(
        name='Memory Association',
        script='memory_association.py',
        phase='core',
        priority=4,
        timeout=180
    ),
    'conflict': ToolConfig(
        name='Memory Conflict Detector',
        script='memory_conflict_detector.py',
        phase='core',
        priority=5,
        timeout=180
    ),
    
    # P0: Biological (Phase 0)
    'immune': ToolConfig(
        name='Memory Immune System',
        script='memory_immune_system.py',
        phase='P0',
        priority=10,
        timeout=300
    ),
    'neural': ToolConfig(
        name='Memory Neural Network',
        script='memory_neural_network.py',
        phase='P0',
        priority=11,
        timeout=300
    ),
    
    # P1: Physics & Math (Phase 1)
    'dark_matter': ToolConfig(
        name='Memory Dark Matter',
        script='memory_dark_matter.py',
        phase='P1',
        priority=20,
        timeout=300
    ),
    'topology': ToolConfig(
        name='Memory Topological Analysis',
        script='memory_topological_analysis.py',
        phase='P1',
        priority=21,
        timeout=300
    ),
    'thermo': ToolConfig(
        name='Memory Thermodynamics',
        script='memory_thermodynamics.py',
        phase='P1',
        priority=22,
        timeout=300
    ),
    'fractal': ToolConfig(
        name='Memory Fractal Compression',
        script='memory_fractal_compression.py',
        phase='P1',
        priority=23,
        timeout=300
    ),
    'causal': ToolConfig(
        name='Memory Causal Discovery',
        script='memory_causal_discovery.py',
        phase='P1',
        priority=24,
        timeout=300
    ),
    
    # P2: Quantum & Time (Phase 2)
    'quantum': ToolConfig(
        name='Memory Quantum Entanglement',
        script='memory_quantum_entanglement.py',
        phase='P2',
        priority=30,
        timeout=300
    ),
    'time_crystal': ToolConfig(
        name='Memory Time Crystal',
        script='memory_time_crystal.py',
        phase='P2',
        priority=31,
        timeout=300
    ),
    
    # P3: Consciousness (Phase 3)
    'consciousness': ToolConfig(
        name='Memory Consciousness Emergence',
        script='memory_consciousness_emergence.py',
        phase='P3',
        priority=40,
        timeout=300
    ),
}

# Default pipelines
PIPELINES = {
    'full': list(TOOL_REGISTRY.keys()),
    'core': ['evolution', 'quality', 'forgetting', 'association', 'conflict'],
    'p0': ['immune', 'neural'],
    'p1': ['dark_matter', 'topology', 'thermo', 'fractal', 'causal'],
    'p2': ['quantum', 'time_crystal'],
    'p3': ['consciousness'],
    'quick': ['evolution', 'quality', 'immune', 'dark_matter'],
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ToolResult:
    """Result from running a tool"""
    tool_id: str
    tool_name: str
    phase: str
    success: bool
    duration: float  # seconds
    exit_code: int = 0
    output: str = ""
    error: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PipelineResult:
    """Result from running a pipeline"""
    pipeline_name: str
    target_file: str
    start_time: str
    end_time: str
    total_duration: float
    tools_run: int
    tools_succeeded: int
    tools_failed: int
    results: List[ToolResult] = field(default_factory=list)
    aggregated_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# Memory Orchestrator Engine
# ============================================================================

class MemoryOrchestrator:
    """Central orchestration engine for memory evolution tools"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize orchestrator"""
        if workspace_path is None:
            # Default to D:\OpenClaw\workspace
            self.workspace = Path(r'D:\OpenClaw\workspace')
        else:
            self.workspace = Path(workspace_path)
        
        self.tools_dir = self.workspace / '30-scripts-tools'
        self.data_dir = self.workspace / 'data'
        self.reports_dir = self.workspace / '30-scripts-tools' / 'reports'
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Memory Orchestrator initialized at {self.workspace}")
    
    def run_tool(self, tool_id: str, target_file: str, 
                 extra_args: Optional[List[str]] = None) -> ToolResult:
        """Run a single tool"""
        import subprocess
        
        if tool_id not in TOOL_REGISTRY:
            error_msg = f"Unknown tool: {tool_id}"
            logger.error(error_msg)
            return ToolResult(
                tool_id=tool_id,
                tool_name="Unknown",
                phase="Unknown",
                success=False,
                duration=0.0,
                error=error_msg
            )
        
        config = TOOL_REGISTRY[tool_id]
        script_path = self.tools_dir / config.script
        
        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            logger.error(error_msg)
            return ToolResult(
                tool_id=tool_id,
                tool_name=config.name,
                phase=config.phase,
                success=False,
                duration=0.0,
                error=error_msg
            )
        
        # Build command
        cmd = [sys.executable, str(script_path)]
        
        # Add target file
        if target_file:
            cmd.append(target_file)
        
        # Add extra arguments
        if extra_args:
            cmd.extend(extra_args)
        
        logger.info(f"Running {config.name}...")
        start_time = time.time()
        
        try:
            # Run tool
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            tool_result = ToolResult(
                tool_id=tool_id,
                tool_name=config.name,
                phase=config.phase,
                success=success,
                duration=duration,
                exit_code=result.returncode,
                output=result.stdout[-10000:] if result.stdout else "",  # Limit output
                error=result.stderr[-5000:] if result.stderr else ""
            )
            
            if success:
                logger.info(f"✓ {config.name} completed in {duration:.2f}s")
            else:
                logger.error(f"✗ {config.name} failed with code {result.returncode}")
            
            return tool_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Timeout after {config.timeout}s"
            logger.error(error_msg)
            return ToolResult(
                tool_id=tool_id,
                tool_name=config.name,
                phase=config.phase,
                success=False,
                duration=duration,
                error=error_msg
            )
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Exception: {str(e)}"
            logger.error(error_msg)
            return ToolResult(
                tool_id=tool_id,
                tool_name=config.name,
                phase=config.phase,
                success=False,
                duration=duration,
                error=error_msg
            )
    
    def run_pipeline(self, pipeline_name: str, target_file: str,
                     tool_ids: Optional[List[str]] = None) -> PipelineResult:
        """Run a pipeline of tools"""
        
        if tool_ids is None:
            if pipeline_name not in PIPELINES:
                raise ValueError(f"Unknown pipeline: {pipeline_name}")
            tool_ids = PIPELINES[pipeline_name]
        
        logger.info(f"Starting pipeline '{pipeline_name}' with {len(tool_ids)} tools")
        start_time = datetime.now()
        
        results: List[ToolResult] = []
        tools_succeeded = 0
        tools_failed = 0
        
        for tool_id in tool_ids:
            result = self.run_tool(tool_id, target_file)
            results.append(result)
            
            if result.success:
                tools_succeeded += 1
            else:
                tools_failed += 1
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Aggregate metrics
        aggregated_metrics = self._aggregate_metrics(results)
        
        pipeline_result = PipelineResult(
            pipeline_name=pipeline_name,
            target_file=target_file,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration=total_duration,
            tools_run=len(tool_ids),
            tools_succeeded=tools_succeeded,
            tools_failed=tools_failed,
            results=results,
            aggregated_metrics=aggregated_metrics
        )
        
        logger.info(f"Pipeline '{pipeline_name}' completed: "
                   f"{tools_succeeded}/{len(tool_ids)} tools succeeded in {total_duration:.2f}s")
        
        return pipeline_result
    
    def _aggregate_metrics(self, results: List[ToolResult]) -> Dict[str, Any]:
        """Aggregate metrics from all tool results"""
        metrics = {
            'total_tools': len(results),
            'successful': sum(1 for r in results if r.success),
            'failed': sum(1 for r in results if not r.success),
            'total_duration': sum(r.duration for r in results),
            'by_phase': {}
        }
        
        # Group by phase
        for result in results:
            phase = result.phase
            if phase not in metrics['by_phase']:
                metrics['by_phase'][phase] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            metrics['by_phase'][phase]['total'] += 1
            if result.success:
                metrics['by_phase'][phase]['successful'] += 1
            else:
                metrics['by_phase'][phase]['failed'] += 1
        
        return metrics
    
    def get_status(self, tool_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get status of all tools"""
        
        if tool_ids is None:
            tool_ids = list(TOOL_REGISTRY.keys())
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'workspace': str(self.workspace),
            'tools': {}
        }
        
        for tool_id in tool_ids:
            if tool_id not in TOOL_REGISTRY:
                continue
            
            config = TOOL_REGISTRY[tool_id]
            script_path = self.tools_dir / config.script
            
            status['tools'][tool_id] = {
                'name': config.name,
                'phase': config.phase,
                'priority': config.priority,
                'exists': script_path.exists(),
                'script': str(script_path)
            }
        
        return status
    
    def save_report(self, result: PipelineResult, filename: Optional[str] = None) -> str:
        """Save pipeline result to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"orchestrator_report_{timestamp}.json"
        
        report_path = self.reports_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved to {report_path}")
        return str(report_path)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Memory Orchestrator - Unified Control System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run-full "MEMORY.md"
  %(prog)s run-pipeline p0,p1 "MEMORY.md"
  %(prog)s run-tool memory_immune_system.py "MEMORY.md"
  %(prog)s status --all
  %(prog)s list-pipelines
  %(prog)s list-tools
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # run-full command
    run_full_parser = subparsers.add_parser('run-full', help='Run full analysis pipeline')
    run_full_parser.add_argument('target', help='Target file to analyze')
    run_full_parser.add_argument('--save', action='store_true', help='Save report to file')
    
    # run-pipeline command
    run_pipeline_parser = subparsers.add_parser('run-pipeline', help='Run custom pipeline')
    run_pipeline_parser.add_argument('pipeline', help='Pipeline name or comma-separated tool IDs')
    run_pipeline_parser.add_argument('target', help='Target file to analyze')
    run_pipeline_parser.add_argument('--save', action='store_true', help='Save report to file')
    
    # run-tool command
    run_tool_parser = subparsers.add_parser('run-tool', help='Run single tool')
    run_tool_parser.add_argument('tool', help='Tool script name')
    run_tool_parser.add_argument('target', help='Target file to analyze')
    run_tool_parser.add_argument('--args', nargs='*', help='Additional arguments')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    status_parser.add_argument('--all', action='store_true', help='Show all tools')
    status_parser.add_argument('--phase', choices=['core', 'P0', 'P1', 'P2', 'P3'],
                              help='Filter by phase')
    
    # list-pipelines command
    subparsers.add_parser('list-pipelines', help='List available pipelines')
    
    # list-tools command
    subparsers.add_parser('list-tools', help='List available tools')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = MemoryOrchestrator()
    
    # Execute command
    if args.command == 'run-full':
        logger.info("Running full pipeline...")
        result = orchestrator.run_pipeline('full', args.target)
        print_pipeline_result(result)
        
        if args.save:
            report_path = orchestrator.save_report(result)
            print(f"\nReport saved to: {report_path}")
    
    elif args.command == 'run-pipeline':
        # Check if pipeline name or custom tools
        if ',' in args.pipeline:
            tool_ids = [t.strip() for t in args.pipeline.split(',')]
            pipeline_name = 'custom'
        else:
            pipeline_name = args.pipeline
            tool_ids = None
        
        logger.info(f"Running pipeline '{pipeline_name}'...")
        result = orchestrator.run_pipeline(pipeline_name, args.target, tool_ids)
        print_pipeline_result(result)
        
        if args.save:
            report_path = orchestrator.save_report(result)
            print(f"\nReport saved to: {report_path}")
    
    elif args.command == 'run-tool':
        # Extract tool ID from script name
        tool_id = args.tool.replace('memory_', '').replace('.py', '')
        if tool_id == 'consciousness_emergence':
            tool_id = 'consciousness'
        elif tool_id == 'time_crystal':
            tool_id = 'time_crystal'
        
        logger.info(f"Running tool {tool_id}...")
        result = orchestrator.run_tool(tool_id, args.target, args.args)
        print_tool_result(result)
    
    elif args.command == 'status':
        tool_ids = None
        if args.phase:
            tool_ids = [tid for tid, config in TOOL_REGISTRY.items() 
                       if config.phase == args.phase]
        
        status = orchestrator.get_status(tool_ids)
        print_status(status, args.all or args.phase is not None)
    
    elif args.command == 'list-pipelines':
        print("\nAvailable Pipelines:")
        print("=" * 60)
        for name, tools in PIPELINES.items():
            print(f"\n{name}:")
            print(f"  Tools: {', '.join(tools)}")
            print(f"  Count: {len(tools)}")
    
    elif args.command == 'list-tools':
        print("\nAvailable Tools:")
        print("=" * 60)
        for tool_id, config in sorted(TOOL_REGISTRY.items(), key=lambda x: x[1].priority):
            print(f"\n{tool_id}:")
            print(f"  Name: {config.name}")
            print(f"  Phase: {config.phase}")
            print(f"  Priority: {config.priority}")
            print(f"  Script: {config.script}")
            print(f"  Timeout: {config.timeout}s")


def print_tool_result(result: ToolResult):
    """Print tool result"""
    print("\n" + "=" * 60)
    print(f"Tool: {result.tool_name}")
    print(f"Phase: {result.phase}")
    print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Exit Code: {result.exit_code}")
    
    if result.output:
        print("\nOutput:")
        print(result.output)
    
    if result.error:
        print("\nError:")
        print(result.error)
    
    print("=" * 60)


def print_pipeline_result(result: PipelineResult):
    """Print pipeline result"""
    print("\n" + "=" * 60)
    print(f"Pipeline: {result.pipeline_name}")
    print(f"Target: {result.target_file}")
    print(f"Duration: {result.total_duration:.2f}s")
    print(f"Tools: {result.tools_succeeded}/{result.tools_run} succeeded")
    print(f"Success Rate: {result.tools_succeeded/result.tools_run*100:.1f}%")
    
    print("\nResults by Phase:")
    for phase, metrics in result.aggregated_metrics.get('by_phase', {}).items():
        print(f"  {phase}: {metrics['successful']}/{metrics['total']}")
    
    print("=" * 60)


def print_status(status: Dict, verbose: bool = False):
    """Print system status"""
    print("\n" + "=" * 60)
    print("Memory Orchestrator Status")
    print("=" * 60)
    print(f"Timestamp: {status['timestamp']}")
    print(f"Workspace: {status['workspace']}")
    print(f"Total Tools: {len(status['tools'])}")
    
    if verbose:
        print("\nTools:")
        for tool_id, info in status['tools'].items():
            exists_str = "✅" if info['exists'] else "❌"
            print(f"  {exists_str} {tool_id}: {info['name']} ({info['phase']})")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
