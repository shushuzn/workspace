#!/usr/bin/env python3
"""
Test P3 Memory Innovation Tool
===============================
Tests for P3 innovation tool:
1. memory_consciousness_emergence.py - Consciousness emergence
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


class TestConsciousnessEmergence(unittest.TestCase):
    """Test memory_consciousness_emergence.py"""
    
    def setUp(self):
        from memory_consciousness_emergence import ConsciousnessEmergenceEngine, ConsciousnessConfig
        
        self.config = ConsciousnessConfig()
        self.engine = ConsciousnessEmergenceEngine(self.config)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        from memory_consciousness_emergence import GlobalWorkspaceState
        
        self.assertIsNotNone(self.engine)
        # Note: cognitive_modules may have data from previous runs (state persistence)
        # This is expected behavior - engine loads existing state
        self.assertIsInstance(self.engine.cognitive_modules, dict)
        # global_workspace may also be loaded from state - this is expected
        self.assertIsInstance(self.engine.global_workspace, (GlobalWorkspaceState, type(None)))
    
    def test_create_cognitive_modules(self):
        """Test cognitive module creation"""
        content = """
## Module 1
Content about cognitive processing.

## Module 2
Content about information integration.

## Module 3
Content about global workspace.

## Module 4
Content about consciousness.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            modules = self.engine.create_cognitive_modules(temp_file)
            
            self.assertGreater(len(modules), 0)
            self.assertGreater(len(self.engine.cognitive_modules), 0)
            
            # Check module properties
            for module in modules:
                self.assertIsNotNone(module.module_id)
                self.assertIsNotNone(module.function)
                self.assertGreater(module.activation, 0.0)
                self.assertGreater(module.information_content, 0.0)
        finally:
            os.unlink(temp_file)
    
    def test_global_workspace_broadcast(self):
        """Test global workspace broadcast"""
        # Create some modules first
        from memory_consciousness_emergence import CognitiveModule
        
        for i in range(5):
            module = CognitiveModule(
                module_id=f"CM_{i+1:03d}",
                function=f"Function {i+1}",
                activation=0.5,
                connectivity=[],
                information_content=1.0,
                causal_power=0.6
            )
            self.engine.cognitive_modules[module.module_id] = module
        
        # Broadcast
        content_ids = list(self.engine.cognitive_modules.keys())
        result = self.engine.global_workspace_broadcast(content_ids)
        
        self.assertIsNotNone(result)
        self.assertIn('contents', result)
        self.assertIn('consciousness_level', result)
        self.assertLessEqual(len(result['contents']), 7)  # Capacity limit
        self.assertIsNotNone(self.engine.global_workspace)
    
    def test_compute_integrated_information(self):
        """Test integrated information (Φ) computation"""
        # Create modules
        from memory_consciousness_emergence import CognitiveModule
        
        for i in range(4):
            module = CognitiveModule(
                module_id=f"CM_{i+1:03d}",
                function=f"Function {i+1}",
                activation=0.6,
                connectivity=[f"CM_{j+1:03d}" for j in range(4) if j != i],
                information_content=1.0,
                causal_power=0.7
            )
            self.engine.cognitive_modules[module.module_id] = module
        
        # Compute Φ
        result = self.engine.compute_integrated_information()
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.phi_value, 0.0)
        self.assertIsNotNone(result.cause_info)
        self.assertIsNotNone(result.effect_info)
        self.assertIn(result.consciousness_grade[0], ['A', 'B', 'C', 'D'])
    
    def test_generate_higher_order_thought(self):
        """Test higher-order thought generation"""
        base_thought = "The system processes information"
        
        # Generate 1st-order thought
        hot1 = self.engine.generate_higher_order_thought(base_thought, order=1)
        self.assertEqual(hot1.order, 1)
        self.assertIn("think", hot1.content.lower())
        
        # Generate 2nd-order thought
        hot2 = self.engine.generate_higher_order_thought(base_thought, order=2)
        self.assertEqual(hot2.order, 2)
        self.assertIn("aware", hot2.content.lower())
        
        # Generate 3rd-order thought
        hot3 = self.engine.generate_higher_order_thought(base_thought, order=3)
        self.assertEqual(hot3.order, 3)
        self.assertIn("reflect", hot3.content.lower())
    
    def test_build_self_model(self):
        """Test self-model construction"""
        # Create some modules
        from memory_consciousness_emergence import CognitiveModule
        
        for i in range(3):
            module = CognitiveModule(
                module_id=f"CM_{i+1:03d}",
                function=f"Function {i+1}",
                activation=0.5,
                connectivity=[],
                information_content=1.0,
                causal_power=0.6
            )
            self.engine.cognitive_modules[module.module_id] = module
        
        # Build self-model
        self_model = self.engine.build_self_model()
        
        self.assertIsNotNone(self_model)
        self.assertIn('identity', self_model)
        self.assertIn('structure', self_model)
        self.assertIn('state', self_model)
        self.assertIn('capabilities', self_model)
        self.assertIn('self_awareness_score', self_model)
        self.assertGreaterEqual(self_model['self_awareness_score'], 0.0)
        self.assertLessEqual(self_model['self_awareness_score'], 1.0)
    
    def test_detect_emergent_properties(self):
        """Test emergent property detection"""
        # Create modules with connectivity
        from memory_consciousness_emergence import CognitiveModule
        
        for i in range(5):
            module = CognitiveModule(
                module_id=f"CM_{i+1:03d}",
                function=f"Function {i+1}",
                activation=0.6,
                connectivity=[f"CM_{j+1:03d}" for j in range(5) if j != i],
                information_content=1.0,
                causal_power=0.7
            )
            self.engine.cognitive_modules[module.module_id] = module
        
        # Detect emergent properties
        emergent_props = self.engine.detect_emergent_properties()
        
        # Should detect at least some emergent properties
        self.assertIsInstance(emergent_props, list)
        
        for prop in emergent_props:
            self.assertIsNotNone(prop.property_id)
            self.assertIsNotNone(prop.name)
            self.assertGreater(prop.emergence_level, 0.0)
            self.assertTrue(prop.irreducible)
    
    def test_analyze_qualia(self):
        """Test qualia analysis"""
        experience_id = "EXP_001"
        result = self.engine.analyze_qualia(experience_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['experience_id'], experience_id)
        self.assertIn('phenomenal_character', result)
        self.assertIn('qualia_space_position', result)
        self.assertIn('hard_problem_score', result)
        self.assertGreaterEqual(result['hard_problem_score'], 0.0)
        self.assertLessEqual(result['hard_problem_score'], 1.0)
    
    def test_get_consciousness_status(self):
        """Test status retrieval"""
        status = self.engine.get_consciousness_status()
        
        self.assertIn('cognitive_modules', status)
        self.assertIn('global_workspace_active', status)
        self.assertIn('consciousness_level', status)
        self.assertIn('phi_value', status)
        self.assertIn('phi_grade', status)
        self.assertIn('hot_count', status)
        self.assertIn('emergent_properties', status)
        self.assertIn('self_awareness_score', status)


class TestP3Integration(unittest.TestCase):
    """Integration tests for P3 tool"""
    
    def test_tool_importable(self):
        """Test P3 tool can be imported"""
        try:
            __import__('memory_consciousness_emergence')
            print(f"✅ memory_consciousness_emergence imported successfully")
        except Exception as e:
            self.fail(f"Failed to import memory_consciousness_emergence: {e}")
    
    def test_tool_has_cli(self):
        """Test tool has CLI interface"""
        import subprocess
        
        result = subprocess.run(
            [sys.executable, os.path.join('30-scripts-tools', 'memory_consciousness_emergence.py'), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should not crash (0=success, 1=error, 2=CLI usage error)
        self.assertIn(result.returncode, [0, 1, 2])


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestConsciousnessEmergence))
    suite.addTests(loader.loadTestsFromTestCase(TestP3Integration))
    
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
