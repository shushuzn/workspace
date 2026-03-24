#!/usr/bin/env python3
"""
Tool Registry System for OpenClaw Workspace
Indexes and manages 300+ Python tools with similarity search and usage tracking.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


# Configuration
SCRIPTS_DIR = Path(__file__).parent
REGISTRY_FILE = SCRIPTS_DIR / "tool_registry.json"
DEFAULT_CATEGORIES = [
    "workflow",
    "analysis",
    "memory",
    "deploy",
    "monitor",
    "collector",
    "automation",
    "security",
    "knowledge",
    "data",
    "novel",
    "stock",
    "research",
    "utils",
    "test",
    "archive",
]


def load_registry() -> Dict:
    """Load the tool registry from JSON file."""
    if not REGISTRY_FILE.exists():
        return {"tools": {}, "categories": DEFAULT_CATEGORIES, "total_tools": 0}

    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load registry: {e}")
        return {"tools": {}, "categories": DEFAULT_CATEGORIES, "total_tools": 0}


def save_registry(registry: Dict) -> bool:
    """Save the tool registry to JSON file."""
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving registry: {e}")
        return False


def get_category_from_path(filepath: Path, scripts_dir: Path) -> str:
    """Determine category based on directory path."""
    rel_path = filepath.relative_to(scripts_dir)
    parts = rel_path.parts

    # Map directory names to categories
    category_map = {
        "00-UTILS": "utils",
        "01-KNOWLEDGE-CARDS": "knowledge",
        "02-DAILY-BRIEF": "workflow",
        "03-LIG-KNOWLEDGE-GRAPH": "knowledge",
        "04-collectors": "collector",
        "05-AI-RESEARCH": "research",
        "06-MONITORING": "monitor",
        "07-DATA": "data",
        "08-AUTOMATION": "automation",
        "09-TESTS": "test",
        "10-DOMAIN-RANKING": "analysis",
        "11-NOVEL-WRITING": "novel",
        "12-KNOWLEDGE-MANAGEMENT": "knowledge",
        "13-SECURITY": "security",
        "13-memory": "memory",
        "14-PLUGIN": "workflow",
        "15-COGNITIVE-SYSTEM": "memory",
        "archive_001": "archive",
        "arxiv-archive": "research",
        "feishu-tools": "workflow",
        "figure-enhancer": "analysis",
        "flow-archive": "archive",
        "knowledge-card-generator": "knowledge",
        "multimodal-kg": "knowledge",
        "pdf-extractor": "data",
        "plugins": "workflow",
        "sa_020_templates": "utils",
        "templates": "utils",
        "utils": "utils",
        "workflow_archive": "archive",
        "workflow_insights": "workflow",
        "workflows": "workflow",
        "stock_pro": "stock",
        "stock_pro_archive": "stock",
    }

    # Check first directory level
    if parts[0] in category_map:
        return category_map[parts[0]]

    # Check for specific file patterns
    filename = filepath.stem.lower()
    if "workflow" in filename:
        return "workflow"
    if "analysis" in filename or "stock" in filename:
        return "analysis"
    if "memory" in filename:
        return "memory"
    if "deploy" in filename or "setup" in filename:
        return "deploy"
    if "monitor" in filename:
        return "monitor"
    if "collector" in filename:
        return "collector"
    if "collector" in str(rel_path):
        return "collector"
    if "test" in filename or "test" in str(rel_path):
        return "test"

    return "utils"


def extract_description(filepath: Path) -> str:
    """Extract description from file docstring or comments."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to get module docstring
        if '"""' in content or "'''" in content:
            # Get first docstring
            for quote in ['"""', "'''"]:
                if quote in content:
                    parts = content.split(quote)
                    if len(parts) >= 2:
                        doc = parts[1].strip()
                        # Take first line or first 100 chars
                        first_line = doc.split("\n")[0].strip()
                        return first_line[:100] if first_line else "Python tool"

        # Try to get first comment line
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                desc = line[1:].strip()
                if desc and len(desc) < 100:
                    return desc

        return "Python tool"
    except Exception:
        return "Python tool"


def extract_tags(filepath: Path, category: str) -> List[str]:
    """Extract tags from filename and category."""
    filename = filepath.stem.lower()
    tags = [category]

    # Common tag patterns
    tag_patterns = {
        "arxiv": "arxiv",
        "social": "social",
        "news": "news",
        "workflow": "workflow",
        "memory": "memory",
        "stock": "stock",
        "analysis": "analysis",
        "collector": "collector",
        "monitor": "monitor",
        "knowledge": "knowledge",
        "data": "data",
        "novel": "novel",
        "security": "security",
        "automation": "automation",
        "test": "test",
        "utils": "utils",
    }

    for pattern, tag in tag_patterns.items():
        if pattern in filename:
            tags.append(tag)

    return list(dict.fromkeys(tags))[:5]


def count_lines(filepath: Path) -> int:
    """Count lines in a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except Exception:
        return 0


def cmd_list(args) -> int:
    """List tools with optional category filter."""
    registry = load_registry()
    tools = registry.get("tools", {})

    if args.category:
        # Filter by category
        filtered = {
            k: v for k, v in tools.items() if v.get("category") == args.category
        }
        tools = filtered

    if not tools:
        print("No tools found.")
        return 0

    # Sort by name
    for name in sorted(tools.keys()):
        tool = tools[name]
        category = tool.get("category", "unknown")
        lines = tool.get("lines", 0)
        use_count = tool.get("use_count", 0)
        print(f"{name:40} [{category:12}] {lines:5} lines, used {use_count} times")

    print(f"\nTotal: {len(tools)} tools")
    return 0


def cmd_search(args) -> int:
    """Search tools by name/description."""
    registry = load_registry()
    tools = registry.get("tools", {})

    query = args.query.lower()
    results = []

    for name, tool in tools.items():
        # Search in name and description
        name_match = query in name.lower()
        desc = tool.get("description", "").lower()
        desc_match = query in desc
        tags = " ".join(tool.get("tags", [])).lower()
        tags_match = query in tags

        if name_match or desc_match or tags_match:
            results.append((name, tool))

    if not results:
        print(f"No tools found matching '{args.query}'")
        return 0

    # Sort by relevance (name match first)
    results.sort(key=lambda x: (query not in x[0].lower(), x[0]))

    for name, tool in results:
        category = tool.get("category", "unknown")
        desc = tool.get("description", "")[:60]
        print(f"{name:40} [{category:12}] {desc}...")

    print(f"\nFound {len(results)} matching tools")
    return 0


def cmd_similar(args) -> int:
    """Find similar tools using keyword matching."""
    registry = load_registry()
    tools = registry.get("tools", {})

    if args.tool not in tools:
        print(f"Tool '{args.tool}' not found in registry")
        return 1

    target = tools[args.tool]
    target_text = (
        args.tool.lower()
        + " "
        + target.get("description", "").lower()
        + " "
        + " ".join(target.get("tags", [])).lower()
    )

    # Calculate similarity scores
    scores = []
    for name, tool in tools.items():
        if name == args.tool:
            continue

        tool_text = (
            name.lower()
            + " "
            + tool.get("description", "").lower()
            + " "
            + " ".join(tool.get("tags", [])).lower()
        )

        # Simple keyword matching
        target_words = set(target_text.split())
        tool_words = set(tool_text.split())
        common = target_words & tool_words
        union = target_words | tool_words

        if union:
            score = len(common) / len(union)
        else:
            score = 0

        if score > 0:
            scores.append((name, score, tool))

    # Sort by score descending
    scores.sort(key=lambda x: -x[1])

    # Show top 5
    print(f"Tools similar to '{args.tool}':")
    for name, score, tool in scores[:5]:
        category = tool.get("category", "unknown")
        desc = tool.get("description", "")[:50]
        print(f"  {name:35} [{category:12}] {desc}... (score: {score:.2f})")

    if not scores:
        print("  No similar tools found")

    return 0


def cmd_stats(args) -> int:
    """Show registry statistics."""
    registry = load_registry()
    tools = registry.get("tools", {})

    # Category counts
    category_counts = {}
    total_lines = 0
    total_uses = 0

    for tool in tools.values():
        cat = tool.get("category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        total_lines += tool.get("lines", 0)
        total_uses += tool.get("use_count", 0)

    print("Tool Registry Statistics")
    print("=" * 40)
    print(f"Total tools:    {len(tools)}")
    print(f"Total lines:    {total_lines:,}")
    print(f"Total uses:     {total_uses}")
    print()

    print("Tools by category:")
    for cat in sorted(category_counts.keys()):
        count = category_counts[cat]
        bar = "#" * min(count, 40)
        print(f"  {cat:15} {count:4} {bar}")

    return 0


def cmd_register(args) -> int:
    """Register a tool from a file path."""
    registry = load_registry()
    tools = registry.get("tools", {})

    # Resolve path
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        return 1

    if not path.is_file():
        print(f"Error: '{args.path}' is not a file")
        return 1

    if path.suffix != ".py":
        print(f"Error: '{args.path}' is not a Python file")
        return 1

    # Get tool info
    name = path.stem
    category = get_category_from_path(path, SCRIPTS_DIR)
    description = extract_description(path)
    tags = extract_tags(path, category)
    lines = count_lines(path)
    today = datetime.now().strftime("%Y-%m-%d")

    tools[name] = {
        "path": str(path.relative_to(SCRIPTS_DIR)),
        "description": description,
        "category": category,
        "tags": tags,
        "created": today,
        "last_used": today,
        "use_count": 0,
        "lines": lines,
    }

    registry["tools"] = tools
    registry["total_tools"] = len(tools)

    if save_registry(registry):
        print(f"Registered: {name}")
        print(f"  Category: {category}")
        print(f"  Lines: {lines}")
        print(f"  Tags: {', '.join(tags)}")
        return 0
    else:
        print("Error: Failed to save registry")
        return 1


def cmd_track(args) -> int:
    """Track tool usage."""
    registry = load_registry()
    tools = registry.get("tools", {})

    if args.tool not in tools:
        print(f"Tool '{args.tool}' not found in registry")
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    tools[args.tool]["last_used"] = today
    tools[args.tool]["use_count"] = tools[args.tool].get("use_count", 0) + 1

    registry["tools"] = tools

    if save_registry(registry):
        print(f"Tracked usage of '{args.tool}'")
        print(f"  Total uses: {tools[args.tool]['use_count']}")
        return 0
    else:
        print("Error: Failed to save registry")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="tool_registry",
        description="Tool Registry System for OpenClaw Workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tool_registry.py list                    # List all tools
  python tool_registry.py list --category workflow  # List workflow tools
  python tool_registry.py search workflow         # Search for workflow tools
  python tool_registry.py similar workflow        # Find tools similar to 'workflow'
  python tool_registry.py stats                   # Show statistics
  python tool_registry.py register ./tool.py      # Register a tool
  python tool_registry.py track workflow          # Track tool usage
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List tools")
    list_parser.add_argument("--category", "-c", help="Filter by category")

    # search command
    search_parser = subparsers.add_parser("search", help="Search tools")
    search_parser.add_argument("query", help="Search query")

    # similar command
    similar_parser = subparsers.add_parser("similar", help="Find similar tools")
    similar_parser.add_argument("tool", help="Tool name to find similar to")

    # stats command
    subparsers.add_parser("stats", help="Show statistics")

    # register command
    register_parser = subparsers.add_parser("register", help="Register a tool")
    register_parser.add_argument("path", help="Path to Python file")

    # track command
    track_parser = subparsers.add_parser("track", help="Track tool usage")
    track_parser.add_argument("tool", help="Tool name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "list": cmd_list,
        "search": cmd_search,
        "similar": cmd_similar,
        "stats": cmd_stats,
        "register": cmd_register,
        "track": cmd_track,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
