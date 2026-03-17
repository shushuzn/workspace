#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smart Documentation Generator - Phase 4 Innovation
Automatically generates documentation from code and analysis
Features: API docs, README generation, usage examples, changelog

Usage:
    python smart_doc_generator.py --api 30-scripts-tools/
    python smart_doc_generator.py --readme
    python smart_doc_generator.py --changelog
    python smart_doc_generator.py --all
"""

import os
import sys
import ast
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DOCS_DIR = WORKSPACE / "15-docs"
API_DOCS = DOCS_DIR / "api-reference.md"
README_FILE = WORKSPACE / "README.md"
CHANGELOG_FILE = WORKSPACE / "CHANGELOG.md"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SmartDocGenerator:
    """Automatically generate documentation"""
    
    def __init__(self):
        self.modules = []
        self.functions = []
        self.classes = []
    
    def scan_directory(self, dir_path: Path, pattern: str = "*.py") -> List[Dict]:
        """Scan directory for Python modules"""
        print(f"[SCAN] Scanning {dir_path}...")
        
        py_files = list(dir_path.glob(pattern))
        modules = []
        
        for file_path in py_files:
            if file_path.name.startswith('test_'):
                continue
            
            module_info = self._analyze_module(file_path)
            if module_info:
                modules.append(module_info)
        
        self.modules = modules
        print(f"[OK] Found {len(modules)} modules")
        
        return modules
    
    def _analyze_module(self, file_path: Path) -> Dict:
        """Analyze a Python module"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            module_info = {
                'name': file_path.stem,
                'path': str(file_path.relative_to(WORKSPACE)),
                'description': self._extract_docstring(content),
                'functions': [],
                'classes': [],
                'imports': []
            }
            
            for node in ast.walk(tree):
                # Functions
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        func_info = {
                            'name': node.name,
                            'args': [arg.arg for arg in node.args.args if arg.arg != 'self'],
                            'docstring': ast.get_docstring(node) or '',
                            'line': node.lineno
                        }
                        module_info['functions'].append(func_info)
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': [n.name for n in node.body 
                                   if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')],
                        'line': node.lineno
                    }
                    module_info['classes'].append(class_info)
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        module_info['imports'].append(f"{module}.{alias.name}")
            
            return module_info
        
        except Exception as e:
            print(f"[WARN] Error analyzing {file_path}: {e}")
            return None
    
    def _extract_docstring(self, content: str) -> str:
        """Extract module-level docstring"""
        lines = content.split('\n')
        in_docstring = False
        docstring_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                    docstring_lines.append(stripped[3:])
                else:
                    docstring_lines.append(stripped[:-3])
                    break
            elif in_docstring:
                docstring_lines.append(stripped)
        
        return ' '.join(docstring_lines).strip()[:200]
    
    def generate_api_docs(self, output_path: Path = None) -> str:
        """Generate API reference documentation"""
        print("[GENERATE] API Reference Documentation...")
        
        if not self.modules:
            self.scan_directory(WORKSPACE / "30-scripts-tools")
        
        doc = f"""# API Reference

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Modules:** {len(self.modules)}

---

## Table of Contents

"""
        
        # Table of contents
        for module in sorted(self.modules, key=lambda x: x['name']):
            doc += f"- [{module['name']}](#{module['name'].lower()})\n"
        
        doc += "\n---\n\n"
        
        # Module details
        for module in sorted(self.modules, key=lambda x: x['name']):
            doc += f"## {module['name']}\n\n"
            doc += f"**Path:** `{module['path']}`\n\n"
            
            if module['description']:
                doc += f"{module['description']}\n\n"
            
            # Functions
            if module['functions']:
                doc += "### Functions\n\n"
                for func in module['functions'][:10]:  # Limit to 10 functions
                    args = ', '.join(func['args'])
                    doc += f"#### `{func['name']}({args})`\n\n"
                    if func['docstring']:
                        doc += f"{func['docstring'][:200]}\n\n"
            
            # Classes
            if module['classes']:
                doc += "### Classes\n\n"
                for cls in module['classes']:
                    methods = ', '.join(cls['methods'][:5])
                    doc += f"#### `{cls['name']}`\n\n"
                    if cls['docstring']:
                        doc += f"{cls['docstring'][:200]}\n\n"
                    doc += f"Methods: `{methods}`\n\n"
            
            doc += "---\n\n"
        
        # Save
        if output_path is None:
            DOCS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = API_DOCS
        
        output_path.write_text(doc, encoding='utf-8')
        print(f"[OK] Saved to {output_path}")
        
        return doc
    
    def generate_readme(self) -> str:
        """Generate README.md"""
        print("[GENERATE] README.md...")
        
        # Count tools
        scripts_dir = WORKSPACE / "30-scripts-tools"
        tool_count = len(list(scripts_dir.glob("*.py"))) if scripts_dir.exists() else 0
        
        # Get recent commits
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'],
                capture_output=True,
                text=True,
                cwd=str(WORKSPACE),
                timeout=10
            )
            recent_commits = result.stdout.strip().split('\n')
        except:
            recent_commits = []
        
        readme = f"""# OpenClaw Workspace

**AI Agent Workspace** - Autonomous Research & Automation System

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Overview

| Metric | Value |
|--------|-------|
| Total Tools | {tool_count} |
| Workspace | `D:\\OpenClaw\\workspace` |
| Git Repo | [obsidian-sync](https://github.com/shushuzn/obsidian-sync) |
| Dashboard | https://felixxii.xyz |

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Usage
```bash
# Run all tools
python 30-scripts-tools/openclaw-cli.py run all

# Check status
python 30-scripts-tools/openclaw-cli.py status

# Generate knowledge graph
python 30-scripts-tools/knowledge_graph_builder.py --build
```

---

## 📁 Directory Structure

```
workspace/
├── 00-09/          # Core configuration
├── 10-19/          # Knowledge & Memory
├── 20-29/          # Data & Reports
├── 30-39/          # Tools & Scripts
├── 40-49/          # Collectors
└── 90-99/          # Archive
```

---

## 🛠️ Key Tools

### Innovation Tools (Phase 4)
| Tool | Purpose | Status |
|------|---------|--------|
| knowledge_graph_builder.py | Auto knowledge extraction | ✅ |
| automation_orchestrator.py | Task orchestration | ✅ |
| smart_notification.py | Multi-channel notifications | ✅ |
| code_quality_reviewer.py | 6-dimension code analysis | ✅ |
| auto_test_generator.py | Auto test generation | ✅ |

### Core Tools
| Tool | Purpose |
|------|---------|
| cache_manager.py | Smart caching layer |
| self_healing.py | Auto error recovery |
| openclaw-cli.py | Unified CLI interface |
| feishu_notification.py | Feishu integration |
| local_qwen_inference.py | Local LLM inference |

---

## 📈 Recent Activity

"""
        
        if recent_commits:
            readme += "### Latest Commits\n\n"
            for commit in recent_commits[:5]:
                readme += f"- `{commit}`\n"
            readme += "\n"
        
        readme += f"""
---

## 🎯 7-Persona System

| Persona | Role | Trigger |
|---------|------|---------|
| Planner | Strategy & planning | Every response |
| Executor | Task execution | After planning |
| Critic | Quality review (≥85 pts) | After execution |
| Learner | Memory updates | After critic ≥85 |
| Coordinator | Rest & balance | Every 60-90 min |
| Innovator | Creative solutions | Continuous |
| Metacognition | System monitoring | Daily/Weekly |

---

## 📝 Documentation

- [API Reference](15-docs/api-reference.md)
- [CHANGELOG](CHANGELOG.md)
- [MEMORY.md](13-memory-记忆系统/MEMORY.md)

---

## 🤝 Contributing

1. Follow zero-error principle
2. Test before commit
3. Auto-generate tests
4. Update documentation

---

*Generated by Smart Documentation Generator (Phase 4 Innovation)*
"""
        
        README_FILE.write_text(readme, encoding='utf-8')
        print(f"[OK] Saved to {README_FILE}")
        
        return readme
    
    def generate_changelog(self) -> str:
        """Generate CHANGELOG.md"""
        print("[GENERATE] CHANGELOG.md...")
        
        import subprocess
        
        # Get all commits grouped by date
        try:
            result = subprocess.run(
                ['git', 'log', '--format=%ad|%s', '--date=short'],
                capture_output=True,
                text=True,
                cwd=str(WORKSPACE),
                timeout=30
            )
            
            commits_by_date = {}
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    date, message = line.split('|', 1)
                    if date not in commits_by_date:
                        commits_by_date[date] = []
                    commits_by_date[date].append(message)
        
        except Exception as e:
            print(f"[WARN] Could not get git log: {e}")
            commits_by_date = {}
        
        changelog = f"""# Changelog

All notable changes to this project will be documented in this file.

---

"""
        
        # Group by version (date-based)
        sorted_dates = sorted(commits_by_date.keys(), reverse=True)[:20]  # Last 20 days
        
        for date in sorted_dates:
            commits = commits_by_date[date]
            
            # Categorize commits
            features = [c for c in commits if 'feat' in c.lower() or 'add' in c.lower() or 'create' in c.lower()]
            fixes = [c for c in commits if 'fix' in c.lower() or 'repair' in c.lower()]
            improvements = [c for c in commits if 'improve' in c.lower() or 'optimize' in c.lower() or 'phase' in c.lower()]
            docs = [c for c in commits if 'doc' in c.lower() or 'readme' in c.lower()]
            other = [c for c in commits if c not in features + fixes + improvements + docs]
            
            changelog += f"## [{date}]\n\n"
            
            if features:
                changelog += "### ✨ Features\n\n"
                for commit in features[:5]:
                    changelog += f"- {commit}\n"
                changelog += "\n"
            
            if fixes:
                changelog += "### 🐛 Bug Fixes\n\n"
                for commit in fixes[:5]:
                    changelog += f"- {commit}\n"
                changelog += "\n"
            
            if improvements:
                changelog += "### 🚀 Improvements\n\n"
                for commit in improvements[:5]:
                    changelog += f"- {commit}\n"
                changelog += "\n"
            
            if docs:
                changelog += "### 📚 Documentation\n\n"
                for commit in docs[:5]:
                    changelog += f"- {commit}\n"
                changelog += "\n"
            
            if other:
                changelog += "### 📝 Other\n\n"
                for commit in other[:5]:
                    changelog += f"- {commit}\n"
                changelog += "\n"
        
        CHANGELOG_FILE.write_text(changelog, encoding='utf-8')
        print(f"[OK] Saved to {CHANGELOG_FILE}")
        
        return changelog
    
    def generate_all(self):
        """Generate all documentation"""
        print("=" * 60)
        print("Smart Documentation Generator - Generating All Docs")
        print("=" * 60)
        
        self.generate_api_docs()
        self.generate_readme()
        self.generate_changelog()
        
        print("\n" + "=" * 60)
        print("Documentation Generation Complete!")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Smart Documentation Generator')
    parser.add_argument('--api', type=str, help='Generate API docs for directory')
    parser.add_argument('--readme', action='store_true', help='Generate README.md')
    parser.add_argument('--changelog', action='store_true', help='Generate CHANGELOG.md')
    parser.add_argument('--all', action='store_true', help='Generate all documentation')
    args = parser.parse_args()
    
    generator = SmartDocGenerator()
    
    if args.api:
        dir_path = Path(args.api)
        generator.scan_directory(dir_path)
        generator.generate_api_docs()
    
    if args.readme:
        generator.generate_readme()
    
    if args.changelog:
        generator.generate_changelog()
    
    if args.all:
        generator.generate_all()
    
    if not any([args.api, args.readme, args.changelog, args.all]):
        parser.print_help()


if __name__ == "__main__":
    main()
