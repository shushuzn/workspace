#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Validator - Validate workflow correctness

Features:
- Syntax validation
- Tool existence check
- Parameter validation
- Dependency analysis
- Cycle detection
- Best practices
"""

import os
import sys
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, deque

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / 'workflows'
TOOLS_DIR = WORKSPACE / '30-scripts-tools'

class SyntaxValidator:
    """Validate workflow syntax"""
    
    def validate(self, workflow: Dict) -> Dict:
        """Validate syntax"""
        issues = []
        
        # Check required fields
        required_fields = ['version', 'name', 'steps']
        for field in required_fields:
            if field not in workflow:
                issues.append({
                    'type': 'missing_field',
                    'field': field,
                    'severity': 'error',
                    'message': f'Required field "{field}" is missing',
                })
        
        # Check version format
        version = workflow.get('version', '')
        if version and not self._is_valid_version(version):
            issues.append({
                'type': 'invalid_version',
                'version': version,
                'severity': 'warning',
                'message': f'Version should be in format X.Y (e.g., 1.0)',
            })
        
        # Check steps structure
        steps = workflow.get('steps', [])
        if not isinstance(steps, list):
            issues.append({
                'type': 'invalid_steps',
                'severity': 'error',
                'message': 'Steps must be a list',
            })
        else:
            for i, step in enumerate(steps):
                step_issues = self._validate_step(step, i)
                issues.extend(step_issues)
        
        return {
            'valid': all(i['severity'] == 'warning' for i in issues),
            'issues': issues,
            'error_count': sum(1 for i in issues if i['severity'] == 'error'),
            'warning_count': sum(1 for i in issues if i['severity'] == 'warning'),
        }
    
    def _is_valid_version(self, version: str) -> bool:
        """Check version format"""
        try:
            parts = version.split('.')
            return len(parts) == 2 and all(p.isdigit() for p in parts)
        except:
            return False
    
    def _validate_step(self, step: Dict, index: int) -> List[Dict]:
        """Validate single step"""
        issues = []
        
        # Check required fields
        if 'name' not in step:
            issues.append({
                'type': 'missing_field',
                'field': 'name',
                'step_index': index,
                'severity': 'error',
                'message': f'Step {index} missing "name" field',
            })
        
        if 'tool' not in step:
            issues.append({
                'type': 'missing_field',
                'field': 'tool',
                'step_index': index,
                'severity': 'error',
                'message': f'Step {index} missing "tool" field',
            })
        
        # Check name uniqueness
        # (Will be checked in full validation)
        
        # Check params structure
        params = step.get('params', {})
        if params and not isinstance(params, dict):
            issues.append({
                'type': 'invalid_params',
                'step_index': index,
                'severity': 'error',
                'message': 'Params must be a dictionary',
            })
        
        return issues


class ToolValidator:
    """Validate tool existence and compatibility"""
    
    def __init__(self):
        self.available_tools = self._scan_tools()
    
    def _scan_tools(self) -> Dict[str, Path]:
        """Scan available tools"""
        tools = {}
        
        if TOOLS_DIR.exists():
            for py_file in TOOLS_DIR.glob('*.py'):
                if not py_file.name.startswith('_'):
                    tools[py_file.name] = py_file
        
        return tools
    
    def validate(self, workflow: Dict) -> Dict:
        """Validate tools in workflow"""
        issues = []
        warnings = []
        
        steps = workflow.get('steps', [])
        
        for i, step in enumerate(steps):
            tool_name = step.get('tool', '')
            
            if not tool_name:
                continue
            
            # Check if tool exists
            if tool_name not in self.available_tools:
                issues.append({
                    'type': 'tool_not_found',
                    'tool': tool_name,
                    'step_index': i,
                    'step_name': step.get('name', f'step_{i}'),
                    'severity': 'error',
                    'message': f'Tool "{tool_name}" not found in {TOOLS_DIR}',
                    'suggestion': 'Check tool name or install required tool',
                })
            else:
                # Check if tool is executable
                tool_path = self.available_tools[tool_name]
                if not self._is_executable(tool_path):
                    warnings.append({
                        'type': 'tool_not_executable',
                        'tool': tool_name,
                        'step_index': i,
                        'severity': 'warning',
                        'message': f'Tool "{tool_name}" may not be executable',
                    })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'available_tools': len(self.available_tools),
        }
    
    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is executable Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for shebang or main block
            has_shebang = content.startswith('#!')
            has_main = 'if __name__ ==' in content
            
            return has_shebang or has_main
        except:
            return False


class ParameterValidator:
    """Validate workflow parameters"""
    
    def validate(self, workflow: Dict) -> Dict:
        """Validate parameters"""
        issues = []
        warnings = []
        
        # Check workflow-level parameters
        params = workflow.get('parameters', {})
        for param_name, param_def in params.items():
            param_issues = self._validate_parameter(param_name, param_def, 'workflow')
            issues.extend([i for i in param_issues if i['severity'] == 'error'])
            warnings.extend([i for i in param_issues if i['severity'] == 'warning'])
        
        # Check step parameters
        for i, step in enumerate(workflow.get('steps', [])):
            step_params = step.get('params', {})
            for param_name, param_value in step_params.items():
                if param_value is None:
                    warnings.append({
                        'type': 'unresolved_parameter',
                        'parameter': param_name,
                        'step': step.get('name', f'step_{i}'),
                        'step_index': i,
                        'severity': 'warning',
                        'message': f'Parameter "{param_name}" in step "{step.get("name")}" is not resolved',
                    })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
        }
    
    def _validate_parameter(self, name: str, definition: Dict, context: str) -> List[Dict]:
        """Validate single parameter"""
        issues = []
        
        if not isinstance(definition, dict):
            issues.append({
                'type': 'invalid_parameter_definition',
                'parameter': name,
                'context': context,
                'severity': 'error',
                'message': f'Parameter "{name}" definition must be a dictionary',
            })
            return issues
        
        # Check type
        param_type = definition.get('type', 'string')
        valid_types = ['string', 'int', 'float', 'bool', 'list', 'dict']
        if param_type not in valid_types:
            issues.append({
                'type': 'invalid_parameter_type',
                'parameter': name,
                'type': param_type,
                'severity': 'warning',
                'message': f'Unknown parameter type "{param_type}"',
            })
        
        # Check required + default
        is_required = definition.get('required', False)
        has_default = 'default' in definition
        has_value = 'value' in definition
        
        if is_required and not has_value and not has_default:
            issues.append({
                'type': 'missing_required_parameter',
                'parameter': name,
                'severity': 'error',
                'message': f'Required parameter "{name}" has no value or default',
            })
        
        return issues


class DependencyAnalyzer:
    """Analyze workflow dependencies and detect cycles"""
    
    def analyze(self, workflow: Dict) -> Dict:
        """Analyze dependencies"""
        steps = workflow.get('steps', [])
        
        # Build dependency graph
        graph = defaultdict(list)
        reverse_graph = defaultdict(list)
        
        # Extract variable references
        step_outputs = {}
        step_inputs = {}
        
        for i, step in enumerate(steps):
            step_name = step.get('name', f'step_{i}')
            params = step.get('params', {})
            
            # Extract inputs (variables referenced)
            inputs = set()
            for param_value in params.values():
                if isinstance(param_value, str):
                    # Find ${variable} references
                    import re
                    refs = re.findall(r'\$\{(\w+)\}', param_value)
                    inputs.update(refs)
            
            step_inputs[step_name] = inputs
            
            # Assume output name matches step name
            step_outputs[step_name] = step_name
        
        # Build edges
        for step in steps:
            step_name = step.get('name', f'step_{steps.index(step)}')
            
            for input_var in step_inputs.get(step_name, []):
                # Find which step produces this variable
                for other_step in steps:
                    other_name = other_step.get('name', f'step_{steps.index(other_step)}')
                    if other_name == input_var or other_name == f'${{{input_var}}}':
                        graph[other_name].append(step_name)
                        reverse_graph[step_name].append(other_name)
        
        # Detect cycles
        cycles = self._detect_cycles(graph)
        
        # Check for missing dependencies
        missing = []
        for step_name, inputs in step_inputs.items():
            for input_var in inputs:
                if input_var not in step_outputs:
                    # Check if it's a workflow parameter
                    if input_var not in workflow.get('parameters', {}):
                        missing.append({
                            'variable': input_var,
                            'step': step_name,
                            'type': 'missing_dependency',
                        })
        
        return {
            'has_cycles': len(cycles) > 0,
            'cycles': cycles,
            'missing_dependencies': missing,
            'dependency_graph': dict(graph),
            'execution_order': self._topological_sort(graph, steps),
        }
    
    def _detect_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles using DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def _topological_sort(self, graph: Dict[str, List[str]], steps: List[Dict]) -> List[str]:
        """Topological sort for execution order"""
        # Get all nodes
        all_nodes = [step.get('name', f'step_{i}') for i, step in enumerate(steps)]
        
        # Calculate in-degrees
        in_degree = {node: 0 for node in all_nodes}
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        # Kahn's algorithm
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # If not all nodes are in result, there's a cycle
        if len(result) != len(all_nodes):
            return []  # Cycle detected
        
        return result


class BestPracticesChecker:
    """Check workflow best practices"""
    
    def check(self, workflow: Dict) -> Dict:
        """Check best practices"""
        recommendations = []
        
        # Check for error handling
        has_error_handling = self._check_error_handling(workflow)
        if not has_error_handling:
            recommendations.append({
                'type': 'error_handling',
                'severity': 'medium',
                'message': 'Consider adding error handling steps',
                'suggestion': 'Add try-catch or on-error steps',
            })
        
        # Check for logging
        has_logging = self._check_logging(workflow)
        if not has_logging:
            recommendations.append({
                'type': 'logging',
                'severity': 'medium',
                'message': 'Consider adding logging steps',
                'suggestion': 'Add logging or monitoring steps',
            })
        
        # Check step count
        step_count = len(workflow.get('steps', []))
        if step_count > 10:
            recommendations.append({
                'type': 'complexity',
                'severity': 'low',
                'message': f'Workflow has {step_count} steps (consider splitting)',
                'suggestion': 'Break into smaller sub-workflows',
            })
        
        # Check naming
        naming_issues = self._check_naming(workflow)
        recommendations.extend(naming_issues)
        
        return {
            'recommendations': recommendations,
            'score': self._calculate_score(recommendations),
        }
    
    def _check_error_handling(self, workflow: Dict) -> bool:
        """Check for error handling"""
        # Look for error-related tools or steps
        error_keywords = ['error', 'exception', 'retry', 'fallback', 'catch']
        
        for step in workflow.get('steps', []):
            step_name = step.get('name', '').lower()
            tool_name = step.get('tool', '').lower()
            
            if any(kw in step_name or kw in tool_name for kw in error_keywords):
                return True
        
        return False
    
    def _check_logging(self, workflow: Dict) -> bool:
        """Check for logging"""
        logging_keywords = ['log', 'notify', 'report', 'monitor', 'alert']
        
        for step in workflow.get('steps', []):
            step_name = step.get('name', '').lower()
            tool_name = step.get('tool', '').lower()
            
            if any(kw in step_name or kw in tool_name for kw in logging_keywords):
                return True
        
        return False
    
    def _check_naming(self, workflow: Dict) -> List[Dict]:
        """Check naming conventions"""
        issues = []
        
        steps = workflow.get('steps', [])
        step_names = [step.get('name', '') for step in steps]
        
        # Check for duplicates
        seen = set()
        for name in step_names:
            if name in seen:
                issues.append({
                    'type': 'duplicate_name',
                    'name': name,
                    'severity': 'low',
                    'message': f'Duplicate step name: "{name}"',
                })
            seen.add(name)
        
        # Check for descriptive names
        for name in step_names:
            if len(name) < 3:
                issues.append({
                    'type': 'unclear_name',
                    'name': name,
                    'severity': 'low',
                    'message': f'Step name "{name}" is too short',
                })
        
        return issues
    
    def _calculate_score(self, recommendations: List[Dict]) -> float:
        """Calculate best practices score"""
        if not recommendations:
            return 1.0
        
        severity_weights = {'high': 0.3, 'medium': 0.2, 'low': 0.1}
        
        penalty = sum(
            severity_weights.get(r['severity'], 0.1)
            for r in recommendations
        )
        
        return max(0.0, 1.0 - penalty)


class WorkflowValidator:
    """
    Comprehensive workflow validator
    
    Features:
    - Syntax validation
    - Tool existence check
    - Parameter validation
    - Dependency analysis
    - Cycle detection
    - Best practices
    """
    
    def __init__(self):
        self.syntax_validator = SyntaxValidator()
        self.tool_validator = ToolValidator()
        self.param_validator = ParameterValidator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.best_practices_checker = BestPracticesChecker()
    
    def validate(self, workflow: Dict) -> Dict:
        """Full validation"""
        # Run all validators
        syntax_result = self.syntax_validator.validate(workflow)
        tool_result = self.tool_validator.validate(workflow)
        param_result = self.param_validator.validate(workflow)
        dependency_result = self.dependency_analyzer.analyze(workflow)
        best_practices_result = self.best_practices_checker.check(workflow)
        
        # Aggregate results
        all_issues = (
            syntax_result['issues'] +
            tool_result['issues'] +
            param_result['issues'] +
            [{'type': 'cycle', 'cycles': dependency_result['cycles'], 'severity': 'error'} 
             if dependency_result['has_cycles'] else []] +
            dependency_result['missing_dependencies']
        )
        
        all_warnings = (
            syntax_result.get('warnings', []) +
            tool_result.get('warnings', []) +
            param_result.get('warnings', []) +
            best_practices_result['recommendations']
        )
        
        is_valid = (
            syntax_result['valid'] and
            tool_result['valid'] and
            param_result['valid'] and
            not dependency_result['has_cycles']
        )
        
        return {
            'valid': is_valid,
            'syntax': syntax_result,
            'tools': tool_result,
            'parameters': param_result,
            'dependencies': dependency_result,
            'best_practices': best_practices_result,
            'issues': all_issues,
            'warnings': all_warnings,
            'error_count': len([i for i in all_issues if isinstance(i, dict) and i.get('severity') == 'error']),
            'warning_count': len(all_warnings),
            'timestamp': datetime.now().isoformat(),
        }
    
    def validate_file(self, workflow_path: Path) -> Dict:
        """Validate workflow from file"""
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        result = self.validate(workflow)
        result['file'] = str(workflow_path)
        
        return result
    
    def print_report(self, result: Dict):
        """Print validation report"""
        print("\n" + "=" * 60)
        print("🔍 WORKFLOW VALIDATION REPORT")
        print("=" * 60)
        
        print(f"\n{'✅ VALID' if result['valid'] else '❌ INVALID'}")
        print(f"Errors: {result['error_count']} | Warnings: {result['warning_count']}")
        
        if result.get('file'):
            print(f"File: {result['file']}")
        
        # Syntax
        print(f"\n📋 SYNTAX: {'✅' if result['syntax']['valid'] else '❌'}")
        for issue in result['syntax']['issues'][:3]:
            print(f"   - {issue['message']}")
        
        # Tools
        print(f"\n🔧 TOOLS: {'✅' if result['tools']['valid'] else '❌'}")
        print(f"   Available: {result['tools']['available_tools']}")
        for issue in result['tools']['issues'][:3]:
            print(f"   - {issue['message']}")
        
        # Dependencies
        print(f"\n🔗 DEPENDENCIES: {'✅' if not result['dependencies']['has_cycles'] else '❌'}")
        if result['dependencies']['has_cycles']:
            print(f"   Cycles detected: {len(result['dependencies']['cycles'])}")
        if result['dependencies']['missing_dependencies']:
            print(f"   Missing: {len(result['dependencies']['missing_dependencies'])}")
        
        # Best practices
        print(f"\n💡 BEST PRACTICES: {result['best_practices']['score']:.1%}")
        for rec in result['best_practices']['recommendations'][:3]:
            print(f"   - [{rec['severity']}] {rec['message']}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Workflow Validator")
    parser.add_argument('--validate', type=str, help='Validate workflow file')
    parser.add_argument('--check-all', action='store_true', help='Validate all workflows')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()
    
    validator = WorkflowValidator()
    
    if args.validate:
        workflow_path = Path(args.validate)
        
        if not workflow_path.exists():
            # Try workflows directory
            workflow_path = WORKFLOWS_DIR / args.validate
            if not workflow_path.exists():
                # Try with .json extension
                workflow_path = WORKFLOWS_DIR / f"{args.validate}.json"
        
        if not workflow_path.exists():
            print(f"❌ Workflow file not found: {args.validate}")
            return
        
        result = validator.validate_file(workflow_path)
        validator.print_report(result)
    
    elif args.check_all:
        workflows = list(WORKFLOWS_DIR.glob('*.json'))
        
        if not workflows:
            print("📭 No workflows found")
            return
        
        print(f"\n🔍 Validating {len(workflows)} workflows...\n")
        
        valid_count = 0
        for workflow_path in workflows:
            result = validator.validate_file(workflow_path)
            status = "✅" if result['valid'] else "❌"
            print(f"{status} {workflow_path.name}: {result['error_count']} errors, {result['warning_count']} warnings")
            
            if result['valid']:
                valid_count += 1
        
        print(f"\n📊 Summary: {valid_count}/{len(workflows)} valid")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
