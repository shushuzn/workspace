#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Forgetting Mechanism - Intelligent memory pruning based on Ebbinghaus curve
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import math

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
ARCHIVE_DIR = MEMORY_DIR / 'archive'
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ForgettingCandidate:
    """Memory candidate for forgetting"""
    memory_id: str
    content_preview: str
    category: str
    created_at: str
    last_accessed: str
    days_inactive: int
    access_count: int
    current_strength: float
    decay_rate: float
    recommendation: str  # forget/archive/retain
    confidence: float

class MemoryForgetting:
    """
    Implements Ebbinghaus forgetting curve for memory management
    Forgets low-value memories, archives medium-value, retains high-value
    """
    
    def __init__(self):
        # Ebbinghaus curve parameters
        self.retention_params = {
            'initial_strength': 1.0,
            'decay_constant': 0.5,  # Controls decay speed
            'review_boost': 1.5,  # Strength boost after review
        }
        
        # Thresholds
        self.thresholds = {
            'forget': 0.2,  # Below = forget
            'archive': 0.4,  # Below = archive
            'retain': 0.4,  # Above = retain
        }
        
        # Priority modifiers
        self.priority_modifiers = {
            'CRITICAL': 1.5,
            'HIGH': 1.2,
            'MEDIUM': 1.0,
            'LOW': 0.8,
        }
    
    def calculate_retention(self, days_since_review: int, 
                           initial_strength: float = 1.0) -> float:
        """
        Calculate memory retention using Ebbinghaus curve
        R = exp(-t/S) where S is strength factor
        """
        if days_since_review < 0:
            return initial_strength
        
        # Ebbinghaus exponential decay
        retention = initial_strength * math.exp(
            -self.retention_params['decay_constant'] * days_since_review
        )
        
        return max(retention, 0.0)
    
    def calculate_optimal_review_time(self, current_strength: float) -> int:
        """
        Calculate optimal time for next review
        Returns days until next review recommended
        """
        if current_strength >= 0.8:
            return 30  # Strong memory, review in 30 days
        elif current_strength >= 0.6:
            return 14  # Medium-strong, review in 14 days
        elif current_strength >= 0.4:
            return 7  # Medium, review in 7 days
        elif current_strength >= 0.2:
            return 3  # Weak, review in 3 days
        else:
            return 1  # Very weak, review tomorrow
    
    def get_forgetting_curve(self, days: int = 30) -> List[Tuple[int, float]]:
        """
        Generate forgetting curve data for visualization
        Returns list of (day, retention) tuples
        """
        curve = []
        for day in range(days + 1):
            retention = self.calculate_retention(day)
            curve.append((day, retention))
        return curve
    
    def evaluate_memory(self, memory_id: str, content: str,
                       created_at: str, last_accessed: str,
                       access_count: int, priority: str = 'MEDIUM',
                       category: str = 'general') -> ForgettingCandidate:
        """
        Evaluate a memory for forgetting decision
        """
        # Parse dates
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            last_access = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
        except:
            created = datetime.now() - timedelta(days=30)
            last_access = datetime.now() - timedelta(days=15)
        
        now = datetime.now()
        days_since_created = (now - created).days
        days_since_access = (now - last_access).days
        
        # Calculate current strength
        base_strength = self.calculate_retention(days_since_access)
        
        # Apply priority modifier
        priority_mod = self.priority_modifiers.get(priority, 1.0)
        current_strength = base_strength * priority_mod
        
        # Access count bonus (frequent access = stronger)
        access_bonus = min(access_count * 0.02, 0.3)  # Max 0.3 bonus
        current_strength = min(current_strength + access_bonus, 1.0)
        
        # Calculate decay rate
        decay_rate = self.retention_params['decay_constant']
        if access_count > 10:
            decay_rate *= 0.7  # Slower decay for frequently accessed
        elif access_count < 2:
            decay_rate *= 1.3  # Faster decay for rarely accessed
        
        # Determine recommendation
        if current_strength < self.thresholds['forget']:
            recommendation = 'forget'
            confidence = 0.9
        elif current_strength < self.thresholds['archive']:
            recommendation = 'archive'
            confidence = 0.8
        else:
            recommendation = 'retain'
            confidence = 0.95
        
        # Content preview
        preview = content[:100].replace('\n', ' ') + '...' if len(content) > 100 else content
        
        return ForgettingCandidate(
            memory_id=memory_id,
            content_preview=preview,
            category=category,
            created_at=created_at,
            last_accessed=last_accessed,
            days_inactive=days_since_access,
            access_count=access_count,
            current_strength=round(current_strength, 3),
            decay_rate=round(decay_rate, 3),
            recommendation=recommendation,
            confidence=confidence
        )
    
    def batch_evaluate(self, memories: List[Dict]) -> List[ForgettingCandidate]:
        """Evaluate multiple memories"""
        candidates = []
        
        for mem in memories:
            candidate = self.evaluate_memory(
                memory_id=mem.get('id', 'unknown'),
                content=mem.get('content', ''),
                created_at=mem.get('created_at', ''),
                last_accessed=mem.get('last_accessed', ''),
                access_count=mem.get('access_count', 0),
                priority=mem.get('priority', 'MEDIUM'),
                category=mem.get('category', 'general')
            )
            candidates.append(candidate)
        
        return sorted(candidates, key=lambda c: c.current_strength)
    
    def archive_memory(self, memory_id: str, content: str, 
                      reason: str = '') -> str:
        """
        Archive a memory (move to archive directory)
        Returns archive file path
        """
        archive_file = ARCHIVE_DIR / f'{memory_id}_{datetime.now().strftime("%Y%m%d")}.md'
        
        archive_content = f"""# Archived Memory: {memory_id}
**Archived:** {datetime.now().isoformat()}
**Reason:** {reason if reason else 'Low retention strength'}

---

## Original Content

{content}

---

## Archive Metadata

- **Original ID:** {memory_id}
- **Archive Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Can Restore:** Yes (from archive)

"""
        
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write(archive_content)
        
        return str(archive_file)
    
    def generate_forgetting_report(self, candidates: List[ForgettingCandidate]) -> Dict:
        """Generate comprehensive forgetting report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_evaluated': len(candidates),
            'recommendations': {
                'forget': [],
                'archive': [],
                'retain': []
            },
            'statistics': {
                'avg_strength': 0.0,
                'avg_days_inactive': 0.0,
                'by_category': {}
            },
            'curve_data': self.get_forgetting_curve(30)
        }
        
        # Categorize
        for candidate in candidates:
            report['recommendations'][candidate.recommendation].append({
                'id': candidate.memory_id,
                'strength': candidate.current_strength,
                'days_inactive': candidate.days_inactive,
                'category': candidate.category,
            })
        
        # Statistics
        if candidates:
            report['statistics']['avg_strength'] = round(
                sum(c.current_strength for c in candidates) / len(candidates), 3
            )
            report['statistics']['avg_days_inactive'] = round(
                sum(c.days_inactive for c in candidates) / len(candidates), 1
            )
        
        # By category
        categories = {}
        for c in candidates:
            cat = c.category
            if cat not in categories:
                categories[cat] = {'total': 0, 'forget': 0, 'archive': 0}
            categories[cat]['total'] += 1
            if c.recommendation == 'forget':
                categories[cat]['forget'] += 1
            elif c.recommendation == 'archive':
                categories[cat]['archive'] += 1
        
        report['statistics']['by_category'] = categories
        
        return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Forgetting Mechanism")
    parser.add_argument('--evaluate', action='store_true', 
                       help='Evaluate memories for forgetting')
    parser.add_argument('--curve', action='store_true',
                       help='Display forgetting curve')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo with sample data')
    args = parser.parse_args()
    
    forgetting = MemoryForgetting()
    
    if args.curve:
        print("\n📈 Ebbinghaus Forgetting Curve")
        print("=" * 60)
        curve = forgetting.get_forgetting_curve(30)
        print(f"{'Day':<5} {'Retention':<10} {'Visual':<30}")
        print("-" * 60)
        for day, retention in curve[::3]:  # Every 3 days
            bars = '█' * int(retention * 20)
            print(f"{day:<5} {retention:<10.3f} {bars}")
        print()
    
    elif args.demo:
        print("\n🧠 Memory Forgetting Demo")
        print("=" * 60)
        
        # Sample memories
        samples = [
            {
                'id': 'mem_001',
                'content': 'Security best practices for API keys',
                'created_at': (datetime.now() - timedelta(days=90)).isoformat(),
                'last_accessed': (datetime.now() - timedelta(days=60)).isoformat(),
                'access_count': 2,
                'priority': 'HIGH',
                'category': 'security'
            },
            {
                'id': 'mem_002',
                'content': 'Old configuration from last year',
                'created_at': (datetime.now() - timedelta(days=365)).isoformat(),
                'last_accessed': (datetime.now() - timedelta(days=300)).isoformat(),
                'access_count': 1,
                'priority': 'LOW',
                'category': 'config'
            },
            {
                'id': 'mem_003',
                'content': 'Critical deployment procedure',
                'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
                'last_accessed': (datetime.now() - timedelta(days=1)).isoformat(),
                'access_count': 15,
                'priority': 'CRITICAL',
                'category': 'deployment'
            }
        ]
        
        candidates = forgetting.batch_evaluate(samples)
        
        print(f"\nEvaluated {len(candidates)} memories:\n")
        for c in candidates:
            icon = '🗑️' if c.recommendation == 'forget' else '📦' if c.recommendation == 'archive' else '✅'
            print(f"{icon} {c.memory_id}: {c.recommendation.upper()}")
            print(f"   Strength: {c.current_strength:.3f}, Days inactive: {c.days_inactive}")
            print(f"   Access count: {c.access_count}, Priority: {c.priority}")
            print()
        
        # Report
        report = forgetting.generate_forgetting_report(candidates))
        print(f"📊 Statistics:")
        print(f"   Average strength: {report['statistics']['avg_strength']:.3f}")
        print(f"   Average days inactive: {report['statistics']['avg_days_inactive']:.1f}")
        print(f"   Forget: {len(report['recommendations']['forget'])}")
        print(f"   Archive: {len(report['recommendations']['archive'])}")
        print(f"   Retain: {len(report['recommendations']['retain'])}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
