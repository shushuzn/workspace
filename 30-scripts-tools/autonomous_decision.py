#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Autonomous Decision Engine - AI Self-Decision Framework
Features: Confidence-based decisions, auto-execute, decision log, learning

Usage:
    python autonomous_decision.py --enable
    python autonomous_decision.py --status
    python autonomous_decision.py --review
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class DecisionLevel(Enum):
    """Decision confidence levels"""
    AUTO = "auto"  # ≥90% - Auto execute
    FAST = "fast"  # 70-89% - Fast confirm (1 min timeout)
    FULL = "full"  # <70% - Full confirmation


@dataclass
class Decision:
    """Decision record"""
    id: str
    timestamp: str
    task: str
    description: str
    confidence: float
    level: str
    action: str
    status: str  # pending/executed/reverted/skipped
    reasoning: List[str]
    alternatives: List[str]
    outcome: Optional[str] = None
    user_review: Optional[str] = None


@dataclass
class DecisionPolicy:
    """Decision policy configuration"""
    auto_threshold: float = 90.0
    fast_threshold: float = 70.0
    timeout_seconds: int = 60
    max_auto_per_hour: int = 10
    require_review: bool = True
    allowed_categories: List[str] = None


class AutonomousDecisionEngine:
    """AI autonomous decision engine"""
    
    def __init__(self):
        self.config_dir = WORKSPACE / "00-09-core-config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.decisions_dir = WORKSPACE / "20-data-reports" / "decisions"
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "decision_policy.json"
        self.decisions_file = self.decisions_dir / "decision_log.json"
        self.pending_file = self.decisions_dir / "pending_decisions.json"
        
        self.policy = self.load_policy()
        self.decisions = []
        self.pending = []
        
        self.load_decisions()
    
    def load_policy(self) -> DecisionPolicy:
        """Load decision policy"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return DecisionPolicy(**data)
        
        # Default policy
        return DecisionPolicy(
            allowed_categories=[
                'file_cleanup',
                'cache_refresh',
                'token_refresh',
                'backup',
                'health_check',
                'data_collection',
                'report_generation'
            ]
        )
    
    def save_policy(self):
        """Save decision policy"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.policy), f, indent=2, ensure_ascii=False)
    
    def load_decisions(self):
        """Load decision history"""
        if self.decisions_file.exists():
            with open(self.decisions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.decisions = [Decision(**d) for d in data.get('decisions', [])]
        
        if self.pending_file.exists():
            with open(self.pending_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.pending = [Decision(**d) for d in data.get('pending', [])]
    
    def save_decisions(self):
        """Save decision history"""
        with open(self.decisions_file, 'w', encoding='utf-8') as f:
            json.dump({
                'decisions': [asdict(d) for d in self.decisions[-500:]],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            json.dump({
                'pending': [asdict(d) for d in self.pending],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def generate_decision_id(self, task: str) -> str:
        """Generate unique decision ID"""
        timestamp = datetime.now().isoformat()
        content = f"{task}-{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def calculate_confidence(self, task: str, context: Dict) -> float:
        """Calculate decision confidence score"""
        confidence = 50.0  # Base confidence
        
        # Factor 1: Task category
        category = context.get('category', 'unknown')
        if category in self.policy.allowed_categories:
            confidence += 20.0
        
        # Factor 2: Historical success rate
        similar_decisions = [
            d for d in self.decisions
            if task.split('_')[0] in d.task.split('_')[0]
        ]
        
        if similar_decisions:
            success_rate = sum(
                1 for d in similar_decisions
                if d.status == 'executed' and d.outcome == 'success'
            ) / len(similar_decisions)
            confidence += success_rate * 25.0
        
        # Factor 3: Risk level
        risk = context.get('risk', 'medium')
        if risk == 'low':
            confidence += 10.0
        elif risk == 'high':
            confidence -= 15.0
        
        # Factor 4: Data availability
        data_quality = context.get('data_quality', 'medium')
        if data_quality == 'high':
            confidence += 10.0
        elif data_quality == 'low':
            confidence -= 10.0
        
        # Factor 5: Time sensitivity
        urgency = context.get('urgency', 'normal')
        if urgency == 'high':
            confidence += 5.0  # Bias toward action in emergencies
        
        return min(max(confidence, 0.0), 100.0)
    
    def make_decision(self, task: str, description: str, context: Dict = None) -> Decision:
        """Make autonomous decision"""
        context = context or {}
        
        confidence = self.calculate_confidence(task, context)
        
        # Determine decision level
        if confidence >= self.policy.auto_threshold:
            level = DecisionLevel.AUTO
        elif confidence >= self.policy.fast_threshold:
            level = DecisionLevel.FAST
        else:
            level = DecisionLevel.FULL
        
        # Generate reasoning
        reasoning = [
            f"Confidence: {confidence:.1f}%",
            f"Category: {context.get('category', 'unknown')}",
            f"Risk: {context.get('risk', 'medium')}",
            f"Data quality: {context.get('data_quality', 'medium')}",
        ]
        
        # Generate alternatives
        alternatives = context.get('alternatives', ['Do nothing', 'Manual review'])
        
        decision = Decision(
            id=self.generate_decision_id(task),
            timestamp=datetime.now().isoformat(),
            task=task,
            description=description,
            confidence=round(confidence, 1),
            level=level.value,
            action=context.get('recommended_action', 'Proceed'),
            status='pending',
            reasoning=reasoning,
            alternatives=alternatives
        )
        
        # Auto-execute if confidence high enough
        if level == DecisionLevel.AUTO:
            print(f"\n🤖 AUTO DECISION (Confidence: {confidence:.1f}%)")
            print(f"  Task: {task}")
            print(f"  Action: {decision.action}")
            print(f"  Executing...\n")
            
            decision.status = 'executed'
            # Here would call the actual action
            # For now, just log
        
        elif level == DecisionLevel.FAST:
            print(f"\n⚡ FAST DECISION (Confidence: {confidence:.1f}%)")
            print(f"  Task: {task}")
            print(f"  Action: {decision.action}")
            print(f"  Timeout: {self.policy.timeout_seconds}s")
            print(f"  (No objection within timeout → auto-execute)\n")
            
            self.pending.append(decision)
            self.save_decisions()
        
        else:
            print(f"\n📋 FULL REVIEW REQUIRED (Confidence: {confidence:.1f}%)")
            print(f"  Task: {task}")
            print(f"  Action: {decision.action}")
            print(f"  Reasoning: {', '.join(reasoning)}")
            print(f"  Alternatives: {', '.join(alternatives)}\n")
            
            self.pending.append(decision)
            self.save_decisions()
        
        self.decisions.append(decision)
        self.save_decisions()
        
        return decision
    
    def review_pending(self, decision_id: str, approve: bool, user_comment: str = None):
        """Review pending decision"""
        for i, decision in enumerate(self.pending):
            if decision.id == decision_id:
                if approve:
                    decision.status = 'executed'
                    decision.user_review = f"Approved: {user_comment}" if user_comment else "Approved"
                    print(f"✅ Decision {decision_id} approved")
                else:
                    decision.status = 'skipped'
                    decision.user_review = f"Rejected: {user_comment}" if user_comment else "Rejected"
                    print(f"❌ Decision {decision_id} rejected")
                
                self.pending.pop(i)
                self.save_decisions()
                return
        
        print(f"⚠️  Decision {decision_id} not found")
    
    def auto_timeout_check(self):
        """Check for timed-out fast decisions"""
        now = datetime.now()
        
        for decision in self.pending[:]:
            if decision.level == 'fast':
                decision_time = datetime.fromisoformat(decision.timestamp)
                elapsed = (now - decision_time).total_seconds()
                
                if elapsed > self.policy.timeout_seconds:
                    print(f"\n⏰ TIMEOUT: Decision {decision.id}")
                    print(f"  Auto-executing (no objection received)\n")
                    
                    decision.status = 'executed'
                    decision.user_review = "Auto-approved (timeout)"
                    self.pending.remove(decision)
        
        self.save_decisions()
    
    def get_statistics(self) -> Dict:
        """Get decision statistics"""
        total = len(self.decisions)
        
        if total == 0:
            return {
                'total': 0,
                'auto': 0,
                'fast': 0,
                'full': 0,
                'executed': 0,
                'success_rate': 0
            }
        
        by_level = {
            'auto': sum(1 for d in self.decisions if d.level == 'auto'),
            'fast': sum(1 for d in self.decisions if d.level == 'fast'),
            'full': sum(1 for d in self.decisions if d.level == 'full')
        }
        
        executed = sum(1 for d in self.decisions if d.status == 'executed')
        success = sum(1 for d in self.decisions if d.status == 'executed' and d.outcome == 'success')
        
        avg_confidence = sum(d.confidence for d in self.decisions) / total
        
        return {
            'total': total,
            'by_level': by_level,
            'executed': executed,
            'success': success,
            'success_rate': round(success / executed * 100, 1) if executed > 0 else 0,
            'avg_confidence': round(avg_confidence, 1),
            'pending': len(self.pending)
        }
    
    def review_recent(self, limit: int = 10) -> List[Dict]:
        """Review recent decisions"""
        return [
            asdict(d) for d in sorted(
                self.decisions,
                key=lambda x: x.timestamp,
                reverse=True
            )[:limit]
        ]
    
    def enable_autonomous(self, categories: List[str] = None):
        """Enable autonomous mode"""
        self.policy.allowed_categories = categories or [
            'file_cleanup',
            'cache_refresh',
            'token_refresh',
            'backup',
            'health_check',
            'data_collection',
            'report_generation',
            'log_rotation',
            'temp_cleanup',
            'auto_commit'
        ]
        self.save_policy()
        
        print("\n✅ Autonomous mode ENABLED")
        print(f"  Allowed categories: {', '.join(self.policy.allowed_categories)}")
        print(f"  Auto threshold: {self.policy.auto_threshold}%")
        print(f"  Fast threshold: {self.policy.fast_threshold}%\n")
    
    def disable_autonomous(self):
        """Disable autonomous mode"""
        self.policy.allowed_categories = []
        self.save_policy()
        
        print("\n⚠️  Autonomous mode DISABLED")
        print("  All decisions require full review\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Autonomous Decision Engine')
    parser.add_argument('--enable', action='store_true', help='Enable autonomous mode')
    parser.add_argument('--disable', action='store_true', help='Disable autonomous mode')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--review', action='store_true', help='Review recent decisions')
    parser.add_argument('--approve', type=str, help='Approve pending decision')
    parser.add_argument('--reject', type=str, help='Reject pending decision')
    parser.add_argument('--test', action='store_true', help='Test decision making')
    args = parser.parse_args()
    
    engine = AutonomousDecisionEngine()
    
    if args.enable:
        engine.enable_autonomous()
    
    elif args.disable:
        engine.disable_autonomous()
    
    elif args.status:
        stats = engine.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.review:
        decisions = engine.review_recent()
        print(json.dumps(decisions, indent=2, ensure_ascii=False))
    
    elif args.approve:
        engine.review_pending(args.approve, True)
    
    elif args.reject:
        engine.review_pending(args.reject, False)
    
    elif args.test:
        # Test decision
        print("\n🧪 Testing Decision Engine\n")
        
        # High confidence decision (auto)
        d1 = engine.make_decision(
            'cache_cleanup',
            'Clear expired cache entries',
            {
                'category': 'cache_refresh',
                'risk': 'low',
                'data_quality': 'high',
                'recommended_action': 'Clear cache older than 24h'
            }
        )
        
        # Medium confidence (fast confirm)
        d2 = engine.make_decision(
            'data_collection',
            'Collect arXiv papers (50 limit)',
            {
                'category': 'data_collection',
                'risk': 'low',
                'data_quality': 'medium',
                'recommended_action': 'Collect latest 50 papers'
            }
        )
        
        # Low confidence (full review)
        d3 = engine.make_decision(
            'model_update',
            'Update local LLM to new version',
            {
                'category': 'model_update',
                'risk': 'medium',
                'data_quality': 'medium',
                'recommended_action': 'Download and install new model',
                'alternatives': ['Keep current version', 'Test in sandbox first']
            }
        )
        
        print("\n📊 Test Results:")
        stats = engine.get_statistics()
        print(json.dumps(stats, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
