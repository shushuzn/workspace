#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Context Database - 上下文数据库原型

Filesystem-based context management for AI Agents.
Inspired by OpenViking (https://github.com/volcengine/OpenViking)

Features:
- Tool Registry (138+ tools)
- Context Hierarchy (3 levels)
- Skills Library
- Self-Evolution Mechanism

Author: OpenClaw Innovator Agent
Date: 2026-03-16
Version: 0.1 (Prototype)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


@dataclass
class Tool:
    """Tool metadata"""
    name: str
    path: str
    category: str
    description: str
    lines: int
    size_kb: float
    last_modified: str
    usage_count: int = 0
    success_rate: float = 100.0


@dataclass
class Context:
    """Context metadata"""
    id: str
    name: str
    level: int  # 1=task, 2=session, 3=project
    tools: List[str]
    memories: List[str]
    created: str
    updated: str


@dataclass
class Skill:
    """Skill definition"""
    name: str
    description: str
    tools: List[str]
    workflow: List[str]
    examples: List[str]


class ContextDB:
    """Context Database for OpenClaw"""
    
    def __init__(self, base_path: str = "./context"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.tools_dir = self.base_path / "tools"
        self.contexts_dir = self.base_path / "contexts"
        self.skills_dir = self.base_path / "skills"
        
        for dir_path in [self.tools_dir, self.contexts_dir, self.skills_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Index files
        self.tool_index = self.base_path / "tool_index.json"
        self.context_index = self.base_path / "context_index.json"
        self.skills_index = self.base_path / "skills_index.json"
        
        # Load or initialize
        self.tools = self._load_tools()
        self.contexts = self._load_contexts()
        self.skills = self._load_skills()
    
    def _load_tools(self) -> Dict[str, Tool]:
        """Load tool registry"""
        if self.tool_index.exists():
            with open(self.tool_index, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: Tool(**v) for k, v in data.items()}
        
        # Scan workspace for tools
        tools = {}
        workspace = Path('D:/OpenClaw/workspace')
        
        # Scan 30-scripts-tools
        tools_dir = workspace / '30-scripts-tools'
        if tools_dir.exists():
            for py_file in tools_dir.glob('*.py'):
                if py_file.name.startswith('_'):
                    continue
                
                tool = Tool(
                    name=py_file.stem,
                    path=str(py_file.relative_to(workspace)),
                    category='tools',
                    description=py_file.stem.replace('_', ' ').title(),
                    lines=py_file.read_text(encoding='utf-8').count('\n') + 1,
                    size_kb=py_file.stat().st_size / 1024,
                    last_modified=datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
                )
                tools[tool.name] = tool
        
        # Save index
        self._save_tool_index(tools)
        return tools
    
    def _save_tool_index(self, tools: Dict[str, Tool]):
        """Save tool index"""
        data = {k: asdict(v) for k, v in tools.items()}
        with open(self.tool_index, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_contexts(self) -> Dict[str, Context]:
        """Load context index"""
        if self.context_index.exists():
            with open(self.context_index, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: Context(**v) for k, v in data.items()}
        return {}
    
    def _load_skills(self) -> Dict[str, Skill]:
        """Load skills index"""
        if self.skills_index.exists():
            with open(self.skills_index, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: Skill(**v) for k, v in data.items()}
        return {}
    
    def register_tool(self, tool_name: str, category: str = 'auto'):
        """Register a tool"""
        workspace = Path('D:/OpenClaw/workspace')
        tool_path = workspace / '30-scripts-tools' / f'{tool_name}.py'
        
        if not tool_path.exists():
            print(f"⚠️  Tool not found: {tool_name}")
            return False
        
        tool = Tool(
            name=tool_name,
            path=str(tool_path.relative_to(workspace)),
            category=category,
            description=tool_name.replace('_', ' ').title(),
            lines=tool_path.read_text(encoding='utf-8').count('\n') + 1,
            size_kb=tool_path.stat().st_size / 1024,
            last_modified=datetime.fromtimestamp(tool_path.stat().st_mtime).isoformat()
        )
        
        self.tools[tool_name] = tool
        self._save_tool_index(self.tools)
        
        print(f"✅ Registered tool: {tool_name}")
        return True
    
    def create_context(self, name: str, level: int, tools: List[str] = None):
        """Create a new context"""
        context_id = f"ctx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        context = Context(
            id=context_id,
            name=name,
            level=level,
            tools=tools or [],
            memories=[],
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat()
        )
        
        self.contexts[context_id] = context
        self._save_context_index()
        
        print(f"✅ Created context: {name} (Level {level})")
        return context_id
    
    def _save_context_index(self):
        """Save context index"""
        data = {k: asdict(v) for k, v in self.contexts.items()}
        with open(self.context_index, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_context(self, context_name: str) -> Optional[Context]:
        """Load context by name"""
        for ctx in self.contexts.values():
            if ctx.name == context_name:
                print(f"📂 Loaded context: {context_name}")
                print(f"   Tools: {len(ctx.tools)}")
                print(f"   Memories: {len(ctx.memories)}")
                return ctx
        
        print(f"⚠️  Context not found: {context_name}")
        return None
    
    def get_skills(self, skill_name: str) -> Optional[Skill]:
        """Get skill by name"""
        if skill_name in self.skills:
            skill = self.skills[skill_name]
            print(f"🎯 Skill: {skill_name}")
            print(f"   Tools: {', '.join(skill.tools)}")
            print(f"   Workflow: {' → '.join(skill.workflow)}")
            return skill
        
        print(f"⚠️  Skill not found: {skill_name}")
        return None
    
    def search_tools(self, query: str) -> List[Tool]:
        """Search tools by name/description"""
        results = []
        query_lower = query.lower()
        
        for tool in self.tools.values():
            if query_lower in tool.name.lower() or query_lower in tool.description.lower():
                results.append(tool)
        
        print(f"🔍 Found {len(results)} tools matching '{query}'")
        for tool in results[:5]:  # Show top 5
            print(f"   - {tool.name} ({tool.lines} lines, {tool.size_kb:.1f} KB)")
        
        return results
    
    def evolve(self):
        """Self-evolution mechanism"""
        print(f"\n🧬 Running self-evolution...")
        
        # Analyze tool usage
        unused_tools = [t for t in self.tools.values() if t.usage_count == 0]
        high_success_tools = [t for t in self.tools.values() if t.success_rate >= 95]
        
        print(f"   Unused tools: {len(unused_tools)}")
        print(f"   High success tools: {len(high_success_tools)}")
        
        # Generate evolution suggestions
        suggestions = []
        if unused_tools:
            suggestions.append(f"Consider removing {len(unused_tools)} unused tools")
        if high_success_tools:
            suggestions.append(f"Promote {len(high_success_tools)} high-success tools to core")
        
        if suggestions:
            print(f"\n💡 Evolution suggestions:")
            for i, sug in enumerate(suggestions, 1):
                print(f"   {i}. {sug}")
        
        print(f"\n✅ Evolution complete\n")
        
        return suggestions
    
    def stats(self):
        """Show statistics"""
        print(f"\n{'='*70}")
        print(f"📊 ContextDB Statistics")
        print(f"{'='*70}")
        print(f"Tools: {len(self.tools)}")
        print(f"Contexts: {len(self.contexts)}")
        print(f"Skills: {len(self.skills)}")
        
        if self.tools:
            total_lines = sum(t.lines for t in self.tools.values())
            total_size = sum(t.size_kb for t in self.tools.values())
            print(f"\nTool Metrics:")
            print(f"   Total Lines: {total_lines:,}")
            print(f"   Total Size: {total_size:.1f} KB")
            print(f"   Avg Lines/Tool: {total_lines/len(self.tools):.0f}")
        
        print(f"{'='*70}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw ContextDB')
    subparsers = parser.add_subparsers(dest='cmd', help='Command')
    
    # Init
    p_init = subparsers.add_parser('init', help='Initialize ContextDB')
    
    # Register
    p_reg = subparsers.add_parser('register', help='Register tool')
    p_reg.add_argument('tool', help='Tool name')
    p_reg.add_argument('--category', default='auto', help='Category')
    
    # Search
    p_search = subparsers.add_parser('search', help='Search tools')
    p_search.add_argument('query', help='Search query')
    
    # Context
    p_ctx = subparsers.add_parser('context', help='Create context')
    p_ctx.add_argument('name', help='Context name')
    p_ctx.add_argument('--level', type=int, default=1, help='Level (1-3)')
    
    # Skills
    p_skill = subparsers.add_parser('skills', help='Get skill')
    p_skill.add_argument('name', help='Skill name')
    
    # Evolve
    p_evolve = subparsers.add_parser('evolve', help='Run evolution')
    
    # Stats
    p_stats = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    db = ContextDB()
    
    if args.cmd == 'init' or args.cmd is None:
        db.stats()
    
    elif args.cmd == 'register':
        db.register_tool(args.tool, args.category)
    
    elif args.cmd == 'search':
        db.search_tools(args.query)
    
    elif args.cmd == 'context':
        db.create_context(args.name, args.level)
    
    elif args.cmd == 'skills':
        db.get_skills(args.name)
    
    elif args.cmd == 'evolve':
        db.evolve()
    
    elif args.cmd == 'stats':
        db.stats()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
