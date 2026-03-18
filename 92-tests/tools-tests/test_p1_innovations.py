#!/usr/bin/env python3
"""
Test P1 Memory Innovation Tools
================================
Tests for P1 innovation tools:
1. memory_dark_matter.py - Dark matter detection
2. memory_topological_analysis.py - TDA
3. memory_thermodynamics.py - Thermodynamics
4. memory_fractal_compression.py - Fractal compression
5. memory_causal_discovery.py - Causal discovery
"""

import os
import sys
import unittest
import tempfile
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add tools to path
sys.path.insert(0, os.path.dirname(__file__))


class TestDarkMatterDetector(unittest.TestCase):
    """Test memory_dark_matter.py"""
    
    def setUp(self):
        from memory_dark_matter import DarkMatterDetector, DarkMatterConfig
        
        self.config = DarkMatterConfig()
        self.detector = DarkMatterDetector(self.config)
    
    def test_detector_initialization(self):
        """Test detector initializes correctly"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(len(self.detector.candidates), 0)
    
    def test_extract_topics(self):
        """Test topic extraction"""
        content = """
## Topic 1
Some content about **machine learning**
#tag1

## Topic 2
More content about **deep learning**
#tag2
"""
        topics = self.detector._extract_topics(content)
        
        self.assertGreater(len(topics), 0)
        self.assertIn('Topic 1', topics)
        self.assertIn('Topic 2', topics)
    
    def test_cluster_topics(self):
        """Test topic clustering"""
        topics = ['apple', 'apricot', 'banana', 'blueberry', 'carrot']
        clusters = self.detector._cluster_topics(topics)
        
        self.assertGreater(len(clusters), 0)
        # 'apple' and 'apricot' should be in same cluster (both start with 'a')
    
    def test_get_status(self):
        """Test status retrieval"""
        status = self.detector.get_status()
        
        self.assertIn('total_candidates', status)
        self.assertIn('by_type', status)
        self.assertIn('by_priority', status)


class TestTopologicalAnalyzer(unittest.TestCase):
    """Test memory_topological_analysis.py"""
    
    def setUp(self):
        from memory_topological_analysis import TopologicalAnalyzer, TopologyConfig
        
        self.config = TopologyConfig()
        self.analyzer = TopologicalAnalyzer(self.config)
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.features), 0)
    
    def test_extract_memory_points(self):
        """Test memory point extraction"""
        content = """
## Section 1
This is content about AI and machine learning.

## Section 2
This is content about data science and statistics.
"""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            points = self.analyzer._extract_memory_points(temp_file)
            
            self.assertGreater(len(points), 0)
            self.assertIn('features', points[0])
            self.assertIn('dimension', points[0])
        finally:
            os.unlink(temp_file)
    
    def test_compute_distance_matrix(self):
        """Test distance matrix computation"""
        points = [
            {'id': 'p1', 'features': {'a': 0.5, 'b': 0.3}},
            {'id': 'p2', 'features': {'a': 0.6, 'b': 0.2}},
            {'id': 'p3', 'features': {'a': 0.1, 'b': 0.9}}
        ]
        
        matrix = self.analyzer._compute_distance_matrix(points)
        
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), 3)
        # Diagonal should be 0
        self.assertEqual(matrix[0][0], 0.0)
    
    def test_get_analysis_summary(self):
        """Test analysis summary"""
        summary = self.analyzer.get_analysis_summary()
        
        self.assertIn('total_features', summary)
        self.assertIn('by_dimension', summary)
        self.assertIn('mapper_nodes', summary)


class TestThermodynamicsEngine(unittest.TestCase):
    """Test memory_thermodynamics.py"""
    
    def setUp(self):
        from memory_thermodynamics import ThermodynamicsEngine, ThermodynamicsConfig
        
        self.config = ThermodynamicsConfig()
        self.engine = ThermodynamicsEngine(self.config)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertIsNone(self.engine.current_state)
    
    def test_compute_entropy(self):
        """Test entropy computation"""
        content = "This is test content with some words. " * 100
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            entropy = self.engine.compute_entropy(temp_file)
            
            self.assertGreater(entropy, 0.0)
            self.assertLessEqual(entropy, 1.0)
        finally:
            os.unlink(temp_file)
    
    def test_compute_internal_energy(self):
        """Test internal energy computation"""
        content = """
## Section 1
Content about AI [[machine-learning]] → deep learning

## Section 2
More content with **bold terms** #tags
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            energy = self.engine.compute_internal_energy(temp_file)
            
            self.assertGreater(energy, 0.0)
        finally:
            os.unlink(temp_file)
    
    def test_compute_free_energy(self):
        """Test free energy computation"""
        U = 10.0
        S = 0.5
        T = 300.0
        
        F = self.engine.compute_free_energy(U, S, T)
        
        # F = U - TS (normalized)
        self.assertIsInstance(F, float)
    
    def test_determine_phase(self):
        """Test phase determination"""
        # Low entropy, low temp = solid
        phase = self.engine.determine_phase(0.2, 200.0)
        self.assertEqual(phase, "solid")
        
        # High entropy, high temp = plasma
        phase = self.engine.determine_phase(0.9, 600.0)
        self.assertEqual(phase, "plasma")
    
    def test_get_status(self):
        """Test status retrieval"""
        status = self.engine.get_status()
        
        # Should handle no data gracefully
        self.assertIsInstance(status, dict)


class TestFractalCompressor(unittest.TestCase):
    """Test memory_fractal_compression.py"""
    
    def setUp(self):
        from memory_fractal_compression import FractalCompressor, FractalConfig
        
        self.config = FractalConfig()
        self.compressor = FractalCompressor(self.config)
    
    def test_compressor_initialization(self):
        """Test compressor initializes correctly"""
        self.assertIsNotNone(self.compressor)
        self.assertEqual(len(self.compressor.patterns), 0)
    
    def test_find_ngram_patterns(self):
        """Test n-gram pattern finding"""
        text = "the quick brown fox jumps over the lazy dog the"
        
        patterns = self.compressor._find_ngram_patterns(text, n=3)
        
        # "the" should appear multiple times
        self.assertGreater(len(patterns), 0)
    
    def test_find_section_patterns(self):
        """Test section pattern finding"""
        content = """
## Introduction
Some intro content

## Methods
Some methods content

## Results
Some results content

## Introduction Again
Repeated structure
"""
        patterns = self.compressor._find_section_patterns(content)
        
        # Should find some patterns
        self.assertIsInstance(patterns, dict)
    
    def test_compute_fractal_dimension(self):
        """Test fractal dimension computation"""
        content = "This is test content with various words. " * 50
        
        dimension = self.compressor.compute_fractal_dimension(content)
        
        self.assertGreaterEqual(dimension, 0.0)
        self.assertLessEqual(dimension, 2.0)  # Typical range
    
    def test_get_compression_stats(self):
        """Test compression stats"""
        stats = self.compressor.get_compression_stats()
        
        # Should handle no data gracefully
        self.assertIsInstance(stats, dict)


class TestCausalDiscoveryEngine(unittest.TestCase):
    """Test memory_causal_discovery.py"""
    
    def setUp(self):
        from memory_causal_discovery import CausalDiscoveryEngine, CausalConfig
        
        self.config = CausalConfig()
        self.engine = CausalDiscoveryEngine(self.config)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.links), 0)
    
    def test_extract_concepts(self):
        """Test concept extraction"""
        content = """
## Machine Learning
Content about **AI** and #technology

## Deep Learning
More about **neural networks**
"""
        concepts = self.engine._extract_concepts(content)
        
        self.assertGreater(len(concepts), 0)
        self.assertIn('Machine Learning', concepts)
    
    def test_discover_from_markers(self):
        """Test causal discovery from linguistic markers"""
        content = """
AI development led to new applications.
Because of better algorithms, performance improved.
Therefore, adoption increased significantly.
"""
        links = self.engine._discover_from_markers(content)
        
        self.assertGreater(len(links), 0)
        # Should find "led to", "because", "therefore"
    
    def test_deduplicate_links(self):
        """Test link deduplication"""
        from memory_causal_discovery import CausalLink
        
        links = [
            CausalLink(
                link_id="CL_001",
                cause="AI",
                effect="automation",
                confidence=0.7,
                evidence=["test"]
            ),
            CausalLink(
                link_id="CL_002",
                cause="AI",  # Same cause
                effect="automation",  # Same effect
                confidence=0.8,
                evidence=["test2"]
            )
        ]
        
        unique = self.engine._deduplicate_links(links)
        
        # Should merge into one link
        self.assertEqual(len(unique), 1)
        # Should keep higher confidence
        self.assertEqual(unique[0].confidence, 0.8)
    
    def test_get_causal_graph_summary(self):
        """Test graph summary"""
        summary = self.engine.get_causal_graph_summary()
        
        self.assertIn('total_nodes', summary)
        self.assertIn('total_links', summary)
        self.assertIn('root_causes', summary)


class TestP1Integration(unittest.TestCase):
    """Integration tests for P1 tools"""
    
    def test_all_tools_importable(self):
        """Test all P1 tools can be imported"""
        tools = [
            'memory_dark_matter',
            'memory_topological_analysis',
            'memory_thermodynamics',
            'memory_fractal_compression',
            'memory_causal_discovery'
        ]
        
        for tool in tools:
            try:
                __import__(tool)
                print(f"✅ {tool} imported successfully")
            except Exception as e:
                self.fail(f"Failed to import {tool}: {e}")
    
    def test_all_tools_have_cli(self):
        """Test all tools have CLI interface"""
        import subprocess
        
        tools = [
            ('memory_dark_matter.py', ['--help']),
            ('memory_topological_analysis.py', ['--help']),
            ('memory_thermodynamics.py', ['--help']),
            ('memory_fractal_compression.py', ['--help']),
            ('memory_causal_discovery.py', ['--help'])
        ]
        
        for tool, args in tools:
            result = subprocess.run(
                [sys.executable, os.path.join('30-scripts-tools', tool)] + args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should not crash
            self.assertIn(result.returncode, [0, 1])  # 0=success, 1=CLI help shown


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestDarkMatterDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestTopologicalAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestThermodynamicsEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestFractalCompressor))
    suite.addTests(loader.loadTestsFromTestCase(TestCausalDiscoveryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestP1Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
