#!/usr/bin/env python3
"""
Memory Forgetting Mechanism
===========================
Ebbinghaus curve-based intelligent memory pruning.

Features:
- Exponential decay modeling
- Importance-based modifiers
- Usage frequency tracking
- Archive vs. delete decisions
- Forgetting curve visualization

Usage:
    python memory-forgetting.py --memory MEMORY.md
    python memory-forgetting.py --demo --curve
    python memory-forgetting.py --evaluate --output report.json
"""

import os
import sys
import json
import math
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
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
    """Forgetting mechanism configuration"""
    
    # Ebbinghaus curve parameters
    DECAY_RATE = 1/30  # 30-day half-life
    FORGET_THRESHOLD = 0.2  # Below: forget (remove from active)
    ARCHIVE_THRESHOLD = 0.4  # 0.2-0.4: archive, >0.4: retain
    
    # Priority modifiers
    PRIORITY_MODIFIERS = {
        'CRITICAL': 1.5,  # Retain 1.5x longer
        'HIGH': 1.2,
        'MEDIUM': 1.0,
        'LOW': 0.8,  # Forget faster
    }
    
    # Usage frequency modifiers
    USAGE_MODIFIERS = {
        'frequent': 0.8,   # Used in last 7 days
        'occasional': 1.0, # Used in last 30 days
        'rare': 1.2,       # Used in last 90 days
        'never': 1.5,      # Never used
    }
    
    # Memory categories (affects retention)
    CATEGORY_RETENTION = {
        'SECURITY': 1.3,    # Security lessons retained longer
        'WORKFLOW': 1.2,
        'CONFIG': 1.1,
        'LESSON': 1.2,
        'TOOL': 1.0,
        'TEMPORARY': 0.5,   # Temporary info forgotten faster
    }


# ============================================================================
# Ebbinghaus Forgetting Curve
# ============================================================================

class EbbinghausCurve:
    """Ebbinghaus forgetting curve implementation"""
    
    @staticmethod
    def retention(t: float, s: float = 30) -> float:
        """
        Calculate retention probability at time t.
        
        Formula: R = exp(-t/S)
        
        Args:
            t: Time elapsed (days)
            s: Memory strength (days, default 30)
        
        Returns:
            Retention probability (0.0-1.0)
        """
        if t < 0:
            return 1.0
        return math.exp(-t / s)
    
    @staticmethod
    def half_life(retention: float, s: float = 30) -> float:
        """Calculate time to reach specific retention level"""
        if retention <= 0 or retention >= 1:
            return float('inf')
        return -s * math.log(retention)
    
    @staticmethod
    def generate_curve(days: int = 90, s: float = 30) -> List[Dict]:
        """Generate forgetting curve data points"""
        curve = []
        for t in range(days + 1):
            r = EbbinghausCurve.retention(t, s)
            curve.append({
                'day': t,
                'retention': round(r, 4),
                'forgotten': round(1 - r, 4),
            })
        return curve


# ============================================================================
# Memory Forgetting Analyzer
# ============================================================================

class MemoryForgettingAnalyzer:
    """Analyze memories for forgetting decisions"""
    
    def __init__(self, config: ForgettingConfig = None):
        self.config = config or ForgettingConfig()
        self.curve = EbbinghausCurve()
    
    def extract_memory_metadata(self, memory_text: str, memory_id: str) -> Dict:
        """Extract metadata from memory entry"""
        metadata = {
            'id': memory_id,
            'created_date': None,
            'last_used': None,
            'priority': 'MEDIUM',
            'category': 'LESSON',
            'usage_count': 0,
        }
        
        # Extract date (YYYY-MM-DD format)
        import re
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', memory_text)
        if date_match:
            try:
                metadata['created_date'] = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            except:
                pass
        
        # Extract priority
        if 'CRITICAL' in memory_text or '关键' in memory_text:
            metadata['priority'] = 'CRITICAL'
        elif 'HIGH' in memory_text or '高' in memory_text:
            metadata['priority'] = 'HIGH'
        elif 'LOW' in memory_text or '低' in memory_text:
            metadata['priority'] = 'LOW'
        
        # Extract category from ID prefix
        if memory_id.startswith('SEC'):
            metadata['category'] = 'SECURITY'
        elif memory_id.startswith('WORKFLOW') or memory_id.startswith('MULTI'):
            metadata['category'] = 'WORKFLOW'
        elif memory_id.startswith('CONFIG') or memory_id.startswith('SYS'):
            metadata['category'] = 'CONFIG'
        elif memory_id.startswith('TOOL'):
            metadata['category'] = 'TOOL'
        elif memory_id.startswith('TEMP'):
            metadata['category'] = 'TEMPORARY'
        
        return metadata
    
    def calculate_forgetting_score(self, metadata: Dict, current_date: datetime = None) -> Dict:
        """Calculate forgetting score for a memory"""
        if not current_date:
            current_date = datetime.now()
        
        # Time elapsed
        if metadata['created_date']:
            days_elapsed = (current_date - metadata['created_date']).days
        else:
            days_elapsed = 0  # Assume new
        
        # Base retention (Ebbinghaus curve)
        base_retention = self.curve.retention(days_elapsed)
        
        # Apply modifiers
        priority_mod = self.config.PRIORITY_MODIFIERS.get(metadata['priority'], 1.0)
        category_mod = self.config.CATEGORY_RETENTION.get(metadata['category'], 1.0)
        usage_mod = self.config.USAGE_MODIFIERS.get('occasional', 1.0)  # Default
        
        # Adjusted retention
        # Higher modifier = slower forgetting = higher retention
        adjusted_retention = base_retention ** (1.0 / (priority_mod * category_mod * usage_mod))
        adjusted_retention = min(1.0, max(0.0, adjusted_retention))
        
        # Decision
        if adjusted_retention < self.config.FORGET_THRESHOLD:
            decision = 'forget'
            action = 'Remove from active memory (archive or delete)'
        elif adjusted_retention < self.config.ARCHIVE_THRESHOLD:
            decision = 'archive'
            action = 'Move to archive (low priority access)'
        else:
            decision = 'retain'
            action = 'Keep in active memory'
        
        return {
            'memory_id': metadata['id'],
            'days_elapsed': days_elapsed,
            'base_retention': round(base_retention, 4),
            'adjusted_retention': round(adjusted_retention, 4),
            'priority': metadata['priority'],
            'priority_modifier': priority_mod,
            'category': metadata['category'],
            'category_modifier': category_mod,
            'decision': decision,
            'action': action,
            'confidence': round(1.0 - adjusted_retention, 4),  # Confidence in decision
        }
    
    def analyze_memory_file(self, file_path: str) -> Dict:
        """Analyze all memories in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract memory entries (simplified pattern matching)
            import re
            memory_pattern = r'\[([A-Z]+-\d+)\](.*?)(?=\n\[|\Z)'
            matches = re.findall(memory_pattern, content, re.DOTALL)
            
            results = []
            for memory_id, memory_text in matches:
                metadata = self.extract_memory_metadata(memory_text, memory_id)
                score = self.calculate_forgetting_score(metadata)
                score['content_preview'] = memory_text[:100].replace('\n', ' ')
                results.append(score)
            
            # Summary statistics
            total = len(results)
            retain_count = sum(1 for r in results if r['decision'] == 'retain')
            archive_count = sum(1 for r in results if r['decision'] == 'archive')
            forget_count = sum(1 for r in results if r['decision'] == 'forget')
            
            report = {
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'total_memories': total,
                'summary': {
                    'retain': retain_count,
                    'archive': archive_count,
                    'forget': forget_count,
                    'retain_percentage': round(retain_count / total * 100, 1) if total > 0 else 0,
                },
                'memories': results,
            }
            
            return report
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {'error': str(e), 'file_path': file_path}


# ============================================================================
# Visualization
# ============================================================================

def generate_curve_chart(curve_data: List[Dict], output_file: str = 'forgetting_curve.json'):
    """Generate data for forgetting curve visualization"""
    # Save as JSON for external charting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(curve_data, f, indent=2)
    
    logger.info(f"Forgetting curve saved to: {output_file}")
    return output_file


# ============================================================================
# CLI Interface
# ============================================================================

def demo_mode():
    """Run demo with sample memories"""
    print("🧪 Memory Forgetting Mechanism - Demo Mode")
    print("=" * 60)
    
    # Generate Ebbinghaus curve
    print("\n📊 Ebbinghaus Forgetting Curve (30-day half-life):")
    print("-" * 60)
    
    curve = EbbinghausCurve.generate_curve(90)
    
    print(f"{'Day':<8} {'Retention':<12} {'Forgotten':<12}")
    print("-" * 60)
    
    for point in curve[::10]:  # Every 10 days
        print(f"{point['day']:<8} {point['retention']:<12.4f} {point['forgotten']:<12.4f}")
    
    # Sample memory analysis
    print("\n\n🧠 Sample Memory Analysis:")
    print("-" * 60)
    
    analyzer = MemoryForgettingAnalyzer()
    
    samples = [
        {
            'id': 'SEC-001',
            'text': '[SEC-001] 2025-01-15 CRITICAL Security lesson about pre-commit hooks',
            'days_ago': 60,
        },
        {
            'id': 'TEMP-001',
            'text': '[TEMP-001] 2026-03-01 Temporary config for testing',
            'days_ago': 16,
        },
        {
            'id': 'LESSON-050',
            'text': '[LESSON-050] 2025-06-01 General workflow lesson',
            'days_ago': 290,
        },
    ]
    
    current_date = datetime.now()
    
    for sample in samples:
        metadata = analyzer.extract_memory_metadata(sample['text'], sample['id'])
        # Override created_date for demo
        metadata['created_date'] = current_date - timedelta(days=sample['days_ago'])
        
        result = analyzer.calculate_forgetting_score(metadata)
        
        print(f"\n{sample['id']}:")
        print(f"  Age: {sample['days_ago']} days")
        print(f"  Priority: {result['priority']} (modifier: {result['priority_modifier']})")
        print(f"  Category: {result['category']} (modifier: {result['category_modifier']})")
        print(f"  Base Retention: {result['base_retention']:.4f}")
        print(f"  Adjusted Retention: {result['adjusted_retention']:.4f}")
        print(f"  Decision: {result['decision'].upper()}")
        print(f"  Action: {result['action']}")
    
    # Summary
    print("\n\n📈 Forgetting Curve Visualization Data:")
    print("-" * 60)
    print(f"Generated {len(curve)} data points")
    print(f"Day 0: 100% retention")
    print(f"Day 30: {curve[30]['retention']:.2%} retention")
    print(f"Day 60: {curve[60]['retention']:.2%} retention")
    print(f"Day 90: {curve[90]['retention']:.2%} retention")


def main():
    parser = argparse.ArgumentParser(
        description='Memory Forgetting Mechanism - Ebbinghaus-based pruning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze memory file
  python memory-forgetting.py --memory MEMORY.md
  
  # Generate evaluation report
  python memory-forgetting.py --evaluate --output report.json
  
  # Demo mode
  python memory-forgetting.py --demo --curve
        """
    )
    
    parser.add_argument('--memory', '-m', type=str, help='Memory file to analyze')
    parser.add_argument('--evaluate', '-e', action='store_true', help='Generate evaluation report')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--curve', action='store_true', help='Show forgetting curve in demo')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_mode()
    elif args.memory:
        analyzer = MemoryForgettingAnalyzer()
        report = analyzer.analyze_memory_file(args.memory)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Report saved to: {args.output}")
    elif args.evaluate:
        # Placeholder for future evaluation mode
        print("Evaluation mode - coming in Phase 2")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
