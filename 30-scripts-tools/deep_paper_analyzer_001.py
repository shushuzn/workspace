#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEEP-PAPER-ANALYZER-001 Extended Paper Analysis
4-STAGE: ARCHITECT to CODE to ASK to DEBUG

STAGE 1: ARCHITECT
Purpose:
    - Extract full paper content section by section
    - Analyze methods, results, discussion in depth
    - Extract methodological framework
    - Generate actionable insights

Data Flow:
    PDF -> Extract All -> Parse Sections -> Deep Analysis -> Report
"""
import sys
import re
import json
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pdfplumber
    PDF_LIB = "pdfplumber"
except ImportError:
    PDF_LIB = None


def extract_full_text(pdf_path):
    """Extract full text from PDF"""
    if not PDF_LIB:
        return None
    
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"[PAGE {i+1}]\n{text}")
    
    return "\n\n".join(full_text)


def parse_sections(text):
    """Parse paper into logical sections"""
    sections = {}
    
    # Define section markers
    markers = {
        "abstract": r"(?:^|\n)(abstract)",
        "introduction": r"(?:^|\n)(1\.?\s*introduction|introduction)",
        "background": r"(?:^|\n)(background|related\s*work|literature\s*review)",
        "methods": r"(?:^|\n)(2\.?\s*method|methodology|approach|experimental|design|procedure)",
        "results": r"(?:^|\n)(3\.?\s*result|experiment|finding|result|evaluation|analysis)",
        "discussion": r"(?:^|\n)(4\.?\s*discussion|discussion|implication)",
        "conclusion": r"(?:^|\n)(conclusion|conclusions|summary|future\s*work|limitation)",
        "references": r"(?:^|\n)(reference|bibliography|citation)"
    }
    
    # Find section boundaries
    section_positions = {}
    for section, pattern in markers.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            section_positions[match.start()] = section
    
    # Sort by position
    sorted_sections = sorted(section_positions.items(), key=lambda x: x[0])
    
    # Extract text for each section
    for i, (pos, name) in enumerate(sorted_sections):
        start = pos
        end = sorted_sections[i+1][0] if i+1 < len(sorted_sections) else len(text)
        section_text = text[start:end].strip()
        sections[name] = section_text[:5000]  # Limit size
    
    return sections


def analyze_methods(text):
    """Deep analysis of methods section"""
    analysis = {
        "paradigm": [],
        "measures": [],
        "tasks": [],
        "analysis_methods": [],
        "sample_size": None
    }
    
    # Find research paradigm
    paradigms = ["experiment", "survey", "longitudinal", "case study", "meta-analysis", "review"]
    for p in paradigms:
        if p.lower() in text.lower():
            analysis["paradigm"].append(p)
    
    # Find cognitive measures
    cognitive_terms = [
        "attention", "memory", "working memory", "executive function",
        "reaction time", "accuracy", "precision", "recall",
        "processing speed", "fluency", "flexibility"
    ]
    for term in cognitive_terms:
        if term.lower() in text.lower():
            analysis["measures"].append(term)
    
    # Find tasks
    task_patterns = [
        r"task[:\s]+([^.]{10,50})",
        r"using\s+(\w+\s+task)",
        r"(\w+)\s+task"
    ]
    for pattern in task_patterns:
        matches = re.findall(pattern, text, re.I)
        analysis["tasks"].extend(matches[:3])
    
    # Find sample size
    n_match = re.search(r"(?:n|participants?|subjects?|sample)[:\s]*[=:]?\s*(\d+)", text, re.I)
    if n_match:
        analysis["sample_size"] = n_match.group(1)
    
    return analysis


def analyze_results(text):
    """Deep analysis of results section"""
    analysis = {
        "key_findings": [],
        "effect_sizes": [],
        "significance": [],
        "comparisons": []
    }
    
    # Find key findings
    finding_patterns = [
        r"found\s+(?:that\s+)?([^.]+\.)",
        r"showed?\s+(?:that\s+)?([^.]+\.)",
        r"demonstrated?\s+(?:that\s+)?([^.]+\.)",
        r"results\s+(?:show|indicate|suggest)\s+(?:that\s+)?([^.]+\.)"
    ]
    
    for pattern in finding_patterns:
        matches = re.findall(pattern, text, re.I)
        analysis["key_findings"].extend(matches[:2])
    
    # Find effect sizes
    effect_matches = re.findall(r"(?:d|Cohen|f|r|p)\s*[=<>:]\s*[\d.]+", text)
    analysis["effect_sizes"] = effect_matches[:5]
    
    # Find significance
    sig_matches = re.findall(r"p\s*[<>:]\s*[\d.]+", text)
    analysis["significance"] = sig_matches[:5]
    
    return analysis


def analyze_arguments(text):
    """Analyze author's arguments and claims"""
    analysis = {
        "main_claim": None,
        "supporting_claims": [],
        "counterarguments": [],
        "evidence_quality": []
    }
    
    # Find main claim (usually in abstract or intro)
    abstract_match = re.search(r"abstract\s*\n?\s*([^.]{100,500})", text, re.I)
    if abstract_match:
        analysis["main_claim"] = abstract_match.group(1).strip()
    
    # Find supporting claims
    claim_patterns = [
        r"(?:has\s+been\s+)?shown\s+(?:to\s+)?([^.]+\.)",
        r"evidence\s+(?:suggests|shows|indicates)\s+([^.]+\.)",
        r"studies?\s+(?:have\s+)?(?:shown|demonstrated)\s+([^.]+\.)"
    ]
    for pattern in claim_patterns:
        matches = re.findall(pattern, text, re.I)
        analysis["supporting_claims"].extend(matches[:3])
    
    # Find limitations/counterarguments
    limit_patterns = [
        r"limitations?\s*[:\-]?\s*([^.]+\.)",
        r"however\s*[,;]\s*([^.]+\.)",
        r"criticism\s*[:\-]?\s*([^.]+\.)",
        r"controversy\s*[:\-]?\s*([^.]+\.)"
    ]
    for pattern in limit_patterns:
        matches = re.findall(pattern, text, re.I)
        analysis["counterarguments"].extend(matches[:3])
    
    return analysis


def generate_deep_report(pdf_path, text):
    """Generate comprehensive deep analysis report"""
    sections = parse_sections(text)
    methods = analyze_methods(sections.get("methods", text))
    results = analyze_results(sections.get("results", text))
    arguments = analyze_arguments(text)
    
    report = []
    report.append("=" * 80)
    report.append("DEEP PAPER ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    report.append(f"Paper: {pdf_path}")
    report.append(f"Library: {PDF_LIB}")
    report.append(f"Total length: {len(text)} chars")
    report.append("")
    
    # Sections overview
    report.append("-" * 80)
    report.append("SECTION STRUCTURE")
    report.append("-" * 80)
    for section, content in sections.items():
        report.append(f"  {section.upper()}: {len(content)} chars")
    report.append("")
    
    # Main argument
    report.append("-" * 80)
    report.append("MAIN ARGUMENT (Abstract)")
    report.append("-" * 80)
    if arguments.get("main_claim"):
        report.append(arguments["main_claim"][:500])
    else:
        report.append("[Could not extract main claim]")
    report.append("")
    
    # Methods
    report.append("-" * 80)
    report.append("METHODOLOGY")
    report.append("-" * 80)
    report.append(f"  Paradigm: {', '.join(methods['paradigm']) if methods['paradigm'] else 'Not specified'}")
    report.append(f"  Sample Size: {methods['sample_size'] or 'Not specified'}")
    report.append(f"  Cognitive Measures ({len(methods['measures'])}):")
    for m in methods['measures'][:5]:
        report.append(f"    - {m}")
    report.append("")
    
    # Results
    report.append("-" * 80)
    report.append("KEY FINDINGS")
    report.append("-" * 80)
    if results['key_findings']:
        for finding in results['key_findings'][:5]:
            report.append(f"  - {finding[:150]}...")
    else:
        report.append("  [Could not extract specific findings]")
    
    if results['significance']:
        report.append(f"\n  Statistical Significance: {', '.join(results['significance'][:3])}")
    report.append("")
    
    # Limitations
    report.append("-" * 80)
    report.append("LIMITATIONS & COUNTERARGUMENTS")
    report.append("-" * 80)
    if arguments['counterarguments']:
        for arg in arguments['counterarguments'][:3]:
            report.append(f"  - {arg[:150]}...")
    else:
        report.append("  [Could not extract limitations]")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: deep_paper_analyzer_001.py <pdf_path>")
        print("       deep_paper_analyzer_001.py <pdf_path> --json")
        return
    
    pdf_path = sys.argv[1]
    
    if not PDF_LIB:
        print("[ERROR] pdfplumber not available")
        return
    
    print(f"[DEEP-PAPER-ANALYZER-001] Extracting: {pdf_path}", file=sys.stderr)
    
    text = extract_full_text(pdf_path)
    if not text:
        print("[ERROR] Could not extract text")
        return
    
    sections = parse_sections(text)
    methods = analyze_methods(sections.get("methods", text))
    results = analyze_results(sections.get("results", text))
    arguments = analyze_arguments(text)
    
    if "--json" in sys.argv:
        print(json.dumps({
            "sections": list(sections.keys()),
            "methods": methods,
            "results": {k: v[:10] for k, v in results.items()},
            "arguments": {k: v[:5] if isinstance(v, list) else v for k, v in arguments.items()}
        }, indent=2))
    else:
        print(generate_deep_report(pdf_path, text))


if __name__ == "__main__":
    main()

# STAGE 3: ASK
"""
ASK: Run verification
    py deep_paper_analyzer_001.py <pdf_path>
    py deep_paper_analyzer_001.py <pdf_path> --json
"""

# STAGE 4: DEBUG
"""
DEBUG:
    - 2026-03-21: Created deep paper analyzer
    - 2026-03-21: Extracting full content from 2603.09753
"""
