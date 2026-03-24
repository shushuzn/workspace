#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified arXiv Tool - Combines best features from scattered arXiv tools

Features:
- arxiv_api.py: Multiple search modes (query, author, title, category), PDF download
- arxiv_collector.py: Relevance scoring (0-100), category classification
- arxiv-论文: Daily collection, archive organization, risk monitoring output

Usage:
    python unified_arxiv.py search <query> [--category CAT] [--relevance]
    python unified_arxiv.py collect <category> [--days N]
    python unified_arxiv.py download <arxiv_id> [--output PATH]
    python unified_arxiv.py stats [--category CAT]
"""

import sys
import json
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


# =============================================================================
# API Layer (from arxiv_api.py)
# =============================================================================


class ArXivClient:
    """arXiv API 客户端 - Core search functionality from arxiv_api.py"""

    def __init__(self, max_results: int = 10):
        self.base_url = "http://export.arxiv.org/api/query"
        self.max_results = max_results

    def search(self, query: str, max_results: int = None) -> List[Dict]:
        """Search arXiv by query (title/author/abstract)"""
        if max_results is None:
            max_results = self.max_results

        search_query = urllib.parse.quote(query)
        url = f"{self.base_url}?search_query=all:{search_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                xml_data = response.read().decode("utf-8")
            return self._parse_response(xml_data)
        except Exception as e:
            print(f"arXiv API Error: {e}")
            return []

    def search_by_author(self, author: str, max_results: int = 10) -> List[Dict]:
        """Search by author name"""
        return self.search(f"au:{author}", max_results)

    def search_by_title(self, title: str, max_results: int = 10) -> List[Dict]:
        """Search by title"""
        return self.search(f"ti:{title}", max_results)

    def search_by_category(self, category: str, max_results: int = 10) -> List[Dict]:
        """Search by arXiv category (e.g., cs.AI, physics, etc.)"""
        query = f"cat:{category}"
        return self.search(query, max_results)

    def _parse_response(self, xml_data: str) -> List[Dict]:
        """Parse arXiv XML response"""
        papers = []
        root = ET.fromstring(xml_data)
        namespace = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        for entry in root.findall("atom:entry", namespace):
            paper = {
                "title": self._get_text(entry, "atom:title", namespace),
                "authors": [
                    a.text for a in entry.findall("atom:author/atom:name", namespace)
                ],
                "summary": self._get_text(entry, "atom:summary", namespace),
                "published": self._get_text(entry, "atom:published", namespace),
                "arxiv_id": self._get_arxiv_id(entry, namespace),
                "pdf_url": self._get_pdf_url(entry, namespace),
                "categories": [
                    c.get("term") for c in entry.findall("atom:category", namespace)
                ],
            }
            papers.append(paper)

        return papers

    def _get_text(self, entry: ET.Element, path: str, namespace: dict) -> str:
        """Get XML node text"""
        elem = entry.find(path, namespace)
        return elem.text.strip() if elem is not None and elem.text else ""

    def _get_arxiv_id(self, entry: ET.Element, namespace: dict) -> str:
        """Extract arXiv ID from entry"""
        id_elem = entry.find("atom:id", namespace)
        if id_elem is not None and id_elem.text:
            url = id_elem.text
            if "arxiv.org/abs/" in url:
                return url.split("arxiv.org/abs/")[-1]
        return ""

    def _get_pdf_url(self, entry: ET.Element, namespace: dict) -> str:
        """Generate PDF download URL"""
        arxiv_id = self._get_arxiv_id(entry, namespace)
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else ""

    def download_pdf(self, pdf_url: str, save_path: str) -> bool:
        """Download PDF file"""
        try:
            urllib.request.urlretrieve(pdf_url, save_path)
            return True
        except Exception as e:
            print(f"PDF download failed: {e}")
            return False


# =============================================================================
# Relevance Scoring (from arxiv_collector.py)
# =============================================================================


class PaperClassifier:
    """Classify papers by relevance score (0-100)"""

    def __init__(self):
        # Category-specific keywords for relevance scoring
        self.keywords = {
            "CNT": ["carbon nanotube", "nanotube", "conductivity", "CNT"],
            "AI": [
                "artificial intelligence",
                "neural network",
                "deep learning",
                "AI",
                "machine learning",
            ],
            "Agent": [
                "agent",
                "multi-agent",
                "autonomous",
                "LLM agent",
                "reinforcement learning",
            ],
            "ML": [
                "machine learning",
                "training",
                "model",
                "optimization",
                "neural network",
            ],
            "cs.AI": [
                "artificial intelligence",
                "neural network",
                "deep learning",
                "AI",
            ],
            "cs.LG": ["machine learning", "training", "neural network", "optimization"],
            "cs.CL": [
                "natural language",
                "language model",
                "LLM",
                "NLP",
                "transformer",
            ],
            "cs.CV": ["computer vision", "image", "detection", "segmentation"],
            "cs.MA": ["multi-agent", "distributed", "cooperative", "agent"],
            "physics": ["physics", "quantum", "particle", "photon"],
        }

    def classify(self, papers: List[Dict]) -> List[Dict]:
        """Add relevance scores to papers"""
        for paper in papers:
            score = self._calculate_relevance(paper)
            paper["relevance_score"] = score
            paper["relevance_level"] = self._get_level(score)
        # Sort by relevance
        papers.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return papers

    def _calculate_relevance(self, paper: Dict) -> int:
        """Calculate relevance score (0-100)"""
        title = paper.get("title", "").lower()
        summary = paper.get("summary", "").lower()
        categories = paper.get("categories", [])

        score = 0

        # Check each category's keywords
        for category in categories:
            keywords = self.keywords.get(category, [])
            for kw in keywords:
                if kw.lower() in title:
                    score += 20  # Title match (high weight)
                if kw.lower() in summary:
                    score += 5  # Summary match (medium weight)

        # Also check general AI keywords if no category match
        if score == 0:
            general_keywords = self.keywords.get("AI", [])
            for kw in general_keywords:
                if kw.lower() in title:
                    score += 20
                if kw.lower() in summary:
                    score += 5

        return min(score, 100)

    def _get_level(self, score: int) -> str:
        """Get relevance level from score"""
        if score >= 80:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        else:
            return "LOW"


# =============================================================================
# Archive Manager (from arxiv-论文)
# =============================================================================


class ArchiveManager:
    """Manage paper archive organization"""

    def __init__(self, archive_root: str = None):
        if archive_root is None:
            # Default to workspace archive folder
            archive_root = "D:/OpenClaw/workspace/30-scripts-tools/arxiv-archive"
        self.archive_root = Path(archive_root)
        self.archive_root.mkdir(parents=True, exist_ok=True)

    def get_archive_path(self, category: str = None) -> Path:
        """Get archive path for category (or today's date if no category)"""
        if category:
            return self.archive_root / category
        else:
            today = datetime.now().strftime("%Y-%m/%Y-%m-%d")
            return self.archive_root / today

    def save_paper(self, paper: Dict, category: str = None) -> str:
        """Save paper to archive as markdown"""
        # Determine path
        if category:
            path = self.get_archive_path(category)
        else:
            path = self.get_archive_path()

        path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        arxiv_id = paper.get("arxiv_id", "unknown")
        title = paper.get("title", "untitled")[:50].replace("/", "-").replace("\\", "-")
        filename = f"{arxiv_id}-{title}.md"
        filepath = path / filename

        # Create markdown content
        content = self._paper_to_markdown(paper)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return str(filepath)

    def save_batch(self, papers: List[Dict], category: str = None) -> List[str]:
        """Save multiple papers to archive"""
        saved = []
        for paper in papers:
            filepath = self.save_paper(paper, category)
            saved.append(filepath)
        return saved

    def _paper_to_markdown(self, paper: Dict) -> str:
        """Convert paper dict to markdown format"""
        md = []
        md.append("---")
        md.append(f"arxiv_id: {paper.get('arxiv_id', 'N/A')}")
        md.append(f"published: {paper.get('published', 'N/A')}")
        md.append(f"categories: {', '.join(paper.get('categories', []))}")
        if "relevance_score" in paper:
            md.append(f"relevance_score: {paper['relevance_score']}")
            md.append(f"relevance_level: {paper['relevance_level']}")
        md.append("---")
        md.append("")
        md.append(f"# {paper.get('title', 'Untitled')}")
        md.append("")
        md.append("## Authors")
        md.append("")
        for author in paper.get("authors", []):
            md.append(f"- {author}")
        md.append("")
        md.append("## Abstract")
        md.append("")
        md.append(paper.get("summary", ""))
        md.append("")
        md.append("## Links")
        md.append("")
        md.append(
            f"- [arXiv Abstract](https://arxiv.org/abs/{paper.get('arxiv_id', '')})"
        )
        md.append(f"- [PDF](https://arxiv.org/pdf/{paper.get('arxiv_id', '')}.pdf)")
        md.append("")
        md.append("## Notes")
        md.append("")
        md.append("<!-- Add your notes here -->")
        md.append("")

        return "\n".join(md)

    def get_stats(self, category: str = None) -> Dict:
        """Get archive statistics"""
        if category:
            path = self.get_archive_path(category)
        else:
            path = self.archive_root

        stats = {
            "total_papers": 0,
            "categories": {},
            "by_relevance": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "recent_papers": [],
        }

        if not path.exists():
            return stats

        # Walk through archive
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".md"):
                    stats["total_papers"] += 1

                    # Extract category from path
                    rel_path = Path(root).relative_to(self.archive_root)
                    cat = (
                        str(rel_path.parts[0]) if len(rel_path.parts) > 0 else "unknown"
                    )
                    stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

                    # Read relevance from file
                    filepath = Path(root) / file
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            if "relevance_level:" in content:
                                level = (
                                    content.split("relevance_level:")[1]
                                    .strip()
                                    .split()[0]
                                )
                                if level in stats["by_relevance"]:
                                    stats["by_relevance"][level] += 1
                    except:
                        pass

        return stats


# =============================================================================
# Daily Collector (combining arxiv_collector.py and arxiv-论文 patterns)
# =============================================================================


class DailyCollector:
    """Daily paper collection with archive organization"""

    def __init__(
        self, archive_manager: ArchiveManager = None, classifier: PaperClassifier = None
    ):
        self.client = ArXivClient(max_results=50)
        self.archive = archive_manager or ArchiveManager()
        self.classifier = classifier or PaperClassifier()

        # Category mapping (from arxiv_collector.py)
        self.category_map = {
            "CNT": ["cond-mat.mes-hall", "cond-mat.supr-con"],
            "AI": ["cs.AI", "cs.LG", "cs.CL"],
            "Agent": ["cs.AI", "cs.MA"],
            "ML": ["cs.LG", "stat.ML"],
        }

    def collect_category(
        self, category: str, days_back: int = 1, limit: int = 50
    ) -> List[Dict]:
        """Collect papers from a category"""
        papers = []

        # Get arXiv categories for this category
        arxiv_cats = self.category_map.get(category, [category])

        for cat in arxiv_cats:
            # Search by category
            results = self.client.search_by_category(cat, max_results=limit)

            # Add category tag
            for paper in results:
                paper["collection_category"] = category
                paper["arxiv_category"] = cat

            papers.extend(results)

        # Apply relevance scoring
        papers = self.classifier.classify(papers)

        # Save to archive
        saved_paths = self.archive.save_batch(papers, category)

        return papers

    def collect_all(
        self, categories: List[str] = None, days_back: int = 1, limit: int = 50
    ) -> Dict[str, List[Dict]]:
        """Collect papers from multiple categories"""
        if categories is None:
            categories = list(self.category_map.keys())

        results = {}
        for category in categories:
            print(f"Collecting {category}...")
            papers = self.collect_category(category, days_back, limit)
            results[category] = papers
            print(f"  Collected {len(papers)} papers")

        return results

    def collect_today(self, categories: List[str] = None) -> Dict[str, List[Dict]]:
        """Collect papers for today (alias for collect_all)"""
        return self.collect_all(categories, days_back=1)


# =============================================================================
# CLI Interface
# =============================================================================


def cmd_search(args):
    """Handle search command"""
    client = ArXivClient(max_results=args.max_results)
    classifier = PaperClassifier()

    # Build search query
    if args.author:
        papers = client.search_by_author(args.author, args.max_results)
        print(f"Searching by author: {args.author}")
    elif args.title:
        papers = client.search_by_title(args.title, args.max_results)
        print(f"Searching by title: {args.title}")
    elif args.category:
        papers = client.search_by_category(args.category, args.max_results)
        print(f"Searching category: {args.category}")
    else:
        papers = client.search(args.query, args.max_results)
        print(f"Searching: {args.query}")

    # Apply relevance scoring if requested
    if args.relevance:
        papers = classifier.classify(papers)

    # Output results
    if args.json:
        # Output as JSON
        output = []
        for paper in papers:
            entry = {
                "arxiv_id": paper["arxiv_id"],
                "title": paper["title"],
                "authors": paper["authors"],
                "summary": paper["summary"][:200] + "..."
                if len(paper["summary"]) > 200
                else paper["summary"],
                "published": paper["published"],
                "categories": paper["categories"],
            }
            if args.relevance:
                entry["relevance_score"] = paper["relevance_score"]
                entry["relevance_level"] = paper["relevance_level"]
            output.append(entry)
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        # Human-readable output
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper['title'][:80]}")
            print(f"   ID: {paper['arxiv_id']}")
            print(f"   Authors: {', '.join(paper['authors'][:3])}")
            if args.relevance:
                print(
                    f"   Relevance: {paper['relevance_score']} ({paper['relevance_level']})"
                )
            print(f"   Categories: {', '.join(paper['categories'][:3])}")
            print(f"   Summary: {paper['summary'][:150]}...")

    return papers


def cmd_collect(args):
    """Handle collect command"""
    collector = DailyCollector()

    print(f"Starting daily collection for category: {args.category}")
    print("=" * 60)

    papers = collector.collect_category(
        args.category, days_back=args.days, limit=args.limit
    )

    print("=" * 60)
    print(f"Collection complete: {len(papers)} papers")

    # Show stats
    stats = collector.archive.get_stats(args.category)
    print(f"\nArchive stats:")
    print(f"  Total papers in {args.category}: {stats['total_papers']}")

    return papers


def cmd_download(args):
    """Handle download command"""
    client = ArXivClient()

    # Generate PDF URL
    pdf_url = f"https://arxiv.org/pdf/{args.arxiv_id}.pdf"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path.cwd() / f"{args.arxiv_id}.pdf"

    print(f"Downloading {args.arxiv_id}...")
    print(f"  URL: {pdf_url}")
    print(f"  Output: {output_path}")

    success = client.download_pdf(pdf_url, str(output_path))

    if success:
        print(f"✓ Downloaded: {output_path}")
    else:
        print(f"✗ Download failed")

    return success


def cmd_stats(args):
    """Handle stats command"""
    archive = ArchiveManager()

    print("arXiv Archive Statistics")
    print("=" * 60)

    stats = archive.get_stats(args.category)

    print(f"\nTotal papers: {stats['total_papers']}")

    if stats["total_papers"] == 0:
        print("\nNo papers found in archive.")
        print("Run 'python unified_arxiv.py collect <category>' to collect papers.")
        return

    print(f"\nBy Category:")
    for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    print(f"\nBy Relevance:")
    for level in ["HIGH", "MEDIUM", "LOW"]:
        count = stats["by_relevance"].get(level, 0)
        if count > 0:
            print(f"  {level}: {count}")

    print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Unified arXiv Tool - Search, collect, and archive papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python unified_arxiv.py search "transformer" --relevance
  python unified_arxiv.py search --author "Geoffrey Hinton"
  python unified_arxiv.py search --category cs.AI --max-results 20
  python unified_arxiv.py collect AI
  python unified_arxiv.py download 2602.12345
  python unified_arxiv.py stats
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search arXiv papers")
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("--author", "-a", help="Search by author")
    search_parser.add_argument("--title", "-t", help="Search by title")
    search_parser.add_argument("--category", "-c", help="Search by category")
    search_parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=10,
        help="Maximum results (default: 10)",
    )
    search_parser.add_argument(
        "--relevance", "-r", action="store_true", help="Include relevance scores"
    )
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Collect command
    collect_parser = subparsers.add_parser(
        "collect", help="Collect papers from a category"
    )
    collect_parser.add_argument(
        "category", help="Category to collect (e.g., AI, Agent, CNT, ML)"
    )
    collect_parser.add_argument(
        "--days", "-d", type=int, default=1, help="Days back to collect (default: 1)"
    )
    collect_parser.add_argument(
        "--limit", "-l", type=int, default=50, help="Papers per category (default: 50)"
    )

    # Download command
    download_parser = subparsers.add_parser("download", help="Download paper PDF")
    download_parser.add_argument("arxiv_id", help="arXiv ID (e.g., 2602.12345)")
    download_parser.add_argument("--output", "-o", help="Output file path")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show archive statistics")
    stats_parser.add_argument("--category", "-c", help="Filter by category")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Execute command
    if args.command == "search":
        cmd_search(args)
    elif args.command == "collect":
        cmd_collect(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
