#!/usr/bin/env python3
"""
Memory Quality Scorer
=====================
Multi-dimensional quality assessment for memory entries.

Dimensions:
- Completeness (25%) - Content length, structure, metadata
- Clarity (20%) - Readability, organization, language
- Relevance (25%) - Topic focus, keyword consistency
- Uniqueness (15%) - Novelty, redundancy check
- Actionability (15%) - Clear actions, examples

Usage:
    python memory-quality-scorer.py --memory "MEMORY.md"
    python memory-quality-scorer.py --text "Your memory text here"
    python memory-quality-scorer.py --demo
"""

import os
import re
import sys
import json
import math
import argparse
import logging
from datetime import datetime
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

class ScorerConfig:
    """Quality scorer configuration"""
    
    # Dimension weights
    WEIGHTS = {
        'completeness': 0.25,
        'clarity': 0.20,
        'relevance': 0.25,
        'uniqueness': 0.15,
        'actionability': 0.15,
    }
    
    # Grading thresholds
    GRADES = {
        'A': 0.90,
        'B': 0.75,
        'C': 0.60,
        'D': 0.50,
        'F': 0.0,
    }
    
    # Quality indicators
    ACTION_VERBS = [
        '应该', '必须', '避免', '建议', '推荐', '不要', '务必',
        'should', 'must', 'avoid', 'recommend', 'never', 'always',
    ]
    
    STRUCTURE_MARKERS = [
        '##', '###', '-', '*', '1.', '2.', '3.',
        '|', '```', '"""",
    ]


# ============================================================================
# Quality Dimensions
# ============================================================================

class CompletenessScorer:
    """Score memory completeness"""
    
    def score(self, text: str) -> Tuple[float, Dict]:
        """Calculate completeness score"""
        details = {}
        
        # Length score (0-1)
        char_count = len(text)
        length_score = min(1.0, char_count / 500)  # 500 chars = full score
        details['length'] = char_count
        details['length_score'] = round(length_score, 3)
        
        # Structure score
        structure_count = sum(1 for marker in ScorerConfig.STRUCTURE_MARKERS 
                            if marker in text)
        structure_score = min(1.0, structure_count / 5)  # 5 markers = full score
        details['structure_markers'] = structure_count
        details['structure_score'] = round(structure_score, 3)
        
        # Metadata score (has编号，date, category)
        metadata_score = 0.0
        if re.search(r'\[?[A-Z]+-\d+\]?', text):  # Has ID like SEC-001
            metadata_score += 0.4
        if re.search(r'\d{4}-\d{2}-\d{2}', text):  # Has date
            metadata_score += 0.3
        if re.search(r'(分类|category|标签|tag)', text, re.IGNORECASE):
            metadata_score += 0.3
        details['metadata_score'] = round(metadata_score, 3)
        
        # Overall completeness
        completeness = (length_score * 0.4 + structure_score * 0.4 + metadata_score * 0.2)
        
        return round(completeness, 3), details


class ClarityScorer:
    """Score memory clarity"""
    
    def score(self, text: str) -> Tuple[float, Dict]:
        """Calculate clarity score"""
        details = {}
        
        # Readability (sentence length)
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
            # Optimal: 20-40 characters
            if 20 <= avg_sentence_length <= 40:
                readability_score = 1.0
            elif avg_sentence_length < 20:
                readability_score = 0.7
            else:
                readability_score = max(0.3, 1.0 - (avg_sentence_length - 40) / 100)
        else:
            readability_score = 0.5
        
        details['avg_sentence_length'] = round(avg_sentence_length if sentences else 0, 1)
        details['readability_score'] = round(readability_score, 3)
        
        # Organization (paragraphs)
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        org_score = min(1.0, len(paragraphs) / 3)  # 3+ paragraphs = full score
        details['paragraphs'] = len(paragraphs)
        details['organization_score'] = round(org_score, 3)
        
        # Language consistency
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total = chinese_chars + english_chars
        
        if total > 0:
            # Mixed language is OK, but dominant one should be consistent
            dominant_ratio = max(chinese_chars, english_chars) / total
            lang_score = 0.7 + (0.3 * dominant_ratio)  # 0.7-1.0
        else:
            lang_score = 0.5
        
        details['language_score'] = round(lang_score, 3)
        
        # Overall clarity
        clarity = (readability_score * 0.4 + org_score * 0.3 + lang_score * 0.3)
        
        return round(clarity, 3), details


class RelevanceScorer:
    """Score memory relevance"""
    
    def score(self, text: str, keywords: List[str] = None) -> Tuple[float, Dict]:
        """Calculate relevance score"""
        details = {}
        
        # Default keywords for memory system
        if not keywords:
            keywords = [
                '记忆', 'memory', '教训', 'lesson', '洞察', 'insight',
                '系统', 'system', '工具', 'tool', '配置', 'config',
            ]
        
        # Keyword density
        keyword_count = sum(1 for kw in keywords if kw.lower() in text.lower())
        keyword_score = min(1.0, keyword_count / 5)  # 5+ keywords = full score
        details['keywords_found'] = keyword_count
        details['keyword_score'] = round(keyword_score, 3)
        
        # Topic focus (avoid too many topics)
        unique_topics = len(set(re.findall(r'\[([A-Z]+-\d+)\]', text)))
        if unique_topics == 0:
            topic_score = 0.7  # No explicit topics, assume OK
        elif unique_topics <= 3:
            topic_score = 1.0  # Focused
        else:
            topic_score = max(0.5, 1.0 - (unique_topics - 3) * 0.1)  # Penalize scattered
        
        details['topics_count'] = unique_topics
        details['topic_score'] = round(topic_score, 3)
        
        # Overall relevance
        relevance = (keyword_score * 0.5 + topic_score * 0.5)
        
        return round(relevance, 3), details


class UniquenessScorer:
    """Score memory uniqueness"""
    
    def __init__(self, memory_file: str = None):
        self.memory_file = memory_file
        self.existing_memories = []
        
        if memory_file and os.path.exists(memory_file):
            self._load_existing_memories()
    
    def _load_existing_memories(self):
        """Load existing memories for comparison"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract memory entries (simplified)
            self.existing_memories = re.findall(r'\[([A-Z]+-\d+)\].*?(?=\n\[|\Z)', content, re.DOTALL)
        except:
            pass
    
    def score(self, text: str) -> Tuple[float, Dict]:
        """Calculate uniqueness score"""
        details = {}
        
        # Check for duplicate IDs
        ids_in_text = re.findall(r'\[([A-Z]+-\d+)\]', text)
        duplicate_ids = [id for id in ids_in_text if id in self.existing_memories]
        
        if duplicate_ids:
            novelty_score = 0.5  # Some duplication
            details['duplicate_ids'] = duplicate_ids
        else:
            novelty_score = 1.0  # No duplication
        
        details['novelty_score'] = round(novelty_score, 3)
        
        # Content similarity (simplified - check for repeated phrases)
        phrases = re.findall(r'[\u4e00-\u9fff]{4,}', text)
        if phrases:
            phrase_counts = {}
            for phrase in phrases:
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
            
            repeated = sum(1 for count in phrase_counts.values() if count > 1)
            repetition_penalty = min(0.3, repeated * 0.05)
            novelty_score = max(0.5, novelty_score - repetition_penalty)
            details['repeated_phrases'] = repeated
        
        details['uniqueness_score'] = round(novelty_score, 3)
        
        return round(novelty_score, 3), details


class ActionabilityScorer:
    """Score memory actionability"""
    
    def score(self, text: str) -> Tuple[float, Dict]:
        """Calculate actionability score"""
        details = {}
        
        # Action verb presence
        action_count = sum(1 for verb in ScorerConfig.ACTION_VERBS if verb in text.lower())
        action_score = min(1.0, action_count / 2)  # 2+ action verbs = full score
        details['action_verbs'] = action_count
        details['action_score'] = round(action_score, 3)
        
        # Example/code presence
        has_example = bool(re.search(r'(例如|比如|example|e\.g\.)', text, re.IGNORECASE))
        has_code = bool(re.search(r'```|`.*`', text))
        
        example_score = 0.0
        if has_example:
            example_score += 0.5
        if has_code:
            example_score += 0.5
        
        details['has_example'] = has_example
        details['has_code'] = has_code
        details['example_score'] = round(example_score, 3)
        
        # Clear recommendation
        has_recommendation = bool(re.search(r'(建议|推荐|应该|必须|避免|should|must|avoid)', text, re.IGNORECASE))
        rec_score = 0.8 if has_recommendation else 0.3
        details['recommendation_score'] = round(rec_score, 3)
        
        # Overall actionability
        actionability = (action_score * 0.4 + example_score * 0.3 + rec_score * 0.3)
        
        return round(actionability, 3), details


# ============================================================================
# Main Quality Scorer
# ============================================================================

class MemoryQualityScorer:
    """Main quality scorer combining all dimensions"""
    
    def __init__(self, config: ScorerConfig = None, memory_file: str = None):
        self.config = config or ScorerConfig()
        self.memory_file = memory_file
        
        self.scorers = {
            'completeness': CompletenessScorer(),
            'clarity': ClarityScorer(),
            'relevance': RelevanceScorer(),
            'uniqueness': UniquenessScorer(memory_file),
            'actionability': ActionabilityScorer(),
        }
    
    def score(self, text: str, keywords: List[str] = None) -> Dict:
        """Score memory across all dimensions"""
        result = {
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'text_length': len(text),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Score each dimension
        dimension_scores = {}
        for dim_name, scorer in self.scorers.items():
            if dim_name == 'relevance':
                score, details = scorer.score(text, keywords)
            else:
                score, details = scorer.score(text)
            
            dimension_scores[dim_name] = {
                'score': score,
                'details': details,
            }
        
        result['dimensions'] = dimension_scores
        
        # Calculate weighted overall score
        weights = self.config.WEIGHTS
        overall_score = sum(
            dimension_scores[dim]['score'] * weights[dim]
            for dim in weights
        )
        
        result['overall_score'] = round(overall_score, 3)
        
        # Determine grade
        for grade, threshold in sorted(self.config.GRADES.items(), key=lambda x: -x[1]):
            if overall_score >= threshold:
                result['grade'] = grade
                break
        
        # Recommendation
        if overall_score >= 0.75:
            result['recommendation'] = 'keep'
        elif overall_score >= 0.60:
            result['recommendation'] = 'improve'
        else:
            result['recommendation'] = 'archive'
        
        return result
    
    def score_file(self, file_path: str) -> Dict:
        """Score a memory file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.score(content)
            result['file_path'] = file_path
            return result
        
        except Exception as e:
            logger.error(f"Error scoring {file_path}: {e}")
            return {'error': str(e), 'file_path': file_path}


# ============================================================================
# CLI Interface
# ============================================================================

def demo_mode():
    """Run demo with sample memories"""
    print("🧪 Memory Quality Scorer - Demo Mode")
    print("=" * 60)
    
    samples = {
        'High Quality': """
[SEC-FIREWALL-001] Pre-commit hook 比 post-push 扫描有效 10 倍

**教训:** 在提交前阻止敏感信息比事后清理效率高 10 倍。

**实施:** 
```bash
python git-firewall-proxy.py --install-hook
```

**建议:** 所有项目必须安装 pre-commit hook，作为安全流程的第一步。

**影响:** 防止意外提交，节省 4+ 小时/月清理时间。
        """,
        
        'Medium Quality': """
今天学习了 Git 防火墙系统。感觉很有用。应该多用。
        """,
        
        'Low Quality': """
一些笔记。待完善。
        """,
    }
    
    scorer = MemoryQualityScorer()
    
    for name, text in samples.items():
        print(f"\n📊 {name} Sample:")
        print("-" * 60)
        result = scorer.score(text)
        
        print(f"Overall Score: {result['overall_score']:.3f}")
        print(f"Grade: {result['grade']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"\nDimension Scores:")
        for dim, data in result['dimensions'].items():
            print(f"  {dim.capitalize()}: {data['score']:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description='Memory Quality Scorer - Multi-dimensional assessment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a memory file
  python memory-quality-scorer.py --memory MEMORY.md
  
  # Score text directly
  python memory-quality-scorer.py --text "Your memory text"
  
  # Demo mode
  python memory-quality-scorer.py --demo
        """
    )
    
    parser.add_argument('--memory', '-m', type=str, help='Memory file to score')
    parser.add_argument('--text', '-t', type=str, help='Text to score')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_mode()
    elif args.memory:
        scorer = MemoryQualityScorer(memory_file=args.memory)
        result = scorer.score_file(args.memory)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Report saved to: {args.output}")
    elif args.text:
        scorer = MemoryQualityScorer()
        result = scorer.score(args.text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
