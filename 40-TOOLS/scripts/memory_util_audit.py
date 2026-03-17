#!/usr/bin/env python3
"""
Memory Audit Logger - Comprehensive Tracking
=============================================
Tracks all memory operations (distillation, forgetting, conflict resolution)
with before/after state comparison and rollback support.

Features:
- Operation logging (distillation/forgetting/conflict)
- Before/after state comparison
- Rollback support
- Statistics and reporting
- Timeline visualization

Usage:
    # Show recent operations
    python memory_audit_logger.py --recent --limit 20
    
    # Show statistics
    python memory_audit_logger.py --stats --days 7
    
    # Show timeline
    python memory_audit_logger.py --timeline --days 30
    
    # Rollback last operation
    python memory_audit_logger.py --rollback --operation-id OP-001
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class AuditConfig:
    """Audit logger configuration"""
    
    # Paths
    WORKSPACE = os.path.join(os.path.dirname(__file__), '..')
    DATA_DIR = os.path.join(WORKSPACE, 'data')
    
    # Audit logs
    DISTILLATION_LOG = os.path.join(DATA_DIR, 'distillation_audit.json')
    FORGETTING_LOG = os.path.join(DATA_DIR, 'forgetting_audit.json')
    CONFLICT_LOG = os.path.join(DATA_DIR, 'conflict_resolution_audit.json')
    COMBINED_LOG = os.path.join(DATA_DIR, 'memory_audit_combined.json')
    
    # Backup directory
    BACKUP_DIR = os.path.join(DATA_DIR, 'memory_backups')


# ============================================================================
# Audit Logger
# ============================================================================

class MemoryAuditLogger:
    """Combined audit logger for all memory operations"""
    
    def __init__(self, config: AuditConfig = None):
        self.config = config or AuditConfig()
        self._ensure_combined_log()
    
    def _ensure_combined_log(self):
        """Create combined audit log if not exists"""
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        if not os.path.exists(self.config.COMBINED_LOG):
            with open(self.config.COMBINED_LOG, 'w', encoding='utf-8') as f:
                json.dump({'operations': []}, f, indent=2, ensure_ascii=False)
    
    def _load_log(self, log_path: str) -> Dict:
        """Load audit log"""
        if not os.path.exists(log_path):
            return {'operations': []}
        
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _merge_logs(self) -> List[Dict]:
        """Merge all audit logs"""
        all_ops = []
        
        # Load distillation logs
        distill_data = self._load_log(self.config.DISTILLATION_LOG)
        for op in distill_data.get('operations', []):
            op['source'] = 'distillation'
            all_ops.append(op)
        
        # Load forgetting logs
        forget_data = self._load_log(self.config.FORGETTING_LOG)
        for op in forget_data.get('operations', []):
            op['source'] = 'forgetting'
            all_ops.append(op)
        
        # Load conflict logs
        conflict_data = self._load_log(self.config.CONFLICT_LOG)
        for op in conflict_data.get('resolutions', []):
            op['source'] = 'conflict_resolution'
            all_ops.append(op)
        
        # Sort by timestamp
        all_ops.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return all_ops
    
    def get_recent_operations(self, limit: int = 20) -> List[Dict]:
        """Get recent operations"""
        all_ops = self._merge_logs()
        return all_ops[:limit]
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Get statistics for time period"""
        cutoff = datetime.now() - timedelta(days=days)
        all_ops = self._merge_logs()
        
        # Filter by date
        recent_ops = [
            op for op in all_ops
            if datetime.fromisoformat(op.get('timestamp', '1970-01-01')) > cutoff
        ]
        
        # Group by source
        by_source = {}
        for op in recent_ops:
            source = op.get('source', 'unknown')
            by_source[source] = by_source.get(source, 0) + 1
        
        # Group by status
        by_status = {}
        for op in recent_ops:
            status = op.get('status', op.get('result', 'unknown'))
            by_status[status] = by_status.get(status, 0) + 1
        
        # Calculate averages
        avg_quality = 0
        quality_ops = [op for op in recent_ops if 'quality_score' in op]
        if quality_ops:
            avg_quality = sum(op['quality_score'] for op in quality_ops) / len(quality_ops)
        
        return {
            'period_days': days,
            'total_operations': len(recent_ops),
            'by_source': by_source,
            'by_status': by_status,
            'avg_quality_score': avg_quality,
            'operations_per_day': len(recent_ops) / max(days, 1)
        }
    
    def get_timeline(self, days: int = 30) -> List[Dict]:
        """Get timeline of operations"""
        cutoff = datetime.now() - timedelta(days=days)
        all_ops = self._merge_logs()
        
        # Filter and group by date
        timeline = {}
        for op in all_ops:
            timestamp = op.get('timestamp', '')
            if not timestamp:
                continue
            
            op_date = timestamp[:10]  # YYYY-MM-DD
            op_datetime = datetime.fromisoformat(timestamp)
            
            if op_datetime < cutoff:
                continue
            
            if op_date not in timeline:
                timeline[op_date] = {
                    'date': op_date,
                    'count': 0,
                    'operations': []
                }
            
            timeline[op_date]['count'] += 1
            timeline[op_date]['operations'].append({
                'time': timestamp[11:16],  # HH:MM
                'source': op.get('source', 'unknown'),
                'type': op.get('operation', op.get('type', 'unknown')),
                'status': op.get('status', op.get('result', 'unknown'))
            })
        
        # Convert to list and sort
        timeline_list = list(timeline.values())
        timeline_list.sort(key=lambda x: x['date'], reverse=True)
        
        return timeline_list
    
    def rollback_operation(self, operation_id: str) -> Dict:
        """
        Rollback an operation (if backup exists)
        
        Args:
            operation_id: Operation identifier
        
        Returns:
            Rollback result
        """
        # Find operation
        all_ops = self._merge_logs()
        operation = None
        
        for op in all_ops:
            if op.get('id') == operation_id or op.get('conflict_id') == operation_id:
                operation = op
                break
        
        if not operation:
            return {
                'success': False,
                'error': f'Operation {operation_id} not found'
            }
        
        # Check if backup exists
        source = operation.get('source_file', operation.get('source', ''))
        target = operation.get('target', '')
        
        backup_file = None
        if os.path.exists(self.config.BACKUP_DIR):
            for filename in os.listdir(self.config.BACKUP_DIR):
                if source in filename or target in filename:
                    backup_file = os.path.join(self.config.BACKUP_DIR, filename)
                    break
        
        if not backup_file:
            return {
                'success': False,
                'error': 'No backup found for rollback'
            }
        
        # Perform rollback (simplified - would need actual file restoration logic)
        return {
            'success': True,
            'backup_file': backup_file,
            'message': f'Rollback ready. Restore {backup_file} manually.'
        }
    
    def generate_report(self, days: int = 7) -> str:
        """Generate audit report"""
        stats = self.get_statistics(days=days)
        timeline = self.get_timeline(days=days)
        
        report = []
        report.append("# Memory Operations Audit Report")
        report.append("")
        report.append(f"**Period:** Last {days} days")
        report.append(f"**Generated:** {datetime.now().isoformat()}")
        report.append("")
        report.append("## Summary")
        report.append("")
        report.append(f"- Total operations: {stats['total_operations']}")
        report.append(f"- Operations per day: {stats['operations_per_day']:.1f}")
        report.append(f"- Average quality score: {stats['avg_quality_score']:.2f}")
        report.append("")
        report.append("### By Source")
        report.append("")
        for source, count in stats['by_source'].items():
            report.append(f"- {source}: {count}")
        report.append("")
        report.append("### By Status")
        report.append("")
        for status, count in stats['by_status'].items():
            report.append(f"- {status}: {count}")
        report.append("")
        report.append("## Timeline")
        report.append("")
        
        for day in timeline[:10]:  # Last 10 days
            report.append(f"### {day['date']}")
            report.append(f"**{day['count']} operations**")
            report.append("")
            for op in day['operations'][:5]:  # First 5 per day
                report.append(f"- {op['time']} | {op['source']} | {op['type']} | {op['status']}")
            if len(day['operations']) > 5:
                report.append(f"- ... and {len(day['operations']) - 5} more")
            report.append("")
        
        return "\n".join(report)


# ============================================================================
# CLI Interface
# ============================================================================

def show_recent(args):
    """Show recent operations"""
    logger = MemoryAuditLogger()
    operations = logger.get_recent_operations(limit=args.limit or 20)
    
    print(f"\n📋 Recent Memory Operations")
    print("=" * 90)
    print(f"{'Timestamp':<20} {'Source':<20} {'Type':<15} {'Status':<15} {'Details':<20}")
    print("=" * 90)
    
    for op in operations:
        timestamp = op.get('timestamp', 'Unknown')[:19]
        source = op.get('source', 'unknown')[:18]
        op_type = op.get('operation', op.get('type', 'unknown'))[:13]
        status = op.get('status', op.get('result', 'unknown'))[:13]
        
        # Details
        details = ''
        if 'quality_score' in op:
            details = f"Score: {op['quality_score']:.2f}"
        elif 'insights_extracted' in op:
            details = f"Insights: {op['insights_extracted']}"
        elif 'source_file' in op:
            details = op['source_file'][:18]
        
        print(f"{timestamp:<20} {source:<20} {op_type:<15} {status:<15} {details:<20}")
    
    print("=" * 90)


def show_stats(args):
    """Show statistics"""
    logger = MemoryAuditLogger()
    stats = logger.get_statistics(days=args.days or 7)
    
    print(f"\n📊 Memory Operations Statistics")
    print("=" * 60)
    print(f"Period: Last {stats['period_days']} days")
    print("=" * 60)
    print(f"Total operations:    {stats['total_operations']}")
    print(f"Operations per day:  {stats['operations_per_day']:.1f}")
    print(f"Avg quality score:   {stats['avg_quality_score']:.2f}")
    
    print(f"\nBy source:")
    for source, count in stats['by_source'].items():
        print(f"  {source}: {count}")
    
    print(f"\nBy status:")
    for status, count in stats['by_status'].items():
        print(f"  {status}: {count}")
    
    print("=" * 60)


def show_timeline(args):
    """Show timeline"""
    logger = MemoryAuditLogger()
    timeline = logger.get_timeline(days=args.days or 30)
    
    print(f"\n📈 Memory Operations Timeline")
    print("=" * 70)
    print(f"Period: Last {args.days or 30} days")
    print("=" * 70)
    
    for day in timeline[:14]:  # Last 2 weeks
        print(f"\n{day['date']} ({day['count']} ops)")
        print("-" * 70)
        
        for op in day['operations'][:10]:  # First 10
            print(f"  {op['time']} | {op['source']:15} | {op['type']:12} | {op['status']}")
        
        if len(day['operations']) > 10:
            print(f"  ... and {len(day['operations']) - 10} more")
    
    print("=" * 70)


def rollback(args):
    """Rollback operation"""
    logger = MemoryAuditLogger()
    result = logger.rollback_operation(args.operation_id)
    
    if result['success']:
        print(f"✅ Rollback ready")
        print(f"Backup file: {result['backup_file']}")
        print(f"Message: {result['message']}")
    else:
        print(f"❌ Rollback failed: {result['error']}")


def generate_report(args):
    """Generate report"""
    logger = MemoryAuditLogger()
    report = logger.generate_report(days=args.days or 7)
    
    # Save report
    report_path = os.path.join(
        logger.config.DATA_DIR,
        '..',
        '15-docs',
        f"MEMORY-AUDIT-REPORT-{datetime.now().strftime('%Y%m%d')}.md"
    )
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated: {report_path}")
    print("\n" + "=" * 70)
    print(report[:2000])  # Show first part
    if len(report) > 2000:
        print("...")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Memory Audit Logger - Comprehensive Tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show recent operations
  python memory_audit_logger.py --recent --limit 20
  
  # Show statistics
  python memory_audit_logger.py --stats --days 7
  
  # Show timeline
  python memory_audit_logger.py --timeline --days 30
  
  # Rollback operation
  python memory_audit_logger.py --rollback --operation-id OP-001
  
  # Generate report
  python memory_audit_logger.py --report --days 7
        """
    )
    
    parser.add_argument('--recent', action='store_true', help='Show recent operations')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--timeline', action='store_true', help='Show timeline')
    parser.add_argument('--rollback', action='store_true', help='Rollback operation')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    parser.add_argument('--limit', type=int, help='Limit for recent operations')
    parser.add_argument('--days', type=int, help='Days for statistics/timeline')
    parser.add_argument('--operation-id', type=str, help='Operation ID for rollback')
    
    args = parser.parse_args()
    
    if args.recent:
        show_recent(args)
    elif args.stats:
        show_stats(args)
    elif args.timeline:
        show_timeline(args)
    elif args.rollback:
        rollback(args)
    elif args.report:
        generate_report(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    main()
