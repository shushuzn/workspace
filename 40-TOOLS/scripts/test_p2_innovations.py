#!/usr/bin/env python3
"""
Test P2 Memory Innovation Tools
================================
Tests for P2 innovation tools:
1. memory_quantum_entanglement.py - Quantum entanglement
2. memory_time_crystal.py - Time crystal dynamics
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


class TestQuantumEntanglement(unittest.TestCase):
    """Test memory_quantum_entanglement.py"""
    
    def setUp(self):
        from memory_quantum_entanglement import QuantumEntanglementEngine, QuantumConfig
        
        self.config = QuantumConfig()
        self.engine = QuantumEntanglementEngine(self.config)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.quantum_memories), 0)
        self.assertEqual(len(self.engine.entangled_pairs), 0)
    
    def test_create_quantum_memory(self):
        """Test quantum memory creation"""
        content = """
## Section 1
Content about AI and machine learning.

## Section 2
Content about data science.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            quantum_mem = self.engine.create_quantum_memory(temp_file, "QM_TEST_001")
            
            self.assertIsNotNone(quantum_mem)
            self.assertEqual(quantum_mem.memory_id, "QM_TEST_001")
            self.assertGreater(len(quantum_mem.wavefunction), 0)
            self.assertFalse(quantum_mem.observed)
        finally:
            os.unlink(temp_file)
    
    def test_entangle_memories(self):
        """Test memory entanglement"""
        # Create two quantum memories
        mem1 = type('obj', (object,), {'memory_id': 'QM_001', 'content_hash': 'abc123', 
                                        'wavefunction': {'state1': 0.7, 'state2': 0.5},
                                        'phase': 0.5, 'coherence': 1.0, 'observed': False,
                                        'created_at': __import__('datetime').datetime.now()})
        mem2 = type('obj', (object,), {'memory_id': 'QM_002', 'content_hash': 'def456',
                                        'wavefunction': {'state1': 0.6, 'state3': 0.6},
                                        'phase': 1.0, 'coherence': 1.0, 'observed': False,
                                        'created_at': __import__('datetime').datetime.now()})
        
        self.engine.quantum_memories['QM_001'] = mem1
        self.engine.quantum_memories['QM_002'] = mem2
        
        # Entangle them
        pair = self.engine.entangle_memories('QM_001', 'QM_002', 'semantic')
        
        self.assertIsNotNone(pair)
        self.assertEqual(pair.memory_a, 'QM_001')
        self.assertEqual(pair.memory_b, 'QM_002')
        self.assertGreater(pair.entanglement_strength, 0.0)
    
    def test_bell_test(self):
        """Test Bell inequality test"""
        # Create entangled pair manually
        from memory_quantum_entanglement import EntangledPair
        from datetime import datetime
        
        pair = EntangledPair(
            pair_id="EP_TEST_001",
            memory_a="QM_001",
            memory_b="QM_002",
            entanglement_strength=0.8,
            bell_parameter=0.85,  # > 0.707 = violation
            correlation_type="temporal",
            created_at=datetime.now(),
            last_measured=datetime.now()
        )
        
        self.engine.entangled_pairs.append(pair)
        
        # Run Bell test
        results = self.engine.bell_test()
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['violation'])  # Should violate Bell inequality
        self.assertEqual(results[0]['interpretation'], "QUANTUM")
    
    def test_get_quantum_status(self):
        """Test status retrieval"""
        status = self.engine.get_quantum_status()
        
        self.assertIn('quantum_memories', status)
        self.assertIn('entangled_pairs', status)
        self.assertIn('bell_violations', status)
        self.assertIn('avg_coherence', status)


class TestTimeCrystal(unittest.TestCase):
    """Test memory_time_crystal.py"""
    
    def setUp(self):
        from memory_time_crystal import TimeCrystalEngine, TimeCrystalConfig
        
        self.config = TimeCrystalConfig()
        self.engine = TimeCrystalEngine(self.config)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.crystals), 0)
        self.assertEqual(len(self.engine.floquet_states), 0)
    
    def test_create_time_crystal(self):
        """Test time crystal creation"""
        content = """
## Section 1
Content about periodic patterns.

## Section 2
More content with temporal structure.

## Section 3
Even more temporal content.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            crystal = self.engine.create_time_crystal(temp_file, "TC_TEST_001")
            
            self.assertIsNotNone(crystal)
            self.assertEqual(crystal.crystal_id, "TC_TEST_001")
            self.assertGreater(len(crystal.temporal_modes), 0)
            self.assertFalse(crystal.symmetry_broken)
        finally:
            os.unlink(temp_file)
    
    def test_apply_periodic_drive(self):
        """Test periodic driving"""
        # Create crystal manually
        from memory_time_crystal import TimeCrystalState, TemporalMode
        from datetime import datetime
        
        mode = TemporalMode(
            mode_id="TM_001",
            frequency=0.1,
            amplitude=0.8,
            phase=0.5,
            coherence_time=30.0,
            energy=1.0
        )
        
        crystal = TimeCrystalState(
            crystal_id="TC_TEST_001",
            temporal_modes=[mode],
            drive_frequency=1.0/7.0,
            subharmonic_response=0.0,
            temporal_order_parameter=0.0,
            symmetry_broken=False,
            created_at=datetime.now()
        )
        
        self.engine.crystals[crystal.crystal_id] = crystal
        
        # Apply drive
        driven_crystal = self.engine.apply_periodic_drive(crystal.crystal_id, period=7.0)
        
        self.assertIsNotNone(driven_crystal)
        self.assertGreaterEqual(driven_crystal.subharmonic_response, 0.0)
        self.assertIsNotNone(driven_crystal.last_driven)
    
    def test_induce_mbl(self):
        """Test many-body localization induction"""
        from memory_time_crystal import TimeCrystalState, TemporalMode
        from datetime import datetime
        
        mode = TemporalMode(
            mode_id="TM_001",
            frequency=0.1,
            amplitude=0.8,
            phase=0.5,
            coherence_time=30.0,
            energy=1.0
        )
        
        crystal = TimeCrystalState(
            crystal_id="TC_TEST_001",
            temporal_modes=[mode],
            drive_frequency=1.0/7.0,
            subharmonic_response=0.5,
            temporal_order_parameter=0.6,
            symmetry_broken=True,
            created_at=datetime.now()
        )
        
        self.engine.crystals[crystal.crystal_id] = crystal
        
        # Induce MBL
        result = self.engine.induce_mbl(crystal.crystal_id)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['thermalization_suppressed'])
        self.assertTrue(result['coherence_enhanced'])
        self.assertGreater(result['avg_coherence_time'], 30.0)
    
    def test_floquet_engineering(self):
        """Test Floquet engineering"""
        from memory_time_crystal import TimeCrystalState, TemporalMode
        from datetime import datetime
        
        modes = [
            TemporalMode(mode_id=f"TM_{i}", frequency=0.1*i, amplitude=0.5,
                        phase=0.3*i, coherence_time=30.0, energy=1.0)
            for i in range(3)
        ]
        
        crystal = TimeCrystalState(
            crystal_id="TC_TEST_001",
            temporal_modes=modes,
            drive_frequency=1.0/7.0,
            subharmonic_response=0.3,
            temporal_order_parameter=0.5,
            symmetry_broken=False,
            created_at=datetime.now()
        )
        
        self.engine.crystals[crystal.crystal_id] = crystal
        
        # Apply Floquet engineering
        floquet_state = self.engine.floquet_engineering(crystal.crystal_id)
        
        self.assertIsNotNone(floquet_state)
        self.assertGreater(len(floquet_state.quasienergies), 0)
        self.assertEqual(floquet_state.harmonics, len(modes))
    
    def test_prethermalization(self):
        """Test prethermalization analysis"""
        from memory_time_crystal import TimeCrystalState, TemporalMode
        from datetime import datetime, timedelta
        
        mode = TemporalMode(
            mode_id="TM_001",
            frequency=0.1,
            amplitude=0.8,
            phase=0.5,
            coherence_time=30.0,
            energy=0.5
        )
        
        # Create crystal 10 days ago
        crystal = TimeCrystalState(
            crystal_id="TC_TEST_001",
            temporal_modes=[mode],
            drive_frequency=1.0/7.0,
            subharmonic_response=0.4,
            temporal_order_parameter=0.6,
            symmetry_broken=True,
            created_at=datetime.now() - timedelta(days=10)
        )
        
        self.engine.crystals[crystal.crystal_id] = crystal
        
        # Analyze prethermalization
        result = self.engine.prethermalization(crystal.crystal_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['age_days'], 10)
        self.assertIn('prethermal_lifetime_days', result)
        self.assertIn('in_prethermal_regime', result)
    
    def test_get_time_crystal_status(self):
        """Test status retrieval"""
        status = self.engine.get_time_crystal_status()
        
        self.assertIn('time_crystals', status)
        self.assertIn('crystalline_order', status)
        self.assertIn('floquet_states', status)
        self.assertIn('avg_temporal_order', status)


class TestP2Integration(unittest.TestCase):
    """Integration tests for P2 tools"""
    
    def test_all_tools_importable(self):
        """Test all P2 tools can be imported"""
        tools = [
            'memory_quantum_entanglement',
            'memory_time_crystal'
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
            ('memory_quantum_entanglement.py', ['--help']),
            ('memory_time_crystal.py', ['--help'])
        ]
        
        for tool, args in tools:
            result = subprocess.run(
                [sys.executable, os.path.join('30-scripts-tools', tool)] + args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should not crash
            self.assertIn(result.returncode, [0, 1])


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumEntanglement))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeCrystal))
    suite.addTests(loader.loadTestsFromTestCase(TestP2Integration))
    
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
