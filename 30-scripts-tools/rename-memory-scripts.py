#!/usr/bin/env python3
"""
Memory Scripts Renamer - Standardize naming convention
"""

import os
import shutil
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

# Rename mapping: old_name_pattern -> new_name
RENAME_MAP = {
    # Distiller scripts
    'memory-distiller.py': 'memory_distiller_v1.py',
    'memory_distiller_v2.py': 'memory_distiller_v2.py',  # Keep
    'memory-llm-distiller.py': 'memory_distiller_llm.py',
    'memory_distillation_runner.py': 'memory_distiller_runner.py',
    
    # Quality scorers
    'memory-quality-assessor.py': 'memory_quality_assessor.py',
    'memory-quality-scorer.py': 'memory_quality_scorer_v1.py',
    'memory_quality_scorer.py': 'memory_quality_scorer_v2.py',
    
    # Search scripts
    'memory-search-v2.py': 'memory_search_v2.py',
    'memory_search_cached.py': 'memory_search_cached.py',  # Keep
    'ultimate_memory_search.py': 'memory_search_ultimate_v1.py',
    'ultimate_memory_search_v2.py': 'memory_search_ultimate_v2.py',
    'ultimate_memory_search_v3.py': 'memory_search_ultimate_v3.py',
    'ultra_fast_memory_search.py': 'memory_search_fast.py',
    
    # Dashboard
    'memory-dashboard.py': 'memory_dashboard_v1.py',
    'memory_dashboard_v2.py': 'memory_dashboard_v2.py',  # Keep
    
    # Forgetting
    'memory-forgetting.py': 'memory_forgetting_v1.py',
    'memory_forgetting.py': 'memory_forgetting_v2.py',
    'memory_forgetting_execute.py': 'memory_forgetting_executor.py',
    
    # Fix scripts
    'memory_auto_fix.py': 'memory_fix_auto.py',
    'memory_ultimate_fix.py': 'memory_fix_ultimate.py',
    'fix_memory_complete.py': 'memory_fix_complete.py',
    'fix_memory_encoding.py': 'memory_fix_encoding.py',
    
    # Core engines
    'memory_autonomous_engine.py': 'memory_engine_autonomous.py',
    'memory_orchestrator.py': 'memory_engine_orchestrator.py',
    'memory_ops.py': 'memory_engine_ops.py',
    'memory_maintenance.py': 'memory_engine_maintenance.py',
    'memory_evolution_engine.py': 'memory_engine_evolution.py',
    
    # Conflict
    'memory_conflict_detector.py': 'memory_conflict_detector.py',  # Keep
    'memory_conflict_resolver.py': 'memory_conflict_resolver.py',  # Keep
    
    # Association
    'memory_association.py': 'memory_association_basic.py',
    'memory_kg_extractor.py': 'memory_association_kg.py',
    'memory_causal_discovery.py': 'memory_association_causal.py',
    'memory_topological_analysis.py': 'memory_association_topology.py',
    
    # Experimental
    'memory_quantum_entanglement.py': 'memory_exp_quantum.py',
    'memory_time_crystal.py': 'memory_exp_time_crystal.py',
    'memory_thermodynamics.py': 'memory_exp_thermodynamics.py',
    'memory_consciousness_emergence.py': 'memory_exp_consciousness.py',
    'memory_dark_matter.py': 'memory_exp_dark_matter.py',
    'memory_fractal_compression.py': 'memory_exp_fractal.py',
    'memory_predictive_coding.py': 'memory_exp_predictive.py',
    'memory_neural_network.py': 'memory_exp_neural.py',
    'memory_self_improving_engine.py': 'memory_exp_self_improving.py',
    'memory_evolutionary_algorithms.py': 'memory_exp_evolutionary.py',
    
    # Multi-agent
    'multi_agent_memory.py': 'memory_multi_agent.py',
    'federated_memory.py': 'memory_federated.py',
    'memory_persona_agents.py': 'memory_persona.py',
    
    # Performance
    'dynamic_memory_allocation.py': 'memory_perf_allocation.py',
    'memory_prefetcher.py': 'memory_perf_prefetch.py',
    'memory_performance_profiler.py': 'memory_perf_profiler.py',
    
    # Utilities
    'memory_audit_logger.py': 'memory_util_audit.py',
    'memory_health_monitor.py': 'memory_util_health.py',
    'memory_indexer.py': 'memory_util_indexer.py',
    'test_memory_integration.py': 'memory_test_integration.py',
    'test_memory_distillation_v2.py': 'memory_test_distillation.py',
}

def rename_scripts():
    """Rename scripts according to convention"""
    
    print("=" * 80)
    print("MEMORY SCRIPTS RENAMING")
    print("=" * 80)
    
    renamed = []
    errors = []
    
    for old_name, new_name in RENAME_MAP.items():
        old_path = SCRIPTS_DIR / old_name
        new_path = SCRIPTS_DIR / new_name
        
        if old_path.exists():
            if new_path.exists() and old_name != new_name:
                print(f"⚠️  SKIP: {new_name} already exists")
                continue
            
            try:
                # Rename file
                shutil.move(str(old_path), str(new_path))
                renamed.append((old_name, new_name))
                print(f"✅ RENAMED: {old_name} → {new_name}")
            except Exception as e:
                errors.append((old_name, str(e)))
                print(f"❌ ERROR: {old_name} → {e}")
        else:
            print(f"⚠️  NOT FOUND: {old_name}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Renamed: {len(renamed)} scripts")
    print(f"Errors: {len(errors)}")
    
    if renamed:
        print(f"\n📋 RENAMED LIST:")
        for old, new in renamed:
            print(f"  {old} → {new}")
    
    return renamed, errors

if __name__ == '__main__':
    rename_scripts()
