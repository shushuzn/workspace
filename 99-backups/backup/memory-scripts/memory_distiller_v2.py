#!/usr/bin/env python3
"""
Memory Distiller v2.0 - Quality-Driven Automatic Distillation
=============================================================
Automatically distills high-quality memories (score ≥0.90) to MEMORY.md
with real-time triggering and audit logging.

Features:
- Quality-driven distillation (score ≥0.90 → immediate)
- Batch distillation (Sunday 5AM)
- Audit logging (before/after comparison)
- Value density tracking
- Automatic MEMORY.md updating

Usage:
    # Distill a specific file
    python memory_distiller_v2.py --distill "13-memory-记忆系统/2026-03-17.md"
    
    # Batch distill all weekly notes
    python memory_distiller_v2.py --batch --week 2026-W12
    
    # Check quality threshold
    python memory_distiller_v2.py --check-quality --threshold 0.90
    
    # Run with auto-execute
    python memory_distiller_v2.py --auto-execute --threshold 0.85
"""

import os
import sys
import json
import logging
import argparse
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import quality scorer
try:
    from memory_quality_scorer import MemoryQualityScorer
except ImportError:
    MemoryQualityScorer = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class DistillerConfig:
    """Memory distiller configuration"""
    
    # Paths
    WORKSPACE = os.path.join(os.path.dirname(__file__), '..')
    MEMORY_DIR = os.path.join(WORKSPACE, '13-memory-记忆系统')
    MEMORY_MD = os.path.join(WORKSPACE, 'MEMORY.md')
    ARCHIVE_DIR = os.path.join(MEMORY_DIR, 'archive')
    AUDIT_LOG = os.path.join(WORKSPACE, 'data', 'distillation_audit.json')
    
    # Quality thresholds
    THRESHOLD_IMMEDIATE = 0.90  # Immediate distillation
    THRESHOLD_BATCH = 0.75      # Include in batch distillation
    THRESHOLD_ARCHIVE = 0.50    # Below this → archive candidate
    
    # Backup
    BACKUP_DIR = os.path.join(WORKSPACE, 'data', 'memory_backups')
    BACKUP_RETENTION_DAYS = 7
    
    # Value density tracking
    DENSITY_LOG = os.path.join(WORKSPACE, 'data', 'memory_density.json')


# ============================================================================
# Audit Logger
# ============================================================================

class DistillationAuditor:
    """Audit logger for distillation operations"""
    
    def __init__(self, audit_log_path: str):
        self.audit_log_path = audit_log_path
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create audit log file if not exists"""
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        if not os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, 'w', encoding='utf-8') as f:
                json.dump({'operations': []}, f, indent=2, ensure_ascii=False)
    
    def log_operation(
        self,
        operation: str,
        source_file: str,
        target: str,
        quality_score: float,
        insights_extracted: int,
        before_state: Dict = None,
        after_state: Dict = None,
        status: str = 'success'
    ):
        """Log distillation operation"""
        with open(self.audit_log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        operation_record = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'source_file': source_file,
            'target': target,
            'quality_score': quality_score,
            'insights_extracted': insights_extracted,
            'before_state': before_state or {},
            'after_state': after_state or {},
            'status': status
        }
        
        data['operations'].append(operation_record)
        
        # Keep last 1000 operations
        if len(data['operations']) > 1000:
            data['operations'] = data['operations'][-1000:]
        
        with open(self.audit_log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Audit logged: {operation} on {source_file}")
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict]:
        """Get recent operations"""
        with open(self.audit_log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['operations'][-limit:]
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Get distillation statistics"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with open(self.audit_log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        operations = [
            op for op in data['operations']
            if datetime.fromisoformat(op['timestamp']) > cutoff
        ]
        
        if not operations:
            return {'total': 0, 'avg_score': 0, 'total_insights': 0}
        
        return {
            'total': len(operations),
            'avg_score': sum(op['quality_score'] for op in operations) / len(operations),
            'total_insights': sum(op['insights_extracted'] for op in operations),
            'success_rate': sum(1 for op in operations if op['status'] == 'success') / len(operations) * 100
        }


# ============================================================================
# Value Density Tracker
# ============================================================================

class DensityTracker:
    """Track memory value density over time"""
    
    def __init__(self, density_log_path: str):
        self.density_log_path = density_log_path
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create density log file if not exists"""
        os.makedirs(os.path.dirname(self.density_log_path), exist_ok=True)
        if not os.path.exists(self.density_log_path):
            with open(self.density_log_path, 'w', encoding='utf-8') as f:
                json.dump({'history': []}, f, indent=2, ensure_ascii=False)
    
    def calculate_density(self, memory_file: str) -> float:
        """
        Calculate value density (insights per line)
        
        Density = insight_count / total_lines
        Higher is better (more value per line)
        """
        if not os.path.exists(memory_file):
            return 0.0
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        if total_lines == 0:
            return 0.0
        
        # Count insight markers (e.g., [XXX-001], **, #, -)
        insight_markers = 0
        for line in lines:
            line = line.strip()
            if line.startswith('- [') or line.startswith('**') or line.startswith('#'):
                insight_markers += 1
        
        density = insight_markers / total_lines
        return density
    
    def log_density(self, memory_file: str, density: float, notes: str = ''):
        """Log density measurement"""
        with open(self.density_log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['history'].append({
            'timestamp': datetime.now().isoformat(),
            'file': memory_file,
            'density': density,
            'notes': notes
        })
        
        # Keep last 365 measurements
        if len(data['history']) > 365:
            data['history'] = data['history'][-365:]
        
        with open(self.density_log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_trend(self, days: int = 30) -> str:
        """Get density trend over time"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with open(self.density_log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        recent = [
            d for d in data['history']
            if datetime.fromisoformat(d['timestamp']) > cutoff
        ]
        
        if len(recent) < 2:
            return 'stable'
        
        # Simple trend analysis
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        
        avg_first = sum(d['density'] for d in first_half) / len(first_half)
        avg_second = sum(d['density'] for d in second_half) / len(second_half)
        
        change = (avg_second - avg_first) / avg_first * 100 if avg_first > 0 else 0
        
        if change > 5:
            return 'increasing ↗'
        elif change < -5:
            return 'decreasing ↘'
        else:
            return 'stable →'


# ============================================================================
# Memory Distiller
# ============================================================================

class MemoryDistiller:
    """Main memory distillation engine"""
    
    def __init__(self, config: DistillerConfig = None):
        self.config = config or DistillerConfig()
        self.auditor = DistillationAuditor(self.config.AUDIT_LOG)
        self.density_tracker = DensityTracker(self.config.DENSITY_LOG)
        self.scorer = MemoryQualityScorer() if MemoryQualityScorer else None
    
    def assess_quality(self, file_path: str) -> float:
        """Assess memory quality score"""
        if not self.scorer:
            logger.warning("Quality scorer not available, using default score 0.75")
            return 0.75
        
        try:
            result = self.scorer.score_file(file_path)
            return result.get('overall_score', 0.75)
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return 0.75
    
    def extract_insights(self, file_path: str) -> List[str]:
        """
        Extract insights from memory file
        
        Looks for patterns like:
        - [XXX-001] Lesson learned
        - **Key point**
        - # Header with insight
        """
        insights = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # Pattern 1: [XXX-001] Lesson
            if line.startswith('- [') and ']' in line:
                insights.append(line)
            
            # Pattern 2: **Key point**
            elif line.startswith('**') and line.endswith('**'):
                insights.append(line)
            
            # Pattern 3: Header with content
            elif line.startswith('###') and len(line) > 10:
                insights.append(line)
        
        return insights
    
    def create_backup(self, file_path: str) -> str:
        """Create backup before modification"""
        os.makedirs(self.config.BACKUP_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_path = os.path.join(self.config.BACKUP_DIR, f"{filename}.{timestamp}.bak")
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        
        return backup_path
    
    def distill_to_memory(
        self,
        source_file: str,
        target_file: str = None,
        threshold: float = 0.90,
        auto_execute: bool = False
    ) -> Tuple[bool, str]:
        """
        Distill insights from source file to MEMORY.md
        
        Args:
            source_file: Source memory file
            target_file: Target file (default: MEMORY.md)
            threshold: Minimum quality score
            auto_execute: If True, actually write to file
        
        Returns:
            (success, message)
        """
        target_file = target_file or self.config.MEMORY_MD
        
        # Assess quality
        quality_score = self.assess_quality(source_file)
        logger.info(f"Quality score for {source_file}: {quality_score:.2f}")
        
        if quality_score < threshold:
            return False, f"Quality score {quality_score:.2f} below threshold {threshold}"
        
        # Extract insights
        insights = self.extract_insights(source_file)
        logger.info(f"Extracted {len(insights)} insights")
        
        if not insights:
            return False, "No insights extracted"
        
        # Create audit log before state
        before_state = {}
        if os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8') as f:
                before_state['lines'] = len(f.readlines())
        
        if auto_execute:
            # Create backup
            if os.path.exists(target_file):
                self.create_backup(target_file)
            
            # Append to MEMORY.md
            self._append_insights(target_file, insights, source_file)
        
        # Create audit log after state
        after_state = {}
        if os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8') as f:
                after_state['lines'] = len(f.readlines())
        
        # Log operation
        self.auditor.log_operation(
            operation='distillation',
            source_file=source_file,
            target=target_file,
            quality_score=quality_score,
            insights_extracted=len(insights),
            before_state=before_state,
            after_state=after_state,
            status='success' if auto_execute else 'dry-run'
        )
        
        # Track density
        density = self.density_tracker.calculate_density(target_file)
        self.density_tracker.log_density(target_file, density, f'After distilling {source_file}')
        
        message = f"Distilled {len(insights)} insights (quality: {quality_score:.2f})"
        if not auto_execute:
            message += " [DRY-RUN]"
        
        return True, message
    
    def _append_insights(self, target_file: str, insights: List[str], source_file: str):
        """Append insights to target file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        section = f"\n\n## 📥 Distilled from {os.path.basename(source_file)} ({timestamp})\n\n"
        section += "\n".join(insights)
        section += "\n"
        
        with open(target_file, 'a', encoding='utf-8') as f:
            f.write(section)
        
        logger.info(f"Appended {len(insights)} insights to {target_file}")
    
    def batch_distill(
        self,
        week: str = None,
        threshold: float = 0.75,
        auto_execute: bool = False
    ) -> Dict:
        """
        Batch distill all memories from a week
        
        Args:
            week: Week identifier (e.g., "2026-W12")
            threshold: Minimum quality score
            auto_execute: If True, actually write
        
        Returns:
            Statistics dictionary
        """
        # Find all daily notes
        daily_notes = []
        for filename in os.listdir(self.config.MEMORY_DIR):
            if filename.endswith('.md') and filename[0].isdigit():
                file_path = os.path.join(self.config.MEMORY_DIR, filename)
                
                # Filter by week if specified
                if week:
                    # Simple week filtering (can be enhanced)
                    file_date = datetime.strptime(filename[:10], '%Y-%m-%d')
                    week_num = file_date.isocalendar()[1]
                    if f"W{week_num:02d}" not in week:
                        continue
                
                daily_notes.append(file_path)
        
        logger.info(f"Found {len(daily_notes)} daily notes for batch distillation")
        
        # Process each
        results = {
            'total': len(daily_notes),
            'distilled': 0,
            'skipped': 0,
            'errors': 0,
            'total_insights': 0
        }
        
        for note_path in daily_notes:
            try:
                success, message = self.distill_to_memory(
                    source_file=note_path,
                    threshold=threshold,
                    auto_execute=auto_execute
                )
                
                if success:
                    results['distilled'] += 1
                    # Extract insight count from message
                    if 'insights' in message:
                        count = int(message.split()[1])
                        results['total_insights'] += count
                else:
                    results['skipped'] += 1
                
                logger.info(f"{note_path}: {message}")
            except Exception as e:
                results['errors'] += 1
                logger.error(f"Error processing {note_path}: {e}")
        
        return results
    
    def check_quality_threshold(self, threshold: float = 0.90) -> List[Dict]:
        """Check all daily notes against quality threshold"""
        candidates = []
        
        for filename in os.listdir(self.config.MEMORY_DIR):
            if filename.endswith('.md') and filename[0].isdigit():
                file_path = os.path.join(self.config.MEMORY_DIR, filename)
                score = self.assess_quality(file_path)
                
                if score >= threshold:
                    candidates.append({
                        'file': filename,
                        'score': score,
                        'status': 'ready_for_distillation'
                    })
        
        # Sort by score descending
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates
    
    def cleanup_old_backups(self, retention_days: int = 7):
        """Clean up old backup files"""
        if not os.path.exists(self.config.BACKUP_DIR):
            return
        
        cutoff = datetime.now() - timedelta(days=retention_days)
        cleaned = 0
        
        for filename in os.listdir(self.config.BACKUP_DIR):
            file_path = os.path.join(self.config.BACKUP_DIR, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if mtime < cutoff:
                os.remove(file_path)
                cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} old backups")


# ============================================================================
# CLI Interface
# ============================================================================

def distill_file(args):
    """Distill a single file"""
    distiller = MemoryDistiller()
    success, message = distiller.distill_to_memory(
        source_file=args.file,
        threshold=args.threshold or 0.90,
        auto_execute=args.auto_execute
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"⏭️  {message}")


def batch_distill(args):
    """Batch distill weekly notes"""
    distiller = MemoryDistiller()
    results = distiller.batch_distill(
        week=args.week,
        threshold=args.threshold or 0.75,
        auto_execute=args.auto_execute
    )
    
    print("\n📊 Batch Distillation Results")
    print("=" * 50)
    print(f"Total notes: {results['total']}")
    print(f"Distilled: {results['distilled']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Errors: {results['errors']}")
    print(f"Total insights: {results['total_insights']}")
    print("=" * 50)


def check_quality(args):
    """Check quality threshold"""
    distiller = MemoryDistiller()
    candidates = distiller.check_quality_threshold(args.threshold or 0.90)
    
    print(f"\n📋 Quality Check (threshold ≥{args.threshold or 0.90})")
    print("=" * 50)
    print(f"Found {len(candidates)} candidates:\n")
    
    for candidate in candidates[:20]:  # Show top 20
        print(f"  {candidate['file']}: {candidate['score']:.2f}")
    
    if len(candidates) > 20:
        print(f"  ... and {len(candidates) - 20} more")
    
    print("=" * 50)


def show_audit(args):
    """Show audit log"""
    auditor = DistillationAuditor(DistillerConfig().AUDIT_LOG)
    
    if args.stats:
        stats = auditor.get_statistics(days=args.days or 7)
        print("\n📊 Distillation Statistics")
        print("=" * 50)
        print(f"Period: Last {args.days or 7} days")
        print(f"Total operations: {stats['total']}")
        print(f"Average quality: {stats['avg_score']:.2f}")
        print(f"Total insights: {stats['total_insights']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print("=" * 50)
    else:
        operations = auditor.get_recent_operations(limit=args.limit or 10)
        print("\n📋 Recent Distillation Operations")
        print("=" * 50)
        for op in operations:
            print(f"{op['timestamp'][:16]} | {op['operation']:12} | {op['source_file']:30} | Score: {op['quality_score']:.2f}")
        print("=" * 50)


def show_density(args):
    """Show density trend"""
    tracker = DensityTracker(DistillerConfig().DENSITY_LOG)
    trend = tracker.get_trend(days=args.days or 30)
    
    print(f"\n📈 Memory Value Density Trend")
    print("=" * 50)
    print(f"Period: Last {args.days or 30} days")
    print(f"Trend: {trend}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='Memory Distiller v2.0 - Quality-Driven Automatic Distillation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Distill a single file
  python memory_distiller_v2.py --distill "13-memory-记忆系统/2026-03-17.md"
  
  # Batch distill weekly notes
  python memory_distiller_v2.py --batch --week 2026-W12
  
  # Check quality threshold
  python memory_distiller_v2.py --check-quality --threshold 0.90
  
  # Auto-execute distillation
  python memory_distiller_v2.py --distill file.md --auto-execute
  
  # Show audit statistics
  python memory_distiller_v2.py --audit --stats --days 7
  
  # Show density trend
  python memory_distiller_v2.py --density --days 30
        """
    )
    
    # Distill commands
    parser.add_argument('--distill', type=str, metavar='FILE', help='Distill a single file')
    parser.add_argument('--batch', action='store_true', help='Batch distill weekly notes')
    parser.add_argument('--check-quality', action='store_true', help='Check quality threshold')
    
    # Options
    parser.add_argument('--threshold', type=float, help='Quality threshold')
    parser.add_argument('--week', type=str, help='Week identifier (e.g., 2026-W12)')
    parser.add_argument('--auto-execute', action='store_true', help='Actually write to file')
    
    # Audit commands
    parser.add_argument('--audit', action='store_true', help='Show audit log')
    parser.add_argument('--stats', action='store_true', help='Show audit statistics')
    parser.add_argument('--days', type=int, help='Days for statistics')
    parser.add_argument('--limit', type=int, help='Limit for recent operations')
    
    # Density commands
    parser.add_argument('--density', action='store_true', help='Show density trend')
    
    args = parser.parse_args()
    
    if args.distill:
        distill_file(args)
    elif args.batch:
        batch_distill(args)
    elif args.check_quality:
        check_quality(args)
    elif args.audit:
        show_audit(args)
    elif args.density:
        show_density(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    main()
