#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Summarizer - Local LLM-based paper summarization

Features:
- Local LLM (Qwen2.5-1.5B) for privacy
- Structured summary format
- Batch processing support
- Cache integration
- Canvas auto-update

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Import local LLM analyzer
sys.path.insert(0, str(Path(__file__).parent))

try:
    from local_llm_analyzer import LocalLLMAnalyzer
    LLM_OK = True
except ImportError:
    LLM_OK = False


class PaperSummarizer:
    """Local LLM-based paper summarizer"""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        if workspace_dir:
            self.workspace = Path(workspace_dir)
        else:
            self.workspace = Path(__file__).parent.parent
        
        self.papers_dir = self.workspace / "data" / "papers"
        self.summaries_dir = self.workspace / "data" / "summaries"
        self.cache_file = self.workspace / "data" / "cache" / "summary_cache.json"
        
        self.llm = LocalLLMAnalyzer() if LLM_OK else None
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cache
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load summary cache"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'summaries': {}, 'stats': {'generated': 0, 'cached': 0}}
    
    def _save_cache(self):
        """Save summary cache"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _load_paper(self, paper_file: Path) -> Optional[Dict]:
        """Load paper from JSON file"""
        try:
            with open(paper_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading {paper_file}: {e}")
            return None
    
    def _extract_text(self, paper: Dict) -> str:
        """Extract text from paper for summarization"""
        # Try markdown first
        markdown = paper.get('markdown', '')
        if markdown:
            # Remove code blocks and references
            text = re.sub(r'```.*?```', '', markdown, flags=re.DOTALL)
            text = re.sub(r'\[.*?\]\(.*?\)', '', text)
            text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
            return text[:4000]  # Limit context
        
        # Fallback to abstract
        abstract = paper.get('abstract', '')
        if abstract:
            return abstract
        
        return paper.get('title', '')
    
    def _generate_prompt(self, paper: Dict) -> str:
        """Generate summarization prompt"""
        title = paper.get('title', 'Unknown')
        text = self._extract_text(paper)
        
        prompt = f"""You are an expert research assistant. Summarize this academic paper:

**Title:** {title}

**Content:**
{text}

Provide a structured summary with the following sections:

1. **Core Problem** (1-2 sentences): What problem does this paper address?
2. **Key Contribution** (2-3 bullet points): What are the main contributions?
3. **Method** (2-3 sentences): What approach/method is used?
4. **Results** (2-3 sentences): What are the key findings?
5. **Limitations** (1-2 sentences): What are the limitations?
6. **Future Work** (1 sentence): What future directions are suggested?

Keep the summary concise (200-300 words total). Use clear, technical language."""

        return prompt
    
    def summarize_paper(self, paper_file: Path, force: bool = False) -> Optional[Dict]:
        """Summarize a single paper"""
        paper = self._load_paper(paper_file)
        if not paper:
            return None
        
        paper_id = paper.get('arxiv_id', paper_file.stem)
        
        # Check cache
        if not force and paper_id in self.cache['summaries']:
            self.cache['stats']['cached'] += 1
            print(f"ℹ️  Using cached summary for {paper_id}")
            return self.cache['summaries'][paper_id]
        
        if not self.llm:
            print("❌ Local LLM not available")
            return None
        
        # Generate summary
        print(f"📝 Generating summary for {paper_id}...")
        
        prompt = self._generate_prompt(paper)
        
        try:
            summary = self.llm.analyze_text(prompt)
            
            # Parse structured summary
            structured = self._parse_summary(summary)
            
            # Add metadata
            structured['paper_id'] = paper_id
            structured['title'] = paper.get('title', 'Unknown')
            structured['generated_at'] = datetime.now().isoformat()
            structured['model'] = self.llm.model_name
            
            # Save to file
            output_file = self.summaries_dir / f"{paper_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self.cache['summaries'][paper_id] = structured
            self.cache['stats']['generated'] += 1
            self._save_cache()
            
            print(f"✅ Summary saved to {output_file}")
            
            return structured
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return None
    
    def _parse_summary(self, text: str) -> Dict:
        """Parse unstructured summary into structured format"""
        sections = {
            'core_problem': '',
            'key_contribution': [],
            'method': '',
            'results': '',
            'limitations': '',
            'future_work': ''
        }
        
        # Simple regex parsing
        patterns = {
            'core_problem': r'\*\*Core Problem\*\*\s*(.+?)(?=\n\*\*|\Z)',
            'key_contribution': r'\*\*Key Contribution\*\*\s*(.+?)(?=\n\*\*|\Z)',
            'method': r'\*\*Method\*\*\s*(.+?)(?=\n\*\*|\Z)',
            'results': r'\*\*Results\*\*\s*(.+?)(?=\n\*\*|\Z)',
            'limitations': r'\*\*Limitations\*\*\s*(.+?)(?=\n\*\*|\Z)',
            'future_work': r'\*\*Future Work\*\*\s*(.+?)(?=\n\*\*|\Z)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if key == 'key_contribution':
                    # Extract bullet points
                    points = re.findall(r'^[-•*]\s*(.+)$', content, re.MULTILINE)
                    sections[key] = points if points else [content]
                else:
                    sections[key] = content
        
        return sections
    
    def summarize_batch(self, keyword: str, force: bool = False) -> Dict:
        """Summarize all papers for a keyword"""
        paper_file = self.papers_dir / f"{keyword}.json"
        
        if not paper_file.exists():
            return {'error': f'No papers found for {keyword}'}
        
        paper_data = self._load_paper(paper_file)
        if not paper_data:
            return {'error': 'Failed to load papers'}
        
        papers = paper_data.get('papers', [])
        results = {
            'keyword': keyword,
            'total': len(papers),
            'summarized': 0,
            'cached': 0,
            'failed': 0,
            'summaries': []
        }
        
        print(f"\n📚 Summarizing {len(papers)} papers for '{keyword}'\n")
        
        for i, paper in enumerate(papers, 1):
            print(f"[{i}/{len(papers)}]")
            
            # Create temporary paper file
            paper_id = paper.get('arxiv_id', f"paper_{i}")
            temp_file = self.papers_dir / f"{paper_id}.json"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(paper, f, indent=2, ensure_ascii=False)
            
            summary = self.summarize_paper(temp_file, force=force)
            
            if summary:
                results['summarized'] += 1
                results['summaries'].append(summary)
            else:
                results['failed'] += 1
            
            temp_file.unlink(missing_ok=True)  # Clean up temp file
        
        # Save batch results
        batch_file = self.summaries_dir / f"{keyword}_batch.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Batch Summary:")
        print(f"  Total: {results['total']}")
        print(f"  Summarized: {results['summarized']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Saved to: {batch_file}")
        
        return results
    
    def get_stats(self) -> Dict:
        """Get summarization statistics"""
        summary_files = list(self.summaries_dir.glob("*.json"))
        
        return {
            'total_summaries': len(summary_files),
            'cache_hits': self.cache['stats'].get('cached', 0),
            'cache_misses': self.cache['stats'].get('generated', 0),
            'cache_hit_rate': (
                self.cache['stats'].get('cached', 0) /
                (self.cache['stats'].get('cached', 0) + self.cache['stats'].get('generated', 0)) * 100
            ) if (self.cache['stats'].get('cached', 0) + self.cache['stats'].get('generated', 0)) > 0 else 0
        }


def demo():
    """Run summarizer demo"""
    print("\n📝 Paper Summarizer Demo\n")
    
    summarizer = PaperSummarizer()
    
    # Show status
    print("="*70)
    print("Status:")
    print("="*70)
    
    print(f"  Local LLM: {'✅' if LLM_OK else '❌'}")
    print(f"  Papers directory: {summarizer.papers_dir}")
    print(f"  Summaries directory: {summarizer.summaries_dir}")
    
    stats = summarizer.get_stats()
    print()
    print("Statistics:")
    print(f"  Total summaries: {stats['total_summaries']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Cache misses: {stats['cache_misses']}")
    print(f"  Hit rate: {stats['cache_hit_rate']:.1f}%")
    
    print()
    print("="*70)
    print("Usage:")
    print("="*70)
    print("  python paper_summarizer.py --summarize quantum_computing")
    print("  python paper_summarizer.py --stats")
    print("  python paper_summarizer.py --demo")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Paper Summarizer')
    parser.add_argument('--summarize', type=str, help='Keyword to summarize')
    parser.add_argument('--force', action='store_true', help='Force regeneration')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    summarizer = PaperSummarizer()
    
    if args.demo or (not args.summarize and not args.stats):
        demo()
    elif args.stats:
        stats = summarizer.get_stats()
        print(json.dumps(stats, indent=2))
    elif args.summarize:
        summarizer.summarize_batch(args.summarize, force=args.force)
    else:
        demo()


if __name__ == "__main__":
    main()
