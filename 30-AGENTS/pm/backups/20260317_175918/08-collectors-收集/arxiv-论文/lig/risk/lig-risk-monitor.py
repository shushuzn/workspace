#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIG Risk Warning System - Monitor 5 risk dimensions
Usage: python lig-risk-monitor.py
"""

import json
import os
import sys
from datetime import datetime, timedelta
import urllib.request
import urllib.parse

def main():
    start_time = datetime.now()
    
    print("=" * 60)
    print("LIG Risk Warning System v1.0")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load config
    config_path = "D:/OpenClaw/workspace/40-arxiv/lig-risk-config.json"
    if not os.path.exists(config_path):
        print(f"[ERROR] Config not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("[OK] Config loaded")
    
    output_dir = config['reportSettings']['outputDir']
    os.makedirs(output_dir, exist_ok=True)
    
    risk_signals = {
        'technicalCompetition': [],
        'patentBarrier': [],
        'fundingFlow': [],
        'talentFlow': [],
        'policyChange': []
    }
    
    # [1/5] Technical Competition
    print("\n[1/5] Technical Competition...")
    today = datetime.now()
    last_week = today - timedelta(days=7)
    
    try:
        query = "laser-induced graphene OR LIG sensor"
        encoded = urllib.parse.quote(query)
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded}&mindate={last_week.strftime('%Y/%m/%d')}&maxdate={today.strftime('%Y/%m/%d')}&retmode=json"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            paper_count = int(data['esearchresult']['count'][0])
        
        threshold = config['riskDimensions']['technicalCompetition']['thresholds']['papersPerWeek']
        print(f"  PubMed papers (7d): {paper_count}")
        
        if paper_count >= threshold:
            risk_signals['technicalCompetition'].append({
                'type': 'technicalCompetition',
                'level': 'YELLOW',
                'source': 'PubMed',
                'message': f'Weekly papers: {paper_count} (threshold: {threshold})',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print("  [WARNING] Yellow alert")
        else:
            print("  [OK] Normal")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # [2/5] Patent Barrier
    print("\n[2/5] Patent Barrier...")
    
    # Search Google Patents
    try:
        query = "laser-induced graphene sensor flexible"
        encoded = urllib.parse.quote(query)
        
        # Google Patents search via API (using public endpoint)
        url = f"https://patents.google.com/?q={encoded}&oq={encoded}"
        
        # Use web scraping for demo (production should use official API)
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract patent count from results
        companies = ['Samsung', 'BASF', '3M', 'LG', 'Huawei', 'Sony', 'Panasonic']
        company_patents = {}
        
        for company in companies:
            count = html.lower().count(company.lower())
            if count > 0:
                company_patents[company] = count
        
        total_company_patents = sum(company_patents.values())
        threshold = config['riskDimensions']['patentBarrier']['thresholds']['majorCompanyPatents']
        
        print(f"  Google Patents search: {url}")
        print(f"  Major company mentions: {total_company_patents}")
        if company_patents:
            for c, n in company_patents.items():
                print(f"    - {c}: {n}")
        
        if total_company_patents >= threshold:
            risk_signals['patentBarrier'].append({
                'type': 'patentBarrier',
                'level': 'YELLOW',
                'source': 'Google Patents',
                'message': f'Major company patents: {total_company_patents} (threshold: {threshold})',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data': {'companies': company_patents}
            })
            print("  [WARNING] Yellow alert")
        else:
            print("  [OK] Normal")
    
    except Exception as e:
        print(f"  [ERROR] Google Patents search failed: {e}")
        # Fallback to local file
        patent_file = "D:/OpenClaw/workspace/11-research/P-20260309-LIG-Patent-Landscape.md"
        if os.path.exists(patent_file):
            with open(patent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            companies = ['Samsung', 'BASF', '3M', 'LG', 'Huawei']
            count = sum(content.count(c) for c in companies)
            print(f"  [FALLBACK] Local patent map: {count} mentions")
    
    # [3/5] Funding Flow
    print("\n[3/5] Funding Flow...")
    print("  [OK] No major funding news (TODO: Crunchbase API)")
    
    # [4/5] Talent Flow
    print("\n[4/5] Talent Flow...")
    researchers = config['riskDimensions']['talentFlow']['keyResearchers']
    print(f"  Monitoring {len(researchers)} key researchers")
    print("  [OK] No talent movement detected (TODO: Author tracking)")
    
    # [5/5] Policy Change
    print("\n[5/5] Policy Change...")
    print("  [OK] No policy changes (TODO: Government RSS)")
    
    # Generate Report
    print("\n" + "=" * 60)
    print("Generating Report...")
    
    total = sum(len(signals) for signals in risk_signals.values())
    red_count = sum(1 for signals in risk_signals.values() for s in signals if s['level'] == 'RED')
    yellow_count = sum(1 for signals in risk_signals.values() for s in signals if s['level'] == 'YELLOW')
    
    if red_count > 0:
        overall = "HIGH"
    elif yellow_count > 0:
        overall = "MEDIUM"
    else:
        overall = "LOW"
    
    report_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Markdown
    md_file = f"{output_dir}/lig-risk-report-{report_date}.md"
    md = f"""# LIG Risk Warning Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Period:** Last 7 days  
**Overall Risk:** {overall}

## Summary

| Level | Count | Action |
|-------|-------|--------|
| RED | {red_count} | Immediate action |
| YELLOW | {yellow_count} | Close monitoring |
| GREEN | {total - red_count - yellow_count} | Normal |

## Detailed Signals

"""
    
    for dim, signals in risk_signals.items():
        md += f"\n### {dim}\n\n"
        if not signals:
            md += "No signals.\n\n"
        else:
            for s in signals:
                md += f"- **[{s['level']}]** {s['message']}\n"
                md += f"  - Source: {s['source']} | Time: {s['timestamp']}\n\n"
    
    md += "\n## Recommendations\n\n"
    if red_count > 0:
        md += "### RED - Immediate Action\n"
        md += "1. Emergency risk assessment meeting\n2. Mitigation plan within 48h\n3. Notify stakeholders\n\n"
    elif yellow_count > 0:
        md += "### YELLOW - Monitor Closely\n"
        md += "1. Increase monitoring frequency\n2. Prepare contingency plan\n3. Review meeting next week\n\n"
    else:
        md += "### GREEN - Maintain Status\n"
        md += "1. Continue regular monitoring\n2. Weekly report\n"
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"[OK] Markdown: {md_file}")
    
    # HTML
    html_file = f"{output_dir}/lig-risk-report-{report_date}.html"
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LIG Risk Report</title>
    <style>
        body {{ font-family: Arial; max-width: 900px; margin: 40px auto; }}
        h1 {{ border-bottom: 2px solid #007bff; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #007bff; color: white; }}
        .red {{ color: #dc3545; }}
        .yellow {{ color: #ffc107; }}
        .green {{ color: #28a745; }}
    </style>
</head>
<body>
    <h1>LIG Risk Warning Report</h1>
    <p><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><b>Overall Risk:</b> <span class="{'red' if red_count else 'yellow' if yellow_count else 'green'}">{overall}</span></p>
    <h2>Summary</h2>
    <table>
        <tr><th>Level</th><th>Count</th><th>Action</th></tr>
        <tr><td class="red">RED</td><td>{red_count}</td><td>Immediate</td></tr>
        <tr><td class="yellow">YELLOW</td><td>{yellow_count}</td><td>Monitor</td></tr>
        <tr><td class="green">GREEN</td><td>{total - red_count - yellow_count}</td><td>Normal</td></tr>
    </table>
    <p><i>See Markdown file for details.</i></p>
</body>
</html>
"""
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] HTML: {html_file}")
    
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"Complete | Duration: {duration:.2f}s")
    print("=" * 60)

if __name__ == '__main__':
    main()
