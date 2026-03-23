#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dual-layer Memory CLI

Usage:
    py memory/cli.py add "content" --type preference
    py memory/cli.py list
    py memory/cli.py search "关键词"
    py memory/cli.py stats
    py memory/cli.py compress
    py memory/cli.py bridge --session new_session_id
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import DualLayerMemory


def main():
    parser = argparse.ArgumentParser(description="Dual-layer Memory CLI")
    parser.add_argument("action", choices=["add", "list", "search", "stats", "compress", "bridge"],
                       help="Action to perform")
    parser.add_argument("content", nargs="?", help="Content for add/search")
    parser.add_argument("--type", "-t", default="conversation",
                       choices=["conversation", "preference", "decision", "fact", "project"],
                       help="Memory type")
    parser.add_argument("--session", "-s", help="Session ID for bridge")
    parser.add_argument("--db", "-d", default="13-memory/memory.db", help="Database path")
    parser.add_argument("--tokens", default="5000", type=int, help="Token budget")

    args = parser.parse_args()

    # Initialize
    memory = DualLayerMemory(token_budget=args.tokens, db_path=args.db)

    if args.action == "add":
        if not args.content:
            print("Error: content required for add action")
            sys.exit(1)

        item = memory.add(args.content, args.type)
        print(json.dumps({
            "status": "added",
            "id": item.id,
            "importance": round(item.importance, 3),
            "type": item.type
        }, ensure_ascii=False, indent=2))

    elif args.action == "list":
        items = memory.get_context()
        print(json.dumps([
            {
                "id": i.id[:20],
                "type": i.type,
                "importance": round(i.importance, 2),
                "content": i.content[:50] + "..." if len(i.content) > 50 else i.content
            }
            for i in items
        ], ensure_ascii=False, indent=2))

    elif args.action == "search":
        if not args.content:
            print("Error: query required for search")
            sys.exit(1)

        results = memory.search(args.content, top_k=10)
        print(json.dumps([
            {
                "id": r.id[:20],
                "importance": round(r.importance, 2),
                "content": r.content[:100] + "..." if len(r.content) > 100 else r.content
            }
            for r in results
        ], ensure_ascii=False, indent=2))

    elif args.action == "stats":
        stats = memory.get_stats()
        # Add archive stats
        archive_stats = memory.archive.get_stats()
        stats["archive"] = archive_stats
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.action == "compress":
        result = memory.compress()
        print(json.dumps(result, indent=2))

    elif args.action == "bridge":
        session_id = args.session or f"session_{Path(args.db).stem}"
        essential = memory.bridge_to(session_id)

        # Save to file
        save_path = f"13-memory/essential_{session_id}.json"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(essential, f, ensure_ascii=False, indent=2)

        print(json.dumps({
            "status": "exported",
            "path": save_path,
            "stats": essential["stats"]
        }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()