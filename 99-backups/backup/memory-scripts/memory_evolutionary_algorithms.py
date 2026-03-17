#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Evolutionary Algorithms (P5-3)
=====================================
Apply genetic programming to innovation generation.

Features:
- Innovation DNA encoding
- Crossover operations
- Mutation mechanisms
- Selection & breeding
- Fitness function
- Population management

Version: 5.3.0
Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import random
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import copy

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


@dataclass
class InnovationGene:
    """Single gene in innovation DNA."""
    name: str
    value: Any
    mutation_rate: float = 0.1
    gene_type: str = "numeric"  # numeric, categorical, boolean
    category_values: List[Any] = field(default_factory=list)
    
    def mutate(self) -> 'InnovationGene':
        """Mutate this gene."""
        new_gene = copy.deepcopy(self)
        
        if random.random() > self.mutation_rate:
            return new_gene
        
        if self.gene_type == "numeric":
            # Gaussian mutation
            import math
            sigma = abs(self.value) * 0.1 if self.value != 0 else 0.1
            new_gene.value = self.value + random.gauss(0, sigma)
        elif self.gene_type == "categorical":
            if self.category_values:
                new_gene.value = random.choice(self.category_values)
        elif self.gene_type == "boolean":
            new_gene.value = not self.value
        
        return new_gene


@dataclass
class InnovationDNA:
    """Complete DNA sequence for an innovation."""
    id: str
    name: str
    genes: List[InnovationGene] = field(default_factory=list)
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'genes': [asdict(g) for g in self.genes],
            'fitness': self.fitness,
            'generation': self.generation,
            'parent_ids': self.parent_ids,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InnovationDNA':
        """Create from dictionary."""
        genes = [InnovationGene(**g) for g in data.get('genes', [])]
        return cls(
            id=data['id'],
            name=data['name'],
            genes=genes,
            fitness=data.get('fitness', 0.0),
            generation=data.get('generation', 0),
            parent_ids=data.get('parent_ids', []),
            created_at=data.get('created_at', datetime.now().isoformat())
        )


class InnovationEvolutionaryEngine:
    """Evolutionary engine for innovation generation."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path(__file__).parent.parent
        self.data_dir = self.workspace_dir / "data" / "evolution"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Population
        self.population: List[InnovationDNA] = []
        self.generation = 0
        self.best_fitness = 0.0
        
        # Configuration
        self.population_size = 20
        self.elite_count = 4
        self.crossover_rate = 0.7
        self.mutation_rate = 0.1
        
        # Load state
        self._load_state()
    
    def initialize_population(self, seed_innovations: List[Dict] = None):
        """Initialize population with seed innovations."""
        self.population = []
        self.generation = 0
        
        if seed_innovations:
            for i, innovation in enumerate(seed_innovations):
                dna = self._innovation_to_dna(innovation, generation=0)
                self.population.append(dna)
        
        # Fill remaining population with random innovations
        while len(self.population) < self.population_size:
            dna = self._generate_random_dna(generation=0)
            self.population.append(dna)
        
        # Evaluate initial population
        self._evaluate_population()
        
        print(f"Initialized population: {len(self.population)} individuals")
        print(f"Best fitness: {self.best_fitness:.3f}")
    
    def _innovation_to_dna(self, innovation: Dict, generation: int = 0) -> InnovationDNA:
        """Convert innovation to DNA representation."""
        # Extract key features as genes
        genes = [
            InnovationGene(
                name="impact_score",
                value=innovation.get('predicted_impact', 0.5),
                gene_type="numeric"
            ),
            InnovationGene(
                name="complexity",
                value=innovation.get('implementation_complexity', 'medium'),
                gene_type="categorical",
                category_values=['low', 'medium', 'high']
            ),
            InnovationGene(
                name="novelty",
                value=innovation.get('novelty_score', 0.5),
                gene_type="numeric"
            ),
            InnovationGene(
                name="feasibility",
                value=innovation.get('feasibility_score', 0.5),
                gene_type="numeric"
            ),
            InnovationGene(
                name="domain",
                value=innovation.get('domain', 'general'),
                gene_type="categorical",
                category_values=['general', 'memory', 'analysis', 'visualization', 'automation']
            )
        ]
        
        # Create DNA ID
        dna_id = f"DNA-{hashlib.md5(str(innovation).encode()).hexdigest()[:8]}"
        
        return InnovationDNA(
            id=dna_id,
            name=innovation.get('title', 'Unknown Innovation'),
            genes=genes,
            fitness=0.0,
            generation=generation
        )
    
    def _generate_random_dna(self, generation: int = 0) -> InnovationDNA:
        """Generate random DNA for diversity."""
        genes = [
            InnovationGene("impact_score", random.uniform(0.1, 0.9), gene_type="numeric"),
            InnovationGene("complexity", random.choice(['low', 'medium', 'high']), 
                          gene_type="categorical", category_values=['low', 'medium', 'high']),
            InnovationGene("novelty", random.uniform(0.1, 0.9), gene_type="numeric"),
            InnovationGene("feasibility", random.uniform(0.1, 0.9), gene_type="numeric"),
            InnovationGene("domain", random.choice(['general', 'memory', 'analysis']), 
                          gene_type="categorical", category_values=['general', 'memory', 'analysis', 'visualization', 'automation'])
        ]
        
        dna_id = f"DNA-R{random.randint(1000, 9999)}"
        
        return InnovationDNA(
            id=dna_id,
            name=f"Random Innovation {dna_id}",
            genes=genes,
            fitness=0.0,
            generation=generation
        )
    
    def _evaluate_population(self):
        """Evaluate fitness of entire population."""
        for dna in self.population:
            dna.fitness = self._calculate_fitness(dna)
        
        # Update best fitness
        if self.population:
            self.best_fitness = max(d.fitness for d in self.population)
    
    def _calculate_fitness(self, dna: InnovationDNA) -> float:
        """Calculate fitness score for DNA."""
        fitness = 0.0
        
        for gene in dna.genes:
            if gene.name == "impact_score":
                fitness += gene.value * 0.4  # 40% weight
            elif gene.name == "novelty":
                fitness += gene.value * 0.3  # 30% weight
            elif gene.name == "feasibility":
                fitness += gene.value * 0.2  # 20% weight
            elif gene.name == "complexity":
                # Lower complexity = higher fitness (easier to implement)
                complexity_map = {'low': 1.0, 'medium': 0.6, 'high': 0.3}
                fitness += complexity_map.get(gene.value, 0.5) * 0.1  # 10% weight
        
        return min(fitness, 1.0)  # Normalize to [0, 1]
    
    def selection(self, tournament_size: int = 3) -> InnovationDNA:
        """Tournament selection."""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda d: d.fitness)
    
    def crossover(self, parent1: InnovationDNA, parent2: InnovationDNA) -> Tuple[InnovationDNA, InnovationDNA]:
        """Single-point crossover."""
        if len(parent1.genes) != len(parent2.genes):
            return parent1, parent2
        
        # Create offspring
        child1_genes = []
        child2_genes = []
        
        crossover_point = random.randint(1, len(parent1.genes) - 1)
        
        for i, gene in enumerate(parent1.genes):
            if i < crossover_point:
                child1_genes.append(copy.deepcopy(gene))
                child2_genes.append(copy.deepcopy(parent2.genes[i]))
            else:
                child1_genes.append(copy.deepcopy(parent2.genes[i]))
                child2_genes.append(copy.deepcopy(gene))
        
        # Create children
        child1 = InnovationDNA(
            id=f"DNA-C{random.randint(1000, 9999)}",
            name=f"{parent1.name}-{parent2.name[:3]}-C1",
            genes=child1_genes,
            fitness=0.0,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id]
        )
        
        child2 = InnovationDNA(
            id=f"DNA-C{random.randint(1000, 9999)}",
            name=f"{parent2.name}-{parent1.name[:3]}-C2",
            genes=child2_genes,
            fitness=0.0,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id]
        )
        
        return child1, child2
    
    def mutate(self, dna: InnovationDNA) -> InnovationDNA:
        """Apply mutation to DNA."""
        mutated_genes = []
        
        for gene in dna.genes:
            mutated_gene = gene.mutate()
            mutated_genes.append(mutated_gene)
        
        dna.genes = mutated_genes
        return dna
    
    def evolve(self, generations: int = 10) -> List[InnovationDNA]:
        """Run evolution for specified generations."""
        print(f"\n🧬 Starting evolution for {generations} generations...")
        print("=" * 60)
        
        for gen in range(generations):
            self.generation += 1
            
            # Elitism: keep best individuals
            elite = sorted(self.population, key=lambda d: d.fitness, reverse=True)[:self.elite_count]
            
            # Create new population
            new_population = elite.copy()
            
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self.selection()
                parent2 = self.selection()
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                
                # Mutation
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                # Add to population
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            # Replace population
            self.population = new_population[:self.population_size]
            
            # Evaluate
            self._evaluate_population()
            
            # Statistics
            avg_fitness = sum(d.fitness for d in self.population) / len(self.population)
            print(f"  Generation {gen + 1}/{generations}: "
                  f"Avg={avg_fitness:.3f}, Best={self.best_fitness:.3f}")
        
        print("\n✅ Evolution complete!")
        print(f"  Final best fitness: {self.best_fitness:.3f}")
        
        # Return top innovations
        top_innovations = sorted(self.population, key=lambda d: d.fitness, reverse=True)[:5]
        return top_innovations
    
    def dna_to_innovation(self, dna: InnovationDNA) -> Dict:
        """Convert evolved DNA back to innovation hypothesis."""
        gene_values = {g.name: g.value for g in dna.genes}
        
        return {
            "id": dna.id,
            "title": dna.name,
            "description": f"Evolved innovation (Gen {dna.generation}, Fitness {dna.fitness:.3f})",
            "predicted_impact": gene_values.get('impact_score', 0.5),
            "implementation_complexity": gene_values.get('complexity', 'medium'),
            "novelty_score": gene_values.get('novelty', 0.5),
            "feasibility_score": gene_values.get('feasibility', 0.5),
            "domain": gene_values.get('domain', 'general'),
            "confidence": dna.fitness,
            "parent_ids": dna.parent_ids,
            "generation": dna.generation,
            "evolution_method": "genetic_algorithm"
        }
    
    def _load_state(self):
        """Load evolution state from file."""
        state_file = self.data_dir / "evolution_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.generation = state.get('generation', 0)
                self.best_fitness = state.get('best_fitness', 0.0)
                self.population = [InnovationDNA.from_dict(d) for d in state.get('population', [])]
    
    def _save_state(self):
        """Save evolution state to file."""
        state = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'population': [d.to_dict() for d in self.population],
            'last_updated': datetime.now().isoformat()
        }
        
        state_file = self.data_dir / "evolution_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict:
        """Get evolution statistics."""
        if not self.population:
            return {}
        
        fitness_values = [d.fitness for d in self.population]
        
        return {
            'generation': self.generation,
            'population_size': len(self.population),
            'best_fitness': self.best_fitness,
            'average_fitness': sum(fitness_values) / len(fitness_values),
            'min_fitness': min(fitness_values),
            'max_fitness': max(fitness_values),
            'diversity': len(set(d.id for d in self.population)) / len(self.population)
        }


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Evolutionary Algorithms (P5-3)")
    parser.add_argument("--evolve", type=int, default=10, help="Number of generations")
    parser.add_argument("--population", type=int, default=20, help="Population size")
    parser.add_argument("--elite", type=int, default=4, help="Elite count")
    parser.add_argument("--crossover-rate", type=float, default=0.7, help="Crossover rate")
    parser.add_argument("--mutation-rate", type=float, default=0.1, help="Mutation rate")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--workspace", type=str, default=None, help="Workspace directory")
    
    args = parser.parse_args()
    
    engine = InnovationEvolutionaryEngine(args.workspace)
    engine.population_size = args.population
    engine.elite_count = args.elite
    engine.crossover_rate = args.crossover_rate
    engine.mutation_rate = args.mutation_rate
    
    if args.stats:
        stats = engine.get_statistics()
        print("\n📊 Evolution Statistics")
        print("=" * 60)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return 0
    
    # Initialize with sample innovations
    seed_innovations = [
        {"title": "Memory Immune System", "predicted_impact": 0.9, "novelty_score": 0.85, "feasibility_score": 0.8, "implementation_complexity": "high"},
        {"title": "Neural Network Memory", "predicted_impact": 0.85, "novelty_score": 0.9, "feasibility_score": 0.75, "implementation_complexity": "high"},
        {"title": "Dark Matter Detector", "predicted_impact": 0.7, "novelty_score": 0.95, "feasibility_score": 0.6, "implementation_complexity": "medium"},
        {"title": "Quantum Entanglement", "predicted_impact": 0.95, "novelty_score": 0.98, "feasibility_score": 0.5, "implementation_complexity": "high"},
    ]
    
    engine.initialize_population(seed_innovations)
    
    # Run evolution
    top_innovations = engine.evolve(args.evolve)
    
    # Save state
    engine._save_state()
    
    # Display top innovations
    print("\n🏆 Top 5 Evolved Innovations")
    print("=" * 60)
    for i, dna in enumerate(top_innovations, 1):
        innovation = engine.dna_to_innovation(dna)
        print(f"\n  {i}. {innovation['title']}")
        print(f"     ID: {dna.id}")
        print(f"     Generation: {dna.generation}")
        print(f"     Fitness: {dna.fitness:.3f}")
        print(f"     Impact: {innovation['predicted_impact']:.2f}")
        print(f"     Novelty: {innovation['novelty_score']:.2f}")
        print(f"     Feasibility: {innovation['feasibility_score']:.2f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
