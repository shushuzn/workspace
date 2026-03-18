#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian Tools CLI - Unified command-line interface

Commands:
- defuddle: Extract markdown from URLs
- collect: arXiv paper collection
- canvas: Generate/update canvas files
- cache: Manage defuddle cache
- status: Show system status

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Import tools
sys.path.insert(0, str(Path(__file__).parent))

try:
    from defuddle_integration import DefuddleExtractor
    DEFUDDLE_OK = True
except ImportError:
    DEFUDDLE_OK = False

try:
    from arxiv_collector_v2 import ArXivCollector
    ARXIV_OK = True
except ImportError:
    ARXIV_OK = False

try:
    from canvas_auto_updater import CanvasAutoUpdater
    CANVAS_OK = True
except ImportError:
    CANVAS_OK = False

try:
    from enhanced_canvas_generator import EnhancedCanvasGenerator
    ENHANCED_CANVAS_OK = True
except ImportError:
    ENHANCED_CANVAS_OK = False

try:
    from paper_summarizer import PaperSummarizer
    SUMMARIZER_OK = True
except ImportError:
    SUMMARIZER_OK = False

try:
    from batch_processor_v2 import BatchProcessorV2
    BATCH_OK = True
except ImportError:
    BATCH_OK = False

try:
    from heartbeat_integration import HeartbeatIntegration
    HEARTBEAT_OK = True
except ImportError:
    HEARTBEAT_OK = False

try:
    from smart_cache_v2 import SmartCacheV2
    SMART_CACHE_OK = True
except ImportError:
    SMART_CACHE_OK = False


def cmd_defuddle(args):
    """Defuddle markdown extraction"""
    if not DEFUDDLE_OK:
        print("❌ Defuddle integration not available")
        return 1
    
    extractor = DefuddleExtractor()
    
    if args.url:
        print(f"🔍 Extracting: {args.url}")
        try:
            markdown, metadata = extractor.extract_markdown(
                args.url,
                output_file=args.output
            )
            print(f"✅ Title: {metadata.get('title', 'N/A')}")
            print(f"✅ Domain: {metadata.get('domain', 'N/A')}")
            print(f"✅ Markdown: {len(markdown)} chars")
            if args.output:
                print(f"💾 Saved to: {args.output}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    else:
        print("Usage: obsidian-tools defuddle --url <URL> [--output <file>]")
    return 0


def cmd_collect(args):
    """arXiv paper collection"""
    if not ARXIV_OK:
        print("❌ arXiv collector not available")
        return 1
    
    collector = ArXivCollector(config_file=args.config)
    
    if args.keywords:
        keywords = args.keywords
    else:
        keywords = collector.config.get('keywords', ['quantum computing'])
    
    collector.config['max_results'] = args.max_results or 20
    
    collector.collect(
        keywords=keywords,
        extract_md=not args.no_md,
        update_canvas=not args.no_canvas
    )
    return 0


def cmd_canvas(args):
    """Canvas generation and updates"""
    if args.enhanced:
        if not ENHANCED_CANVAS_OK:
            print("❌ Enhanced canvas generator not available")
            return 1
        
        generator = EnhancedCanvasGenerator()
        
        if args.all or args.timeline:
            if args.timeline:
                results = generator.create_timeline_canvas()
                print(f"✅ Timeline canvas: {results.get('nodes', 0)} nodes, {results.get('edges', 0)} edges")
            else:
                results = generator.create_all()
                print(f"✅ Created {results['summary']['files_created']} canvas files")
                print(f"   {results['summary']['total_nodes']} nodes, {results['summary']['total_edges']} edges")
                
                if results['timeline'].get('success'):
                    print(f"   Timeline: {results['timeline']['nodes']} nodes, {results['timeline']['edges']} edges")
        elif args.lessons:
            results = generator.create_lessons_canvas()
            print(f"✅ Lessons canvas: {results.get('nodes', 0)} nodes, {results.get('edges', 0)} edges")
        elif args.papers:
            results = generator.create_papers_canvas()
            print(f"✅ Papers canvas: {results.get('nodes', 0)} nodes, {results.get('edges', 0)} edges")
        else:
            results = generator.create_all()
            print(f"✅ Created {results['summary']['files_created']} canvas files")
            print(f"   {results['summary']['total_nodes']} nodes, {results['summary']['total_edges']} edges")
    else:
        if not CANVAS_OK:
            print("❌ Canvas generator not available")
            return 1
        
        updater = CanvasAutoUpdater()
        
        if args.update:
            print("🎨 Updating canvases...")
            results = updater.update_all(force=args.force)
            
            if results['lessons']['updated']:
                print(f"✅ Lessons: {results['lessons']['nodes']} nodes, {results['lessons']['edges']} edges")
            else:
                print(f"ℹ️  Lessons: {results['lessons']['reason']}")
            
            if results['workflows']['updated']:
                print(f"✅ Workflows: {results['workflows']['nodes']} nodes, {results['workflows']['edges']} edges")
            else:
                print(f"ℹ️  Workflows: {results['workflows']['reason']}")
            
            print(f"\n📊 Total: {results['summary']['total_updated']} updated")
            
        elif args.status:
            status = updater.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        else:
            print("Usage: obsidian-tools canvas --update [--force]")
            print("       obsidian-tools canvas --status")
            print("       obsidian-tools canvas --enhanced --all")
            print("       obsidian-tools canvas --enhanced --timeline")
    
    return 0


def cmd_summarize(args):
    """Paper summarization"""
    if not SUMMARIZER_OK:
        print("❌ Paper summarizer not available")
        return 1
    
    summarizer = PaperSummarizer()
    
    if args.stats:
        stats = summarizer.get_stats()
        print(json.dumps(stats, indent=2))
    elif args.keyword:
        summarizer.summarize_batch(args.keyword, force=args.force)
    else:
        print("Usage: obsidian-tools summarize --keyword <keyword>")
        print("       obsidian-tools summarize --stats")
    
    return 0


def cmd_batch(args):
    """Batch processing demo"""
    if not BATCH_OK:
        print("❌ Batch processor not available")
        return 1
    
    if args.demo:
        processor = BatchProcessorV2(max_workers=args.workers)
        
        # Demo with sample tasks
        import time
        
        def sample_task(n):
            time.sleep(0.3)
            return n * 2
        
        items = list(range(10))
        results = processor.process_batch(
            items=items,
            processor_func=sample_task,
            item_ids=[f"task_{i}" for i in items],
            show_progress=True
        )
        
        return 0
    else:
        print("Usage: obsidian-tools batch --demo")
        print("       obsidian-tools batch --workers 4")
        return 0


def cmd_heartbeat(args):
    """HEARTBEAT automation"""
    if not HEARTBEAT_OK:
        print("❌ HEARTBEAT integration not available")
        return 1
    
    heartbeat = HeartbeatIntegration()
    
    if args.run or args.force:
        heartbeat.run_heartbeat(force=args.force)
    elif args.status:
        heartbeat.show_status()
    elif args.config:
        if args.interval:
            heartbeat.config['interval_minutes'] = args.interval
            heartbeat.save_config(heartbeat.config)
            print(f"✅ Configuration updated")
        heartbeat.show_status()
    else:
        print("Usage: obsidian-tools heartbeat --run")
        print("       obsidian-tools heartbeat --force")
        print("       obsidian-tools heartbeat --status")
        print("       obsidian-tools heartbeat --config --interval 30")
    
    return 0


def cmd_cache(args):
    """Cache management"""
    if args.v2:
        if not SMART_CACHE_OK:
            print("❌ Smart cache v2 not available")
            return 1
        
        cache = SmartCacheV2()
        
        if args.stats:
            cache.show_stats()
        elif args.clear:
            cache.clear()
            print("✅ Cache cleared")
        elif args.cleanup:
            result = cache.cleanup_expired()
            print(f"✅ Cleanup: {result['removed']} entries, {result['freed_mb']:.2f} MB freed")
        else:
            cache.show_stats()
    else:
        # Legacy cache (if available)
        if not CACHE_OK:
            print("❌ Cache manager not available")
            print("   Try: obsidian-tools cache --v2 --stats")
            return 1
        
        cache = CacheManager()
        
        if args.stats:
            stats = cache.get_stats()
            print(json.dumps(stats, indent=2))
        elif args.clear:
            cache.clear()
            print("✅ Cache cleared")
        elif args.cleanup:
            result = cache.cleanup_expired()
            print(f"✅ Cleanup: {result['removed']} entries")
        elif args.list:
            stats = cache.get_stats()
            print(f"Total entries: {stats.get('total_entries', 0)}")
        else:
            print("Usage: obsidian-tools cache --stats")
            print("       obsidian-tools cache --list")
            print("       obsidian-tools cache --clear")
            print("       obsidian-tools cache --cleanup")
            print("       obsidian-tools cache --v2 --stats (smart cache)")
    
    return 0


def cmd_cache(args):
    """Cache management"""
    cache_file = Path(__file__).parent.parent / "data" / "cache" / "defuddle_cache.json"
    
    if not cache_file.exists():
        print("ℹ️  No cache found")
        return 0
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    if args.stats:
        stats = cache.get('stats', {})
        total = stats.get('hits', 0) + stats.get('misses', 0)
        hit_rate = (stats.get('hits', 0) / total * 100) if total > 0 else 0
        
        print("📊 Cache Statistics:")
        print(f"  Hits: {stats.get('hits', 0)}")
        print(f"  Misses: {stats.get('misses', 0)}")
        print(f"  Hit Rate: {hit_rate:.1f}%")
        print(f"  Cached URLs: {len(cache.get('urls', {}))}")
    
    if args.clear:
        confirm = input("Clear cache? [y/N]: ")
        if confirm.lower() == 'y':
            cache = {'urls': {}, 'stats': {'hits': 0, 'misses': 0}}
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            print("✅ Cache cleared")
    
    if args.list:
        urls = cache.get('urls', {})
        print(f"📋 Cached URLs ({len(urls)}):")
        for url, data in list(urls.items())[:10]:
            cached_at = data.get('cached_at', 'N/A')[:19]
            length = data.get('markdown_length', 0)
            print(f"  - {url[:60]}... ({length} chars, {cached_at})")
        if len(urls) > 10:
            print(f"  ... and {len(urls) - 10} more")
    
    return 0


def cmd_status(args):
    """Show system status"""
    print("╔════════════════════════════════════════════════╗")
    print("║  Obsidian Tools Status                         ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    
    # Tool availability
    print("🔧 Tools:")
    print(f"  Defuddle: {'✅' if DEFUDDLE_OK else '❌'}")
    print(f"  arXiv Collector: {'✅' if ARXIV_OK else '❌'}")
    print(f"  Canvas Generator: {'✅' if CANVAS_OK else '❌'}")
    print(f"  Enhanced Canvas: {'✅' if ENHANCED_CANVAS_OK else '❌'}")
    print(f"  Paper Summarizer: {'✅' if SUMMARIZER_OK else '❌'}")
    print(f"  Batch Processor: {'✅' if BATCH_OK else '❌'}")
    print(f"  HEARTBEAT: {'✅' if HEARTBEAT_OK else '❌'}")
    print(f"  Smart Cache v2: {'✅' if SMART_CACHE_OK else '❌'}")
    print()
    
    # Cache status
    cache_file = Path(__file__).parent.parent / "data" / "cache" / "defuddle_cache.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        stats = cache.get('stats', {})
        total = stats.get('hits', 0) + stats.get('misses', 0)
        hit_rate = (stats.get('hits', 0) / total * 100) if total > 0 else 0
        print("💾 Defuddle Cache:")
        print(f"  Cached URLs: {len(cache.get('urls', {}))}")
        print(f"  Hit Rate: {hit_rate:.1f}%")
    else:
        print("💾 Defuddle Cache: Empty")
    print()
    
    # Summary cache status
    summary_cache = Path(__file__).parent.parent / "data" / "cache" / "summary_cache.json"
    if summary_cache.exists():
        with open(summary_cache, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        stats = cache.get('stats', {})
        print("💾 Summary Cache:")
        print(f"  Generated: {stats.get('generated', 0)}")
        print(f"  Cached: {stats.get('cached', 0)}")
    else:
        print("💾 Summary Cache: Empty")
    print()
    
    # Canvas status
    canvas_state = Path(__file__).parent.parent / "00-config" / "canvas_state.json"
    if canvas_state.exists():
        with open(canvas_state, 'r', encoding='utf-8') as f:
            state = json.load(f)
        print("🎨 Canvas:")
        print(f"  Lessons updates: {state.get('lessons', {}).get('update_count', 0)}")
        print(f"  Workflows updates: {state.get('workflows', {}).get('update_count', 0)}")
    else:
        print("🎨 Canvas: No state")
    print()
    
    # Data files
    papers_dir = Path(__file__).parent.parent / "data" / "papers"
    if papers_dir.exists():
        paper_files = list(papers_dir.glob("*.json"))
        print(f"📄 Papers: {len(paper_files)} files")
    else:
        print("📄 Papers: No data")
    
    summaries_dir = Path(__file__).parent.parent / "data" / "summaries"
    if summaries_dir.exists():
        summary_files = list(summaries_dir.glob("*.json"))
        print(f"📝 Summaries: {len(summary_files)} files")
    else:
        print("📝 Summaries: No data")
    
    return 0


def cmd_version(args):
    """Show version"""
    print("Obsidian Tools CLI v1.0")
    print("Build: 2026-03-16")
    print()
    print("Tools:")
    print("  - defuddle_integration.py (Defuddle CLI wrapper)")
    print("  - arxiv_collector_v2.py (arXiv API + Defuddle)")
    print("  - json_canvas_generator.py (Canvas generation)")
    print("  - canvas_auto_updater.py (Auto-update + HEARTBEAT)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Obsidian Tools CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  obsidian-tools defuddle --url https://arxiv.org/abs/2301.07041
  obsidian-tools collect --keywords "quantum computing" "AI"
  obsidian-tools canvas --update --force
  obsidian-tools cache --stats
  obsidian-tools status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Defuddle command
    p_defuddle = subparsers.add_parser('defuddle', help='Extract markdown from URL')
    p_defuddle.add_argument('--url', type=str, help='URL to extract')
    p_defuddle.add_argument('--output', type=str, help='Output file path')
    p_defuddle.set_defaults(func=cmd_defuddle)
    
    # Collect command
    p_collect = subparsers.add_parser('collect', help='arXiv paper collection')
    p_collect.add_argument('--keywords', type=str, nargs='+', help='Keywords')
    p_collect.add_argument('--config', type=str, help='Config file')
    p_collect.add_argument('--max-results', type=int, help='Max results per keyword')
    p_collect.add_argument('--no-md', action='store_true', help='Disable markdown extraction')
    p_collect.add_argument('--no-canvas', action='store_true', help='Disable canvas update')
    p_collect.set_defaults(func=cmd_collect)
    
    # Canvas command
    p_canvas = subparsers.add_parser('canvas', help='Canvas management')
    p_canvas.add_argument('--update', action='store_true', help='Update canvases')
    p_canvas.add_argument('--force', action='store_true', help='Force update')
    p_canvas.add_argument('--status', action='store_true', help='Show status')
    p_canvas.add_argument('--enhanced', action='store_true', help='Use enhanced generator')
    p_canvas.add_argument('--timeline', action='store_true', help='Create timeline canvas')
    p_canvas.add_argument('--all', action='store_true', help='Create all canvases')
    p_canvas.set_defaults(func=cmd_canvas)
    
    # Summarize command
    p_summarize = subparsers.add_parser('summarize', help='Paper summarization')
    p_summarize.add_argument('--keyword', type=str, help='Keyword to summarize')
    p_summarize.add_argument('--force', action='store_true', help='Force regeneration')
    p_summarize.add_argument('--stats', action='store_true', help='Show statistics')
    p_summarize.set_defaults(func=cmd_summarize)
    
    # Batch command
    p_batch = subparsers.add_parser('batch', help='Batch processing demo')
    p_batch.add_argument('--demo', action='store_true', help='Run demo')
    p_batch.add_argument('--workers', type=int, default=4, help='Max workers')
    p_batch.set_defaults(func=cmd_batch)
    
    # Heartbeat command
    p_heartbeat = subparsers.add_parser('heartbeat', help='HEARTBEAT automation')
    p_heartbeat.add_argument('--run', action='store_true', help='Run heartbeat cycle')
    p_heartbeat.add_argument('--force', action='store_true', help='Force run')
    p_heartbeat.add_argument('--status', action='store_true', help='Show status')
    p_heartbeat.add_argument('--config', action='store_true', help='Show/config config')
    p_heartbeat.add_argument('--interval', type=int, help='Interval in minutes')
    p_heartbeat.set_defaults(func=cmd_heartbeat)
    
    # Cache command (updated for v2)
    # Note: cache command already exists, just update help
    
    # Cache command
    p_cache = subparsers.add_parser('cache', help='Cache management')
    p_cache.add_argument('--stats', action='store_true', help='Show statistics')
    p_cache.add_argument('--clear', action='store_true', help='Clear cache')
    p_cache.add_argument('--list', action='store_true', help='List cached URLs')
    p_cache.set_defaults(func=cmd_cache)
    
    # Status command
    p_status = subparsers.add_parser('status', help='Show system status')
    p_status.set_defaults(func=cmd_status)
    
    # Version command
    p_version = subparsers.add_parser('version', help='Show version')
    p_version.set_defaults(func=cmd_version)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
