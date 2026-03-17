#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Template Generator - Enhanced
Create custom workflows from templates
Features: interactive creation, validation, examples

Usage:
    python workflow_template_gen.py --create my_workflow
    python workflow_template_gen.py --examples
    python workflow_template_gen.py --validate workflow.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Workspace root
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / "40-workflows"
TEMPLATES_DIR = WORKSPACE / "30-scripts-tools" / "workflow_templates"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class WorkflowTemplateGenerator:
    """Generate workflow templates"""
    
    def __init__(self):
        WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    def create_workflow(self, name: str, workflow_type: str = 'sequential') -> str:
        """Create a new workflow from template"""
        workflow_id = name.lower().replace(' ', '_')
        
        templates = {
            'sequential': {
                'id': workflow_id,
                'name': name,
                'description': 'Custom sequential workflow',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'step_1',
                        'tool': 'your_tool.py',
                        'args': [],
                        'parallel': False,
                        'timeout': 300
                    },
                    {
                        'id': 'step_2',
                        'tool': 'another_tool.py',
                        'args': [],
                        'parallel': False,
                        'depends_on': ['step_1'],
                        'timeout': 300
                    }
                ]
            },
            'parallel': {
                'id': workflow_id,
                'name': name,
                'description': 'Custom parallel workflow',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'branch_1',
                        'tool': 'tool_a.py',
                        'args': [],
                        'parallel': True,
                        'timeout': 300
                    },
                    {
                        'id': 'branch_2',
                        'tool': 'tool_b.py',
                        'args': [],
                        'parallel': True,
                        'timeout': 300
                    },
                    {
                        'id': 'merge',
                        'tool': 'merger.py',
                        'args': [],
                        'parallel': False,
                        'depends_on': ['branch_1', 'branch_2'],
                        'timeout': 300
                    }
                ]
            },
            'conditional': {
                'id': workflow_id,
                'name': name,
                'description': 'Custom conditional workflow',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'check',
                        'tool': 'checker.py',
                        'args': [],
                        'parallel': False,
                        'timeout': 300
                    },
                    {
                        'id': 'if_true',
                        'tool': 'action_true.py',
                        'args': [],
                        'parallel': False,
                        'depends_on': ['check'],
                        'condition': 'check.success',
                        'timeout': 300
                    },
                    {
                        'id': 'if_false',
                        'tool': 'action_false.py',
                        'args': [],
                        'parallel': False,
                        'depends_on': ['check'],
                        'condition': 'not check.success',
                        'timeout': 300
                    }
                ]
            },
            'daily_brief': {
                'id': workflow_id,
                'name': name,
                'description': 'Daily research brief workflow',
                'version': '1.0',
                'steps': [
                    {'id': 'collect_arxiv', 'tool': 'arxiv_collector.py', 'parallel': False},
                    {'id': 'collect_github', 'tool': 'github_collector.py', 'parallel': False},
                    {'id': 'collect_medium', 'tool': 'medium_collector.py', 'parallel': False},
                    {'id': 'review_code', 'tool': 'code_reviewer.py', 'depends_on': ['collect_github']},
                    {'id': 'review_papers', 'tool': 'paper_reviewer.py', 'depends_on': ['collect_arxiv']},
                    {'id': 'update_kg', 'tool': 'knowledge_graph_builder.py', 'depends_on': ['review_code', 'review_papers']},
                    {'id': 'generate_brief', 'tool': 'daily_brief_generator.py', 'depends_on': ['update_kg']}
                ]
            },
            'data_pipeline': {
                'id': workflow_id,
                'name': name,
                'description': 'Data processing pipeline',
                'version': '1.0',
                'steps': [
                    {'id': 'extract', 'tool': 'extractor.py', 'parallel': False},
                    {'id': 'transform', 'tool': 'transformer.py', 'depends_on': ['extract']},
                    {'id': 'validate', 'tool': 'validator.py', 'depends_on': ['transform']},
                    {'id': 'load', 'tool': 'loader.py', 'depends_on': ['validate']}
                ]
            },
            'quality_gate': {
                'id': workflow_id,
                'name': name,
                'description': 'Quality gate workflow',
                'version': '1.0',
                'steps': [
                    {'id': 'lint', 'tool': 'linter.py', 'parallel': False},
                    {'id': 'test', 'tool': 'tester.py', 'depends_on': ['lint']},
                    {'id': 'review', 'tool': 'reviewer.py', 'depends_on': ['test']},
                    {'id': 'deploy', 'tool': 'deployer.py', 'depends_on': ['review'], 'condition': 'review.success'}
                ]
            }
        }
        
        if workflow_type not in templates:
            print(f"[ERROR] Unknown template: {workflow_type}")
            print(f"Available: {', '.join(templates.keys())}")
            return ""
        
        workflow = templates[workflow_type]
        
        # Save to workflows directory
        workflow_file = WORKFLOWS_DIR / f"{workflow_id}.json"
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Workflow created: {workflow_file}")
        print(f"\nWorkflow Structure:")
        print(f"  ID: {workflow['id']}")
        print(f"  Name: {workflow['name']}")
        print(f"  Steps: {len(workflow['steps'])}")
        print(f"\nNext Steps:")
        print(f"  1. Edit {workflow_file} to customize tools and args")
        print(f"  2. Run: python workflow_engine_v2.py --run {workflow_id}")
        print(f"  3. Visualize: python workflow_engine_v2.py --visualize {workflow_id}")
        
        return str(workflow_file)
    
    def show_examples(self):
        """Show workflow examples"""
        examples = [
            {
                'name': 'Research Pipeline',
                'type': 'daily_brief',
                'description': 'Collect → Review → Synthesize → Brief',
                'steps': 7,
                'duration': '~15 min'
            },
            {
                'name': 'Data Pipeline',
                'type': 'data_pipeline',
                'description': 'Extract → Transform → Validate → Load',
                'steps': 4,
                'duration': '~5 min'
            },
            {
                'name': 'Quality Gate',
                'type': 'quality_gate',
                'description': 'Lint → Test → Review → Deploy',
                'steps': 4,
                'duration': '~10 min'
            },
            {
                'name': 'Parallel Collection',
                'type': 'parallel',
                'description': 'Collect from multiple sources simultaneously',
                'steps': 3,
                'duration': '~3 min'
            },
            {
                'name': 'Conditional Processing',
                'type': 'conditional',
                'description': 'Execute different paths based on conditions',
                'steps': 3,
                'duration': '~5 min'
            }
        ]
        
        print("\n" + "=" * 60)
        print("Workflow Examples")
        print("=" * 60)
        
        for ex in examples:
            print(f"\n📋 {ex['name']}")
            print(f"   Type: {ex['type']}")
            print(f"   Description: {ex['description']}")
            print(f"   Steps: {ex['steps']}")
            print(f"   Est. Duration: {ex['duration']}")
            print(f"   Create: python workflow_template_gen.py --create \"{ex['name']}\" --type {ex['type']}")
        
        print("\n" + "=" * 60)
    
    def validate_workflow(self, workflow_file: str) -> bool:
        """Validate workflow structure"""
        print("\n" + "=" * 60)
        print(f"Validating: {workflow_file}")
        print("=" * 60)
        
        errors = []
        warnings = []
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load: {e}")
            return False
        
        # Check required fields
        required = ['id', 'name', 'steps']
        for field in required:
            if field not in workflow:
                errors.append(f"Missing required field: {field}")
        
        # Check steps
        steps = workflow.get('steps', [])
        if not steps:
            errors.append("No steps defined")
        
        step_ids = set()
        for i, step in enumerate(steps):
            # Check step ID
            if 'id' not in step:
                errors.append(f"Step {i+1} missing 'id'")
            else:
                if step['id'] in step_ids:
                    errors.append(f"Duplicate step ID: {step['id']}")
                step_ids.add(step['id'])
            
            # Check tool
            if 'tool' not in step:
                warnings.append(f"Step '{step.get('id', i+1)}' missing 'tool'")
            
            # Check dependencies
            deps = step.get('depends_on', [])
            for dep in deps:
                if dep not in step_ids:
                    errors.append(f"Step '{step.get('id')}' depends on unknown step: {dep}")
        
        # Check for circular dependencies (simple check)
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        if not errors and not warnings:
            print("\n✅ Workflow is valid!")
        
        print("=" * 60)
        
        return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description='Workflow Template Generator')
    parser.add_argument('--create', type=str, metavar='NAME', help='Create new workflow')
    parser.add_argument('--type', type=str, default='sequential', 
                       choices=['sequential', 'parallel', 'conditional', 'daily_brief', 'data_pipeline', 'quality_gate'],
                       help='Workflow type')
    parser.add_argument('--examples', action='store_true', help='Show examples')
    parser.add_argument('--validate', type=str, metavar='FILE', help='Validate workflow')
    args = parser.parse_args()
    
    generator = WorkflowTemplateGenerator()
    
    if args.create:
        generator.create_workflow(args.create, args.type)
    
    if args.examples:
        generator.show_examples()
    
    if args.validate:
        generator.validate_workflow(args.validate)
    
    if not any([args.create, args.examples, args.validate]):
        parser.print_help()


if __name__ == "__main__":
    main()
