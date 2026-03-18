#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge Graph Builder - Phase 4 Innovation
Automatically extracts entities and relations from workspace files
Builds interactive knowledge graph (JSON + Web UI)

Usage:
    python knowledge_graph_builder.py --build          # Full build
    python knowledge_graph_builder.py --incremental    # Incremental update
    python knowledge_graph_builder.py --view           # Open Web UI
    python knowledge_graph_builder.py --stats          # Show statistics
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports" / "knowledge-graph"
GRAPH_FILE = DATA_DIR / "knowledge-graph.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class KnowledgeGraphBuilder:
    """Build knowledge graph from workspace files"""
    
    def __init__(self):
        self.entities: Dict[str, Dict] = {}
        self.relations: List[Dict] = []
        self.stats = {
            'entities': 0,
            'relations': 0,
            'sources': 0,
            'last_updated': None,
            'build_time_seconds': 0,
        }
    
    def extract_entities(self, text: str, source: str) -> List[Dict]:
        """Extract entities from text"""
        entities = []
        
        # Pattern 1: Lesson codes (e.g., [SYS-001], [INNOV-005])
        lesson_pattern = r'\[([A-Z]+-\d+)\]'
        for match in re.finditer(lesson_pattern, text):
            code = match.group(1)
            entities.append({
                'id': code,
                'type': 'lesson',
                'source': source,
                'metadata': {'category': code.split('-')[0]}
            })
        
        # Pattern 2: Tool names (e.g., cache_manager.py)
        tool_pattern = r'([a-z_]+\.py)'
        for match in re.finditer(tool_pattern, text):
            tool = match.group(1)
            entities.append({
                'id': tool,
                'type': 'tool',
                'source': source,
                'metadata': {}
            })
        
        # Pattern 3: Model names (e.g., Qwen2.5-1.5B)
        model_pattern = r'(Qwen[\d.]+-?\d*[A-Z]?[B]?)'
        for match in re.finditer(model_pattern, text):
            model = match.group(1)
            entities.append({
                'id': model,
                'type': 'model',
                'source': source,
                'metadata': {}
            })
        
        # Pattern 4: URLs
        url_pattern = r'(https?://[^\s\)]+)'
        for match in re.finditer(url_pattern, text):
            url = match.group(1)
            entities.append({
                'id': url,
                'type': 'url',
                'source': source,
                'metadata': {}
            })
        
        # Pattern 5: Git commits
        commit_pattern = r'\b([a-f0-9]{7})\b'
        for match in re.finditer(commit_pattern, text):
            commit = match.group(1)
            entities.append({
                'id': commit,
                'type': 'commit',
                'source': source,
                'metadata': {}
            })
        
        return entities
    
    def extract_relations(self, entities: List[Dict], text: str, source: str) -> List[Dict]:
        """Extract relations between entities"""
        relations = []
        entity_ids = {e['id'] for e in entities}
        
        # Pattern 1: "X → Y" or "X -> Y" (dependency/flow)
        arrow_pattern = r'([A-Z]+-\d+)\s*[→-]+\s*([A-Z]+-\d+)'
        for match in re.finditer(arrow_pattern, text):
            src, tgt = match.group(1), match.group(2)
            if src in entity_ids and tgt in entity_ids:
                relations.append({
                    'source': src,
                    'target': tgt,
                    'type': 'references',
                    'source_file': source
                })
        
        # Pattern 2: "X integrates Y" or "X uses Y"
        integrate_pattern = r'([a-z_]+\.py)\s+(integrates|uses|calls|imports)\s+([a-z_]+\.py)'
        for match in re.finditer(integrate_pattern, text, re.IGNORECASE):
            src, _, tgt = match.groups()
            relations.append({
                'source': src,
                'target': tgt,
                'type': 'integrates',
                'source_file': source
            })
        
        # Pattern 3: "Phase X builds on Phase Y"
        phase_pattern = r'Phase\s+(\d+)\s+builds on\s+Phase\s+(\d+)'
        for match in re.finditer(phase_pattern, text, re.IGNORECASE):
            src, tgt = f"Phase-{match.group(1)}", f"Phase-{match.group(2)}"
            relations.append({
                'source': src,
                'target': tgt,
                'type': 'builds_on',
                'source_file': source
            })
        
        # Pattern 4: Co-occurrence in same file (implicit relation)
        lessons = [e['id'] for e in entities if e['type'] == 'lesson']
        tools = [e['id'] for e in entities if e['type'] == 'tool']
        
        # Lessons used by tools
        for lesson in lessons:
            for tool in tools:
                if lesson in text and tool in text:
                    # Check if they appear in same context (within 200 chars)
                    lesson_idx = text.find(lesson)
                    tool_idx = text.find(tool)
                    if lesson_idx >= 0 and tool_idx >= 0 and abs(lesson_idx - tool_idx) < 200:
                        relations.append({
                            'source': tool,
                            'target': lesson,
                            'type': 'implements',
                            'source_file': source
                        })
        
        # Pattern 5: Model used by tool
        models = [e['id'] for e in entities if e['type'] == 'model']
        for model in models:
            for tool in tools:
                if model in text and tool in text:
                    relations.append({
                        'source': tool,
                        'target': model,
                        'type': 'uses_model',
                        'source_file': source
                    })
        
        return relations
    
    def scan_files(self) -> List[Tuple[Path, str]]:
        """Scan workspace for relevant files"""
        files = []
        
        # Directories to scan
        scan_dirs = [
            WORKSPACE / '30-scripts-tools',
            WORKSPACE / '20-data-reports',
            WORKSPACE / '13-memory-记忆系统',
            WORKSPACE / '00-人格系统',
        ]
        
        # File patterns
        patterns = ['*.py', '*.md', '*.json']
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            for pattern in patterns:
                for file_path in scan_dir.glob(pattern):
                    if file_path.name.startswith('.'):
                        continue
                    if 'node_modules' in str(file_path):
                        continue
                    if '__pycache__' in str(file_path):
                        continue
                    files.append(file_path)
        
        return files
    
    def read_file(self, file_path: Path) -> str:
        """Read file content with encoding handling"""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding='gbk')
            except:
                return ""
    
    def build(self, incremental: bool = False) -> Dict:
        """Build knowledge graph"""
        start_time = datetime.now()
        
        print("[BUILD] Starting knowledge graph construction...")
        print(f"  Mode: {'incremental' if incremental else 'full'}")
        
        # Load existing graph if incremental
        if incremental and GRAPH_FILE.exists():
            print("[LOAD] Loading existing graph...")
            with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                self.entities = {e['id']: e for e in existing.get('entities', [])}
                self.relations = existing.get('relations', [])
        
        # Scan files
        files = self.scan_files()
        print(f"[SCAN] Found {len(files)} files to process")
        
        # Process files
        processed = 0
        for file_path in files:
            try:
                content = self.read_file(file_path)
                if not content:
                    continue
                
                rel_path = str(file_path.relative_to(WORKSPACE))
                
                # Extract entities
                entities = self.extract_entities(content, rel_path)
                for entity in entities:
                    if entity['id'] not in self.entities:
                        self.entities[entity['id']] = entity
                    else:
                        # Add source if not already present
                        if rel_path not in self.entities[entity['id']].get('sources', []):
                            if 'sources' not in self.entities[entity['id']]:
                                self.entities[entity['id']]['sources'] = []
                            self.entities[entity['id']]['sources'].append(rel_path)
                
                # Extract relations
                relations = self.extract_relations(entities, content, rel_path)
                for rel in relations:
                    # Avoid duplicates
                    if not any(r['source'] == rel['source'] and r['target'] == rel['target'] 
                              and r['type'] == rel['type'] for r in self.relations):
                        self.relations.append(rel)
                
                processed += 1
                if processed % 10 == 0:
                    print(f"  Processed {processed}/{len(files)} files...")
                
            except Exception as e:
                print(f"[WARN] Error processing {file_path}: {e}")
        
        # Calculate statistics
        end_time = datetime.now()
        build_time = (end_time - start_time).total_seconds()
        
        self.stats = {
            'entities': len(self.entities),
            'relations': len(self.relations),
            'sources': processed,
            'last_updated': end_time.isoformat(),
            'build_time_seconds': round(build_time, 2),
            'entity_types': self._count_entity_types(),
        }
        
        # Save graph
        self._save_graph()
        
        print(f"[OK] Build complete in {build_time:.2f}s")
        print(f"  Entities: {self.stats['entities']}")
        print(f"  Relations: {self.stats['relations']}")
        print(f"  Sources: {processed} files")
        
        return self._to_dict()
    
    def _count_entity_types(self) -> Dict[str, int]:
        """Count entities by type"""
        type_counts = {}
        for entity in self.entities.values():
            etype = entity.get('type', 'unknown')
            type_counts[etype] = type_counts.get(etype, 0) + 1
        return type_counts
    
    def _save_graph(self):
        """Save graph to file"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        graph_data = self._to_dict()
        
        with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] Graph saved to {GRAPH_FILE}")
    
    def _to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'metadata': {
                'version': '1.0',
                'builder': 'knowledge_graph_builder.py',
                'workspace': str(WORKSPACE),
            },
            'statistics': self.stats,
            'entities': list(self.entities.values()),
            'relations': self.relations,
        }
    
    def show_stats(self):
        """Show graph statistics"""
        if not GRAPH_FILE.exists():
            print("[ERROR] Graph not found. Run --build first.")
            return
        
        with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = data.get('statistics', {})
        
        print("\n" + "=" * 60)
        print("Knowledge Graph Statistics")
        print("=" * 60)
        print(f"  Total Entities:  {stats.get('entities', 0)}")
        print(f"  Total Relations: {stats.get('relations', 0)}")
        print(f"  Source Files:    {stats.get('sources', 0)}")
        print(f"  Last Updated:    {stats.get('last_updated', 'N/A')}")
        print(f"  Build Time:      {stats.get('build_time_seconds', 0):.2f}s")
        print()
        print("Entity Types:")
        for etype, count in stats.get('entity_types', {}).items():
            print(f"    {etype:15} {count:5}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Knowledge Graph Builder')
    parser.add_argument('--build', action='store_true', help='Full build')
    parser.add_argument('--incremental', action='store_true', help='Incremental update')
    parser.add_argument('--view', action='store_true', help='Open Web UI')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()
    
    builder = KnowledgeGraphBuilder()
    
    if args.build or args.incremental:
        builder.build(incremental=args.incremental)
    
    if args.stats:
        builder.show_stats()
    
    if args.view:
        # Open Web UI
        viewer_path = WORKSPACE / '30-scripts-tools' / 'knowledge_graph_viewer.html'
        if viewer_path.exists():
            os.startfile(str(viewer_path))
            print(f"[OK] Opening Web UI: {viewer_path}")
        else:
            print("[WARN] Web UI not found. Run builder first.")
    
    if not any([args.build, args.incremental, args.view, args.stats]):
        parser.print_help()


if __name__ == "__main__":
    main()
