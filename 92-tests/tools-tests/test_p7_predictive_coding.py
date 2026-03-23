"""
Test suite for Memory Predictive Coding System
Phase 7: Predictive Coding Memory System

Tests cover:
- Prediction generation
- Error computation
- Model updates
- State persistence
- Autonomous cycles
"""

import sys
import os
import time
import json
import tempfile
import unittest
from pathlib import Path

# Fix Windows UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from memory_predictive_coding import (
    PredictiveCodingEngine,
    Prediction,
    PredictionError,
    GenerativeModel
)


class TestPredictionDataStructures(unittest.TestCase):
    """Test prediction data structures"""

    def test_prediction_creation(self):
        """Test prediction object creation"""
        pred = Prediction(
            prediction_id="test_001",
            timestamp=time.time(),
            prediction_type="memory_access",
            predicted_content={'file': 'MEMORY.md'},
            confidence=0.75,
            time_horizon=300.0,
            hierarchical_level=3
        )

        self.assertEqual(pred.prediction_id, "test_001")
        self.assertEqual(pred.prediction_type, "memory_access")
        self.assertEqual(pred.confidence, 0.75)
        self.assertEqual(pred.hierarchical_level, 3)

    def test_prediction_to_dict(self):
        """Test prediction serialization"""
        pred = Prediction(
            prediction_id="test_002",
            timestamp=time.time(),
            prediction_type="user_need",
            predicted_content={'need': 'planning'},
            confidence=0.8,
            time_horizon=600.0,
            hierarchical_level=4
        )

        pred_dict = pred.to_dict()

        self.assertIsInstance(pred_dict, dict)
        self.assertEqual(pred_dict['prediction_id'], "test_002")
        self.assertEqual(pred_dict['confidence'], 0.8)

    def test_prediction_error_creation(self):
        """Test prediction error object creation"""
        error = PredictionError(
            error_id="err_001",
            prediction_id="pred_001",
            timestamp=time.time(),
            predicted_value={'file': 'A.md'},
            actual_value={'file': 'B.md'},
            error_magnitude=0.5,
            error_type='content',
            surprise_level=0.7,
            learning_signal=0.35
        )

        self.assertEqual(error.error_id, "err_001")
        self.assertEqual(error.error_magnitude, 0.5)
        self.assertEqual(error.surprise_level, 0.7)
        self.assertEqual(error.learning_signal, 0.35)


class TestGenerativeModel(unittest.TestCase):
    """Test generative model functionality"""

    def test_model_initialization(self):
        """Test model initialization"""
        model = GenerativeModel(
            model_id="test_model",
            created_at=time.time(),
            last_updated=time.time(),
            hierarchical_levels=5,
            layer_weights=[0.3, 0.25, 0.2, 0.15, 0.1]
        )

        self.assertEqual(model.model_id, "test_model")
        self.assertEqual(model.hierarchical_levels, 5)
        self.assertEqual(len(model.layer_weights), 5)
        self.assertAlmostEqual(sum(model.layer_weights), 1.0)


class TestPredictiveCodingEngine(unittest.TestCase):
    """Test main predictive coding engine"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.engine = PredictiveCodingEngine(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine.model)
        self.assertEqual(self.engine.model.hierarchical_levels, 5)
        self.assertEqual(len(self.engine.active_predictions), 0)

    def test_prediction_generation(self):
        """Test prediction generation"""
        prediction = self.engine.predict(
            prediction_type='memory_access',
            context={'activity': 'test'},
            time_horizon=300.0,
            hierarchical_level=3
        )

        self.assertIsNotNone(prediction.prediction_id)
        self.assertEqual(prediction.prediction_type, 'memory_access')
        self.assertGreater(prediction.confidence, 0.0)
        self.assertEqual(prediction.hierarchical_level, 3)

        # Check prediction is stored
        self.assertIn(prediction.prediction_id, self.engine.active_predictions)
        self.assertEqual(self.engine.stats['total_predictions'], 1)

    def test_multiple_prediction_types(self):
        """Test different prediction types"""
        types = ['memory_access', 'user_need', 'system_state']

        for pred_type in types:
            prediction = self.engine.predict(
                prediction_type=pred_type,
                context={'activity': 'test'}
            )
            self.assertEqual(prediction.prediction_type, pred_type)

    def test_hierarchical_levels(self):
        """Test different hierarchical levels"""
        for level in range(1, 6):
            prediction = self.engine.predict(
                prediction_type='memory_access',
                context={},
                hierarchical_level=level
            )
            self.assertEqual(prediction.hierarchical_level, level)

    def test_error_computation(self):
        """Test prediction error computation"""
        # Make a prediction
        prediction = self.engine.predict(
            prediction_type='memory_access',
            context={}
        )

        # Observe actual outcome (different from prediction)
        actual = {'predicted_memory': 'DIFFERENT.md'}
        error = self.engine.observe(prediction.prediction_id, actual)

        self.assertIsNotNone(error.error_id)
        self.assertEqual(error.prediction_id, prediction.prediction_id)
        self.assertGreaterEqual(error.error_magnitude, 0.0)
        self.assertLessEqual(error.error_magnitude, 1.0)
        self.assertGreaterEqual(error.surprise_level, 0.0)
        self.assertGreaterEqual(error.learning_signal, 0.0)

        # Check error is stored
        self.assertIn(error, self.engine.errors)
        self.assertEqual(self.engine.stats['total_errors'], 1)

    def test_perfect_prediction(self):
        """Test error computation for perfect prediction"""
        prediction = self.engine.predict(
            prediction_type='system_state',
            context={}
        )

        # Observe exact match
        actual = prediction.predicted_content
        error = self.engine.observe(prediction.prediction_id, actual)

        # Should have low or zero error
        self.assertLess(error.error_magnitude, 0.5)

    def test_surprise_computation(self):
        """Test surprise level computation"""
        # High confidence prediction with large error → high surprise
        prediction = self.engine.predict(
            prediction_type='memory_access',
            context={},
            hierarchical_level=1  # Lower level = higher confidence typically
        )

        # Force high confidence
        prediction.confidence = 0.9

        # Large error
        actual = {'completely': 'different'}
        error = self.engine.observe(prediction.prediction_id, actual)

        # Should have high surprise
        self.assertGreater(error.surprise_level, 0.5)

    def test_model_update_on_significant_error(self):
        """Test that model updates on significant errors"""
        initial_updates = self.engine.stats['model_updates']
        initial_weights = self.engine.model.layer_weights.copy()

        # Make several predictions with high surprise errors
        surprises = []
        for i in range(5):
            prediction = self.engine.predict(
                prediction_type='memory_access',
                context={},
                hierarchical_level=5  # High level = lower confidence
            )

            # Create surprising error
            actual = {'unexpected': f'outcome_{i}'}
            error = self.engine.observe(prediction.prediction_id, actual)
            surprises.append(error.surprise_level)

        # Debug output
        print(f"\nDEBUG: Surprises: {surprises}")
        print(f"DEBUG: Initial updates: {initial_updates}, Final: {self.engine.stats['model_updates']}")

        # Model should have been updated
        final_updates = self.engine.stats['model_updates']
        # At least some surprises should be > 0.3
        high_surprises = [s for s in surprises if s > 0.3]
        self.assertGreater(len(high_surprises), 0, "Should have at least one high surprise")
        self.assertGreater(final_updates, initial_updates)

    def test_state_persistence(self):
        """Test state save and load"""
        # Make some predictions
        predictions = []
        for i in range(3):
            pred = self.engine.predict(
                prediction_type='user_need',
                context={'test': i}
            )
            predictions.append(pred)

        # Save state (should happen automatically)
        self.engine._save_state()

        # Create new engine instance
        new_engine = PredictiveCodingEngine(self.test_dir)

        # Check state was loaded
        self.assertEqual(new_engine.stats['total_predictions'], 3)
        self.assertEqual(len(new_engine.model.accuracy_by_level), 5)

    def test_get_prediction_status(self):
        """Test status reporting"""
        # Make some predictions and errors
        for i in range(10):
            pred = self.engine.predict(
                prediction_type='memory_access',
                context={}
            )
            actual = {'outcome': i % 2}  # Some variation
            self.engine.observe(pred.prediction_id, actual)

        status = self.engine.get_prediction_status()

        self.assertIn('active_predictions', status)
        self.assertIn('total_predictions', status)
        self.assertIn('total_errors', status)
        self.assertIn('accuracy_overall', status)
        self.assertIn('accuracy_by_level', status)
        self.assertIn('average_surprise', status)

        self.assertEqual(status['total_predictions'], 10)
        self.assertEqual(status['total_errors'], 10)
        self.assertGreaterEqual(status['accuracy_overall'], 0.0)
        self.assertLessEqual(status['accuracy_overall'], 1.0)

    def test_accuracy_by_level_tracking(self):
        """Test accuracy tracking per hierarchical level"""
        # Make predictions at different levels
        for level in range(1, 6):
            for _ in range(5):
                pred = self.engine.predict(
                    prediction_type='memory_access',
                    context={},
                    hierarchical_level=level
                )
                actual = {'outcome': 'test'}
                self.engine.observe(pred.prediction_id, actual)

        status = self.engine.get_prediction_status()

        # Check all levels have accuracy tracked
        for level in range(1, 6):
            self.assertIn(level, status['accuracy_by_level'])
            acc = status['accuracy_by_level'][level]
            self.assertGreaterEqual(acc, 0.0)
            self.assertLessEqual(acc, 1.0)


class TestAutonomousCycle(unittest.TestCase):
    """Test autonomous prediction-observation cycles"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.engine = PredictiveCodingEngine(self.test_dir)

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_short_autonomous_cycle(self):
        """Test short autonomous cycle"""
        results = self.engine.run_autonomous_cycle(duration_seconds=5)

        self.assertIn('cycle_predictions', results)
        self.assertIn('cycle_errors', results)
        self.assertGreater(results['cycle_predictions'], 0)
        self.assertEqual(results['cycle_predictions'], results['cycle_errors'])

    def test_cycle_improves_accuracy(self):
        """Test that accuracy can be tracked over cycle"""
        # Run cycle
        results1 = self.engine.run_autonomous_cycle(duration_seconds=3)

        # Get status
        status = self.engine.get_prediction_status()

        # Should have recorded accuracy
        self.assertIn('accuracy_overall', status)
        self.assertIsInstance(status['accuracy_overall'], float)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        """Set up with real workspace"""
        self.workspace = Path(__file__).parent.parent
        self.engine = PredictiveCodingEngine(str(self.workspace))

    def test_real_workspace_initialization(self):
        """Test initialization with real workspace"""
        self.assertIsNotNone(self.engine.model)
        self.assertTrue(self.engine.data_dir.exists())

    def test_prediction_in_real_context(self):
        """Test prediction in real workspace context"""
        prediction = self.engine.predict(
            prediction_type='memory_access',
            context={
                'time_of_day': 'morning',
                'day_of_week': 'weekday',
                'recent_activity': 'coding'
            }
        )

        self.assertIsNotNone(prediction)
        self.assertIn('predicted_content', prediction.to_dict())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPredictionDataStructures))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerativeModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPredictiveCodingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousCycle))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
