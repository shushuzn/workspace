#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation Generator - Automated Documentation Generation
Features: API docs, README generation, usage examples, inline comments extraction

Usage:
    python doc_generator.py --api
    python doc_generator.py --readme
    python doc_generator.py --examples
    python doc_generator.py --all
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import inspect

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class FunctionDoc:
    """Function documentation"""
    name: str
    args: List[str]
    returns: str
    description: str
    examples: List[str]


@dataclass
class ClassDoc:
    """Class documentation"""
    name: str
    methods: List[FunctionDoc]
    attributes: List[str]
    description: str


@dataclass
class ModuleDoc:
    """Module documentation"""
    name: str
    description: str
    functions: List[FunctionDoc]
    classes: List[ClassDoc]
    constants: List[str]


class DocumentationGenerator:
    """Automated documentation generation"""
    
    def __init__(self):
        self.docs_dir = WORKSPACE / "15-docs" / "generated"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        self.api_dir = self.docs_dir / "api"
        self.api_dir.mkdir(parents=True, exist_ok=True)
        
        self.examples_dir = self.docs_dir / "examples"
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        
        self.docs_index = self.docs_dir / "index.json"
        self.docs = []
        
        self.load_index()
    
    def load_index(self):
        """Load docs index"""
        if self.docs_index.exists():
            with open(self.docs_index, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.docs = data.get('docs', [])
    
    def save_index(self):
        """Save docs index"""
        with open(self.docs_index, 'w', encoding='utf-8') as f:
            json.dump({
                'docs': self.docs,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def extract_docstring(self, node) -> str:
        """Extract docstring from AST node"""
        docstring = ast.get_docstring(node)
        return docstring or ""
    
    def parse_function(self, node: ast.FunctionDef) -> FunctionDoc:
        """Parse function definition"""
        args = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        docstring = self.extract_docstring(node)
        
        # Extract examples from docstring
        examples = []
        if 'Example:' in docstring or 'Examples:' in docstring:
            example_match = re.search(r'Example[s]?:\s*```(.*?)```', docstring, re.DOTALL)
            if example_match:
                examples = [example_match.group(1).strip()]
        
        return FunctionDoc(
            name=node.name,
            args=args,
            returns='Unknown',
            description=docstring.split('\n\n')[0] if docstring else "",
            examples=examples
        )
    
    def parse_class(self, node: ast.ClassDef) -> ClassDoc:
        """Parse class definition"""
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self.parse_function(item))
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        docstring = self.extract_docstring(node)
        
        return ClassDoc(
            name=node.name,
            methods=methods,
            attributes=attributes,
            description=docstring.split('\n\n')[0] if docstring else ""
        )
    
    def parse_module(self, filepath: Path) -> ModuleDoc:
        """Parse Python module"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            functions = []
            classes = []
            constants = []
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        functions.append(self.parse_function(node))
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith('_'):
                        classes.append(self.parse_class(node))
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constants.append(target.id)
            
            description = ast.get_docstring(tree) or ""
            
            return ModuleDoc(
                name=filepath.stem,
                description=description.split('\n\n')[0] if description else "",
                functions=functions,
                classes=classes,
                constants=constants
            )
        
        except Exception as e:
            print(f"  ⚠️  Failed to parse {filepath.name}: {e}")
            return None
    
    def generate_api_docs(self, target_dir: Path = None) -> int:
        """Generate API documentation"""
        print("\n" + "="*60)
        print(" Generating API Documentation")
        print("="*60 + "\n")
        
        if target_dir is None:
            target_dir = WORKSPACE / "30-scripts-tools"
        
        modules_documented = 0
        
        for py_file in target_dir.glob("*.py"):
            if py_file.name.startswith('test_') or py_file.name.startswith('_'):
                continue
            
            print(f"  Processing {py_file.name}...")
            
            module_doc = self.parse_module(py_file)
            
            if not module_doc:
                continue
            
            # Generate Markdown
            md_content = f"""# {module_doc.name}

**Module:** `{module_doc.name}.py`  
**Description:** {module_doc.description}

---

## Functions

"""
            
            for func in module_doc.functions:
                args_str = ', '.join(func.args)
                md_content += f"""### `{func.name}({args_str})`

{func.description}

**Parameters:**
"""
                for arg in func.args:
                    md_content += f"- `{arg}`\n"
                
                if func.examples:
                    md_content += f"""
**Example:**
```python
{func.examples[0]}
```
"""
                
                md_content += "\n---\n\n"
            
            if module_doc.classes:
                md_content += "## Classes\n\n"
                
                for cls in module_doc.classes:
                    md_content += f"""### `{cls.name}`

{cls.description}

**Attributes:** {', '.join(cls.attributes) if cls.attributes else 'None'}

**Methods:**
"""
                    for method in cls.methods:
                        md_content += f"- `{method.name}({', '.join(method.args)})`\n"
                    
                    md_content += "\n---\n\n"
            
            if module_doc.constants:
                md_content += f"""## Constants

{', '.join(f"`{c}`" for c in module_doc.constants)}

"""
            
            # Save
            doc_file = self.api_dir / f"{module_doc.name}.md"
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            modules_documented += 1
            print(f"  ✅ {doc_file.name}")
        
        # Generate index
        self.generate_api_index()
        
        print(f"\n✅ Generated {modules_documented} API docs\n")
        
        return modules_documented
    
    def generate_api_index(self):
        """Generate API index"""
        index_content = """# API Documentation Index

**Generated:** {timestamp}

## Modules

| Module | Functions | Classes | Constants |
|--------|-----------|---------|-----------|
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        for doc_file in sorted(self.api_dir.glob("*.md")):
            module_doc = self.parse_module(WORKSPACE / "30-scripts-tools" / f"{doc_file.stem}.py")
            
            if module_doc:
                index_content += f"| [{doc_file.stem}]({doc_file.name}) | {len(module_doc.functions)} | {len(module_doc.classes)} | {len(module_doc.constants)} |\n"
        
        index_content += """
---

*Generated by Documentation Generator v1.0*
"""
        
        index_file = self.api_dir / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
    
    def generate_readme(self) -> str:
        """Generate README for project"""
        print("\n" + "="*60)
        print(" Generating README")
        print("="*60 + "\n")
        
        # Count tools
        tools_dir = WORKSPACE / "30-scripts-tools"
        tools_count = len(list(tools_dir.glob("*.py"))) - len(list(tools_dir.glob("test_*.py")))
        
        # Count workflows
        workflows_dir = WORKSPACE / "30-scripts-tools" / "workflows"
        workflows_count = len(list(workflows_dir.glob("*.json"))) if workflows_dir.exists() else 0
        
        readme_content = f"""# OpenClaw Workspace

**AI Agent Workspace** - Automated Research & Development System

**Version:** 5.0  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
**Tools:** {tools_count} Python scripts  
**Workflows:** {workflows_count} automated workflows

---

## Overview

OpenClaw is an autonomous AI agent workspace designed for automated research, data collection, analysis, and self-improvement. The system features:

- **Multi-Source Data Collection** - arXiv, GitHub, Medium, RSS feeds
- **Automated Analysis** - Local LLM (Qwen2.5-1.5B), sentiment analysis, quality scoring
- **Knowledge Management** - Knowledge graph, memory system, lesson extraction
- **Workflow Automation** - DAG-based orchestration, parallel execution
- **Self-Improvement** - Automated testing, code analysis, performance optimization
- **7-Persona System** - Planner, Executor, Critic, Learner, Coordinator, Innovator, Meta-Cognition

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/shushuzn/obsidian-sync.git
cd workspace

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Run unified CLI
python openclaw.py --help

# Collect data
python openclaw.py collect arxiv --limit 10

# Analyze papers
python openclaw.py analyze paper.pdf

# Run workflow
python openclaw.py workflow run daily_brief

# Generate report
python openclaw.py report daily
```

---

## Tools

### Data Collection (40-50-collectors/)
- `arxiv_collector.py` - arXiv paper collection
- `github_collector.py` - GitHub trending repos
- `medium_collector.py` - Medium articles
- `rss_collector.py` - RSS feed aggregation

### Analysis (30-scripts-tools/)
- `local_llm_analyzer.py` - Local LLM analysis (Qwen2.5-1.5B)
- `paper_analyzer.py` - Paper summarization
- `code_reviewer.py` - Code quality analysis
- `sentiment_analyzer.py` - Sentiment analysis

### Workflow (30-scripts-tools/)
- `workflow_engine.py` - DAG-based workflow engine
- `workflow_enhancer.py` - Workflow visualization & optimization
- `automation_orchestrator.py` - Central orchestration

### Knowledge (13-memory-记忆系统/)
- `kg_builder.py` - Knowledge graph construction
- `kg_enhancer.py` - Knowledge graph enhancement
- `memory_maintenance.py` - Memory system maintenance

### Self-Improvement
- `self_iteration.py` - Self-iteration engine
- `test_enhancer.py` - Automated testing
- `auto_optimizer.py` - Performance optimization
- `security_auditor.py` - Security auditing

---

## Workflows

### Built-in Workflows

| Workflow | Steps | Description |
|----------|-------|-------------|
| `daily_brief` | 8 | Daily data collection + analysis |
| `security_audit` | 4 | Security scanning + reporting |
| `self_iteration` | 6 | Self-improvement cycle |
| `report_gen` | 5 | Multi-format report generation |

### Running Workflows

```bash
# List workflows
python workflow_enhancer.py --list

# Visualize workflow
python workflow_enhancer.py --visualize daily_brief

# Execute workflow
python workflow_enhancer.py --execute daily_brief
```

---

## Configuration

### Environment Variables

```bash
# API Keys
OPENAI_API_KEY=sk-...
FEISHU_APP_ID=cli_...
FEISHU_APP_SECRET=...

# Local LLM
LOCAL_LLM_MODEL=qwen2.5:1.5b
LOCAL_LLM_BACKEND=ollama

# Paths
WORKSPACE_DIR=D:\\OpenClaw\\workspace
```

### Configuration File

Edit `00-09-core-config/config.json`:

```json
{{
  "system": {{
    "timezone": "Asia/Hong_Kong",
    "debug": false
  }},
  "cache": {{
    "default_ttl": 3600,
    "max_memory_items": 1000
  }},
  "automation": {{
    "self_iteration_interval": 30,
    "daily_brief_time": "07:00"
  }}
}}
```

---

## Architecture

```
workspace/
├── 00-09-core-config/     # System configuration
├── 10-19-knowledge/       # Knowledge base
│   ├── 13-memory-记忆系统/  # Memory system
│   └── 15-docs/           # Documentation
├── 20-data-reports/       # Data & reports
├── 30-scripts-tools/      # Tools & scripts
├── 40-50-collectors/      # Data collectors
└── 90-99-archive/         # Archive
```

---

## Automation

### Scheduled Tasks

| Time | Task | Description |
|------|------|-------------|
| 07:00 | Daily Brief | Data collection + analysis |
| 06:00 | Security Audit | Security scanning |
| */30 min | Self-Iteration | Self-improvement cycle |
| */30 min | Health Check | System health monitoring |

### HEARTBEAT Configuration

Edit `HEARTBEAT.md` to configure automated tasks:

```yaml
- time: "0 7 * * *"
  workflow: daily_brief
  description: "Daily brief generation"

- time: "0 6 * * *"
  workflow: security_audit
  description: "Daily security audit"
```

---

## Monitoring

### Unified Monitor

```bash
# Start monitor
python unified_monitor.py --start --port 8088

# Access dashboard
http://localhost:8088
```

### System Health

- **CPU:** Real-time monitoring
- **Memory:** Usage tracking
- **Disk:** Space monitoring
- **Network:** I/O statistics

---

## Development

### Running Tests

```bash
# Generate tests
python test_enhancer.py --generate

# Run tests
python test_enhancer.py --run

# Coverage analysis
python test_enhancer.py --coverage
```

### Code Quality

```bash
# Security audit
python security_auditor.py --scan

# Performance analysis
python performance_analyzer.py --analyze
```

---

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

---

## License

MIT License

---

## Contact

- **GitHub:** https://github.com/shushuzn/obsidian-sync
- **Website:** https://felixxii.xyz

---

*Generated by Documentation Generator v1.0*
"""
        
        readme_file = WORKSPACE / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  ✅ README.md generated\n")
        
        return readme_file
    
    def generate_examples(self) -> int:
        """Generate usage examples"""
        print("\n" + "="*60)
        print(" Generating Examples")
        print("="*60 + "\n")
        
        examples = {
            'data_collection.md': """# Data Collection Examples

## Collect arXiv Papers

```bash
# Collect latest papers
python openclaw.py collect arxiv --limit 10

# Collect specific category
python openclaw.py collect arxiv --category cs.AI --limit 20

# Collect with keywords
python openclaw.py collect arxiv --keywords "large language model" --limit 10
```

## Collect GitHub Trending

```bash
# Collect trending repos
python openclaw.py collect github --language Python

# Collect specific topic
python openclaw.py collect github --topic "machine-learning"
```

## Collect Medium Articles

```bash
# Collect articles
python openclaw.py collect medium --tag "artificial-intelligence"

# Collect from publication
python openclaw.py collect medium --publication "towards-data-science"
```
""",
            
            'analysis.md': """# Analysis Examples

## Analyze Paper

```bash
# Analyze PDF paper
python openclaw.py analyze paper.pdf

# Analyze with custom model
python openclaw.py analyze paper.pdf --model qwen2.5:1.5b

# Analyze arXiv ID
python openclaw.py analyze --arxiv 2301.12345
```

## Code Review

```bash
# Review single file
python openclaw.py review script.py

# Review directory
python openclaw.py review ./30-scripts-tools/

# Review with security focus
python openclaw.py review ./ --security
```

## Sentiment Analysis

```bash
# Analyze text
python openclaw.py sentiment "This is great!"

# Analyze file
python openclaw.py sentiment --file reviews.txt
```
""",
            
            'workflow.md': """# Workflow Examples

## List Workflows

```bash
python workflow_enhancer.py --list
```

## Visualize Workflow

```bash
# ASCII visualization
python workflow_enhancer.py --visualize daily_brief

# Show parallel groups
python workflow_enhancer.py --visualize daily_brief --parallel
```

## Execute Workflow

```bash
# Simulate execution
python workflow_enhancer.py --execute daily_brief --simulate

# Real execution
python workflow_enhancer.py --execute daily_brief
```

## Analyze Workflow

```bash
# Analyze performance
python workflow_enhancer.py --analyze daily_brief

# Get optimization suggestions
python workflow_enhancer.py --optimize daily_brief
```
""",
            
            'self_improvement.md': """# Self-Improvement Examples

## Run Self-Iteration

```bash
# Full cycle
python self_iter_cli.py iterate

# Analyze only
python self_iter_cli.py analyze

# Plan improvements
python self_iter_cli.py plan
```

## Run Tests

```bash
# Generate tests
python test_enhancer.py --generate

# Run tests
python test_enhancer.py --run

# Coverage analysis
python test_enhancer.py --coverage

# Generate report
python test_enhancer.py --report
```

## Performance Optimization

```bash
# Analyze bottlenecks
python performance_analyzer.py --analyze

# Auto-optimize
python auto_optimizer.py --optimize
```

## Security Audit

```bash
# Scan codebase
python security_auditor.py --scan

# Check secrets
python security_auditor.py --secrets

# Generate report
python security_auditor.py --report
```
"""
        }
        
        examples_generated = 0
        
        for filename, content in examples.items():
            example_file = self.examples_dir / filename
            
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            examples_generated += 1
            print(f"  ✅ {filename}")
        
        print(f"\n✅ Generated {examples_generated} example files\n")
        
        return examples_generated
    
    def generate_all(self):
        """Generate all documentation"""
        print("\n" + "="*60)
        print(" Generating All Documentation")
        print("="*60 + "\n")
        
        self.generate_api_docs()
        self.generate_readme()
        self.generate_examples()
        
        print("\n" + "="*60)
        print(" Documentation Complete")
        print("="*60)
        print(f"  API Docs: {len(list(self.api_dir.glob('*.md')))}")
        print(f"  Examples: {len(list(self.examples_dir.glob('*.md')))}")
        print(f"  README: ✅")
        print("="*60 + "\n")
    
    def get_statistics(self) -> Dict:
        """Get documentation statistics"""
        return {
            'api_docs': len(list(self.api_dir.glob('*.md'))),
            'examples': len(list(self.examples_dir.glob('*.md'))),
            'readme': (WORKSPACE / "README.md").exists()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Generator')
    parser.add_argument('--api', action='store_true', help='Generate API docs')
    parser.add_argument('--readme', action='store_true', help='Generate README')
    parser.add_argument('--examples', action='store_true', help='Generate examples')
    parser.add_argument('--all', action='store_true', help='Generate all')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()
    
    generator = DocumentationGenerator()
    
    if args.api:
        generator.generate_api_docs()
    
    elif args.readme:
        generator.generate_readme()
    
    elif args.examples:
        generator.generate_examples()
    
    elif args.all:
        generator.generate_all()
    
    elif args.stats:
        stats = generator.get_statistics()
        print(json.dumps(stats, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
