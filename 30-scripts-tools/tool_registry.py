#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Registry - Central tool registration and discovery system

Features:
- Automatic tool scanning and registration
- Metadata extraction (name, version, author, description)
- Category-based organization
- Dependency tracking
- Usage statistics
- Search and filtering
- Health monitoring
"""

import os
import sys
import json
import re
import ast
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
REGISTRY_DIR = WORKSPACE / 'data' / 'tool_registry'
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

class ToolMetadata:
    """Tool metadata extraction"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.name = file_path.stem
        self.size = file_path.stat().st_size
        self.created = datetime.fromtimestamp(file_path.stat().st_ctime)
        self.modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Extracted metadata
        self.version = "1.0"
        self.author = "Claw"
        self.description = ""
        self.category = "general"
        self.dependencies = []
        self.functions = []
        self.classes = []
        self.docstring = ""
        
        # Extract from source
        self._extract_metadata()
    
    def _extract_metadata(self):
        """Extract metadata from Python source"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract docstring
            docstring_match = re.search(r'^"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                self.docstring = docstring_match.group(1).strip()
                # Extract description (first line)
                self.description = self.docstring.split('\n')[0].strip()
            
            # Extract version
            version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                self.version = version_match.group(1)
            
            # Extract author
            author_match = re.search(r'__author__\s*=\s*["\']([^"\']+)["\']', content)
            if author_match:
                self.author = author_match.group(1)
            
            # Extract category from comments
            category_match = re.search(r'#\s*Category:\s*(\w+)', content)
            if category_match:
                self.category = category_match.group(1)
            else:
                # Infer from filename
                self.category = self._infer_category()
            
            # Parse AST for functions and classes
            self._parse_ast(content)
            
        except Exception as e:
            print(f"⚠️  Error extracting metadata from {self.file_path}: {e}")
    
    def _infer_category(self) -> str:
        """Infer category from filename"""
        name_lower = self.name.lower()
        
        categories = {
            'cache': ['cache', 'caching'],
            'search': ['search', 'retrieval', 'index'],
            'ml': ['ml', 'neural', 'rl', 'optimizer', 'predictor'],
            'analysis': ['analysis', 'analyzer', 'analytics'],
            'workflow': ['workflow', 'orchestrator', 'engine'],
            'collector': ['collector', 'crawler', 'scraper'],
            'converter': ['converter', 'transformer', 'parser'],
            'dashboard': ['dashboard', 'visualizer', 'viewer'],
            'utility': ['util', 'helper', 'tools'],
            'cli': ['cli', 'command', 'interface'],
        }
        
        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category
        
        return 'general'
    
    def _parse_ast(self, content: str):
        """Parse AST for functions and classes"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                    })
                elif isinstance(node, ast.ClassDef):
                    self.classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [
                            n.name for n in node.body
                            if isinstance(n, ast.FunctionDef)
                        ],
                    })
            
            # Extract imports as dependencies
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.dependencies.append(node.module)
        
        except Exception as e:
            print(f"⚠️  AST parsing error: {e}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'file': str(self.file_path.name),
            'path': str(self.file_path),
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'category': self.category,
            'size_bytes': self.size,
            'size_kb': round(self.size / 1024, 2),
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'dependencies': list(set(self.dependencies)),
            'functions': self.functions,
            'classes': self.classes,
            'docstring': self.docstring,
            'hash': self._calculate_hash(),
        }
    
    def _calculate_hash(self) -> str:
        """Calculate file hash"""
        with open(self.file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()


class ToolRegistry:
    """
    Central tool registry and discovery system
    
    Features:
    - Automatic scanning
    - Metadata extraction
    - Category organization
    - Search and filtering
    - Usage tracking
    - Health monitoring
    """
    
    # Category definitions
    CATEGORIES = {
        'cache': 'Caching and memory optimization',
        'search': 'Search and retrieval',
        'ml': 'Machine learning and optimization',
        'analysis': 'Data analysis and reporting',
        'workflow': 'Workflow and orchestration',
        'collector': 'Data collection and scraping',
        'converter': 'Format conversion and parsing',
        'dashboard': 'Visualization and dashboards',
        'utility': 'Utilities and helpers',
        'cli': 'Command-line interfaces',
        'general': 'General purpose tools',
    }
    
    def __init__(self, tools_dir: Path = None):
        self.tools_dir = tools_dir or TOOLS_DIR
        self.registry_file = REGISTRY_DIR / 'registry.json'
        self.usage_file = REGISTRY_DIR / 'usage_stats.json'
        
        # Registry data
        self.tools: Dict[str, Dict] = {}
        self.usage_stats: Dict[str, Dict] = {}
        
        # Load existing registry
        self._load_registry()
    
    def _load_registry(self):
        """Load existing registry from disk"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tools = data.get('tools', {})
        
        if self.usage_file.exists():
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                self.usage_stats = json.load(f)
    
    def _save_registry(self):
        """Save registry to disk"""
        data = {
            'tools': self.tools,
            'last_updated': datetime.now().isoformat(),
            'total_tools': len(self.tools),
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _save_usage(self):
        """Save usage statistics"""
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_stats, f, indent=2)
    
    def scan(self, force: bool = False) -> Dict:
        """
        Scan tools directory and register all tools
        
        Args:
            force: Force re-scan even if already registered
        
        Returns:
            Scan results with added/updated/removed counts
        """
        print(f"\n🔍 Scanning tools directory: {self.tools_dir}\n")
        
        # Find all Python files
        python_files = list(self.tools_dir.glob('*.py'))
        
        results = {
            'scanned': len(python_files),
            'added': 0,
            'updated': 0,
            'removed': 0,
            'errors': 0,
        }
        
        current_files = set()
        
        for file_path in python_files:
            try:
                # Skip private files
                if file_path.name.startswith('_'):
                    continue
                
                current_files.add(file_path.name)
                
                # Create metadata
                metadata = ToolMetadata(file_path)
                tool_data = metadata.to_dict()
                
                # Check if already registered
                if file_path.name in self.tools:
                    # Check for changes
                    old_hash = self.tools[file_path.name].get('hash', '')
                    if old_hash != tool_data['hash']:
                        # Updated
                        self.tools[file_path.name] = tool_data
                        results['updated'] += 1
                    # else: unchanged
                else:
                    # New tool
                    self.tools[file_path.name] = tool_data
                    results['added'] += 1
                
                # Initialize usage stats
                if file_path.name not in self.usage_stats:
                    self.usage_stats[file_path.name] = {
                        'total_runs': 0,
                        'last_run': None,
                        'avg_execution_time_ms': 0,
                        'error_count': 0,
                    }
                
            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")
                results['errors'] += 1
        
        # Check for removed files
        registered_files = set(self.tools.keys())
        removed_files = registered_files - current_files
        
        for removed in removed_files:
            # Mark as removed (don't delete, keep history)
            if removed in self.tools:
                self.tools[removed]['status'] = 'removed'
                results['removed'] += 1
        
        # Save registry
        self._save_registry()
        self._save_usage()
        
        print(f"✅ Scan complete!")
        print(f"   Scanned: {results['scanned']} files")
        print(f"   Added: {results['added']} new tools")
        print(f"   Updated: {results['updated']} changed tools")
        print(f"   Removed: {results['removed']} missing tools")
        print(f"   Errors: {results['errors']}")
        
        return results
    
    def search(self, query: str, category: str = None) -> List[Dict]:
        """
        Search tools by name, description, or category
        
        Args:
            query: Search query
            category: Optional category filter
        
        Returns:
            List of matching tools
        """
        results = []
        query_lower = query.lower()
        
        for tool_name, tool_data in self.tools.items():
            # Skip removed tools
            if tool_data.get('status') == 'removed':
                continue
            
            # Category filter
            if category and tool_data.get('category') != category:
                continue
            
            # Search in name, description, docstring
            searchable = f"{tool_name} {tool_data.get('description', '')} {tool_data.get('docstring', '')}".lower()
            
            if query_lower in searchable or query == '*':
                results.append(tool_data)
        
        # Sort by relevance (exact match first)
        results.sort(key=lambda x: (
            0 if x['name'].lower() == query_lower else 1,
            x['name'],
        ))
        
        return results
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all tools in a category"""
        return [
            tool for tool in self.tools.values()
            if tool.get('category') == category and tool.get('status') != 'removed'
        ]
    
    def get_categories(self) -> Dict[str, int]:
        """Get category statistics"""
        categories = defaultdict(int)
        
        for tool_data in self.tools.values():
            if tool_data.get('status') != 'removed':
                categories[tool_data.get('category', 'general')] += 1
        
        return dict(categories)
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        active_tools = [
            t for t in self.tools.values()
            if t.get('status') != 'removed'
        ]
        
        total_size = sum(t.get('size_bytes', 0) for t in active_tools)
        
        return {
            'total_tools': len(active_tools),
            'total_size_kb': round(total_size / 1024, 2),
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'categories': self.get_categories(),
            'avg_size_kb': round(total_size / max(1, len(active_tools)) / 1024, 2),
            'last_updated': self.tools.get('last_updated', 'Never'),
        }
    
    def record_usage(self, tool_name: str, execution_time_ms: float = 0,
                    success: bool = True):
        """Record tool usage"""
        if tool_name not in self.usage_stats:
            self.usage_stats[tool_name] = {
                'total_runs': 0,
                'last_run': None,
                'avg_execution_time_ms': 0,
                'error_count': 0,
            }
        
        stats = self.usage_stats[tool_name]
        stats['total_runs'] += 1
        stats['last_run'] = datetime.now().isoformat()
        
        # Update average execution time
        old_avg = stats['avg_execution_time_ms']
        n = stats['total_runs']
        stats['avg_execution_time_ms'] = old_avg + (execution_time_ms - old_avg) / n
        
        if not success:
            stats['error_count'] += 1
        
        self._save_usage()
    
    def get_health(self) -> Dict:
        """Get tool health status"""
        health = {
            'healthy': [],
            'warnings': [],
            'errors': [],
        }
        
        for tool_name, tool_data in self.tools.items():
            if tool_data.get('status') == 'removed':
                continue
            
            # Check file exists
            tool_path = Path(tool_data.get('path', ''))
            if not tool_path.exists():
                health['errors'].append({
                    'tool': tool_name,
                    'issue': 'File missing',
                })
                continue
            
            # Check size (warn if too large)
            size_kb = tool_data.get('size_kb', 0)
            if size_kb > 50:
                health['warnings'].append({
                    'tool': tool_name,
                    'issue': f'Large file ({size_kb} KB)',
                })
            
            # Check last modified (warn if old)
            modified = datetime.fromisoformat(tool_data.get('modified', '2020-01-01'))
            age_days = (datetime.now() - modified).days
            if age_days > 90:
                health['warnings'].append({
                    'tool': tool_name,
                    'issue': f'Not updated in {age_days} days',
                })
            
            # Check usage stats
            usage = self.usage_stats.get(tool_name, {})
            error_rate = usage.get('error_count', 0) / max(1, usage.get('total_runs', 1))
            if error_rate > 0.1:
                health['warnings'].append({
                    'tool': tool_name,
                    'issue': f'High error rate ({error_rate:.1%})',
                })
            
            # If no issues, mark as healthy
            if not any(h['tool'] == tool_name for h in health['warnings'] + health['errors']):
                health['healthy'].append(tool_name)
        
        return health
    
    def export_report(self, output_file: Path = None) -> Path:
        """Export registry report"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = REGISTRY_DIR / f'registry_report_{timestamp}.json'
        
        report = {
            'generated': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'tools': self.tools,
            'usage': self.usage_stats,
            'health': self.get_health(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report exported to: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tool Registry")
    parser.add_argument('--scan', action='store_true', help='Scan tools directory')
    parser.add_argument('--search', type=str, help='Search tools')
    parser.add_argument('--category', type=str, help='Filter by category')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--health', action='store_true', help='Show health status')
    parser.add_argument('--export', action='store_true', help='Export report')
    parser.add_argument('--list', action='store_true', help='List all tools')
    args = parser.parse_args()
    
    registry = ToolRegistry()
    
    if args.scan:
        registry.scan(force=True)
    
    elif args.search:
        results = registry.search(args.search, args.category)
        print(f"\n🔍 Search results for '{args.search}':\n")
        for tool in results[:20]:
            print(f"  {tool['name']} ({tool['category']})")
            print(f"     {tool['description'][:80]}")
            print(f"     Size: {tool['size_kb']} KB\n")
        print(f"Total: {len(results)} tools\n")
    
    elif args.stats:
        stats = registry.get_stats()
        print("\n📊 Tool Registry Statistics")
        print("=" * 80)
        print(f"Total tools: {stats['total_tools']}")
        print(f"Total size: {stats['total_size_mb']} MB ({stats['total_size_kb']} KB)")
        print(f"Avg tool size: {stats['avg_size_kb']} KB")
        print(f"\nCategories:")
        for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count} tools")
    
    elif args.health:
        health = registry.get_health()
        print("\n🏥 Tool Health Status")
        print("=" * 80)
        print(f"✅ Healthy: {len(health['healthy'])} tools")
        print(f"⚠️  Warnings: {len(health['warnings'])} tools")
        print(f"❌ Errors: {len(health['errors'])} tools")
        
        if health['warnings']:
            print(f"\n⚠️  Warnings:")
            for w in health['warnings'][:10]:
                print(f"   {w['tool']}: {w['issue']}")
        
        if health['errors']:
            print(f"\n❌ Errors:")
            for e in health['errors']:
                print(f"   {e['tool']}: {e['issue']}")
    
    elif args.export:
        registry.export_report()
    
    elif args.list:
        categories = registry.get_categories()
        print("\n📚 Tool Categories")
        print("=" * 80)
        
        for category in sorted(categories.keys()):
            tools = registry.get_by_category(category)
            print(f"\n{category.upper()} ({len(tools)} tools):")
            for tool in sorted(tools, key=lambda x: x['name']):
                print(f"   - {tool['name']} ({tool['size_kb']} KB)")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
