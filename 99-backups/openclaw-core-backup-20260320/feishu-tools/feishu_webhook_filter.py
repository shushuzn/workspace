#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu Webhook Event Filter - Filter unwanted events
=====================================================
Features:
- Event type filtering
- Reaction event suppression
- Configurable filters
- Logging level control

Usage:
    python feishu_webhook_filter.py --add-filter im.message.reaction.created_v1
    python feishu_webhook_filter.py --list-filters
    python feishu_webhook_filter.py --test

Author: OpenClaw Team
Date: 2026-03-17
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import List, Set, Optional, Dict, Any

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
SCRIPT_DIR = Path(__file__).parent
FILTER_CONFIG_FILE = SCRIPT_DIR / "feishu-event-filters.json"

# Default filters (unwanted event types)
DEFAULT_FILTERS = {
    'im.message.reaction.created_v1',      # Message reaction (emoji)
    'im.message.reaction.deleted_v1',      # Message reaction removed
    'im.chat.updated_v1',                   # Chat update notifications
    'im.chat.member.updated_v1',            # Chat member changes
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class FeishuEventFilter:
    """Filter Feishu webhook events to suppress unwanted notifications."""

    def __init__(self, config_file: Path = None):
        self.config_file = config_file or FILTER_CONFIG_FILE
        self.filters: Set[str] = set()
        self.load_filters()

    def load_filters(self):
        """Load filters from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.filters = set(config.get('filters', DEFAULT_FILTERS))
                logger.info(f"Loaded {len(self.filters)} filters from config")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Config load error: {e}, using defaults")
                self.filters = DEFAULT_FILTERS.copy()
        else:
            logger.info("No config file found, using default filters")
            self.filters = DEFAULT_FILTERS.copy()
            self.save_filters()

    def save_filters(self):
        """Save filters to config file."""
        config = {
            'filters': list(self.filters),
            'description': 'Feishu webhook event filters - events to ignore',
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.filters)} filters to config")

    def add_filter(self, event_type: str):
        """Add event type to filter list."""
        if event_type not in self.filters:
            self.filters.add(event_type)
            self.save_filters()
            logger.info(f"✅ Added filter: {event_type}")
        else:
            logger.info(f"ℹ️  Filter already exists: {event_type}")

    def remove_filter(self, event_type: str):
        """Remove event type from filter list."""
        if event_type in self.filters:
            self.filters.remove(event_type)
            self.save_filters()
            logger.info(f"✅ Removed filter: {event_type}")
        else:
            logger.warning(f"⚠️  Filter not found: {event_type}")

    def should_filter(self, event_type: str) -> bool:
        """Check if event type should be filtered out."""
        return event_type in self.filters

    def process_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process incoming event, return None if filtered.
        
        Args:
            event_data: Raw event data from Feishu webhook
        
        Returns:
            Processed event data or None if filtered
        """
        event_type = event_data.get('type', event_data.get('header', {}).get('event_type', ''))

        if self.should_filter(event_type):
            logger.debug(f"🚫 Filtered event: {event_type}")
            return None

        logger.debug(f"✅ Passed event: {event_type}")
        return event_data

    def list_filters(self) -> List[str]:
        """Get list of active filters."""
        return sorted(list(self.filters))

    def get_stats(self) -> Dict[str, Any]:
        """Get filter statistics."""
        return {
            'total_filters': len(self.filters),
            'filters': self.list_filters(),
            'config_file': str(self.config_file),
        }


def create_event_processor(filter_instance: FeishuEventFilter):
    """
    Create event processor function for Feishu webhook.
    
    This function should be integrated into your Feishu webhook handler.
    
    Example integration:
    ```python
    from feishu_webhook_filter import FeishuEventFilter, create_event_processor
    
    event_filter = FeishuEventFilter()
    process_event = create_event_processor(event_filter)
    
    @app.route('/feishu/webhook', methods=['POST'])
    def webhook():
        event_data = request.json
        processed = process_event(event_data)
        
        if processed is None:
            # Event was filtered, return success without processing
            return json.dumps({'status': 'filtered'}), 200
        
        # Process the event normally
        return handle_event(processed)
    ```
    """
    def processor(event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return filter_instance.process_event(event_data)

    return processor


def patch_lark_oapi_logger():
    """
    Patch lark_oapi logger to suppress 'processor not found' errors for filtered events.
    
    This prevents error logs for events that are intentionally filtered.
    """
    import logging

    class FilteredEventLogger(logging.Filter):
        def filter(self, record):
            msg = record.getMessage()

            # Suppress 'processor not found' for filtered event types
            if 'processor not found' in msg:
                filtered_types = [
                    'im.message.reaction.created_v1',
                    'im.message.reaction.deleted_v1',
                ]

                for event_type in filtered_types:
                    if event_type in msg:
                        return False  # Suppress this log

            return True  # Allow other logs

    # Get lark_oapi logger
    lark_logger = logging.getLogger('lark_oapi')
    lark_logger.addFilter(FilteredEventLogger())

    logger.info("✅ Patched lark_oapi logger to suppress filtered event errors")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Feishu Webhook Event Filter")
    parser.add_argument('--add-filter', type=str, help='Add event type to filter')
    parser.add_argument('--remove-filter', type=str, help='Remove event type from filter')
    parser.add_argument('--list-filters', action='store_true', help='List active filters')
    parser.add_argument('--stats', action='store_true', help='Show filter statistics')
    parser.add_argument('--test', action='store_true', help='Test filter with sample events')
    parser.add_argument('--patch-logger', action='store_true', help='Patch lark_oapi logger')
    args = parser.parse_args()

    event_filter = FeishuEventFilter()

    if args.add_filter:
        event_filter.add_filter(args.add_filter)

    elif args.remove_filter:
        event_filter.remove_filter(args.remove_filter)

    elif args.list_filters:
        filters = event_filter.list_filters()
        print(f"\n📋 Active Filters ({len(filters)}):")
        print("=" * 60)
        for f in filters:
            print(f"  • {f}")
        print("=" * 60)

    elif args.stats:
        stats = event_filter.get_stats()
        print(f"\n📊 Filter Statistics:")
        print("=" * 60)
        print(f"Total filters: {stats['total_filters']}")
        print(f"Config file: {stats['config_file']}")
        print("\nFilters:")
        for f in stats['filters']:
            print(f"  • {f}")
        print("=" * 60)

    elif args.test:
        print("\n🧪 Testing Event Filter")
        print("=" * 60)

        test_events = [
            {'type': 'im.message.reaction.created_v1', 'data': 'test'},
            {'type': 'im.message.reaction.deleted_v1', 'data': 'test'},
            {'type': 'im.message.receive_v1', 'data': 'test'},
            {'type': 'im.chat.updated_v1', 'data': 'test'},
            {'type': 'unknown_event', 'data': 'test'},
        ]

        for event in test_events:
            result = event_filter.process_event(event)
            status = '🚫 FILTERED' if result is None else '✅ PASSED'
            print(f"  {status}: {event['type']}")

        print("=" * 60)
        print("✅ Test complete!")

    elif args.patch_logger:
        patch_lark_oapi_logger()
        print("\n✅ Logger patched successfully!")
        print("   This suppresses 'processor not found' errors for filtered events.")

    else:
        parser.print_help()

        # Show current filters
        print(f"\n📋 Current Filters ({len(event_filter.list_filters())}):")
        for f in event_filter.list_filters()[:5]:
            print(f"  • {f}")
        if len(event_filter.list_filters()) > 5:
            print(f"  ... and {len(event_filter.list_filters()) - 5} more")


if __name__ == "__main__":
    main()
