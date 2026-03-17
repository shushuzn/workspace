#!/usr/bin/env python3
"""
Memory Dark Matter Detector - Infer Hidden Knowledge
=====================================================
Detects and makes explicit the "dark matter" of memory - knowledge that exists
implicitly but has not been recorded.

Key Concepts:
- Gravitational Lensing: Infer hidden structure from visible memory distribution
- Missing Patterns: Identify "should exist but not recorded" knowledge
- Counterfactual Reasoning: "If X was recorded, what would it say?"
- Cross-Domain Mapping: Infer missing knowledge from other domains

Usage:
    python memory_dark_matter.py --scan "MEMORY.md"
    python memory_dark_matter.py --infer "topic"
    python memory_dark_matter.py --counterfactual "event"
    python memory_dark_matter.py --map source_domain target_domain
    python memory_dark_matter.py --status
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter, defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class DarkMatterConfig:
    """Dark matter detection configuration"""
    
    # Detection thresholds
    GRAVITATIONAL_LENS_THRESHOLD: float = 0.6   # Min evidence for lensing
    MISSING_PATTERN_THRESHOLD: float = 0.7      # Min confidence for missing pattern
    COUNTERFACTUAL_CONFIDENCE: float = 0.5      # Min confidence for counterfactual
    
    # Pattern recognition
    MIN_TOPIC_CLUSTER_SIZE: int = 3             # Min memories to form cluster
    GAP_DETECTION_WINDOW: int = 7               # Days to detect temporal gaps
    EXPECTED_CO_OCCURRENCE: float = 0.3         # Expected co-occurrence rate
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    DARK_MATTER_STATE: str = os.path.join(WORKSPACE, 'data', 'dark_matter_state.json')
    DARK_MATTER_REPORT: str = os.path.join(WORKSPACE, 'data', 'dark_matter_report.json')


# ============================================================================
# Dark Matter Types
# ============================================================================

@dataclass
class DarkMatterCandidate:
    """Candidate for undiscovered knowledge"""
    candidate_id: str
    dm_type: str  # gravitational_lens/missing_pattern/counterfactual/cross_domain
    topic: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    inferred_content: str = ""
    priority: str = "medium"  # low/medium/high/critical
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'candidate_id': self.candidate_id,
            'dm_type': self.dm_type,
            'topic': self.topic,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'inferred_content': self.inferred_content,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DarkMatterCandidate':
        return cls(
            candidate_id=data['candidate_id'],
            dm_type=data['dm_type'],
            topic=data['topic'],
            confidence=data['confidence'],
            evidence=data.get('evidence', []),
            inferred_content=data.get('inferred_content', ''),
            priority=data['priority'],
            created_at=datetime.fromisoformat(data['created_at'])
        )


# ============================================================================
# Dark Matter Detector
# ============================================================================

class DarkMatterDetector:
    """Detect hidden knowledge in memory"""
    
    def __init__(self, config: DarkMatterConfig = None):
        self.config = config or DarkMatterConfig()
        self.candidates: List[DarkMatterCandidate] = []
        self._load_state()
    
    def _load_state(self):
        """Load detection state"""
        if os.path.exists(self.config.DARK_MATTER_STATE):
            with open(self.config.DARK_MATTER_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.candidates = [
                DarkMatterCandidate.from_dict(c) for c in state.get('candidates', [])
            ]
            logger.info(f"Loaded {len(self.candidates)} dark matter candidates")
    
    def _save_state(self):
        """Save detection state"""
        state = {
            'candidates': [c.to_dict() for c in self.candidates],
            'last_scan': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.config.DARK_MATTER_STATE), exist_ok=True)
        
        with open(self.config.DARK_MATTER_STATE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def scan_memory(self, memory_file: str) -> List[DarkMatterCandidate]:
        """
        Scan memory file for dark matter candidates
        
        Detection strategies:
        1. Gravitational lensing - infer from visible distribution
        2. Missing patterns - identify gaps
        3. Temporal gaps - detect time periods with no records
        4. Topic imbalances - identify underrepresented topics
        """
        logger.info(f"Scanning {memory_file} for dark matter...")
        
        candidates = []
        
        # Read memory content
        if not os.path.exists(memory_file):
            logger.error(f"Memory file not found: {memory_file}")
            return candidates
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Strategy 1: Gravitational Lensing
        lens_candidates = self._detect_gravitational_lensing(content, memory_file)
        candidates.extend(lens_candidates)
        logger.info(f"Gravitational lensing: {len(lens_candidates)} candidates")
        
        # Strategy 2: Missing Patterns
        pattern_candidates = self._detect_missing_patterns(content, memory_file)
        candidates.extend(pattern_candidates)
        logger.info(f"Missing patterns: {len(pattern_candidates)} candidates")
        
        # Strategy 3: Temporal Gaps
        temporal_candidates = self._detect_temporal_gaps(memory_file)
        candidates.extend(temporal_candidates)
        logger.info(f"Temporal gaps: {len(temporal_candidates)} candidates")
        
        # Store candidates
        self.candidates.extend(candidates)
        self._save_state()
        
        return candidates
    
    def _detect_gravitational_lensing(self, content: str, source_file: str) -> List[DarkMatterCandidate]:
        """
        Detect hidden knowledge through gravitational lensing effect
        
        Analogy: Just as dark matter bends light, hidden knowledge bends
        the distribution of visible knowledge
        """
        candidates = []
        
        # Extract topic distribution
        topics = self._extract_topics(content)
        
        # Find topic clusters with unusual distributions
        topic_clusters = self._cluster_topics(topics)
        
        for cluster_id, cluster_topics in topic_clusters.items():
            if len(cluster_topics) >= self.config.MIN_TOPIC_CLUSTER_SIZE:
                # Check for "lensing" - topics that should exist based on cluster structure
                expected_topics = self._infer_expected_topics(cluster_topics)
                
                for expected_topic in expected_topics:
                    if expected_topic not in topics:
                        # Dark matter detected!
                        candidate = DarkMatterCandidate(
                            candidate_id=f"DM_LENS_{len(candidates)+1:03d}",
                            dm_type="gravitational_lens",
                            topic=expected_topic,
                            confidence=self.config.GRAVITATIONAL_LENS_THRESHOLD,
                            evidence=[
                                f"Cluster {cluster_id} has related topics: {', '.join(cluster_topics[:5])}",
                                f"Expected topic based on semantic proximity"
                            ],
                            inferred_content=f"Hidden knowledge about '{expected_topic}' inferred from cluster structure",
                            priority="high" if len(cluster_topics) > 5 else "medium"
                        )
                        candidates.append(candidate)
        
        return candidates
    
    def _detect_missing_patterns(self, content: str, source_file: str) -> List[DarkMatterCandidate]:
        """
        Detect missing patterns - knowledge that should exist based on patterns
        """
        candidates = []
        
        # Pattern 1: Cause without effect (or vice versa)
        cause_effect_patterns = [
            ("led to", "result"),
            ("because", "cause"),
            ("therefore", "consequence"),
            ("as a result", "outcome"),
        ]
        
        for trigger, pattern_type in cause_effect_patterns:
            if trigger in content.lower():
                # Check if corresponding pattern exists
                # This is simplified - real implementation would use NLP
                pass
        
        # Pattern 2: Incomplete sequences
        sequence_markers = ["first", "second", "third", "finally"]
        found_markers = [m for m in sequence_markers if m in content.lower()]
        
        if len(found_markers) > 0 and len(found_markers) < 4:
            missing_count = 4 - len(found_markers)
            candidate = DarkMatterCandidate(
                candidate_id=f"DM_SEQ_{len(candidates)+1:03d}",
                dm_type="missing_pattern",
                topic="incomplete_sequence",
                confidence=self.config.MISSING_PATTERN_THRESHOLD,
                evidence=[
                    f"Found sequence markers: {', '.join(found_markers)}",
                    f"Missing {missing_count} steps in sequence"
                ],
                inferred_content=f"Knowledge about missing steps in sequence: {found_markers}",
                priority="medium"
            )
            candidates.append(candidate)
        
        # Pattern 3: Referenced but undefined concepts
        import re
        ref_pattern = r'\[\[(.*?)\]\]'  # Wiki-style links
        references = re.findall(ref_pattern, content)
        
        # Check if referenced concepts are defined
        for ref in references:
            if f"**{ref}**" not in content and f"### {ref}" not in content:
                candidate = DarkMatterCandidate(
                    candidate_id=f"DM_REF_{len(candidates)+1:03d}",
                    dm_type="missing_pattern",
                    topic=ref,
                    confidence=0.8,
                    evidence=[
                        f"Referenced concept '{ref}' not defined in memory"
                    ],
                    inferred_content=f"Definition and explanation of '{ref}' is missing",
                    priority="high"
                )
                candidates.append(candidate)
        
        return candidates
    
    def _detect_temporal_gaps(self, memory_file: str) -> List[DarkMatterCandidate]:
        """
        Detect temporal gaps - periods with no memory records
        """
        candidates = []
        
        # Find all daily notes
        memory_dir = os.path.join(self.config.WORKSPACE, '13-memory-记忆系统')
        
        if not os.path.exists(memory_dir):
            return candidates
        
        dates = []
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                try:
                    date_str = filename.replace('.md', '')
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date)
                except ValueError:
                    pass
        
        if len(dates) < 2:
            return candidates
        
        # Sort dates
        dates.sort()
        
        # Find gaps
        for i in range(len(dates) - 1):
            gap_days = (dates[i+1] - dates[i]).days
            
            if gap_days > self.config.GAP_DETECTION_WINDOW:
                candidate = DarkMatterCandidate(
                    candidate_id=f"DM_TIME_{len(candidates)+1:03d}",
                    dm_type="temporal_gap",
                    topic=f"gap_{dates[i].strftime('%Y-%m-%d')}_{dates[i+1].strftime('%Y-%m-%d')}",
                    confidence=min(1.0, gap_days / 30.0),
                    evidence=[
                        f"Gap from {dates[i].strftime('%Y-%m-%d')} to {dates[i+1].strftime('%Y-%m-%d')}",
                        f"{gap_days} days with no records"
                    ],
                    inferred_content=f"Knowledge from {dates[i].strftime('%Y-%m-%d')} to {dates[i+1].strftime('%Y-%m-%d')} is missing",
                    priority="high" if gap_days > 14 else "medium"
                )
                candidates.append(candidate)
        
        return candidates
    
    def infer_knowledge(self, topic: str) -> DarkMatterCandidate:
        """
        Infer hidden knowledge about a specific topic
        
        Uses cross-domain mapping and counterfactual reasoning
        """
        logger.info(f"Inferring knowledge about: {topic}")
        
        # Find related knowledge
        related_knowledge = self._find_related_knowledge(topic)
        
        # Infer missing knowledge
        inferred_content = self._generate_inference(topic, related_knowledge)
        
        candidate = DarkMatterCandidate(
            candidate_id=f"DM_INFER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dm_type="inference",
            topic=topic,
            confidence=0.6,  # Initial confidence
            evidence=[f"Inferred from {len(related_knowledge)} related memories"],
            inferred_content=inferred_content,
            priority="medium"
        )
        
        self.candidates.append(candidate)
        self._save_state()
        
        return candidate
    
    def counterfactual_reasoning(self, event: str) -> DarkMatterCandidate:
        """
        Perform counterfactual reasoning: "What if X happened?"
        """
        logger.info(f"Counterfactual reasoning about: {event}")
        
        # Find related events
        related_events = self._find_related_events(event)
        
        # Generate counterfactual
        counterfactual = self._generate_counterfactual(event, related_events)
        
        candidate = DarkMatterCandidate(
            candidate_id=f"DM_CF_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dm_type="counterfactual",
            topic=event,
            confidence=self.config.COUNTERFACTUAL_CONFIDENCE,
            evidence=[f"Based on {len(related_events)} related events"],
            inferred_content=counterfactual,
            priority="low"
        )
        
        self.candidates.append(candidate)
        self._save_state()
        
        return candidate
    
    def cross_domain_map(self, source_domain: str, target_domain: str) -> List[DarkMatterCandidate]:
        """
        Map knowledge from source domain to infer missing knowledge in target domain
        """
        logger.info(f"Mapping {source_domain} → {target_domain}")
        
        candidates = []
        
        # Find knowledge in source domain
        source_knowledge = self._get_domain_knowledge(source_domain)
        
        # Map to target domain
        for concept in source_knowledge:
            mapped_concept = self._map_concept(concept, source_domain, target_domain)
            
            if mapped_concept:
                # Check if mapped concept exists in target
                if not self._concept_exists_in_domain(mapped_concept, target_domain):
                    candidate = DarkMatterCandidate(
                        candidate_id=f"DM_MAP_{len(candidates)+1:03d}",
                        dm_type="cross_domain",
                        topic=mapped_concept,
                        confidence=0.5,
                        evidence=[
                            f"Mapped from {source_domain} concept: {concept}",
                            f"Missing in {target_domain}"
                        ],
                        inferred_content=f"Knowledge about '{mapped_concept}' in {target_domain} domain",
                        priority="medium"
                    )
                    candidates.append(candidate)
        
        self.candidates.extend(candidates)
        self._save_state()
        
        return candidates
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        # Simple keyword extraction
        # Real implementation would use NLP
        import re
        
        # Find headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Find bold terms
        bold_terms = re.findall(r'\*\*(.+?)\*\*', content)
        
        # Find tags
        tags = re.findall(r'#(\w+)', content)
        
        topics = list(set(headers + bold_terms + tags))
        return [t.strip() for t in topics if len(t) > 2]
    
    def _cluster_topics(self, topics: List[str]) -> Dict[str, List[str]]:
        """Cluster related topics"""
        # Simple clustering based on keyword overlap
        clusters = defaultdict(list)
        
        for topic in topics:
            # Use first letter as simple cluster ID
            cluster_id = topic[0].lower() if topic else 'other'
            clusters[cluster_id].append(topic)
        
        return dict(clusters)
    
    def _infer_expected_topics(self, cluster_topics: List[str]) -> List[str]:
        """Infer expected topics from cluster"""
        # This would use semantic analysis in real implementation
        # For now, return placeholder
        return []
    
    def _find_related_knowledge(self, topic: str) -> List[str]:
        """Find knowledge related to topic"""
        # Placeholder - would search memory in real implementation
        return []
    
    def _generate_inference(self, topic: str, related: List[str]) -> str:
        """Generate inference about topic"""
        return f"Inferred knowledge about {topic} based on {len(related)} related memories"
    
    def _find_related_events(self, event: str) -> List[str]:
        """Find events related to given event"""
        return []
    
    def _generate_counterfactual(self, event: str, related: List[str]) -> str:
        """Generate counterfactual scenario"""
        return f"If {event} had happened differently, outcomes might include..."
    
    def _get_domain_knowledge(self, domain: str) -> List[str]:
        """Get knowledge from specific domain"""
        return []
    
    def _map_concept(self, concept: str, source: str, target: str) -> Optional[str]:
        """Map concept from source to target domain"""
        return concept  # Placeholder
    
    def _concept_exists_in_domain(self, concept: str, domain: str) -> bool:
        """Check if concept exists in domain"""
        return False  # Placeholder
    
    def get_candidates(self, min_confidence: float = 0.5) -> List[DarkMatterCandidate]:
        """Get dark matter candidates above confidence threshold"""
        return [c for c in self.candidates if c.confidence >= min_confidence]
    
    def get_status(self) -> Dict:
        """Get detection status"""
        by_type = Counter(c.dm_type for c in self.candidates)
        by_priority = Counter(c.priority for c in self.candidates)
        
        return {
            'total_candidates': len(self.candidates),
            'by_type': dict(by_type),
            'by_priority': dict(by_priority),
            'avg_confidence': sum(c.confidence for c in self.candidates) / max(len(self.candidates), 1),
            'high_priority': len([c for c in self.candidates if c.priority == 'high'])
        }


# ============================================================================
# CLI Interface
# ============================================================================

def scan_command(args):
    """Scan memory for dark matter"""
    detector = DarkMatterDetector()
    candidates = detector.scan_memory(args.file)
    
    print(f"\n🌌 Dark Matter Detection Results")
    print("=" * 60)
    print(f"File: {args.file}")
    print(f"Candidates found: {len(candidates)}")
    
    for candidate in candidates[:10]:
        print(f"\n  {candidate.candidate_id} [{candidate.dm_type}]")
        print(f"  Topic: {candidate.topic}")
        print(f"  Confidence: {candidate.confidence:.2f}")
        print(f"  Priority: {candidate.priority}")
        print(f"  Evidence: {len(candidate.evidence)} items")
    
    if len(candidates) > 10:
        print(f"\n  ... and {len(candidates) - 10} more")
    
    print("=" * 60)


def infer_command(args):
    """Infer knowledge about topic"""
    detector = DarkMatterDetector()
    candidate = detector.infer_knowledge(args.topic)
    
    print(f"\n🔮 Knowledge Inference")
    print("=" * 60)
    print(f"Topic: {args.topic}")
    print(f"Confidence: {candidate.confidence:.2f}")
    print(f"Inferred content: {candidate.inferred_content}")
    print("=" * 60)


def counterfactual_command(args):
    """Counterfactual reasoning"""
    detector = DarkMatterDetector()
    candidate = detector.counterfactual_reasoning(args.event)
    
    print(f"\n🔄 Counterfactual Reasoning")
    print("=" * 60)
    print(f"Event: {args.event}")
    print(f"Scenario: {candidate.inferred_content}")
    print("=" * 60)


def map_command(args):
    """Cross-domain mapping"""
    detector = DarkMatterDetector()
    candidates = detector.cross_domain_map(args.source, args.target)
    
    print(f"\n🗺️ Cross-Domain Mapping: {args.source} → {args.target}")
    print("=" * 60)
    print(f"Mapped concepts: {len(candidates)}")
    
    for candidate in candidates[:5]:
        print(f"  - {candidate.topic} (confidence: {candidate.confidence:.2f})")
    
    print("=" * 60)


def status_command(args):
    """Get detection status"""
    detector = DarkMatterDetector()
    status = detector.get_status()
    
    print(f"\n🌌 Dark Matter Detection Status")
    print("=" * 60)
    print(f"Total candidates: {status['total_candidates']}")
    print(f"By type: {status['by_type']}")
    print(f"By priority: {status['by_priority']}")
    print(f"Average confidence: {status['avg_confidence']:.2f}")
    print(f"High priority: {status['high_priority']}")
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Dark Matter Detector - Infer Hidden Knowledge')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan memory for dark matter')
    scan_parser.add_argument('file', type=str, help='Memory file to scan')
    scan_parser.set_defaults(func=scan_command)
    
    # Infer command
    infer_parser = subparsers.add_parser('infer', help='Infer knowledge about topic')
    infer_parser.add_argument('topic', type=str, help='Topic to infer')
    infer_parser.set_defaults(func=infer_command)
    
    # Counterfactual command
    cf_parser = subparsers.add_parser('counterfactual', help='Counterfactual reasoning')
    cf_parser.add_argument('event', type=str, help='Event to reason about')
    cf_parser.set_defaults(func=counterfactual_command)
    
    # Map command
    map_parser = subparsers.add_parser('map', help='Cross-domain mapping')
    map_parser.add_argument('source', type=str, help='Source domain')
    map_parser.add_argument('target', type=str, help='Target domain')
    map_parser.set_defaults(func=map_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get detection status')
    status_parser.set_defaults(func=status_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
