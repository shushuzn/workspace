#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Association Builder - Automatically build connections between memories
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import re

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
MEMORY_FILE = MEMORY_DIR / 'MEMORY.md'
ASSOCIATION_DIR = WORKSPACE / 'data' / 'memory_associations'
ASSOCIATION_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Association:
    """Represents an association between two memories"""
    source_id: str
    target_id: str
    association_type: str  # semantic, categorical, temporal, causal
    strength: float  # 0-1
    evidence: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AssociationGraph:
    """Graph of memory associations"""
    nodes: Dict[str, Dict] = field(default_factory=dict)
    edges: List[Association] = field(default_factory=list)
    
    def add_node(self, node_id: str, metadata: Dict):
        self.nodes[node_id] = metadata
    
    def add_edge(self, association: Association):
        self.edges.append(association)
    
    def to_dict(self) -> dict:
        return {
            'nodes': self.nodes,
            'edges': [asdict(e) for e in self.edges],
            'stats': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'avg_edges_per_node': len(self.edges) / max(len(self.nodes), 1)
            }
        }

class MemoryAssociationBuilder:
    """
    Builds associations between memories using multiple strategies:
    1. Semantic similarity (text overlap)
    2. Categorical (same category)
    3. Temporal (close creation time)
    4. Causal (one references another)
    5. Tag-based (shared tags)
    """
    
    def __init__(self):
        self.strategies = {
            'semantic': 0.30,
            'categorical': 0.20,
            'temporal': 0.15,
            'causal': 0.20,
            'tag_based': 0.15,
        }
        
        self.min_strength = 0.3  # Minimum strength to create association
    
    def extract_entities(self, text: str) -> Set[str]:
        """Extract key entities from text"""
        entities = set()
        
        # Extract [XXX-000] patterns
        patterns = re.findall(r'\[([A-Z]+-\d+)\]', text)
        entities.update(patterns)
        
        # Extract code names (camelCase or snake_case)
        code_names = re.findall(r'\b([a-z]+(?:_[a-z]+)+|[a-z]+(?:[A-Z][a-z]+)+)\b', text)
        entities.update(code_names)
        
        # Extract section headers
        headers = re.findall(r'^#{1,3}\s+(.+)$', text, re.MULTILINE)
        entities.update(h.strip() for h in headers)
        
        return entities
    
    def extract_tags(self, text: str) -> Set[str]:
        """Extract tags from text"""
        tags = set()
        
        # Look for tag patterns
        tag_patterns = re.findall(r'#(\w+)', text)
        tags.update(tag_patterns)
        
        # Look for category indicators
        categories = ['security', 'memory', 'persona', 'tool', 'workflow', 
                     'research', 'config', 'deployment']
        for cat in categories:
            if cat in text.lower():
                tags.add(cat)
        
        return tags
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> Tuple[float, List[str]]:
        """
        Calculate semantic similarity between two texts
        Returns (score, evidence)
        """
        evidence = []
        
        # Entity overlap (40%)
        entities1 = self.extract_entities(text1)
        entities2 = self.extract_entities(text2)
        
        if entities1 and entities2:
            entity_overlap = entities1 & entities2
            entity_score = len(entity_overlap) / max(len(entities1 | entities2), 1)
            if entity_overlap:
                evidence.append(f"Shared entities: {', '.join(list(entity_overlap)[:5])}")
        else:
            entity_score = 0
        
        # Word overlap (40%)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Filter common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else',
                     'when', 'at', 'from', 'by', 'on', 'off', 'for', 'in', 'out',
                     'over', 'to', 'into', 'with', 'of', 'as', '是', '的', '了', '在'}
        
        words1 -= stop_words
        words2 -= stop_words
        
        if words1 and words2:
            word_overlap = words1 & words2
            word_score = len(word_overlap) / max(len(words1 | words2), 1)
            if word_overlap:
                evidence.append(f"Shared keywords: {len(word_overlap)} words")
        else:
            word_score = 0
        
        # Tag overlap (20%)
        tags1 = self.extract_tags(text1)
        tags2 = self.extract_tags(text2)
        
        if tags1 and tags2:
            tag_overlap = tags1 & tags2
            tag_score = len(tag_overlap) / max(len(tags1 | tags2), 1)
            if tag_overlap:
                evidence.append(f"Shared tags: {', '.join(tag_overlap)}")
        else:
            tag_score = 0
        
        # Weighted score
        total_score = (entity_score * 0.4 + word_score * 0.4 + tag_score * 0.2)
        
        return total_score, evidence
    
    def calculate_categorical_similarity(self, cat1: str, cat2: str) -> Tuple[float, List[str]]:
        """Calculate categorical similarity"""
        if cat1 == cat2:
            return 1.0, [f"Same category: {cat1}"]
        return 0.0, []
    
    def calculate_temporal_similarity(self, date1: str, date2: str) -> Tuple[float, List[str]]:
        """Calculate temporal similarity based on creation dates"""
        try:
            d1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
            d2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
            
            days_diff = abs((d1 - d2).days)
            
            if days_diff == 0:
                return 1.0, ["Created on same day"]
            elif days_diff <= 1:
                return 0.8, ["Created within 1 day"]
            elif days_diff <= 7:
                return 0.6, ["Created within 1 week"]
            elif days_diff <= 30:
                return 0.4, ["Created within 1 month"]
            elif days_diff <= 90:
                return 0.2, ["Created within 3 months"]
            else:
                return 0.1, ["Created more than 3 months apart"]
        except:
            return 0.0, ["Invalid dates"]
    
    def calculate_causal_similarity(self, text1: str, text2: str, 
                                   id1: str, id2: str) -> Tuple[float, List[str]]:
        """Check if one memory references another"""
        evidence = []
        
        # Check if text1 mentions id2
        if id2 in text1:
            evidence.append(f"Memory {id1} references {id2}")
            return 0.9, evidence
        
        # Check if text2 mentions id1
        if id1 in text2:
            evidence.append(f"Memory {id2} references {id1}")
            return 0.9, evidence
        
        # Check for lesson code references
        codes1 = set(re.findall(r'[A-Z]+-\d+', text1))
        codes2 = set(re.findall(r'[A-Z]+-\d+', text2))
        
        if codes1 & codes2:
            evidence.append(f"Shared lesson codes: {', '.join(list(codes1 & codes2)[:3])}")
            return 0.7, evidence
        
        return 0.0, []
    
    def build_associations(self, memories: List[Dict]) -> AssociationGraph:
        """
        Build association graph from list of memories
        Each memory should have: id, content, category, created_at
        """
        graph = AssociationGraph()
        
        # Add nodes
        for mem in memories:
            graph.add_node(mem['id'], {
                'category': mem.get('category', 'general'),
                'created_at': mem.get('created_at', ''),
                'tags': list(self.extract_tags(mem.get('content', '')))
            })
        
        # Build edges
        n = len(memories)
        for i in range(n):
            for j in range(i + 1, n):
                mem1 = memories[i]
                mem2 = memories[j]
                
                associations = []
                
                # 1. Semantic similarity
                sem_score, sem_evidence = self.calculate_semantic_similarity(
                    mem1.get('content', ''),
                    mem2.get('content', '')
                )
                if sem_score > 0:
                    associations.append(('semantic', sem_score, sem_evidence))
                
                # 2. Categorical
                cat_score, cat_evidence = self.calculate_categorical_similarity(
                    mem1.get('category', ''),
                    mem2.get('category', '')
                )
                if cat_score > 0:
                    associations.append(('categorical', cat_score, cat_evidence))
                
                # 3. Temporal
                temp_score, temp_evidence = self.calculate_temporal_similarity(
                    mem1.get('created_at', ''),
                    mem2.get('created_at', '')
                )
                if temp_score > 0:
                    associations.append(('temporal', temp_score, temp_evidence))
                
                # 4. Causal
                causal_score, causal_evidence = self.calculate_causal_similarity(
                    mem1.get('content', ''),
                    mem2.get('content', ''),
                    mem1['id'],
                    mem2['id']
                )
                if causal_score > 0:
                    associations.append(('causal', causal_score, causal_evidence))
                
                # Calculate weighted strength
                if associations:
                    total_strength = 0
                    all_evidence = []
                    
                    for assoc_type, strength, evidence in associations:
                        weight = self.strategies.get(assoc_type, 0.1)
                        total_strength += strength * weight
                        all_evidence.extend(evidence)
                    
                    if total_strength >= self.min_strength:
                        association = Association(
                            source_id=mem1['id'],
                            target_id=mem2['id'],
                            association_type=associations[0][0],  # Primary type
                            strength=round(min(total_strength, 1.0), 3),
                            evidence=all_evidence[:5]  # Top 5 evidence
                        )
                        graph.add_edge(association)
        
        return graph
    
    def find_related(self, memory_id: str, graph: AssociationGraph, 
                    max_results: int = 10) -> List[Tuple[str, float, str]]:
        """Find memories related to given memory"""
        related = []
        
        for edge in graph.edges:
            if edge.source_id == memory_id:
                related.append((edge.target_id, edge.strength, edge.association_type))
            elif edge.target_id == memory_id:
                related.append((edge.source_id, edge.strength, edge.association_type))
        
        return sorted(related, key=lambda x: x[1], reverse=True)[:max_results]
    
    def save_graph(self, graph: AssociationGraph, filename: str = None):
        """Save association graph to JSON file"""
        if not filename:
            filename = f'associations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        output_file = ASSOCIATION_DIR / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"💾 Association graph saved to: {output_file}")
        return output_file

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Association Builder")
    parser.add_argument('--build', action='store_true', 
                       help='Build associations from MEMORY.md')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo with sample data')
    parser.add_argument('--output', type=str,
                       help='Output JSON file')
    args = parser.parse_args()
    
    builder = MemoryAssociationBuilder()
    
    if args.demo:
        print("\n🔗 Memory Association Builder Demo")
        print("=" * 80)
        
        # Sample memories
        samples = [
            {
                'id': 'mem_001',
                'content': '[SECURITY-001] Security best practices - use environment variables for secrets',
                'category': 'security',
                'created_at': '2026-03-15T10:00:00'
            },
            {
                'id': 'mem_002',
                'content': '[SECURITY-002] Store all secrets in .env file, add to .gitignore',
                'category': 'security',
                'created_at': '2026-03-15T11:00:00'
            },
            {
                'id': 'mem_003',
                'content': '[MEMORY-001] Memory distillation achieves 5.6x compression with Qwen2.5:1.5b',
                'category': 'memory',
                'created_at': '2026-03-16T09:00:00'
            },
            {
                'id': 'mem_004',
                'content': '[TOOL-001] memory-distiller.py tool created for automatic memory compression',
                'category': 'tool',
                'created_at': '2026-03-16T10:00:00'
            }
        ]
        
        print(f"\nBuilding associations for {len(samples)} memories...")
        graph = builder.build_associations(samples)
        
        print(f"\n📊 Association Graph Statistics:")
        stats = graph.to_dict()['stats']
        print(f"   Nodes: {stats['node_count']}")
        print(f"   Edges: {stats['edge_count']}")
        print(f"   Avg edges per node: {stats['avg_edges_per_node']:.2f}")
        
        print(f"\n🔗 Discovered Associations:")
        for edge in graph.edges:
            print(f"   {edge.source_id} ←[{edge.association_type}:{edge.strength:.2f}]→ {edge.target_id}")
            for ev in edge.evidence:
                print(f"      • {ev}")
        
        # Save
        output = builder.save_graph(graph, args.output)
        print(f"\n✅ Demo complete!")
    
    elif args.build:
        # Load MEMORY.md
        if not MEMORY_FILE.exists():
            print(f"❌ Memory file not found: {MEMORY_FILE}")
            return
        
        print(f"📖 Loading memories from {MEMORY_FILE}...")
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple parsing
        sections = content.split('###')[1:]
        memories = []
        
        for i, section in enumerate(sections):
            lines = section.strip().split('\n')
            if lines:
                # Try to extract category from section title
                title = lines[0].lower()
                category = 'general'
                if 'security' in title:
                    category = 'security'
                elif 'memory' in title:
                    category = 'memory'
                elif 'persona' in title or '人格' in title:
                    category = 'persona'
                elif 'tool' in title or '工具' in title:
                    category = 'tool'
                
                memories.append({
                    'id': f'mem_{i:03d}',
                    'content': section.strip(),
                    'category': category,
                    'created_at': datetime.now().isoformat()
                })
        
        print(f"✅ Loaded {len(memories)} memories")
        print(f"🔗 Building associations...")
        
        graph = builder.build_associations(memories)
        
        # Stats
        stats = graph.to_dict()['stats']
        print(f"\n📊 Results:")
        print(f"   Nodes: {stats['node_count']}")
        print(f"   Edges: {stats['edge_count']}")
        print(f"   Avg connections: {stats['avg_edges_per_node']:.2f}")
        
        # Save
        output = builder.save_graph(graph)
        print(f"\n✅ Association building complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
