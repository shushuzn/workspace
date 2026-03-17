#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defuddle Integration - Extract clean markdown from web pages

Integrates Defuddle CLI for:
- arXiv paper content extraction
- Research article cleanup
- Token optimization (removes ads/navigation)

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class DefuddleExtractor:
    """Defuddle CLI wrapper for clean content extraction"""
    
    def __init__(self):
        self.defuddle_path = self._find_defuddle()
        
    def _find_defuddle(self) -> Optional[str]:
        """Find defuddle CLI in PATH"""
        # Check standard PATH first
        try:
            result = subprocess.run(
                ['defuddle', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return 'defuddle'
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Check npm global paths on Windows
        npm_paths = [
            r'D:\npm-global',
            r'C:\Users\华为\AppData\Roaming\npm',
            os.path.expanduser(r'~\AppData\Roaming\npm'),
        ]
        
        for npm_path in npm_paths:
            defuddle_exe = Path(npm_path) / 'defuddle.cmd'
            if defuddle_exe.exists():
                return str(defuddle_exe)
        
        return None
    
    def is_available(self) -> bool:
        """Check if defuddle is available"""
        return self.defuddle_path is not None
    
    def extract_markdown(self, url: str, output_file: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Extract clean markdown from URL
        
        Args:
            url: Web page URL
            output_file: Optional file path to save markdown
            
        Returns:
            Tuple of (markdown_content, metadata)
        """
        if not self.is_available():
            raise RuntimeError("Defuddle CLI not found. Install with: npm install -g defuddle")
        
        # Step 1: Get markdown output
        cmd_md = [self.defuddle_path, 'parse', url, '--md']
        
        try:
            result_md = subprocess.run(
                cmd_md,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            if result_md.returncode != 0:
                raise RuntimeError(f"Defuddle error: {result_md.stderr}")
            
            markdown = result_md.stdout
            
            # Step 2: Get metadata from JSON output
            cmd_json = [self.defuddle_path, 'parse', url, '--json']
            result_json = subprocess.run(
                cmd_json,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            metadata = {
                'title': '',
                'description': '',
                'domain': '',
                'author': '',
                'url': url,
                'extracted_at': datetime.now().isoformat()
            }
            
            if result_json.returncode == 0:
                try:
                    data = json.loads(result_json.stdout)
                    metadata['title'] = data.get('title', '')
                    metadata['description'] = data.get('description', '')
                    metadata['domain'] = data.get('domain', '')
                    metadata['author'] = data.get('author', '')
                except json.JSONDecodeError:
                    pass
            
            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"---\n")
                    f.write(f"title: {metadata['title']}\n")
                    f.write(f"description: {metadata['description']}\n")
                    f.write(f"author: {metadata['author']}\n")
                    f.write(f"source: {url}\n")
                    f.write(f"extracted: {metadata['extracted_at']}\n")
                    f.write(f"---\n\n")
                    f.write(markdown)
            
            return markdown, metadata
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Defuddle timeout after 60 seconds")
        except Exception as e:
            raise RuntimeError(f"Defuddle error: {str(e)}")
    
    def extract_metadata(self, url: str, property: str = 'title') -> str:
        """
        Extract specific metadata property
        
        Args:
            url: Web page URL
            property: Property name (title/description/domain)
            
        Returns:
            Property value
        """
        if not self.is_available():
            raise RuntimeError("Defuddle CLI not available")
        
        cmd = ['defuddle', 'parse', url, '-p', property]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Defuddle error: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Defuddle timeout")
    
    def extract_arxiv_paper(self, arxiv_id: str, output_dir: Optional[str] = None) -> Dict:
        """
        Extract arXiv paper information
        
        Args:
            arxiv_id: arXiv ID (e.g., '2301.07041')
            output_dir: Optional directory to save markdown
            
        Returns:
            Paper information dict
        """
        url = f"https://arxiv.org/abs/{arxiv_id}"
        
        # Extract content
        markdown, metadata = self.extract_markdown(url)
        
        # Parse arXiv-specific information
        paper_info = {
            'arxiv_id': arxiv_id,
            'title': metadata['title'],
            'abstract': self._extract_abstract(markdown),
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}",
            'arxiv_url': url,
            'markdown': markdown,
            'extracted_at': metadata['extracted_at']
        }
        
        # Save to file if directory provided
        if output_dir:
            output_path = Path(output_dir) / f"{arxiv_id}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"arxiv_id: {arxiv_id}\n")
                f.write(f"title: {paper_info['title']}\n")
                f.write(f"pdf: {paper_info['pdf_url']}\n")
                f.write(f"extracted: {paper_info['extracted_at']}\n")
                f.write(f"tags: [arxiv, paper]\n")
                f.write(f"---\n\n")
                f.write(f"# {paper_info['title']}\n\n")
                f.write(f"## Abstract\n\n")
                f.write(f"{paper_info['abstract']}\n\n")
                f.write(f"## Full Content\n\n")
                f.write(markdown)
        
        return paper_info
    
    def _extract_abstract(self, markdown: str) -> str:
        """Extract abstract from markdown"""
        lines = markdown.split('\n')
        abstract_lines = []
        in_abstract = False
        
        for line in lines:
            if 'Abstract' in line or '> Abstract' in line:
                in_abstract = True
                continue
            elif in_abstract:
                if line.startswith('##') or line.startswith('#'):
                    break
                abstract_lines.append(line)
        
        return '\n'.join(abstract_lines).strip()


def demo():
    """Run defuddle integration demo"""
    print("\n🔍 Defuddle Integration Demo\n")
    
    extractor = DefuddleExtractor()
    
    if not extractor.is_available():
        print("❌ Defuddle CLI not found!")
        print("Install with: npm install -g defuddle")
        return
    
    print("✅ Defuddle CLI available\n")
    
    # Demo 1: Extract arXiv paper
    print("="*70)
    print("Demo 1: Extract arXiv Paper")
    print("="*70)
    
    arxiv_id = "2301.07041"
    print(f"Extracting arXiv:{arxiv_id}...\n")
    
    try:
        paper = extractor.extract_arxiv_paper(arxiv_id)
        print(f"Title: {paper['title']}")
        print(f"PDF: {paper['pdf_url']}")
        print(f"Abstract (first 200 chars): {paper['abstract'][:200]}...")
        print(f"Markdown length: {len(paper['markdown'])} chars")
        print(f"Extracted at: {paper['extracted_at']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Demo 2: Extract metadata
    print("="*70)
    print("Demo 2: Extract Metadata")
    print("="*70)
    
    test_url = "https://arxiv.org/abs/2301.07041"
    print(f"URL: {test_url}\n")
    
    try:
        title = extractor.extract_metadata(test_url, 'title')
        description = extractor.extract_metadata(test_url, 'description')
        domain = extractor.extract_metadata(test_url, 'domain')
        
        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Domain: {domain}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Demo 3: Token savings estimate
    print("="*70)
    print("Demo 3: Token Savings Estimate")
    print("="*70)
    
    # Estimate: raw HTML ~100KB, clean markdown ~10KB
    raw_html_estimate = 100000  # chars
    clean_md_estimate = 10000   # chars
    savings = (1 - clean_md_estimate / raw_html_estimate) * 100
    
    print(f"Raw HTML: ~{raw_html_estimate/1000:.0f}K chars")
    print(f"Clean Markdown: ~{clean_md_estimate/1000:.0f}K chars")
    print(f"Token Savings: {savings:.0f}%")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Defuddle Integration')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--url', type=str, help='URL to extract')
    parser.add_argument('--arxiv', type=str, help='arXiv ID to extract')
    parser.add_argument('--output', type=str, help='Output directory')
    args = parser.parse_args()
    
    if args.demo or (not args.url and not args.arxiv):
        demo()
    elif args.arxiv:
        extractor = DefuddleExtractor()
        if not extractor.is_available():
            print("❌ Defuddle CLI not found. Install with: npm install -g defuddle")
            sys.exit(1)
        
        paper = extractor.extract_arxiv_paper(args.arxiv, args.output)
        print(f"✅ Extracted: {paper['title']}")
        if args.output:
            print(f"Saved to: {args.output}/{args.arxiv}.md")
    elif args.url:
        extractor = DefuddleExtractor()
        if not extractor.is_available():
            print("❌ Defuddle CLI not found. Install with: npm install -g defuddle")
            sys.exit(1)
        
        markdown, metadata = extractor.extract_markdown(args.url, args.output)
        print(f"✅ Extracted: {metadata['title']}")
        print(f"Domain: {metadata['domain']}")
        print(f"Markdown: {len(markdown)} chars")


if __name__ == "__main__":
    main()
