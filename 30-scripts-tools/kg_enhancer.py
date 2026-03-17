#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge Graph Enhancer - Advanced KG Management
Features: Auto extraction, relationship inference, MEMORY.md integration, visualization

Usage:
    python kg_enhancer.py --extract
    python kg_enhancer.py --infer
    python kg_enhancer.py --sync-memory
    python kg_enhancer.py --visualize
"""

import os
import sys
import json
import re
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
    type: str  # lesson/persona/tool/system/concept
    category: str
    properties: Dict
    created_at: str
    source: str


@dataclass
class Relationship:
    """Knowledge graph relationship"""
    id: str
    source: str  # entity_id
    target: str  # entity_id
    type: str  # improves/depends_on/creates/uses
    strength: float  # 0.0-1.0
    evidence: str


@dataclass
class Lesson:
    """Extracted lesson"""
    id: str
    code: str  # e.g., SYS-001
    category: str
    content: str
    confidence: float
    source_file: str
    line_number: int
    extracted_at: str


class KnowledgeGraphEnhancer:
    """Advanced knowledge graph management"""
    
    def __init__(self):
        self.kg_dir = WORKSPACE / "15-docs" / "knowledge-graph"
        self.kg_dir.mkdir(parents=True, exist_ok=True)
        
        self.entities_file = self.kg_dir / "entities.json"
        self.relationships_file = self.kg_dir / "relationships.json"
        self.lessons_file = self.kg_dir / "lessons_learned.json"
        self.memory_file = WORKSPACE / "MEMORY.md"
        
        self.entities = []
        self.relationships = []
        self.lessons = []
        
        self.load_state()
    
    def load_state(self):
        """Load KG state"""
        if self.entities_file.exists():
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entities = [Entity(**e) if isinstance(e, dict) else e for e in data.get('entities', [])]
        
        if self.relationships_file.exists():
            with open(self.relationships_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.relationships = [Relationship(**r) if isinstance(r, dict) else r for r in data.get('relationships', [])]
        
        if self.lessons_file.exists():
            with open(self.lessons_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.lessons = [Lesson(**l) if isinstance(l, dict) else l for l in data.get('lessons', [])]
    
    def save_state(self):
        """Save KG state"""
        with open(self.entities_file, 'w', encoding='utf-8') as f:
            json.dump({
                'entities': [asdict(e) if hasattr(e, '__dataclass_fields__') else e for e in self.entities],
                'count': len(self.entities),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.relationships_file, 'w', encoding='utf-8') as f:
            json.dump({
                'relationships': [asdict(r) if hasattr(r, '__dataclass_fields__') else r for r in self.relationships],
                'count': len(self.relationships),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.lessons_file, 'w', encoding='utf-8') as f:
            json.dump({
                'lessons': [asdict(l) if hasattr(l, '__dataclass_fields__') else l for l in self.lessons],
                'count': len(self.lessons),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def extract_lessons_from_memory(self) -> List[Lesson]:
        """Extract lessons from MEMORY.md"""
        print("\n" + "="*60)
        print(" Extracting Lessons from MEMORY.md")
        print("="*60 + "\n")
        
        if not self.memory_file.exists():
            print("❌ MEMORY.md not found")
            return []
        
        lessons = []
        lesson_pattern = r'\[([A-Z]+-\d+)\]\s*(.+?)(?=\n\[|\n\n|$)'
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all lessons
        matches = re.findall(lesson_pattern, content, re.DOTALL)
        
        for code, content in matches:
            # Determine category from code prefix
            category = self._get_category_from_code(code)
            
            # Clean content
            content = content.strip()
            content = re.sub(r'^[-*]\s*', '', content)  # Remove bullet points
            
            lesson = Lesson(
                id=f"lesson_{len(lessons)}",
                code=code,
                category=category,
                content=content,
                confidence=0.9,  # High confidence from structured format
                source_file="MEMORY.md",
                line_number=0,  # Would need line tracking
                extracted_at=datetime.now().isoformat()
            )
            lessons.append(lesson)
            
            print(f"  ✅ {code}: {content[:50]}...")
        
        # Also scan for lessons in other formats
        lesson_patterns = [
            r'### 关键教训.*?\n(.*?)(?=\n##|\Z)',  # Section headers
            r'教训.*?:\s*(.+?)(?=\n)',  # Inline lessons
        ]
        
        for pattern in lesson_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                # Split into individual lessons
                for line in match.split('\n'):
                    line = line.strip()
                    if line and len(line) > 20:  # Meaningful content
                        lesson = Lesson(
                            id=f"lesson_{len(lessons)}",
                            code=f"AUTO-{len(lessons)+1:03d}",
                            category='general',
                            content=line,
                            confidence=0.7,
                            source_file="MEMORY.md",
                            line_number=0,
                            extracted_at=datetime.now().isoformat()
                        )
                        lessons.append(lesson)
        
        print(f"\n✅ Extracted {len(lessons)} lessons\n")
        
        # Merge with existing
        existing_codes = {l.code for l in self.lessons}
        new_lessons = [l for l in lessons if l.code not in existing_codes]
        
        self.lessons.extend(new_lessons)
        self.save_state()
        
        return new_lessons
    
    def _get_category_from_code(self, code: str) -> str:
        """Get category from lesson code"""
        prefix = code.split('-')[0]
        
        categories = {
            'SYS': 'system',
            'MULTI': 'persona',
            'MEM': 'memory',
            'FEISHU': 'integration',
            'SEC': 'security',
            'FILE': 'file_ops',
            'INNOVATOR': 'innovation',
            'LEARNER': 'learning',
            'OPT': 'optimization',
            'REPORT': 'reporting',
            'API': 'api',
            'CACHE': 'caching',
            'HEAL': 'self_healing',
            'WORKFLOW': 'workflow',
            'PERSONA': 'persona',
            'SELF': 'self_iteration',
            'ORCHESTRATE': 'orchestration',
            'MONITOR': 'monitoring',
            'DEPLOY': 'deployment',
            'PERF': 'performance',
        }
        
        return categories.get(prefix, 'general')
    
    def extract_lessons_from_tools(self) -> List[Lesson]:
        """Extract lessons from tool docstrings and comments"""
        print("\n" + "="*60)
        print(" Extracting Lessons from Tools")
        print("="*60 + "\n")
        
        tools_dir = WORKSPACE / "30-scripts-tools"
        lessons = []
        
        for py_file in tools_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for LESSON comments
                lesson_matches = re.findall(r'#\s*LESSON:\s*(.+)', content)
                
                for lesson_text in lesson_matches:
                    lesson = Lesson(
                        id=f"tool_lesson_{len(lessons)}",
                        code=f"TOOL-{len(lessons)+1:03d}",
                        category='tool',
                        content=lesson_text.strip(),
                        confidence=0.8,
                        source_file=str(py_file.relative_to(WORKSPACE)),
                        line_number=0,
                        extracted_at=datetime.now().isoformat()
                    )
                    lessons.append(lesson)
                    print(f"  ✅ {py_file.name}: {lesson_text[:50]}...")
            
            except:
                pass
        
        print(f"\n✅ Extracted {len(lessons)} lessons from tools\n")
        
        # Merge
        self.lessons.extend(lessons)
        self.save_state()
        
        return lessons
    
    def infer_relationships(self) -> List[Relationship]:
        """Infer relationships between entities"""
        print("\n" + "="*60)
        print(" Inferring Relationships")
        print("="*60 + "\n")
        
        relationships = []
        
        # Group lessons by category
        by_category = defaultdict(list)
        for lesson in self.lessons:
            by_category[lesson.category].append(lesson)
        
        # Create relationships within categories
        for category, cat_lessons in by_category.items():
            for i, lesson1 in enumerate(cat_lessons):
                for lesson2 in cat_lessons[i+1:]:
                    # Lessons in same category are related
                    rel = Relationship(
                        id=f"rel_{len(relationships)}",
                        source=lesson1.code,
                        target=lesson2.code,
                        type='related_to',
                        strength=0.6,
                        evidence=f'Same category: {category}'
                    )
                    relationships.append(rel)
        
        # Create relationships based on code patterns
        # e.g., SYS-001 -> SYS-002 (sequential)
        code_groups = defaultdict(list)
        for lesson in self.lessons:
            prefix = lesson.code.split('-')[0]
            code_groups[prefix].append(lesson)
        
        for prefix, group in code_groups.items():
            sorted_group = sorted(group, key=lambda l: int(l.code.split('-')[1]))
            for i in range(len(sorted_group) - 1):
                rel = Relationship(
                    id=f"rel_{len(relationships)}",
                    source=sorted_group[i].code,
                    target=sorted_group[i+1].code,
                    type='evolves_to',
                    strength=0.8,
                    evidence=f'Sequential {prefix} lessons'
                )
                relationships.append(rel)
        
        print(f"✅ Inferred {len(relationships)} relationships\n")
        
        # Merge with existing
        existing_ids = {r.id for r in self.relationships}
        new_rels = [r for r in relationships if r.id not in existing_ids]
        
        self.relationships.extend(new_rels)
        self.save_state()
        
        return new_rels
    
    def create_entities_from_lessons(self) -> List[Entity]:
        """Create entities from lessons"""
        print("\n" + "="*60)
        print(" Creating Entities from Lessons")
        print("="*60 + "\n")
        
        entities = []
        
        for lesson in self.lessons:
            entity = Entity(
                id=f"entity_{lesson.code}",
                name=lesson.code,
                type='lesson',
                category=lesson.category,
                properties={
                    'content': lesson.content,
                    'confidence': lesson.confidence,
                    'source': lesson.source_file
                },
                created_at=lesson.extracted_at,
                source=lesson.source_file
            )
            entities.append(entity)
            print(f"  ✅ {lesson.code} → Entity")
        
        print(f"\n✅ Created {len(entities)} entities\n")
        
        # Merge
        existing_ids = {e.id for e in self.entities}
        new_entities = [e for e in entities if e.id not in existing_ids]
        
        self.entities.extend(new_entities)
        self.save_state()
        
        return new_entities
    
    def sync_with_memory_md(self):
        """Sync extracted lessons to MEMORY.md"""
        print("\n" + "="*60)
        print(" Syncing with MEMORY.md")
        print("="*60 + "\n")
        
        if not self.memory_file.exists():
            print("❌ MEMORY.md not found")
            return
        
        # Read current content
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find lessons section
        lessons_section = "## 🛡️ 文件操作保护系统"
        
        if lessons_section not in content:
            print("⚠️  Lessons section not found, appending to end")
            lessons_section = "## 📝 记忆维护规则"
        
        # Build lessons text
        lessons_text = "\n\n### 最新教训 (Auto-Extracted)\n\n"
        
        for lesson in self.lessons[-20:]:  # Last 20 lessons
            lessons_text += f"- **[{lesson.code}]** {lesson.content}\n"
        
        # Insert before section
        if lessons_section in content:
            content = content.replace(
                lessons_section,
                lessons_text + "\n" + lessons_section
            )
        
        # Write back
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Synced {len(self.lessons[-20:])} lessons to MEMORY.md\n")
    
    def visualize_graph(self) -> str:
        """Generate text visualization of knowledge graph"""
        output = []
        output.append("\n" + "="*70)
        output.append(" Knowledge Graph Visualization")
        output.append("="*70 + "\n")
        
        # Statistics
        output.append("Statistics:")
        output.append(f"  Entities: {len(self.entities)}")
        output.append(f"  Relationships: {len(self.relationships)}")
        output.append(f"  Lessons: {len(self.lessons)}")
        output.append("")
        
        # By category
        by_category = defaultdict(int)
        for lesson in self.lessons:
            by_category[lesson.category] += 1
        
        output.append("Lessons by Category:")
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
            output.append(f"  {cat}: {count}")
        output.append("")
        
        # Top entities by relationships
        entity_rels = defaultdict(int)
        for rel in self.relationships:
            entity_rels[rel.source] += 1
            entity_rels[rel.target] += 1
        
        output.append("Top Connected Entities:")
        for entity, count in sorted(entity_rels.items(), key=lambda x: -x[1])[:10]:
            output.append(f"  {entity}: {count} connections")
        output.append("")
        
        # Sample relationships
        output.append("Sample Relationships:")
        for rel in self.relationships[:10]:
            output.append(f"  {rel.source} --[{rel.type}]--> {rel.target}")
        output.append("")
        
        output.append("="*70 + "\n")
        
        return "\n".join(output)
    
    def get_statistics(self) -> Dict:
        """Get KG statistics"""
        by_category = defaultdict(int)
        for lesson in self.lessons:
            by_category[lesson.category] += 1
        
        return {
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'total_lessons': len(self.lessons),
            'by_category': dict(by_category),
            'avg_relationships_per_entity': len(self.relationships) / len(self.entities) if self.entities else 0
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Graph Enhancer')
    parser.add_argument('--extract', action='store_true', help='Extract lessons')
    parser.add_argument('--infer', action='store_true', help='Infer relationships')
    parser.add_argument('--sync', action='store_true', help='Sync with MEMORY.md')
    parser.add_argument('--visualize', action='store_true', help='Visualize graph')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--full', action='store_true', help='Full extraction cycle')
    args = parser.parse_args()
    
    enhancer = KnowledgeGraphEnhancer()
    
    if args.extract:
        enhancer.extract_lessons_from_memory()
        enhancer.extract_lessons_from_tools()
    
    elif args.infer:
        enhancer.infer_relationships()
        enhancer.create_entities_from_lessons()
    
    elif args.sync:
        enhancer.sync_with_memory_md()
    
    elif args.visualize:
        print(enhancer.visualize_graph())
    
    elif args.stats:
        stats = enhancer.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.full:
        enhancer.extract_lessons_from_memory()
        enhancer.extract_lessons_from_tools()
        enhancer.infer_relationships()
        enhancer.create_entities_from_lessons()
        enhancer.sync_with_memory_md()
        print(enhancer.visualize_graph())
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
