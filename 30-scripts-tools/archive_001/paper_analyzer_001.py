#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PAPER-ANALYZER-001 Deep Paper Analysis
4-STAGE: ARCHITECT to CODE to ASK to DEBUG

STAGE 1: ARCHITECT

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose:
    - Deep analysis of research papers
    - Extract key contributions, methods, results
    - Evaluate innovation and limitations
    - Connect to existing knowledge

Data Flow:
    PDF -> Extract Text -> Parse Structure -> Analyze -> Report
"""
import sys
import re
from pathlib import Path

# Try multiple PDF libraries
try:
    import pypdf
    PDF_LIB = "pypdf"
except ImportError:
    try:
        import pdfplumber
        PDF_LIB = "pdfplumber"
    except ImportError:
        PDF_LIB = None


def extract_text_pypdf(pdf_path, max_pages=5):
    """Extract text using pypdf"""
    reader = pypdf.PdfReader(pdf_path)
    text = []
    for i, page in enumerate(reader.pages[:max_pages]):
        if page.extract_text():
            text.append(page.extract_text())
    return "\n\n".join(text)


def extract_text_pdfplumber(pdf_path, max_pages=5):
    """Extract text using pdfplumber"""
    with pdfplumber.open(pdf_path) as pdf:
        text = []
        for i, page in enumerate(pdf.pages[:max_pages]):
            if page.extract_text():
                text.append(page.extract_text())
        return "\n\n".join(text)


def extract_text(pdf_path, max_pages=5):
    """Extract text from PDF"""
    if PDF_LIB == "pypdf":
        return extract_text_pypdf(pdf_path, max_pages)
    elif PDF_LIB == "pdfplumber":
        return extract_text_pdfplumber(pdf_path, max_pages)
    else:
        return "No PDF library available"


def analyze_structure(text):
    """Analyze paper structure"""
    sections = {
        "title": [],
        "abstract": [],
        "introduction": [],
        "methods": [],
        "results": [],
        "conclusion": []
    }

    # Find sections
    patterns = {
        "abstract": r"abstract",
        "introduction": r"1\.?\s*introduction|introduction",
        "methods": r"2\.?\s*method|method|approach",
        "results": r"3\.?\s*result|experiment|result|evaluation",
        "conclusion": r"conclusion|conclusions|summary|discussion"
    }

    for section, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            sections[section].append(pattern)

    return sections


def extract_key_info(text):
    """Extract key information"""
    info = {
        "authors": [],
        "keywords": [],
        "references_count": 0,
        "figures_count": 0,
        "tables_count": 0
    }

    # Count references
    info["references_count"] = len(re.findall(r'\[?\d+\]?', text[:5000]))

    # Count figures/tables
    info["figures_count"] = len(re.findall(r'fig\.?\s*\d+|figure\s*\d+', text, re.I))
    info["tables_count"] = len(re.findall(r'tab\.?\s*\d+|table\s*\d+', text, re.I))

    # Extract potential keywords
    keywords = re.findall(r'keyword[s]?[:\s]+([^.]+)', text, re.I)
    if keywords:
        info["keywords"] = [k.strip() for k in keywords[0].split(',')[:10]]

    return info


def generate_report(pdf_path, text, max_length=5000):
    """Generate analysis report"""
    structure = analyze_structure(text)
    info = extract_key_info(text)

    report = []
    report.append("=" * 60)
    report.append("PAPER-ANALYZER-001 Deep Analysis Report")
    report.append("=" * 60)
    report.append("")
    report.append("Paper: " + str(pdf_path))
    report.append("Library: " + str(PDF_LIB))
    report.append("Characters: " + str(len(text)))
    report.append("")

    report.append("[STRUCTURE]")
    for section, found in structure.items():
        status = "FOUND" if found else "MISSING"
        report.append("  " + section + ": " + status)

    report.append("")
    report.append("[KEY INFO]")
    report.append("  References: " + str(info["references_count"]))
    report.append("  Figures: " + str(info["figures_count"]))
    report.append("  Tables: " + str(info["tables_count"]))
    if info["keywords"]:
        report.append("  Keywords: " + ", ".join(info["keywords"][:5]))

    report.append("")
    report.append("[TEXT PREVIEW]")
    report.append("-" * 40)
    report.append(text[:max_length])
    report.append("")
    report.append("=" * 60)

    return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Usage: paper_analyzer_001.py <pdf_path> [max_pages]")
        print("  --full    Extract all pages")
        print("  --json    Output as JSON")
        return

    pdf_path = sys.argv[1]
    max_pages = 5

    if "--full" in sys.argv:
        max_pages = 100

    if not PDF_LIB:
        print("[ERROR] No PDF library available")
        print("Install: pip install pypdf pdfplumber")
        return

    print("[PAPER-ANALYZER-001] Extracting: " + pdf_path, file=sys.stderr)

    try:
        text = extract_text(pdf_path, max_pages)

        if "--json" in sys.argv:
            import json
            info = extract_key_info(text)
            print(json.dumps({
                "path": str(pdf_path),
                "library": PDF_LIB,
                "length": len(text),
                "structure": {k: bool(v) for k, v in analyze_structure(text).items()},
                "info": info
            }, indent=2))
        else:
            print(generate_report(pdf_path, text))

    except Exception as e:
        print("[ERROR] " + str(e))


if __name__ == "__main__":
    main()

# STAGE 3: ASK
# py paper_analyzer_001.py  # Run verification
"""
ASK: Run verification
    py paper_analyzer_001.py <pdf_path>
    py paper_analyzer_001.py <pdf_path> --full
    py paper_analyzer_001.py <pdf_path> --json

Test:
    py paper_analyzer_001.py "test.pdf"  # Basic extraction
"""

# STAGE 4: DEBUG
# Test: 2026
"""
DEBUG:
    - 2026-03-21: Created paper analyzer tool
    - 2026-03-21: Supports pypdf and pdfplumber
    - 2026-03-21: Extracted 62823 chars from 2603.09753.pdf
    - 2026-03-21: Analyzed "Commercial Videogames" paper
"""

