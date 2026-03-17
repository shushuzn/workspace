#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta-Learning Optimizer - Learn How to Learn
Features: Reinforcement learning, Bayesian optimization, adaptive strategies

Usage:
    python meta_learning_optimizer.py --optimize
    python meta_learning_optimizer.py --strategies
    python meta_learning_optimizer.py --demo
"""

import os
import sys
import json
import math
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import random
import statistics

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class StrategyType:
    """Learning strategy types"""
    GREEDY = "greedy"  # Always choose best known
    EPSILON_GREEDY = "epsilon_greedy"  # Explore with probability ε
    UCB = "ucb"  # Upper Confidence Bound
    THOMPSON = "thompson"  # Thompson sampling
    EXP3 = "exp3"  # Exponential-weight algorithm


@dataclass
class Arm:
    """Multi-armed bandit arm"""
    id: str
    name: str
    total_pulls: int = 0
    total_reward: float = 0.0
    rewards_history: List[float] = field(default_factory=list)
    
    @property
    def mean_reward(self) -> float:
        return self.total_reward / max(1, self.total_pulls)
    
    @property
    def success_rate(self) -> float:
        return self.mean_reward


@dataclass
class Strategy:
    """Learning strategy"""
    id: str
    name: str
    type: StrategyType
    parameters: Dict
    total_trials: int = 0
    total_reward: float = 0.0
    avg_reward: float = 0.0
    regret: float = 0.0


@dataclass
class Trial:
    """Learning trial"""
    id: str
    strategy_id: str
    arm_id: str
    reward: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict = field(default_factory=dict)


@dataclass
class HyperparameterConfig:
    """Hyperparameter configuration"""
    name: str
    search_space: Dict
    best_value: Optional[Dict] = None
    best_score: float = 0.0
    trials: int = 0


class MetaLearningOptimizer:
    """Meta-learning optimizer"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "meta_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.strategies_file = self.data_dir / "strategies.json"
        self.arms_file = self.data_dir / "arms.json"
        self.trials_file = self.data_dir / "trials.json"
        self.hyperparams_file = self.data_dir / "hyperparams.json"
        
        self.strategies: Dict[str, Strategy] = {}
        self.arms: Dict[str, Arm] = {}
        self.trials: List[Trial] = []
        self.hyperparams: Dict[str, HyperparameterConfig] = {}
        
        self.load_state()
        self._initialize_default_strategies()
    
    def load_state(self):
        """Load state"""
        if self.strategies_file.exists():
            with open(self.strategies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.strategies = {
                    k: Strategy(
                        id=v['id'],
                        name=v['name'],
                        type=v['type'],
                        parameters=v.get('parameters', {}),
                        total_trials=v.get('total_trials', 0),
                        total_reward=v.get('total_reward', 0),
                        avg_reward=v.get('avg_reward', 0),
                        regret=v.get('regret', 0)
                    )
                    for k, v in data.get('strategies', {}).items()
                }
        
        if self.arms_file.exists():
            with open(self.arms_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.arms = {
                    k: Arm(
                        id=v['id'],
                        name=v['name'],
                        total_pulls=v.get('total_pulls', 0),
                        total_reward=v.get('total_reward', 0),
                        rewards_history=v.get('rewards_history', [])
                    )
                    for k, v in data.get('arms', {}).items()
                }
        
        if self.trials_file.exists():
            with open(self.trials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.trials = [
                    Trial(
                        id=v['id'],
                        strategy_id=v['strategy_id'],
                        arm_id=v['arm_id'],
                        reward=v['reward'],
                        timestamp=v.get('timestamp', datetime.now().isoformat()),
                        context=v.get('context', {})
                    )
                    for v in data.get('trials', [])
                ]
        
        if self.hyperparams_file.exists():
            with open(self.hyperparams_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.hyperparams = {
                    k: HyperparameterConfig(
                        name=v['name'],
                        search_space=v['search_space'],
                        best_value=v.get('best_value'),
                        best_score=v.get('best_score', 0),
                        trials=v.get('trials', 0)
                    )
                    for k, v in data.get('configs', {}).items()
                }
    
    def save_state(self):
        """Save state"""
        with open(self.strategies_file, 'w', encoding='utf-8') as f:
            json.dump({
                'strategies': {k: asdict(v) for k, v in self.strategies.items()},
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.arms_file, 'w', encoding='utf-8') as f:
            json.dump({
                'arms': {k: asdict(v) for k, v in self.arms.items()},
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.trials_file, 'w', encoding='utf-8') as f:
            json.dump({
                'trials': [asdict(t) for t in self.trials[-10000:]],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.hyperparams_file, 'w', encoding='utf-8') as f:
            json.dump({
                'configs': {k: asdict(v) for k, v in self.hyperparams.items()},
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def _initialize_default_strategies(self):
        """Initialize default learning strategies"""
        if not self.strategies:
            # Epsilon-greedy
            self.strategies['epsilon_greedy'] = Strategy(
                id='epsilon_greedy',
                name='Epsilon-Greedy',
                type=StrategyType.EPSILON_GREEDY,
                parameters={'epsilon': 0.1}
            )
            
            # UCB1
            self.strategies['ucb1'] = Strategy(
                id='ucb1',
                name='UCB1',
                type=StrategyType.UCB,
                parameters={'c': 2.0}
            )
            
            # Thompson Sampling
            self.strategies['thompson'] = Strategy(
                id='thompson',
                name='Thompson Sampling',
                type=StrategyType.THOMPSON,
                parameters={'alpha_prior': 1, 'beta_prior': 1}
            )
            
            # EXP3
            self.strategies['exp3'] = Strategy(
                id='exp3',
                name='EXP3',
                type=StrategyType.EXP3,
                parameters={'gamma': 0.1}
            )
    
    def add_arm(self, arm_id: str, name: str, true_reward_prob: float = None):
        """Add arm (option/action)"""
        self.arms[arm_id] = Arm(
            id=arm_id,
            name=name
        )
        
        # Store true reward probability for simulation
        if true_reward_prob is not None:
            self.arms[arm_id].true_reward_prob = true_reward_prob
    
    def select_arm(self, strategy_id: str) -> str:
        """Select arm using specified strategy"""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return random.choice(list(self.arms.keys()))
        
        if strategy.type == StrategyType.GREEDY:
            return self._select_greedy()
        elif strategy.type == StrategyType.EPSILON_GREEDY:
            return self._select_epsilon_greedy(strategy.parameters['epsilon'])
        elif strategy.type == StrategyType.UCB:
            return self._select_ucb(strategy.parameters.get('c', 2.0))
        elif strategy.type == StrategyType.THOMPSON:
            return self._select_thompson()
        elif strategy.type == StrategyType.EXP3:
            return self._select_exp3(strategy.parameters.get('gamma', 0.1))
        
        return random.choice(list(self.arms.keys()))
    
    def _select_greedy(self) -> str:
        """Greedy selection"""
        if not self.arms:
            return None
        
        best_arm = max(self.arms.values(), key=lambda a: a.mean_reward)
        return best_arm.id
    
    def _select_epsilon_greedy(self, epsilon: float) -> str:
        """Epsilon-greedy selection"""
        if random.random() < epsilon:
            # Explore
            return random.choice(list(self.arms.keys()))
        else:
            # Exploit
            return self._select_greedy()
    
    def _select_ucb(self, c: float) -> str:
        """UCB1 selection"""
        total_pulls = sum(a.total_pulls for a in self.arms.values())
        
        if total_pulls == 0:
            return random.choice(list(self.arms.keys()))
        
        ucb_values = {}
        for arm in self.arms.values():
            if arm.total_pulls == 0:
                ucb_values[arm.id] = float('inf')
            else:
                exploitation = arm.mean_reward
                exploration = c * math.sqrt(math.log(total_pulls) / arm.total_pulls)
                ucb_values[arm.id] = exploitation + exploration
        
        return max(ucb_values.items(), key=lambda x: x[1])[0]
    
    def _select_thompson(self) -> str:
        """Thompson sampling (Beta-Bernoulli)"""
        samples = {}
        for arm in self.arms.values():
            # Beta posterior: alpha = successes + 1, beta = failures + 1
            alpha = arm.total_reward + 1
            beta = arm.total_pulls - arm.total_reward + 1
            samples[arm.id] = random.betavariate(alpha, beta)
        
        return max(samples.items(), key=lambda x: x[1])[0]
    
    def _select_exp3(self, gamma: float) -> str:
        """EXP3 selection"""
        n_arms = len(self.arms)
        
        # Initialize weights if needed
        for arm in self.arms.values():
            if not hasattr(arm, 'weight'):
                arm.weight = 1.0
        
        # Calculate probabilities
        total_weight = sum(a.weight for a in self.arms.values())
        
        probs = {}
        for arm in self.arms.values():
            probs[arm.id] = (1 - gamma) * arm.weight / total_weight + gamma / n_arms
        
        # Sample arm
        r = random.random()
        cumsum = 0
        for arm_id, prob in probs.items():
            cumsum += prob
            if r <= cumsum:
                return arm_id
        
        return list(self.arms.keys())[-1]
    
    def observe_reward(self, strategy_id: str, arm_id: str, reward: float):
        """Observe reward and update"""
        strategy = self.strategies.get(strategy_id)
        arm = self.arms.get(arm_id)
        
        if not strategy or not arm:
            return
        
        # Update arm
        arm.total_pulls += 1
        arm.total_reward += reward
        arm.rewards_history.append(reward)
        
        # Update strategy
        strategy.total_trials += 1
        strategy.total_reward += reward
        strategy.avg_reward = strategy.total_reward / strategy.total_trials
        
        # Update EXP3 weights
        if strategy.type == StrategyType.EXP3:
            n_arms = len(self.arms)
            gamma = strategy.parameters.get('gamma', 0.1)
            
            # Calculate importance-weighted reward
            total_weight = sum(a.weight for a in self.arms.values())
            prob = (1 - gamma) * arm.weight / total_weight + gamma / n_arms
            
            # Update weight
            estimated_reward = reward / prob
            arm.weight *= math.exp(gamma * estimated_reward / n_arms)
        
        # Record trial
        trial = Trial(
            id=str(uuid.uuid4())[:8],
            strategy_id=strategy_id,
            arm_id=arm_id,
            reward=reward
        )
        self.trials.append(trial)
    
    def calculate_regret(self, strategy_id: str, optimal_arm_id: str) -> float:
        """Calculate cumulative regret"""
        strategy = self.strategies.get(strategy_id)
        optimal_arm = self.arms.get(optimal_arm_id)
        
        if not strategy or not optimal_arm:
            return 0.0
        
        # Optimal expected reward
        optimal_reward = optimal_arm.mean_reward * strategy.total_trials
        
        # Actual reward
        actual_reward = strategy.total_reward
        
        # Regret
        regret = optimal_reward - actual_reward
        
        strategy.regret = regret
        return regret
    
    def compare_strategies(self) -> List[Dict]:
        """Compare all strategies"""
        comparisons = []
        
        for strategy in self.strategies.values():
            comparisons.append({
                'id': strategy.id,
                'name': strategy.name,
                'type': strategy.type,
                'trials': strategy.total_trials,
                'avg_reward': round(strategy.avg_reward, 4),
                'total_reward': round(strategy.total_reward, 2),
                'regret': round(strategy.regret, 2)
            })
        
        # Sort by avg_reward
        comparisons.sort(key=lambda x: x['avg_reward'], reverse=True)
        
        return comparisons
    
    def bayesian_optimization(self, name: str, search_space: Dict,
                             objective_fn: callable, n_trials: int = 20) -> Dict:
        """Simple Bayesian optimization"""
        print(f"\n🔍 Bayesian Optimization: {name}")
        print(f"   Search Space: {search_space}")
        print(f"   Trials: {n_trials}\n")
        
        best_params = None
        best_score = float('-inf')
        
        for i in range(n_trials):
            # Sample random parameters (simplified - use random search)
            params = {}
            for param_name, space in search_space.items():
                if isinstance(space, tuple):
                    params[param_name] = random.uniform(space[0], space[1])
                elif isinstance(space, list):
                    params[param_name] = random.choice(space)
            
            # Evaluate
            try:
                score = objective_fn(params)
            except Exception as e:
                score = float('-inf')
            
            # Update best
            if score > best_score:
                best_score = score
                best_params = params.copy()
            
            if (i + 1) % 5 == 0:
                print(f"   Trial {i+1}/{n_trials}: score={score:.4f}, best={best_score:.4f}")
        
        print(f"\n✅ Best Parameters: {best_params}")
        print(f"   Best Score: {best_score:.4f}\n")
        
        # Store config
        self.hyperparams[name] = HyperparameterConfig(
            name=name,
            search_space=search_space,
            best_value=best_params,
            best_score=best_score,
            trials=n_trials
        )
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'trials': n_trials
        }
    
    def get_learning_curve(self, strategy_id: str) -> List[float]:
        """Get learning curve for strategy"""
        strategy_trials = [t for t in self.trials if t.strategy_id == strategy_id]
        strategy_trials.sort(key=lambda t: t.timestamp)
        
        cumulative_avg = []
        total = 0
        for i, trial in enumerate(strategy_trials, 1):
            total += trial.reward
            cumulative_avg.append(total / i)
        
        return cumulative_avg
    
    def get_statistics(self) -> Dict:
        """Get optimizer statistics"""
        return {
            'strategies': len(self.strategies),
            'arms': len(self.arms),
            'trials': len(self.trials),
            'hyperparameter_configs': len(self.hyperparams),
            'best_strategy': max(
                self.strategies.values(),
                key=lambda s: s.avg_reward
            ).name if self.strategies else None
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Meta-Learning Optimizer')
    parser.add_argument('--optimize', action='store_true', help='Run optimization')
    parser.add_argument('--strategies', action='store_true', help='Compare strategies')
    parser.add_argument('--bayesian', action='store_true', help='Bayesian optimization demo')
    parser.add_argument('--demo', action='store_true', help='Run full demo')
    args = parser.parse_args()
    
    optimizer = MetaLearningOptimizer()
    
    if args.optimize:
        # Run optimization
        comparisons = optimizer.compare_strategies()
        print("\n📊 Strategy Comparison:")
        print(json.dumps(comparisons, indent=2))
    
    elif args.strategies:
        stats = optimizer.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.bayesian:
        # Bayesian optimization demo
        def objective(params):
            # Rosenbrock function (test function)
            x = params.get('x', 0)
            y = params.get('y', 0)
            return -(100 * (y - x**2)**2 + (1 - x)**2)
        
        optimizer.bayesian_optimization(
            name='rosenbrock',
            search_space={
                'x': (-2, 2),
                'y': (-1, 3)
            },
            objective_fn=objective,
            n_trials=30
        )
        optimizer.save_state()
    
    elif args.demo:
        print("\n🧪 Meta-Learning Optimizer Demo\n")
        
        # Create arms (slot machines with different reward probabilities)
        print("1. Creating Arms (Slot Machines):")
        optimizer.add_arm('arm_a', 'Conservative', true_reward_prob=0.4)
        optimizer.add_arm('arm_b', 'Balanced', true_reward_prob=0.5)
        optimizer.add_arm('arm_c', 'Aggressive', true_reward_prob=0.6)
        optimizer.add_arm('arm_d', 'Risky', true_reward_prob=0.3)
        print(f"   Created {len(optimizer.arms)} arms\n")
        
        # Run strategies
        print("2. Running Learning Strategies (1000 trials each):\n")
        
        n_trials = 1000
        
        for strategy_id in optimizer.strategies.keys():
            print(f"   {optimizer.strategies[strategy_id].name}:")
            
            for _ in range(n_trials):
                # Select arm
                arm_id = optimizer.select_arm(strategy_id)
                arm = optimizer.arms[arm_id]
                
                # Simulate reward (Bernoulli)
                reward = 1.0 if random.random() < arm.true_reward_prob else 0.0
                
                # Observe
                optimizer.observe_reward(strategy_id, arm_id, reward)
            
            # Calculate regret (optimal is arm_c with 0.6)
            regret = optimizer.calculate_regret(strategy_id, 'arm_c')
            
            print(f"      Trials: {n_trials}")
            print(f"      Avg Reward: {optimizer.strategies[strategy_id].avg_reward:.4f}")
            print(f"      Regret: {regret:.2f}\n")
        
        # Compare strategies
        print("3. Strategy Comparison:")
        comparisons = optimizer.compare_strategies()
        for i, comp in enumerate(comparisons, 1):
            print(f"   {i}. {comp['name']}: {comp['avg_reward']:.4f} (regret: {comp['regret']:.2f})")
        
        print()
        
        # Show statistics
        print("4. Statistics:")
        stats = optimizer.get_statistics()
        print(json.dumps(stats, indent=2))
        
        optimizer.save_state()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
