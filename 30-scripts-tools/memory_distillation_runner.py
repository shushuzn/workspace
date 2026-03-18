#!/usr/bin/env python3
"""
Memory Distillation System - Integrated Runner
===============================================
Single entry point for all memory distillation operations.
Automates the complete workflow: quality check → distill → forget → resolve conflicts.

Usage:
    # Daily run (quality check + distill high-quality)
    python memory_distillation_runner.py --daily-run
    
    # Weekly run (batch distill + forget + conflicts)
    python memory_distillation_runner.py --weekly-run
    
    # Monthly run (full audit + cleanup)
    python memory_distillation_runner.py --monthly-run
    
    # Status check
    python memory_distillation_runner.py --status
    
    # Manual single file
    python memory_distillation_runner.py --distill "13-memory-记忆系统/2026-03-17.md"
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================================
# Configuration
# ============================================================================

class RunnerConfig:
    """Runner configuration"""
    
    WORKSPACE = os.path.join(os.path.dirname(__file__), '..')
    MEMORY_DIR = os.path.join(WORKSPACE, '13-memory-记忆系统')
    DATA_DIR = os.path.join(WORKSPACE, 'data')
    STATE_FILE = os.path.join(DATA_DIR, 'memory_distillation_state.json')
    
    # Thresholds
    DAILY_THRESHOLD = 0.90
    WEEKLY_THRESHOLD = 0.75
    FORGET_THRESHOLD = 0.20
    CONFLICT_SIMILARITY = 0.70


# ============================================================================
# State Manager
# ============================================================================

class StateManager:
    """Manage distillation state"""
    
    def __init__(self, state_file: str):
        self.state_file = state_file
        self._ensure_state_file()
    
    def _ensure_state_file(self):
        """Create state file if not exists"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        if not os.path.exists(self.state_file):
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'last_daily_run': None,
                    'last_weekly_run': None,
                    'last_monthly_run': None,
                    'total_distilled': 0,
                    'total_archived': 0,
                    'total_conflicts_resolved': 0,
                    'avg_quality_score': 0.0
                }, f, indent=2, ensure_ascii=False)
    
    def load(self) -> Dict:
        """Load state"""
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, state: Dict):
        """Save state"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def update(self, **kwargs):
        """Update state fields"""
        state = self.load()
        for key, value in kwargs.items():
            if key in state:
                state[key] = value
        self.save(state)


# ============================================================================
# Memory Distillation Runner
# ============================================================================

class MemoryDistillationRunner:
    """Integrated memory distillation runner"""
    
    def __init__(self, config: RunnerConfig = None):
        self.config = config or RunnerConfig()
        self.state_manager = StateManager(self.config.STATE_FILE)
    
    def daily_run(self) -> Dict:
        """
        Daily distillation run
        
        1. Check quality (threshold ≥0.90)
        2. Distill high-quality memories
        3. Update state
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting daily distillation run...")
        
        stats = {
            'mode': 'daily',
            'timestamp': datetime.now().isoformat(),
            'files_checked': 0,
            'files_distilled': 0,
            'insights_extracted': 0,
            'avg_quality': 0.0,
            'errors': 0
        }
        
        try:
            # Import distiller
            from memory_distiller_v2 import MemoryDistiller, DistillerConfig
            
            distiller = MemoryDistiller(DistillerConfig())
            
            # Find today's daily note
            today = datetime.now().strftime('%Y-%m-%d')
            today_file = os.path.join(self.config.MEMORY_DIR, f"{today}.md")
            
            if os.path.exists(today_file):
                stats['files_checked'] = 1
                
                # Assess quality
                quality_score = distiller.assess_quality(today_file)
                logger.info(f"Quality score for {today_file}: {quality_score:.2f}")
                
                if quality_score >= self.config.DAILY_THRESHOLD:
                    # Distill
                    success, message = distiller.distill_to_memory(
                        source_file=today_file,
                        threshold=self.config.DAILY_THRESHOLD,
                        auto_execute=True
                    )
                    
                    if success:
                        stats['files_distilled'] = 1
                        # Extract insight count from message
                        if 'insights' in message:
                            try:
                                count = int(message.split()[1])
                                stats['insights_extracted'] = count
                            except:
                                pass
                        stats['avg_quality'] = quality_score
                        
                        logger.info(f"✅ Distilled: {message}")
                    else:
                        stats['errors'] += 1
                        logger.error(f"Distillation failed: {message}")
                else:
                    logger.info(f"⏭️  Skipped (quality {quality_score:.2f} < {self.config.DAILY_THRESHOLD})")
            else:
                logger.info(f"No daily note found for {today}")
            
            # Update state
            state = self.state_manager.load()
            state['last_daily_run'] = datetime.now().isoformat()
            if stats['files_distilled'] > 0:
                state['total_distilled'] += stats['files_distilled']
                # Update average quality
                total = state['total_distilled']
                old_avg = state['avg_quality_score']
                state['avg_quality_score'] = ((old_avg * (total - stats['files_distilled'])) + (stats['avg_quality'] * stats['files_distilled'])) / total
            
            self.state_manager.save(state)
            
            logger.info(f"Daily run complete: {stats['files_distilled']} files distilled")
            
        except ImportError as e:
            logger.error(f"Failed to import distiller: {e}")
            stats['errors'] += 1
        except Exception as e:
            logger.error(f"Daily run failed: {e}")
            stats['errors'] += 1
        
        return stats
    
    def weekly_run(self) -> Dict:
        """
        Weekly distillation run
        
        1. Batch distill all weekly notes
        2. Evaluate forgetting
        3. Scan and resolve conflicts
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting weekly distillation run...")
        
        stats = {
            'mode': 'weekly',
            'timestamp': datetime.now().isoformat(),
            'batch_distilled': 0,
            'total_insights': 0,
            'files_archived': 0,
            'conflicts_resolved': 0,
            'errors': 0
        }
        
        try:
            # Step 1: Batch distillation
            logger.info("Step 1: Batch distillation...")
            from memory_distiller_v2 import MemoryDistiller, DistillerConfig
            
            distiller = MemoryDistiller(DistillerConfig())
            
            # Calculate current week
            now = datetime.now()
            week_num = now.isocalendar()[1]
            week_str = f"{now.year}-W{week_num:02d}"
            
            batch_result = distiller.batch_distill(
                week=week_str,
                threshold=self.config.WEEKLY_THRESHOLD,
                auto_execute=True
            )
            
            stats['batch_distilled'] = batch_result['distilled']
            stats['total_insights'] = batch_result['total_insights']
            
            logger.info(f"Batch distilled: {batch_result['distilled']} files, {batch_result['total_insights']} insights")
            
            # Step 2: Forgetting evaluation (dry-run)
            logger.info("Step 2: Forgetting evaluation...")
            from memory_forgetting_execute import ForgettingEngine, ForgettingConfig
            
            engine = ForgettingEngine(ForgettingConfig())
            forgetting_stats = engine.execute_forgetting(dry_run=True)
            
            logger.info(f"Forgetting analysis: {forgetting_stats['to_archive']} to archive, {forgetting_stats['to_review']} to review")
            
            # Step 3: Conflict resolution
            logger.info("Step 3: Conflict resolution...")
            from memory_conflict_resolver import ConflictDetector, ConflictResolver, ResolverConfig
            
            detector = ConflictDetector(ResolverConfig())
            resolver = ConflictResolver(ResolverConfig())
            
            conflicts = detector.scan_all()
            resolution_stats = resolver.auto_resolve_all(conflicts)
            
            stats['conflicts_resolved'] = resolution_stats['auto_resolved']
            
            logger.info(f"Conflicts: {resolution_stats['auto_resolved']} auto-resolved, {resolution_stats['manual_required']} manual required")
            
            # Update state
            state = self.state_manager.load()
            state['last_weekly_run'] = datetime.now().isoformat()
            state['total_distilled'] += stats['batch_distilled']
            state['total_conflicts_resolved'] += stats['conflicts_resolved']
            self.state_manager.save(state)
            
            logger.info(f"Weekly run complete!")
            
        except ImportError as e:
            logger.error(f"Failed to import tools: {e}")
            stats['errors'] += 1
        except Exception as e:
            logger.error(f"Weekly run failed: {e}")
            stats['errors'] += 1
        
        return stats
    
    def monthly_run(self) -> Dict:
        """
        Monthly distillation run
        
        1. Generate audit report
        2. Clean up old backups
        3. Analyze density trend
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting monthly distillation run...")
        
        stats = {
            'mode': 'monthly',
            'timestamp': datetime.now().isoformat(),
            'report_generated': False,
            'backups_cleaned': 0,
            'density_trend': 'unknown',
            'errors': 0
        }
        
        try:
            # Step 1: Audit report
            logger.info("Step 1: Generating audit report...")
            from memory_audit_logger import MemoryAuditLogger, AuditConfig
            
            audit_logger = MemoryAuditLogger(AuditConfig())
            report = audit_logger.generate_report(days=30)
            
            # Save report
            report_path = os.path.join(
                self.config.WORKSPACE,
                '15-docs',
                f"MEMORY-MONTHLY-REPORT-{datetime.now().strftime('%Y%m')}.md"
            )
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            stats['report_generated'] = True
            logger.info(f"Audit report saved: {report_path}")
            
            # Step 2: Clean up backups
            logger.info("Step 2: Cleaning up old backups...")
            from memory_distiller_v2 import MemoryDistiller, DistillerConfig
            
            distiller = MemoryDistiller(DistillerConfig())
            distiller.cleanup_old_backups(retention_days=30)
            
            # Count remaining backups
            backup_dir = distiller.config.BACKUP_DIR
            if os.path.exists(backup_dir):
                stats['backups_cleaned'] = len(os.listdir(backup_dir))
            
            # Step 3: Density trend
            logger.info("Step 3: Analyzing density trend...")
            density_trend = distiller.density_tracker.get_trend(days=30)
            stats['density_trend'] = density_trend
            
            logger.info(f"Density trend: {density_trend}")
            
            # Update state
            state = self.state_manager.load()
            state['last_monthly_run'] = datetime.now().isoformat()
            self.state_manager.save(state)
            
            logger.info(f"Monthly run complete!")
            
        except ImportError as e:
            logger.error(f"Failed to import tools: {e}")
            stats['errors'] += 1
        except Exception as e:
            logger.error(f"Monthly run failed: {e}")
            stats['errors'] += 1
        
        return stats
    
    def get_status(self) -> Dict:
        """Get current status"""
        state = self.state_manager.load()
        
        # Calculate time since last runs
        def time_since(iso_string: str) -> str:
            if not iso_string:
                return "Never"
            last_run = datetime.fromisoformat(iso_string)
            delta = datetime.now() - last_run
            if delta.days > 0:
                return f"{delta.days} days ago"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} hours ago"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60} minutes ago"
            else:
                return "Just now"
        
        return {
            'last_daily_run': time_since(state['last_daily_run']),
            'last_weekly_run': time_since(state['last_weekly_run']),
            'last_monthly_run': time_since(state['last_monthly_run']),
            'total_distilled': state['total_distilled'],
            'total_archived': state['total_archived'],
            'total_conflicts_resolved': state['total_conflicts_resolved'],
            'avg_quality_score': state['avg_quality_score']
        }
    
    def distill_single_file(self, file_path: str) -> Dict:
        """Distill a single file"""
        stats = {
            'mode': 'manual',
            'file': file_path,
            'success': False,
            'message': '',
            'quality_score': 0.0,
            'insights': 0
        }
        
        try:
            from memory_distiller_v2 import MemoryDistiller, DistillerConfig
            
            distiller = MemoryDistiller(DistillerConfig())
            
            # Check if file exists
            if not os.path.exists(file_path):
                stats['message'] = f"File not found: {file_path}"
                return stats
            
            # Assess quality
            quality_score = distiller.assess_quality(file_path)
            stats['quality_score'] = quality_score
            
            # Distill
            success, message = distiller.distill_to_memory(
                source_file=file_path,
                threshold=0.75,
                auto_execute=True
            )
            
            stats['success'] = success
            stats['message'] = message
            
            if success:
                # Extract insight count
                if 'insights' in message:
                    try:
                        count = int(message.split()[1])
                        stats['insights'] = count
                    except:
                        pass
            
            return stats
            
        except Exception as e:
            stats['message'] = str(e)
            return stats


# ============================================================================
# CLI Interface
# ============================================================================

def daily_run(args):
    """Daily run"""
    runner = MemoryDistillationRunner()
    stats = runner.daily_run()
    
    print("\n📊 Daily Distillation Run")
    print("=" * 60)
    print(f"Timestamp: {stats['timestamp']}")
    print(f"Files checked: {stats['files_checked']}")
    print(f"Files distilled: {stats['files_distilled']}")
    print(f"Insights extracted: {stats['insights_extracted']}")
    print(f"Average quality: {stats['avg_quality']:.2f}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)


def weekly_run(args):
    """Weekly run"""
    runner = MemoryDistillationRunner()
    stats = runner.weekly_run()
    
    print("\n📊 Weekly Distillation Run")
    print("=" * 60)
    print(f"Timestamp: {stats['timestamp']}")
    print(f"Batch distilled: {stats['batch_distilled']}")
    print(f"Total insights: {stats['total_insights']}")
    print(f"Files archived: {stats['files_archived']}")
    print(f"Conflicts resolved: {stats['conflicts_resolved']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)


def monthly_run(args):
    """Monthly run"""
    runner = MemoryDistillationRunner()
    stats = runner.monthly_run()
    
    print("\n📊 Monthly Distillation Run")
    print("=" * 60)
    print(f"Timestamp: {stats['timestamp']}")
    print(f"Report generated: {stats['report_generated']}")
    print(f"Backups remaining: {stats['backups_cleaned']}")
    print(f"Density trend: {stats['density_trend']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)


def show_status(args):
    """Show status"""
    runner = MemoryDistillationRunner()
    status = runner.get_status()
    
    print("\n📊 Memory Distillation Status")
    print("=" * 60)
    print(f"Last daily run: {status['last_daily_run']}")
    print(f"Last weekly run: {status['last_weekly_run']}")
    print(f"Last monthly run: {status['last_monthly_run']}")
    print(f"Total distilled: {status['total_distilled']}")
    print(f"Total archived: {status['total_archived']}")
    print(f"Conflicts resolved: {status['total_conflicts_resolved']}")
    print(f"Average quality: {status['avg_quality_score']:.2f}")
    print("=" * 60)


def distill_file(args):
    """Distill single file"""
    runner = MemoryDistillationRunner()
    stats = runner.distill_single_file(args.distill_file)
    
    print(f"\n📊 Manual Distillation: {stats['file']}")
    print("=" * 60)
    print(f"Quality score: {stats['quality_score']:.2f}")
    print(f"Success: {stats['success']}")
    print(f"Message: {stats['message']}")
    if stats['success']:
        print(f"Insights extracted: {stats['insights']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Memory Distillation System - Integrated Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily run
  python memory_distillation_runner.py --daily-run
  
  # Weekly run
  python memory_distillation_runner.py --weekly-run
  
  # Monthly run
  python memory_distillation_runner.py --monthly-run
  
  # Status check
  python memory_distillation_runner.py --status
  
  # Manual distillation
  python memory_distillation_runner.py --distill "13-memory-记忆系统/2026-03-17.md"
        """
    )
    
    parser.add_argument('--daily-run', action='store_true', help='Daily distillation run')
    parser.add_argument('--weekly-run', action='store_true', help='Weekly distillation run')
    parser.add_argument('--monthly-run', action='store_true', help='Monthly distillation run')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--distill', type=str, dest='distill_file', metavar='FILE', help='Distill single file')
    
    args = parser.parse_args()
    
    if args.daily_run:
        daily_run(args)
    elif args.weekly_run:
        weekly_run(args)
    elif args.monthly_run:
        monthly_run(args)
    elif args.status:
        show_status(args)
    elif args.distill_file:
        distill_file(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
