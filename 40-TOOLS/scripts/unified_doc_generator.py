#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Doc Generator - Generate unified documentation

Features:
- Tool documentation
- API reference
- Usage examples
- README generation
- Index creation
- Search index
"""

import os
import sys
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
DOCS_DIR = WORKSPACE / '15-docs 文档'
DOCS_DIR.mkdir(parents=True, exist_ok=True)

class DocGenerator:
    """Generate documentation"""
    
    def __init__(self, tools_dir: Path):
        self.tools_dir = tools_dir
        self.tools = []
    
    def scan_tools(self) -> List[Dict]:
        """Scan all tools"""
        tools = []
        
        for py_file in sorted(self.tools_dir.glob('*.py')):
            if py_file.name.startswith('_'):
                continue
            
            tool_info = self._extract_info(py_file)
            if tool_info:
                tools.append(tool_info)
        
        self.tools = tools
        return tools
    
    def _extract_info(self, file_path: Path) -> Optional[Dict]:
        """Extract tool information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Get module docstring
            docstring = ast.get_docstring(tree) or ''
            
            # Get description (first line)
            description = docstring.split('\n')[0].strip() if docstring else 'No description'
            
            # Get full docstring
            full_doc = docstring
            
            # Extract classes
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = ast.get_docstring(node) or ''
                    classes.append({
                        'name': node.name,
                        'doc': class_doc.split('\n')[0] if class_doc else '',
                        'methods': [
                            n.name for n in node.body
                            if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')
                        ]
                    })
            
            # Extract functions
            functions = [
                node.name for node in tree.body
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')
            ]
            
            # Extract CLI arguments
            cli_args = []
            if 'argparse' in content:
                # Simple extraction
                if '--demo' in content:
                    cli_args.append('--demo')
                if '--analyze' in content:
                    cli_args.append('--analyze')
                if '--report' in content:
                    cli_args.append('--report')
            
            return {
                'name': file_path.stem,
                'file': file_path.name,
                'path': str(file_path),
                'description': description,
                'full_doc': full_doc,
                'classes': classes,
                'functions': functions,
                'cli_args': cli_args,
                'size_kb': round(file_path.stat().st_size / 1024, 2),
                'lines': len(content.splitlines()),
                'has_main': 'if __name__ ==' in content,
            }
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
            return None
    
    def generate_tool_docs(self, output_dir: Path = None) -> List[str]:
        """Generate documentation for each tool"""
        output_dir = output_dir or (DOCS_DIR / 'tools')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated = []
        
        for tool in self.tools:
            doc_content = self._generate_single_tool_doc(tool)
            
            output_file = output_dir / f"{tool['name']}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            generated.append(str(output_file))
        
        return generated
    
    def _generate_single_tool_doc(self, tool: Dict) -> str:
        """Generate documentation for single tool"""
        doc = f"""# {tool['name']}

**File:** `{tool['file']}`  
**Size:** {tool['size_kb']} KB | **Lines:** {tool['lines']}  
**Description:** {tool['description']}

---

## Overview

{tool['full_doc']}

"""
        
        # Classes
        if tool['classes']:
            doc += "## Classes\n\n"
            for cls in tool['classes']:
                doc += f"### {cls['name']}\n\n"
                doc += f"{cls['doc']}\n\n"
                
                if cls['methods']:
                    doc += "**Methods:**\n"
                    for method in cls['methods']:
                        doc += f"- `{method}()`\n"
                    doc += "\n"
        
        # Functions
        if tool['functions']:
            doc += "## Functions\n\n"
            for func in tool['functions']:
                doc += f"- `{func}()`\n"
            doc += "\n"
        
        # CLI
        if tool['cli_args']:
            doc += "## CLI Usage\n\n"
            doc += f"```bash\npython {tool['file']} "
            doc += " ".join(tool['cli_args'][:3])
            doc += "\n```\n\n"
        
        return doc
    
    def generate_readme(self, output_file: Path = None) -> str:
        """Generate main README"""
        output_file = output_file or (DOCS_DIR / 'TOOLS-README.md')
        
        # Group tools by category
        categories = defaultdict(list)
        for tool in self.tools:
            # Simple categorization
            name_lower = tool['name'].lower()
            if 'deploy' in name_lower or 'ci' in name_lower:
                categories['Deployment'].append(tool)
            elif 'analyze' in name_lower or 'analytics' in name_lower:
                categories['Analysis'].append(tool)
            elif 'auto' in name_lower or 'schedule' in name_lower:
                categories['Automation'].append(tool)
            elif 'monitor' in name_lower or 'health' in name_lower:
                categories['Monitoring'].append(tool)
            elif 'cache' in name_lower or 'redis' in name_lower:
                categories['Data'].append(tool)
            elif 'optim' in name_lower or 'enhance' in name_lower:
                categories['Optimization'].append(tool)
            else:
                categories['Other'].append(tool)
        
        # Generate README
        readme = f"""# Tools Documentation

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Total Tools:** {len(self.tools)}  
**Total Size:** {sum(t['size_kb'] for t in self.tools):.1f} KB

---

## Overview

This directory contains {len(self.tools)} tools for automation, analysis, deployment, and more.

## Categories

"""
        
        for category, tools in sorted(categories.items()):
            readme += f"### {category} ({len(tools)} tools)\n\n"
            for tool in tools:
                readme += f"- **[{tool['name']}](tools/{tool['name']}.md)** - {tool['description']}\n"
            readme += "\n"
        
        # Quick reference table
        readme += """## Quick Reference

| Tool | Size | Lines | Description |
|------|------|-------|-------------|
"""
        
        for tool in sorted(self.tools, key=lambda t: t['name']):
            readme += f"| [{tool['name']}](tools/{tool['name']}.md) | {tool['size_kb']} KB | {tool['lines']} | {tool['description'][:50]}... |\n"
        
        readme += f"""
---

*Generated by Unified Doc Generator on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        return str(output_file)
    
    def generate_index(self, output_file: Path = None) -> Dict:
        """Generate search index"""
        output_file = output_file or (DOCS_DIR / 'tools_index.json')
        
        index = {
            'generated': datetime.now().isoformat(),
            'total_tools': len(self.tools),
            'tools': [
                {
                    'name': tool['name'],
                    'description': tool['description'],
                    'keywords': self._extract_keywords(tool),
                    'path': f"tools/{tool['name']}.md",
                }
                for tool in self.tools
            ],
        }
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        return index
    
    def _extract_keywords(self, tool: Dict) -> List[str]:
        """Extract keywords from tool"""
        keywords = []
        
        # From name
        keywords.extend(tool['name'].lower().split('_'))
        
        # From description
        keywords.extend(tool['description'].lower().split())
        
        # From classes and functions
        for cls in tool['classes']:
            keywords.append(cls['name'].lower())
        
        keywords.extend([f.lower() for f in tool['functions']])
        
        return list(set(keywords))[:20]  # Limit to 20
    
    def generate_all(self) -> Dict:
        """Generate all documentation"""
        print("\n📝 GENERATING DOCUMENTATION")
        print("=" * 60)
        
        # Scan tools
        print("\n🔍 Scanning tools...")
        self.scan_tools()
        print(f"✅ Found {len(self.tools)} tools")
        
        # Generate tool docs
        print("\n📄 Generating tool documentation...")
        tool_docs = self.generate_tool_docs()
        print(f"✅ Generated {len(tool_docs)} tool docs")
        
        # Generate README
        print("\n📋 Generating README...")
        readme = self.generate_readme()
        print(f"✅ Generated README: {readme}")
        
        # Generate index
        print("\n🔖 Generating search index...")
        index = self.generate_index()
        print(f"✅ Generated index with {len(index['tools'])} entries")
        
        return {
            'tool_docs': tool_docs,
            'readme': readme,
            'index': index,
            'total_tools': len(self.tools),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified Doc Generator")
    parser.add_argument('--generate', action='store_true', help='Generate all docs')
    parser.add_argument('--readme', action='store_true', help='Generate README only')
    parser.add_argument('--index', action='store_true', help='Generate index only')
    parser.add_argument('--list', action='store_true', help='List tools')
    args = parser.parse_args()
    
    generator = DocGenerator(TOOLS_DIR)
    
    if args.generate:
        result = generator.generate_all()
        print(f"\n✅ Documentation generation complete!")
        print(f"   Tool docs: {len(result['tool_docs'])}")
        print(f"   README: {result['readme']}")
        print(f"   Index entries: {len(result['index']['tools'])}")
    
    elif args.readme:
        generator.scan_tools()
        readme = generator.generate_readme()
        print(f"✅ README generated: {readme}")
    
    elif args.index:
        generator.scan_tools()
        index = generator.generate_index()
        print(f"✅ Index generated with {len(index['tools'])} entries")
    
    elif args.list:
        generator.scan_tools()
        print(f"\n📋 TOOLS ({len(generator.tools)} total)")
        print("=" * 60)
        for tool in sorted(generator.tools, key=lambda t: t['name']):
            print(f"{tool['name']:30} - {tool['description'][:50]}")
        print("=" * 60)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
