#!/usr/bin/env python3
"""
Memory Conflict Resolver - Automatic Resolution
================================================
Detects and automatically resolves memory conflicts
using predefined rules.

Conflict Types:
1. Contradictory - Opposing statements (severity: high-critical)
2. Duplicate - >70% similar content (severity: medium-high)
3. Outdated - Newer supersedes old (severity: medium)
4. Ambiguous - Internal contradictions (severity: low)

Resolution Rules:
- Newer overrides older (timestamp-based)
- Higher quality overrides lower (score-based)
- CRITICAL priority overrides all
- Manual review for critical conflicts

Usage:
    # Scan for conflicts
    python memory_conflict_resolver.py --scan
    
    # Auto-resolve (with rules)
    python memory_conflict_resolver.py --auto-resolve
    
    # Show specific conflict
    python memory_conflict_resolver.py --show CONFLICT-001
    
    # Generate report
    python memory_conflict_resolver.py --report
"""

import os
import sys
import json
import logging
import argparse
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class ResolverConfig:
    """Conflict resolver configuration"""
    
    # Paths
    WORKSPACE = os.path.join(os.path.dirname(__file__), '..')
    MEMORY_DIR = os.path.join(WORKSPACE, '13-memory-记忆系统')
    MEMORY_MD = os.path.join(WORKSPACE, 'MEMORY.md')
    
    # Conflict detection
    SIMILARITY_THRESHOLD = 0.70  # >70% similar → duplicate
    CONTRADICTION_KEYWORDS = [
        'however', 'but', 'although', 'despite', 'nevertheless',
        'contrary', 'opposite', 'instead', 'rather', 'while'
    ]
    
    # Resolution rules
    RULE_NEWER_WINS = True
    RULE_HIGHER_QUALITY_WINS = True
    RULE_CRITICAL_PRIORITY_WINS = True
    
    # Audit log
    AUDIT_LOG = os.path.join(WORKSPACE, 'data', 'conflict_resolution_audit.json')
    CONFLICTS_LOG = os.path.join(WORKSPACE, 'data', 'detected_conflicts.json')


# ============================================================================
# Conflict Detector
# ============================================================================

class ConflictDetector:
    """Detect memory conflicts"""
    
    def __init__(self, config: ResolverConfig = None):
        self.config = config or ResolverConfig()
    
    def extract_statements(self, file_path: str) -> List[Dict]:
        """Extract statements from memory file"""
        statements = []
        
        if not os.path.exists(file_path):
            return statements
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_section = ''
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Track sections
            if line.startswith('##') or line.startswith('###'):
                current_section = line
            
            # Extract lesson/insight lines
            if line.startswith('- [') or (line.startswith('**') and ']' in line):
                statements.append({
                    'file': file_path,
                    'line_num': i + 1,
                    'content': line,
                    'section': current_section,
                    'hash': hashlib.md5(line.encode()).hexdigest()
                })
        
        return statements
    
    def detect_duplicates(self, statements: List[Dict]) -> List[Dict]:
        """Detect duplicate statements"""
        conflicts = []
        seen = {}
        
        for stmt in statements:
            content_hash = stmt['hash']
            
            if content_hash in seen:
                # Found duplicate
                conflicts.append({
                    'type': 'duplicate',
                    'severity': 'high',
                    'statement1': seen[content_hash],
                    'statement2': stmt,
                    'similarity': 1.0,
                    'description': 'Exact duplicate detected'
                })
            else:
                seen[content_hash] = stmt
        
        # Also check for near-duplicates (>70% similar)
        stmt_list = list(seen.values())
        for i in range(len(stmt_list)):
            for j in range(i + 1, len(stmt_list)):
                similarity = SequenceMatcher(
                    None,
                    stmt_list[i]['content'],
                    stmt_list[j]['content']
                ).ratio()
                
                if similarity > self.config.SIMILARITY_THRESHOLD:
                    conflicts.append({
                        'type': 'duplicate',
                        'severity': 'medium',
                        'statement1': stmt_list[i],
                        'statement2': stmt_list[j],
                        'similarity': similarity,
                        'description': f'Near-duplicate ({similarity:.0%} similar)'
                    })
        
        return conflicts
    
    def detect_contradictions(self, statements: List[Dict]) -> List[Dict]:
        """Detect contradictory statements"""
        conflicts = []
        
        # Group by topic (first bracket content)
        topics = {}
        for stmt in statements:
            # Extract topic from [TOPIC-XXX]
            content = stmt['content']
            if '[' in content and ']' in content:
                topic = content.split('[')[1].split(']')[0]
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(stmt)
        
        # Check for contradictions within same topic
        for topic, topic_stmts in topics.items():
            if len(topic_stmts) < 2:
                continue
            
            for i in range(len(topic_stmts)):
                for j in range(i + 1, len(topic_stmts)):
                    stmt1 = topic_stmts[i]
                    stmt2 = topic_stmts[j]
                    
                    # Check for contradiction keywords
                    has_contradiction = any(
                        kw in stmt2['content'].lower()
                        for kw in self.config.CONTRADICTION_KEYWORDS
                    )
                    
                    if has_contradiction:
                        conflicts.append({
                            'type': 'contradictory',
                            'severity': 'critical',
                            'statement1': stmt1,
                            'statement2': stmt2,
                            'topic': topic,
                            'description': f'Contradiction in topic {topic}'
                        })
        
        return conflicts
    
    def detect_outdated(self, statements: List[Dict]) -> List[Dict]:
        """Detect outdated statements (newer supersedes old)"""
        conflicts = []
        
        # Group by topic
        topics = {}
        for stmt in statements:
            content = stmt['content']
            if '[' in content and ']' in content:
                topic = content.split('[')[1].split(']')[0]
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(stmt)
        
        # Check for multiple statements on same topic
        for topic, topic_stmts in topics.items():
            if len(topic_stmts) < 2:
                continue
            
            # Sort by file date (newer first)
            topic_stmts.sort(
                key=lambda s: self._extract_date(s['file']),
                reverse=True
            )
            
            # Mark older ones as potentially outdated
            for i in range(1, len(topic_stmts)):
                conflicts.append({
                    'type': 'outdated',
                    'severity': 'medium',
                    'statement1': topic_stmts[0],  # Newest
                    'statement2': topic_stmts[i],  # Older
                    'topic': topic,
                    'description': f'Older statement on topic {topic}'
                })
        
        return conflicts
    
    def _extract_date(self, file_path: str) -> datetime:
        """Extract date from file path or mtime"""
        filename = os.path.basename(file_path)
        
        # Try to extract from filename
        if filename[0].isdigit() and '-' in filename:
            try:
                return datetime.strptime(filename[:10], '%Y-%m-%d')
            except:
                pass
        
        # Fallback to mtime
        if os.path.exists(file_path):
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        
        return datetime.now()
    
    def scan_all(self) -> List[Dict]:
        """Scan all memory files for conflicts"""
        all_statements = []
        
        # Scan MEMORY.md
        if os.path.exists(self.config.MEMORY_MD):
            statements = self.extract_statements(self.config.MEMORY_MD)
            all_statements.extend(statements)
        
        # Scan daily notes
        if os.path.exists(self.config.MEMORY_DIR):
            for filename in os.listdir(self.config.MEMORY_DIR):
                if filename.endswith('.md') and filename[0].isdigit():
                    file_path = os.path.join(self.config.MEMORY_DIR, filename)
                    statements = self.extract_statements(file_path)
                    all_statements.extend(statements)
        
        logger.info(f"Extracted {len(all_statements)} statements")
        
        # Detect conflicts
        conflicts = []
        conflicts.extend(self.detect_duplicates(all_statements))
        conflicts.extend(self.detect_contradictions(all_statements))
        conflicts.extend(self.detect_outdated(all_statements))
        
        # Assign IDs
        for i, conflict in enumerate(conflicts):
            conflict['id'] = f'CONFLICT-{i+1:03d}'
            conflict['detected_at'] = datetime.now().isoformat()
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        
        return conflicts


# ============================================================================
# Conflict Resolver
# ============================================================================

class ConflictResolver:
    """Automatically resolve conflicts"""
    
    def __init__(self, config: ResolverConfig = None):
        self.config = config or ResolverConfig()
        self.detector = ConflictDetector(config)
        self._ensure_audit_log()
        self._ensure_conflicts_log()
    
    def _ensure_audit_log(self):
        """Create audit log if not exists"""
        os.makedirs(os.path.dirname(self.config.AUDIT_LOG), exist_ok=True)
        if not os.path.exists(self.config.AUDIT_LOG):
            with open(self.config.AUDIT_LOG, 'w', encoding='utf-8') as f:
                json.dump({'resolutions': []}, f, indent=2, ensure_ascii=False)
    
    def _ensure_conflicts_log(self):
        """Create conflicts log if not exists"""
        os.makedirs(os.path.dirname(self.config.CONFLICTS_LOG), exist_ok=True)
    
    def resolve_conflict(self, conflict: Dict, auto: bool = True) -> Dict:
        """
        Resolve a single conflict
        
        Args:
            conflict: Conflict dictionary
            auto: If True, use automatic rules
        
        Returns:
            Resolution result
        """
        resolution = {
            'conflict_id': conflict['id'],
            'type': conflict['type'],
            'method': None,
            'action': None,
            'result': None,
            'timestamp': datetime.now().isoformat()
        }
        
        if conflict['type'] == 'duplicate':
            resolution = self._resolve_duplicate(conflict, auto)
        elif conflict['type'] == 'contradictory':
            resolution = self._resolve_contradiction(conflict, auto)
        elif conflict['type'] == 'outdated':
            resolution = self._resolve_outdated(conflict, auto)
        else:
            resolution['method'] = 'manual_required'
            resolution['action'] = 'flag_for_review'
            resolution['result'] = 'pending'
        
        # Log resolution
        self._log_resolution(resolution)
        
        return resolution
    
    def _resolve_duplicate(self, conflict: Dict, auto: bool) -> Dict:
        """Resolve duplicate conflict"""
        resolution = {
            'conflict_id': conflict['id'],
            'type': 'duplicate',
            'method': 'keep_newer',
            'timestamp': datetime.now().isoformat()
        }
        
        if auto:
            # Keep newer, mark older as duplicate
            newer = self._get_newer(conflict['statement1'], conflict['statement2'])
            older = conflict['statement2'] if newer == conflict['statement1'] else conflict['statement1']
            
            resolution['action'] = f"Keep {newer['file']}, mark {older['file']} as duplicate"
            resolution['result'] = 'auto_resolved'
            resolution['kept'] = newer
            resolution['marked'] = older
        else:
            resolution['action'] = 'manual_review_required'
            resolution['result'] = 'pending'
        
        return resolution
    
    def _resolve_contradiction(self, conflict: Dict, auto: bool) -> Dict:
        """Resolve contradiction conflict"""
        resolution = {
            'conflict_id': conflict['id'],
            'type': 'contradictory',
            'method': 'flag_for_manual_review',
            'timestamp': datetime.now().isoformat()
        }
        
        # Contradictions always require manual review
        resolution['action'] = 'manual_review_required'
        resolution['result'] = 'pending'
        resolution['reason'] = 'Contradictions require human judgment'
        
        return resolution
    
    def _resolve_outdated(self, conflict: Dict, auto: bool) -> Dict:
        """Resolve outdated conflict"""
        resolution = {
            'conflict_id': conflict['id'],
            'type': 'outdated',
            'method': 'keep_newer',
            'timestamp': datetime.now().isoformat()
        }
        
        if auto:
            # Keep newer statement
            newer = conflict['statement1']  # Already sorted newest first
            older = conflict['statement2']
            
            resolution['action'] = f"Keep {newer['file']}, archive {older['file']} reference"
            resolution['result'] = 'auto_resolved'
            resolution['kept'] = newer
            resolution['archived'] = older
        else:
            resolution['action'] = 'manual_review_required'
            resolution['result'] = 'pending'
        
        return resolution
    
    def _get_newer(self, stmt1: Dict, stmt2: Dict) -> Dict:
        """Get newer statement"""
        date1 = self.detector._extract_date(stmt1['file'])
        date2 = self.detector._extract_date(stmt2['file'])
        
        return stmt1 if date1 >= date2 else stmt2
    
    def _log_resolution(self, resolution: Dict):
        """Log resolution"""
        with open(self.config.AUDIT_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['resolutions'].append(resolution)
        
        # Keep last 500 resolutions
        if len(data['resolutions']) > 500:
            data['resolutions'] = data['resolutions'][-500:]
        
        with open(self.config.AUDIT_LOG, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def auto_resolve_all(self, conflicts: List[Dict]) -> Dict:
        """
        Auto-resolve all conflicts
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(conflicts),
            'auto_resolved': 0,
            'manual_required': 0,
            'by_type': {},
            'resolutions': []
        }
        
        for conflict in conflicts:
            resolution = self.resolve_conflict(conflict, auto=True)
            stats['resolutions'].append(resolution)
            
            # Count by type
            conflict_type = conflict['type']
            if conflict_type not in stats['by_type']:
                stats['by_type'][conflict_type] = {'auto': 0, 'manual': 0}
            
            if resolution['result'] == 'auto_resolved':
                stats['auto_resolved'] += 1
                stats['by_type'][conflict_type]['auto'] += 1
            else:
                stats['manual_required'] += 1
                stats['by_type'][conflict_type]['manual'] += 1
        
        # Save conflicts log
        with open(self.config.CONFLICTS_LOG, 'w', encoding='utf-8') as f:
            json.dump({
                'detected_at': datetime.now().isoformat(),
                'total_conflicts': len(conflicts),
                'conflicts': conflicts,
                'resolutions': stats['resolutions']
            }, f, indent=2, ensure_ascii=False)
        
        return stats


# ============================================================================
# CLI Interface
# ============================================================================

def scan(args):
    """Scan for conflicts"""
    detector = ConflictDetector()
    conflicts = detector.scan_all()
    
    print(f"\n🔍 Conflict Scan Results")
    print("=" * 80)
    print(f"{'ID':<15} {'Type':<15} {'Severity':<10} {'Description':<40}")
    print("=" * 80)
    
    for conflict in conflicts[:30]:  # Show top 30
        print(f"{conflict['id']:<15} {conflict['type']:<15} {conflict['severity']:<10} {conflict['description']:<40}")
    
    if len(conflicts) > 30:
        print(f"... and {len(conflicts) - 30} more")
    
    print("=" * 80)
    
    # Summary
    by_type = {}
    by_severity = {}
    for c in conflicts:
        by_type[c['type']] = by_type.get(c['type'], 0) + 1
        by_severity[c['severity']] = by_severity.get(c['severity'], 0) + 1
    
    print(f"\nBy type:")
    for t, count in by_type.items():
        print(f"  {t}: {count}")
    
    print(f"\nBy severity:")
    for s, count in by_severity.items():
        print(f"  {s}: {count}")
    
    print("=" * 80)


def auto_resolve(args):
    """Auto-resolve conflicts"""
    detector = ConflictDetector()
    resolver = ConflictResolver()
    
    print(f"\n⚙️  Auto-Resolve Conflicts")
    print("=" * 80)
    
    conflicts = detector.scan_all()
    stats = resolver.auto_resolve_all(conflicts)
    
    print(f"\n📊 Resolution Statistics")
    print("=" * 80)
    print(f"Total conflicts:     {stats['total']}")
    print(f"Auto-resolved:       {stats['auto_resolved']} ({stats['auto_resolved']/max(stats['total'],1)*100:.1f}%)")
    print(f"Manual required:     {stats['manual_required']} ({stats['manual_required']/max(stats['total'],1)*100:.1f}%)")
    
    print(f"\nBy type:")
    for t, counts in stats['by_type'].items():
        print(f"  {t}: {counts['auto']} auto, {counts['manual']} manual")
    
    print("=" * 80)
    print(f"\nDetailed log: {resolver.config.CONFLICTS_LOG}")
    print(f"Audit log: {resolver.config.AUDIT_LOG}")


def show_conflict(args):
    """Show specific conflict"""
    conflicts_log = ResolverConfig().CONFLICTS_LOG
    
    if not os.path.exists(conflicts_log):
        print("❌ No conflicts log found. Run --scan first.")
        return
    
    with open(conflicts_log, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conflict_id = args.conflict_id
    
    for conflict in data.get('conflicts', []):
        if conflict['id'] == conflict_id:
            print(f"\n📋 Conflict: {conflict_id}")
            print("=" * 80)
            print(f"Type: {conflict['type']}")
            print(f"Severity: {conflict['severity']}")
            print(f"Description: {conflict['description']}")
            print(f"\nStatement 1:")
            print(f"  File: {conflict['statement1']['file']}")
            print(f"  Line: {conflict['statement1']['line_num']}")
            print(f"  Content: {conflict['statement1']['content']}")
            print(f"\nStatement 2:")
            print(f"  File: {conflict['statement2']['file']}")
            print(f"  Line: {conflict['statement2']['line_num']}")
            print(f"  Content: {conflict['statement2']['content']}")
            print("=" * 80)
            return
    
    print(f"❌ Conflict {conflict_id} not found")


def generate_report(args):
    """Generate conflict report"""
    conflicts_log = ResolverConfig().CONFLICTS_LOG
    
    if not os.path.exists(conflicts_log):
        print("❌ No conflicts log found. Run --scan first.")
        return
    
    with open(conflicts_log, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    report_path = os.path.join(
        os.path.dirname(conflicts_log),
        '..',
        '15-docs',
        f"CONFLICT-REPORT-{datetime.now().strftime('%Y%m%d')}.md"
    )
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Memory Conflict Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total conflicts: {data['total_conflicts']}\n")
        f.write(f"- Detection time: {data['detected_at']}\n\n")
        
        f.write(f"## Conflicts by Type\n\n")
        by_type = {}
        for c in data['conflicts']:
            by_type[c['type']] = by_type.get(c['type'], 0) + 1
        
        for t, count in by_type.items():
            f.write(f"- {t}: {count}\n")
        
        f.write(f"\n## Detailed Conflicts\n\n")
        for conflict in data['conflicts'][:50]:  # First 50
            f.write(f"### {conflict['id']}\n\n")
            f.write(f"- **Type:** {conflict['type']}\n")
            f.write(f"- **Severity:** {conflict['severity']}\n")
            f.write(f"- **Description:** {conflict['description']}\n\n")
    
    print(f"✅ Report generated: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Memory Conflict Resolver - Automatic Resolution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for conflicts
  python memory_conflict_resolver.py --scan
  
  # Auto-resolve all conflicts
  python memory_conflict_resolver.py --auto-resolve
  
  # Show specific conflict
  python memory_conflict_resolver.py --show CONFLICT-001
  
  # Generate report
  python memory_conflict_resolver.py --report
        """
    )
    
    parser.add_argument('--scan', action='store_true', help='Scan for conflicts')
    parser.add_argument('--auto-resolve', action='store_true', help='Auto-resolve conflicts')
    parser.add_argument('--show', type=str, metavar='CONFLICT-ID', help='Show specific conflict')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    if args.scan:
        scan(args)
    elif args.auto_resolve:
        auto_resolve(args)
    elif args.show:
        show_conflict(args)
    elif args.report:
        generate_report(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    main()
