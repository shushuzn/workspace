#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Consolidator - Tool integration and cleanup

Features:
- Duplicate detection
- Tool categorization
- Dependency analysis
- Integration suggestions
- Cleanup recommendations
- Unified interface generation
"""

import os
import sys
import json
import ast
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, Counter

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
INTEGRATION_DIR = WORKSPACE / 'data' / 'integration'
INTEGRATION_DIR.mkdir(parents=True, exist_ok=True)

class ToolScanner:
    """Scan and analyze tools"""
    
    def __init__(self, tools_dir: Path):
        self.tools_dir = tools_dir
        self.tools = []
    
    def scan(self) -> List[Dict]:
        """Scan all Python tools"""
        tools = []
        
        for py_file in self.tools_dir.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            
            tool_info = self._analyze_file(py_file)
            if tool_info:
                tools.append(tool_info)
        
        self.tools = tools
        return tools
    
    def _analyze_file(self, file_path: Path) -> Optional[Dict]:
        """Analyze single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic info
            info = {
                'name': file_path.stem,
                'file': str(file_path),
                'size_bytes': file_path.stat().st_size,
                'size_kb': round(file_path.stat().st_size / 1024, 2),
                'lines': len(content.splitlines()),
                'imports': self._extract_imports(content),
                'functions': self._extract_functions(content),
                'classes': self._extract_classes(content),
                'has_main': 'if __name__ ==' in content,
                'has_cli': 'argparse' in content or 'click' in content,
                'dependencies': self._extract_dependencies(content),
                'content_hash': hashlib.md5(content.encode()).hexdigest(),
            }
            
            # Extract docstring
            tree = ast.parse(content)
            if ast.get_docstring(tree):
                info['description'] = ast.get_docstring(tree).split('\n')[0]
            
            return info
        
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return None
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        for line in content.splitlines():
            if line.startswith('import '):
                imports.append(line.split()[1].split('.')[0])
            elif line.startswith('from '):
                imports.append(line.split()[1].split('.')[0])
        return list(set(imports))
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names"""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            pass
        return functions
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names"""
        classes = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except:
            pass
        return classes
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract external dependencies"""
        # Common external packages
        external = {
            'requests', 'flask', 'fastapi', 'sqlalchemy', 'pandas',
            'numpy', 'matplotlib', 'plotly', 'chartjs', 'redis',
            'paramiko', 'openai', 'anthropic', 'langchain', 'llama'
        }
        
        imports = self._extract_imports(content)
        return [i for i in imports if i in external]


class DuplicateDetector:
    """Detect duplicate or similar tools"""
    
    def __init__(self, tools: List[Dict]):
        self.tools = tools
    
    def detect(self) -> List[Dict]:
        """Detect duplicates"""
        duplicates = []
        
        # Group by hash (exact duplicates)
        hash_groups = defaultdict(list)
        for tool in self.tools:
            hash_groups[tool['content_hash']].append(tool)
        
        for hash_val, group in hash_groups.items():
            if len(group) > 1:
                duplicates.append({
                    'type': 'exact_duplicate',
                    'tools': [t['name'] for t in group],
                    'severity': 'high',
                    'recommendation': 'Keep only one copy',
                })
        
        # Group by similar functionality (name similarity)
        name_groups = defaultdict(list)
        for tool in self.tools:
            # Extract base name (remove version numbers)
            base_name = ''.join(c for c in tool['name'] if not c.isdigit())
            name_groups[base_name].append(tool)
        
        for base_name, group in name_groups.items():
            if len(group) > 1:
                duplicates.append({
                    'type': 'similar_functionality',
                    'tools': [t['name'] for t in group],
                    'base_name': base_name,
                    'severity': 'medium',
                    'recommendation': 'Consider merging or versioning',
                })
        
        # Group by shared imports (potential overlap)
        import_groups = defaultdict(list)
        for tool in self.tools:
            import_key = tuple(sorted(tool['imports'][:5]))  # First 5 imports
            import_groups[import_key].append(tool)
        
        for import_key, group in import_groups.items():
            if len(group) > 3:
                duplicates.append({
                    'type': 'shared_dependencies',
                    'tools': [t['name'] for t in group[:5]],  # Show first 5
                    'shared_imports': list(import_key),
                    'severity': 'low',
                    'recommendation': 'Review for potential consolidation',
                })
        
        return duplicates


class IntegrationAnalyzer:
    """Analyze tool integration opportunities"""
    
    def __init__(self, tools: List[Dict]):
        self.tools = tools
    
    def analyze(self) -> Dict:
        """Analyze integration opportunities"""
        # Category analysis
        categories = self._categorize_tools()
        
        # Dependency graph
        dep_graph = self._build_dependency_graph()
        
        # Integration suggestions
        suggestions = self._generate_suggestions(categories, dep_graph)
        
        return {
            'categories': categories,
            'dependency_graph': dep_graph,
            'integration_suggestions': suggestions,
            'total_tools': len(self.tools),
        }
    
    def _categorize_tools(self) -> Dict[str, List[str]]:
        """Categorize tools by functionality"""
        categories = defaultdict(list)
        
        # Keyword-based categorization
        category_keywords = {
            'deployment': ['deploy', 'ci', 'cd', 'pipeline', 'release'],
            'analysis': ['analyze', 'analytics', 'predict', 'insight', 'report'],
            'automation': ['auto', 'schedule', 'cron', 'heartbeat', 'workflow'],
            'monitoring': ['monitor', 'health', 'watch', 'check', 'dashboard'],
            'data': ['data', 'cache', 'storage', 'database', 'redis'],
            'integration': ['integrat', 'connect', 'api', 'webhook', 'sync'],
            'optimization': ['optim', 'enhance', 'improve', 'tune', 'accelerat'],
            'utility': ['util', 'helper', 'common', 'config', 'setup'],
        }
        
        for tool in self.tools:
            name_lower = tool['name'].lower()
            desc_lower = tool.get('description', '').lower()
            
            categorized = False
            for category, keywords in category_keywords.items():
                if any(kw in name_lower or kw in desc_lower for kw in keywords):
                    categories[category].append(tool['name'])
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(tool['name'])
        
        return dict(categories)
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build tool dependency graph"""
        graph = {}
        
        for tool in self.tools:
            deps = []
            
            # Check for internal dependencies
            for other_tool in self.tools:
                if other_tool['name'] != tool['name']:
                    # Check if imports other tool
                    if other_tool['name'] in tool['imports']:
                        deps.append(other_tool['name'])
            
            graph[tool['name']] = deps
        
        return graph
    
    def _generate_suggestions(self, categories: Dict, dep_graph: Dict) -> List[Dict]:
        """Generate integration suggestions"""
        suggestions = []
        
        # Suggest merging small tools in same category
        for category, tools in categories.items():
            if len(tools) >= 3:
                small_tools = [
                    t for t in tools
                    if next((tool['size_kb'] for tool in self.tools if tool['name'] == t), 100) < 10
                ]
                
                if len(small_tools) >= 2:
                    suggestions.append({
                        'type': 'merge_small_tools',
                        'category': category,
                        'tools': small_tools,
                        'impact': 'medium',
                        'effort': 'medium',
                        'description': f'Merge {len(small_tools)} small {category} tools',
                    })
        
        # Suggest shared modules for common dependencies
        dep_counts = Counter()
        for tool in self.tools:
            for dep in tool.get('dependencies', []):
                dep_counts[dep] += 1
        
        common_deps = [dep for dep, count in dep_counts.items() if count >= 5]
        if common_deps:
            suggestions.append({
                'type': 'create_shared_module',
                'dependencies': common_deps,
                'impact': 'high',
                'effort': 'high',
                'description': f'Create shared module for common dependencies: {", ".join(common_deps[:3])}',
            })
        
        # Suggest unified CLI for tools without CLI
        no_cli = [t['name'] for t in self.tools if not t['has_cli'] and t['has_main']]
        if len(no_cli) >= 5:
            suggestions.append({
                'type': 'add_cli_interface',
                'tools': no_cli[:10],
                'impact': 'medium',
                'effort': 'low',
                'description': f'Add CLI interface to {len(no_cli)} tools',
            })
        
        return suggestions


class ToolConsolidator:
    """
    Tool integration and cleanup
    
    Features:
    - Duplicate detection
    - Tool categorization
    - Dependency analysis
    - Integration suggestions
    - Cleanup recommendations
    - Unified interface generation
    """
    
    def __init__(self, tools_dir: Path = None):
        self.tools_dir = tools_dir or TOOLS_DIR
        self.scanner = ToolScanner(self.tools_dir)
        self.tools = []
        self.duplicates = []
        self.analysis = {}
    
    def scan_tools(self) -> List[Dict]:
        """Scan all tools"""
        self.tools = self.scanner.scan()
        print(f"✅ Scanned {len(self.tools)} tools")
        return self.tools
    
    def detect_duplicates(self) -> List[Dict]:
        """Detect duplicates"""
        if not self.tools:
            self.scan_tools()
        
        self.duplicates = DuplicateDetector(self.tools).detect()
        print(f"🔍 Found {len(self.duplicates)} duplicate/similarity issues")
        return self.duplicates
    
    def analyze_integration(self) -> Dict:
        """Analyze integration opportunities"""
        if not self.tools:
            self.scan_tools()
        
        self.analysis = IntegrationAnalyzer(self.tools).analyze()
        print(f"📊 Analysis complete: {len(self.analysis['categories'])} categories")
        return self.analysis
    
    def generate_report(self) -> Dict:
        """Generate consolidation report"""
        if not self.tools:
            self.scan_tools()
        if not self.duplicates:
            self.detect_duplicates()
        if not self.analysis:
            self.analyze_integration()
        
        # Calculate statistics
        total_size = sum(t['size_bytes'] for t in self.tools)
        total_lines = sum(t['lines'] for t in self.tools)
        avg_size = total_size / max(1, len(self.tools))
        
        # Tools with CLI
        cli_tools = sum(1 for t in self.tools if t['has_cli'])
        
        # Most common dependencies
        dep_counts = Counter()
        for tool in self.tools:
            for dep in tool.get('dependencies', []):
                dep_counts[dep] += 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tools': len(self.tools),
                'total_size_kb': round(total_size / 1024, 2),
                'total_lines': total_lines,
                'avg_tool_size_kb': round(avg_size / 1024, 2),
                'cli_tools': cli_tools,
                'cli_percentage': round(cli_tools / max(1, len(self.tools)) * 100, 1),
            },
            'duplicates': self.duplicates,
            'categories': self.analysis.get('categories', {}),
            'integration_suggestions': self.analysis.get('integration_suggestions', []),
            'top_dependencies': dict(dep_counts.most_common(10)),
        }
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _save_report(self, report: Dict):
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = INTEGRATION_DIR / f'tool_consolidation_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 Report saved: {report_file}")
    
    def print_summary(self):
        """Print summary to console"""
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("🔧 TOOL CONSOLIDATION REPORT")
        print("=" * 60)
        
        summary = report['summary']
        print(f"\n📊 SUMMARY:")
        print(f"   Total tools: {summary['total_tools']}")
        print(f"   Total size: {summary['total_size_kb']} KB")
        print(f"   Total lines: {summary['total_lines']:,}")
        print(f"   Average tool size: {summary['avg_tool_size_kb']:.2f} KB")
        print(f"   Tools with CLI: {summary['cli_tools']} ({summary['cli_percentage']}%)")
        
        print(f"\n📁 CATEGORIES:")
        for category, tools in sorted(report['categories'].items()):
            print(f"   {category}: {len(tools)} tools")
        
        print(f"\n⚠️  DUPLICATES/SIMILARITIES:")
        for dup in report['duplicates'][:5]:
            print(f"   [{dup['severity'].upper()}] {dup['type']}: {', '.join(dup['tools'][:3])}")
        
        print(f"\n💡 INTEGRATION SUGGESTIONS:")
        for sug in report['integration_suggestions'][:5]:
            print(f"   [{sug['impact'].upper()}] {sug['description']}")
        
        print(f"\n📦 TOP DEPENDENCIES:")
        for dep, count in list(report['top_dependencies'].items())[:5]:
            print(f"   {dep}: {count} tools")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tool Consolidator")
    parser.add_argument('--scan', action='store_true', help='Scan tools')
    parser.add_argument('--duplicates', action='store_true', help='Detect duplicates')
    parser.add_argument('--analyze', action='store_true', help='Analyze integration')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--summary', action='store_true', help='Print summary')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    args = parser.parse_args()
    
    consolidator = ToolConsolidator()
    
    if args.scan or args.all:
        consolidator.scan_tools()
    
    if args.duplicates or args.all:
        consolidator.detect_duplicates()
    
    if args.analyze or args.all:
        consolidator.analyze_integration()
    
    if args.report or args.all:
        consolidator.generate_report()
    
    if args.summary or args.all or (not any([args.scan, args.duplicates, args.analyze, args.report, args.all])):
        consolidator.print_summary()

if __name__ == "__main__":
    main()
