#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Canvas Generator - Create Obsidian Canvas files for knowledge visualization

Generates .canvas files for:
- Knowledge graph visualization
- Lesson relationship mapping
- Concept mind maps
- Workflow diagrams

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class CanvasNode:
    """Canvas node representation"""
    def __init__(self, id: str, label: str, x: int = 0, y: int = 0, 
                 width: int = 350, height: int = 200, color: str = None):
        self.id = id
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "type": "text",
            "text": self.label,
            "color": self.color
        }


class CanvasEdge:
    """Canvas edge/connection representation"""
    def __init__(self, from_node: str, to_node: str, label: str = None):
        self.from_node = from_node
        self.to_node = to_node
        self.label = label
    
    def to_dict(self) -> Dict:
        edge = {
            "id": f"edge-{self.from_node}-{self.to_node}",
            "fromNode": self.from_node,
            "toNode": self.to_node,
            "fromSide": "right",
            "toSide": "left"
        }
        if self.label:
            edge["label"] = self.label
        return edge


class JsonCanvasGenerator:
    """Generate Obsidian JSON Canvas files"""
    
    def __init__(self):
        self.nodes: List[CanvasNode] = []
        self.edges: List[CanvasEdge] = []
    
    def add_node(self, id: str, label: str, x: int = 0, y: int = 0,
                 width: int = 350, height: int = 200, color: str = None) -> CanvasNode:
        """Add a node to canvas"""
        node = CanvasNode(id, label, x, y, width, height, color)
        self.nodes.append(node)
        return node
    
    def add_edge(self, from_node: str, to_node: str, label: str = None) -> CanvasEdge:
        """Add an edge between nodes"""
        edge = CanvasEdge(from_node, to_node, label)
        self.edges.append(edge)
        return edge
    
    def clear(self):
        """Clear all nodes and edges"""
        self.nodes = []
        self.edges = []
    
    def generate(self, title: str = "Knowledge Graph") -> Dict:
        """Generate canvas JSON"""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges]
        }
    
    def save(self, filepath: str, title: str = "Knowledge Graph"):
        """Save canvas to file"""
        canvas_data = self.generate(title)
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def extract_lessons_from_memory(self, memory_file: str) -> Dict[str, List[Dict]]:
        """
        Extract lessons from MEMORY.md
        
        Returns dict of lesson categories
        """
        lessons = {
            'FILE': [],
            'MULTI': [],
            'SYS': [],
            'INNOVATOR': [],
            'STOCK': []
        }
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all lesson references like [FILE-001], [MULTI-002], etc.
            pattern = r'\[([A-Z]+-\d+)\]'
            matches = re.findall(pattern, content)
            
            for match in matches:
                parts = match.split('-')
                if len(parts) == 2:
                    prefix, num = parts[0], parts[1]
                    if prefix in lessons:
                        lessons[prefix].append({
                            'id': match,
                            'number': num
                        })
            
            # Remove duplicates
            for key in lessons:
                seen = set()
                unique = []
                for lesson in lessons[key]:
                    if lesson['id'] not in seen:
                        seen.add(lesson['id'])
                        unique.append(lesson)
                lessons[key] = unique
            
        except Exception as e:
            print(f"Error extracting lessons: {e}")
        
        return lessons
    
    def create_lessons_canvas(self, memory_file: str, output_file: str):
        """
        Create canvas visualization of lessons from MEMORY.md
        
        Args:
            memory_file: Path to MEMORY.md
            output_file: Output canvas file path
        """
        self.clear()
        
        # Extract lessons
        lessons = self.extract_lessons_from_memory(memory_file)
        
        # Create center node
        center_x, center_y = 400, 300
        self.add_node(
            id="center",
            label="# OpenClaw Lessons\n\nKnowledge Base",
            x=center_x,
            y=center_y,
            width=400,
            height=100,
            color=1
        )
        
        # Category colors
        colors = {
            'FILE': 2,      # Red
            'MULTI': 3,     # Orange
            'SYS': 4,       # Yellow
            'INNOVATOR': 5, # Green
            'STOCK': 6      # Blue
        }
        
        category_labels = {
            'FILE': '📁 File Operations',
            'MULTI': '🎭 Multi-Persona',
            'SYS': '⚙️ System',
            'INNOVATOR': '💡 Innovator',
            'STOCK': '📈 Stock Analysis'
        }
        
        # Create category nodes and lesson nodes
        offset_y = 150
        for category, category_lessons in lessons.items():
            if not category_lessons:
                continue
            
            # Category node
            cat_id = f"cat-{category}"
            cat_y = offset_y
            self.add_node(
                id=cat_id,
                label=f"## {category_labels.get(category, category)}\n\n{len(category_lessons)} lessons",
                x=center_x,
                y=cat_y,
                width=300,
                height=80,
                color=colors.get(category, 0)
            )
            
            # Connect center to category
            self.add_edge("center", cat_id)
            
            # Lesson nodes (arranged in arc)
            num_lessons = min(len(category_lessons), 10)  # Limit to 10 per category
            angle_step = 180 / (num_lessons + 1)
            
            for i, lesson in enumerate(category_lessons[:10]):
                angle = (i + 1) * angle_step
                lesson_x = int(center_x - 400 + 800 * (i / max(1, num_lessons - 1)))
                lesson_y = cat_y - 150
                
                lesson_id = f"lesson-{category}-{lesson['number']}"
                self.add_node(
                    id=lesson_id,
                    label=f"**{lesson['id']}**",
                    x=lesson_x,
                    y=lesson_y,
                    width=200,
                    height=60,
                    color=colors.get(category, 0)
                )
                
                # Connect category to lesson
                self.add_edge(cat_id, lesson_id)
            
            offset_y += 200
        
        # Save canvas
        self.save(output_file, "OpenClaw Lessons Knowledge Graph")
        print(f"✅ Canvas saved to: {output_file}")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Edges: {len(self.edges)}")
    
    def create_workflow_canvas(self, workflows: List[Dict], output_file: str):
        """
        Create canvas visualization of workflows
        
        Args:
            workflows: List of workflow dicts with name, steps, dependencies
            output_file: Output canvas file path
        """
        self.clear()
        
        # Title node
        self.add_node(
            id="title",
            label="# OpenClaw Workflows\n\nAutomation Pipeline",
            x=400,
            y=50,
            width=400,
            height=100,
            color=1
        )
        
        # Create workflow nodes
        y_offset = 200
        for i, workflow in enumerate(workflows):
            wf_name = workflow.get('name', f'Workflow-{i}')
            wf_steps = workflow.get('steps', [])
            
            wf_id = f"wf-{i}"
            self.add_node(
                id=wf_id,
                label=f"## {wf_name}\n\n{len(wf_steps)} steps",
                x=400,
                y=y_offset,
                width=350,
                height=100,
                color=3
            )
            
            # Connect title to workflow
            self.add_edge("title", wf_id)
            
            # Create step nodes
            for j, step in enumerate(wf_steps[:5]):  # Limit to 5 steps
                step_id = f"step-{i}-{j}"
                step_x = 400 - 200 + (j * 100)
                step_y = y_offset + 150
                
                self.add_node(
                    id=step_id,
                    label=f"**Step {j+1}**\n{step[:50]}...",
                    x=step_x,
                    y=step_y,
                    width=150,
                    height=80,
                    color=4
                )
                
                # Connect workflow to step
                self.add_edge(wf_id, step_id)
            
            y_offset += 300
        
        # Save canvas
        self.save(output_file, "OpenClaw Workflows")
        print(f"✅ Canvas saved to: {output_file}")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Edges: {len(self.edges)}")


def demo():
    """Run canvas generator demo"""
    print("\n🎨 JSON Canvas Generator Demo\n")
    
    generator = JsonCanvasGenerator()
    
    # Demo 1: Create lessons canvas
    print("="*70)
    print("Demo 1: Lessons Knowledge Graph")
    print("="*70)
    
    memory_file = Path(__file__).parent.parent / "MEMORY.md"
    output_file = Path(__file__).parent.parent / "00-config" / "lessons.canvas"
    
    if memory_file.exists():
        generator.create_lessons_canvas(str(memory_file), str(output_file))
    else:
        print(f"⚠️ MEMORY.md not found at: {memory_file}")
        
        # Create demo canvas with sample data
        generator.clear()
        generator.add_node("center", "# OpenClaw Lessons", 400, 300, 400, 100, 1)
        generator.add_node("file", "## File Operations\n5 lessons", 400, 150, 300, 80, 2)
        generator.add_node("multi", "## Multi-Persona\n10 lessons", 400, 450, 300, 80, 3)
        generator.add_edge("center", "file")
        generator.add_edge("center", "multi")
        generator.save(str(output_file), "Demo Lessons")
        print(f"✅ Demo canvas saved to: {output_file}")
    
    print()
    
    # Demo 2: Create workflow canvas
    print("="*70)
    print("Demo 2: Workflow Visualization")
    print("="*70)
    
    sample_workflows = [
        {
            'name': 'Daily Brief',
            'steps': ['Collect data', 'Analyze', 'Generate report', 'Send notification']
        },
        {
            'name': 'Paper Review',
            'steps': ['Fetch arXiv', 'Extract abstract', 'Local LLM analysis', 'Save to vault']
        },
        {
            'name': 'Code Quality',
            'steps': ['Scan code', 'Calculate metrics', 'Generate report', 'Git commit']
        }
    ]
    
    workflow_output = Path(__file__).parent.parent / "00-config" / "workflows.canvas"
    generator.create_workflow_canvas(sample_workflows, str(workflow_output))
    
    print()
    
    # Demo 3: Canvas structure
    print("="*70)
    print("Demo 3: Canvas JSON Structure")
    print("="*70)
    
    generator.clear()
    generator.add_node("node1", "Node 1: Concept A", 100, 100, 300, 150, 2)
    generator.add_node("node2", "Node 2: Concept B", 500, 100, 300, 150, 3)
    generator.add_edge("node1", "node2", "relates to")
    
    canvas = generator.generate()
    print(json.dumps(canvas, indent=2))
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='JSON Canvas Generator')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--lessons', action='store_true', help='Create lessons canvas')
    parser.add_argument('--workflows', action='store_true', help='Create workflows canvas')
    parser.add_argument('--output', type=str, help='Output file path')
    args = parser.parse_args()
    
    if args.demo or (not args.lessons and not args.workflows):
        demo()
    elif args.lessons:
        generator = JsonCanvasGenerator()
        memory_file = Path(__file__).parent.parent / "MEMORY.md"
        output = args.output or str(Path(__file__).parent.parent / "00-config" / "lessons.canvas")
        generator.create_lessons_canvas(str(memory_file), output)
    elif args.workflows:
        generator = JsonCanvasGenerator()
        # Sample workflows
        workflows = [
            {'name': 'Daily Brief', 'steps': ['Collect', 'Analyze', 'Report']},
        ]
        output = args.output or str(Path(__file__).parent.parent / "00-config" / "workflows.canvas")
        generator.create_workflow_canvas(workflows, output)


if __name__ == "__main__":
    main()
