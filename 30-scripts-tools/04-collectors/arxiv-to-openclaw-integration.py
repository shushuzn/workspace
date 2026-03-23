#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv to OpenClaw Integration
Connects arXiv collector with OpenClaw analysis workflow

Workflow:
1. arXiv Collector → JSON data
2. PDF Downloader → PDF files
3. PDF Parser → Text content
4. OpenAI Analysis → Structured data
5. Memory System → Long-term storage
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Configuration
ARXIV_DATA_DIR = r"str(Path(__file__).parent.parent)\40-collectors\arxiv\data"
OPENCLAW_WORKSPACE = str(Path(__file__).parent.parent)
PDF_OUTPUT_DIR = r"str(Path(__file__).parent.parent)\40-collectors\arxiv\pdfs"
ANALYSIS_OUTPUT_DIR = r"str(Path(__file__).parent.parent)\40-collectors\arxiv\analysis"

# Create directories
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
os.makedirs(ANALYSIS_OUTPUT_DIR, exist_ok=True)

def load_arxiv_data(date=None):
    """Load arXiv JSON data from specified date"""
    if date is None:
        date = datetime.now().strftime('%Y%m%d')

    json_files = list(Path(ARXIV_DATA_DIR).glob(f"*_{date}.json"))

    if not json_files:
        print(f"[WARN] No data found for {date}")
        return []

    all_papers = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            papers = data.get('papers', [])
            all_papers.extend(papers)
            print(f"[INFO] Loaded {len(papers)} papers from {json_file.name}")

    return all_papers

def download_pdf(paper, output_dir):
    """Download PDF from arXiv"""
    try:
        # Convert arXiv abstract URL to PDF URL
        pdf_url = paper['link'].replace('abs', 'pdf')
        paper_id = paper.get('id', 'unknown').split('/')[-1]

        # Sanitize filename
        title_slug = paper['title'][:50].replace(':', '').replace('/', '')
        filename = f"{paper_id}_{title_slug}.pdf"
        filepath = os.path.join(output_dir, filename)

        # Download
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, headers=headers, timeout=30)

        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  [OK] Downloaded: {filename}")
            return filepath
        else:
            print(f"  [ERROR] Failed to download: {pdf_url}")
            return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

def batch_download_pdfs(papers, max_downloads=10):
    """Batch download PDFs"""
    downloaded = []

    print(f"\n[INFO] Downloading up to {max_downloads} PDFs...")

    for i, paper in enumerate(papers[:max_downloads]):
        print(f"[{i+1}/{max_downloads}] {paper['title'][:60]}...")
        filepath = download_pdf(paper, PDF_OUTPUT_DIR)
        if filepath:
            downloaded.append({
                'paper': paper,
                'pdf_path': filepath
            })

    print(f"\n[SUCCESS] Downloaded {len(downloaded)} PDFs")
    return downloaded

def create_analysis_manifest(downloaded_papers):
    """Create manifest for OpenClaw analysis"""
    manifest = {
        'createdAt': datetime.now().isoformat(),
        'totalPapers': len(downloaded_papers),
        'papers': []
    }

    for item in downloaded_papers:
        paper = item['paper']
        manifest['papers'].append({
            'id': paper.get('id', ''),
            'title': paper.get('title', ''),
            'authors': paper.get('authors', []),
            'pdf_path': item['pdf_path'],
            'arxiv_link': paper.get('link', ''),
            'status': 'pending_analysis'
        })

    # Save manifest
    manifest_file = os.path.join(ANALYSIS_OUTPUT_DIR, f"analysis_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Analysis manifest saved: {manifest_file}")
    return manifest_file

def main():
    print("=" * 70)
    print("arXiv to OpenClaw Integration")
    print("=" * 70)
    print()

    # Step 1: Load arXiv data
    print("[STEP 1] Loading arXiv data...")
    papers = load_arxiv_data()

    if not papers:
        print("[ERROR] No papers to process")
        return

    print(f"[INFO] Total papers: {len(papers)}")
    print()

    # Step 2: Download PDFs (top 10)
    print("[STEP 2] Downloading PDFs...")
    downloaded = batch_download_pdfs(papers, max_downloads=10)

    if not downloaded:
        print("[WARN] No PDFs downloaded")
        return

    print()

    # Step 3: Create analysis manifest
    print("[STEP 3] Creating analysis manifest...")
    manifest_file = create_analysis_manifest(downloaded)

    print()
    print("=" * 70)
    print("[SUMMARY]")
    print(f"  Papers collected: {len(papers)}")
    print(f"  PDFs downloaded: {len(downloaded)}")
    print(f"  Manifest created: {manifest_file}")
    print("=" * 70)
    print()
    print("[NEXT STEPS]")
    print("  1. Run OpenClaw PDF parser on downloaded PDFs")
    print("  2. Analyze with OpenAI")
    print("  3. Store in memory system")
    print()

if __name__ == '__main__':
    main()
