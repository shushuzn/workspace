#!/usr/bin/env python3
"""
Memory Integration Tests
Test dynamic memory integration with existing systems

Tests:
1. ContextDB Integration
2. Memory Distillation Integration
3. 7-Persona Integration
4. HEARTBEAT Integration
5. Workflow Integration
6. Performance Benchmarks

Usage:
  python test_memory_integration.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import unittest
import time
from datetime import datetime
import json
import os

# Import memory systems
from dynamic_memory_allocation import (
    DynamicMemoryAllocator,
    MemoryTier,
    MemoryPriority,
    MemoryBlock
)
from memory_integration import (
    MemoryIntegrationLayer,
    MemoryIntegrationConfig,
    WorkflowMemoryProfile,
    setup_default_workflows
)


class TestDynamicMemoryAllocation(unittest.TestCase):
    """Test dynamic memory allocation system"""

    def setUp(self):
        """Setup test fixtures"""
        self.allocator = DynamicMemoryAllocator(total_capacity_mb=128)

    def test_allocation_basic(self):
        """Test basic memory allocation"""
        content = "Test memory block"
        result = self.allocator.allocate(content, MemoryPriority.MEDIUM)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.block_id)
        self.assertGreater(result.size_bytes, 0)

    def test_allocation_priority(self):
        """Test priority-based allocation"""
        # Allocate critical block
        critical = self.allocator.allocate("Critical data", MemoryPriority.CRITICAL)
        # Allocate low priority block
        low = self.allocator.allocate("Low priority", MemoryPriority.LOW)

        self.assertTrue(critical.success)
        self.assertTrue(low.success)

        # Critical should have higher priority (lower value)
        critical_block = self.allocator.block_registry[critical.block_id]
        low_block = self.allocator.block_registry[low.block_id]

        self.assertLess(critical_block.priority, low_block.priority)

    def test_access_pattern(self):
        """Test memory access patterns"""
        # Allocate block
        result = self.allocator.allocate("Test data", MemoryPriority.MEDIUM)
        block_id = result.block_id

        # Access multiple times
        for i in range(5):
            block = self.allocator.access(block_id)
            self.assertIsNotNone(block)
            self.assertEqual(block.access_count, i + 1)

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        # Allocate and access blocks
        block_ids = []
        for i in range(10):
            result = self.allocator.allocate(f"Block {i}", MemoryPriority.MEDIUM)
            block_ids.append(result.block_id)

        # Access all blocks (hits)
        for block_id in block_ids:
            self.allocator.access(block_id)

        # Access non-existent block (miss)
        self.allocator.access("nonexistent")

        stats = self.allocator.get_stats()

        # Should have high hit rate
        self.assertGreater(stats.hit_rate, 0.8)

    def test_garbage_collection(self):
        """Test automatic garbage collection"""
        # Allocate many low-priority blocks
        for i in range(50):
            self.allocator.allocate(f"Block {i}", MemoryPriority.LOW)

        # Run GC
        gc_results = self.allocator.run_gc()

        # Should have collected some blocks
        self.assertGreater(len(gc_results), 0)

    def test_tier_distribution(self):
        """Test tier memory distribution"""
        stats = self.allocator.get_stats()

        # Check tier ratios (60/30/10)
        self.assertAlmostEqual(stats.l1_usage, 0, delta=0.1)  # Empty initially
        self.assertAlmostEqual(stats.l2_usage, 0, delta=0.1)
        self.assertAlmostEqual(stats.l3_usage, 0, delta=0.1)


class TestMemoryIntegration(unittest.TestCase):
    """Test memory integration layer"""

    def setUp(self):
        """Setup test fixtures"""
        config = MemoryIntegrationConfig(
            enabled=True,
            total_capacity_mb=256,
            auto_gc=True
        )
        self.integration = MemoryIntegrationLayer(config)

    def test_workflow_registration(self):
        """Test workflow profile registration"""
        profile = WorkflowMemoryProfile(
            workflow_name="test_workflow",
            priority=2,
            l1_allocation_mb=20,
            l2_allocation_mb=10,
            l3_allocation_mb=5,
            auto_gc=True,
            description="Test workflow"
        )

        self.integration.register_workflow("test_workflow", profile)

        self.assertIn("test_workflow", self.integration.workflow_profiles)

    def test_workflow_allocation(self):
        """Test workflow-specific memory allocation"""
        # Register workflow
        profile = WorkflowMemoryProfile(
            workflow_name="test_wf",
            priority=1,
            l1_allocation_mb=30,
            l2_allocation_mb=15,
            l3_allocation_mb=10,
            auto_gc=True,
            description="Test"
        )
        self.integration.register_workflow("test_wf", profile)

        # Allocate for workflow
        block_id = self.integration.allocate_for_workflow(
            "test_wf",
            "Workflow context data"
        )

        self.assertIsNotNone(block_id)

    def test_default_workflows(self):
        """Test default workflow setup"""
        setup_default_workflows(self.integration)

        # Should have 8 default workflows
        self.assertEqual(len(self.integration.workflow_profiles), 8)

        # Check specific workflows exist
        expected_workflows = [
            "arxiv_research",
            "memory_distillation",
            "7_persona_collaboration",
            "knowledge_graph"
        ]

        for wf in expected_workflows:
            self.assertIn(wf, self.integration.workflow_profiles)

    def test_optimization(self):
        """Test memory optimization"""
        # Allocate some memory
        for i in range(20):
            self.integration.allocate_for_workflow(
                "arxiv_research",
                f"Data block {i}"
            )

        # Run optimization
        result = self.integration.optimize_workflow_memory("arxiv_research")

        self.assertIsNotNone(result)
        self.assertEqual(result.workflow, "arxiv_research")
        self.assertGreaterEqual(result.memory_after_mb, 0)

    def test_status_reporting(self):
        """Test integration status reporting"""
        setup_default_workflows(self.integration)

        # Allocate some memory
        for i in range(10):
            self.integration.allocate_for_workflow(
                "memory_distillation",
                f"Distillation data {i}"
            )

        status = self.integration.get_integration_status()

        # Check status fields
        self.assertIn("enabled", status)
        self.assertIn("total_capacity_mb", status)
        self.assertIn("utilization", status)
        self.assertIn("cache_hit_rate", status)
        self.assertIn("registered_workflows", status)

        self.assertTrue(status["enabled"])
        self.assertEqual(status["total_capacity_mb"], 256)
        self.assertEqual(status["registered_workflows"], 8)


class TestIntegrationWithExistingSystems(unittest.TestCase):
    """Test integration with existing systems"""

    def test_contextdb_integration_ready(self):
        """Test ContextDB integration readiness"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=512)

        # Simulate ContextDB operations
        # 1. Store entity
        entity_block = allocator.allocate(
            {"type": "entity", "id": "E001", "name": "Test"},
            MemoryPriority.HIGH
        )

        # 2. Store relationship
        rel_block = allocator.allocate(
            {"type": "relation", "source": "E001", "target": "E002"},
            MemoryPriority.MEDIUM
        )

        # 3. Access entity
        entity = allocator.access(entity_block.block_id)

        self.assertIsNotNone(entity)
        self.assertEqual(entity.content["type"], "entity")

    def test_memory_distillation_integration(self):
        """Test Memory Distillation integration"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=256)

        # Simulate distillation workflow
        # 1. Store raw context (L3)
        raw_context = allocator.allocate(
            "Raw conversation context " * 100,
            MemoryPriority.LOW,
            {"stage": "raw"}
        )

        # 2. Store distilled context (L2)
        distilled = allocator.allocate(
            "Distilled key points",
            MemoryPriority.MEDIUM,
            {"stage": "distilled"}
        )

        # 3. Store core insights (L1)
        insights = allocator.allocate(
            "Core insights",
            MemoryPriority.HIGH,
            {"stage": "insights"}
        )

        # Verify tier assignment
        raw_block = allocator.block_registry[raw_context.block_id]
        distilled_block = allocator.block_registry[distilled.block_id]
        insights_block = allocator.block_registry[insights.block_id]

        # Higher priority should be in higher tier
        self.assertLessEqual(insights_block.priority, distilled_block.priority)
        self.assertLessEqual(distilled_block.priority, raw_block.priority)

    def test_persona_system_integration(self):
        """Test 7-Persona system integration"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=512)

        # Simulate persona memory
        personas = ["planner", "executor", "critic", "learner",
                   "coordinator", "innovator", "metacognition"]

        persona_blocks = {}

        for persona in personas:
            # Each persona gets memory allocation
            block = allocator.allocate(
                f"{persona} state and context",
                MemoryPriority.HIGH,
                {"persona": persona}
            )
            persona_blocks[persona] = block.block_id

        # Access all persona memories
        for persona, block_id in persona_blocks.items():
            block = allocator.access(block_id)
            self.assertIsNotNone(block)
            self.assertEqual(block.metadata["persona"], persona)

    def test_heartbeat_integration(self):
        """Test HEARTBEAT integration"""
        integration = MemoryIntegrationLayer(MemoryIntegrationConfig(
            enabled=True,
            total_capacity_mb=256,
            auto_gc=True,
            gc_threshold=0.7
        ))

        setup_default_workflows(integration)

        # Simulate HEARTBEAT task
        # 1. Allocate memory for task
        task_block = integration.allocate_for_workflow(
            "heartbeat_tasks",
            "HEARTBEAT task data"
        )

        # 2. Access task
        task_data = integration.access_for_workflow("heartbeat_tasks", task_block)

        # 3. Optimize after task
        result = integration.optimize_workflow_memory("heartbeat_tasks")

        self.assertIsNotNone(task_data)
        self.assertIsNotNone(result)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test performance benchmarks"""

    def test_allocation_speed(self):
        """Test allocation speed"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=512)

        start = time.time()

        for i in range(100):
            allocator.allocate(f"Block {i}", MemoryPriority.MEDIUM)

        elapsed = time.time() - start

        # Should allocate 100 blocks in <1 second
        self.assertLess(elapsed, 1.0)
        print(f"\n  ⚡ Allocation speed: {100/elapsed:.0f} blocks/sec")

    def test_access_speed(self):
        """Test access speed"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=512)

        # Allocate blocks
        block_ids = []
        for i in range(100):
            result = allocator.allocate(f"Block {i}", MemoryPriority.MEDIUM)
            block_ids.append(result.block_id)

        # Access blocks
        start = time.time()

        for block_id in block_ids:
            allocator.access(block_id)

        elapsed = time.time() - start

        # Should access 100 blocks in <0.5 seconds
        self.assertLess(elapsed, 0.5)
        print(f"\n  ⚡ Access speed: {100/elapsed:.0f} accesses/sec")

    def test_memory_efficiency(self):
        """Test memory efficiency"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=256)

        # Allocate varying sizes
        for i in range(50):
            size = (i + 1) * 1000  # 1KB to 50KB
            content = "x" * size
            allocator.allocate(content, MemoryPriority.MEDIUM)

        stats = allocator.get_stats()

        # Utilization should be reasonable (<90%)
        self.assertLess(stats.utilization, 0.9)
        print(f"\n  📊 Memory efficiency: {stats.utilization:.0%} utilization")

    def test_cache_performance(self):
        """Test cache performance"""
        allocator = DynamicMemoryAllocator(total_capacity_mb=512)

        # Allocate blocks
        block_ids = []
        for i in range(50):
            result = allocator.allocate(f"Hot block {i}", MemoryPriority.HIGH)
            block_ids.append(result.block_id)

        # Access hot blocks multiple times
        for _ in range(10):
            for block_id in block_ids:
                allocator.access(block_id)

        # Access cold blocks once
        for i in range(20):
            result = allocator.allocate(f"Cold block {i}", MemoryPriority.LOW)
            allocator.access(result.block_id)

        stats = allocator.get_stats()

        # Hit rate should be high (>80%)
        self.assertGreater(stats.hit_rate, 0.8)
        print(f"\n  🎯 Cache performance: {stats.hit_rate:.0%} hit rate")


def run_tests():
    """Run all tests"""

    print("\n" + "="*80)
    print("🧪 Memory Integration Tests")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicMemoryAllocation))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithExistingSystems))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmarks))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.0f}%")

    # Export results
    os.makedirs("data", exist_ok=True)
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    }

    with open("data/memory_integration_test_results.json", 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: data/memory_integration_test_results.json")

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
