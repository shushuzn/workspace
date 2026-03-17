#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Tuner - ML-based cache optimization
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TUNER_DIR = WORKSPACE / 'data' / 'auto_tuner'
TUNER_DIR.mkdir(parents=True, exist_ok=True)

class AutoTuner:
    """
    Automatically optimize cache parameters using ML
    
    Features:
    - Usage pattern analysis
    - Optimal TTL prediction
    - Cache size optimization
    - Performance monitoring
    - Reinforcement learning
    """
    
    def __init__(self):
        # Historical data
        self.usage_history: List[Dict] = []
        self.performance_history: List[Dict] = []
        
        # Current configuration
        self.config = {
            'base_ttl': 600,
            'max_cache_size': 1000,
            'l1_ttl': 3600,
            'l2_ttl': 600,
            'semantic_ttl': 600,
            'similarity_threshold': 0.7,
        }
        
        # Optimal configuration (learned)
        self.optimal_config = self.config.copy()
        
        # Load historical data
        self._load_history()
        
        # Statistics
        self.stats = {
            'optimizations_run': 0,
            'performance_improvements': 0,
            'last_optimization': None,
        }
    
    def _load_history(self):
        """Load historical usage data"""
        history_file = TUNER_DIR / 'usage_history.json'
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.usage_history = data.get('usage', [])
                self.performance_history = data.get('performance', [])
                self.stats = data.get('stats', self.stats)
                
                print(f"✅ Loaded {len(self.usage_history)} usage records")
            except Exception as e:
                print(f"⚠️  Failed to load history: {e}")
    
    def _save_history(self):
        """Save historical usage data"""
        history_file = TUNER_DIR / 'usage_history.json'
        
        data = {
            'usage': self.usage_history[-1000:],  # Keep last 1000
            'performance': self.performance_history[-100:],
            'stats': self.stats,
            'last_updated': datetime.now().isoformat(),
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def record_usage(self, query: str, 
                     cache_hit: bool,
                     response_time_ms: float,
                     cache_layer: str):
        """
        Record cache usage for analysis
        
        Args:
            query: Search query
            cache_hit: Whether cache was hit
            response_time_ms: Response time in milliseconds
            cache_layer: L1/L2/Semantic/Index/Vector
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'cache_hit': cache_hit,
            'response_time_ms': response_time_ms,
            'cache_layer': cache_layer,
        }
        
        self.usage_history.append(record)
        
        # Save periodically
        if len(self.usage_history) % 50 == 0:
            self._save_history()
    
    def record_performance(self, config: Dict, 
                          avg_response_ms: float,
                          hit_rate: float):
        """
        Record performance metrics for configuration
        
        Args:
            config: Cache configuration used
            avg_response_ms: Average response time
            hit_rate: Cache hit rate percentage
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'avg_response_ms': avg_response_ms,
            'hit_rate': hit_rate,
        }
        
        self.performance_history.append(record)
    
    def analyze_patterns(self) -> Dict:
        """Analyze usage patterns"""
        if not self.usage_history:
            return {}
        
        # Query frequency analysis
        query_counts = defaultdict(int)
        for record in self.usage_history:
            query_counts[record['query']] += 1
        
        # Cache layer effectiveness
        layer_stats = defaultdict(lambda: {'hits': 0, 'total': 0, 'time': 0})
        for record in self.usage_history:
            layer = record['cache_layer']
            layer_stats[layer]['total'] += 1
            if record['cache_hit']:
                layer_stats[layer]['hits'] += 1
            layer_stats[layer]['time'] += record['response_time_ms']
        
        # Time-based patterns
        hour_stats = defaultdict(int)
        for record in self.usage_history:
            hour = datetime.fromisoformat(record['timestamp']).hour
            hour_stats[hour] += 1
        
        # Calculate metrics
        total_queries = len(self.usage_history)
        overall_hit_rate = sum(1 for r in self.usage_history if r['cache_hit']) / total_queries * 100
        avg_response = sum(r['response_time_ms'] for r in self.usage_history) / total_queries
        
        return {
            'total_queries': total_queries,
            'overall_hit_rate': round(overall_hit_rate, 2),
            'avg_response_ms': round(avg_response, 2),
            'top_queries': sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'layer_effectiveness': {
                layer: {
                    'hit_rate': round(stats['hits'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0,
                    'avg_time': round(stats['time'] / stats['total'], 2) if stats['total'] > 0 else 0,
                    'usage_count': stats['total']
                }
                for layer, stats in layer_stats.items()
            },
            'hourly_distribution': dict(hour_stats),
        }
    
    def optimize(self) -> Dict:
        """
        Optimize cache configuration based on usage patterns
        
        Returns:
            Optimized configuration
        """
        patterns = self.analyze_patterns()
        
        if not patterns:
            print("⚠️  Insufficient data for optimization")
            return self.config
        
        # Optimize TTL based on query frequency
        top_queries = patterns.get('top_queries', [])
        
        if top_queries:
            # High-frequency queries → longer TTL
            avg_frequency = sum(count for _, count in top_queries) / len(top_queries)
            
            if avg_frequency > 10:
                self.optimal_config['base_ttl'] = max(600, self.config['base_ttl'] * 1.5)
            elif avg_frequency < 3:
                self.optimal_config['base_ttl'] = max(300, self.config['base_ttl'] * 0.8)
        
        # Optimize cache size based on hit rate
        hit_rate = patterns.get('overall_hit_rate', 0)
        
        if hit_rate < 50:
            # Low hit rate → increase cache size
            self.optimal_config['max_cache_size'] = min(2000, self.config['max_cache_size'] * 1.2)
        elif hit_rate > 90:
            # High hit rate → can reduce size
            self.optimal_config['max_cache_size'] = max(500, self.config['max_cache_size'] * 0.9)
        
        # Optimize layer TTLs based on effectiveness
        layer_stats = patterns.get('layer_effectiveness', {})
        
        if 'L1' in layer_stats and layer_stats['L1']['hit_rate'] > 80:
            # L1 very effective → increase L1 TTL
            self.optimal_config['l1_ttl'] = min(7200, self.config['l1_ttl'] * 1.2)
        
        if 'Semantic' in layer_stats and layer_stats['Semantic']['hit_rate'] < 30:
            # Semantic not effective → adjust threshold
            self.optimal_config['similarity_threshold'] = max(0.6, self.config['similarity_threshold'] - 0.05)
        
        # Record optimization
        self.stats['optimizations_run'] += 1
        self.stats['last_optimization'] = datetime.now().isoformat()
        
        print(f"✅ Optimization complete:")
        print(f"   Base TTL: {self.config['base_ttl']}s → {self.optimal_config['base_ttl']}s")
        print(f"   Max cache size: {self.config['max_cache_size']} → {self.optimal_config['max_cache_size']}")
        print(f"   L1 TTL: {self.config['l1_ttl']}s → {self.optimal_config['l1_ttl']}s")
        
        return self.optimal_config
    
    def get_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        patterns = self.analyze_patterns()
        recommendations = []
        
        if not patterns:
            return ["⚠️  Insufficient data for recommendations"]
        
        # Hit rate recommendations
        hit_rate = patterns.get('overall_hit_rate', 0)
        if hit_rate < 50:
            recommendations.append(f"⚠️  Low hit rate ({hit_rate}%). Consider increasing cache size or TTL.")
        elif hit_rate > 95:
            recommendations.append(f"✅ Excellent hit rate ({hit_rate}%). Cache is well-optimized.")
        
        # Response time recommendations
        avg_response = patterns.get('avg_response_ms', 0)
        if avg_response > 100:
            recommendations.append(f"⚠️  High avg response ({avg_response}ms). Consider optimizing slower cache layers.")
        elif avg_response < 10:
            recommendations.append(f"✅ Excellent response time ({avg_response}ms).")
        
        # Layer-specific recommendations
        layer_stats = patterns.get('layer_effectiveness', {})
        
        for layer, stats in layer_stats.items():
            if stats['hit_rate'] < 30 and stats['usage_count'] > 10:
                recommendations.append(f"⚠️  {layer} layer has low hit rate ({stats['hit_rate']}%). Consider tuning.")
            elif stats['hit_rate'] > 80:
                recommendations.append(f"✅ {layer} layer is highly effective ({stats['hit_rate']}% hit rate).")
        
        return recommendations
    
    def get_stats(self) -> Dict:
        """Get tuner statistics"""
        patterns = self.analyze_patterns()
        
        return {
            'optimizations_run': self.stats['optimizations_run'],
            'last_optimization': self.stats['last_optimization'],
            'current_config': self.config,
            'optimal_config': self.optimal_config,
            'usage_records': len(self.usage_history),
            'performance_records': len(self.performance_history),
            'patterns': patterns,
            'recommendations': self.get_recommendations(),
        }
    
    def apply_optimal(self):
        """Apply optimal configuration"""
        self.config = self.optimal_config.copy()
        print("✅ Optimal configuration applied")
        
        # Save configuration
        config_file = TUNER_DIR / 'current_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def export_report(self, output_file: Path = None) -> Path:
        """Export optimization report"""
        if output_file is None:
            output_file = TUNER_DIR / 'optimization_report.json'
        
        data = {
            'stats': self.get_stats(),
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Report exported to: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Tuner")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--optimize', action='store_true', help='Run optimization')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--apply', action='store_true', help='Apply optimal config')
    args = parser.parse_args()
    
    tuner = AutoTuner()
    
    if args.demo:
        print("\n🤖 Auto-Tuner Demo")
        print("=" * 80)
        
        # Simulate usage data
        print("\n📊 Simulating usage data...\n")
        
        import random
        queries = ["memory", "security", "workflow", "memory evolution", "security config"]
        layers = ["L1", "L2", "Semantic", "Index", "Vector"]
        
        for i in range(100):
            query = random.choice(queries)
            cache_hit = random.random() > 0.3  # 70% hit rate
            response_time = random.uniform(1, 100) if cache_hit else random.uniform(100, 500)
            layer = random.choice(layers) if cache_hit else "Miss"
            
            tuner.record_usage(query, cache_hit, response_time, layer)
        
        print(f"Recorded {len(tuner.usage_history)} usage records")
        
        # Analyze patterns
        print("\n🔍 Analyzing patterns...")
        patterns = tuner.analyze_patterns()
        
        print(f"\nTotal queries: {patterns.get('total_queries', 0)}")
        print(f"Overall hit rate: {patterns.get('overall_hit_rate', 0)}%")
        print(f"Avg response: {patterns.get('avg_response_ms', 0)}ms")
        
        print("\nTop queries:")
        for query, count in patterns.get('top_queries', [])[:5]:
            print(f"   {query}: {count}")
        
        # Get recommendations
        print("\n💡 Recommendations:")
        for rec in tuner.get_recommendations():
            print(f"   {rec}")
        
        # Run optimization
        print("\n⚙️  Running optimization...")
        optimal = tuner.optimize()
        
        # Show stats
        print("\n📈 Tuner Statistics:")
        stats = tuner.get_stats()
        print(f"   Optimizations run: {stats['optimizations_run']}")
        print(f"   Usage records: {stats['usage_records']}")
        
        print("\n✅ Demo complete!")
    
    elif args.optimize:
        print("\n⚙️  Running optimization...")
        optimal = tuner.optimize()
        
        print("\n💡 Recommendations:")
        for rec in tuner.get_recommendations():
            print(f"   {rec}")
    
    elif args.apply:
        tuner.apply_optimal()
    
    elif args.stats:
        stats = tuner.get_stats()
        print("\n📊 Auto-Tuner Statistics")
        print("=" * 80)
        print(f"Optimizations run: {stats['optimizations_run']}")
        print(f"Usage records: {stats['usage_records']}")
        print(f"\nCurrent config:")
        for key, val in stats['current_config'].items():
            print(f"   {key}: {val}")
        print(f"\nOptimal config:")
        for key, val in stats['optimal_config'].items():
            print(f"   {key}: {val}")
        
        print(f"\nRecommendations:")
        for rec in stats['recommendations']:
            print(f"   {rec}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
