import os
from pathlib import Path

SCRIPTS_DIR = Path(r'D:\OpenClaw\workspace\30-scripts-tools')

renames = [
    ('memory-dashboard.py', 'memory_dashboard_v1.py'),
    ('memory-distiller.py', 'memory_distiller_v1.py'),
    ('memory-llm-distiller.py', 'memory_distiller_llm.py'),
    ('memory-maintenance.py', 'memory_engine_maintenance.py'),
    ('memory-ops.py', 'memory_engine_ops.py'),
    ('memory-quality-assessor.py', 'memory_quality_assessor.py'),
    ('memory-quality-scorer.py', 'memory_quality_scorer_v1.py'),
    ('memory-search-v2.py', 'memory_search_v2.py'),
    ('memory-forgetting.py', 'memory_forgetting_v1.py'),
    ('memory_auto_fix.py', 'memory_fix_auto.py'),
    ('memory_ultimate_fix.py', 'memory_fix_ultimate.py'),
    ('memory_autonomous_engine.py', 'memory_engine_autonomous.py'),
    ('memory_orchestrator.py', 'memory_engine_orchestrator.py'),
    ('memory_evolution_engine.py', 'memory_engine_evolution.py'),
    ('memory_association.py', 'memory_association_basic.py'),
    ('multi_agent_memory.py', 'memory_multi_agent.py'),
    ('federated_memory.py', 'memory_federated.py'),
    ('memory_persona_agents.py', 'memory_persona.py'),
    ('dynamic_memory_allocation.py', 'memory_perf_allocation.py'),
    ('memory_prefetcher.py', 'memory_perf_prefetch.py'),
    ('memory_performance_profiler.py', 'memory_perf_profiler.py'),
    ('memory_audit_logger.py', 'memory_util_audit.py'),
    ('memory_health_monitor.py', 'memory_util_health.py'),
    ('memory_indexer.py', 'memory_util_indexer.py'),
    ('test_memory_integration.py', 'memory_test_integration.py'),
]

done = 0
for old, new in renames:
    old_path = SCRIPTS_DIR / old
    new_path = SCRIPTS_DIR / new
    if old_path.exists():
        if not new_path.exists():
            old_path.rename(new_path)
            print(f'OK: {old} -> {new}')
            done += 1
        else:
            print(f'SKIP: {new} exists')
    else:
        print(f'NOT FOUND: {old}')

print(f'\nTotal renamed: {done}/{len(renames)}')
