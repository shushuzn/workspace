#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Canvas Generator - Multiple canvas types

Types:
- lessons: Research lessons from MEMORY.md
- workflows: Workflow visualizations
- papers: Paper collection overview
- timeline: Research timeline

Author: OpenClaw Team
Date: 2026-03-16
Version: 2.0
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class EnhancedCanvasGenerator:
    """Enhanced canvas generator with multiple types"""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        if workspace_dir:
            self.workspace = Path(workspace_dir)
        else:
            self.workspace = Path(__file__).parent.parent
        
        self.config_dir = self.workspace / "00-config"
        self.memory_file = self.workspace / "MEMORY.md"
        self.papers_dir = self.workspace / "data" / "papers"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def create_lessons_canvas(self, memory_file: Optional[str] = None, output_file: Optional[str] = None) -> Dict:
        """Create lessons canvas from MEMORY.md"""
        if not memory_file:
            memory_file = self.memory_file
        
        if not output_file:
            output_file = self.config_dir / "lessons.canvas"
        
        memory_path = Path(memory_file)
        if not memory_path.exists():
            return {'error': f'MEMORY.md not found at {memory_file}'}
        
        with open(memory_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract lessons (format: [XXX-001] Lesson text)
        lesson_pattern = r'\[([A-Z]+-\d+)\]\s*(.+?)(?=\n|$)'
        lessons = re.findall(lesson_pattern, content)
        
        nodes = []
        edges = []
        
        # Title node
        nodes.append({
            'id': 'title',
            'type': 'text',
            'text': f'# Research Lessons\n{len(lessons)} insights extracted',
            'x': 0,
            'y': 0,
            'width': 400,
            'height': 100
        })
        
        # Group by category
        categories = {}
        for lesson_id, lesson_text in lessons:
            category = lesson_id.split('-')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((lesson_id, lesson_text))
        
        # Create category nodes
        y_offset = 150
        x_offset = -300
        
        for i, (category, category_lessons) in enumerate(categories.items()):
            cat_x = x_offset + (i % 5) * 250
            cat_y = y_offset + (i // 5) * 400
            
            # Category node
            nodes.append({
                'id': f'cat_{category}',
                'type': 'text',
                'text': f'## {category}\n{len(category_lessons)} lessons',
                'x': cat_x,
                'y': cat_y,
                'width': 200,
                'height': 80
            })
            
            # Connect to title
            edges.append({
                'fromNode': 'title',
                'toNode': f'cat_{category}'
            })
            
            # Lesson nodes
            for j, (lesson_id, lesson_text) in enumerate(category_lessons[:10]):  # Limit 10 per category
                lesson_x = cat_x
                lesson_y = cat_y + 100 + j * 120
                
                nodes.append({
                    'id': lesson_id,
                    'type': 'text',
                    'text': f'**{lesson_id}**\n{lesson_text[:100]}...',
                    'x': lesson_x,
                    'y': lesson_y,
                    'width': 200,
                    'height': 100
                })
                
                edges.append({
                    'fromNode': f'cat_{category}',
                    'toNode': lesson_id
                })
        
        canvas = {
            'nodes': nodes,
            'edges': edges
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'output': str(output_file),
            'nodes': len(nodes),
            'edges': len(edges),
            'categories': len(categories),
            'lessons': len(lessons)
        }
    
    def create_papers_canvas(self, keyword: Optional[str] = None, output_file: Optional[str] = None) -> Dict:
        """Create papers overview canvas"""
        if not output_file:
            output_file = self.config_dir / "papers.canvas"
        
        # Scan papers directory
        paper_files = list(self.papers_dir.glob("*.json")) if self.papers_dir.exists() else []
        
        papers_data = []
        for pf in paper_files:
            with open(pf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            papers_data.append({
                'keyword': pf.stem,
                'papers': data.get('papers', []),
                'count': len(data.get('papers', []))
            })
        
        nodes = []
        edges = []
        
        # Title node
        total_papers = sum(p['count'] for p in papers_data)
        nodes.append({
            'id': 'title',
            'type': 'text',
            'text': f'# Paper Collection\n{len(papers_data)} keywords, {total_papers} papers',
            'x': 0,
            'y': 0,
            'width': 400,
            'height': 100
        })
        
        # Keyword nodes
        y_offset = 150
        x_offset = -250
        
        for i, paper_data in enumerate(papers_data):
            if keyword and paper_data['keyword'] != keyword:
                continue
            
            kw_x = x_offset + (i % 4) * 300
            kw_y = y_offset + (i // 4) * 350
            
            keyword_name = paper_data['keyword'].replace('_', ' ').title()
            
            nodes.append({
                'id': f"kw_{paper_data['keyword']}",
                'type': 'text',
                'text': f'## {keyword_name}\n{paper_data["count"]} papers',
                'x': kw_x,
                'y': kw_y,
                'width': 250,
                'height': 80
            })
            
            edges.append({
                'fromNode': 'title',
                'toNode': f"kw_{paper_data['keyword']}"
            })
            
            # Top 5 paper nodes
            for j, paper in enumerate(paper_data['papers'][:5]):
                paper_x = kw_x + 300
                paper_y = kw_y + j * 100
                
                title = paper.get('title', 'Unknown')[:50]
                authors = paper.get('authors', ['Unknown'])[0] if paper.get('authors') else 'Unknown'
                
                nodes.append({
                    'id': f"paper_{paper_data['keyword']}_{j}",
                    'type': 'text',
                    'text': f'**{title}**\n{authors}',
                    'x': paper_x,
                    'y': paper_y,
                    'width': 300,
                    'height': 80
                })
                
                edges.append({
                    'fromNode': f"kw_{paper_data['keyword']}",
                    'toNode': f"paper_{paper_data['keyword']}_{j}"
                })
        
        canvas = {
            'nodes': nodes,
            'edges': edges
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'output': str(output_file),
            'nodes': len(nodes),
            'edges': len(edges),
            'keywords': len(papers_data),
            'papers': total_papers
        }
    
    def create_timeline_canvas(self, output_file: Optional[str] = None) -> Dict:
        """Create timeline canvas from lessons chronologically"""
        if not output_file:
            output_file = self.config_dir / "timeline.canvas"
        
        if not self.memory_file.exists():
            return {'error': 'MEMORY.md not found'}
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract lessons with dates
        lesson_pattern = r'\[([A-Z]+-\d+)\]\s*(.+?)(?=\n|$)'
        lessons = re.findall(lesson_pattern, content)
        
        # Extract dates from section headers
        date_pattern = r'###.*?(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, content)
        
        nodes = []
        edges = []
        
        # Title node
        nodes.append({
            'id': 'title',
            'type': 'text',
            'text': f'# Research Timeline\n{len(lessons)} lessons over {len(dates)} periods',
            'x': 0,
            'y': 0,
            'width': 400,
            'height': 100
        })
        
        # Create timeline nodes (group by date periods)
        y_offset = 150
        x_center = 0
        
        # Group lessons by category for timeline
        categories = {}
        for lesson_id, lesson_text in lessons:
            category = lesson_id.split('-')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((lesson_id, lesson_text))
        
        # Create timeline by category
        for i, (category, category_lessons) in enumerate(categories.items()):
            cat_y = y_offset + i * 300
            
            # Category timeline node
            nodes.append({
                'id': f'timeline_{category}',
                'type': 'text',
                'text': f'## {category} Timeline\n{len(category_lessons)} milestones',
                'x': x_center - 200,
                'y': cat_y,
                'width': 400,
                'height': 80
            })
            
            edges.append({
                'fromNode': 'title',
                'toNode': f'timeline_{category}'
            })
            
            # Lesson milestone nodes (horizontal timeline)
            for j, (lesson_id, lesson_text) in enumerate(category_lessons[:8]):  # Limit 8 per timeline
                milestone_x = x_center - 400 + (j % 4) * 220
                milestone_y = cat_y + 100 + (j // 4) * 120
                
                nodes.append({
                    'id': lesson_id,
                    'type': 'text',
                    'text': f'**{lesson_id}**\n{lesson_text[:80]}...',
                    'x': milestone_x,
                    'y': milestone_y,
                    'width': 200,
                    'height': 100
                })
                
                # Connect to timeline
                edges.append({
                    'fromNode': f'timeline_{category}',
                    'toNode': lesson_id
                })
        
        canvas = {
            'nodes': nodes,
            'edges': edges
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'output': str(output_file),
            'nodes': len(nodes),
            'edges': len(edges),
            'categories': len(categories),
            'lessons': len(lessons)
        }
    
    def create_all(self) -> Dict:
        """Create all canvas types"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'lessons': self.create_lessons_canvas(),
            'papers': self.create_papers_canvas(),
            'timeline': self.create_timeline_canvas(),
            'summary': {
                'total_nodes': 0,
                'total_edges': 0,
                'files_created': 0
            }
        }
        
        for key in ['lessons', 'papers', 'timeline']:
            if results[key].get('success'):
                results['summary']['total_nodes'] += results[key].get('nodes', 0)
                results['summary']['total_edges'] += results[key].get('edges', 0)
                results['summary']['files_created'] += 1
        
        return results


def demo():
    """Run enhanced generator demo"""
    print("\n🎨 Enhanced Canvas Generator Demo\n")
    
    generator = EnhancedCanvasGenerator()
    
    print("="*70)
    print("Creating all canvases...")
    print("="*70)
    
    results = generator.create_all()
    
    print()
    print(f"Lessons: {'✅' if results['lessons'].get('success') else '❌'}")
    if results['lessons'].get('success'):
        print(f"  {results['lessons']['nodes']} nodes, {results['lessons']['edges']} edges")
        print(f"  {results['lessons']['categories']} categories, {results['lessons']['lessons']} lessons")
    
    print()
    print(f"Papers: {'✅' if results['papers'].get('success') else '❌'}")
    if results['papers'].get('success'):
        print(f"  {results['papers']['nodes']} nodes, {results['papers']['edges']} edges")
        print(f"  {results['papers']['keywords']} keywords, {results['papers']['papers']} papers")
    
    print()
    print("="*70)
    print(f"Total: {results['summary']['files_created']} files, {results['summary']['total_nodes']} nodes, {results['summary']['total_edges']} edges")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Canvas Generator')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--lessons', action='store_true', help='Create lessons canvas')
    parser.add_argument('--papers', action='store_true', help='Create papers canvas')
    parser.add_argument('--all', action='store_true', help='Create all canvases')
    args = parser.parse_args()
    
    generator = EnhancedCanvasGenerator()
    
    if args.demo or (not args.lessons and not args.papers and not args.all):
        demo()
    elif args.lessons:
        results = generator.create_lessons_canvas()
        print(json.dumps(results, indent=2))
    elif args.papers:
        results = generator.create_papers_canvas()
        print(json.dumps(results, indent=2))
    elif args.all:
        results = generator.create_all()
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
