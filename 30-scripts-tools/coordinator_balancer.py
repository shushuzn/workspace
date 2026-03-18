#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coordinator Workflow Balancer - 工作流平衡检查

Check workflow balance every 60 minutes.
Detect persona collaboration issues and trigger arbitration.

Features:
- Workflow balance checking (every 60min)
- Collaboration score monitoring
- Conflict detection
- Auto-trigger meta-cognition arbitration
- Generate balance recommendations

Author: OpenClaw Coordinator Agent
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class WorkflowBalancer:
    """Coordinator workflow balancer"""
    
    def __init__(self):
        self.workspace = Path('D:/OpenClaw/workspace')
        self.data_dir = self.workspace / 'data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.data_dir / 'coordinator_state.json'
        self.state = self.load_state()
        
        # Collaboration threshold
        self.COLLAB_THRESHOLD = 70  # Minimum acceptable collaboration score
        self.CONFLICT_THRESHOLD = 3  # Conflicts per week before intervention
    
    def load_state(self) -> Dict:
        """Load coordinator state"""
        state_file = self.data_dir / 'coordinator_state.json'
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'last_check': None,
            'checks_today': 0,
            'interventions': 0,
            'collaboration_scores': {}
        }
    
    def save_state(self):
        """Save coordinator state"""
        with open(self.data_dir / 'coordinator_state.json', 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def load_meta_cognition_data(self) -> Dict:
        """Load data from meta-cognition monitor"""
        meta_state_file = self.data_dir / 'meta_cognition_state.json'
        if meta_state_file.exists():
            with open(meta_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_health_history(self) -> List:
        """Load health history from meta-cognition"""
        history_file = self.data_dir / 'persona_health_history.json'
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def calculate_collaboration_scores(self, meta_data: Dict) -> Dict[str, float]:
        """Calculate collaboration scores for each persona"""
        scores = {}
        
        # Get persona scores from meta-cognition
        persona_scores = meta_data.get('persona_scores', {})
        
        for persona, score in persona_scores.items():
            # Collaboration score is slightly different from individual score
            # Based on interaction patterns
            scores[persona] = min(100, score + 5)
        
        return scores
    
    def detect_imbalances(self, collab_scores: Dict[str, float]) -> List[str]:
        """Detect workflow imbalances"""
        imbalances = []
        
        # Check for low collaboration scores
        for persona, score in collab_scores.items():
            if score < self.COLLAB_THRESHOLD:
                imbalances.append(
                    f"{persona.capitalize()} collaboration low ({score:.1f}/100 < {self.COLLAB_THRESHOLD})"
                )
        
        # Check for score variance (some personas much higher than others)
        if collab_scores:
            scores = list(collab_scores.values())
            avg = sum(scores) / len(scores)
            variance = sum((s - avg) ** 2 for s in scores) / len(scores)
            
            if variance > 400:  # High variance threshold
                imbalances.append(f"High persona score variance ({variance:.1f})")
        
        return imbalances
    
    def detect_conflicts(self, history: List) -> int:
        """Count conflicts this week"""
        if not history:
            return 0
        
        # Count records with alerts
        conflicts = 0
        for record in history[-50:]:  # Last 50 checks
            if record.get('alerts'):
                conflicts += len(record['alerts'])
        
        return conflicts
    
    def generate_recommendations(self, imbalances: List[str], conflicts: int) -> List[str]:
        """Generate balance recommendations"""
        recommendations = []
        
        if any('collaboration low' in i for i in imbalances):
            recommendations.append(
                "Schedule persona collaboration review session"
            )
            recommendations.append(
                "Implement pair programming for low-collab personas"
            )
        
        if conflicts > self.CONFLICT_THRESHOLD:
            recommendations.append(
                f"High conflict rate ({conflicts}/week) - trigger meta-cognition arbitration"
            )
        
        if any('variance' in i for i in imbalances):
            recommendations.append(
                "Balance workload distribution across personas"
            )
        
        if not recommendations:
            recommendations.append("Workflow balanced - continue monitoring")
        
        return recommendations
    
    def trigger_arbitration(self, reason: str):
        """Trigger meta-cognition arbitration"""
        print(f"\n⚖️  Triggering Meta-Cognition Arbitration...")
        print(f"   Reason: {reason}")
        
        # Log arbitration request
        arbitration_log = {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'status': 'triggered'
        }
        
        log_file = self.data_dir / 'arbitration_log.json'
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        logs.append(arbitration_log)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Arbitration request logged")
        print(f"   📁 Log: {log_file}\n")
        
        self.state['interventions'] += 1
    
    def run_check(self) -> Dict:
        """Run workflow balance check"""
        print(f"\n{'='*70}")
        print(f"⚖️  Coordinator Workflow Balance Check")
        print(f"{'='*70}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Check #{self.state['checks_today'] + 1} today")
        print(f"{'='*70}\n")
        
        # Load data
        meta_data = self.load_meta_cognition_data()
        history = self.load_health_history()
        
        # Calculate collaboration scores
        collab_scores = self.calculate_collaboration_scores(meta_data)
        self.state['collaboration_scores'] = collab_scores
        
        # Print collaboration scores
        print(f"📊 Collaboration Scores:")
        for persona, score in collab_scores.items():
            icon = '✅' if score >= self.COLLAB_THRESHOLD else '⚠️'
            print(f"   {icon} {persona.capitalize():15} {score:5.1f}/100")
        
        # Detect imbalances
        imbalances = self.detect_imbalances(collab_scores)
        
        # Detect conflicts
        conflicts = self.detect_conflicts(history)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(imbalances, conflicts)
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"⚖️  Workflow Balance Summary")
        print(f"{'='*70}")
        print(f"Imbalances Detected: {len(imbalances)}")
        print(f"Conflicts This Week: {conflicts}")
        print(f"Interventions Today: {self.state['interventions']}")
        
        if imbalances:
            print(f"\n⚠️  Imbalances:")
            for i, imbalance in enumerate(imbalances, 1):
                print(f"   {i}. {imbalance}")
        
        if conflicts > self.CONFLICT_THRESHOLD:
            print(f"\n🚨 High Conflict Rate: {conflicts}/week (threshold: {self.CONFLICT_THRESHOLD})")
            self.trigger_arbitration(f"High conflict rate: {conflicts}/week")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Update state
        self.state['last_check'] = datetime.now().isoformat()
        self.state['checks_today'] += 1
        self.save_state()
        
        print(f"\n{'='*70}\n")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'collaboration_scores': collab_scores,
            'imbalances': imbalances,
            'conflicts': conflicts,
            'recommendations': recommendations,
            'interventions': self.state['interventions']
        }
    
    def status(self) -> Dict:
        """Show coordinator status"""
        print(f"\n{'='*70}")
        print(f"⚖️  Coordinator Status")
        print(f"{'='*70}")
        print(f"Last Check: {self.state['last_check'] or 'Never'}")
        print(f"Checks Today: {self.state['checks_today']}")
        print(f"Interventions: {self.state['interventions']}")
        
        if self.state['collaboration_scores']:
            print(f"\nCollaboration Scores:")
            for persona, score in self.state['collaboration_scores'].items():
                print(f"   {persona.capitalize():15} {score:5.1f}/100")
        
        print(f"{'='*70}\n")
        
        return self.state


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Coordinator Workflow Balancer')
    subparsers = parser.add_subparsers(dest='cmd', help='Command')
    
    # Check
    p_check = subparsers.add_parser('check', help='Run balance check')
    
    # Status
    p_status = subparsers.add_parser('status', help='Show status')
    
    args = parser.parse_args()
    
    balancer = WorkflowBalancer()
    
    if args.cmd == 'check' or args.cmd is None:
        balancer.run_check()
    
    elif args.cmd == 'status':
        balancer.status()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
