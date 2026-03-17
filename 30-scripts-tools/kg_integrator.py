#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge Graph Integrator - Auto-Update Lessons
Automatically updates knowledge graph with new lessons learned
Features: Lesson extraction, entity linking, relationship mapping, auto-update

Usage:
    python kg_integrator.py --extract
    python kg_integrator.py --update
    python kg_integrator.py --sync
    python kg_integrator.py --status
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class Lesson:
    """Lesson learned"""
    id: str
    code: str  # e.g., SELF-001
    category: str
    title: str
    description: str
    source: str
    timestamp: str
    confidence: float
    related_lessons: List[str]
    tags: List[str]


@dataclass
class Entity:
    """Knowledge graph entity"""
    id: str
    name: str
    type: str  # system/tool/concept/pattern
    properties: Dict
    created_at: str
    updated_at: str


@dataclass
class Relationship:
    """Knowledge graph relationship"""
    id: str
    source: str
    target: str
    type: str  # depends_on/uses/improves/relates_to
    weight: float
    created_at: str


class KnowledgeGraphIntegrator:
    """Integrate lessons into knowledge graph"""
    
    def __init__(self):
        self.kg_dir = WORKSPACE / "15-docs" / "knowledge-graph"
        self.lessons_file = self.kg_dir / "lessons_learned.json"
        self.entities_file = self.kg_dir / "entities.json"
        self.relationships_file = self.kg_dir / "relationships.json"
        
        self.lessons = []
        self.entities = []
        self.relationships = []
        
        self.kg_dir.mkdir(parents=True, exist_ok=True)
        self.load_state()
    
    def load_state(self):
        """Load knowledge graph state"""
        if self.lessons_file.exists():
            try:
                with open(self.lessons_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.lessons = [Lesson(**l) if isinstance(l, dict) else l 
                                   for l in data.get('lessons', [])]
            except:
                pass
        
        if self.entities_file.exists():
            try:
                with open(self.entities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entities = [Entity(**e) if isinstance(e, dict) else e 
                                    for e in data.get('entities', [])]
            except:
                pass
        
        if self.relationships_file.exists():
            try:
                with open(self.relationships_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.relationships = [Relationship(**r) if isinstance(r, dict) else r 
                                         for r in data.get('relationships', [])]
            except:
                pass
    
    def save_state(self):
        """Save knowledge graph state"""
        with open(self.lessons_file, 'w', encoding='utf-8') as f:
            json.dump({
                'lessons': [asdict(l) if isinstance(l, Lesson) else l 
                           for l in self.lessons],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.entities_file, 'w', encoding='utf-8') as f:
            json.dump({
                'entities': [asdict(e) if isinstance(e, Entity) else e 
                            for e in self.entities],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.relationships_file, 'w', encoding='utf-8') as f:
            json.dump({
                'relationships': [asdict(r) if isinstance(r, Relationship) else r 
                                 for r in self.relationships],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def extract_lessons_from_memory(self) -> List[Lesson]:
        """Extract lessons from MEMORY.md"""
        print("\n" + "="*60)
        print(" Extracting Lessons from MEMORY.md")
        print("="*60 + "\n")
        
        memory_file = WORKSPACE / "MEMORY.md"
        if not memory_file.exists():
            print("❌ MEMORY.md not found")
            return []
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lessons = []
        
        # Pattern for lesson markers: [XXX-001]
        lesson_pattern = r'\[([A-Z]+-\d+)\]\s*(.*?)\n(.*?)(?=\n\[|$)'
        matches = re.findall(lesson_pattern, content, re.DOTALL)
        
        for match in matches:
            code = match[0]
            title = match[1].strip()
            description = match[2].strip()
            
            # Determine category from code prefix
            category_map = {
                'SELF': 'self_iteration',
                'LEARN': 'meta_learning',
                'EVOLVE': 'evolution',
                'CLI': 'interface',
                'INT': 'integration',
                'DASH': 'visualization',
                'REC': 'recommendation',
                'ORCH': 'orchestration',
                'SYS': 'system',
                'MULTI': 'persona',
                'FILE': 'file_operation',
                'FEISHU': 'notification',
                'SEC': 'security',
                'INNOVATOR': 'innovation',
                'CACHE': 'caching',
                'HEAL': 'self_healing',
                'WORKFLOW': 'workflow',
                'PERSONA': 'persona',
                'CORE': 'core_system',
                'PHASE4': 'phase4'
            }
            
            prefix = code.split('-')[0]
            category = category_map.get(prefix, 'general')
            
            lesson = Lesson(
                id=f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(lessons)}",
                code=code,
                category=category,
                title=title,
                description=description,
                source='MEMORY.md',
                timestamp=datetime.now().isoformat(),
                confidence=0.9,
                related_lessons=[],
                tags=[category, prefix.lower()]
            )
            
            lessons.append(lesson)
            print(f"✅ Extracted: {code} - {title[:50]}...")
        
        print(f"\nTotal extracted: {len(lessons)} lessons\n")
        
        return lessons
    
    def extract_lessons_from_reports(self) -> List[Lesson]:
        """Extract lessons from report files"""
        print("\n" + "="*60)
        print(" Extracting Lessons from Reports")
        print("="*60 + "\n")
        
        reports_dir = WORKSPACE / "20-data-reports"
        lessons = []
        
        if not reports_dir.exists():
            return lessons
        
        # Scan report files
        for report_file in reports_dir.glob("*.md"):
            if not report_file.name.startswith("self_iteration"):
                continue
            
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for lesson sections
            if 'Lessons Learned' in content:
                lesson = Lesson(
                    id=f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(lessons)}",
                    code=f"REPORT-{len(lessons)+1:03d}",
                    category='report',
                    title=f"Lessons from {report_file.name}",
                    description="Extracted from report file",
                    source=report_file.name,
                    timestamp=datetime.fromtimestamp(report_file.stat().st_mtime).isoformat(),
                    confidence=0.8,
                    related_lessons=[],
                    tags=['report', 'lessons']
                )
                lessons.append(lesson)
                print(f"✅ Extracted from: {report_file.name}")
        
        print(f"\nTotal from reports: {len(lessons)}\n")
        
        return lessons
    
    def create_entities(self, lessons: List[Lesson]) -> List[Entity]:
        """Create entities from lessons"""
        print("\n" + "="*60)
        print(" Creating Entities")
        print("="*60 + "\n")
        
        entities = []
        entity_names = set()
        
        # Create system entities
        systems = {
            'self_iteration': 'Self-Iteration Engine',
            'meta_learning': 'Meta-Learning System',
            'evolution': 'Evolution Engine',
            'recommendations': 'Smart Recommendations',
            'dashboard': 'Dashboard',
            'orchestrator': 'System Orchestrator',
            'heartbeat': 'HEARTBEAT Integration',
            'persona': '7-Persona Collaboration',
            'workflow': 'Workflow Engine',
            'cache': 'Cache Manager',
            'self_healing': 'Self-Healing System'
        }
        
        for sys_id, sys_name in systems.items():
            entity = Entity(
                id=f"entity_{sys_id}",
                name=sys_name,
                type='system',
                properties={
                    'category': sys_id,
                    'status': 'active',
                    'priority': 10 if sys_id in ['self_iteration', 'persona', 'self_healing'] else 8
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            entities.append(entity)
            entity_names.add(sys_id)
            print(f"✅ Entity: {sys_name}")
        
        # Create concept entities from lessons
        for lesson in lessons:
            # Extract key concepts from title
            concepts = lesson.title.split()[:3]
            for concept in concepts:
                if len(concept) > 3 and concept.lower() not in entity_names:
                    entity = Entity(
                        id=f"entity_concept_{len(entities)}",
                        name=concept,
                        type='concept',
                        properties={
                            'source_lesson': lesson.code,
                            'category': lesson.category
                        },
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    )
                    entities.append(entity)
                    entity_names.add(concept.lower())
        
        print(f"\nTotal entities: {len(entities)}\n")
        
        return entities
    
    def create_relationships(self, lessons: List[Lesson], entities: List[Entity]) -> List[Relationship]:
        """Create relationships between entities"""
        print("\n" + "="*60)
        print(" Creating Relationships")
        print("="*60 + "\n")
        
        relationships = []
        
        # System dependencies
        dependencies = [
            ('meta_learning', 'self_iteration', 'depends_on'),
            ('evolution', 'meta_learning', 'depends_on'),
            ('recommendations', 'self_iteration', 'uses'),
            ('recommendations', 'meta_learning', 'uses'),
            ('heartbeat', 'self_iteration', 'uses'),
            ('orchestrator', 'self_iteration', 'manages'),
            ('orchestrator', 'meta_learning', 'manages'),
            ('orchestrator', 'evolution', 'manages'),
            ('dashboard', 'self_iteration', 'visualizes'),
            ('dashboard', 'meta_learning', 'visualizes'),
            ('dashboard', 'evolution', 'visualizes'),
        ]
        
        for source, target, rel_type in dependencies:
            rel = Relationship(
                id=f"rel_{len(relationships)}",
                source=f"entity_{source}",
                target=f"entity_{target}",
                type=rel_type,
                weight=0.9,
                created_at=datetime.now().isoformat()
            )
            relationships.append(rel)
            print(f"✅ {source} --[{rel_type}]--> {target}")
        
        # Lesson-based relationships
        for lesson in lessons:
            if lesson.category in ['self_iteration', 'meta_learning', 'evolution']:
                rel = Relationship(
                    id=f"rel_lesson_{lesson.code}",
                    source=f"entity_{lesson.category}",
                    target=f"entity_concept_{len(relationships)}",
                    type='relates_to',
                    weight=0.7,
                    created_at=datetime.now().isoformat()
                )
                relationships.append(rel)
        
        print(f"\nTotal relationships: {len(relationships)}\n")
        
        return relationships
    
    def sync_knowledge_graph(self) -> Dict:
        """Synchronize entire knowledge graph"""
        print("\n" + "="*60)
        print(" Knowledge Graph Synchronization")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        # Step 1: Extract lessons
        lessons_memory = self.extract_lessons_from_memory()
        lessons_reports = self.extract_lessons_from_reports()
        all_lessons = lessons_memory + lessons_reports
        
        # Merge with existing
        existing_codes = {l.code for l in self.lessons}
        new_lessons = [l for l in all_lessons if l.code not in existing_codes]
        self.lessons.extend(new_lessons)
        
        print(f"New lessons: {len(new_lessons)}")
        print(f"Total lessons: {len(self.lessons)}\n")
        
        # Step 2: Create entities
        self.entities = self.create_entities(self.lessons)
        
        # Step 3: Create relationships
        self.relationships = self.create_relationships(self.lessons, self.entities)
        
        # Step 4: Save
        self.save_state()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print(" Synchronization Complete")
        print("="*60)
        print(f"Duration: {duration:.2f}s")
        print(f"Lessons: {len(self.lessons)}")
        print(f"Entities: {len(self.entities)}")
        print(f"Relationships: {len(self.relationships)}")
        print("="*60 + "\n")
        
        return {
            'duration_seconds': duration,
            'lessons': len(self.lessons),
            'new_lessons': len(new_lessons),
            'entities': len(self.entities),
            'relationships': len(self.relationships)
        }
    
    def get_status(self) -> Dict:
        """Get knowledge graph status"""
        return {
            'total_lessons': len(self.lessons),
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'by_category': {},
            'by_entity_type': {},
            'last_updated': datetime.now().isoformat()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Graph Integrator')
    parser.add_argument('--extract', action='store_true', help='Extract lessons')
    parser.add_argument('--update', action='store_true', help='Update knowledge graph')
    parser.add_argument('--sync', action='store_true', help='Full synchronization')
    parser.add_argument('--status', action='store_true', help='Show status')
    args = parser.parse_args()
    
    integrator = KnowledgeGraphIntegrator()
    
    if args.extract:
        lessons = integrator.extract_lessons_from_memory()
        print(f"\nTotal: {len(lessons)} lessons")
    
    elif args.update:
        integrator.sync_knowledge_graph()
    
    elif args.sync:
        result = integrator.sync_knowledge_graph()
        print(json.dumps(result, indent=2))
    
    elif args.status:
        status = integrator.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
