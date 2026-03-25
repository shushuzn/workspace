#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HEARTBEAT Integration - Automated Canvas updates

Features:
- Auto canvas update every 30 minutes
- Smart cache management
- Status tracking
- Error recovery

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Import obsidian tools
try:
    from enhanced_canvas_generator import EnhancedCanvasGenerator
    CANVAS_OK = True
except ImportError:
    CANVAS_OK = False

try:
    from cache_manager import CacheManager
    CACHE_OK = True
except ImportError:
    CACHE_OK = False


class HeartbeatIntegration:
    """HEARTBEAT automation for Obsidian tools"""

    def __init__(self, workspace: str = '.'):
        self.workspace = Path(workspace)
        self.state_file = self.workspace / 'data' / 'heartbeat_state.json'
        self.config_file = self.workspace / '30-scripts-tools' / 'heartbeat_config.json'
        self.state = self.load_state()
        self.config = self.load_config()

    def load_state(self) -> Dict:
        """Load heartbeat state"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'last_run': None,
            'next_run': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_canvas_update': None,
            'last_cache_cleanup': None
        }

    def save_state(self):
        """Save heartbeat state"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def load_config(self) -> Dict:
        """Load heartbeat configuration"""
        default_config = {
            'interval_minutes': 30,
            'auto_canvas_update': True,
            'auto_cache_cleanup': True,
            'cache_ttl_hours': 24,
            'notify_on_success': False,
            'notify_on_failure': True
        }

        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}

        # Save default config
        self.save_config(default_config)
        return default_config

    def save_config(self, config: Dict):
        """Save heartbeat configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def should_run(self) -> bool:
        """Check if heartbeat should run"""
        if not self.state['last_run']:
            return True

        last_run = datetime.fromisoformat(self.state['last_run'])
        next_run = last_run + timedelta(minutes=self.config['interval_minutes'])

        return datetime.now() >= next_run

    def update_canvas(self) -> Dict:
        """Update all canvases"""
        if not CANVAS_OK:
            return {'success': False, 'error': 'Canvas generator not available'}

        try:
            generator = EnhancedCanvasGenerator()
            results = generator.create_all()

            self.state['last_canvas_update'] = datetime.now().isoformat()

            return {
                'success': True,
                'files_created': results['summary']['files_created'],
                'total_nodes': results['summary']['total_nodes'],
                'total_edges': results['summary']['total_edges']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cleanup_cache(self) -> Dict:
        """Cleanup expired cache entries"""
        if not CACHE_OK:
            return {'success': False, 'error': 'Cache manager not available'}

        try:
            cache = CacheManager()
            stats = cache.cleanup_expired()

            self.state['last_cache_cleanup'] = datetime.now().isoformat()

            return {
                'success': True,
                'entries_removed': stats.get('removed', 0),
                'space_freed_mb': stats.get('space_freed_mb', 0)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_heartbeat(self, force: bool = False) -> Dict:
        """Run heartbeat cycle"""
        print(f"\n{'=' *70}")
        print(f"💓 HEARTBEAT Cycle Started")
        print(f"{'=' *70}\n")

        if not force and not self.should_run():
            next_run = datetime.fromisoformat(self.state['next_run']) if self.state['next_run'] else None
            print(f"ℹ️  Not time yet. Next run: {next_run}")
            return {'skipped': True, 'reason': 'Not scheduled'}

        start_time = datetime.now()
        results = {
            'timestamp': start_time.isoformat(),
            'canvas_update': None,
            'cache_cleanup': None,
            'duration_seconds': 0
        }

        # Update canvases
        if self.config['auto_canvas_update']:
            print("🎨 Updating canvases...")
            canvas_result = self.update_canvas()
            results['canvas_update'] = canvas_result

            if canvas_result['success']:
                print(f"  ✅ {canvas_result['files_created']} files, "
                      f"{canvas_result['total_nodes']} nodes, "
                      f"{canvas_result['total_edges']} edges")
            else:
                print(f"  ❌ Error: {canvas_result.get('error', 'Unknown')}")

        # Cleanup cache
        if self.config['auto_cache_cleanup']:
            print("\n🧹 Cleaning up cache...")
            cache_result = self.cleanup_cache()
            results['cache_cleanup'] = cache_result

            if cache_result['success']:
                print(f"  ✅ {cache_result['entries_removed']} entries removed, "
                      f"{cache_result['space_freed_mb']:.2f} MB freed")
            else:
                print(f"  ❌ Error: {cache_result.get('error', 'Unknown')}")

        # Update state
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        results['duration_seconds'] = duration

        self.state['last_run'] = start_time.isoformat()
        self.state['next_run'] = (start_time + timedelta(minutes=self.config['interval_minutes'])).isoformat()
        self.state['total_runs'] += 1

        if all(r.get('success', True) for r in [results['canvas_update'], results['cache_cleanup']] if r):
            self.state['successful_runs'] += 1
            print(f"\n✅ HEARTBEAT completed successfully ({duration:.2f}s)")
        else:
            self.state['failed_runs'] += 1
            print(f"\n⚠️  HEARTBEAT completed with errors ({duration:.2f}s)")

        self.save_state()

        # Print summary
        print(f"\n{'=' *70}")
        print(f"📊 HEARTBEAT Summary:")
        print(f"  Total runs: {self.state['total_runs']}")
        print(f"  Successful: {self.state['successful_runs']}")
        print(f"  Failed: {self.state['failed_runs']}")
        print(f"  Success rate: {self.state['successful_runs'] /self.state['total_runs'] *100:.1f}%")
        print(f"  Next run: {self.state['next_run']}")
        print(f"{'=' *70}\n")

        return results

    def get_status(self) -> Dict:
        """Get heartbeat status"""
        return {
            'enabled': True,
            'interval_minutes': self.config['interval_minutes'],
            'last_run': self.state['last_run'],
            'next_run': self.state['next_run'],
            'total_runs': self.state['total_runs'],
            'successful_runs': self.state['successful_runs'],
            'failed_runs': self.state['failed_runs'],
            'success_rate': f"{self.state['successful_runs'] /max(1,self.state['total_runs']) *100:.1f}%",
            'last_canvas_update': self.state['last_canvas_update'],
            'last_cache_cleanup': self.state['last_cache_cleanup'],
            'config': self.config
        }

    def show_status(self):
        """Display heartbeat status"""
        status = self.get_status()

        print(f"\n{'=' *70}")
        print(f"💓 HEARTBEAT Status")
        print(f"{'=' *70}\n")

        print(f"⚙️  Configuration:")
        print(f"  Interval: {status['interval_minutes']} minutes")
        print(f"  Auto Canvas Update: {status['config']['auto_canvas_update']}")
        print(f"  Auto Cache Cleanup: {status['config']['auto_cache_cleanup']}")
        print(f"  Cache TTL: {status['config']['cache_ttl_hours']} hours\n")

        print(f"📊 Statistics:")
        print(f"  Total runs: {status['total_runs']}")
        print(f"  Successful: {status['successful_runs']}")
        print(f"  Failed: {status['failed_runs']}")
        print(f"  Success rate: {status['success_rate']}\n")

        print(f"🕐 Schedule:")
        print(f"  Last run: {status['last_run'] or 'Never'}")
        print(f"  Next run: {status['next_run'] or 'Not scheduled'}")
        print(f"  Last canvas update: {status['last_canvas_update'] or 'Never'}")
        print(f"  Last cache cleanup: {status['last_cache_cleanup'] or 'Never'}\n")

        print(f"{'=' *70}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='HEARTBEAT Integration')
    parser.add_argument('action', choices=['run', 'status', 'config', 'force'],
                       help='Action to perform')
    parser.add_argument('--force', action='store_true', help='Force run')
    parser.add_argument('--interval', type=int, help='Interval in minutes')
    parser.add_argument('--no-canvas', action='store_true', help='Disable canvas update')
    parser.add_argument('--no-cache', action='store_true', help='Disable cache cleanup')
    args = parser.parse_args()

    heartbeat = HeartbeatIntegration()

    if args.action == 'run':
        heartbeat.run_heartbeat(force=args.force)
    elif args.action == 'force':
        heartbeat.run_heartbeat(force=True)
    elif args.action == 'status':
        heartbeat.show_status()
    elif args.action == 'config':
        if args.interval:
            heartbeat.config['interval_minutes'] = args.interval
        if args.no_canvas:
            heartbeat.config['auto_canvas_update'] = False
        if args.no_cache:
            heartbeat.config['auto_cache_cleanup'] = False
        heartbeat.save_config(heartbeat.config)
        print(f"✅ Configuration updated")
        heartbeat.show_status()

    return 0


if __name__ == "__main__":
    sys.exit(main())
