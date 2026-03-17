#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Management CLI - Unified interface for context operations
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / '30-scripts-tools'))

def cmd_compress(args):
    """Compress context"""
    from context_compressor import ContextCompressor
    
    compressor = ContextCompressor()
    
    if args.demo:
        # Demo mode
        import subprocess
        subprocess.run([
            sys.executable, 
            str(WORKSPACE / '30-scripts-tools' / 'context_compressor.py'),
            '--demo'
        ])
    else:
        # Read from stdin or file
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = sys.stdin.read()
        
        result = compressor.compress_context(
            text, 
            level=args.level,
            method=args.method
        )
        
        print(f"\n📊 Compression Result:")
        print(f"  Original: {result.original_length} chars")
        print(f"  Compressed: {result.compressed_length} chars")
        print(f"  Ratio: {result.compression_ratio:.1%}")
        print(f"  Saved: {(1 - result.compression_ratio) * 100:.1f}%")
        
        if args.save:
            output = compressor.save_compressed(result, args.save)
            print(f"\n💾 Saved to: {output}")

def cmd_cache(args):
    """Manage context cache"""
    from context_cache_manager import ContextCacheManager
    
    cache = ContextCacheManager()
    
    if args.stats:
        stats = cache.stats()
        print("\n💾 Context Cache Statistics")
        print("=" * 60)
        for key, val in stats.items():
            print(f"  {key}: {val}")
    
    elif args.clear:
        level = args.clear if args.clear != True else 'all'
        cache.clear(level)
        print(f"✅ Cache cleared ({level})")
    
    elif args.cleanup:
        cleaned = cache.cleanup()
        print(f"🧹 Cleanup complete: L1={cleaned['l1']}, L2={cleaned['l2']}")
    
    elif args.demo:
        import subprocess
        subprocess.run([
            sys.executable,
            str(WORKSPACE / '30-scripts-tools' / 'context_cache_manager.py'),
            '--demo'
        ])

def cmd_search(args):
    """Search context"""
    from context_search import ContextSearcher
    
    searcher = ContextSearcher()
    
    if args.demo:
        import subprocess
        subprocess.run([
            sys.executable,
            str(WORKSPACE / '30-scripts-tools' / 'context_search.py'),
            '--demo',
            '--max', str(args.max)
        ])
    else:
        results = searcher.search(
            args.query,
            max_results=args.max,
            min_score=args.min_score
        )
        
        print(f"\n🔍 Search Results for '{args.query}'")
        print("=" * 60)
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result.source}] (Score: {result.score:.2f})")
            print(f"   Matched: {', '.join(result.matched_terms)}")
            print(f"   Content: {result.content[:200]}...")
            print()

def cmd_status(args):
    """Show context system status"""
    from context_cache_manager import ContextCacheManager
    
    cache = ContextCacheManager()
    stats = cache.stats()
    
    print("\n🗜️  Context Compression System Status")
    print("=" * 60)
    print(f"\n📦 Cache:")
    print(f"  L1 (Memory): {stats['l1_count']}/{stats['l1_max']} entries")
    print(f"  L2 (Disk):   {stats['l2_count']}/{stats['l2_max']} entries")
    print(f"  L2 Size:     {stats['l2_size_bytes'] / 1024:.1f} KB")
    
    print(f"\n📁 Context Directory:")
    context_dir = WORKSPACE / 'data' / 'context_cache'
    if context_dir.exists():
        files = list(context_dir.glob('*.json'))
        print(f"  Compressed contexts: {len(files)} files")
    
    print(f"\n🛠️  Tools:")
    tools = [
        'context_compressor.py',
        'context_cache_manager.py',
        'context_search.py',
        'context_cli.py'
    ]
    for tool in tools:
        tool_path = WORKSPACE / '30-scripts-tools' / tool
        status = "✅" if tool_path.exists() else "❌"
        print(f"  {status} {tool}")
    
    print(f"\n📚 Usage:")
    print(f"  context_cli.py compress --demo          # Test compression")
    print(f"  context_cli.py cache --stats            # View cache stats")
    print(f"  context_cli.py search --query \"xxx\"     # Search context")
    print(f"  context_cli.py status                   # This status")

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Context Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s compress --demo              # Run compression demo
  %(prog)s compress --file input.txt --level heavy
  %(prog)s cache --stats                # Show cache statistics
  %(prog)s cache --cleanup              # Cleanup expired entries
  %(prog)s search --query "memory"      # Search context
  %(prog)s status                       # System status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Compress command
    p_compress = subparsers.add_parser('compress', help='Compress context')
    p_compress.add_argument('--demo', action='store_true', help='Demo mode')
    p_compress.add_argument('--file', type=str, help='Input file')
    p_compress.add_argument('--level', type=str,
                           choices=['light', 'medium', 'heavy', 'extreme'],
                           default='medium', help='Compression level')
    p_compress.add_argument('--method', type=str,
                           choices=['extractive', 'hierarchical'],
                           default='extractive', help='Compression method')
    p_compress.add_argument('--save', type=str, help='Save with ID')
    p_compress.set_defaults(func=cmd_compress)
    
    # Cache command
    p_cache = subparsers.add_parser('cache', help='Manage cache')
    p_cache.add_argument('--demo', action='store_true', help='Demo mode')
    p_cache.add_argument('--stats', action='store_true', help='Show stats')
    p_cache.add_argument('--clear', nargs='?', const=True, 
                        choices=['l1', 'l2', 'all'], help='Clear cache')
    p_cache.add_argument('--cleanup', action='store_true', help='Cleanup expired')
    p_cache.set_defaults(func=cmd_cache)
    
    # Search command
    p_search = subparsers.add_parser('search', help='Search context')
    p_search.add_argument('--query', type=str, required=True, help='Search query')
    p_search.add_argument('--max', type=int, default=5, help='Max results')
    p_search.add_argument('--min-score', type=float, default=0.3, help='Min score')
    p_search.add_argument('--demo', action='store_true', help='Demo mode')
    p_search.set_defaults(func=cmd_search)
    
    # Status command
    p_status = subparsers.add_parser('status', help='System status')
    p_status.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
    else:
        args.func(args)

if __name__ == "__main__":
    main()
