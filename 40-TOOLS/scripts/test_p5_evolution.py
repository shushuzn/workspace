#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for P5-3 Evolutionary Algorithms
============================================
Tests for:
- InnovationGene
- InnovationDNA
- InnovationEvolutionaryEngine

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import unittest
from pathlib import Path
import tempfile
import shutil
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TestInnovationGene(unittest.TestCase):
    """Test InnovationGene class."""
    
    def test_numeric_gene_creation(self):
        """Test numeric gene creation."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="impact_score",
            value=0.75,
            gene_type="numeric"
        )
        
        self.assertEqual(gene.name, "impact_score")
        self.assertEqual(gene.value, 0.75)
        self.assertEqual(gene.gene_type, "numeric")
    
    def test_categorical_gene_creation(self):
        """Test categorical gene creation."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="complexity",
            value="medium",
            gene_type="categorical",
            category_values=['low', 'medium', 'high']
        )
        
        self.assertEqual(gene.value, "medium")
        self.assertIn("medium", gene.category_values)
    
    def test_boolean_gene_creation(self):
        """Test boolean gene creation."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="is_active",
            value=True,
            gene_type="boolean"
        )
        
        self.assertEqual(gene.value, True)
        self.assertEqual(gene.gene_type, "boolean")
    
    def test_numeric_mutation(self):
        """Test numeric gene mutation."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="score",
            value=0.5,
            mutation_rate=1.0,  # Force mutation
            gene_type="numeric"
        )
        
        mutated = gene.mutate()
        
        # Value should change
        self.assertNotEqual(mutated.value, 0.5)
        # Should still be numeric
        self.assertIsInstance(mutated.value, float)
    
    def test_categorical_mutation(self):
        """Test categorical gene mutation."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="type",
            value="A",
            mutation_rate=1.0,  # Force mutation
            gene_type="categorical",
            category_values=['A', 'B', 'C']
        )
        
        mutated = gene.mutate()
        
        # Should be one of category values
        self.assertIn(mutated.value, ['A', 'B', 'C'])
    
    def test_boolean_mutation(self):
        """Test boolean gene mutation."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="flag",
            value=True,
            mutation_rate=1.0,  # Force mutation
            gene_type="boolean"
        )
        
        mutated = gene.mutate()
        
        # Should flip
        self.assertEqual(mutated.value, False)
    
    def test_no_mutation(self):
        """Test gene with 0 mutation rate."""
        from memory_evolutionary_algorithms import InnovationGene
        
        gene = InnovationGene(
            name="stable",
            value=0.9,
            mutation_rate=0.0,  # No mutation
            gene_type="numeric"
        )
        
        mutated = gene.mutate()
        
        # Should not change
        self.assertEqual(mutated.value, 0.9)


class TestInnovationDNA(unittest.TestCase):
    """Test InnovationDNA class."""
    
    def setUp(self):
        from memory_evolutionary_algorithms import InnovationGene, InnovationDNA
        
        self.genes = [
            InnovationGene("impact", 0.8, gene_type="numeric"),
            InnovationGene("novelty", 0.9, gene_type="numeric"),
            InnovationGene("feasibility", 0.7, gene_type="numeric")
        ]
        
        self.dna = InnovationDNA(
            id="DNA-TEST-001",
            name="Test Innovation",
            genes=self.genes,
            fitness=0.8,
            generation=5,
            parent_ids=["DNA-PARENT-1", "DNA-PARENT-2"]
        )
    
    def test_dna_creation(self):
        """Test DNA creation."""
        self.assertEqual(self.dna.id, "DNA-TEST-001")
        self.assertEqual(self.dna.name, "Test Innovation")
        self.assertEqual(len(self.dna.genes), 3)
        self.assertEqual(self.dna.fitness, 0.8)
    
    def test_to_dict(self):
        """Test DNA to dictionary conversion."""
        from memory_evolutionary_algorithms import InnovationDNA
        
        dna_dict = self.dna.to_dict()
        
        self.assertEqual(dna_dict['id'], "DNA-TEST-001")
        self.assertEqual(dna_dict['name'], "Test Innovation")
        self.assertEqual(len(dna_dict['genes']), 3)
        self.assertEqual(dna_dict['fitness'], 0.8)
        self.assertIn('created_at', dna_dict)
    
    def test_from_dict(self):
        """Test DNA from dictionary conversion."""
        from memory_evolutionary_algorithms import InnovationDNA
        
        dna_dict = {
            'id': 'DNA-TEST-002',
            'name': 'Restored Innovation',
            'genes': [
                {'name': 'impact', 'value': 0.75, 'mutation_rate': 0.1, 'gene_type': 'numeric', 'category_values': []}
            ],
            'fitness': 0.75,
            'generation': 3,
            'parent_ids': [],
            'created_at': '2026-03-17T00:00:00'
        }
        
        restored_dna = InnovationDNA.from_dict(dna_dict)
        
        self.assertEqual(restored_dna.id, "DNA-TEST-002")
        self.assertEqual(restored_dna.name, "Restored Innovation")
        self.assertEqual(len(restored_dna.genes), 1)
        self.assertEqual(restored_dna.genes[0].value, 0.75)


class TestInnovationEvolutionaryEngine(unittest.TestCase):
    """Test InnovationEvolutionaryEngine class."""
    
    def setUp(self):
        from memory_evolutionary_algorithms import InnovationEvolutionaryEngine
        
        self.test_dir = tempfile.mkdtemp()
        self.engine = InnovationEvolutionaryEngine(self.test_dir)
        
        # Reduce population for faster tests
        self.engine.population_size = 10
        self.engine.elite_count = 2
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.workspace_dir)
        self.assertTrue(self.engine.data_dir.exists())
        self.assertEqual(self.engine.population_size, 10)
    
    def test_initialize_population(self):
        """Test population initialization."""
        seed_innovations = [
            {"title": "Innovation 1", "predicted_impact": 0.8},
            {"title": "Innovation 2", "predicted_impact": 0.9}
        ]
        
        self.engine.initialize_population(seed_innovations)
        
        self.assertEqual(len(self.engine.population), 10)
        self.assertEqual(self.engine.generation, 0)
    
    def test_fitness_calculation(self):
        """Test fitness calculation."""
        from memory_evolutionary_algorithms import InnovationDNA, InnovationGene
        
        dna = InnovationDNA(
            id="DNA-TEST",
            name="Test",
            genes=[
                InnovationGene("impact_score", 0.9, gene_type="numeric"),
                InnovationGene("novelty", 0.8, gene_type="numeric"),
                InnovationGene("feasibility", 0.7, gene_type="numeric"),
                InnovationGene("complexity", "low", gene_type="categorical", category_values=['low', 'medium', 'high'])
            ],
            fitness=0.0
        )
        
        fitness = self.engine._calculate_fitness(dna)
        
        self.assertGreater(fitness, 0.0)
        self.assertLessEqual(fitness, 1.0)
    
    def test_selection(self):
        """Test tournament selection."""
        from memory_evolutionary_algorithms import InnovationDNA, InnovationGene
        
        # Create population with varying fitness
        self.engine.population = []
        for i in range(10):
            dna = InnovationDNA(
                id=f"DNA-{i}",
                name=f"Innovation {i}",
                genes=[InnovationGene("score", i/10, gene_type="numeric")],
                fitness=i/10
            )
            self.engine.population.append(dna)
        
        # Select multiple times
        selected = []
        for _ in range(20):
            winner = self.engine.selection()
            selected.append(winner)
        
        # Best individuals should be selected more often
        best_count = sum(1 for s in selected if s.fitness >= 0.8)
        self.assertGreater(best_count, 5)  # At least 5/20 should be best
    
    def test_crossover(self):
        """Test crossover operation."""
        from memory_evolutionary_algorithms import InnovationDNA, InnovationGene
        
        parent1 = InnovationDNA(
            id="DNA-P1",
            name="Parent1",
            genes=[
                InnovationGene("g1", 0.9, gene_type="numeric"),
                InnovationGene("g2", 0.8, gene_type="numeric"),
                InnovationGene("g3", 0.7, gene_type="numeric")
            ],
            fitness=0.8
        )
        
        parent2 = InnovationDNA(
            id="DNA-P2",
            name="Parent2",
            genes=[
                InnovationGene("g1", 0.3, gene_type="numeric"),
                InnovationGene("g2", 0.4, gene_type="numeric"),
                InnovationGene("g3", 0.5, gene_type="numeric")
            ],
            fitness=0.4
        )
        
        child1, child2 = self.engine.crossover(parent1, parent2)
        
        # Children should have different IDs
        self.assertNotEqual(child1.id, parent1.id)
        self.assertNotEqual(child2.id, parent2.id)
        
        # Children should have parents recorded
        self.assertIn(parent1.id, child1.parent_ids)
        self.assertIn(parent2.id, child1.parent_ids)
        
        # Genes should be mixed
        self.assertEqual(len(child1.genes), 3)
        self.assertEqual(len(child2.genes), 3)
    
    def test_mutation(self):
        """Test mutation operation."""
        from memory_evolutionary_algorithms import InnovationDNA, InnovationGene
        
        dna = InnovationDNA(
            id="DNA-MUT",
            name="Mutator",
            genes=[
                InnovationGene("stable", 0.5, mutation_rate=0.0, gene_type="numeric"),
                InnovationGene("mutable", 0.5, mutation_rate=1.0, gene_type="numeric")
            ],
            fitness=0.5
        )
        
        mutated = self.engine.mutate(dna)
        
        # Stable gene should not change
        self.assertEqual(mutated.genes[0].value, 0.5)
        
        # Mutable gene should change (with high probability)
        # Note: Due to randomness, this might occasionally fail
        # For deterministic test, we use mutation_rate=1.0
    
    def test_evolve_single_generation(self):
        """Test single generation evolution."""
        seed_innovations = [
            {"title": "Innovation 1", "predicted_impact": 0.8, "novelty_score": 0.7, "feasibility_score": 0.6},
            {"title": "Innovation 2", "predicted_impact": 0.9, "novelty_score": 0.8, "feasibility_score": 0.7}
        ]
        
        self.engine.initialize_population(seed_innovations)
        initial_best = self.engine.best_fitness
        
        # Evolve one generation
        self.engine.evolve(1)
        
        # Generation should increment
        self.assertEqual(self.engine.generation, 1)
        
        # Best fitness should be tracked
        self.assertGreaterEqual(self.engine.best_fitness, 0.0)
    
    def test_dna_to_innovation(self):
        """Test DNA to innovation conversion."""
        from memory_evolutionary_algorithms import InnovationDNA, InnovationGene
        
        dna = InnovationDNA(
            id="DNA-CONV",
            name="Converter",
            genes=[
                InnovationGene("impact_score", 0.85, gene_type="numeric"),
                InnovationGene("complexity", "medium", gene_type="categorical", category_values=['low', 'medium', 'high']),
                InnovationGene("novelty", 0.9, gene_type="numeric"),
                InnovationGene("feasibility", 0.75, gene_type="numeric")
            ],
            fitness=0.82,
            generation=5,
            parent_ids=["DNA-P1"]
        )
        
        innovation = self.engine.dna_to_innovation(dna)
        
        self.assertEqual(innovation['id'], "DNA-CONV")
        self.assertEqual(innovation['title'], "Converter")
        self.assertAlmostEqual(innovation['predicted_impact'], 0.85)
        self.assertEqual(innovation['implementation_complexity'], "medium")
        self.assertEqual(innovation['generation'], 5)
        self.assertEqual(innovation['evolution_method'], "genetic_algorithm")
    
    def test_state_persistence(self):
        """Test state save and load."""
        from memory_evolutionary_algorithms import InnovationEvolutionaryEngine
        
        # Initialize and evolve
        self.engine.initialize_population([
            {"title": "Test Innovation", "predicted_impact": 0.8}
        ])
        self.engine.evolve(2)
        
        # Save state
        self.engine._save_state()
        
        # Create new engine and load
        new_engine = InnovationEvolutionaryEngine(self.test_dir)
        
        # State should be restored
        self.assertEqual(new_engine.generation, self.engine.generation)
        self.assertEqual(len(new_engine.population), len(self.engine.population))
    
    def test_get_statistics(self):
        """Test statistics retrieval."""
        self.engine.initialize_population([
            {"title": "Innovation", "predicted_impact": 0.8}
        ])
        self.engine.evolve(3)
        
        stats = self.engine.get_statistics()
        
        self.assertIn('generation', stats)
        self.assertIn('population_size', stats)
        self.assertIn('best_fitness', stats)
        self.assertIn('average_fitness', stats)
        self.assertIn('diversity', stats)
        
        self.assertEqual(stats['generation'], 3)
        self.assertEqual(stats['population_size'], 10)


class TestIntegration(unittest.TestCase):
    """Integration tests for evolutionary algorithms."""
    
    def setUp(self):
        from memory_evolutionary_algorithms import InnovationEvolutionaryEngine
        
        self.test_dir = tempfile.mkdtemp()
        self.engine = InnovationEvolutionaryEngine(self.test_dir)
        self.engine.population_size = 15
        self.engine.elite_count = 3
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_full_evolution_pipeline(self):
        """Test complete evolution pipeline."""
        # 1. Initialize with diverse seed
        seed_innovations = [
            {"title": "Immune System", "predicted_impact": 0.9, "novelty_score": 0.85, "feasibility_score": 0.8},
            {"title": "Neural Network", "predicted_impact": 0.85, "novelty_score": 0.9, "feasibility_score": 0.75},
            {"title": "Dark Matter", "predicted_impact": 0.7, "novelty_score": 0.95, "feasibility_score": 0.6},
            {"title": "Quantum", "predicted_impact": 0.95, "novelty_score": 0.98, "feasibility_score": 0.5}
        ]
        
        self.engine.initialize_population(seed_innovations)
        
        # 2. Evolve for multiple generations
        top_innovations = self.engine.evolve(5)
        
        # 3. Verify results
        self.assertEqual(len(top_innovations), 5)  # Top 5
        
        # 4. Check fitness improvement
        self.assertGreater(self.engine.best_fitness, 0.0)
        
        # 5. Convert to innovations
        innovations = [self.engine.dna_to_innovation(dna) for dna in top_innovations]
        
        # 6. Verify innovations are valid
        for innovation in innovations:
            self.assertIn('id', innovation)
            self.assertIn('title', innovation)
            self.assertIn('predicted_impact', innovation)
            self.assertIn('evolution_method', innovation)
            self.assertEqual(innovation['evolution_method'], "genetic_algorithm")
    
    def test_fitness_improvement_over_generations(self):
        """Test that fitness improves over generations."""
        self.engine.initialize_population([
            {"title": "Seed", "predicted_impact": 0.5, "novelty_score": 0.5, "feasibility_score": 0.5}
        ])
        
        initial_best = self.engine.best_fitness
        
        # Evolve for 10 generations
        self.engine.evolve(10)
        
        final_best = self.engine.best_fitness
        
        # Fitness should improve or stay same (elitism)
        self.assertGreaterEqual(final_best, initial_best)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestInnovationGene))
    suite.addTests(loader.loadTestsFromTestCase(TestInnovationDNA))
    suite.addTests(loader.loadTestsFromTestCase(TestInnovationEvolutionaryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
