#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for LLM Hypothesis Generator (P5-1)
==============================================
Tests for memory_llm_hypothesis.py

Coverage:
- OllamaClient health check
- Hypothesis generation (LLM + template)
- Batch generation
- State persistence
- Statistics
- Export functionality

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import unittest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TestOllamaClient(unittest.TestCase):
    """Test OllamaClient class."""
    
    def setUp(self):
        from memory_llm_hypothesis import OllamaClient
        self.client = OllamaClient()
    
    @patch('memory_llm_hypothesis.requests.get')
    def test_check_health_success(self, mock_get):
        """Test health check success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.client.check_health()
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('memory_llm_hypothesis.requests.get')
    def test_check_health_failure(self, mock_get):
        """Test health check failure."""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.client.check_health()
        self.assertFalse(result)
    
    @patch('memory_llm_hypothesis.requests.post')
    def test_generate_success(self, mock_post):
        """Test text generation success."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'Test response'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.client.generate("Test prompt")
        self.assertEqual(result, 'Test response')
        mock_post.assert_called_once()
    
    @patch('memory_llm_hypothesis.requests.get')
    def test_list_models(self, mock_get):
        """Test model listing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'models': [
                {'name': 'qwen2.5:1.5b'},
                {'name': 'qwen2.5:3b'}
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.client.list_models()
        self.assertEqual(len(result), 2)
        self.assertIn('qwen2.5:1.5b', result)


class TestLLMHypothesisGenerator(unittest.TestCase):
    """Test LLMHypothesisGenerator class."""
    
    def setUp(self):
        from memory_llm_hypothesis import LLMHypothesisGenerator
        self.test_dir = tempfile.mkdtemp()
        self.generator = LLMHypothesisGenerator(self.test_dir)
        
        # Sample gaps for testing
        self.sample_gaps = [
            {"id": "GAP-001", "name": "Pattern Diversity", "description": "Limited pattern variety"},
            {"id": "GAP-002", "name": "Hypothesis Quality", "description": "Low confidence scores"}
        ]
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.state['total_generated'], 0)
        self.assertEqual(self.generator.state['total_deployed'], 0)
        self.assertIsInstance(self.generator.innovation_patterns, list)
        self.assertTrue(len(self.generator.innovation_patterns) > 0)
    
    def test_load_state_new(self):
        """Test state loading for new instance."""
        # Fresh generator should have empty state
        self.assertEqual(self.generator.state['total_generated'], 0)
    
    @patch('memory_llm_hypothesis.requests.post')
    def test_generate_with_llm(self, mock_post):
        """Test LLM-based hypothesis generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': '''{
                "title": "Enhanced Pattern Detection",
                "description": "Improve pattern detection accuracy",
                "predicted_impact": 0.7,
                "implementation_effort": "Medium",
                "estimated_time": "6 hours",
                "related_patterns": ["Integration Pattern"],
                "confidence": 0.8,
                "priority": "P1"
            }'''
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Mock health check to return True
        with patch.object(self.generator, 'check_ollama_available', return_value=True):
            gap = self.sample_gaps[0]
            hypothesis = self.generator.generate_hypothesis(gap, self.generator.innovation_patterns, use_llm=True)
            
            self.assertEqual(hypothesis['gap_id'], 'GAP-001')
            self.assertEqual(hypothesis['method'], 'llm')
            self.assertIn('HYP-LLM-', hypothesis['id'])
            self.assertEqual(hypothesis['status'], 'pending')
            self.assertEqual(self.generator.state['total_generated'], 1)
    
    def test_generate_template_fallback(self):
        """Test template-based fallback generation."""
        gap = self.sample_gaps[0]
        hypothesis = self.generator.generate_hypothesis(gap, self.generator.innovation_patterns, use_llm=False)
        
        self.assertEqual(hypothesis['gap_id'], 'GAP-001')
        self.assertEqual(hypothesis['method'], 'template')
        self.assertIn('HYP-TPL-', hypothesis['id'])
        self.assertEqual(hypothesis['status'], 'pending')
        self.assertIn('priority', hypothesis)
        self.assertIn('predicted_impact', hypothesis)
    
    def test_generate_batch(self):
        """Test batch hypothesis generation."""
        hypotheses = self.generator.generate_batch(self.sample_gaps, use_llm=False)
        
        self.assertEqual(len(hypotheses), 2)
        self.assertEqual(self.generator.state['total_generated'], 2)
        
        # Check all gaps were processed
        gap_ids = [h['gap_id'] for h in hypotheses]
        self.assertIn('GAP-001', gap_ids)
        self.assertIn('GAP-002', gap_ids)
    
    def test_get_hypotheses(self):
        """Test hypothesis retrieval."""
        # Generate some hypotheses
        self.generator.generate_batch(self.sample_gaps, use_llm=False)
        
        # Get all
        all_hyps = self.generator.get_hypotheses()
        self.assertEqual(len(all_hyps), 2)
        
        # Get by status
        pending = self.generator.get_hypotheses(status='pending')
        self.assertEqual(len(pending), 2)
        
        deployed = self.generator.get_hypotheses(status='deployed')
        self.assertEqual(len(deployed), 0)
    
    def test_deploy_hypothesis(self):
        """Test hypothesis deployment."""
        # Generate and deploy
        hypotheses = self.generator.generate_batch([self.sample_gaps[0]], use_llm=False)
        hyp_id = hypotheses[0]['id']
        
        success = self.generator.deploy_hypothesis(hyp_id)
        self.assertTrue(success)
        
        # Verify deployment
        deployed = self.generator.get_hypotheses(status='deployed')
        self.assertEqual(len(deployed), 1)
        self.assertEqual(deployed[0]['id'], hyp_id)
        self.assertEqual(self.generator.state['total_deployed'], 1)
    
    def test_deploy_nonexistent(self):
        """Test deploying nonexistent hypothesis."""
        success = self.generator.deploy_hypothesis("HYP-NONEXISTENT")
        self.assertFalse(success)
    
    def test_get_statistics(self):
        """Test statistics generation."""
        # Generate and deploy some hypotheses
        self.generator.generate_batch(self.sample_gaps, use_llm=False)
        hypotheses = self.generator.get_hypotheses()
        if hypotheses:
            self.generator.deploy_hypothesis(hypotheses[0]['id'])
        
        stats = self.generator.get_statistics()
        
        self.assertIn('total_generated', stats)
        self.assertIn('total_deployed', stats)
        self.assertIn('by_status', stats)
        self.assertIn('by_priority', stats)
        self.assertIn('by_method', stats)
        self.assertEqual(stats['total_generated'], 2)
        self.assertEqual(stats['total_deployed'], 1)
    
    def test_state_persistence(self):
        """Test state persistence across instances."""
        # Generate hypotheses
        self.generator.generate_batch([self.sample_gaps[0]], use_llm=False)
        self.generator._save_state()
        
        # Create new instance with same directory
        from memory_llm_hypothesis import LLMHypothesisGenerator
        generator2 = LLMHypothesisGenerator(self.test_dir)
        
        # State should be loaded
        self.assertEqual(generator2.state['total_generated'], 1)
        self.assertEqual(len(generator2.get_hypotheses()), 1)
    
    def test_export_report(self):
        """Test report export."""
        # Generate some data
        self.generator.generate_batch(self.sample_gaps, use_llm=False)
        
        # Export report
        report_path = self.generator.export_report()
        
        # Verify file exists
        self.assertTrue(Path(report_path).exists())
        
        # Verify content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("LLM Hypothesis Generation Report", content)
            self.assertIn("Pattern Diversity", content)
            self.assertIn("Hypothesis Quality", content)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def setUp(self):
        from memory_llm_hypothesis import LLMHypothesisGenerator
        self.test_dir = tempfile.mkdtemp()
        self.generator = LLMHypothesisGenerator(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_full_workflow(self):
        """Test complete workflow."""
        # 1. Generate hypotheses
        gaps = [
            {"id": "GAP-001", "name": "Test Gap 1"},
            {"id": "GAP-002", "name": "Test Gap 2"},
            {"id": "GAP-003", "name": "Test Gap 3"}
        ]
        
        hypotheses = self.generator.generate_batch(gaps, use_llm=False)
        self.assertEqual(len(hypotheses), 3)
        
        # 2. Check statistics
        stats = self.generator.get_statistics()
        self.assertEqual(stats['total_generated'], 3)
        self.assertEqual(stats['total_deployed'], 0)
        
        # 3. Deploy some
        self.generator.deploy_hypothesis(hypotheses[0]['id'])
        self.generator.deploy_hypothesis(hypotheses[1]['id'])
        
        # 4. Verify deployment
        stats = self.generator.get_statistics()
        self.assertEqual(stats['total_deployed'], 2)
        
        # 5. Export report
        report_path = self.generator.export_report()
        self.assertTrue(Path(report_path).exists())


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestOllamaClient))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMHypothesisGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
