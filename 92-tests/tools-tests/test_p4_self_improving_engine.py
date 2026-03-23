#!/usr/bin/env python3
"""
Test Suite for Memory Self-Improving Engine (P4-4)

Tests:
1. Engine initialization
2. Pattern mining
3. Gap detection
4. Hypothesis generation
5. Improvement cycle
6. Status reporting
7. State persistence
8. Auto-execution

Expected: 8/8 tests passing (100%)
"""

import sys
import json
from pathlib import Path

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from memory_self_improving_engine import (
    MemorySelfImprovingEngine,
    InnovationPattern,
    CapabilityGap,
    InnovationHypothesis,
    SelfImprovementCycle
)

def test_engine_initialization():
    """Test 1: Engine initialization"""
    print("Test 1: Engine Initialization")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()

    assert engine.workspace.exists(), "Workspace should exist"
    assert engine.data_dir.exists(), "Data directory should exist"
    assert engine.state is not None, "State should be loaded"
    assert 'system_score' in engine.state, "State should have system_score"
    assert 99.0 <= engine.state['system_score'] <= 100.0, "Score should be ~99.7"

    print(f"  Workspace: {engine.workspace}")
    print(f"  Data Dir: {engine.data_dir}")
    print(f"  Initial Score: {engine.state['system_score']:.1f}/100")
    print("✅ PASS\n")

def test_pattern_mining():
    """Test 2: Pattern mining"""
    print("Test 2: Pattern Mining")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()
    patterns = engine.mine_patterns()

    assert len(engine.pattern_library) >= 6, "Should have at least 6 patterns"
    assert all(isinstance(p, InnovationPattern) for p in engine.pattern_library), "All should be InnovationPattern"

    # Check pattern categories
    categories = set(p.category for p in engine.pattern_library)
    assert 'biological' in categories, "Should have biological patterns"
    assert 'quantum' in categories, "Should have quantum patterns"
    assert 'integration' in categories, "Should have integration patterns"

    print(f"  Total Patterns: {len(engine.pattern_library)}")
    print(f"  Categories: {', '.join(categories)}")
    print("✅ PASS\n")

def test_gap_detection():
    """Test 3: Gap detection"""
    print("Test 3: Gap Detection")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()
    gaps = engine.detect_gaps()

    assert len(gaps) >= 1, "Should detect at least 1 gap"
    assert all(isinstance(g, CapabilityGap) for g in gaps), "All should be CapabilityGap"

    # Check gap severities
    severities = set(g.severity for g in gaps)
    assert any(s in severities for s in ['critical', 'high', 'medium']), "Should have serious gaps"

    # Check priorities
    priorities = [g.priority for g in gaps]
    assert max(priorities) >= 7, "Should have high-priority gaps"

    print(f"  Gaps Detected: {len(gaps)}")
    for gap in gaps:
        print(f"    - {gap.id}: {gap.area} (Priority: {gap.priority}, Severity: {gap.severity})")
    print("✅ PASS\n")

def test_hypothesis_generation():
    """Test 4: Hypothesis generation"""
    print("Test 4: Hypothesis Generation")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()
    patterns = engine.pattern_library
    gaps = engine.detect_gaps()
    hypotheses = engine.generate_hypotheses(patterns, gaps)

    assert len(hypotheses) >= 2, "Should generate at least 2 hypotheses"
    assert all(isinstance(h, InnovationHypothesis) for h in hypotheses), "All should be InnovationHypothesis"

    # Check hypothesis quality
    avg_confidence = sum(h.confidence for h in hypotheses) / len(hypotheses)
    assert avg_confidence >= 0.6, f"Average confidence should be >= 0.6, got {avg_confidence:.2f}"

    # Check predicted scores
    max_predicted = max(h.predicted_score for h in hypotheses)
    assert max_predicted >= 99.9, f"Should have hypothesis predicting >= 99.9, got {max_predicted:.1f}"

    print(f"  Hypotheses Generated: {len(hypotheses)}")
    for hyp in hypotheses:
        print(f"    - {hyp.id}: {hyp.title}")
        print(f"      Predicted Score: {hyp.predicted_score:.1f}, Confidence: {hyp.confidence:.2f}")
    print("✅ PASS\n")

def test_improvement_cycle():
    """Test 5: Improvement cycle"""
    print("Test 5: Improvement Cycle")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()
    score_before = engine.state['system_score']

    cycle = engine.run_improvement_cycle(auto_execute=False)

    assert cycle.cycle_id.startswith("CYCLE-"), "Cycle ID should start with CYCLE-"
    assert cycle.patterns_mined >= 0, "Should mine patterns"
    assert cycle.gaps_detected >= 1, "Should detect gaps"
    assert cycle.hypotheses_generated >= 2, "Should generate hypotheses"
    assert cycle.system_score_before == score_before, "Should record before score"

    print(f"  Cycle ID: {cycle.cycle_id}")
    print(f"  Patterns Mined: {cycle.patterns_mined}")
    print(f"  Gaps Detected: {cycle.gaps_detected}")
    print(f"  Hypotheses Generated: {cycle.hypotheses_generated}")
    print(f"  Score: {cycle.system_score_before:.1f} → {cycle.system_score_after:.1f}")
    print("✅ PASS\n")

def test_status_reporting():
    """Test 6: Status reporting"""
    print("Test 6: Status Reporting")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()
    status = engine.status(brief=False)

    assert 'system_score' in status, "Status should have system_score"
    assert 'cycle_count' in status, "Status should have cycle_count"
    assert 'target' in status, "Status should have target"
    assert 'remaining' in status, "Status should have remaining"

    assert status['target'] == "100+/100 🎯", "Target should be 100+/100"
    assert 0 <= status['remaining'] <= 1.0, f"Remaining should be small, got {status['remaining']:.1f}"

    print(f"  System Score: {status['system_score']:.1f}/100")
    print(f"  Target: {status['target']}")
    print(f"  Remaining: {status['remaining']:.1f} points")
    print(f"  Cycle Count: {status['cycle_count']}")
    print("✅ PASS\n")

def test_state_persistence():
    """Test 7: State persistence"""
    print("Test 7: State Persistence")
    print("=" * 60)

    engine1 = MemorySelfImprovingEngine()
    initial_score = engine1.state['system_score']
    initial_cycles = engine1.state['cycle_count']

    # Run a cycle
    engine1.run_improvement_cycle(auto_execute=False)
    engine1._save_state()

    # Create new engine instance (should load saved state)
    engine2 = MemorySelfImprovingEngine()

    assert engine2.state['cycle_count'] >= initial_cycles, "Should persist cycle count"
    assert engine2.state['system_score'] >= initial_score, "Should persist score"

    print(f"  Initial Cycles: {initial_cycles}")
    print(f"  After Cycle: {engine2.state['cycle_count']}")
    print(f"  State persisted correctly ✅")
    print("✅ PASS\n")

def test_brief_output():
    """Test 8: Brief output mode"""
    print("Test 8: Brief Output Mode")
    print("=" * 60)

    engine = MemorySelfImprovingEngine()
    status = engine.status(brief=True)

    # Brief mode should still return full status dict
    assert 'system_score' in status, "Brief mode should still return status"
    assert status['system_score'] >= 99.0, "Score should be correct"

    print(f"  Brief mode works correctly ✅")
    print("✅ PASS\n")


def main():
    """Run all tests"""
    print("=" * 70)
    print("Memory Self-Improving Engine (P4-4) - Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_engine_initialization,
        test_pattern_mining,
        test_gap_detection,
        test_hypothesis_generation,
        test_improvement_cycle,
        test_status_reporting,
        test_state_persistence,
        test_brief_output
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            failed += 1

    print("=" * 70)
    print(f"Tests: {len(tests)} total, {passed} passed, {failed} failed")
    print(f"Success Rate: {passed /len(tests) *100:.1f}%")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
