#!/usr/bin/env python3
"""
Tool Registry Indexer for OpenClaw Workspace
Scans 30-scripts-tools/ for Python files and generates tool_registry.json.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


# Configuration
SCRIPTS_DIR = Path(__file__).parent
REGISTRY_FILE = SCRIPTS_DIR / "tool_registry.json"

# Directories to exclude from indexing
EXCLUDE_DIRS = {
    "__pycache__",
    ".cache",
    ".git",
    ".githooks",
    "archive_001",
    "stock_pro_archive",
    "workflow_archive",
    "arxiv-archive",
}

# Files to exclude
EXCLUDE_FILES = {
    "tool_registry.py",
    "tool_registry_indexer.py",
    "tools_registry.json",
    ".py",
}


def should_exclude(filepath: Path, scripts_dir: Path) -> bool:
    """Check if a file should be excluded from indexing."""
    rel_path = filepath.relative_to(scripts_dir)
    parts = rel_path.parts

    # Check if any part is in exclude dirs
    for part in parts[:-1]:  # Exclude filename
        if part in EXCLUDE_DIRS:
            return True

    # Check filename
    if filepath.name in EXCLUDE_FILES:
        return True

    return False


def get_category_from_path(filepath: Path, scripts_dir: Path) -> str:
    """Determine category based on directory path."""
    rel_path = filepath.relative_to(scripts_dir)
    parts = rel_path.parts

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

    if parts[0] in category_map:
        return category_map[parts[0]]

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

        if '"""' in content or "'''" in content:
            for quote in ['"""', "'''"]:
                if quote in content:
                    parts = content.split(quote)
                    if len(parts) >= 2:
                        doc = parts[1].strip()
                        first_line = doc.split("\n")[0].strip()
                        return first_line[:100] if first_line else "Python tool"

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


def scan_tools(scripts_dir: Path) -> Tuple[Dict, int]:
    """Scan directory for Python tools and return registry data."""
    tools = {}
    total_lines = 0
    today = datetime.now().strftime("%Y-%m-%d")

    py_files = list(scripts_dir.rglob("*.py"))

    for filepath in py_files:
        if should_exclude(filepath, scripts_dir):
            continue

        name = filepath.stem
        category = get_category_from_path(filepath, scripts_dir)
        description = extract_description(filepath)
        tags = extract_tags(filepath, category)
        lines = count_lines(filepath)

        tools[name] = {
            "path": str(filepath.relative_to(scripts_dir)),
            "description": description,
            "category": category,
            "tags": tags,
            "created": today,
            "last_used": today,
            "use_count": 0,
            "lines": lines,
        }

        total_lines += lines

    return tools, total_lines


def generate_registry(scripts_dir: Path, output_file: Path) -> bool:
    """Generate the tool registry JSON file."""
    print(f"Scanning {scripts_dir} for Python tools...")

    tools, total_lines = scan_tools(scripts_dir)

    if not tools:
        print("No tools found!")
        return False

    # Get unique categories
    categories = list(set(t.get("category", "unknown") for t in tools.values()))
    categories.sort()

    registry = {
        "tools": tools,
        "categories": categories,
        "total_tools": len(tools),
        "generated": datetime.now().isoformat(),
        "total_lines": total_lines,
    }

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving registry: {e}")
        return False


def main():
    """Main entry point."""
    scripts_dir = SCRIPTS_DIR
    output_file = REGISTRY_FILE

    print("=" * 60)
    print("Tool Registry Indexer")
    print("=" * 60)
    print(f"Scripts directory: {scripts_dir}")
    print(f"Output file: {output_file}")
    print()

    if not scripts_dir.exists():
        print(f"Error: Directory not found: {scripts_dir}")
        return 1

    if not scripts_dir.is_dir():
        print(f"Error: Not a directory: {scripts_dir}")
        return 1

    if generate_registry(scripts_dir, output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            registry = json.load(f)

        tools = registry.get("tools", {})
        categories = registry.get("categories", [])

        print()
        print("Indexing complete!")
        print(f"  Total tools:    {len(tools)}")
        print(f"  Total lines:    {registry.get('total_lines', 0):,}")
        print(f"  Categories:     {len(categories)}")
        print(f"  Output file:    {output_file}")
        print()

        print("Categories:")
        for cat in categories:
            count = sum(1 for t in tools.values() if t.get("category") == cat)
            print(f"  {cat:15} {count:4} tools")

        return 0
    else:
        print("Indexing failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
