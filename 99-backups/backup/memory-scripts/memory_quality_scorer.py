#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Quality Scorer - Evaluate memory quality across multiple dimensions
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
MEMORY_FILE = MEMORY_DIR / 'MEMORY.md'

@dataclass
class QualityReport:
    """Quality assessment report"""
    memory_id: str
    overall_score: float
    dimensions: Dict[str, float]
    grade: str  # A/B/C/D/F
    issues: List[str]
    recommendations: List[str]
    timestamp: str

class MemoryQualityScorer:
    """
    Multi-dimensional memory quality scoring
    Dimensions: completeness, clarity, relevance, uniqueness, actionability
    """
    
    def __init__(self):
        self.weights = {
            'completeness': 0.25,
            'clarity': 0.20,
            'relevance': 0.25,
            'uniqueness': 0.15,
            'actionability': 0.15,
        }
        
        self.grade_thresholds = {
            'A': 0.90,
            'B': 0.75,
            'C': 0.60,
            'D': 0.50,
            'F': 0.0,
        }
    
    def score_completeness(self, content: str) -> float:
        """
        Score completeness (0-1)
        Factors: length, structure, examples
        """
        score = 0.0
        
        # Length score (40%)
        length = len(content)
        if length >= 200:
            score += 0.4
        elif length >= 100:
            score += 0.3
        elif length >= 50:
            score += 0.2
        elif length >= 20:
            score += 0.1
        
        # Structure score (40%)
        if '\n' in content:
            lines = content.split('\n')
            if len(lines) >= 5:
                score += 0.4
            elif len(lines) >= 3:
                score += 0.3
            elif len(lines) >= 2:
                score += 0.2
        
        # Has metadata (20%)
        if '[' in content and ']' in content:  # Likely has tags/IDs
            score += 0.2
        
        return min(score, 1.0)
    
    def score_clarity(self, content: str) -> float:
        """
        Score clarity (0-1)
        Factors: readability, organization, language
        """
        score = 0.0
        
        # Readability (50%)
        words = content.split()
        if len(words) >= 10:
            avg_word_len = sum(len(w) for w in words) / len(words)
            if 4 <= avg_word_len <= 8:  # Reasonable word length
                score += 0.3
            elif 3 <= avg_word_len <= 10:
                score += 0.2
            
            # Sentence structure
            sentences = content.replace('。', '.').replace('！', '.').replace('？', '.').split('.')
            if len(sentences) >= 3:
                score += 0.2
        
        # Organization (30%)
        if content.count('#') > 0 or content.count('-') > 0 or content.count('*') > 0:
            score += 0.3
        
        # No excessive repetition (20%)
        unique_words = set(words)
        if len(words) > 0:
            uniqueness_ratio = len(unique_words) / len(words)
            if uniqueness_ratio > 0.7:
                score += 0.2
            elif uniqueness_ratio > 0.5:
                score += 0.1
        
        return min(score, 1.0)
    
    def score_relevance(self, content: str, context: str = "") -> float:
        """
        Score relevance (0-1)
        Factors: keyword density, topic focus, context match
        """
        score = 0.0
        
        # Has clear topic (40%)
        if len(content.split('\n')[0]) <= 50:  # Clear title/heading
            score += 0.4
        
        # Keyword consistency (30%)
        words = content.lower().split()
        if len(words) > 0:
            # Check if key terms repeat
            word_freq = {}
            for w in words:
                if len(w) > 3:  # Ignore short words
                    word_freq[w] = word_freq.get(w, 0) + 1
            
            # Some repetition indicates focus
            repeated = sum(1 for count in word_freq.values() if count > 1)
            if repeated >= 5:
                score += 0.3
            elif repeated >= 2:
                score += 0.2
        
        # Context match (30%)
        if context:
            context_words = set(context.lower().split())
            content_words = set(content.lower().split())
            overlap = len(context_words & content_words)
            if overlap >= 10:
                score += 0.3
            elif overlap >= 5:
                score += 0.2
            elif overlap >= 2:
                score += 0.1
        else:
            score += 0.3  # Default if no context
        
        return min(score, 1.0)
    
    def score_uniqueness(self, content: str, other_memories: List[str] = None) -> float:
        """
        Score uniqueness (0-1)
        Factors: novelty, redundancy check
        """
        score = 0.0
        
        # Has unique identifiers (40%)
        if '[' in content and ']' in content:  # Likely has lesson codes
            score += 0.4
        
        # Content diversity (30%)
        words = set(content.lower().split())
        if len(words) >= 50:
            score += 0.3
        elif len(words) >= 30:
            score += 0.2
        elif len(words) >= 15:
            score += 0.1
        
        # Compare with other memories (30%)
        if other_memories:
            min_similarity = 1.0
            for other in other_memories:
                similarity = self._jaccard_similarity(content, other)
                min_similarity = min(min_similarity, similarity)
            
            # Lower similarity = more unique
            if min_similarity < 0.3:
                score += 0.3
            elif min_similarity < 0.5:
                score += 0.2
            elif min_similarity < 0.7:
                score += 0.1
        else:
            score += 0.3  # Default
        
        return min(score, 1.0)
    
    def score_actionability(self, content: str) -> float:
        """
        Score actionability (0-1)
        Factors: clear actions, implementation details, examples
        """
        score = 0.0
        
        # Has action verbs (40%)
        action_words = ['implement', 'create', 'use', 'add', 'fix', 'update', 
                       'build', 'deploy', 'test', 'run', 'execute', 'apply',
                       '实现', '创建', '使用', '添加', '修复', '更新',
                       '构建', '部署', '测试', '运行', '执行', '应用']
        
        content_lower = content.lower()
        has_action = any(word in content_lower for word in action_words)
        if has_action:
            score += 0.4
        
        # Has specific details (30%)
        if any(c.isdigit() for c in content):  # Has numbers
            score += 0.15
        if ':' in content or '=' in content:  # Has specifications
            score += 0.15
        
        # Has examples or implementation notes (30%)
        if 'example' in content_lower or '示例' in content_lower:
            score += 0.15
        if 'code' in content_lower or '代码' in content_lower:
            score += 0.15
        
        return min(score, 1.0)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def calculate_overall(self, dimensions: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        score = sum(
            dimensions[dim] * self.weights[dim]
            for dim in self.weights
        )
        return round(score, 3)
    
    def get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        for grade, threshold in sorted(self.grade_thresholds.items(), 
                                       key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return grade
        return 'F'
    
    def identify_issues(self, dimensions: Dict[str, float]) -> List[str]:
        """Identify quality issues"""
        issues = []
        
        if dimensions['completeness'] < 0.5:
            issues.append("Content too short or lacks structure")
        if dimensions['clarity'] < 0.5:
            issues.append("Poor readability or organization")
        if dimensions['relevance'] < 0.5:
            issues.append("Unclear topic focus")
        if dimensions['uniqueness'] < 0.5:
            issues.append("Potentially redundant with other memories")
        if dimensions['actionability'] < 0.5:
            issues.append("Lacks actionable insights or examples")
        
        return issues
    
    def generate_recommendations(self, dimensions: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recs = []
        
        if dimensions['completeness'] < 0.7:
            recs.append("Add more details, examples, or context")
        if dimensions['clarity'] < 0.7:
            recs.append("Improve organization with headings and bullet points")
        if dimensions['relevance'] < 0.7:
            recs.append("Clarify the main topic and key takeaways")
        if dimensions['uniqueness'] < 0.7:
            recs.append("Add unique identifiers or differentiate from similar memories")
        if dimensions['actionability'] < 0.7:
            recs.append("Include specific actions, code examples, or implementation steps")
        
        return recs
    
    def score_memory(self, memory_id: str, content: str, 
                    other_memories: List[str] = None) -> QualityReport:
        """
        Score a single memory across all dimensions
        """
        # Calculate dimension scores
        dimensions = {
            'completeness': self.score_completeness(content),
            'clarity': self.score_clarity(content),
            'relevance': self.score_relevance(content),
            'uniqueness': self.score_uniqueness(content, other_memories),
            'actionability': self.score_actionability(content),
        }
        
        # Overall score
        overall = self.calculate_overall(dimensions)
        grade = self.get_grade(overall)
        
        # Issues and recommendations
        issues = self.identify_issues(dimensions)
        recs = self.generate_recommendations(dimensions)
        
        return QualityReport(
            memory_id=memory_id,
            overall_score=overall,
            dimensions=dimensions,
            grade=grade,
            issues=issues,
            recommendations=recs,
            timestamp=datetime.now().isoformat()
        )
    
    def score_all(self, memories: Dict[str, str]) -> List[QualityReport]:
        """Score multiple memories"""
        reports = []
        contents = list(memories.values())
        
        for memory_id, content in memories.items():
            report = self.score_memory(memory_id, content, contents)
            reports.append(report)
        
        return sorted(reports, key=lambda r: r.overall_score, reverse=True)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Quality Scorer")
    parser.add_argument('--memory', type=str, default=str(MEMORY_FILE),
                       help='Memory file to score')
    parser.add_argument('--output', type=str, 
                       help='Output JSON file for report')
    args = parser.parse_args()
    
    # Load memory file
    memory_file = Path(args.memory)
    if not memory_file.exists():
        print(f"❌ Memory file not found: {memory_file}")
        return
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple parsing (split by sections)
    sections = content.split('###')[1:]  # Skip first empty
    memories = {}
    for section in sections:
        lines = section.strip().split('\n')
        if lines:
            memory_id = f"mem_{len(memories)}"
            memories[memory_id] = section.strip()
    
    print(f"📊 Scoring {len(memories)} memories...")
    
    # Score all
    scorer = MemoryQualityScorer()
    reports = scorer.score_all(memories)
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 Memory Quality Summary")
    print("=" * 80)
    
    grades = {}
    for report in reports:
        grade = report.grade
        grades[grade] = grades.get(grade, 0) + 1
    
    print(f"Total Memories: {len(reports)}")
    print(f"\nGrade Distribution:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = grades.get(grade, 0)
        pct = count / len(reports) * 100
        print(f"  {grade}: {count} ({pct:.1f}%)")
    
    avg_score = sum(r.overall_score for r in reports) / len(reports)
    print(f"\nAverage Score: {avg_score:.3f}")
    
    # Top 5
    print(f"\n🏆 Top 5 Memories:")
    for i, report in enumerate(reports[:5], 1):
        print(f"  {i}. {report.memory_id}: {report.overall_score:.3f} ({report.grade})")
    
    # Bottom 5
    print(f"\n⚠️  Bottom 5 Memories (Need Improvement):")
    for i, report in enumerate(reports[-5:], 1):
        print(f"  {i}. {report.memory_id}: {report.overall_score:.3f} ({report.grade})")
        for issue in report.issues:
            print(f"      - {issue}")
    
    # Save report
    if args.output:
        output_file = Path(args.output)
        report_data = {
            'summary': {
                'total': len(reports),
                'average_score': avg_score,
                'grade_distribution': grades,
            },
            'reports': [asdict(r) for r in reports]
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full report saved to: {output_file}")

if __name__ == "__main__":
    main()
