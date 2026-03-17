#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Conflict Detector - Identify contradictory or conflicting memories
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict, field
import re

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
MEMORY_FILE = MEMORY_DIR / 'MEMORY.md'
CONFLICT_DIR = WORKSPACE / 'data' / 'memory_conflicts'
CONFLICT_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Conflict:
    """Represents a conflict between memories"""
    conflict_id: str
    memory1_id: str
    memory2_id: str
    conflict_type: str  # contradictory, duplicate, outdated, ambiguous
    severity: str  # critical, high, medium, low
    description: str
    evidence: List[str] = field(default_factory=list)
    resolution_suggestion: str = ""
    confidence: float = 0.0
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())

class MemoryConflictDetector:
    """
    Detects various types of conflicts in memory:
    1. Contradictory (directly opposing statements)
    2. Duplicate (nearly identical content)
    3. Outdated (newer info supersedes older)
    4. Ambiguous (unclear or conflicting within same memory)
    """
    
    def __init__(self):
        # Contradiction indicators
        self.contradiction_patterns = [
            (r'(?i)should\s+not', r'(?i)should'),
            (r'(?i)never', r'(?i)always'),
            (r'(?i)disable', r'(?i)enable'),
            (r'(?i)avoid', r'(?i)use'),
            (r'(?i)don\'t', r'(?i)do'),
            (r'(?i)cannot', r'(?i)can'),
            (r'(?i)must\s+not', r'(?i)must'),
            (r'(?i)incorrect', r'(?i)correct'),
            (r'(?i)wrong', r'(?i)right'),
            (r'(?i)false', r'(?i>true'),
            # Chinese patterns
            (r'不应该', r'应该'),
            (r'不要', r'要'),
            (r'禁止', r'允许'),
            (r'错误', r'正确'),
            (r'避免', r'使用'),
        ]
        
        # Severity thresholds
        self.severity_thresholds = {
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5,
            'low': 0.3,
        }
    
    def detect_contradictions(self, text1: str, text2: str, 
                            id1: str, id2: str) -> List[Conflict]:
        """Detect contradictory statements between two memories"""
        conflicts = []
        
        for pattern1, pattern2 in self.contradiction_patterns:
            has_pattern1 = re.search(pattern1, text1)
            has_pattern2 = re.search(pattern2, text2)
            
            if has_pattern1 and has_pattern2:
                # Check if they're talking about similar topics
                similarity = self._topic_similarity(text1, text2)
                
                if similarity > 0.4:  # Same topic area
                    conflict = Conflict(
                        conflict_id=f"conflict_{id1}_{id2}",
                        memory1_id=id1,
                        memory2_id=id2,
                        conflict_type='contradictory',
                        severity=self._calculate_severity(similarity, 0.8),
                        description=f"Contradictory statements detected: '{has_pattern1.group()}' vs '{has_pattern2.group()}'",
                        evidence=[
                            f"Memory {id1}: ...{has_pattern1.group()}...",
                            f"Memory {id2}: ...{has_pattern2.group()}...",
                            f"Topic similarity: {similarity:.2f}"
                        ],
                        resolution_suggestion="Review both memories and determine which is correct based on recency and source credibility",
                        confidence=min(similarity + 0.2, 1.0)
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def detect_duplicates(self, text1: str, text2: str,
                         id1: str, id2: str) -> List[Conflict]:
        """Detect duplicate or near-duplicate memories"""
        conflicts = []
        
        # Calculate similarity
        similarity = self._jaccard_similarity(text1, text2)
        
        if similarity > 0.7:  # High similarity
            conflict = Conflict(
                conflict_id=f"duplicate_{id1}_{id2}",
                memory1_id=id1,
                memory2_id=id2,
                conflict_type='duplicate',
                severity=self._calculate_severity(similarity, 0.9),
                description=f"Near-duplicate content detected ({similarity:.1%} similar)",
                evidence=[
                    f"Similarity score: {similarity:.3f}",
                    f"Memory {id1} length: {len(text1)} chars",
                    f"Memory {id2} length: {len(text2)} chars"
                ],
                resolution_suggestion="Merge the two memories or delete the redundant one",
                confidence=similarity
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def detect_outdated(self, text1: str, text2: str,
                       id1: str, id2: str,
                       date1: str, date2: str) -> List[Conflict]:
        """Detect if one memory makes another outdated"""
        conflicts = []
        
        # Parse dates
        try:
            d1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
            d2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
        except:
            return conflicts
        
        # Check for version indicators
        version_patterns = [
            r'v(\d+\.\d+)',
            r'version\s*(\d+)',
            r'(\d+)\.0',
        ]
        
        v1 = self._extract_version(text1, version_patterns)
        v2 = self._extract_version(text2, version_patterns)
        
        if v1 and v2 and v2 > v1:
            conflict = Conflict(
                conflict_id=f"outdated_{id1}_{id2}",
                memory1_id=id1,
                memory2_id=id2,
                conflict_type='outdated',
                severity='medium',
                description=f"Memory {id1} (v{v1}) may be outdated by {id2} (v{v2})",
                evidence=[
                    f"Version in {id1}: {v1}",
                    f"Version in {id2}: {v2}",
                    f"Date {id1}: {d1.strftime('%Y-%m-%d')}",
                    f"Date {id2}: {d2.strftime('%Y-%m-%d')}"
                ],
                resolution_suggestion=f"Archive {id1} and keep {id2} as the authoritative version",
                confidence=0.85
            )
            conflicts.append(conflict)
        
        # Check for "replaces" or "supersedes" language
        replaces_patterns = [
            r'(?i)replaces?\s+(\w+-\d+)',
            r'(?i)supersedes?\s+(\w+-\d+)',
            r'(?i)updated\s+version\s+of\s+(\w+-\d+)',
        ]
        
        for pattern in replaces_patterns:
            match = re.search(pattern, text2)
            if match and id1 in match.group():
                conflict = Conflict(
                    conflict_id=f"superseded_{id1}_{id2}",
                    memory1_id=id1,
                    memory2_id=id2,
                    conflict_type='outdated',
                    severity='high',
                    description=f"Memory {id2} explicitly supersedes {id1}",
                    evidence=[
                        f"Supersession statement in {id2}",
                        f"Date {id1}: {d1.strftime('%Y-%m-%d')}",
                        f"Date {id2}: {d2.strftime('%Y-%m-%d')}"
                    ],
                    resolution_suggestion=f"Archive {id1} and mark as superseded by {id2}",
                    confidence=0.95
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_internal_conflicts(self, text: str, memory_id: str) -> List[Conflict]:
        """Detect conflicts within a single memory"""
        conflicts = []
        
        # Split into sections
        sections = text.split('\n\n')
        
        for i, s1 in enumerate(sections):
            for j, s2 in enumerate(sections[i+1:], i+1):
                for pattern1, pattern2 in self.contradiction_patterns[:5]:  # Top 5 patterns
                    has_p1 = re.search(pattern1, s1)
                    has_p2 = re.search(pattern2, s2)
                    
                    if has_p1 and has_p2:
                        conflict = Conflict(
                            conflict_id=f"internal_{memory_id}_{i}_{j}",
                            memory1_id=memory_id,
                            memory2_id=memory_id,
                            conflict_type='ambiguous',
                            severity='low',
                            description=f"Internal contradiction in memory {memory_id}",
                            evidence=[
                                f"Section {i}: ...{has_p1.group()}...",
                                f"Section {j}: ...{has_p2.group()}..."
                            ],
                            resolution_suggestion="Clarify the memory to resolve internal inconsistency",
                            confidence=0.6
                        )
                        conflicts.append(conflict)
                        break  # One conflict per section pair
        
        return conflicts
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _topic_similarity(self, text1: str, text2: str) -> float:
        """Calculate topic similarity based on key terms"""
        # Extract key terms (nouns, technical terms)
        def extract_key_terms(text):
            # Remove common words
            stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                         'be', 'been', 'being', 'have', 'has', 'had'}
            words = text.lower().split()
            key_terms = set()
            for word in words:
                if len(word) > 4 and word not in stop_words:
                    key_terms.add(word)
            return key_terms
        
        terms1 = extract_key_terms(text1)
        terms2 = extract_key_terms(text2)
        
        if not terms1 or not terms2:
            return 0.0
        
        overlap = terms1 & terms2
        return len(overlap) / max(len(terms1 | terms2), 1)
    
    def _extract_version(self, text: str, patterns: List[str]) -> float:
        """Extract version number from text"""
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        return None
    
    def _calculate_severity(self, score: float, threshold: float) -> str:
        """Calculate severity based on score and threshold"""
        ratio = score / threshold
        
        if ratio >= 1.0:
            return 'critical'
        elif ratio >= 0.8:
            return 'high'
        elif ratio >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def scan_all(self, memories: List[Dict]) -> List[Conflict]:
        """Scan all memories for conflicts"""
        all_conflicts = []
        n = len(memories)
        
        print(f"🔍 Scanning {n} memories for conflicts...")
        
        # Pairwise comparison
        for i in range(n):
            mem1 = memories[i]
            
            # Internal conflicts
            internal = self.detect_internal_conflicts(
                mem1.get('content', ''),
                mem1['id']
            )
            all_conflicts.extend(internal)
            
            # Pairwise conflicts
            for j in range(i + 1, n):
                mem2 = memories[j]
                
                # Contradictions
                contradictions = self.detect_contradictions(
                    mem1.get('content', ''),
                    mem2.get('content', ''),
                    mem1['id'],
                    mem2['id']
                )
                all_conflicts.extend(contradictions)
                
                # Duplicates
                duplicates = self.detect_duplicates(
                    mem1.get('content', ''),
                    mem2.get('content', ''),
                    mem1['id'],
                    mem2['id']
                )
                all_conflicts.extend(duplicates)
                
                # Outdated
                outdated = self.detect_outdated(
                    mem1.get('content', ''),
                    mem2.get('content', ''),
                    mem1['id'],
                    mem2['id'],
                    mem1.get('created_at', ''),
                    mem2.get('created_at', '')
                )
                all_conflicts.extend(outdated)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_conflicts.sort(key=lambda c: severity_order.get(c.severity, 4))
        
        return all_conflicts
    
    def generate_report(self, conflicts: List[Conflict]) -> Dict:
        """Generate conflict analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_conflicts': len(conflicts),
                'by_type': {},
                'by_severity': {},
            },
            'critical_conflicts': [],
            'recommendations': []
        }
        
        # Count by type and severity
        for conflict in conflicts:
            # By type
            ctype = conflict.conflict_type
            report['summary']['by_type'][ctype] = \
                report['summary']['by_type'].get(ctype, 0) + 1
            
            # By severity
            sev = conflict.severity
            report['summary']['by_severity'][sev] = \
                report['summary']['by_severity'].get(sev, 0) + 1
            
            # Critical conflicts
            if conflict.severity in ['critical', 'high']:
                report['critical_conflicts'].append(asdict(conflict))
        
        # Generate recommendations
        if report['summary']['by_type'].get('duplicate', 0) > 5:
            report['recommendations'].append(
                "Consider implementing deduplication during memory creation"
            )
        if report['summary']['by_type'].get('contradictory', 0) > 3:
            report['recommendations'].append(
                "Review contradictory memories and establish authoritative sources"
            )
        if report['summary']['by_severity'].get('critical', 0) > 0:
            report['recommendations'].append(
                f"URGENT: Address {report['summary']['by_severity']['critical']} critical conflicts immediately"
            )
        
        return report
    
    def save_report(self, report: Dict, conflicts: List[Conflict]):
        """Save conflict report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = CONFLICT_DIR / f'conflict_report_{timestamp}.json'
        
        output_data = {
            'report': report,
            'all_conflicts': [asdict(c) for c in conflicts]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conflict report saved to: {output_file}")
        return output_file

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Conflict Detector")
    parser.add_argument('--scan', action='store_true',
                       help='Scan MEMORY.md for conflicts')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo with sample data')
    args = parser.parse_args()
    
    detector = MemoryConflictDetector()
    
    if args.demo:
        print("\n⚠️  Memory Conflict Detector Demo")
        print("=" * 80)
        
        # Sample memories with conflicts
        samples = [
            {
                'id': 'mem_001',
                'content': 'You should always use environment variables for secrets. Never hardcode passwords.',
                'created_at': '2026-03-15T10:00:00'
            },
            {
                'id': 'mem_002',
                'content': 'For development, you can hardcode passwords in config files for convenience.',
                'created_at': '2026-03-16T10:00:00'
            },
            {
                'id': 'mem_003',
                'content': 'Memory distillation achieves 5.6x compression with Qwen2.5:1.5b',
                'created_at': '2026-03-16T09:00:00'
            },
            {
                'id': 'mem_004',
                'content': 'Memory distillation achieves 5.6x compression with Qwen2.5:1.5b',
                'created_at': '2026-03-16T09:30:00'
            }
        ]
        
        conflicts = detector.scan_all(samples)
        
        print(f"\n📊 Conflict Summary:")
        print(f"   Total conflicts found: {len(conflicts)}")
        
        if conflicts:
            print(f"\n⚠️  Detected Conflicts:")
            for conflict in conflicts:
                print(f"\n   [{conflict.severity.upper()}] {conflict.conflict_type}")
                print(f"   ID: {conflict.conflict_id}")
                print(f"   Memories: {conflict.memory1_id} ↔ {conflict.memory2_id}")
                print(f"   Description: {conflict.description}")
                print(f"   Confidence: {conflict.confidence:.1%}")
                print(f"   Resolution: {conflict.resolution_suggestion}")
        else:
            print(f"   ✅ No conflicts detected!")
        
        # Report
        report = detector.generate_report(conflicts)
        print(f"\n📈 Statistics:")
        print(f"   By type: {report['summary']['by_type']}")
        print(f"   By severity: {report['summary']['by_severity']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
    
    elif args.scan:
        # Load MEMORY.md
        if not MEMORY_FILE.exists():
            print(f"❌ Memory file not found: {MEMORY_FILE}")
            return
        
        print(f"📖 Loading memories from {MEMORY_FILE}...")
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple parsing
        sections = content.split('###')[1:]
        memories = []
        
        for i, section in enumerate(sections):
            memories.append({
                'id': f'mem_{i:03d}',
                'content': section.strip(),
                'created_at': datetime.now().isoformat()
            })
        
        print(f"✅ Loaded {len(memories)} memories")
        
        # Scan
        conflicts = detector.scan_all(memories)
        
        # Report
        report = detector.generate_report(conflicts)
        print(f"\n📊 Results:")
        print(f"   Total conflicts: {len(conflicts)}")
        print(f"   By type: {report['summary']['by_type']}")
        print(f"   By severity: {report['summary']['by_severity']}")
        
        # Save
        detector.save_report(report, conflicts)
        print(f"\n✅ Scan complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
