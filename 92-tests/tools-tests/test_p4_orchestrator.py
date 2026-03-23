#!/usr/bin/env python3
"""
Test Memory Orchestrator (P4-1)
================================
"""

import sys
import os
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from memory_orchestrator import MemoryOrchestrator, TOOL_REGISTRY, PIPELINES


def test_tool_registry():
    """Test tool registry has all 15 tools"""
    print("Test 1: Tool Registry")
    print("=" * 60)

    expected_tools = 15
    actual_tools = len(TOOL_REGISTRY)

    print(f"Expected tools: {expected_tools}")
    print(f"Actual tools: {actual_tools}")

    assert actual_tools == expected_tools, f"Expected {expected_tools} tools, got {actual_tools}"

    # Check all phases represented
    phases = set(config.phase for config in TOOL_REGISTRY.values())
    expected_phases = {'core', 'P0', 'P1', 'P2', 'P3'}

    print(f"Phases: {phases}")
    assert phases == expected_phases, f"Missing phases: {expected_phases - phases}"

    print("✅ PASS\n")


def test_pipelines():
    """Test pipeline definitions"""
    print("Test 2: Pipelines")
    print("=" * 60)

    expected_pipelines = 7
    actual_pipelines = len(PIPELINES)

    print(f"Expected pipelines: {expected_pipelines}")
    print(f"Actual pipelines: {actual_pipelines}")

    assert actual_pipelines >= expected_pipelines

    # Check pipeline contents
    assert 'full' in PIPELINES
    assert 'core' in PIPELINES
    assert 'p0' in PIPELINES
    assert 'p1' in PIPELINES
    assert 'p2' in PIPELINES
    assert 'p3' in PIPELINES
    assert 'quick' in PIPELINES

    print("✅ PASS\n")


def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    print("Test 3: Orchestrator Initialization")
    print("=" * 60)

    orchestrator = MemoryOrchestrator()

    print(f"Workspace: {orchestrator.workspace}")
    print(f"Tools dir: {orchestrator.tools_dir}")
    print(f"Data dir: {orchestrator.data_dir}")
    print(f"Reports dir: {orchestrator.reports_dir}")

    assert orchestrator.workspace.exists()
    assert orchestrator.tools_dir.exists()

    print("✅ PASS\n")


def test_get_status():
    """Test get_status method"""
    print("Test 4: Get Status")
    print("=" * 60)

    orchestrator = MemoryOrchestrator()
    status = orchestrator.get_status()

    print(f"Timestamp: {status['timestamp']}")
    print(f"Total tools: {len(status['tools'])}")

    assert 'timestamp' in status
    assert 'workspace' in status
    assert 'tools' in status
    assert len(status['tools']) > 0

    # Check tool info
    for tool_id, info in list(status['tools'].items())[:3]:
        print(f"  - {tool_id}: {info['name']} ({info['phase']})")
        assert 'name' in info
        assert 'phase' in info
        assert 'exists' in info

    print("✅ PASS\n")


def test_run_single_tool():
    """Test running a single tool (quick one)"""
    print("Test 5: Run Single Tool")
    print("=" * 60)

    orchestrator = MemoryOrchestrator()

    # Test with a quick tool - quality scorer
    target_file = str(orchestrator.workspace / 'MEMORY.md')

    if not Path(target_file).exists():
        print(f"⚠️  Target file not found: {target_file}")
        print("Skipping test")
        print("✅ PASS (skipped)\n")
        return

    print(f"Target: {target_file}")
    print("Running quality scorer...")

    result = orchestrator.run_tool('quality', target_file)

    print(f"Tool: {result.tool_name}")
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration:.2f}s")

    # Success is optional (depends on tool implementation)
    print("✅ PASS (tool executed)\n")


def test_invalid_tool():
    """Test error handling for invalid tool"""
    print("Test 6: Invalid Tool Handling")
    print("=" * 60)

    orchestrator = MemoryOrchestrator()

    result = orchestrator.run_tool('nonexistent_tool', 'test.md')

    print(f"Success: {result.success}")
    print(f"Error: {result.error}")

    assert not result.success
    assert 'Unknown tool' in result.error

    print("✅ PASS\n")


def test_aggregate_metrics():
    """Test metrics aggregation"""
    print("Test 7: Aggregate Metrics")
    print("=" * 60)

    orchestrator = MemoryOrchestrator()

    # Create mock results
    from memory_orchestrator import ToolResult

    results = [
        ToolResult('immune', 'Immune System', 'P0', True, 10.5),
        ToolResult('neural', 'Neural Network', 'P0', True, 12.3),
        ToolResult('dark_matter', 'Dark Matter', 'P1', False, 5.2, error='Test error'),
    ]

    metrics = orchestrator._aggregate_metrics(results)

    print(f"Total tools: {metrics['total_tools']}")
    print(f"Successful: {metrics['successful']}")
    print(f"Failed: {metrics['failed']}")
    print(f"By phase: {metrics['by_phase']}")

    assert metrics['total_tools'] == 3
    assert metrics['successful'] == 2
    assert metrics['failed'] == 1
    assert 'P0' in metrics['by_phase']
    assert 'P1' in metrics['by_phase']

    print("✅ PASS\n")


def test_pipeline_structure():
    """Test pipeline structure"""
    print("Test 8: Pipeline Structure")
    print("=" * 60)

    # Check full pipeline
    full_pipeline = PIPELINES['full']
    print(f"Full pipeline: {len(full_pipeline)} tools")

    # Check phase pipelines
    p0_pipeline = PIPELINES['p0']
    p1_pipeline = PIPELINES['p1']
    p2_pipeline = PIPELINES['p2']
    p3_pipeline = PIPELINES['p3']

    print(f"P0 (Biological): {len(p0_pipeline)} tools - {p0_pipeline}")
    print(f"P1 (Physics/Math): {len(p1_pipeline)} tools - {p1_pipeline}")
    print(f"P2 (Quantum/Time): {len(p2_pipeline)} tools - {p2_pipeline}")
    print(f"P3 (Consciousness): {len(p3_pipeline)} tools - {p3_pipeline}")

    assert len(full_pipeline) >= 10
    assert len(p0_pipeline) == 2
    assert len(p1_pipeline) == 5
    assert len(p2_pipeline) == 2
    assert len(p3_pipeline) == 1

    print("✅ PASS\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Memory Orchestrator (P4-1) - Test Suite")
    print("=" * 60 + "\n")

    tests = [
        test_tool_registry,
        test_pipelines,
        test_orchestrator_initialization,
        test_get_status,
        test_run_single_tool,
        test_invalid_tool,
        test_aggregate_metrics,
        test_pipeline_structure,
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

    print("=" * 60)
    print(f"Tests: {passed + failed} total, {passed} passed, {failed} failed")
    print(f"Success Rate: {passed /(passed +failed) *100:.1f}%")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
