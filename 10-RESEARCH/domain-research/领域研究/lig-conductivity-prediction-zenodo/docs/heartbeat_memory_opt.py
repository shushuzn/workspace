#!/usr/bin/env python3
"""
Heartbeat Memory Optimization
Automatic memory optimization for HEARTBEAT tasks

Runs every 30 minutes to:
1. Optimize memory for all workflows
2. Run garbage collection
3. Update cache statistics
4. Report memory health

Usage:
  python heartbeat_memory_opt.py
  python heartbeat_memory_opt.py --status
  python heartbeat_memory_opt.py --gc
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import argparse
from datetime import datetime
import os

# Import memory systems
from memory_integration import (
    MemoryIntegrationLayer,
    MemoryIntegrationConfig,
    setup_default_workflows
)
from dynamic_memory_allocation import MemoryPriority


def optimize_for_heartbeat():
    """Run memory optimization for HEARTBEAT"""

    print("\n" + "=" *80)
    print("🔔 HEARTBEAT Memory Optimization")
    print("=" *80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")

    # Initialize integration layer
    config = MemoryIntegrationConfig(
        enabled=True,
        total_capacity_mb=512,
        auto_gc=True,
        gc_threshold=0.7,  # Aggressive GC for heartbeat
        prefetch_enabled=True
    )

    integration = MemoryIntegrationLayer(config)
    setup_default_workflows(integration)

    # Optimize each workflow
    print("\n" + "=" *80)
    print("Workflow Memory Optimization")
    print("=" *80)

    optimization_results = []

    workflows = [
        "arxiv_research",
        "memory_distillation",
        "7_persona_collaboration",
        "knowledge_graph",
        "heartbeat_tasks",
        "data_collection",
        "code_generation",
        "report_generation"
    ]

    for workflow in workflows:
        result = integration.optimize_workflow_memory(workflow)
        optimization_results.append(result)

        # Show summary for workflows with activity
        if result.gc_triggered or result.blocks_evicted > 0:
            print(f"\n  {workflow}:")
            print(f"    Memory: {result.memory_before_mb:.2f} → {result.memory_after_mb:.2f} MB ({result.reduction_percent:.1f}%)")
            print(f"    GC: {'Triggered' if result.gc_triggered else 'Skipped'}, {result.blocks_evicted} blocks evicted")

    # Overall statistics
    print("\n" + "=" *80)
    print("Overall Memory Statistics")
    print("=" *80)

    status = integration.get_integration_status()

    print(f"\n  📊 Memory Status:")
    print(f"     Total Capacity: {status['total_capacity_mb']} MB")
    print(f"     Utilization: {status['utilization']:.0%}")
    print(f"     L1 (Hot):  {status['l1_usage']:.0%}")
    print(f"     L2 (Warm): {status['l2_usage']:.0%}")
    print(f"     L3 (Cold): {status['l3_usage']:.0%}")

    print(f"\n  ⚡ Performance:")
    print(f"     Cache Hit Rate: {status['cache_hit_rate']:.0%}")
    print(f"     Avg Access Time: {status['avg_access_time_ms']:.2f}ms")

    print(f"\n  🔗 Integration Status:")
    print(f"     Registered Workflows: {status['registered_workflows']}")
    print(f"     Optimizations Run: {status['optimizations_run']}")

    # Calculate improvements
    total_memory_before = sum(r.memory_before_mb for r in optimization_results)
    total_memory_after = sum(r.memory_after_mb for r in optimization_results)
    total_reduction = ((total_memory_before - total_memory_after) / total_memory_before * 100) if total_memory_before > 0 else 0

    total_gc_triggered = sum(1 for r in optimization_results if r.gc_triggered)
    total_blocks_evicted = sum(r.blocks_evicted for r in optimization_results)

    print(f"\n  📈 Optimization Summary:")
    print(f"     Total Memory: {total_memory_before:.2f} → {total_memory_after:.2f} MB ({total_reduction:.1f}% reduction)")
    print(f"     GC Triggered: {total_gc_triggered}/{len(workflows)} workflows")
    print(f"     Blocks Evicted: {total_blocks_evicted}")

    # Save heartbeat state
    os.makedirs("13-memory", exist_ok=True)
    heartbeat_state = {
        "timestamp": datetime.now().isoformat(),
        "optimization_results": [
            {
                "workflow": r.workflow,
                "memory_before_mb": r.memory_before_mb,
                "memory_after_mb": r.memory_after_mb,
                "reduction_percent": r.reduction_percent,
                "gc_triggered": r.gc_triggered,
                "blocks_evicted": r.blocks_evicted
            }
            for r in optimization_results
        ],
        "overall_status": status,
        "improvements": {
            "total_memory_reduction_mb": total_memory_before - total_memory_after,
            "total_memory_reduction_percent": total_reduction,
            "total_gc_triggered": total_gc_triggered,
            "total_blocks_evicted": total_blocks_evicted
        }
    }

    state_file = "13-memory/heartbeat-memory-state.json"
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(heartbeat_state, f, indent=2, ensure_ascii=False)

    print(f"\n💾 State saved to: {state_file}")

    # Export detailed stats
    integration.export_stats("data/heartbeat_memory_stats.json")

    # Health check
    print("\n" + "=" *80)
    print("Memory Health Check")
    print("=" *80)

    health_status = "✅ HEALTHY"
    health_issues = []

    if status['utilization'] > 0.9:
        health_status = "⚠️ CRITICAL"
        health_issues.append("High memory utilization (>90%)")

    if status['cache_hit_rate'] < 0.7:
        health_status = "⚠️ WARNING"
        health_issues.append("Low cache hit rate (<70%)")

    if status['avg_access_time_ms'] > 10:
        health_status = "⚠️ WARNING"
        health_issues.append("High access latency (>10ms)")

    print(f"\n  Overall Health: {health_status}")

    if health_issues:
        print(f"\n  ⚠️ Issues Detected:")
        for issue in health_issues:
            print(f"     - {issue}")
    else:
        print(f"\n  ✅ All metrics within healthy ranges")

    print("\n" + "=" *80)
    print("✅ HEARTBEAT Memory Optimization Complete!")
    print("=" *80)

    return heartbeat_state


def show_status():
    """Show current memory status"""

    print("\n" + "=" *80)
    print("📊 Memory Status (HEARTBEAT)")
    print("=" *80)

    # Load last state
    state_file = "13-memory/heartbeat-memory-state.json"

    if not os.path.exists(state_file):
        print("\n⚠️ No previous heartbeat state found. Run optimization first.")
        return

    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    print(f"\n⏰ Last Optimization: {state['timestamp']}")

    print(f"\n📈 Overall Status:")
    status = state['overall_status']
    print(f"   Utilization: {status['utilization']:.0%}")
    print(f"   Cache Hit Rate: {status['cache_hit_rate']:.0%}")
    print(f"   Avg Access Time: {status['avg_access_time_ms']:.2f}ms")

    print(f"\n📊 Improvements:")
    improvements = state['improvements']
    print(f"   Memory Reduction: {improvements['total_memory_reduction_mb']:.2f} MB ({improvements['total_memory_reduction_percent']:.1f}%)")
    print(f"   GC Triggered: {improvements['total_gc_triggered']} workflows")
    print(f"   Blocks Evicted: {improvements['total_blocks_evicted']}")


def force_gc():
    """Force garbage collection"""

    print("\n" + "=" *80)
    print("🧹 Forced Garbage Collection")
    print("=" *80)

    config = MemoryIntegrationConfig(
        enabled=True,
        total_capacity_mb=512,
        auto_gc=False  # Manual GC
    )

    integration = MemoryIntegrationLayer(config)
    setup_default_workflows(integration)

    # Run GC on all tiers
    gc_results = integration.allocator.run_gc()

    print(f"\n  GC Results:")
    for result in gc_results:
        print(f"    {result.tier.upper()}: {result.blocks_collected} blocks, {result.bytes_freed:,} bytes freed")

    total_freed = sum(r.bytes_freed for r in gc_results)
    print(f"\n  Total Freed: {total_freed:,} bytes ({total_freed / 1024 / 1024:.2f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Heartbeat Memory Optimization")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--gc", action="store_true", help="Force garbage collection")
    parser.add_argument("--optimize", action="store_true", help="Run optimization (default)")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.gc:
        force_gc()
    else:
        optimize_for_heartbeat()


if __name__ == "__main__":
    main()
