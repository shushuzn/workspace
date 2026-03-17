#!/usr/bin/env python3
"""
Memory Forgetting Engine - Automatic Archival
=============================================
Implements Ebbinghaus forgetting curve with automatic archival
for memories with retention score < 0.20.

Features:
- Ebbinghaus curve calculation (R = exp(-t/S))
- Automatic archival (score < 0.20 → archive/)
- Warning markers (score 0.20-0.40 → mark for review)
- Priority modifiers (CRITICAL ×1.5, HIGH ×1.2, etc.)
- Batch execution mode

Usage:
    # Analyze forgetting (dry-run)
    python memory_forgetting.py --analyze
    
    # Execute archival (actual move)
    python memory_forgetting.py --execute
    
    # Show forgetting curve demo
    python memory_forgetting.py --demo --curve
    
    # Evaluate specific file
    python memory_forgetting.py --evaluate "MEMORY.md"
"""

import os
import sys
import json
import math
import logging
import argparse
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
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

class ForgettingConfig:
    """Forgetting engine configuration"""
    
    # Paths
    WORKSPACE = os.path.join(os.path.dirname(__file__), '..')
    MEMORY_DIR = os.path.join(WORKSPACE, '13-memory-记忆系统')
    MEMORY_MD = os.path.join(WORKSPACE, 'MEMORY.md')
    ARCHIVE_DIR = os.path.join(MEMORY_DIR, 'archive')
    
    # Forgetting curve parameters
    # R = exp(-t/S) where S = strength factor
    STRENGTH_FACTOR = 100.0  # Days for R to drop to ~0.37
    
    # Thresholds
    THRESHOLD_FORGET = 0.20   # Below → archive
    THRESHOLD_REVIEW = 0.40   # Below → mark for review
    
    # Priority modifiers
    PRIORITY_MODIFIERS = {
        'CRITICAL': 1.5,
        'HIGH': 1.2,
        'MEDIUM': 1.0,
        'LOW': 0.8
    }
    
    # Audit log
    AUDIT_LOG = os.path.join(WORKSPACE, 'data', 'forgetting_audit.json')


# ============================================================================
# Forgetting Engine
# ============================================================================

class ForgettingEngine:
    """Ebbinghaus forgetting curve engine"""
    
    def __init__(self, config: ForgettingConfig = None):
        self.config = config or ForgettingConfig()
        self._ensure_archive_dir()
        self._ensure_audit_log()
    
    def _ensure_archive_dir(self):
        """Create archive directory if not exists"""
        os.makedirs(self.config.ARCHIVE_DIR, exist_ok=True)
    
    def _ensure_audit_log(self):
        """Create audit log file if not exists"""
        os.makedirs(os.path.dirname(self.config.AUDIT_LOG), exist_ok=True)
        if not os.path.exists(self.config.AUDIT_LOG):
            with open(self.config.AUDIT_LOG, 'w', encoding='utf-8') as f:
                json.dump({'operations': []}, f, indent=2, ensure_ascii=False)
    
    def calculate_retention(
        self,
        created_at: datetime,
        last_reviewed: datetime = None,
        priority: str = 'MEDIUM'
    ) -> float:
        """
        Calculate retention score using Ebbinghaus curve
        
        R = exp(-t/S)
        
        Args:
            created_at: When memory was created
            last_reviewed: When memory was last reviewed (resets decay)
            priority: Memory priority (CRITICAL/HIGH/MEDIUM/LOW)
        
        Returns:
            Retention score (0.0-1.0)
        """
        # Calculate time since creation or last review
        reference_time = last_reviewed or created_at
        days_elapsed = (datetime.now() - reference_time).days
        
        if days_elapsed < 0:
            days_elapsed = 0
        
        # Apply Ebbinghaus curve
        S = self.config.STRENGTH_FACTOR
        R = math.exp(-days_elapsed / S)
        
        # Apply priority modifier
        modifier = self.config.PRIORITY_MODIFIERS.get(priority, 1.0)
        R_adjusted = min(R * modifier, 1.0)  # Cap at 1.0
        
        return R_adjusted
    
    def extract_metadata(self, file_path: str) -> Dict:
        """Extract metadata from memory file"""
        metadata = {
            'created_at': None,
            'last_reviewed': None,
            'priority': 'MEDIUM',
            'insight_count': 0
        }
        
        if not os.path.exists(file_path):
            # Use file modification time
            mtime = os.path.getmtime(file_path)
            metadata['created_at'] = datetime.fromtimestamp(mtime)
            return metadata
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to extract created date from filename
        filename = os.path.basename(file_path)
        if filename[0].isdigit() and '-' in filename:
            try:
                date_str = filename[:10]  # YYYY-MM-DD
                metadata['created_at'] = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                pass
        
        # Try to extract priority from content
        if 'CRITICAL' in content:
            metadata['priority'] = 'CRITICAL'
        elif 'HIGH' in content:
            metadata['priority'] = 'HIGH'
        elif 'LOW' in content:
            metadata['priority'] = 'LOW'
        
        # Count insights
        metadata['insight_count'] = content.count('[INSIGHT-') + content.count('**')
        
        # Use file modification time as fallback
        if not metadata['created_at']:
            mtime = os.path.getmtime(file_path)
            metadata['created_at'] = datetime.fromtimestamp(mtime)
        
        return metadata
    
    def evaluate_file(self, file_path: str) -> Dict:
        """Evaluate a single file for forgetting"""
        metadata = self.extract_metadata(file_path)
        
        retention = self.calculate_retention(
            created_at=metadata['created_at'],
            last_reviewed=metadata['last_reviewed'],
            priority=metadata['priority']
        )
        
        # Determine action
        if retention < self.config.THRESHOLD_FORGET:
            action = 'archive'
        elif retention < self.config.THRESHOLD_REVIEW:
            action = 'review'
        else:
            action = 'retain'
        
        return {
            'file': file_path,
            'filename': os.path.basename(file_path),
            'retention_score': retention,
            'priority': metadata['priority'],
            'age_days': (datetime.now() - metadata['created_at']).days if metadata['created_at'] else 0,
            'insight_count': metadata['insight_count'],
            'action': action,
            'metadata': metadata
        }
    
    def evaluate_all(self, include_memory_md: bool = True) -> List[Dict]:
        """Evaluate all memory files"""
        results = []
        
        # Evaluate daily notes
        if os.path.exists(self.config.MEMORY_DIR):
            for filename in os.listdir(self.config.MEMORY_DIR):
                if filename.endswith('.md') and filename[0].isdigit():
                    file_path = os.path.join(self.config.MEMORY_DIR, filename)
                    result = self.evaluate_file(file_path)
                    results.append(result)
        
        # Evaluate MEMORY.md
        if include_memory_md and os.path.exists(self.config.MEMORY_MD):
            result = self.evaluate_file(self.config.MEMORY_MD)
            result['filename'] = 'MEMORY.md'
            results.append(result)
        
        # Sort by retention score (lowest first)
        results.sort(key=lambda x: x['retention_score'])
        
        return results
    
    def archive_file(self, file_path: str, reason: str = '') -> Tuple[bool, str]:
        """
        Archive a memory file
        
        Args:
            file_path: File to archive
            reason: Reason for archival
        
        Returns:
            (success, message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_path = os.path.join(self.config.ARCHIVE_DIR, f"{timestamp}_{filename}")
        
        try:
            # Move file
            shutil.move(file_path, archive_path)
            
            # Log operation
            self._log_operation('archive', file_path, archive_path, reason)
            
            logger.info(f"Archived: {filename} → {archive_path}")
            return True, f"Archived to {archive_path}"
        except Exception as e:
            logger.error(f"Failed to archive {filename}: {e}")
            return False, str(e)
    
    def mark_for_review(self, file_path: str) -> Tuple[bool, str]:
        """Mark file for review (add warning marker)"""
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add review marker at top
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            marker = f"⚠️ **REVIEW NEEDED** ({timestamp}) - Low retention score\n\n"
            
            if not content.startswith('⚠️'):
                content = marker + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self._log_operation('mark_review', file_path, file_path, 'Low retention score')
                logger.info(f"Marked for review: {file_path}")
            
            return True, "Marked for review"
        except Exception as e:
            logger.error(f"Failed to mark for review: {e}")
            return False, str(e)
    
    def execute_forgetting(self, dry_run: bool = False) -> Dict:
        """
        Execute forgetting process
        
        Args:
            dry_run: If True, only analyze without executing
        
        Returns:
            Statistics dictionary
        """
        results = self.evaluate_all()
        
        stats = {
            'total': len(results),
            'to_archive': 0,
            'to_review': 0,
            'to_retain': 0,
            'archived': 0,
            'marked': 0,
            'errors': 0
        }
        
        for result in results:
            action = result['action']
            
            if action == 'archive':
                stats['to_archive'] += 1
                
                if not dry_run:
                    success, message = self.archive_file(
                        result['file'],
                        reason=f"Retention score {result['retention_score']:.2f} < {self.config.THRESHOLD_FORGET}"
                    )
                    if success:
                        stats['archived'] += 1
                    else:
                        stats['errors'] += 1
            
            elif action == 'review':
                stats['to_review'] += 1
                
                if not dry_run:
                    success, message = self.mark_for_review(result['file'])
                    if success:
                        stats['marked'] += 1
                    else:
                        stats['errors'] += 1
            
            else:  # retain
                stats['to_retain'] += 1
        
        return stats
    
    def _log_operation(self, operation: str, source: str, target: str, reason: str):
        """Log forgetting operation"""
        with open(self.config.AUDIT_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['operations'].append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'source': source,
            'target': target,
            'reason': reason
        })
        
        # Keep last 500 operations
        if len(data['operations']) > 500:
            data['operations'] = data['operations'][-500:]
        
        with open(self.config.AUDIT_LOG, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Get forgetting statistics"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with open(self.config.AUDIT_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        operations = [
            op for op in data['operations']
            if datetime.fromisoformat(op['timestamp']) > cutoff
        ]
        
        if not operations:
            return {'total': 0, 'archived': 0, 'marked': 0}
        
        return {
            'total': len(operations),
            'archived': sum(1 for op in operations if op['operation'] == 'archive'),
            'marked': sum(1 for op in operations if op['operation'] == 'mark_review'),
            'by_reason': self._group_by_reason(operations)
        }
    
    def _group_by_reason(self, operations: List[Dict]) -> Dict:
        """Group operations by reason"""
        reasons = {}
        for op in operations:
            reason = op.get('reason', 'Unknown')[:50]  # Truncate
            reasons[reason] = reasons.get(reason, 0) + 1
        return reasons
    
    def plot_forgetting_curve(self, days: int = 365):
        """Plot forgetting curve (ASCII art)"""
        print("\n📈 Ebbinghaus Forgetting Curve")
        print("=" * 60)
        
        # Calculate curve
        points = []
        for d in range(0, days + 1, 10):
            R = math.exp(-d / self.config.STRENGTH_FACTOR)
            points.append((d, R))
        
        # ASCII plot
        height = 10
        width = len(points)
        
        for row in range(height, -1, -1):
            threshold = row / height
            line = f"{threshold:4.1f} │"
            for d, R in points:
                if R >= threshold:
                    line += "█"
                else:
                    line += " "
            print(line)
        
        print("     └" + "─" * width)
        print(f"      0{' ' * (width//2 - 5)}{days//2}{' ' * (width//2 - 5)}{days} days")
        
        # Show thresholds
        print(f"\nThresholds:")
        print(f"  Archive: R < {self.config.THRESHOLD_FORGET:.2f} (≈{int(-math.log(self.config.THRESHOLD_FORGET) * self.config.STRENGTH_FACTOR)} days)")
        print(f"  Review:  R < {self.config.THRESHOLD_REVIEW:.2f} (≈{int(-math.log(self.config.THRESHOLD_REVIEW) * self.config.STRENGTH_FACTOR)} days)")
        print("=" * 60)


# ============================================================================
# CLI Interface
# ============================================================================

def analyze(args):
    """Analyze forgetting"""
    engine = ForgettingEngine()
    results = engine.evaluate_all()
    
    print(f"\n📊 Forgetting Analysis")
    print("=" * 70)
    print(f"{'File':<40} {'Score':>8} {'Age':>6} {'Priority':>10} {'Action':>12}")
    print("=" * 70)
    
    for result in results[:30]:  # Show top 30
        print(f"{result['filename']:<40} {result['retention_score']:>8.2f} {result['age_days']:>6}d {result['priority']:>10} {result['action']:>12}")
    
    if len(results) > 30:
        print(f"... and {len(results) - 30} more")
    
    print("=" * 70)
    
    # Summary
    to_archive = sum(1 for r in results if r['action'] == 'archive')
    to_review = sum(1 for r in results if r['action'] == 'review')
    to_retain = sum(1 for r in results if r['action'] == 'retain')
    
    print(f"\nSummary:")
    print(f"  To archive: {to_archive}")
    print(f"  To review:  {to_review}")
    print(f"  To retain:  {to_retain}")
    print("=" * 70)


def execute(args):
    """Execute forgetting"""
    engine = ForgettingEngine()
    
    dry_run = args.dry_run
    action = "DRY-RUN" if dry_run else "EXECUTE"
    
    print(f"\n⚠️  Forgetting Engine - {action}")
    print("=" * 70)
    
    if dry_run:
        print("No files will be modified")
    
    stats = engine.execute_forgetting(dry_run=dry_run)
    
    print(f"\n📊 Results")
    print("=" * 70)
    print(f"Total evaluated:    {stats['total']}")
    print(f"To archive:         {stats['to_archive']}")
    print(f"To review:          {stats['to_review']}")
    print(f"To retain:          {stats['to_retain']}")
    print(f"Actually archived:  {stats['archived']}")
    print(f"Actually marked:    {stats['marked']}")
    print(f"Errors:             {stats['errors']}")
    print("=" * 70)


def evaluate_file(args):
    """Evaluate specific file"""
    engine = ForgettingEngine()
    result = engine.evaluate_file(args.file)
    
    print(f"\n📋 File Evaluation: {result['filename']}")
    print("=" * 70)
    print(f"Retention score:  {result['retention_score']:.2f}")
    print(f"Priority:         {result['priority']}")
    print(f"Age:              {result['age_days']} days")
    print(f"Insights:         {result['insight_count']}")
    print(f"Action:           {result['action']}")
    print(f"Thresholds:       Archive <{engine.config.THRESHOLD_FORGET:.2f}, Review <{engine.config.THRESHOLD_REVIEW:.2f}")
    print("=" * 70)


def show_curve(args):
    """Show forgetting curve"""
    engine = ForgettingEngine()
    engine.plot_forgetting_curve(days=args.days or 365)


def show_stats(args):
    """Show statistics"""
    engine = ForgettingEngine()
    stats = engine.get_statistics(days=args.days or 7)
    
    print(f"\n📊 Forgetting Statistics (Last {args.days or 7} days)")
    print("=" * 70)
    print(f"Total operations: {stats['total']}")
    print(f"Archived:         {stats['archived']}")
    print(f"Marked for review: {stats['marked']}")
    
    if stats.get('by_reason'):
        print(f"\nBy reason:")
        for reason, count in stats['by_reason'].items():
            print(f"  {reason}: {count}")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Memory Forgetting Engine - Automatic Archival',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze (dry-run)
  python memory_forgetting.py --analyze
  
  # Execute archival
  python memory_forgetting.py --execute
  
  # Dry-run execution
  python memory_forgetting.py --execute --dry-run
  
  # Evaluate specific file
  python memory_forgetting.py --evaluate "MEMORY.md"
  
  # Show forgetting curve
  python memory_forgetting.py --demo --curve
  
  # Show statistics
  python memory_forgetting.py --stats --days 30
        """
    )
    
    parser.add_argument('--analyze', action='store_true', help='Analyze forgetting (dry-run)')
    parser.add_argument('--execute', action='store_true', help='Execute archival')
    parser.add_argument('--evaluate', type=str, metavar='FILE', help='Evaluate specific file')
    parser.add_argument('--demo', action='store_true', help='Show demo')
    parser.add_argument('--curve', action='store_true', help='Show forgetting curve')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')
    parser.add_argument('--days', type=int, help='Days for statistics/curve')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze(args)
    elif args.execute:
        execute(args)
    elif args.evaluate:
        evaluate_file(args)
    elif args.demo and args.curve:
        show_curve(args)
    elif args.stats:
        show_stats(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    main()
