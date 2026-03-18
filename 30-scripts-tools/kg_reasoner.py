#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge Graph Reasoning Engine - Automatic Knowledge Inference
Features: Transitive reasoning, symmetry, temporal reasoning, conflict detection

Usage:
    python kg_reasoner.py --infer
    python kg_reasoner.py --conflicts
    python kg_reasoner.py --query "A related_to B"
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class Entity:
    """Knowledge graph entity"""
    id: str
    name: str
    category: str
    properties: Dict


@dataclass
class Relationship:
    """Knowledge graph relationship"""
    source: str
    target: str
    type: str
    strength: float
    evidence: str
    timestamp: str


@dataclass
class InferredRelationship:
    """Newly inferred relationship"""
    source: str
    target: str
    type: str
    strength: float
    inference_rule: str
    confidence: float
    path: List[str]


@dataclass
class Conflict:
    """Knowledge conflict"""
    entity1: str
    entity2: str
    relationship1: str
    relationship2: str
    conflict_type: str
    severity: str
    resolution: str


class KnowledgeGraphReasoner:
    """Knowledge graph reasoning engine"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "knowledge"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.entities_file = self.data_dir / "entities.json"
        self.relationships_file = self.data_dir / "relationships.json"
        self.inferred_file = self.data_dir / "inferred.json"
        self.conflicts_file = self.data_dir / "conflicts.json"
        
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.inferred: List[InferredRelationship] = []
        self.conflicts: List[Conflict] = []
        
        # Adjacency lists for efficient traversal
        self.outgoing: Dict[str, List[Relationship]] = defaultdict(list)
        self.incoming: Dict[str, List[Relationship]] = defaultdict(list)
        
        self.load_graph()
    
    def load_graph(self):
        """Load knowledge graph"""
        if self.entities_file.exists():
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entities = {
                    k: Entity(**v) for k, v in data.get('entities', {}).items()
                }
        
        if self.relationships_file.exists():
            with open(self.relationships_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.relationships = [
                    Relationship(**r) for r in data.get('relationships', [])
                ]
                
                # Build adjacency lists
                for rel in self.relationships:
                    self.outgoing[rel.source].append(rel)
                    self.incoming[rel.target].append(rel)
        
        if self.inferred_file.exists():
            with open(self.inferred_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.inferred = [
                    InferredRelationship(**i) for i in data.get('inferred', [])
                ]
        
        if self.conflicts_file.exists():
            with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conflicts = [
                    Conflict(**c) for c in data.get('conflicts', [])
                ]
    
    def save_graph(self):
        """Save knowledge graph"""
        with open(self.entities_file, 'w', encoding='utf-8') as f:
            json.dump({
                'entities': {k: asdict(v) for k, v in self.entities.items()},
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.relationships_file, 'w', encoding='utf-8') as f:
            json.dump({
                'relationships': [asdict(r) for r in self.relationships],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.inferred_file, 'w', encoding='utf-8') as f:
            json.dump({
                'inferred': [asdict(i) for i in self.inferred],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.conflicts_file, 'w', encoding='utf-8') as f:
            json.dump({
                'conflicts': [asdict(c) for c in self.conflicts],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def add_entity(self, entity_id: str, name: str, category: str, properties: Dict = None):
        """Add entity to graph"""
        self.entities[entity_id] = Entity(
            id=entity_id,
            name=name,
            category=category,
            properties=properties or {}
        )
    
    def add_relationship(self, source: str, target: str, rel_type: str, 
                        strength: float = 1.0, evidence: str = ""):
        """Add relationship to graph"""
        rel = Relationship(
            source=source,
            target=target,
            type=rel_type,
            strength=strength,
            evidence=evidence,
            timestamp=datetime.now().isoformat()
        )
        
        self.relationships.append(rel)
        self.outgoing[source].append(rel)
        self.incoming[target].append(rel)
    
    def infer_transitive(self) -> List[InferredRelationship]:
        """Infer transitive relationships: A→B, B→C ⇒ A→C"""
        print("\n🔮 Inferring Transitive Relationships\n")
        
        new_inferences = []
        
        # For each A→B relationship
        for rel1 in self.relationships:
            if rel1.type not in ['related_to', 'influences', 'evolves_to']:
                continue
            
            # Find B→C relationships
            for rel2 in self.outgoing[rel1.target]:
                if rel2.type != rel1.type:
                    continue
                
                # Skip if A→C already exists
                existing = any(
                    r.source == rel1.source and r.target == rel2.target
                    for r in self.relationships
                )
                
                if not existing:
                    # Infer A→C
                    inferred_strength = rel1.strength * rel2.strength * 0.8  # Decay
                    
                    inference = InferredRelationship(
                        source=rel1.source,
                        target=rel2.target,
                        type=rel1.type,
                        strength=round(inferred_strength, 2),
                        inference_rule='transitive',
                        confidence=round(inferred_strength * 100, 1),
                        path=[rel1.source, rel1.target, rel2.target]
                    )
                    
                    new_inferences.append(inference)
                    self.inferred.append(inference)
                    
                    print(f"  {rel1.source} → {rel2.target} ({rel1.type})")
                    print(f"    Via: {rel1.source} → {rel1.target} → {rel2.target}")
                    print(f"    Confidence: {inference.confidence}%\n")
        
        print(f"✅ Inferred {len(new_inferences)} transitive relationships\n")
        return new_inferences
    
    def infer_symmetry(self) -> List[InferredRelationship]:
        """Infer symmetric relationships: A collaborates B ⇒ B collaborates A"""
        print("\n🔮 Inferring Symmetric Relationships\n")
        
        symmetric_types = ['collaborates_with', 'co_authors', 'connected_to']
        new_inferences = []
        
        for rel in self.relationships:
            if rel.type in symmetric_types:
                # Check if reverse exists
                existing = any(
                    r.source == rel.target and r.target == rel.source
                    for r in self.relationships
                )
                
                if not existing:
                    inference = InferredRelationship(
                        source=rel.target,
                        target=rel.source,
                        type=rel.type,
                        strength=rel.strength,
                        inference_rule='symmetry',
                        confidence=round(rel.strength * 100, 1),
                        path=[rel.target, rel.source]
                    )
                    
                    new_inferences.append(inference)
                    self.inferred.append(inference)
                    
                    print(f"  {rel.target} → {rel.source} ({rel.type})")
                    print(f"    Via symmetry: {rel.source} → {rel.target}\n")
        
        print(f"✅ Inferred {len(new_inferences)} symmetric relationships\n")
        return new_inferences
    
    def infer_temporal(self) -> List[InferredRelationship]:
        """Infer temporal/causal relationships from event sequences"""
        print("\n🔮 Inferring Temporal Relationships\n")
        
        # Group events by entity
        entity_events = defaultdict(list)
        
        for rel in self.relationships:
            if rel.type == 'occurs_at':
                entity_events[rel.source].append(rel)
        
        new_inferences = []
        
        # For each entity with multiple events
        for entity, events in entity_events.items():
            if len(events) < 2:
                continue
            
            # Sort by timestamp
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            
            # Infer sequence relationships
            for i in range(len(sorted_events) - 1):
                inference = InferredRelationship(
                    source=sorted_events[i].target,
                    target=sorted_events[i+1].target,
                    type='precedes',
                    strength=0.7,
                    inference_rule='temporal_sequence',
                    confidence=70.0,
                    path=[sorted_events[i].target, sorted_events[i+1].target]
                )
                
                new_inferences.append(inference)
                self.inferred.append(inference)
                
                print(f"  {sorted_events[i].target} → {sorted_events[i+1].target} (precedes)")
        
        print(f"✅ Inferred {len(new_inferences)} temporal relationships\n")
        return new_inferences
    
    def detect_conflicts(self) -> List[Conflict]:
        """Detect conflicting knowledge"""
        print("\n⚠️  Detecting Knowledge Conflicts\n")
        
        new_conflicts = []
        
        # Check for contradictory relationships
        for rel1 in self.relationships:
            for rel2 in self.relationships:
                if rel1.source == rel2.source and rel1.target == rel2.target:
                    if rel1.type != rel2.type:
                        # Check if types are contradictory
                        contradictory_pairs = [
                            ('causes', 'prevents'),
                            ('increases', 'decreases'),
                            ('supports', 'contradicts')
                        ]
                        
                        for pair in contradictory_pairs:
                            if (rel1.type in pair and rel2.type in pair 
                                and rel1.type != rel2.type):
                                conflict = Conflict(
                                    entity1=rel1.source,
                                    entity2=rel1.target,
                                    relationship1=f"{rel1.type} (strength: {rel1.strength})",
                                    relationship2=f"{rel2.type} (strength: {rel2.strength})",
                                    conflict_type='contradictory_relationships',
                                    severity='high',
                                    resolution='requires_manual_review'
                                )
                                
                                new_conflicts.append(conflict)
                                self.conflicts.append(conflict)
                                
                                print(f"  ❌ Conflict: {rel1.source} → {rel1.target}")
                                print(f"     {rel1.type} vs {rel2.type}\n")
        
        print(f"⚠️  Detected {len(new_conflicts)} conflicts\n")
        return new_conflicts
    
    def query(self, query: str) -> List[Dict]:
        """Query knowledge graph"""
        # Simple query parser
        parts = query.split()
        
        if len(parts) < 3:
            return []
        
        source = parts[0]
        rel_type = parts[1]
        target = parts[2]
        
        results = []
        
        # Search relationships
        for rel in self.relationships + [asdict(i) for i in self.inferred]:
            match = True
            
            if source != '*' and rel.get('source') != source:
                match = False
            if rel_type != '*' and rel.get('type') != rel_type:
                match = False
            if target != '*' and rel.get('target') != target:
                match = False
            
            if match:
                results.append(rel)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        return {
            'entities': len(self.entities),
            'relationships': len(self.relationships),
            'inferred': len(self.inferred),
            'conflicts': len(self.conflicts),
            'avg_relationships_per_entity': round(
                len(self.relationships) / len(self.entities), 2
            ) if self.entities else 0
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Graph Reasoner')
    parser.add_argument('--infer', action='store_true', help='Run all inference')
    parser.add_argument('--conflicts', action='store_true', help='Detect conflicts')
    parser.add_argument('--query', type=str, help='Query graph')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--test', action='store_true', help='Test reasoning')
    args = parser.parse_args()
    
    reasoner = KnowledgeGraphReasoner()
    
    if args.infer:
        reasoner.infer_transitive()
        reasoner.infer_symmetry()
        reasoner.infer_temporal()
        reasoner.save_graph()
    
    elif args.conflicts:
        reasoner.detect_conflicts()
        reasoner.save_graph()
    
    elif args.query:
        results = reasoner.query(args.query)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.stats:
        stats = reasoner.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.test:
        print("\n🧪 Testing Knowledge Graph Reasoning\n")
        
        # Create test graph
        print("Creating test knowledge graph...")
        
        reasoner.add_entity('A', 'Entity A', 'concept')
        reasoner.add_entity('B', 'Entity B', 'concept')
        reasoner.add_entity('C', 'Entity C', 'concept')
        reasoner.add_entity('D', 'Entity D', 'concept')
        
        reasoner.add_relationship('A', 'B', 'related_to', 0.9, 'observation')
        reasoner.add_relationship('B', 'C', 'related_to', 0.8, 'observation')
        reasoner.add_relationship('A', 'D', 'influences', 0.7, 'study')
        
        # Test transitive inference
        print("\n1. Transitive Inference:")
        reasoner.infer_transitive()
        
        # Test symmetry (add symmetric relationship)
        reasoner.add_relationship('X', 'Y', 'collaborates_with', 0.95, 'paper')
        print("\n2. Symmetry Inference:")
        reasoner.infer_symmetry()
        
        # Test conflict detection
        reasoner.add_relationship('P', 'Q', 'causes', 0.8, 'study1')
        reasoner.add_relationship('P', 'Q', 'prevents', 0.6, 'study2')
        print("\n3. Conflict Detection:")
        reasoner.detect_conflicts()
        
        # Show statistics
        print("\n4. Graph Statistics:")
        stats = reasoner.get_statistics()
        print(json.dumps(stats, indent=2))
        
        reasoner.save_graph()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
