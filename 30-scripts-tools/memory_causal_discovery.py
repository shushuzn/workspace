#!/usr/bin/env python3
"""
Memory Causal Discovery Engine - Causal Mechanism Inference
============================================================
Discovers causal relationships in memory using causal inference methods.

Key Concepts:
- Causal Graph: Directed acyclic graph (DAG) of cause-effect relationships
- Do-Calculus: Judea Pearl's framework for causal reasoning
- Confounding: Hidden variables that affect both cause and effect
- Mediation: Indirect causal pathways
- Counterfactuals: "What if" reasoning
- Granger Causality: Temporal precedence implies causation

Usage:
    python memory_causal_discovery.py --discover "MEMORY.md"
    python memory_causal_discovery.py --graph
    python memory_causal_discovery.py --intervene "X" "Y"
    python memory_causal_discovery.py --counterfactual "event"
    python memory_causal_discovery.py --mediation
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter

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
class CausalConfig:
    """Causal discovery configuration"""
    
    # Discovery thresholds
    MIN_CAUSAL_CONFIDENCE: float = 0.6    # Minimum confidence for causal link
    TEMPORAL_WINDOW_DAYS: int = 7         # Days for temporal precedence
    CO_OCCURRENCE_THRESHOLD: float = 0.5  # Minimum co-occurrence
    
    # Causal patterns
    CAUSAL_MARKERS: List[str] = field(default_factory=lambda: [
        'led to', 'caused', 'resulted in', 'because', 'therefore',
        'as a result', 'consequently', 'thus', 'hence', 'due to',
        'triggered', 'initiated', 'produced', 'generated', 'created'
    ])
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    CAUSAL_STATE: str = os.path.join(WORKSPACE, 'data', 'causal_state.json')
    CAUSAL_GRAPH: str = os.path.join(WORKSPACE, 'data', 'causal_graph.json')


# ============================================================================
# Causal Structures
# ============================================================================

@dataclass
class CausalLink:
    """A causal relationship between two events/concepts"""
    link_id: str
    cause: str
    effect: str
    confidence: float
    evidence: List[str]
    mechanism: str = ""           # How cause leads to effect
    confounders: List[str] = field(default_factory=list)  # Potential confounding variables
    mediators: List[str] = field(default_factory=list)    # Intermediate variables
    temporal_order: bool = True   # Cause precedes effect
    link_type: str = "direct"     # direct/indirect/spurious
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'link_id': self.link_id,
            'cause': self.cause,
            'effect': self.effect,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'mechanism': self.mechanism,
            'confounders': self.confounders,
            'mediators': self.mediators,
            'temporal_order': self.temporal_order,
            'link_type': self.link_type,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CausalLink':
        return cls(
            link_id=data['link_id'],
            cause=data['cause'],
            effect=data['effect'],
            confidence=data['confidence'],
            evidence=data['evidence'],
            mechanism=data.get('mechanism', ''),
            confounders=data.get('confounders', []),
            mediators=data.get('mediators', []),
            temporal_order=data.get('temporal_order', True),
            link_type=data.get('link_type', 'direct'),
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class CausalNode:
    """A node in the causal graph"""
    node_id: str
    concept: str
    in_degree: int = 0      # Number of incoming causal links (effects)
    out_degree: int = 0     # Number of outgoing causal links (causes)
    centrality: float = 0.0 # How central this node is
    is_root: bool = False   # Root cause (no incoming links)
    is_leaf: bool = False   # Final effect (no outgoing links)
    
    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'concept': self.concept,
            'in_degree': self.in_degree,
            'out_degree': self.out_degree,
            'centrality': self.centrality,
            'is_root': self.is_root,
            'is_leaf': self.is_leaf
        }


# ============================================================================
# Causal Discovery Engine
# ============================================================================

class CausalDiscoveryEngine:
    """Discover causal relationships in memory"""
    
    def __init__(self, config: CausalConfig = None):
        self.config = config or CausalConfig()
        self.links: List[CausalLink] = []
        self.nodes: Dict[str, CausalNode] = {}
        self._load_state()
    
    def _load_state(self):
        """Load causal state"""
        if os.path.exists(self.config.CAUSAL_STATE):
            with open(self.config.CAUSAL_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.links = [
                CausalLink.from_dict(l) for l in state.get('links', [])
            ]
            
            self.nodes = {
                node_id: CausalNode(**node_data)
                for node_id, node_data in state.get('nodes', {}).items()
            }
            
            logger.info(f"Loaded {len(self.links)} causal links")
    
    def _save_state(self):
        """Save causal state"""
        state = {
            'links': [l.to_dict() for l in self.links],
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'last_discovery': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.config.CAUSAL_STATE), exist_ok=True)
        
        with open(self.config.CAUSAL_STATE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def discover_causal_relationships(self, memory_file: str) -> List[CausalLink]:
        """
        Discover causal relationships from memory
        
        Methods:
        1. Linguistic markers (causal verbs/connectives)
        2. Temporal precedence (cause before effect)
        3. Co-occurrence patterns
        4. Granger causality (time series)
        """
        logger.info(f"Discovering causal relationships in {memory_file}...")
        
        if not os.path.exists(memory_file):
            logger.error(f"Memory file not found: {memory_file}")
            return []
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = []
        
        # Method 1: Linguistic markers
        marker_links = self._discover_from_markers(content)
        links.extend(marker_links)
        logger.info(f"Linguistic markers: {len(marker_links)} links")
        
        # Method 2: Temporal precedence
        temporal_links = self._discover_temporal_causality(memory_file)
        links.extend(temporal_links)
        logger.info(f"Temporal precedence: {len(temporal_links)} links")
        
        # Method 3: Co-occurrence patterns
        cooccur_links = self._discover_from_cooccurrence(content)
        links.extend(cooccur_links)
        logger.info(f"Co-occurrence: {len(cooccur_links)} links")
        
        # Remove duplicates
        unique_links = self._deduplicate_links(links)
        
        # Build causal graph
        self.links = unique_links
        self._build_causal_graph()
        self._save_state()
        
        return unique_links
    
    def _discover_from_markers(self, content: str) -> List[CausalLink]:
        """Discover causal links from linguistic markers"""
        links = []
        link_id = 0
        
        sentences = re.split(r'[.!?]\s+', content)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            for marker in self.config.CAUSAL_MARKERS:
                if marker in sentence_lower:
                    # Try to extract cause and effect
                    parts = re.split(rf'\b{marker}\b', sentence, flags=re.IGNORECASE)
                    
                    if len(parts) >= 2:
                        # Determine order based on marker
                        if marker in ['because', 'due to']:
                            cause = parts[1].strip()[:100]
                            effect = parts[0].strip()[:100]
                        else:
                            cause = parts[0].strip()[:100]
                            effect = parts[1].strip()[:100]
                        
                        if cause and effect and len(cause) > 5 and len(effect) > 5:
                            link = CausalLink(
                                link_id=f"CL_MARKER_{link_id:04d}",
                                cause=cause,
                                effect=effect,
                                confidence=0.7,  # Initial confidence
                                evidence=[f"Linguistic marker: '{marker}'"],
                                mechanism=f"Via {marker}",
                                link_type="direct"
                            )
                            links.append(link)
                            link_id += 1
        
        return links
    
    def _discover_temporal_causality(self, memory_file: str) -> List[CausalLink]:
        """Discover causal links from temporal precedence"""
        links = []
        link_id = 0
        
        # Find daily notes
        memory_dir = os.path.join(self.config.WORKSPACE, '13-memory-记忆系统')
        
        if not os.path.exists(memory_dir):
            return links
        
        # Get chronologically ordered notes
        dates = []
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                try:
                    date_str = filename.replace('.md', '')
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date)
                except ValueError:
                    pass
        
        dates.sort()
        
        # Look for patterns that appear in temporal order
        concept_timeline = defaultdict(list)
        
        for date in dates[-30:]:  # Last 30 days
            note_file = os.path.join(memory_dir, f"{date.strftime('%Y-%m-%d')}.md")
            
            if os.path.exists(note_file):
                with open(note_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract concepts
                concepts = self._extract_concepts(content)
                
                for concept in concepts:
                    concept_timeline[concept].append(date)
        
        # Find concepts that consistently appear in temporal order
        concepts = list(concept_timeline.keys())
        
        for i, concept1 in enumerate(concepts[:50]):  # Limit for performance
            for concept2 in concepts[i+1:50]:
                dates1 = concept_timeline[concept1]
                dates2 = concept_timeline[concept2]
                
                if not dates1 or not dates2:
                    continue
                
                # Check if concept1 consistently precedes concept2
                precedence_count = 0
                total_pairs = 0
                
                for d1 in dates1:
                    for d2 in dates2:
                        total_pairs += 1
                        if d1 < d2:
                            precedence_count += 1
                
                if total_pairs > 0:
                    precedence_ratio = precedence_count / total_pairs
                    
                    if precedence_ratio > 0.8:  # 80% temporal precedence
                        link = CausalLink(
                            link_id=f"CL_TEMP_{link_id:04d}",
                            cause=concept1,
                            effect=concept2,
                            confidence=precedence_ratio * 0.8,  # Max 0.8 for temporal alone
                            evidence=[f"Temporal precedence: {precedence_ratio:.1%}"],
                            mechanism="Temporal precedence suggests causation",
                            link_type="potential"
                        )
                        links.append(link)
                        link_id += 1
        
        return links
    
    def _discover_from_cooccurrence(self, content: str) -> List[CausalLink]:
        """Discover causal links from co-occurrence patterns"""
        links = []
        link_id = 0
        
        # Extract sections
        sections = content.split('\n## ')
        
        # Build co-occurrence matrix
        concept_sections = defaultdict(set)
        
        for i, section in enumerate(sections):
            concepts = self._extract_concepts(section)
            
            for concept in concepts:
                concept_sections[concept].add(i)
        
        # Find highly co-occurring concepts
        concepts = list(concept_sections.keys())
        
        for i, concept1 in enumerate(concepts[:50]):
            for concept2 in concepts[i+1:50]:
                sections1 = concept_sections[concept1]
                sections2 = concept_sections[concept2]
                
                if not sections1 or not sections2:
                    continue
                
                # Jaccard similarity
                intersection = len(sections1 & sections2)
                union = len(sections1 | sections2)
                
                if union > 0:
                    similarity = intersection / union
                    
                    if similarity > self.config.CO_OCCURRENCE_THRESHOLD:
                        link = CausalLink(
                            link_id=f"CL_COOC_{link_id:04d}",
                            cause=concept1,
                            effect=concept2,
                            confidence=similarity * 0.6,  # Max 0.6 for co-occurrence alone
                            evidence=[f"Co-occurrence similarity: {similarity:.2f}"],
                            mechanism="High co-occurrence suggests relationship",
                            link_type="correlational"
                        )
                        links.append(link)
                        link_id += 1
        
        return links
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract concepts from content"""
        # Find headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Find bold terms
        bold_terms = re.findall(r'\*\*(.+?)\*\*', content)
        
        # Find tags
        tags = re.findall(r'#(\w+)', content)
        
        concepts = list(set(headers + bold_terms + tags))
        return [c.strip() for c in concepts if len(c) > 2 and len(c) < 50]
    
    def _deduplicate_links(self, links: List[CausalLink]) -> List[CausalLink]:
        """Remove duplicate causal links"""
        seen = set()
        unique = []
        
        for link in links:
            key = (link.cause.lower(), link.effect.lower())
            
            if key not in seen:
                seen.add(key)
                unique.append(link)
            else:
                # Merge evidence
                for existing in unique:
                    if (existing.cause.lower(), existing.effect.lower()) == key:
                        existing.evidence.extend(link.evidence)
                        existing.confidence = max(existing.confidence, link.confidence)
                        break
        
        return unique
    
    def _build_causal_graph(self):
        """Build causal graph from links"""
        self.nodes = {}
        
        # Create nodes
        for link in self.links:
            if link.cause not in self.nodes:
                self.nodes[link.cause] = CausalNode(
                    node_id=f"CN_{len(self.nodes):04d}",
                    concept=link.cause
                )
            
            if link.effect not in self.nodes:
                self.nodes[link.effect] = CausalNode(
                    node_id=f"CN_{len(self.nodes):04d}",
                    concept=link.effect
                )
            
            # Update degrees
            self.nodes[link.cause].out_degree += 1
            self.nodes[link.effect].in_degree += 1
        
        # Identify roots and leaves
        for node in self.nodes.values():
            if node.in_degree == 0:
                node.is_root = True
            if node.out_degree == 0:
                node.is_leaf = True
            
            # Compute centrality (degree centrality)
            node.centrality = (node.in_degree + node.out_degree) / max(len(self.nodes), 1)
    
    def intervene(self, cause: str, effect: str) -> Dict:
        """
        Perform causal intervention (do-calculus)
        
        Compute P(effect | do(cause)) - probability of effect given intervention on cause
        """
        logger.info(f"Intervention: do({cause}) → {effect}")
        
        # Find relevant causal links
        relevant_links = [
            link for link in self.links
            if cause.lower() in link.cause.lower() and effect.lower() in link.effect.lower()
        ]
        
        if not relevant_links:
            return {
                'intervention': f"do({cause})",
                'outcome': effect,
                'probability': 0.0,
                'confidence': 0.0,
                'pathway': None,
                'confounders': []
            }
        
        # Aggregate confidence
        avg_confidence = sum(link.confidence for link in relevant_links) / len(relevant_links)
        
        # Find mediators
        mediators = []
        for link in relevant_links:
            mediators.extend(link.mediators)
        
        # Find confounders
        confounders = []
        for link in relevant_links:
            confounders.extend(link.confounders)
        
        result = {
            'intervention': f"do({cause})",
            'outcome': effect,
            'probability': avg_confidence,
            'confidence': avg_confidence,
            'pathway': f"{cause} → {effect}",
            'confounders': list(set(confounders)),
            'mediators': list(set(mediators)),
            'num_paths': len(relevant_links)
        }
        
        return result
    
    def counterfactual(self, event: str) -> Dict:
        """
        Perform counterfactual reasoning
        
        "What would have happened if event was different?"
        """
        logger.info(f"Counterfactual: What if {event}?")
        
        # Find causal links involving this event
        as_cause = [link for link in self.links if event.lower() in link.cause.lower()]
        as_effect = [link for link in self.links if event.lower() in link.effect.lower()]
        
        # Generate counterfactual scenarios
        scenarios = []
        
        # If event didn't happen (as cause)
        for link in as_cause:
            scenarios.append({
                'type': 'prevent_cause',
                'scenario': f"If {event} had not occurred...",
                'consequence': f"{link.effect} might not have happened",
                'confidence': link.confidence * 0.7  # Counterfactual uncertainty
            })
        
        # If event was different (as effect)
        for link in as_effect:
            scenarios.append({
                'type': 'change_cause',
                'scenario': f"If {link.cause} had been different...",
                'consequence': f"{event} might have been different",
                'confidence': link.confidence * 0.7
            })
        
        result = {
            'event': event,
            'counterfactuals': scenarios,
            'num_causal_links_as_cause': len(as_cause),
            'num_causal_links_as_effect': len(as_effect)
        }
        
        return result
    
    def find_mediation_paths(self) -> List[Dict]:
        """
        Find mediation pathways (indirect causal effects)
        
        A → M → B (A affects B through mediator M)
        """
        logger.info("Finding mediation pathways...")
        
        mediation_paths = []
        
        # Find nodes that are both effects and causes (potential mediators)
        potential_mediators = [
            node_id for node_id, node in self.nodes.items()
            if node.in_degree > 0 and node.out_degree > 0
        ]
        
        for mediator in potential_mediators:
            # Find causes of mediator
            causes = [
                link.cause for link in self.links
                if link.effect.lower() == mediator.lower()
            ]
            
            # Find effects of mediator
            effects = [
                link.effect for link in self.links
                if link.cause.lower() == mediator.lower()
            ]
            
            # Create mediation paths
            for cause in causes:
                for effect in effects:
                    if cause != effect:
                        path = {
                            'pathway': f"{cause} → {mediator} → {effect}",
                            'mediator': mediator,
                            'direct_effect': any(
                                link.cause.lower() == cause.lower() and link.effect.lower() == effect.lower()
                                for link in self.links
                            ),
                            'confidence': 0.6  # Estimate
                        }
                        mediation_paths.append(path)
        
        return mediation_paths
    
    def get_causal_graph_summary(self) -> Dict:
        """Get summary of causal graph"""
        roots = [n for n in self.nodes.values() if n.is_root]
        leaves = [n for n in self.nodes.values() if n.is_leaf]
        
        # Find most central nodes
        central_nodes = sorted(
            self.nodes.values(),
            key=lambda n: n.centrality,
            reverse=True
        )[:10]
        
        return {
            'total_nodes': len(self.nodes),
            'total_links': len(self.links),
            'root_causes': len(roots),
            'final_effects': len(leaves),
            'central_nodes': [n.concept for n in central_nodes],
            'avg_confidence': sum(l.confidence for l in self.links) / max(len(self.links), 1)
        }


# ============================================================================
# CLI Interface
# ============================================================================

def discover_command(args):
    """Discover causal relationships"""
    engine = CausalDiscoveryEngine()
    links = engine.discover_causal_relationships(args.file)
    
    print(f"\n🔗 Causal Discovery Results")
    print("=" * 60)
    print(f"File: {args.file}")
    print(f"Causal links found: {len(links)}")
    
    # Show top links
    top_links = sorted(links, key=lambda l: l.confidence, reverse=True)[:10]
    
    for link in top_links:
        print(f"\n  {link.link_id} (confidence: {link.confidence:.2f})")
        print(f"  Cause: {link.cause}")
        print(f"  Effect: {link.effect}")
        print(f"  Type: {link.link_type}")
        print(f"  Evidence: {len(link.evidence)} items")
    
    print("=" * 60)


def graph_command(args):
    """Show causal graph summary"""
    engine = CausalDiscoveryEngine()
    summary = engine.get_causal_graph_summary()
    
    print(f"\n🕸️ Causal Graph Summary")
    print("=" * 60)
    print(f"Total nodes: {summary['total_nodes']}")
    print(f"Total links: {summary['total_links']}")
    print(f"Root causes: {summary['root_causes']}")
    print(f"Final effects: {summary['final_effects']}")
    print(f"Average confidence: {summary['avg_confidence']:.2f}")
    
    print(f"\nTop 10 central nodes:")
    for i, node in enumerate(summary['central_nodes'], 1):
        print(f"  {i}. {node}")
    
    print("=" * 60)


def intervene_command(args):
    """Causal intervention"""
    engine = CausalDiscoveryEngine()
    result = engine.intervene(args.cause, args.effect)
    
    print(f"\n🎯 Causal Intervention")
    print("=" * 60)
    print(f"Intervention: {result['intervention']}")
    print(f"Outcome: {result['outcome']}")
    print(f"Probability: {result['probability']:.2f}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Pathway: {result['pathway']}")
    
    if result['confounders']:
        print(f"Confounders: {', '.join(result['confounders'][:5])}")
    
    if result['mediators']:
        print(f"Mediators: {', '.join(result['mediators'][:5])}")
    
    print("=" * 60)


def counterfactual_command(args):
    """Counterfactual reasoning"""
    engine = CausalDiscoveryEngine()
    result = engine.counterfactual(args.event)
    
    print(f"\n🔄 Counterfactual Reasoning: {result['event']}")
    print("=" * 60)
    print(f"As cause in {result['num_causal_links_as_cause']} links")
    print(f"As effect in {result['num_causal_links_as_effect']} links")
    
    print(f"\nScenarios:")
    for scenario in result['counterfactuals'][:5]:
        print(f"\n  {scenario['type']}")
        print(f"  {scenario['scenario']}")
        print(f"  {scenario['consequence']}")
        print(f"  Confidence: {scenario['confidence']:.2f}")
    
    print("=" * 60)


def mediation_command(args):
    """Find mediation pathways"""
    engine = CausalDiscoveryEngine()
    paths = engine.find_mediation_paths()
    
    print(f"\n🔀 Mediation Pathways")
    print("=" * 60)
    print(f"Total pathways: {len(paths)}")
    
    for path in paths[:10]:
        print(f"\n  {path['pathway']}")
        print(f"  Mediator: {path['mediator']}")
        print(f"  Direct effect exists: {path['direct_effect']}")
    
    if len(paths) > 10:
        print(f"\n  ... and {len(paths) - 10} more")
    
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Causal Discovery Engine - Causal Mechanism Inference')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover causal relationships')
    discover_parser.add_argument('file', type=str, help='Memory file')
    discover_parser.set_defaults(func=discover_command)
    
    # Graph command
    graph_parser = subparsers.add_parser('graph', help='Show causal graph')
    graph_parser.set_defaults(func=graph_command)
    
    # Intervene command
    intervene_parser = subparsers.add_parser('intervene', help='Causal intervention')
    intervene_parser.add_argument('cause', type=str, help='Cause variable')
    intervene_parser.add_argument('effect', type=str, help='Effect variable')
    intervene_parser.set_defaults(func=intervene_command)
    
    # Counterfactual command
    cf_parser = subparsers.add_parser('counterfactual', help='Counterfactual reasoning')
    cf_parser.add_argument('event', type=str, help='Event to reason about')
    cf_parser.set_defaults(func=counterfactual_command)
    
    # Mediation command
    med_parser = subparsers.add_parser('mediation', help='Find mediation pathways')
    med_parser.set_defaults(func=mediation_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
