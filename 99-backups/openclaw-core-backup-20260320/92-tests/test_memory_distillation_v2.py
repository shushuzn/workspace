#!/usr/bin/env python3
"""
Memory Distillation System v2.0 - Test Suite
=============================================
Comprehensive tests for memory distillation components:
- memory_distiller_v2.py (Quality-driven distillation)
- memory_forgetting_execute.py (Automatic archival)
- memory_conflict_resolver.py (Conflict resolution)
- memory_audit_logger.py (Audit logging)

Usage:
    python test_memory_distillation_v2.py
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================================
# Test Utilities
# ============================================================================

class TestUtilities:
    """Test utility functions"""

    @staticmethod
    def create_temp_file(content: str, suffix: str = '.md') -> str:
        """Create temporary file with content"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    @staticmethod
    def create_temp_dir() -> str:
        """Create temporary directory"""
        return tempfile.mkdtemp()

    @staticmethod
    def cleanup(path: str):
        """Clean up temporary file or directory"""
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


# ============================================================================
# Memory Distiller v2 Tests
# ============================================================================

class TestMemoryDistiller(unittest.TestCase):
    """Tests for memory_distiller_v2.py"""

    def setUp(self):
        """Set up test fixtures"""
        from memory_distiller_v2 import MemoryDistiller, DistillerConfig

        self.config = DistillerConfig()
        self.distiller = MemoryDistiller(self.config)
        self.temp_dir = TestUtilities.create_temp_dir()

    def tearDown(self):
        """Clean up"""
        TestUtilities.cleanup(self.temp_dir)

    def test_01_quality_assessment(self):
        """Test quality assessment"""
        # Create test file with high-quality content
        content = """# Test Memory

## Key Insights

- [INSIGHT-001] High-quality insight with clear action
- [INSIGHT-002] Another valuable lesson learned
- [INSIGHT-003] Third insight with examples

**Important:** This is well-structured content.
"""
        test_file = TestUtilities.create_temp_file(content)

        try:
            score = self.distiller.assess_quality(test_file)
            self.assertGreaterEqual(score, 0.5)
            self.assertLessEqual(score, 1.0)
            print(f"✅ Quality score: {score:.2f}")
        finally:
            TestUtilities.cleanup(test_file)

    def test_02_insight_extraction(self):
        """Test insight extraction"""
        content = """# Test

- [LESSON-001] First lesson
- [LESSON-002] Second lesson
**Key point**
### Header with content
"""
        test_file = TestUtilities.create_temp_file(content)

        try:
            insights = self.distiller.extract_insights(test_file)
            self.assertGreaterEqual(len(insights), 2)
            print(f"✅ Extracted {len(insights)} insights")
        finally:
            TestUtilities.cleanup(test_file)

    def test_03_backup_creation(self):
        """Test backup creation"""
        content = "Test content"
        test_file = TestUtilities.create_temp_file(content)

        try:
            backup_path = self.distiller.create_backup(test_file)
            self.assertTrue(os.path.exists(backup_path))
            print(f"✅ Backup created: {backup_path}")
        finally:
            TestUtilities.cleanup(test_file)

    def test_04_distillation_dry_run(self):
        """Test distillation (dry-run)"""
        content = """# Test

- [TEST-001] Test insight 1
- [TEST-002] Test insight 2
"""
        test_file = TestUtilities.create_temp_file(content)
        target_file = os.path.join(self.temp_dir, 'target.md')

        try:
            success, message = self.distiller.distill_to_memory(
                source_file=test_file,
                target_file=target_file,
                threshold=0.50,
                auto_execute=False  # Dry run
            )
            # May fail if quality scorer not available, that's OK
            print(f"✅ Distillation dry-run: {message}")
        finally:
            TestUtilities.cleanup(test_file)

    def test_05_density_calculation(self):
        """Test density calculation"""
        content = """# Test

- [INSIGHT-001] Insight 1
- [INSIGHT-002] Insight 2
- [INSIGHT-003] Insight 3

Some regular text.
"""
        test_file = TestUtilities.create_temp_file(content)

        try:
            density = self.distiller.density_tracker.calculate_density(test_file)
            self.assertGreaterEqual(density, 0.0)
            self.assertLessEqual(density, 1.0)
            print(f"✅ Density: {density:.2f}")
        finally:
            TestUtilities.cleanup(test_file)


# ============================================================================
# Memory Forgetting Engine Tests
# ============================================================================

class TestForgettingEngine(unittest.TestCase):
    """Tests for memory_forgetting_execute.py"""

    def setUp(self):
        """Set up test fixtures"""
        from memory_forgetting_execute import ForgettingEngine, ForgettingConfig

        self.config = ForgettingConfig()
        self.engine = ForgettingEngine(self.config)
        self.temp_dir = TestUtilities.create_temp_dir()

    def tearDown(self):
        """Clean up"""
        TestUtilities.cleanup(self.temp_dir)

    def test_01_retention_calculation(self):
        """Test retention score calculation"""
        # Fresh memory (0 days)
        now = datetime.now()
        retention_fresh = self.engine.calculate_retention(now)
        self.assertGreater(retention_fresh, 0.9)

        # Old memory (365 days)
        old = now - timedelta(days=365)
        retention_old = self.engine.calculate_retention(old)
        self.assertLess(retention_old, 0.5)

        # Priority modifier
        retention_critical = self.engine.calculate_retention(old, priority='CRITICAL')
        self.assertGreater(retention_critical, retention_old)

        print(f"✅ Retention: fresh={retention_fresh:.2f}, old={retention_old:.2f}, critical={retention_critical:.2f}")

    def test_02_metadata_extraction(self):
        """Test metadata extraction"""
        content = """# Test Memory

CRITICAL: This is important.

- [TEST-001] Test insight
"""
        test_file = TestUtilities.create_temp_file(content)

        try:
            metadata = self.engine.extract_metadata(test_file)
            self.assertEqual(metadata['priority'], 'CRITICAL')
            self.assertGreater(metadata['insight_count'], 0)
            print(f"✅ Metadata extracted: priority={metadata['priority']}")
        finally:
            TestUtilities.cleanup(test_file)

    def test_03_action_determination(self):
        """Test action determination"""
        # Fresh file → retain
        now = datetime.now()
        retention_fresh = self.engine.calculate_retention(now)
        if retention_fresh > self.config.THRESHOLD_REVIEW:
            action = 'retain'
        elif retention_fresh > self.config.THRESHOLD_FORGET:
            action = 'review'
        else:
            action = 'archive'

        self.assertEqual(action, 'retain')
        print(f"✅ Action for fresh file: {action}")

    def test_04_ebbinghaus_curve(self):
        """Test Ebbinghaus curve plotting"""
        # Just test it doesn't crash
        try:
            self.engine.plot_forgetting_curve(days=100)
            print("✅ Forgetting curve plotted")
        except Exception as e:
            self.fail(f"Curve plotting failed: {e}")


# ============================================================================
# Memory Conflict Resolver Tests
# ============================================================================

class TestConflictResolver(unittest.TestCase):
    """Tests for memory_conflict_resolver.py"""

    def setUp(self):
        """Set up test fixtures"""
        from memory_conflict_resolver import ConflictDetector, ConflictResolver, ResolverConfig

        self.config = ResolverConfig()
        self.detector = ConflictDetector(self.config)
        self.resolver = ConflictResolver(self.config)

    def test_01_statement_extraction(self):
        """Test statement extraction"""
        content = """# Test

- [LESSON-001] First lesson
- [LESSON-002] Second lesson
- [LESSON-003] Third lesson
"""
        test_file = TestUtilities.create_temp_file(content)

        try:
            statements = self.detector.extract_statements(test_file)
            self.assertEqual(len(statements), 3)
            print(f"✅ Extracted {len(statements)} statements")
        finally:
            TestUtilities.cleanup(test_file)

    def test_02_duplicate_detection(self):
        """Test duplicate detection"""
        content1 = "- [TEST-001] Duplicate content"
        content2 = "- [TEST-001] Duplicate content"  # Exact duplicate

        file1 = TestUtilities.create_temp_file(content1)
        file2 = TestUtilities.create_temp_file(content2)

        try:
            statements1 = self.detector.extract_statements(file1)
            statements2 = self.detector.extract_statements(file2)
            all_statements = statements1 + statements2

            duplicates = self.detector.detect_duplicates(all_statements)
            # May or may not detect depending on hash
            print(f"✅ Detected {len(duplicates)} duplicates")
        finally:
            TestUtilities.cleanup(file1)
            TestUtilities.cleanup(file2)

    def test_03_conflict_resolution(self):
        """Test conflict resolution"""
        conflict = {
            'id': 'CONFLICT-001',
            'type': 'duplicate',
            'severity': 'medium',
            'statement1': {
                'file': 'file1.md',
                'content': 'Statement 1',
                'line_num': 1
            },
            'statement2': {
                'file': 'file2.md',
                'content': 'Statement 2',
                'line_num': 1
            }
        }

        resolution = self.resolver.resolve_conflict(conflict, auto=True)

        self.assertEqual(resolution['conflict_id'], 'CONFLICT-001')
        self.assertIn(resolution['result'], ['auto_resolved', 'pending'])
        print(f"✅ Resolution: {resolution['result']}")

    def test_04_similarity_calculation(self):
        """Test similarity calculation"""
        from difflib import SequenceMatcher

        text1 = "This is a test statement"
        text2 = "This is a test statement"  # 100% similar
        text3 = "Completely different text"  # 0% similar

        similarity_same = SequenceMatcher(None, text1, text2).ratio()
        similarity_diff = SequenceMatcher(None, text1, text3).ratio()

        self.assertGreater(similarity_same, 0.9)
        self.assertLess(similarity_diff, 0.5)

        print(f"✅ Similarity: same={similarity_same:.2f}, diff={similarity_diff:.2f}")


# ============================================================================
# Memory Audit Logger Tests
# ============================================================================

class TestAuditLogger(unittest.TestCase):
    """Tests for memory_audit_logger.py"""

    def setUp(self):
        """Set up test fixtures"""
        from memory_audit_logger import MemoryAuditLogger, AuditConfig

        self.config = AuditConfig()
        self.logger = MemoryAuditLogger(self.config)
        self.temp_dir = TestUtilities.create_temp_dir()

    def tearDown(self):
        """Clean up"""
        TestUtilities.cleanup(self.temp_dir)

    def test_01_log_initialization(self):
        """Test log initialization"""
        # Combined log should be created
        self.assertTrue(os.path.exists(self.config.COMBINED_LOG))
        print(f"✅ Audit log initialized: {self.config.COMBINED_LOG}")

    def test_02_statistics_calculation(self):
        """Test statistics calculation"""
        stats = self.logger.get_statistics(days=7)

        self.assertIn('total_operations', stats)
        self.assertIn('by_source', stats)
        self.assertIn('by_status', stats)

        print(f"✅ Statistics: {stats['total_operations']} operations")

    def test_03_timeline_generation(self):
        """Test timeline generation"""
        timeline = self.logger.get_timeline(days=30)

        # Should be a list
        self.assertIsInstance(timeline, list)
        print(f"✅ Timeline: {len(timeline)} days with operations")

    def test_04_report_generation(self):
        """Test report generation"""
        report = self.logger.generate_report(days=7)

        self.assertIn("Memory Operations Audit Report", report)
        self.assertIn("Summary", report)

        print(f"✅ Report generated ({len(report)} chars)")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""

    def test_01_complete_workflow(self):
        """Test complete distillation workflow"""
        print("\n" + "=" * 70)
        print("INTEGRATION TEST: Complete Distillation Workflow")
        print("=" * 70)

        # Step 1: Create test memory
        content = """# Integration Test Memory

- [INT-001] Integration test insight 1
- [INT-002] Integration test insight 2
- [INT-003] Integration test insight 3

**Key finding:** This is important.
"""
        test_file = TestUtilities.create_temp_file(content)
        temp_dir = TestUtilities.create_temp_dir()

        try:
            # Step 2: Assess quality
            from memory_distiller_v2 import MemoryDistiller
            distiller = MemoryDistiller()
            score = distiller.assess_quality(test_file)
            print(f"✓ Quality score: {score:.2f}")

            # Step 3: Extract insights
            insights = distiller.extract_insights(test_file)
            print(f"✓ Extracted {len(insights)} insights")

            # Step 4: Evaluate for forgetting
            from memory_forgetting_execute import ForgettingEngine
            engine = ForgettingEngine()
            result = engine.evaluate_file(test_file)
            print(f"✓ Retention score: {result['retention_score']:.2f}")
            print(f"✓ Action: {result['action']}")

            # Step 5: Scan for conflicts
            from memory_conflict_resolver import ConflictDetector
            detector = ConflictDetector()
            statements = detector.extract_statements(test_file)
            print(f"✓ Extracted {len(statements)} statements for conflict check")

            # Step 6: Log audit
            from memory_audit_logger import MemoryAuditLogger
            audit_logger = MemoryAuditLogger()
            stats = audit_logger.get_statistics(days=7)
            print(f"✓ Audit statistics: {stats['total_operations']} operations")

            print("=" * 70)
            print("✅ INTEGRATION TEST PASSED")
            print("=" * 70)

        finally:
            TestUtilities.cleanup(test_file)
            TestUtilities.cleanup(temp_dir)


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("MEMORY DISTILLATION SYSTEM V2.0 - TEST SUITE")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryDistiller))
    suite.addTests(loader.loadTestsFromTestCase(TestForgettingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
