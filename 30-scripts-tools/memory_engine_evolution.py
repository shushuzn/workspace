#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Evolution Engine v2.0 - Active Memory Evolution System
Transforms passive storage into active evolution
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import hashlib

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
MEMORY_FILE = MEMORY_DIR / 'MEMORY.md'
EVOLUTION_DIR = WORKSPACE / 'data' / 'memory_evolution'
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class MemoryEntity:
    """Represents a memory entity"""
    id: str
    content: str
    category: str
    created_at: str
    last_accessed: str
    access_count: int = 0
    quality_score: float = 0.0
    relevance_score: float = 0.0
    decay_rate: float = 0.1  # 0-1, higher = faster decay
    tags: List[str] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemoryEntity':
        return cls(**data)

@dataclass
class EvolutionEvent:
    """Represents a memory evolution event"""
    timestamp: str
    event_type: str  # created, updated, distilled, forgotten, merged, split
    memory_id: str
    details: Dict
    impact_score: float  # 0-1
    
    def to_dict(self) -> dict:
        return asdict(self)

class MemoryEvolutionEngine:
    """
    Active memory evolution system
    Implements: quality scoring, forgetting, association, conflict detection
    """
    
    def __init__(self, memory_file: str = None):
        self.memory_file = Path(memory_file) if memory_file else MEMORY_FILE
        self.entities: Dict[str, MemoryEntity] = {}
        self.events: List[EvolutionEvent] = []
        self.config = {
            'quality_threshold': 0.7,  # Min quality to retain
            'forgetting_threshold': 0.3,  # Below this = candidate for forgetting
            'decay_base': 0.95,  # Daily decay factor
            'max_entities': 1000,  # LRU eviction
            'auto_distill': True,
        }
        self.load_memory()
    
    def load_memory(self):
        """Load memory from MEMORY.md"""
        if not self.memory_file.exists():
            print(f"⚠️  Memory file not found: {self.memory_file}")
            return
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse memory sections (simplified)
        sections = content.split('###')
        for section in sections[1:]:  # Skip first empty
            lines = section.strip().split('\n')
            if lines:
                title = lines[0].strip()
                category = self._extract_category(title)
                entity_id = self._generate_id(title)
                
                self.entities[entity_id] = MemoryEntity(
                    id=entity_id,
                    content=title + '\n' + '\n'.join(lines[1:3]),  # First few lines
                    category=category,
                    created_at=datetime.now().isoformat(),
                    last_accessed=datetime.now().isoformat(),
                    access_count=0,
                    quality_score=0.8,  # Default
                    relevance_score=0.8,
                    tags=self._extract_tags(section)
                )
        
        print(f"✅ Loaded {len(self.entities)} memory entities")
    
    def _extract_category(self, title: str) -> str:
        """Extract category from title"""
        if '安全' in title or 'SECURITY' in title:
            return 'security'
        elif '人格' in title or 'PERSONA' in title:
            return 'persona'
        elif '记忆' in title or 'MEMORY' in title:
            return 'memory'
        elif '工具' in title or 'TOOL' in title:
            return 'tools'
        elif '研究' in title or 'RESEARCH' in title:
            return 'research'
        else:
            return 'general'
    
    def _generate_id(self, title: str) -> str:
        """Generate unique ID from title"""
        return hashlib.md5(title.encode()).hexdigest()[:12]
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        tags = []
        # Extract [XXX-001] patterns
        import re
        patterns = re.findall(r'\[([A-Z]+-\d+)\]', content)
        tags.extend(patterns)
        return list(set(tags))
    
    def calculate_quality(self, entity: MemoryEntity) -> float:
        """
        Calculate memory quality score
        Factors: completeness, clarity, relevance, uniqueness
        """
        score = 0.0
        
        # Completeness (30%)
        content_len = len(entity.content)
        if content_len > 100:
            score += 0.3
        elif content_len > 50:
            score += 0.2
        elif content_len > 20:
            score += 0.1
        
        # Clarity (25%)
        if entity.content.count('\n') > 2:  # Has structure
            score += 0.25
        elif len(entity.content.split()) > 10:
            score += 0.15
        
        # Relevance (25%)
        score += entity.relevance_score * 0.25
        
        # Uniqueness (20%)
        if len(entity.tags) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate_decay(self, entity: MemoryEntity, days_since_access: int) -> float:
        """Calculate memory decay based on time"""
        decay = self.config['decay_base'] ** days_since_access
        return decay
    
    def update_relevance(self, entity_id: str, access: bool = True):
        """Update relevance score based on access"""
        if entity_id not in self.entities:
            return
        
        entity = self.entities[entity_id]
        if access:
            entity.access_count += 1
            entity.last_accessed = datetime.now().isoformat()
            # Boost relevance
            entity.relevance_score = min(1.0, entity.relevance_score + 0.05)
        else:
            # Decay relevance
            entity.relevance_score *= 0.95
    
    def get_forgetting_candidates(self) -> List[MemoryEntity]:
        """Get memories that are candidates for forgetting"""
        candidates = []
        now = datetime.now()
        
        for entity in self.entities.values():
            last_access = datetime.fromisoformat(entity.last_accessed)
            days_since = (now - last_access).days
            
            # Calculate current score
            decay = self.calculate_decay(entity, days_since)
            current_score = entity.quality_score * decay * entity.relevance_score
            
            if current_score < self.config['forgetting_threshold']:
                candidates.append(entity)
        
        return sorted(candidates, key=lambda e: e.relevance_score)
    
    def detect_conflicts(self) -> List[Tuple[MemoryEntity, MemoryEntity, str]]:
        """Detect conflicting memories"""
        conflicts = []
        entities_list = list(self.entities.values())
        
        for i, e1 in enumerate(entities_list):
            for e2 in entities_list[i+1:]:
                # Check for contradictory tags
                if e1.category == e2.category:
                    # Simple similarity check
                    similarity = self._calculate_similarity(e1.content, e2.content)
                    if similarity > 0.8 and e1.id != e2.id:
                        conflicts.append((e1, e2, f"High similarity: {similarity:.2f}"))
        
        return conflicts
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple Jaccard)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def associate_memories(self, entity_id: str) -> List[str]:
        """Find related memories"""
        if entity_id not in self.entities:
            return []
        
        entity = self.entities[entity_id]
        related = []
        
        for other_id, other in self.entities.items():
            if other_id == entity_id:
                continue
            
            # Same category
            if entity.category == other.category:
                related.append(other_id)
                continue
            
            # Shared tags
            shared_tags = set(entity.tags) & set(other.tags)
            if shared_tags:
                related.append(other_id)
        
        return related[:10]  # Top 10
    
    def distill_memory(self) -> Dict:
        """
        Distill memory - extract core insights
        Returns distillation report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_entities': len(self.entities),
            'by_category': {},
            'quality_distribution': {
                'high': 0,  # >0.8
                'medium': 0,  # 0.5-0.8
                'low': 0,  # <0.5
            },
            'forgetting_candidates': 0,
            'conflicts_detected': 0,
            'recommendations': []
        }
        
        # Categorize
        for entity in self.entities.values():
            cat = entity.category
            report['by_category'][cat] = report['by_category'].get(cat, 0) + 1
            
            # Quality
            quality = self.calculate_quality(entity)
            entity.quality_score = quality
            
            if quality > 0.8:
                report['quality_distribution']['high'] += 1
            elif quality > 0.5:
                report['quality_distribution']['medium'] += 1
            else:
                report['quality_distribution']['low'] += 1
        
        # Forgetting
        forgetting = self.get_forgetting_candidates()
        report['forgetting_candidates'] = len(forgetting)
        
        # Conflicts
        conflicts = self.detect_conflicts()
        report['conflicts_detected'] = len(conflicts)
        
        # Recommendations
        if report['quality_distribution']['low'] > 10:
            report['recommendations'].append(
                f"Consider reviewing {report['quality_distribution']['low']} low-quality memories"
            )
        if len(forgetting) > 20:
            report['recommendations'].append(
                f"{len(forgetting)} memories are candidates for forgetting"
            )
        if len(conflicts) > 5:
            report['recommendations'].append(
                f"{len(conflicts)} potential conflicts detected - review needed"
            )
        
        # Save report
        report_file = EVOLUTION_DIR / f'distillation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def evolve(self) -> Dict:
        """
        Run full evolution cycle
        """
        print("=" * 80)
        print("🧠 Memory Evolution Engine v2.0 - Evolution Cycle")
        print("=" * 80)
        
        # 1. Quality assessment
        print("\n1️⃣  Quality Assessment...")
        avg_quality = sum(
            self.calculate_quality(e) for e in self.entities.values()
        ) / max(len(self.entities), 1)
        print(f"   Average Quality: {avg_quality:.2f}")
        
        # 2. Decay calculation
        print("\n2️⃣  Calculating Decay...")
        now = datetime.now()
        for entity in self.entities.values():
            last_access = datetime.fromisoformat(entity.last_accessed)
            days = (now - last_access).days
            decay = self.calculate_decay(entity, days)
            entity.relevance_score *= decay
        
        # 3. Forgetting candidates
        print("\n3️⃣  Identifying Forgetting Candidates...")
        forgetting = self.get_forgetting_candidates()
        print(f"   Found {len(forgetting)} candidates")
        
        # 4. Conflict detection
        print("\n4️⃣  Detecting Conflicts...")
        conflicts = self.detect_conflicts()
        print(f"   Found {len(conflicts)} potential conflicts")
        
        # 5. Association building
        print("\n5️⃣  Building Associations...")
        association_count = 0
        for entity in list(self.entities.values())[:20]:  # Sample
            related = self.associate_memories(entity.id)
            entity.related_ids = related
            association_count += len(related)
        print(f"   Built {association_count} associations")
        
        # 6. Distillation
        print("\n6️⃣  Running Distillation...")
        report = self.distill_memory()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 Evolution Summary")
        print("=" * 80)
        print(f"   Total Entities: {report['total_entities']}")
        print(f"   By Category: {report['by_category']}")
        print(f"   Quality: H={report['quality_distribution']['high']} "
              f"M={report['quality_distribution']['medium']} "
              f"L={report['quality_distribution']['low']}")
        print(f"   Forgetting Candidates: {report['forgetting_candidates']}")
        print(f"   Conflicts: {report['conflicts_detected']}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   - {rec}")
        
        print("\n✅ Evolution cycle complete!")
        print(f"   Report saved to: {EVOLUTION_DIR}")
        
        return report
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'total_entities': len(self.entities),
            'categories': {cat: sum(1 for e in self.entities.values() if e.category == cat) 
                          for cat in set(e.category for e in self.entities.values())},
            'avg_quality': sum(e.quality_score for e in self.entities.values()) / max(len(self.entities), 1),
            'avg_relevance': sum(e.relevance_score for e in self.entities.values()) / max(len(self.entities), 1),
            'total_accesses': sum(e.access_count for e in self.entities.values()),
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Evolution Engine v2.0")
    parser.add_argument('--evolve', action='store_true', help='Run evolution cycle')
    parser.add_argument('--distill', action='store_true', help='Run distillation only')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--memory', type=str, help='Custom memory file path')
    args = parser.parse_args()
    
    engine = MemoryEvolutionEngine(args.memory)
    
    if args.evolve:
        engine.evolve()
    elif args.distill:
        report = engine.distill_memory()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.stats:
        stats = engine.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
