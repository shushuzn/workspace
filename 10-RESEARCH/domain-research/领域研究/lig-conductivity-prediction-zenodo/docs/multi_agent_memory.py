#!/usr/bin/env python3
"""
Multi-Agent Memory System
Collaborative memory management across 7 persona agents

Based on arXiv: 2603.12631 "Multi-Agent Memory for Collaborative AI Systems"

Features:
- Agent-specific memory partitions
- Cross-agent memory sharing protocol
- Conflict resolution mechanism
- Memory consensus building
- Collaborative decision tracking

Usage:
  python multi_agent_memory.py --demo
  python multi_agent_memory.py --simulate
  python multi_agent_memory.py --analyze
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import argparse
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import hashlib


class AgentRole(Enum):
    """7 Persona agent roles"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    LEARNER = "learner"
    COORDINATOR = "coordinator"
    INNOVATOR = "innovator"
    META_COGNITION = "meta_cognition"


class MemoryType(Enum):
    """Memory types"""
    TASK = "task"
    DECISION = "decision"
    LESSON = "lesson"
    FACT = "fact"
    INSIGHT = "insight"


class ConsensusStatus(Enum):
    """Memory consensus status"""
    PENDING = "pending"
    AGREED = "agreed"
    CONFLICT = "conflict"
    RESOLVED = "resolved"


@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    content: str
    agent_id: AgentRole
    memory_type: MemoryType
    timestamp: str
    confidence: float  # 0-1
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    consensus_status: ConsensusStatus = ConsensusStatus.PENDING
    agent_votes: Dict[str, float] = field(default_factory=dict)  # agent_id -> vote (0-1)

    def to_dict(self):
        return {
            **asdict(self),
            'agent_id': self.agent_id.value,
            'memory_type': self.memory_type.value,
            'consensus_status': self.consensus_status.value
        }


@dataclass
class AgentMemory:
    """Agent-specific memory partition"""
    agent_id: AgentRole
    memories: List[MemoryEntry] = field(default_factory=list)
    shared_memories: Set[str] = field(default_factory=set)  # Memory IDs
    trust_scores: Dict[str, float] = field(default_factory=dict)  # agent_id -> trust (0-1)

    def add_memory(self, entry: MemoryEntry):
        self.memories.append(entry)

    def get_memories_by_type(self, memory_type: MemoryType) -> List[MemoryEntry]:
        return [m for m in self.memories if m.memory_type == memory_type]


@dataclass
class ConsensusResult:
    """Memory consensus result"""
    memory_id: str
    status: ConsensusStatus
    agreement_score: float  # 0-1
    participating_agents: List[str]
    conflicting_agents: List[str]
    resolution: Optional[str] = None


class MultiAgentMemory:
    """Multi-agent memory management system"""

    def __init__(self):
        self.agents: Dict[AgentRole, AgentMemory] = {}
        self.shared_memory: Dict[str, MemoryEntry] = {}
        self.consensus_history: List[ConsensusResult] = []

        # Initialize 7 persona agents
        for role in AgentRole:
            self.agents[role] = AgentMemory(agent_id=role)
            # Initialize trust scores (all agents start with equal trust)
            for other_role in AgentRole:
                if other_role != role:
                    self.agents[role].trust_scores[other_role.value] = 0.8

    def add_memory(self, agent_id: AgentRole, content: str,
                   memory_type: MemoryType, confidence: float = 0.8,
                   tags: List[str] = None) -> MemoryEntry:
        """Add memory from specific agent"""

        # Generate unique ID
        memory_id = hashlib.md5(
            f"{agent_id.value}:{content}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        entry = MemoryEntry(
            id=memory_id,
            content=content,
            agent_id=agent_id,
            memory_type=memory_type,
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
            tags=tags or [],
            consensus_status=ConsensusStatus.PENDING
        )

        # Add to agent's memory
        self.agents[agent_id].add_memory(entry)

        # Request consensus from other agents
        self._request_consensus(entry)

        return entry

    def _request_consensus(self, memory: MemoryEntry):
        """Request consensus from other agents"""
        # Simulate agent votes based on memory type and confidence
        for agent_id, agent_memory in self.agents.items():
            if agent_id == memory.agent_id:
                continue  # Skip self

            # Simulate vote (in real system, agents would evaluate)
            vote = self._simulate_agent_vote(agent_id, memory)
            memory.agent_votes[agent_id.value] = vote

        # Calculate consensus
        self._calculate_consensus(memory)

    def _simulate_agent_vote(self, agent_id: AgentRole, memory: MemoryEntry) -> float:
        """Simulate agent vote based on role compatibility"""
        # Role-based voting patterns
        role_weights = {
            (AgentRole.CRITIC, MemoryType.LESSON): 1.0,
            (AgentRole.CRITIC, MemoryType.DECISION): 0.9,
            (AgentRole.LEARNER, MemoryType.LESSON): 1.0,
            (AgentRole.LEARNER, MemoryType.INSIGHT): 0.95,
            (AgentRole.INNOVATOR, MemoryType.INSIGHT): 1.0,
            (AgentRole.PLANNER, MemoryType.TASK): 1.0,
            (AgentRole.EXECUTOR, MemoryType.TASK): 0.9,
            (AgentRole.META_COGNITION, MemoryType.DECISION): 0.95,
        }

        base_vote = memory.confidence
        role_bonus = role_weights.get((agent_id, memory.memory_type), 0.8)

        # Trust score modifier
        trust = self.agents[memory.agent_id].trust_scores.get(agent_id.value, 0.8)

        vote = base_vote * 0.6 + role_bonus * 0.3 + trust * 0.1
        return min(1.0, max(0.0, vote))

    def _calculate_consensus(self, memory: MemoryEntry):
        """Calculate consensus status"""
        if not memory.agent_votes:
            memory.consensus_status = ConsensusStatus.PENDING
            return

        votes = list(memory.agent_votes.values())
        avg_vote = sum(votes) / len(votes)
        vote_variance = sum((v - avg_vote) ** 2 for v in votes) / len(votes)

        # Consensus thresholds
        if avg_vote >= 0.8 and vote_variance < 0.05:
            memory.consensus_status = ConsensusStatus.AGREED
        elif vote_variance > 0.2:
            memory.consensus_status = ConsensusStatus.CONFLICT
        elif avg_vote >= 0.6:
            memory.consensus_status = ConsensusStatus.RESOLVED
        else:
            memory.consensus_status = ConsensusStatus.PENDING

        # Record consensus result
        result = ConsensusResult(
            memory_id=memory.id,
            status=memory.consensus_status,
            agreement_score=avg_vote,
            participating_agents=list(memory.agent_votes.keys()),
            conflicting_agents=[
                aid for aid, vote in memory.agent_votes.items() if vote < 0.5
            ],
            resolution="Auto-resolved" if memory.consensus_status == ConsensusStatus.RESOLVED else None
        )

        self.consensus_history.append(result)

        # If agreed, add to shared memory
        if memory.consensus_status == ConsensusStatus.AGREED:
            self.shared_memory[memory.id] = memory
            for agent_memory in self.agents.values():
                agent_memory.shared_memories.add(memory.id)

    def resolve_conflict(self, memory_id: str, resolution: str) -> bool:
        """Manually resolve memory conflict"""
        # Find memory
        memory = None
        for agent_memory in self.agents.values():
            for m in agent_memory.memories:
                if m.id == memory_id:
                    memory = m
                    break

        if not memory:
            return False

        # Update consensus
        memory.consensus_status = ConsensusStatus.RESOLVED

        # Record resolution
        result = ConsensusResult(
            memory_id=memory_id,
            status=ConsensusStatus.RESOLVED,
            agreement_score=0.7,  # Compromise score
            participating_agents=list(memory.agent_votes.keys()),
            conflicting_agents=[],
            resolution=resolution
        )

        self.consensus_history.append(result)
        return True

    def query_memories(self, agent_id: Optional[AgentRole] = None,
                       memory_type: Optional[MemoryType] = None,
                       min_confidence: float = 0.5,
                       consensus_status: Optional[ConsensusStatus] = None) -> List[MemoryEntry]:
        """Query memories with filters"""
        results = []

        # Collect memories from specified agent or all agents
        if agent_id:
            agents_to_search = [self.agents[agent_id]]
        else:
            agents_to_search = list(self.agents.values())

        for agent_memory in agents_to_search:
            for memory in agent_memory.memories:
                # Apply filters
                if memory.confidence < min_confidence:
                    continue
                if memory_type and memory.memory_type != memory_type:
                    continue
                if consensus_status and memory.consensus_status != consensus_status:
                    continue

                results.append(memory)

        return results

    def get_shared_memories(self) -> List[MemoryEntry]:
        """Get all agreed memories"""
        return list(self.shared_memory.values())

    def get_consensus_stats(self) -> Dict:
        """Get consensus statistics"""
        total = len(self.consensus_history)
        if total == 0:
            return {
                "total_memories": 0,
                "agreed": 0,
                "conflicts": 0,
                "pending": 0,
                "resolved": 0,
                "agreement_rate": 0.0
            }

        agreed = sum(1 for r in self.consensus_history if r.status == ConsensusStatus.AGREED)
        conflicts = sum(1 for r in self.consensus_history if r.status == ConsensusStatus.CONFLICT)
        resolved = sum(1 for r in self.consensus_history if r.status == ConsensusStatus.RESOLVED)
        pending = total - agreed - conflicts - resolved

        return {
            "total_memories": total,
            "agreed": agreed,
            "conflicts": conflicts,
            "pending": pending,
            "resolved": resolved,
            "agreement_rate": agreed / total if total > 0 else 0.0,
            "avg_agreement_score": sum(r.agreement_score for r in self.consensus_history) / total
        }

    def export_to_json(self) -> str:
        """Export system state to JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                role.value: {
                    "memory_count": len(agent.memories),
                    "shared_count": len(agent.shared_memories),
                    "memories": [m.to_dict() for m in agent.memories]
                }
                for role, agent in self.agents.items()
            },
            "shared_memory_count": len(self.shared_memory),
            "consensus_stats": self.get_consensus_stats(),
            "consensus_history": [
                {
                    "memory_id": r.memory_id,
                    "status": r.status.value,
                    "agreement_score": r.agreement_score,
                    "resolution": r.resolution
                }
                for r in self.consensus_history
            ]
        }

        return json.dumps(data, indent=2, ensure_ascii=False)


def simulate_collaborative_task():
    """Simulate multi-agent collaborative task"""
    print("="*80)
    print("🧠 Multi-Agent Memory System - Collaborative Task Simulation")
    print("="*80)

    mam = MultiAgentMemory()

    # Simulate task execution workflow
    print("\n📋 Simulating 7-Persona workflow...\n")

    # 1. Planner creates task
    print("1️⃣  Planner: Creating task...")
    task_memory = mam.add_memory(
        AgentRole.PLANNER,
        "Task: Analyze CNT conductivity data with PSM method",
        MemoryType.TASK,
        confidence=0.95,
        tags=["cnt", "psm", "analysis"]
    )
    print(f"   ✅ Task created: {task_memory.id}")

    # 2. Executor reports progress
    print("2️⃣  Executor: Reporting progress...")
    exec_memory = mam.add_memory(
        AgentRole.EXECUTOR,
        "Completed data preprocessing, 194 samples ready",
        MemoryType.FACT,
        confidence=0.90,
        tags=["data", "preprocessing"]
    )
    print(f"   ✅ Progress reported: {exec_memory.id}")

    # 3. Critic reviews
    print("3️⃣  Critic: Reviewing quality...")
    critic_memory = mam.add_memory(
        AgentRole.CRITIC,
        "Quality score: 92/100, VIF < 5 verified",
        MemoryType.DECISION,
        confidence=0.88,
        tags=["quality", "review"]
    )
    print(f"   ✅ Review completed: {critic_memory.id}")

    # 4. Innovator suggests improvement
    print("4️⃣  Innovator: Suggesting optimization...")
    innovator_memory = mam.add_memory(
        AgentRole.INNOVATOR,
        "Insight: Use PSM + SCM combination for robustness",
        MemoryType.INSIGHT,
        confidence=0.85,
        tags=["innovation", "methodology"]
    )
    print(f"   ✅ Insight shared: {innovator_memory.id}")

    # 5. Learner extracts lesson
    print("5️⃣  Learner: Extracting lesson...")
    learner_memory = mam.add_memory(
        AgentRole.LEARNER,
        "Lesson: Quality > Quantity, 194 high-quality samples preferred",
        MemoryType.LESSON,
        confidence=0.92,
        tags=["lesson", "quality"]
    )
    print(f"   ✅ Lesson learned: {learner_memory.id}")

    # 6. Coordinator balances workflow
    print("6️⃣  Coordinator: Balancing workflow...")
    coord_memory = mam.add_memory(
        AgentRole.COORDINATOR,
        "Decision: Proceed to next phase, all checks passed",
        MemoryType.DECISION,
        confidence=0.90,
        tags=["coordination", "decision"]
    )
    print(f"   ✅ Workflow balanced: {coord_memory.id}")

    # 7. Meta-cognition monitors
    print("7️⃣  Meta-Cognition: System monitoring...")
    meta_memory = mam.add_memory(
        AgentRole.META_COGNITION,
        "System health: 96/100, all agents functioning normally",
        MemoryType.FACT,
        confidence=0.95,
        tags=["monitoring", "health"]
    )
    print(f"   ✅ System monitored: {meta_memory.id}")

    # Print consensus statistics
    print("\n" + "="*80)
    print("📊 Consensus Statistics:")
    print("="*80)

    stats = mam.get_consensus_stats()
    print(f"  Total Memories: {stats['total_memories']}")
    print(f"  ✅ Agreed: {stats['agreed']} ({stats['agreement_rate']:.0%})")
    print(f"  ⚠️  Conflicts: {stats['conflicts']}")
    print(f"  ⏳ Pending: {stats['pending']}")
    print(f"  ✅ Resolved: {stats['resolved']}")
    print(f"  Average Agreement Score: {stats['avg_agreement_score']:.2f}")

    # Print shared memories
    print("\n" + "="*80)
    print("📚 Shared Memories (Agreed):")
    print("="*80)

    shared = mam.get_shared_memories()
    for memory in shared:
        print(f"\n  📝 [{memory.memory_type.value.upper()}] {memory.content[:60]}...")
        print(f"     Agent: {memory.agent_id.value} | Confidence: {memory.confidence:.0%}")
        print(f"     Consensus: {memory.consensus_status.value} ({len(memory.agent_votes)} votes)")

    # Export to JSON
    print("\n" + "="*80)
    print("💾 Exporting to JSON...")
    print("="*80)

    json_output = mam.export_to_json()
    output_file = "data/multi_agent_memory_demo.json"

    import os
    os.makedirs("data", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json_output)

    print(f"✅ Exported to: {output_file}")

    return mam


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Memory System")
    parser.add_argument("--demo", action="store_true", help="Run demo simulation")
    parser.add_argument("--analyze", action="store_true", help="Analyze memory patterns")
    parser.add_argument("--output", type=str, help="Output JSON file")
    args = parser.parse_args()

    if args.demo or True:  # Default to demo
        mam = simulate_collaborative_task()

        # Save if output specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(mam.export_to_json())
            print(f"\n✅ Saved to: {args.output}")

    print("\n" + "="*80)
    print("✅ Multi-Agent Memory System demo complete!")
    print("="*80)
    print("\n📚 Based on arXiv: 2603.12631")
    print("🎯 Key Innovation: Collaborative memory with consensus building")
    print("💡 Next: Implement real agent voting mechanism")


if __name__ == "__main__":
    main()
