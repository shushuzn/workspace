#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Knowledge Graph Updater - Automated knowledge graph updates

Usage:
    python knowledge_graph_updater.py --scan MEMORY_DIR [--output OUTPUT]
    python knowledge_graph_updater.py --update [--output OUTPUT]
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
OUTPUT_DIR = Path(r"str(Path(__file__).parent.parent)\20-data-reports")
OUTPUT_FILE = OUTPUT_DIR / "knowledge-graph-update.json"
MEMORY_FILE = Path(r"str(Path(__file__).parent.parent)\13-memory-记忆系统\MEMORY.md")
GRAPH_FILE = Path(r"str(Path(__file__).parent.parent)\20-data-reports\knowledge-graph.json")

class KnowledgeGraphUpdater:
    """Automated knowledge graph updater"""
    
    def __init__(self):
        self.entities = {}
        self.relationships = []
        self.categories = set()
        
        # Lesson patterns
        self.lesson_pattern = re.compile(
            r'\[(\w+-\d+)\]\s*(.+?)(?:\n|$)',
            re.IGNORECASE
        )
        
        # Category mapping
        self.category_map = {
            'SYS': 'System',
            'MULTI': 'Multi-Agent',
            'FEISHU': 'Integration',
            'SEC': 'Security',
            'MEM': 'Memory',
            'FILE': 'File Management',
            'COLLECT': 'Data Collection',
            'REVIEW': 'Code Review',
            'DASH': 'Dashboard',
            'CRON': 'Automation',
            'DEPLOY': 'Deployment',
            'EXPAND': 'Expansion',
            'ENCODING': 'Encoding',
            'AUDIT': 'Audit'
        }
    
    def scan_memory(self, memory_file: Path) -> List[Dict]:
        """Scan MEMORY.md for new lessons"""
        if not memory_file.exists():
            return []
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lessons = []
            matches = self.lesson_pattern.findall(content)
            
            seen_ids = set()
            for lesson_id, title in matches:
                if lesson_id not in seen_ids:
                    seen_ids.add(lesson_id)
                    
                    # Determine category
                    category_prefix = lesson_id.split('-')[0]
                    category = self.category_map.get(category_prefix, 'General')
                    
                    # Extract keywords from title
                    keywords = self._extract_keywords(title)
                    
                    lessons.append({
                        'id': lesson_id,
                        'title': title.strip(),
                        'category': category,
                        'keywords': keywords,
                        'confidence': 0.8,
                        'created_at': datetime.now().strftime('%Y-%m-%d')
                    })
            
            return lessons
            
        except Exception as e:
            print(f"[WARN] Scan failed: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split and filter
        words = text.lower().split()
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return keywords[:10]  # Top 10
    
    def build_graph(self, lessons: List[Dict]) -> Dict:
        """Build knowledge graph from lessons"""
        self.entities = {}
        self.relationships = []
        self.categories = set()
        
        # Add entities
        for lesson in lessons:
            self._add_entity(lesson)
        
        # Build relationships
        self._build_relationships()
        
        # Calculate statistics
        stats = self._calculate_stats()
        
        return {
            'version': '2.0',
            'updated_at': datetime.now().isoformat(),
            'statistics': stats,
            'entities': list(self.entities.values()),
            'relationships': self.relationships,
            'categories': list(self.categories)
        }
    
    def _add_entity(self, lesson: Dict):
        """Add entity to graph"""
        entity_id = lesson['id']
        
        self.entities[entity_id] = {
            'id': entity_id,
            'type': 'lesson',
            'title': lesson['title'],
            'category': lesson['category'],
            'keywords': lesson['keywords'],
            'confidence': lesson['confidence'],
            'created_at': lesson['created_at']
        }
        
        self.categories.add(lesson['category'])
    
    def _build_relationships(self):
        """Build relationships between entities"""
        entity_list = list(self.entities.values())
        
        for i, entity1 in enumerate(entity_list):
            for entity2 in entity_list[i+1:]:
                # Keyword-based relationships
                shared_keywords = set(entity1['keywords']) & set(entity2['keywords'])
                if shared_keywords:
                    self.relationships.append({
                        'from': entity1['id'],
                        'to': entity2['id'],
                        'type': 'shares_keyword',
                        'strength': len(shared_keywords) / max(len(entity1['keywords']), len(entity2['keywords'])),
                        'keywords': list(shared_keywords)
                    })
                
                # Category-based relationships
                if entity1['category'] == entity2['category']:
                    self.relationships.append({
                        'from': entity1['id'],
                        'to': entity2['id'],
                        'type': 'same_category',
                        'strength': 0.5,
                        'category': entity1['category']
                    })
    
    def _calculate_stats(self) -> Dict:
        """Calculate graph statistics"""
        # Category distribution
        category_dist = {}
        for entity in self.entities.values():
            cat = entity['category']
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Relationship types
        relationship_types = {}
        for rel in self.relationships:
            rel_type = rel['type']
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        # Average connections per entity
        total_connections = len(self.relationships) * 2
        avg_connections = total_connections / len(self.entities) if self.entities else 0
        
        return {
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'total_categories': len(self.categories),
            'category_distribution': category_dist,
            'relationship_types': relationship_types,
            'avg_connections_per_entity': round(avg_connections, 2),
            'graph_density': round(len(self.relationships) / (len(self.entities) ** 2), 4) if self.entities else 0
        }
    
    def load_existing_graph(self, graph_file: Path) -> Dict:
        """Load existing knowledge graph"""
        if not graph_file.exists():
            return {}
        
        try:
            with open(graph_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def detect_new_lessons(self, new_lessons: List[Dict], existing_graph: Dict) -> List[Dict]:
        """Detect new lessons not in existing graph"""
        existing_ids = set()
        
        for entity in existing_graph.get('entities', []):
            existing_ids.add(entity.get('id', ''))
        
        new = []
        for lesson in new_lessons:
            if lesson['id'] not in existing_ids:
                new.append(lesson)
        
        return new
    
    def merge_graphs(self, existing_graph: Dict, new_lessons: List[Dict]) -> Dict:
        """Merge new lessons into existing graph"""
        # Start with existing
        merged = existing_graph.copy()
        merged['entities'] = existing_graph.get('entities', []).copy()
        merged['relationships'] = existing_graph.get('relationships', []).copy()
        
        # Add new entities
        existing_ids = set(e['id'] for e in merged['entities'])
        
        for lesson in new_lessons:
            if lesson['id'] not in existing_ids:
                merged['entities'].append({
                    'id': lesson['id'],
                    'type': 'lesson',
                    'title': lesson['title'],
                    'category': lesson['category'],
                    'keywords': lesson['keywords'],
                    'confidence': lesson['confidence'],
                    'created_at': lesson['created_at']
                })
                existing_ids.add(lesson['id'])
        
        # Rebuild relationships
        self.entities = {e['id']: e for e in merged['entities']}
        self.relationships = []
        self.categories = set(e['category'] for e in merged['entities'])
        self._build_relationships()
        
        merged['relationships'] = self.relationships
        merged['updated_at'] = datetime.now().isoformat()
        merged['statistics'] = self._calculate_stats()
        
        return merged
    
    def save_graph(self, graph: Dict, output_file: Path = None):
        """Save knowledge graph"""
        if output_file is None:
            output_file = GRAPH_FILE
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Graph saved to {output_file}")
    
    def save_update_report(self, new_lessons: List[Dict], graph: Dict, output_file: Path = None):
        """Save update report"""
        if output_file is None:
            output_file = OUTPUT_FILE
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'summary': {
                'new_lessons': len(new_lessons),
                'total_entities': graph['statistics']['total_entities'],
                'total_relationships': graph['statistics']['total_relationships'],
                'total_categories': graph['statistics']['total_categories']
            },
            'new_lessons': new_lessons,
            'statistics': graph['statistics'],
            'category_distribution': graph['statistics']['category_distribution']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Report saved to {output_file}")
    
    def preview(self, new_lessons: List[Dict], graph: Dict):
        """Preview update in console"""
        print(f"\n🧠 Knowledge Graph Update\n")
        
        print(f"[CHART] Statistics:")
        stats = graph['statistics']
        print(f"   Total Entities: {stats['total_entities']}")
        print(f"   Total Relationships: {stats['total_relationships']}")
        print(f"   Total Categories: {stats['total_categories']}")
        print(f"   Avg Connections: {stats['avg_connections_per_entity']}")
        print(f"   Graph Density: {stats['graph_density']}")
        
        print(f"\n[FOLDER] Category Distribution:")
        for cat, count in sorted(stats['category_distribution'].items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count}")
        
        if new_lessons:
            print(f"\n✨ New Lessons ({len(new_lessons)}):")
            for lesson in new_lessons[:10]:  # Show first 10
                print(f"   [{lesson['id']}] {lesson['title'][:60]}")
            if len(new_lessons) > 10:
                print(f"   ... and {len(new_lessons) - 10} more")
        else:
            print(f"\n[OK] No new lessons")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Graph Updater')
    parser.add_argument('--scan', type=Path, help='Scan memory directory')
    parser.add_argument('--update', action='store_true', help='Update from MEMORY.md')
    parser.add_argument('--output', '-o', type=Path, help='Output file')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--save', action='store_true', help='Save report')
    
    args = parser.parse_args()
    
    updater = KnowledgeGraphUpdater()
    
    # Load existing graph
    existing_graph = updater.load_existing_graph(GRAPH_FILE)
    
    if args.update:
        # Scan MEMORY.md for lessons
        lessons = updater.scan_memory(MEMORY_FILE)
        
        # Detect new lessons
        new_lessons = updater.detect_new_lessons(lessons, existing_graph)
        
        if new_lessons:
            print(f"🆕 Found {len(new_lessons)} new lessons")
            # Merge into existing graph
            if existing_graph:
                graph = updater.merge_graphs(existing_graph, new_lessons)
            else:
                graph = updater.build_graph(lessons)
        else:
            print("[OK] No new lessons")
            graph = existing_graph if existing_graph else updater.build_graph(lessons)
    
    elif args.scan:
        # Scan directory
        lessons = updater.scan_memory(args.scan)
        graph = updater.build_graph(lessons)
        new_lessons = lessons
    
    else:
        # Default: update from MEMORY.md
        lessons = updater.scan_memory(MEMORY_FILE)
        new_lessons = updater.detect_new_lessons(lessons, existing_graph)
        
        if new_lessons or not existing_graph:
            if existing_graph:
                graph = updater.merge_graphs(existing_graph, new_lessons)
            else:
                graph = updater.build_graph(lessons)
        else:
            graph = existing_graph
    
    if args.preview or not args.save:
        updater.preview(new_lessons, graph)
    
    if args.save:
        updater.save_graph(graph)
        updater.save_update_report(new_lessons, graph, args.output)


if __name__ == '__main__':
    main()
