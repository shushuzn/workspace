#!/usr/bin/env python3
"""
Memory LLM Distiller
=====================
AI-powered memory distillation using local Ollama LLM.

Features:
- Automatic insight extraction from daily notes
- Quality scoring (5 dimensions)
- JSON output for easy integration
- Batch processing support
- Configurable models

Usage:
    python memory-llm-distiller.py --input memory/2026-03-17.md
    python memory-llm-distiller.py --batch memory/*.md --output distilled.json
    python memory-llm-distiller.py --demo
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Optional
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

class DistillerConfig:
    """Distiller configuration"""
    
    # Ollama settings
    OLLAMA_HOST = os.getenv('LOCAL_LLM_HOST', 'localhost:11434')
    DEFAULT_MODEL = os.getenv('LOCAL_LLM_MODEL', 'qwen2.5:1.5b')
    BACKUP_MODELS = ['qwen3.5:0.8b', 'qwen3.5:2b']
    TIMEOUT = int(os.getenv('LOCAL_LLM_TIMEOUT', '120'))
    
    # Distillation settings
    MAX_INSIGHTS_PER_NOTE = 5
    MIN_INSIGHT_LENGTH = 20
    MAX_INSIGHT_LENGTH = 200
    QUALITY_THRESHOLD = 0.75
    
    # Quality scoring weights
    WEIGHTS = {
        'importance': 0.30,
        'generality': 0.25,
        'actionability': 0.20,
        'novelty': 0.15,
        'timeliness': 0.10,
    }
    
    # Prompt templates
    DISTILL_PROMPT = """
You are a memory distillation expert. Extract 3-5 core insights from the following daily note.

For each insight, provide:
1. **content**: The insight (20-200 characters, concise and actionable)
2. **importance**: 0.0-1.0 (how critical this is for future decisions)
3. **generality**: 0.0-1.0 (how broadly applicable across scenarios)
4. **actionability**: 0.0-1.0 (how directly it guides action)
5. **novelty**: 0.0-1.0 (how new vs. existing knowledge)
6. **category**: One of [SECURITY, WORKFLOW, TOOL, MEMORY, INNOVATION, LESSON, CONFIG]

Daily Note:
{note_content}

Output ONLY valid JSON in this format:
{{
  "insights": [
    {{
      "content": "...",
      "importance": 0.9,
      "generality": 0.8,
      "actionability": 0.7,
      "novelty": 0.9,
      "category": "SECURITY",
      "suggested_id": "SEC-XXX"
    }}
  ],
  "summary": "One-sentence summary of the note",
  "key_topics": ["topic1", "topic2"]
}}
"""


# ============================================================================
# Ollama Client
# ============================================================================

class OllamaClient:
    """Simple Ollama API client"""
    
    def __init__(self, host: str = 'localhost:11434', model: str = 'qwen2.5:1.5b'):
        self.host = host
        self.model = model
        self.base_url = f'http://{host}/api'
    
    def generate(self, prompt: str, model: str = None) -> str:
        """Generate text using Ollama"""
        import urllib.request
        import json as json_lib
        
        model = model or self.model
        
        data = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'top_p': 0.9,
            }
        }
        
        try:
            req = urllib.request.Request(
                f'{self.base_url}/generate',
                data=json_lib.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json_lib.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        import urllib.request
        import urllib.error
        
        try:
            req = urllib.request.Request(f'{self.base_url}/tags')
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except:
            return False


# ============================================================================
# Quality Scorer
# ============================================================================

class InsightQualityScorer:
    """Score insight quality across 5 dimensions"""
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DistillerConfig.WEIGHTS
    
    def score(self, insight: Dict) -> Dict:
        """Calculate quality score for an insight"""
        # Extract dimension scores
        importance = insight.get('importance', 0.5)
        generality = insight.get('generality', 0.5)
        actionability = insight.get('actionability', 0.5)
        novelty = insight.get('novelty', 0.5)
        timeliness = insight.get('timeliness', 0.5)
        
        # Calculate weighted score
        weighted_score = (
            importance * self.weights['importance'] +
            generality * self.weights['generality'] +
            actionability * self.weights['actionability'] +
            novelty * self.weights['novelty'] +
            timeliness * self.weights['timeliness']
        )
        
        # Determine grade
        if weighted_score >= 0.90:
            grade = 'A'
        elif weighted_score >= 0.75:
            grade = 'B'
        elif weighted_score >= 0.60:
            grade = 'C'
        elif weighted_score >= 0.50:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'weighted_score': round(weighted_score, 3),
            'grade': grade,
            'dimensions': {
                'importance': importance,
                'generality': generality,
                'actionability': actionability,
                'novelty': novelty,
                'timeliness': timeliness,
            },
            'recommendation': 'distill' if weighted_score >= DistillerConfig.QUALITY_THRESHOLD else 'archive'
        }


# ============================================================================
# Memory Distiller
# ============================================================================

class MemoryDistiller:
    """Main memory distillation engine"""
    
    def __init__(self, config: DistillerConfig = None):
        self.config = config or DistillerConfig()
        self.client = OllamaClient(self.config.OLLAMA_HOST, self.config.DEFAULT_MODEL)
        self.scorer = InsightQualityScorer(self.config.WEIGHTS)
        self.stats = {
            'notes_processed': 0,
            'insights_extracted': 0,
            'insights_distilled': 0,
            'insights_archived': 0,
            'errors': 0,
        }
    
    def read_note(self, note_path: str) -> str:
        """Read daily note file"""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {note_path}: {e}")
            self.stats['errors'] += 1
            return ""
    
    def extract_insights(self, note_content: str) -> Dict:
        """Extract insights from note using LLM"""
        prompt = self.config.DISTILL_PROMPT.format(note_content=note_content[:3000])  # Limit context
        
        response = self.client.generate(prompt)
        
        # Parse JSON from response
        try:
            # Try to find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in LLM response")
                return {'insights': [], 'summary': '', 'key_topics': []}
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {'insights': [], 'summary': '', 'key_topics': []}
    
    def score_insights(self, insights: List[Dict]) -> List[Dict]:
        """Score all insights"""
        scored_insights = []
        
        for insight in insights:
            score_result = self.scorer.score(insight)
            insight['quality_score'] = score_result['weighted_score']
            insight['grade'] = score_result['grade']
            insight['recommendation'] = score_result['recommendation']
            insight['dimensions'] = score_result['dimensions']
            scored_insights.append(insight)
        
        return scored_insights
    
    def distill_note(self, note_path: str) -> Dict:
        """Distill a single note"""
        logger.info(f"Distilling: {note_path}")
        self.stats['notes_processed'] += 1
        
        # Read note
        note_content = self.read_note(note_path)
        if not note_content:
            return {'error': 'Failed to read note', 'path': note_path}
        
        # Extract insights
        result = self.extract_insights(note_content)
        
        # Score insights
        if result.get('insights'):
            result['insights'] = self.score_insights(result['insights'])
            self.stats['insights_extracted'] += len(result['insights'])
            
            # Separate by recommendation
            distilled = [i for i in result['insights'] if i['recommendation'] == 'distill']
            archived = [i for i in result['insights'] if i['recommendation'] == 'archive']
            
            self.stats['insights_distilled'] += len(distilled)
            self.stats['insights_archived'] += len(archived)
            
            result['distilled_insights'] = distilled
            result['archived_insights'] = archived
        
        # Add metadata
        result['source'] = note_path
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    def distill_batch(self, note_paths: List[str], output_file: str = None) -> Dict:
        """Distill multiple notes"""
        logger.info(f"Distilling batch of {len(note_paths)} notes")
        
        results = []
        for note_path in note_paths:
            result = self.distill_note(note_path)
            results.append(result)
        
        # Aggregate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_notes': len(note_paths),
            'stats': self.stats,
            'results': results,
            'distilled_count': self.stats['insights_distilled'],
            'archived_count': self.stats['insights_archived'],
        }
        
        # Save report
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to: {output_file}")
        
        return report


# ============================================================================
# CLI Interface
# ============================================================================

def demo_mode():
    """Run demo with sample note"""
    print("🧪 Memory LLM Distiller - Demo Mode")
    print("=" * 60)
    
    # Check Ollama availability
    client = OllamaClient()
    if client.is_available():
        print(f"✅ Ollama available at {client.host}")
        print(f"   Model: {client.model}")
    else:
        print(f"⚠️  Ollama not available at {client.host}")
        print(f"   Install: https://ollama.ai")
        return
    
    # Create sample note
    sample_note = """
# Daily Note - 2026-03-17

## Work Summary
- Implemented Git Firewall Proxy system
- Added 12 secret detection patterns
- Created pre-commit hook for automatic scanning
- Test coverage: 100% (12/12 tests passed)

## Key Learnings
- Pre-commit hooks are 10x more effective than post-push scanning
- Entropy analysis catches secrets that regex misses
- Windows console encoding requires special handling (UTF-8)
- Security tools must have 100% test coverage

## Next Steps
- Deploy to obsidian-sync repository
- Add to HEARTBEAT.md for regular scans
- Package for PyPI distribution
"""
    
    # Distill
    distiller = MemoryDistiller()
    result = distiller.extract_insights(sample_note)
    
    print(f"\n📊 Extracted Insights: {len(result.get('insights', []))}")
    print(f"Summary: {result.get('summary', 'N/A')}")
    print(f"Topics: {', '.join(result.get('key_topics', []))}")
    
    if result.get('insights'):
        print(f"\n💡 Top Insights:")
        for i, insight in enumerate(result['insights'][:3], 1):
            print(f"\n  {i}. {insight.get('content', 'N/A')}")
            print(f"     Category: {insight.get('category', 'N/A')}")
            print(f"     Importance: {insight.get('importance', 0):.2f}")
            print(f"     Actionability: {insight.get('actionability', 0):.2f}")


def main():
    parser = argparse.ArgumentParser(
        description='Memory LLM Distiller - AI-powered insight extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single note
  python memory-llm-distiller.py --input memory/2026-03-17.md
  
  # Batch processing
  python memory-llm-distiller.py --batch memory/*.md --output distilled.json
  
  # Demo mode
  python memory-llm-distiller.py --demo
  
  # Check Ollama status
  python memory-llm-distiller.py --check-ollama
        """
    )
    
    parser.add_argument('--input', '-i', type=str, help='Single note file to distill')
    parser.add_argument('--batch', '-b', type=str, nargs='+', help='Batch of note files')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--check-ollama', action='store_true', help='Check Ollama availability')
    parser.add_argument('--model', '-m', type=str, default='qwen2.5:1.5b', help='Ollama model')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.demo:
        demo_mode()
    elif args.check_ollama:
        client = OllamaClient()
        if client.is_available():
            print(f"✅ Ollama available at {client.host}")
            print(f"   Model: {args.model}")
        else:
            print(f"❌ Ollama not available at {client.host}")
            print(f"   Install: https://ollama.ai")
            sys.exit(1)
    elif args.input:
        distiller = MemoryDistiller()
        result = distiller.distill_note(args.input)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.batch:
        distiller = MemoryDistiller()
        report = distiller.distill_batch(args.batch, args.output)
        print(f"\n📊 Distillation Report")
        print(f"  Notes processed: {report['total_notes']}")
        print(f"  Insights extracted: {report['distilled_count']}")
        print(f"  Insights archived: {report['archived_count']}")
        if args.output:
            print(f"  Report saved to: {args.output}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
