#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL TTL Optimizer - Reinforcement learning for dynamic TTL adjustment
"""

import os
import sys
import json
import time
import math
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
RL_DIR = WORKSPACE / 'data' / 'rl_ttl_optimizer'
RL_DIR.mkdir(parents=True, exist_ok=True)

class QLearningAgent:
    """
    Q-Learning agent for TTL optimization
    
    State: (access_frequency, time_since_last_access, importance)
    Action: TTL adjustment (increase/decrease/maintain)
    Reward: hit_rate × freshness
    """
    
    def __init__(self, learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 epsilon: float = 0.1):
        self.learning_rate = learning_rate  # α
        self.discount_factor = discount_factor  # γ
        self.epsilon = epsilon  # Exploration rate
        
        # Q-table: state -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'increase': 0.0, 'decrease': 0.0, 'maintain': 0.0}
        )
        
        # State tracking
        self.current_state = None
        self.current_action = None
        
        # Statistics
        self.episodes = 0
        self.total_reward = 0.0
    
    def _discretize_state(self, access_freq: float, 
                          time_decay: float, 
                          importance: float) -> str:
        """Convert continuous state to discrete state"""
        # Discretize access frequency (0-1)
        if access_freq < 0.2:
            freq_bucket = 'low'
        elif access_freq < 0.6:
            freq_bucket = 'medium'
        else:
            freq_bucket = 'high'
        
        # Discretize time decay (0-1, 1 = fresh)
        if time_decay < 0.3:
            time_bucket = 'stale'
        elif time_decay < 0.7:
            time_bucket = 'aging'
        else:
            time_bucket = 'fresh'
        
        # Discretize importance (0-1)
        if importance < 0.3:
            imp_bucket = 'low'
        elif importance < 0.7:
            imp_bucket = 'medium'
        else:
            imp_bucket = 'high'
        
        return f"{freq_bucket}_{time_bucket}_{imp_bucket}"
    
    def get_action(self, state: str, training: bool = True) -> str:
        """Get action using ε-greedy policy"""
        if training and random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(['increase', 'decrease', 'maintain'])
        else:
            # Exploitation: best action
            q_values = self.q_table[state]
            max_value = max(q_values.values())
            best_actions = [a for a, v in q_values.items() if v == max_value]
            return random.choice(best_actions)
    
    def update(self, state: str, action: str, 
               reward: float, next_state: str):
        """Update Q-value using Bellman equation"""
        current_q = self.q_table[state][action]
        
        # Max Q-value for next state
        max_next_q = max(self.q_table[next_state].values())
        
        # Bellman equation
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def get_optimal_ttl_adjustment(self, access_freq: float,
                                    time_decay: float,
                                    importance: float) -> Tuple[str, float]:
        """Get optimal TTL adjustment for given state"""
        state = self._discretize_state(access_freq, time_decay, importance)
        action = self.get_action(state, training=False)
        
        # Adjustment multipliers
        multipliers = {
            'increase': 1.5,
            'decrease': 0.7,
            'maintain': 1.0,
        }
        
        return action, multipliers[action]
    
    def save(self, model_file: Path = None) -> Path:
        """Save Q-table to disk"""
        if model_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_file = RL_DIR / f'q_table_{timestamp}.json'
        
        data = {
            'q_table': dict(self.q_table),
            'hyperparameters': {
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon,
            },
            'statistics': {
                'episodes': self.episodes,
                'total_reward': self.total_reward,
            },
            'created_at': datetime.now().isoformat(),
        }
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Q-table saved to: {model_file}")
        return model_file
    
    @classmethod
    def load(cls, model_file: Path) -> 'QLearningAgent':
        """Load Q-table from disk"""
        with open(model_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        agent = cls(
            learning_rate=data['hyperparameters']['learning_rate'],
            discount_factor=data['hyperparameters']['discount_factor'],
            epsilon=data['hyperparameters']['epsilon']
        )
        
        agent.q_table = defaultdict(
            lambda: {'increase': 0.0, 'decrease': 0.0, 'maintain': 0.0},
            data['q_table']
        )
        
        agent.episodes = data['statistics']['episodes']
        agent.total_reward = data['statistics']['total_reward']
        
        print(f"✅ Q-table loaded from: {model_file}")
        return agent


class RLTTOptimizer:
    """
    RL-based TTL Optimizer
    
    Features:
    - Q-learning for TTL adjustment
    - Reward: hit_rate × freshness
    - State: access patterns, time decay, importance
    - Action: increase/decrease/maintain TTL
    - Continuous learning from cache performance
    """
    
    # Base TTL values (seconds)
    BASE_TTL = {
        'CRITICAL': 86400,  # 24 hours
        'HIGH': 21600,      # 6 hours
        'MEDIUM': 600,      # 10 minutes
        'LOW': 60,          # 1 minute
    }
    
    def __init__(self, tier: str = 'MEDIUM',
                 min_ttl: int = 30,
                 max_ttl: int = 172800,  # 48 hours
                 training_episodes: int = 100):
        """
        Args:
            tier: Cache tier to optimize
            min_ttl: Minimum TTL (seconds)
            max_ttl: Maximum TTL (seconds)
            training_episodes: Number of training episodes
        """
        self.tier = tier
        self.min_ttl = min_ttl
        self.max_ttl = max_ttl
        
        # Current TTL
        self.base_ttl = self.BASE_TTL.get(tier, 600)
        self.current_ttl = self.base_ttl
        
        # Q-learning agent
        self.agent = QLearningAgent()
        
        # Episode tracking
        self.episode_history: List[Dict] = []
        
        # Cache metrics
        self.hit_count = 0
        self.miss_count = 0
        self.total_freshness = 0.0
        
        # Train if requested
        if training_episodes > 0:
            self._train(training_episodes)
    
    def _calculate_reward(self, hit_rate: float, freshness: float) -> float:
        """Calculate reward as hit_rate × freshness"""
        # Weighted combination
        reward = 0.6 * hit_rate + 0.4 * freshness
        return reward
    
    def _calculate_freshness(self, ttl_ratio: float) -> float:
        """Calculate freshness score (0-1)"""
        # Freshness decays as TTL ratio increases
        freshness = 1.0 - (ttl_ratio ** 0.5)  # Square root for smooth decay
        return max(0.0, min(1.0, freshness))
    
    def _train_episode(self) -> Dict:
        """Run one training episode"""
        # Simulate cache access patterns
        access_freq = random.random()
        time_decay = random.random()
        importance = random.random()
        
        # Get current state
        state = self.agent._discretize_state(access_freq, time_decay, importance)
        action = self.agent.get_action(state)
        
        # Apply action
        old_ttl = self.current_ttl
        
        if action == 'increase':
            self.current_ttl = min(self.max_ttl, int(self.current_ttl * 1.5))
        elif action == 'decrease':
            self.current_ttl = max(self.min_ttl, int(self.current_ttl * 0.7))
        # maintain: no change
        
        # Simulate cache performance
        ttl_ratio = self.current_ttl / self.max_ttl
        
        # Hit rate depends on TTL (higher TTL → more hits but stale)
        simulated_hit_rate = 0.3 + 0.5 * (1.0 - ttl_ratio) + 0.2 * access_freq
        simulated_hit_rate = min(1.0, max(0.0, simulated_hit_rate))
        
        # Freshness depends on TTL (lower TTL → fresher)
        freshness = self._calculate_freshness(ttl_ratio)
        
        # Calculate reward
        reward = self._calculate_reward(simulated_hit_rate, freshness)
        
        # Get next state (simulated)
        next_access_freq = random.random()
        next_time_decay = random.random()
        next_importance = random.random()
        next_state = self.agent._discretize_state(next_access_freq, next_time_decay, next_importance)
        
        # Update Q-table
        self.agent.update(state, action, reward, next_state)
        
        # Update statistics
        self.agent.episodes += 1
        self.agent.total_reward += reward
        
        return {
            'episode': self.agent.episodes,
            'state': state,
            'action': action,
            'old_ttl': old_ttl,
            'new_ttl': self.current_ttl,
            'hit_rate': simulated_hit_rate,
            'freshness': freshness,
            'reward': reward,
        }
    
    def _train(self, episodes: int):
        """Train for multiple episodes"""
        print(f"\n🎯 Training RL agent for {episodes} episodes...")
        
        for i in range(episodes):
            episode_result = self._train_episode()
            self.episode_history.append(episode_result)
            
            if (i + 1) % 20 == 0:
                avg_reward = sum(e['reward'] for e in self.episode_history[-20:]) / 20
                print(f"   Episode {i + 1}/{episodes} - Avg Reward: {avg_reward:.4f}")
        
        # Reset TTL to base after training
        self.current_ttl = self.base_ttl
        
        print(f"✅ Training complete! Final avg reward: {avg_reward:.4f}\n")
    
    def record_access(self, cache_hit: bool, entry_age: float = 0.0):
        """Record a cache access for online learning"""
        if cache_hit:
            self.hit_count += 1
        else:
            self.miss_count += 1
        
        self.total_freshness += (1.0 - entry_age)
    
    def get_current_metrics(self) -> Dict:
        """Get current cache metrics"""
        total = self.hit_count + self.miss_count
        
        if total == 0:
            return {
                'hit_rate': 0.0,
                'avg_freshness': 0.0,
                'total_accesses': 0,
            }
        
        hit_rate = self.hit_count / total
        avg_freshness = self.total_freshness / total
        
        return {
            'hit_rate': hit_rate,
            'avg_freshness': avg_freshness,
            'total_accesses': total,
        }
    
    def optimize_ttl(self) -> Tuple[str, int]:
        """
        Optimize TTL based on learned policy and current metrics
        
        Returns:
            (action, new_ttl) tuple
        """
        # Get current metrics
        metrics = self.get_current_metrics()
        
        # Calculate state features
        access_freq = metrics['hit_rate']  # Use hit rate as proxy
        time_decay = metrics['avg_freshness']
        importance = {'CRITICAL': 0.9, 'HIGH': 0.7, 'MEDIUM': 0.5, 'LOW': 0.3}.get(self.tier, 0.5)
        
        # Get optimal action from Q-learning agent
        action, multiplier = self.agent.get_optimal_ttl_adjustment(
            access_freq, time_decay, importance
        )
        
        # Apply adjustment
        old_ttl = self.current_ttl
        new_ttl = int(self.current_ttl * multiplier)
        new_ttl = max(self.min_ttl, min(self.max_ttl, new_ttl))
        
        self.current_ttl = new_ttl
        
        return action, new_ttl
    
    def reset_metrics(self):
        """Reset cache metrics"""
        self.hit_count = 0
        self.miss_count = 0
        self.total_freshness = 0.0
    
    def get_stats(self) -> Dict:
        """Get optimizer statistics"""
        return {
            'tier': self.tier,
            'base_ttl': self.base_ttl,
            'current_ttl': self.current_ttl,
            'ttl_change_percent': round((self.current_ttl - self.base_ttl) / self.base_ttl * 100, 2),
            'metrics': self.get_current_metrics(),
            'training_episodes': self.agent.episodes,
            'avg_training_reward': round(self.agent.total_reward / max(1, self.agent.episodes), 4),
            'q_table_size': len(self.agent.q_table),
        }
    
    def save(self, model_file: Path = None) -> Path:
        """Save optimizer state"""
        if model_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_file = RL_DIR / f'rl_ttl_optimizer_{self.tier}_{timestamp}.json'
        
        data = {
            'config': {
                'tier': self.tier,
                'base_ttl': self.base_ttl,
                'current_ttl': self.current_ttl,
                'min_ttl': self.min_ttl,
                'max_ttl': self.max_ttl,
            },
            'metrics': self.get_current_metrics(),
            'episode_history': self.episode_history[-100:],  # Last 100 episodes
            'agent_data': {
                'q_table': dict(self.agent.q_table),
                'hyperparameters': {
                    'learning_rate': self.agent.learning_rate,
                    'discount_factor': self.agent.discount_factor,
                    'epsilon': self.agent.epsilon,
                },
                'statistics': {
                    'episodes': self.agent.episodes,
                    'total_reward': self.agent.total_reward,
                },
            },
            'created_at': datetime.now().isoformat(),
        }
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Optimizer saved to: {model_file}")
        return model_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="RL TTL Optimizer")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--train', type=int, default=100, help='Training episodes')
    parser.add_argument('--tier', default='MEDIUM', 
                       choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
                       help='Cache tier')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    args = parser.parse_args()
    
    if args.demo:
        print("\n🎯 RL TTL Optimizer Demo")
        print("=" * 80)
        print(f"Tier: {args.tier}\n")
        
        # Create optimizer with training
        optimizer = RLTTOptimizer(tier=args.tier, training_episodes=args.train)
        
        # Show initial stats
        print("\n📊 Initial Statistics:")
        stats = optimizer.get_stats()
        print(f"   Base TTL: {stats['base_ttl']}s ({stats['base_ttl']/3600:.1f}h)")
        print(f"   Current TTL: {stats['current_ttl']}s")
        print(f"   Training episodes: {stats['training_episodes']}")
        print(f"   Avg training reward: {stats['avg_training_reward']}")
        
        # Simulate cache accesses
        print("\n📈 Simulating cache accesses...\n")
        
        for i in range(50):
            # Simulate cache access
            cache_hit = random.random() > 0.3  # 70% hit rate
            entry_age = random.random() * 0.5  # 0-50% age
            
            optimizer.record_access(cache_hit, entry_age)
            
            if (i + 1) % 10 == 0:
                metrics = optimizer.get_current_metrics()
                print(f"   After {i + 1} accesses:")
                print(f"      Hit rate: {metrics['hit_rate']:.2%}")
                print(f"      Avg freshness: {metrics['avg_freshness']:.2%}")
        
        # Optimize TTL
        print("\n⚙️  Optimizing TTL...")
        action, new_ttl = optimizer.optimize_ttl()
        
        print(f"\n   Action: {action}")
        print(f"   New TTL: {new_ttl}s ({new_ttl/3600:.1f}h)")
        
        # Final stats
        print("\n📊 Final Statistics:")
        stats = optimizer.get_stats()
        print(f"   TTL change: {stats['ttl_change_percent']:+.2f}%")
        print(f"   Total accesses: {stats['metrics']['total_accesses']}")
        print(f"   Final hit rate: {stats['metrics']['hit_rate']:.2%}")
        print(f"   Final freshness: {stats['metrics']['avg_freshness']:.2%}")
        
        # Save optimizer
        optimizer.save()
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        optimizer = RLTTOptimizer(tier=args.tier, training_episodes=0)
        stats = optimizer.get_stats()
        
        print("\n📊 RL TTL Optimizer Statistics")
        print("=" * 80)
        print(f"Tier: {stats['tier']}")
        print(f"Base TTL: {stats['base_ttl']}s")
        print(f"Current TTL: {stats['current_ttl']}s")
        print(f"Training episodes: {stats['training_episodes']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
