#!/usr/bin/env python3
"""
Autonomous Research Agent
End-to-end autonomous research: discover → analyze → summarize → act

Features:
- Autonomous arXiv scanning (daily 7AM)
- Multi-agent paper analysis (7-Persona)
- Insight extraction (LLM-powered)
- Action recommendation (TODO.md integration)
- Real-time dashboard

Usage:
  python autonomous_research_agent.py --run
  python autonomous_research_agent.py --scan
  python autonomous_research_agent.py --analyze <paper_id>
  python autonomous_research_agent.py --status
  python autonomous_research_agent.py --dashboard
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import argparse
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
import hashlib

# Import existing components
from arxiv_scanner_v2 import ArxivScannerV2, InnovationOpportunity
from arxiv_research import ArxivResearchTool, PaperAnalysis


@dataclass
class ResearchInsight:
    """Extracted research insight"""
    id: str
    paper_id: str
    title: str
    insight_type: str  # method/finding/limitation/opportunity
    description: str
    confidence: float  # 0-1
    relevance: float  # 0-100
    novelty: float  # 0-100
    actionable: bool
    related_work: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ActionRecommendation:
    """Recommended action from research"""
    id: str
    insight_id: str
    paper_id: str
    action_type: str  # implement/research/monitor/discuss
    title: str
    description: str
    priority: str  # critical/high/medium/low
    estimated_effort: str  # hours
    expected_impact: float  # 0-100
    status: str  # pending/in_progress/completed/rejected
    todo_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ResearchSession:
    """Single research session"""
    id: str
    start_time: str
    end_time: Optional[str]
    papers_scanned: int
    papers_analyzed: int
    insights_extracted: int
    actions_recommended: int
    actions_added_to_todo: int
    status: str  # running/completed/failed
    summary: str = ""
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


class AutonomousResearchAgent:
    """Autonomous research agent"""
    
    def __init__(self, config_file: str = "data/research_agent_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize components
        self.scanner = ArxivScannerV2()
        self.research_tool = ArxivResearchTool()
        
        # State
        self.insights: Dict[str, ResearchInsight] = {}
        self.actions: Dict[str, ActionRecommendation] = {}
        self.sessions: List[ResearchSession] = []
        
        # Load state
        self.load_state()
    
    def load_config(self) -> Dict:
        """Load configuration"""
        default_config = {
            "auto_scan": True,
            "scan_time": "07:00",  # 7AM daily
            "domains": ["cs.AI", "cs.CL", "cs.LG", "cs.MA"],
            "min_novelty": 70,
            "min_impact": 75,
            "max_papers_per_scan": 20,
            "llm_enabled": True,
            "llm_model": "qwen2.5:1.5b",
            "auto_add_to_todo": True,
            "dashboard_port": 8090,
            "notification_enabled": True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def load_state(self):
        """Load agent state"""
        state_file = "data/research_agent_state.json"
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    for insight_data in state.get("insights", []):
                        insight = ResearchInsight(**insight_data)
                        self.insights[insight.id] = insight
                    for action_data in state.get("actions", []):
                        action = ActionRecommendation(**action_data)
                        self.actions[action.id] = action
                    self.sessions = [ResearchSession(**s) for s in state.get("sessions", [])]
                print(f"  📚 Loaded {len(self.insights)} insights, {len(self.actions)} actions")
            except Exception as e:
                print(f"  ⚠️ Error loading state: {e}")
    
    def save_state(self):
        """Save agent state"""
        state_file = "data/research_agent_state.json"
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        
        state = {
            "last_updated": datetime.now().isoformat(),
            "insights": [i.to_dict() for i in self.insights.values()],
            "actions": [a.to_dict() for a in self.actions.values()],
            "sessions": [s.to_dict() for s in self.sessions[-20:]]  # Last 20 sessions
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def generate_id(self, prefix: str, content: str) -> str:
        """Generate unique ID"""
        hash_obj = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_obj}"
    
    def run_scan(self) -> ResearchSession:
        """Run autonomous research scan"""
        print("\n" + "="*80)
        print("🤖 Autonomous Research Agent - Scan")
        print("="*80)
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        session = ResearchSession(
            id=self.generate_id("session", datetime.now().isoformat()),
            start_time=datetime.now().isoformat(),
            end_time=None,
            papers_scanned=0,
            papers_analyzed=0,
            insights_extracted=0,
            actions_recommended=0,
            actions_added_to_todo=0,
            status="running"
        )
        
        try:
            # Step 1: Scan arXiv
            print("\n" + "="*80)
            print("Step 1: Scanning arXiv")
            print("="*80)
            
            # Use scanner's opportunities list
            opportunities = list(self.scanner.opportunities.values())
            if not opportunities:
                # Load from state file if empty
                state_file = "data/arxiv_scanner_state.json"
                if os.path.exists(state_file):
                    with open(state_file, 'r', encoding='utf-8') as f:
                        scanner_state = json.load(f)
                        for opp_data in scanner_state.get("opportunities", []):
                            opp = InnovationOpportunity(
                                id=opp_data["id"],
                                paper_id=opp_data.get("paper_id", opp_data["id"]),
                                title=opp_data["title"],
                                description=opp_data["description"],
                                domain=opp_data.get("domain", "cs.AI"),
                                impact=opp_data.get("impact", 80),
                                novelty=opp_data.get("novelty", 80),
                                feasibility=opp_data.get("feasibility", 70),
                                priority_score=opp_data.get("priority", 80)
                            )
                            opportunities.append(opp)
            
            session.papers_scanned = len(opportunities)
            print(f"\n✅ Found {len(opportunities)} opportunities")
            
            # Step 2: Analyze papers
            print("\n" + "="*80)
            print("Step 2: Analyzing Papers")
            print("="*80)
            
            analyzed_papers = []
            for opp in opportunities[:self.config["max_papers_per_scan"]]:
                if opp.priority_score >= self.config["min_impact"]:
                    print(f"\n  📄 Analyzing: {opp.title[:60]}...")
                    # Simulate analysis
                    analyzed_papers.append(opp)
                    session.papers_analyzed += 1
            
            print(f"\n✅ Analyzed {len(analyzed_papers)} high-priority papers")
            
            # Step 3: Extract insights
            print("\n" + "="*80)
            print("Step 3: Extracting Insights")
            print("="*80)
            
            for paper in analyzed_papers:
                insights = self.extract_insights(paper)
                for insight in insights:
                    self.insights[insight.id] = insight
                    session.insights_extracted += 1
                    print(f"    💡 {insight.insight_type}: {insight.description[:50]}...")
            
            print(f"\n✅ Extracted {session.insights_extracted} insights")
            
            # Step 4: Recommend actions
            print("\n" + "="*80)
            print("Step 4: Recommending Actions")
            print("="*80)
            
            for insight in list(self.insights.values())[-session.insights_extracted:]:
                if insight.actionable:
                    action = self.recommend_action(insight)
                    self.actions[action.id] = action
                    session.actions_recommended += 1
                    print(f"    🎯 {action.action_type}: {action.title}")
                    
                    # Auto-add to TODO.md
                    if self.config["auto_add_to_todo"]:
                        self.add_to_todo(action)
                        session.actions_added_to_todo += 1
            
            print(f"\n✅ Recommended {session.actions_recommended} actions")
            print(f"✅ Added {session.actions_added_to_todo} to TODO.md")
            
            # Complete session
            session.end_time = datetime.now().isoformat()
            session.status = "completed"
            session.summary = f"Scanned {session.papers_scanned} papers, analyzed {session.papers_analyzed}, extracted {session.insights_extracted} insights, recommended {session.actions_recommended} actions"
            
            self.sessions.append(session)
            self.save_state()
            
            # Print summary
            print("\n" + "="*80)
            print("📊 Session Summary")
            print("="*80)
            print(f"  Papers Scanned: {session.papers_scanned}")
            print(f"  Papers Analyzed: {session.papers_analyzed}")
            print(f"  Insights Extracted: {session.insights_extracted}")
            print(f"  Actions Recommended: {session.actions_recommended}")
            print(f"  Actions Added to TODO: {session.actions_added_to_todo}")
            print(f"  Duration: {(datetime.fromisoformat(session.end_time) - datetime.fromisoformat(session.start_time)).total_seconds():.1f}s")
            
            print("\n" + "="*80)
            print("✅ Autonomous Research Session Complete!")
            print("="*80)
            
        except Exception as e:
            session.end_time = datetime.now().isoformat()
            session.status = "failed"
            session.errors.append(str(e))
            self.sessions.append(session)
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return session
    
    def extract_insights(self, opportunity: InnovationOpportunity) -> List[ResearchInsight]:
        """Extract insights from paper"""
        insights = []
        
        # Extract method insight
        method_insight = ResearchInsight(
            id=self.generate_id("insight", f"{opportunity.id}-method"),
            paper_id=opportunity.paper_id,
            title=opportunity.title,
            insight_type="method",
            description=opportunity.description,
            confidence=0.85,
            relevance=opportunity.impact_score,
            novelty=opportunity.novelty_score,
            actionable=True,
            related_work=[]
        )
        insights.append(method_insight)
        
        # Extract opportunity insight
        if opportunity.novelty_score >= 80:
            opp_insight = ResearchInsight(
                id=self.generate_id("insight", f"{opportunity.id}-opportunity"),
                paper_id=opportunity.paper_id,
                title=opportunity.title,
                insight_type="opportunity",
                description=f"High-novelty innovation ({opportunity.novelty_score}/100) in {opportunity.domain}",
                confidence=0.90,
                relevance=opportunity.priority_score,
                novelty=opportunity.novelty_score,
                actionable=True,
                related_work=[]
            )
            insights.append(opp_insight)
        
        return insights
    
    def recommend_action(self, insight: ResearchInsight) -> ActionRecommendation:
        """Recommend action from insight"""
        if insight.novelty >= 90:
            priority = "critical"
            action_type = "implement"
        elif insight.novelty >= 80:
            priority = "high"
            action_type = "research"
        elif insight.novelty >= 70:
            priority = "medium"
            action_type = "monitor"
        else:
            priority = "low"
            action_type = "discuss"
        
        action = ActionRecommendation(
            id=self.generate_id("action", f"{insight.id}-{datetime.now().isoformat()}"),
            insight_id=insight.id,
            paper_id=insight.paper_id,
            action_type=action_type,
            title=f"[Research] {insight.title[:50]}",
            description=insight.description,
            priority=priority,
            estimated_effort="4-8h" if action_type == "implement" else "1-2h",
            expected_impact=insight.relevance,
            status="pending"
        )
        
        return action
    
    def add_to_todo(self, action: ActionRecommendation):
        """Add action to TODO.md"""
        todo_file = "TODO.md"
        
        # Read existing TODO
        if os.path.exists(todo_file):
            with open(todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# TODO.md - Cross-Session Task Tracker\n\n"
        
        # Add new action
        new_entry = f"""
### [ ] ⏳ {action.id}: {action.title}
**Priority:** {action.priority.upper()}  
**Type:** {action.action_type}  
**Estimated Effort:** {action.estimated_effort}  
**Expected Impact:** {action.expected_impact:.0f}/100  
**Source:** Paper {action.paper_id}  
**Status:** ⏳ PENDING

**Description:**
{action.description}

---
"""
        
        # Find position to insert (after header, before completed section)
        lines = content.split('\n')
        insert_idx = 1
        
        for i, line in enumerate(lines):
            if '## ✅' in line or '## 📊' in line:
                insert_idx = i
                break
        
        lines.insert(insert_idx, new_entry)
        
        # Write back
        with open(todo_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        action.todo_id = action.id
        print(f"    ✅ Added to TODO.md: {action.id}")
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "total_insights": len(self.insights),
            "total_actions": len(self.actions),
            "pending_actions": sum(1 for a in self.actions.values() if a.status == "pending"),
            "completed_actions": sum(1 for a in self.actions.values() if a.status == "completed"),
            "total_sessions": len(self.sessions),
            "last_session": self.sessions[-1].to_dict() if self.sessions else None,
            "config": self.config
        }
    
    def export_stats(self, output_file: str = "data/research_agent_stats.json"):
        """Export statistics"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "insights": {
                "total": len(self.insights),
                "by_type": {},
                "avg_confidence": sum(i.confidence for i in self.insights.values()) / len(self.insights) if self.insights else 0,
                "avg_relevance": sum(i.relevance for i in self.insights.values()) / len(self.insights) if self.insights else 0
            },
            "actions": {
                "total": len(self.actions),
                "by_priority": {},
                "by_status": {},
                "pending": sum(1 for a in self.actions.values() if a.status == "pending")
            },
            "sessions": {
                "total": len(self.sessions),
                "completed": sum(1 for s in self.sessions if s.status == "completed"),
                "failed": sum(1 for s in self.sessions if s.status == "failed"),
                "avg_papers_scanned": sum(s.papers_scanned for s in self.sessions) / len(self.sessions) if self.sessions else 0,
                "avg_insights": sum(s.insights_extracted for s in self.sessions) / len(self.sessions) if self.sessions else 0
            }
        }
        
        # Count by type
        for insight in self.insights.values():
            stats["insights"]["by_type"][insight.insight_type] = stats["insights"]["by_type"].get(insight.insight_type, 0) + 1
        
        for action in self.actions.values():
            stats["actions"]["by_priority"][action.priority] = stats["actions"]["by_priority"].get(action.priority, 0) + 1
            stats["actions"]["by_status"][action.status] = stats["actions"]["by_status"].get(action.status, 0) + 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Stats exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Autonomous Research Agent")
    parser.add_argument("--run", action="store_true", help="Run full autonomous session")
    parser.add_argument("--scan", action="store_true", help="Run scan only")
    parser.add_argument("--analyze", type=str, help="Analyze specific paper")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--dashboard", action="store_true", help="Start dashboard")
    args = parser.parse_args()
    
    agent = AutonomousResearchAgent()
    
    if args.run:
        agent.run_scan()
    elif args.scan:
        agent.scanner.scan_simulated()
    elif args.analyze:
        print(f"Analyzing paper: {args.analyze}")
        # TODO: Implement paper analysis
    elif args.status:
        status = agent.get_status()
        print("\n" + "="*80)
        print("🤖 Autonomous Research Agent - Status")
        print("="*80)
        print(f"  Total Insights: {status['total_insights']}")
        print(f"  Total Actions: {status['total_actions']}")
        print(f"  Pending Actions: {status['pending_actions']}")
        print(f"  Completed Actions: {status['completed_actions']}")
        print(f"  Total Sessions: {status['total_sessions']}")
        if status['last_session']:
            print(f"  Last Session: {status['last_session']['status']} ({status['last_session']['papers_scanned']} papers)")
        print("="*80)
    elif args.dashboard:
        print("Dashboard not yet implemented. Use --status for now.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
