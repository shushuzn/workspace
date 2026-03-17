#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decision Self-Learning Optimizer
Learn from decision outcomes and auto-optimize rules

Usage:
    python decision_optimizer.py [--train] [--optimize] [--analyze]
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class DecisionFeedbackLogger:
    """Track decision outcomes"""
    
    def __init__(self, log_file: str = None):
        self.log_file = Path(log_file) if log_file else Path(__file__).parent.parent / '.decision_feedback.json'
        self.feedback_log = self._load_log()
    
    def _load_log(self) -> list:
        """Load feedback log"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def log_outcome(self, decision_id: str, outcome: str, 
                   actual_impact: float, expected_impact: float,
                   execution_time: float = None):
        """Log decision outcome"""
        entry = {
            'decision_id': decision_id,
            'outcome': outcome,  # success/failure/partial
            'actual_impact': actual_impact,
            'expected_impact': expected_impact,
            'impact_accuracy': actual_impact / expected_impact if expected_impact > 0 else 0,
            'execution_time': execution_time,
            'logged_at': datetime.now().isoformat()
        }
        
        self.feedback_log.append(entry)
        self._save_log()
        
        return entry
    
    def _save_log(self):
        """Save feedback log"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_log, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self, days: int = 7) -> dict:
        """Get feedback statistics"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.feedback_log 
                 if datetime.fromisoformat(e['logged_at']) > cutoff]
        
        if not recent:
            return {'count': 0}
        
        success_rate = sum(1 for e in recent if e['outcome'] == 'success') / len(recent) * 100
        avg_impact_accuracy = sum(e['impact_accuracy'] for e in recent) / len(recent)
        
        return {
            'count': len(recent),
            'success_rate': success_rate,
            'avg_impact_accuracy': avg_impact_accuracy,
            'period_days': days
        }


class RuleOptimizer:
    """Optimize decision rules based on feedback"""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent.parent / '.autonomous_config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load config"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def analyze_performance(self, feedback_stats: dict) -> dict:
        """Analyze rule performance"""
        analysis = {
            'current_auto_rate': self.config.get('optimization_rules', {}).get('increase_auto_rate_target', 0.85),
            'actual_success_rate': feedback_stats.get('success_rate', 0),
            'impact_accuracy': feedback_stats.get('avg_impact_accuracy', 0),
            'recommendations': []
        }
        
        # Generate recommendations
        if feedback_stats.get('success_rate', 0) > 95:
            analysis['recommendations'].append({
                'type': 'increase_autonomy',
                'reason': 'High success rate indicates rules can be more aggressive',
                'action': 'Increase max_risk_score by 5-10 points'
            })
        
        if feedback_stats.get('avg_impact_accuracy', 0) < 0.7:
            analysis['recommendations'].append({
                'type': 'adjust_scoring',
                'reason': 'Impact predictions are inaccurate',
                'action': 'Recalibrate impact scoring model'
            })
        
        return analysis
    
    def generate_optimized_config(self, analysis: dict) -> dict:
        """Generate optimized configuration"""
        optimized = self.config.copy()
        
        # Adjust risk thresholds based on success rate
        if analysis.get('actual_success_rate', 0) > 95:
            current_low = optimized.get('risk_thresholds', {}).get('low', 40)
            optimized['risk_thresholds'] = optimized.get('risk_thresholds', {})
            optimized['risk_thresholds']['low'] = min(current_low + 5, 50)
            optimized['risk_thresholds']['medium'] = min(current_low + 35, 80)
        
        # Update optimization rules
        optimized['optimization_rules'] = optimized.get('optimization_rules', {})
        optimized['optimization_rules']['last_optimized'] = datetime.now().isoformat()
        optimized['optimization_rules']['success_rate_at_optimization'] = analysis.get('actual_success_rate', 0)
        
        return optimized
    
    def apply_optimization(self, optimized_config: dict, dry_run: bool = True):
        """Apply optimized configuration"""
        if dry_run:
            print("[DRY-RUN] Would apply optimized config:")
            print(json.dumps(optimized_config.get('risk_thresholds', {}), indent=2))
            return
        
        # Backup current config
        backup_path = self.config_path.with_suffix('.json.bak')
        with open(self.config_path, 'r', encoding='utf-8') as f:
            original = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)
        
        # Apply new config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(optimized_config, f, indent=2, ensure_ascii=False)
        
        print(f"[APPLY] Optimization applied. Backup: {backup_path}")


class ReinforcementLearner:
    """Simple reinforcement learning for decision rules"""
    
    def __init__(self):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.9
    
    def update(self, state: str, action: str, reward: float):
        """Update Q-table"""
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[state].values()) if self.q_table[state] else 0
        
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[state][action] = new_value
    
    def get_best_action(self, state: str) -> str:
        """Get best action for state"""
        if not self.q_table[state]:
            return None
        return max(self.q_table[state].items(), key=lambda x: x[1])[0]
    
    def save(self, path: str):
        """Save Q-table"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(dict(self.q_table), f, indent=2)
    
    def load(self, path: str):
        """Load Q-table"""
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.q_table = defaultdict(lambda: defaultdict(float), 
                                          {k: defaultdict(float, v) for k, v in data.items()})


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Decision Optimizer')
    parser.add_argument('--train', action='store_true', help='Train on feedback')
    parser.add_argument('--optimize', action='store_true', help='Optimize rules')
    parser.add_argument('--analyze', action='store_true', help='Analyze performance')
    parser.add_argument('--apply', action='store_true', help='Apply optimization')
    parser.add_argument('--days', type=int, default=7, help='Analysis period')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[OPTIMIZER] Decision Self-Learning System")
    print("=" * 60)
    
    # Initialize
    logger = DecisionFeedbackLogger()
    optimizer = RuleOptimizer()
    
    # Analyze
    if args.analyze or True:  # Always analyze
        stats = logger.get_statistics(days=args.days)
        analysis = optimizer.analyze_performance(stats)
        
        print(f"\n[ANALYSIS]")
        print(f"  Decisions (last {args.days} days): {stats.get('count', 0)}")
        print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
        print(f"  Impact Accuracy: {stats.get('avg_impact_accuracy', 0):.2f}")
        
        if analysis.get('recommendations'):
            print(f"\n[RECOMMENDATIONS]")
            for rec in analysis['recommendations']:
                print(f"  - {rec['type']}: {rec['reason']}")
                print(f"    Action: {rec['action']}")
    
    # Optimize
    if args.optimize or args.apply:
        optimized = optimizer.generate_optimized_config(analysis)
        
        print(f"\n[OPTIMIZATION]")
        print(f"  Current risk thresholds: {optimizer.config.get('risk_thresholds', {})}")
        print(f"  Optimized thresholds: {optimized.get('risk_thresholds', {})}")
        
        if args.apply:
            optimizer.apply_optimization(optimized, dry_run=False)
        else:
            optimizer.apply_optimization(optimized, dry_run=True)
    
    # Output
    if args.json:
        output = {
            'statistics': stats,
            'analysis': analysis,
            'optimized_config': optimized if args.optimize else None
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
