#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Generator - Generate workflows from natural language

Features:
- NL → Workflow conversion
- Template selection
- Parameter inference
- Validation & testing
- Smart defaults
- Multi-step workflows
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / 'workflows'
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATES_DIR = WORKSPACE / '30-scripts-tools' / 'workflow_templates'
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

class WorkflowTemplate:
    """Workflow template definitions"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load workflow templates"""
        return {
            'data_pipeline': {
                'name': 'Data Pipeline',
                'description': 'Extract, transform, load data',
                'steps': [
                    {
                        'name': 'extract',
                        'tool': 'data_collector.py',
                        'params': {'source': '${source}', 'output': '${output}'},
                    },
                    {
                        'name': 'transform',
                        'tool': 'data_transformer.py',
                        'params': {'input': '${output}', 'operations': '${operations}'},
                    },
                    {
                        'name': 'load',
                        'tool': 'data_loader.py',
                        'params': {'input': '${transformed}', 'destination': '${destination}'},
                    },
                ],
                'parameters': {
                    'source': {'type': 'string', 'required': True, 'description': 'Data source'},
                    'output': {'type': 'string', 'required': True, 'description': 'Output path'},
                    'operations': {'type': 'list', 'required': False, 'description': 'Transform operations'},
                    'destination': {'type': 'string', 'required': True, 'description': 'Final destination'},
                },
            },
            'analysis_pipeline': {
                'name': 'Analysis Pipeline',
                'description': 'Run analysis and generate report',
                'steps': [
                    {
                        'name': 'prepare',
                        'tool': 'data_preparator.py',
                        'params': {'input': '${input}', 'output': '${prepared}'},
                    },
                    {
                        'name': 'analyze',
                        'tool': 'analyzer.py',
                        'params': {'data': '${prepared}', 'metrics': '${metrics}'},
                    },
                    {
                        'name': 'report',
                        'tool': 'report_generator.py',
                        'params': {'results': '${analysis}', 'format': '${format}'},
                    },
                ],
                'parameters': {
                    'input': {'type': 'string', 'required': True},
                    'metrics': {'type': 'list', 'required': False},
                    'format': {'type': 'string', 'default': 'html'},
                },
            },
            'deployment_pipeline': {
                'name': 'Deployment Pipeline',
                'description': 'Build, test, deploy application',
                'steps': [
                    {
                        'name': 'build',
                        'tool': 'builder.py',
                        'params': {'source': '${source}', 'output': '${build}'},
                    },
                    {
                        'name': 'test',
                        'tool': 'test_runner.py',
                        'params': {'build': '${build}', 'suite': '${suite}'},
                    },
                    {
                        'name': 'deploy',
                        'tool': 'auto_deployer.py',
                        'params': {'artifact': '${build}', 'env': '${env}'},
                    },
                ],
                'parameters': {
                    'source': {'type': 'string', 'required': True},
                    'suite': {'type': 'string', 'default': 'full'},
                    'env': {'type': 'string', 'required': True},
                },
            },
            'monitoring_pipeline': {
                'name': 'Monitoring Pipeline',
                'description': 'Monitor, alert, report',
                'steps': [
                    {
                        'name': 'collect',
                        'tool': 'metrics_collector.py',
                        'params': {'targets': '${targets}', 'interval': '${interval}'},
                    },
                    {
                        'name': 'analyze',
                        'tool': 'anomaly_detector.py',
                        'params': {'metrics': '${collected}', 'threshold': '${threshold}'},
                    },
                    {
                        'name': 'notify',
                        'tool': 'feishu_notification.py',
                        'params': {'alerts': '${anomalies}', 'channel': '${channel}'},
                    },
                ],
                'parameters': {
                    'targets': {'type': 'list', 'required': True},
                    'interval': {'type': 'int', 'default': 300},
                    'threshold': {'type': 'float', 'default': 0.8},
                    'channel': {'type': 'string', 'default': 'general'},
                },
            },
            'backup_pipeline': {
                'name': 'Backup Pipeline',
                'description': 'Backup, compress, store',
                'steps': [
                    {
                        'name': 'backup',
                        'tool': 'backup_tool.py',
                        'params': {'sources': '${sources}', 'output': '${backup}'},
                    },
                    {
                        'name': 'compress',
                        'tool': 'compressor.py',
                        'params': {'input': '${backup}', 'format': '${format}'},
                    },
                    {
                        'name': 'store',
                        'tool': 'storage_sync.py',
                        'params': {'file': '${compressed}', 'destination': '${destination}'},
                    },
                ],
                'parameters': {
                    'sources': {'type': 'list', 'required': True},
                    'format': {'type': 'string', 'default': 'zip'},
                    'destination': {'type': 'string', 'required': True},
                },
            },
        }
    
    def get_template(self, name: str) -> Optional[Dict]:
        """Get template by name"""
        return self.templates.get(name)
    
    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by keywords"""
        query_lower = query.lower()
        matches = []
        
        for name, template in self.templates.items():
            # Match name
            if query_lower in name.lower():
                matches.append({'name': name, 'template': template, 'score': 1.0})
                continue
            
            # Match description
            if query_lower in template['description'].lower():
                matches.append({'name': name, 'template': template, 'score': 0.8})
                continue
            
            # Match step tools
            for step in template['steps']:
                if query_lower in step['tool'].lower():
                    matches.append({'name': name, 'template': template, 'score': 0.6})
                    break
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches


class IntentParser:
    """Parse natural language to workflow intent"""
    
    def __init__(self):
        self.intent_patterns = {
            'data_pipeline': [
                r'(extract|load|transform|etl)\s*(data)?',
                r'data\s*(pipeline|flow|processing)',
                r'(import|export)\s*data',
                r'数据\s*(处理 | 转换 | 管道)',
            ],
            'analysis_pipeline': [
                r'(analyze|analysis)\s*(data|report)?',
                r'generate\s*report',
                r'(statistics|metrics|insights)',
                r'(分析 | 报告 | 统计)',
            ],
            'deployment_pipeline': [
                r'(deploy|release|publish)',
                r'(build|test)\s*and\s*deploy',
                r'ci\s*[/-]?\s*cd',
                r'(部署 | 发布 | 上线)',
            ],
            'monitoring_pipeline': [
                r'(monitor|watch|alert)',
                r'(health|status)\s*check',
                r'(监控 | 警报 | 健康)',
            ],
            'backup_pipeline': [
                r'(backup|save|archive)',
                r'(compress|zip|store)',
                r'(备份 | 压缩 | 存储)',
            ],
        }
    
    def parse(self, description: str) -> Dict:
        """Parse description to intent"""
        desc_lower = description.lower()
        
        # Match intents
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, desc_lower))
            intent_scores[intent] = score
        
        # Get best match
        if max(intent_scores.values()) == 0:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_scores': intent_scores,
            }
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(1.0, intent_scores[best_intent] / 2.0)
        
        # Extract parameters
        params = self._extract_parameters(desc_lower)
        
        return {
            'intent': best_intent,
            'confidence': confidence,
            'parameters': params,
            'all_scores': intent_scores,
        }
    
    def _extract_parameters(self, description: str) -> Dict:
        """Extract parameters from description"""
        params = {}
        
        # Extract paths (simple pattern)
        paths = re.findall(r'[/\\][\w\s./\\-]+', description)
        if paths:
            params['paths'] = paths
        
        # Extract numbers (for intervals, thresholds)
        numbers = re.findall(r'\b\d+\b', description)
        if numbers:
            params['numbers'] = [int(n) for n in numbers]
        
        # Extract common keywords
        keywords = {
            'daily': {'interval': 86400},
            'hourly': {'interval': 3600},
            'weekly': {'interval': 604800},
            'html': {'format': 'html'},
            'json': {'format': 'json'},
            'csv': {'format': 'csv'},
            'production': {'env': 'production'},
            'staging': {'env': 'staging'},
            'test': {'env': 'test'},
        }
        
        for keyword, param in keywords.items():
            if keyword in description:
                params.update(param)
        
        return params


class WorkflowGenerator:
    """
    Generate workflows from natural language
    
    Features:
    - NL → Workflow conversion
    - Template selection
    - Parameter inference
    - Validation & testing
    - Smart defaults
    - Multi-step workflows
    """
    
    def __init__(self):
        self.template_engine = WorkflowTemplate()
        self.intent_parser = IntentParser()
    
    def generate(self, description: str, workflow_name: str = None) -> Dict:
        """Generate workflow from description"""
        # Parse intent
        intent = self.intent_parser.parse(description)
        
        if intent['intent'] == 'unknown':
            return {
                'status': 'error',
                'message': 'Could not understand workflow intent',
                'suggestions': self._get_suggestions(description),
            }
        
        # Get template
        template = self.template_engine.get_template(intent['intent'])
        
        if not template:
            return {
                'status': 'error',
                'message': f'No template found for intent: {intent["intent"]}',
            }
        
        # Generate workflow
        workflow = self._instantiate_workflow(template, intent['parameters'])
        
        # Add metadata
        workflow['metadata'] = {
            'name': workflow_name or f"workflow_{intent['intent']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'description': description,
            'intent': intent['intent'],
            'confidence': intent['confidence'],
            'created_at': datetime.now().isoformat(),
            'template': intent['intent'],
        }
        
        # Validate
        validation = self._validate_workflow(workflow)
        
        return {
            'status': 'success',
            'workflow': workflow,
            'intent': intent,
            'validation': validation,
        }
    
    def _instantiate_workflow(self, template: Dict, params: Dict) -> Dict:
        """Instantiate workflow from template"""
        workflow = {
            'version': '1.0',
            'name': template['name'],
            'description': template['description'],
            'steps': [],
            'parameters': {},
        }
        
        # Copy steps with parameter substitution
        for step in template['steps']:
            new_step = {
                'name': step['name'],
                'tool': step['tool'],
                'params': {},
            }
            
            # Substitute parameters
            for param_name, param_value in step['params'].items():
                if isinstance(param_value, str):
                    # Replace ${param} with actual value or default
                    for key, value in params.items():
                        param_value = param_value.replace(f'${{{key}}}', str(value))
                    
                    # Keep as variable if not substituted
                    if '${' in param_value:
                        param_value = None  # Will be filled by user
                
                new_step['params'][param_name] = param_value
            
            workflow['steps'].append(new_step)
        
        # Set parameters
        for param_name, param_def in template['parameters'].items():
            default = param_def.get('default')
            value = params.get(param_name, default)
            
            workflow['parameters'][param_name] = {
                'value': value,
                'type': param_def.get('type', 'string'),
                'required': param_def.get('required', False),
                'description': param_def.get('description', ''),
            }
        
        return workflow
    
    def _validate_workflow(self, workflow: Dict) -> Dict:
        """Validate workflow"""
        issues = []
        warnings = []
        
        # Check required parameters
        for param_name, param_def in workflow['parameters'].items():
            if param_def['required'] and param_def['value'] is None:
                issues.append({
                    'type': 'missing_parameter',
                    'parameter': param_name,
                    'severity': 'error',
                })
        
        # Check steps
        for i, step in enumerate(workflow['steps']):
            # Check tool exists
            tool_path = WORKSPACE / '30-scripts-tools' / step['tool']
            if not tool_path.exists():
                warnings.append({
                    'type': 'tool_not_found',
                    'step': step['name'],
                    'tool': step['tool'],
                    'severity': 'warning',
                })
            
            # Check params
            for param_name, param_value in step['params'].items():
                if param_value is None:
                    warnings.append({
                        'type': 'unresolved_parameter',
                        'step': step['name'],
                        'parameter': param_name,
                        'severity': 'warning',
                    })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'error_count': len(issues),
            'warning_count': len(warnings),
        }
    
    def _get_suggestions(self, description: str) -> List[str]:
        """Get suggestions for unclear intent"""
        suggestions = [
            "Try using keywords like: 'deploy', 'analyze', 'backup', 'monitor'",
            "Specify the type of workflow: 'data pipeline', 'deployment', etc.",
            "Include source and destination paths",
            "Mention tools you want to use",
        ]
        return suggestions
    
    def save_workflow(self, workflow: Dict, output_path: Path = None) -> str:
        """Save workflow to file"""
        if output_path is None:
            name = workflow['metadata']['name']
            output_path = WORKFLOWS_DIR / f"{name}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2)
        
        return str(output_path)
    
    def print_workflow(self, workflow: Dict):
        """Print workflow to console"""
        print("\n" + "=" * 60)
        print("📋 GENERATED WORKFLOW")
        print("=" * 60)
        
        meta = workflow['metadata']
        print(f"\n📝 Name: {meta['name']}")
        print(f"📄 Description: {meta['description']}")
        print(f"🎯 Intent: {meta['intent']} (confidence: {meta['confidence']:.2f})")
        
        print(f"\n🔧 STEPS ({len(workflow['steps'])}):")
        for i, step in enumerate(workflow['steps'], 1):
            print(f"\n  {i}. {step['name']}")
            print(f"     Tool: {step['tool']}")
            print(f"     Params:")
            for param, value in step['params'].items():
                print(f"       - {param}: {value}")
        
        print(f"\n⚙️  PARAMETERS:")
        for param, defn in workflow['parameters'].items():
            required = " (required)" if defn['required'] else ""
            print(f"   - {param}: {defn['value']} {required}")
        
        validation = workflow.get('validation', {})
        if validation:
            print(f"\n✅ Validation: {'PASS' if validation['valid'] else 'FAIL'}")
            if validation['issues']:
                print(f"   Issues: {len(validation['issues'])}")
                for issue in validation['issues'][:3]:
                    print(f"     - {issue['type']}: {issue.get('parameter', issue.get('step', ''))}")
            if validation['warnings']:
                print(f"   Warnings: {len(validation['warnings'])}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Workflow Generator")
    parser.add_argument('--generate', type=str, help='Generate workflow from description')
    parser.add_argument('--name', type=str, help='Workflow name')
    parser.add_argument('--save', action='store_true', help='Save workflow to file')
    parser.add_argument('--templates', action='store_true', help='List templates')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()
    
    generator = WorkflowGenerator()
    
    if args.templates:
        templates = generator.template_engine.templates
        print("\n📋 AVAILABLE TEMPLATES:")
        for name, template in templates.items():
            print(f"\n  {name}: {template['description']}")
            print(f"     Steps: {len(template['steps'])}")
    
    elif args.generate:
        result = generator.generate(args.generate, args.name)
        
        if result['status'] == 'success':
            generator.print_workflow(result['workflow'])
            
            if args.save:
                path = generator.save_workflow(result['workflow'])
                print(f"\n💾 Workflow saved: {path}")
        else:
            print(f"\n❌ Error: {result['message']}")
            if 'suggestions' in result:
                print("\n💡 Suggestions:")
                for sug in result['suggestions']:
                    print(f"   - {sug}")
    
    elif args.interactive:
        print("\n🤖 Workflow Generator - Interactive Mode")
        print("=" * 60)
        print("Describe your workflow! (type 'templates' to see available, 'quit' to exit)")
        print("=" * 60)
        
        while True:
            try:
                description = input("\n📝 Description: ").strip()
                
                if description.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if description.lower() == 'templates':
                    templates = generator.template_engine.templates
                    print("\n📋 Templates:")
                    for name, template in templates.items():
                        print(f"   {name}: {template['description']}")
                    continue
                
                if not description:
                    continue
                
                result = generator.generate(description)
                
                if result['status'] == 'success':
                    generator.print_workflow(result['workflow'])
                    
                    # Ask to save
                    save = input("\n💾 Save workflow? (y/n): ").strip().lower()
                    if save == 'y':
                        name = input("   Name: ").strip() or result['workflow']['metadata']['name']
                        result['workflow']['metadata']['name'] = name
                        path = generator.save_workflow(result['workflow'])
                        print(f"   ✅ Saved: {path}")
                else:
                    print(f"\n❌ {result['message']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
