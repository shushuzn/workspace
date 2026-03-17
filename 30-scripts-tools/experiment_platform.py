#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated Experiment Platform - End-to-End Experimentation
Features: A/B testing, factorial design, sequential analysis, auto execution

Usage:
    python experiment_platform.py --create ab_test
    python experiment_platform.py --run experiment_001
    python experiment_platform.py --analyze experiment_001
"""

import os
import sys
import json
import math
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import random
import statistics

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ExperimentType(Enum):
    """Experiment types"""
    AB_TEST = "ab_test"
    FACTORIAL = "factorial"
    SEQUENTIAL = "sequential"
    MULTIVARIATE = "multivariate"


class ExperimentStatus(Enum):
    """Experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ANALYZED = "analyzed"


@dataclass
class Variant:
    """Experiment variant"""
    id: str
    name: str
    description: str
    parameters: Dict
    traffic_allocation: float = 0.0  # 0-1
    conversions: int = 0
    samples: int = 0


@dataclass
class Experiment:
    """Experiment definition"""
    id: str
    name: str
    type: ExperimentType
    hypothesis: str
    variants: List[Variant]
    status: ExperimentStatus = ExperimentStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    sample_size: int = 0
    min_detectable_effect: float = 0.05
    significance_level: float = 0.05
    power: float = 0.8
    results: Optional[Dict] = None
    conclusion: Optional[str] = None


@dataclass
class FactorialDesign:
    """Factorial experiment design"""
    factors: Dict[str, List[Any]]  # factor_name -> [levels]
    runs: int  # total runs
    design_matrix: List[Dict]


@dataclass
class SequentialAnalysis:
    """Sequential analysis state"""
    experiment_id: str
    interim_analyses: int = 0
    current_z_score: float = 0.0
    can_stop_early: bool = False
    recommendation: str = ""
    stopping_boundaries: Dict = field(default_factory=dict)


class AutomatedExperimentPlatform:
    """Automated experiment platform"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "experiments"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiments_file = self.data_dir / "experiments.json"
        self.results_file = self.data_dir / "results.json"
        
        self.experiments: Dict[str, Experiment] = {}
        self.results: Dict[str, Dict] = {}
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.experiments_file.exists():
            with open(self.experiments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.experiments = {
                    k: Experiment(
                        id=v['id'],
                        name=v['name'],
                        type=ExperimentType(v['type']),
                        hypothesis=v['hypothesis'],
                        variants=[Variant(**var) for var in v['variants']],
                        status=ExperimentStatus(v.get('status', 'draft')),
                        created_at=v.get('created_at', datetime.now().isoformat()),
                        started_at=v.get('started_at'),
                        completed_at=v.get('completed_at'),
                        sample_size=v.get('sample_size', 0),
                        min_detectable_effect=v.get('min_detectable_effect', 0.05),
                        significance_level=v.get('significance_level', 0.05),
                        power=v.get('power', 0.8),
                        results=v.get('results'),
                        conclusion=v.get('conclusion')
                    )
                    for k, v in data.get('experiments', {}).items()
                }
        
        if self.results_file.exists():
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
    
    def save_state(self):
        """Save state"""
        with open(self.experiments_file, 'w', encoding='utf-8') as f:
            json.dump({
                'experiments': {
                    k: {
                        **asdict(v),
                        'type': v.type.value,  # Convert enum to string
                        'status': v.status.value  # Convert enum to string
                    }
                    for k, v in self.experiments.items()
                },
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'results': self.results,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def create_ab_test(self, name: str, hypothesis: str,
                      variant_a: Dict, variant_b: Dict,
                      traffic_split: float = 0.5) -> Experiment:
        """Create A/B test"""
        variants = [
            Variant(
                id='A',
                name='Control',
                description='Baseline variant',
                parameters=variant_a,
                traffic_allocation=1 - traffic_split
            ),
            Variant(
                id='B',
                name='Treatment',
                description='Experimental variant',
                parameters=variant_b,
                traffic_allocation=traffic_split
            )
        ]
        
        experiment = Experiment(
            id=f'exp_{uuid.uuid4().hex[:8]}',
            name=name,
            type=ExperimentType.AB_TEST,
            hypothesis=hypothesis,
            variants=variants,
            sample_size=self._calculate_sample_size()
        )
        
        self.experiments[experiment.id] = experiment
        
        print(f"✅ A/B Test Created: {name}")
        print(f"   Hypothesis: {hypothesis}")
        print(f"   Sample Size: {experiment.sample_size}")
        print(f"   Traffic Split: {(1-traffic_split)*100:.0f}% / {traffic_split*100:.0f}%\n")
        
        return experiment
    
    def create_factorial_design(self, name: str, hypothesis: str,
                               factors: Dict[str, List[Any]]) -> Experiment:
        """Create factorial experiment"""
        # Calculate runs
        num_runs = 1
        for levels in factors.values():
            num_runs *= len(levels)
        
        # Generate design matrix
        design_matrix = self._generate_factorial_matrix(factors)
        
        # Create variants from design matrix
        variants = [
            Variant(
                id=f'run_{i}',
                name=f'Run {i}',
                description=f'Factor combination {i}',
                parameters=run,
                traffic_allocation=1.0 / num_runs
            )
            for i, run in enumerate(design_matrix)
        ]
        
        experiment = Experiment(
            id=f'exp_{uuid.uuid4().hex[:8]}',
            name=name,
            type=ExperimentType.FACTORIAL,
            hypothesis=hypothesis,
            variants=variants,
            sample_size=self._calculate_sample_size() * num_runs
        )
        
        self.experiments[experiment.id] = experiment
        
        print(f"✅ Factorial Design Created: {name}")
        print(f"   Factors: {len(factors)}")
        print(f"   Runs: {num_runs}")
        print(f"   Total Samples: {experiment.sample_size}\n")
        
        return experiment
    
    def _generate_factorial_matrix(self, factors: Dict[str, List[Any]]) -> List[Dict]:
        """Generate full factorial design matrix"""
        if not factors:
            return [{}]
        
        factor_names = list(factors.keys())
        factor_levels = [factors[name] for name in factor_names]
        
        # Cartesian product
        import itertools
        combinations = list(itertools.product(*factor_levels))
        
        return [
            dict(zip(factor_names, combo))
            for combo in combinations
        ]
    
    def _calculate_sample_size(self, baseline_rate: float = 0.1,
                              min_detectable_effect: float = 0.05,
                              significance: float = 0.05,
                              power: float = 0.8) -> int:
        """Calculate required sample size per variant"""
        # Using approximation for two-proportion z-test
        z_alpha = 1.96  # 95% confidence
        z_beta = 0.84   # 80% power
        
        p1 = baseline_rate
        p2 = baseline_rate * (1 + min_detectable_effect)
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) +
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p2 - p1) ** 2
        
        n = numerator / denominator
        
        return max(100, int(math.ceil(n)))
    
    def start_experiment(self, experiment_id: str):
        """Start experiment"""
        exp = self.experiments.get(experiment_id)
        if not exp:
            print(f"❌ Experiment not found: {experiment_id}")
            return
        
        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.now().isoformat()
        
        # Reset variant stats
        for variant in exp.variants:
            variant.conversions = 0
            variant.samples = 0
        
        print(f"🚀 Experiment Started: {exp.name}")
        print(f"   ID: {exp.id}")
        print(f"   Status: RUNNING\n")
    
    def record_observation(self, experiment_id: str, variant_id: str,
                          converted: bool):
        """Record observation"""
        exp = self.experiments.get(experiment_id)
        if not exp:
            return
        
        variant = next((v for v in exp.variants if v.id == variant_id), None)
        if not variant:
            return
        
        variant.samples += 1
        if converted:
            variant.conversions += 1
    
    def analyze_ab_test(self, experiment_id: str) -> Dict:
        """Analyze A/B test results"""
        exp = self.experiments.get(experiment_id)
        if not exp or exp.type != ExperimentType.AB_TEST:
            return {}
        
        if len(exp.variants) != 2:
            return {}
        
        variant_a = exp.variants[0]
        variant_b = exp.variants[1]
        
        # Conversion rates
        rate_a = variant_a.conversions / max(1, variant_a.samples)
        rate_b = variant_b.conversions / max(1, variant_b.samples)
        
        # Relative improvement
        relative_improvement = (rate_b - rate_a) / max(0.001, rate_a)
        
        # Statistical significance (two-proportion z-test)
        n_a, n_b = variant_a.samples, variant_b.samples
        p_a, p_b = rate_a, rate_b
        p_pooled = (variant_a.conversions + variant_b.conversions) / max(1, n_a + n_b)
        
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b))
        z_score = (p_b - p_a) / max(0.001, se)
        
        # P-value (approximation)
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
        
        # Confidence interval for difference
        se_diff = math.sqrt(p_a*(1-p_a)/n_a + p_b*(1-p_b)/n_b)
        ci_lower = (p_b - p_a) - 1.96 * se_diff
        ci_upper = (p_b - p_a) + 1.96 * se_diff
        
        # Significance
        significant = p_value < exp.significance_level
        
        results = {
            'variant_a': {
                'name': variant_a.name,
                'samples': variant_a.samples,
                'conversions': variant_a.conversions,
                'rate': round(rate_a, 4)
            },
            'variant_b': {
                'name': variant_b.name,
                'samples': variant_b.samples,
                'conversions': variant_b.conversions,
                'rate': round(rate_b, 4)
            },
            'relative_improvement': round(relative_improvement, 4),
            'absolute_improvement': round(p_b - p_a, 4),
            'z_score': round(z_score, 3),
            'p_value': round(p_value, 4),
            'confidence_interval': [round(ci_lower, 4), round(ci_upper, 4)],
            'significant': significant,
            'winner': 'B' if (significant and p_b > p_a) else ('A' if significant else 'inconclusive')
        }
        
        exp.results = results
        exp.status = ExperimentStatus.ANALYZED
        
        # Generate conclusion
        if significant:
            if p_b > p_a:
                exp.conclusion = f"Variant B is significantly better than A ({relative_improvement*100:.1f}% improvement, p={p_value:.4f})"
            else:
                exp.conclusion = f"Variant A is significantly better than B ({abs(relative_improvement)*100:.1f}% improvement, p={p_value:.4f})"
        else:
            exp.conclusion = f"No significant difference detected (p={p_value:.4f})"
        
        exp.completed_at = datetime.now().isoformat()
        
        self.results[experiment_id] = results
        
        return results
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def sequential_analysis(self, experiment_id: str) -> SequentialAnalysis:
        """Perform sequential analysis for early stopping"""
        exp = self.experiments.get(experiment_id)
        if not exp:
            return None
        
        # O'Brien-Fleming spending function
        interim = len([r for r in self.results.values() if r]) + 1
        max_interim = 5
        
        # Stopping boundaries (approximate)
        boundaries = {
            1: 4.56,
            2: 3.23,
            3: 2.63,
            4: 2.28,
            5: 2.04
        }
        
        # Calculate current z-score
        results = self.analyze_ab_test(experiment_id)
        z_score = results.get('z_score', 0)
        
        boundary = boundaries.get(interim, 2.04)
        can_stop = abs(z_score) > boundary
        
        analysis = SequentialAnalysis(
            experiment_id=experiment_id,
            interim_analyses=interim,
            stopping_boundaries=boundaries,
            current_z_score=z_score,
            can_stop_early=can_stop,
            recommendation='STOP' if can_stop else 'CONTINUE'
        )
        
        print(f"📊 Sequential Analysis (Interim {interim}/{max_interim}):")
        print(f"   Z-score: {z_score:.3f}")
        print(f"   Boundary: {boundary:.3f}")
        print(f"   Can Stop Early: {can_stop}")
        print(f"   Recommendation: {analysis.recommendation}\n")
        
        return analysis
    
    def get_experiment_status(self, experiment_id: str) -> Dict:
        """Get experiment status"""
        exp = self.experiments.get(experiment_id)
        if not exp:
            return {}
        
        return {
            'id': exp.id,
            'name': exp.name,
            'type': exp.type.value,
            'status': exp.status.value,
            'hypothesis': exp.hypothesis,
            'variants': len(exp.variants),
            'total_samples': sum(v.samples for v in exp.variants),
            'sample_size_required': exp.sample_size,
            'progress': round(sum(v.samples for v in exp.variants) / max(1, exp.sample_size) * 100, 1),
            'conclusion': exp.conclusion
        }
    
    def get_all_experiments(self) -> List[Dict]:
        """Get all experiments summary"""
        return [
            {
                'id': exp.id,
                'name': exp.name,
                'type': exp.type.value,
                'status': exp.status.value,
                'conclusion': exp.conclusion
            }
            for exp in self.experiments.values()
        ]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Experiment Platform')
    parser.add_argument('--create', type=str, help='Create experiment (ab_test/factorial)')
    parser.add_argument('--run', type=str, help='Run experiment')
    parser.add_argument('--analyze', type=str, help='Analyze experiment')
    parser.add_argument('--status', type=str, help='Show experiment status')
    parser.add_argument('--list', action='store_true', help='List all experiments')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    platform = AutomatedExperimentPlatform()
    
    if args.create == 'ab_test':
        exp = platform.create_ab_test(
            name='Email Subject Line Test',
            hypothesis='Personalized subject lines increase open rates',
            variant_a={'subject': 'Weekly Report'},
            variant_b={'subject': 'Your Weekly Report, John'},
            traffic_split=0.5
        )
        platform.save_state()
    
    elif args.create == 'factorial':
        exp = platform.create_factorial_design(
            name='Landing Page Optimization',
            hypothesis='Headline and CTA color affect conversion',
            factors={
                'headline': ['Benefit-focused', 'Feature-focused'],
                'cta_color': ['green', 'blue', 'red'],
                'image': ['product', 'lifestyle']
            }
        )
        platform.save_state()
    
    elif args.run:
        platform.start_experiment(args.run)
        platform.save_state()
    
    elif args.analyze:
        results = platform.analyze_ab_test(args.analyze)
        print("\n📊 Analysis Results:")
        print(json.dumps(results, indent=2))
        platform.save_state()
    
    elif args.status:
        status = platform.get_experiment_status(args.status)
        print(json.dumps(status, indent=2))
    
    elif args.list:
        experiments = platform.get_all_experiments()
        print(json.dumps(experiments, indent=2))
    
    elif args.demo:
        print("\n🧪 Automated Experiment Platform Demo\n")
        
        # Create A/B test
        print("1. Creating A/B Test:")
        exp = platform.create_ab_test(
            name='CTA Button Color Test',
            hypothesis='Green CTA button increases clicks vs blue',
            variant_a={'color': 'blue', 'text': 'Sign Up'},
            variant_b={'color': 'green', 'text': 'Sign Up'},
            traffic_split=0.5
        )
        
        # Start experiment
        print("\n2. Starting Experiment:")
        platform.start_experiment(exp.id)
        
        # Simulate observations
        print("\n3. Simulating Observations:")
        for i in range(500):
            # Variant A: 10% conversion
            converted_a = random.random() < 0.10
            platform.record_observation(exp.id, 'A', converted_a)
            
            # Variant B: 15% conversion
            converted_b = random.random() < 0.15
            platform.record_observation(exp.id, 'B', converted_b)
        
        # Analyze
        print("\n4. Analyzing Results:")
        results = platform.analyze_ab_test(exp.id)
        print(json.dumps(results, indent=2))
        
        print(f"\n✅ Conclusion: {exp.conclusion}")
        
        platform.save_state()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
