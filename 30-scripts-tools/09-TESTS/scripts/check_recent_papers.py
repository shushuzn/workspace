#!/usr/bin/env python3
"""Check recent LIG papers from last 3 days"""
import json
from datetime import datetime, timedelta
from pathlib import Path

papers = []
for f in Path('40-arxiv').glob('lig-papers-*.json'):
    try:
        with open(f) as fp:
            data = json.load(fp)
            if isinstance(data, dict):
                papers.extend(data.get('value', []))
            elif isinstance(data, list):
                papers.extend(data)
    except:
        pass

cutoff = datetime.now() - timedelta(days=3)
recent = []
for p in papers:
    try:
        collected = p.get('collected_at', '')
        if collected:
            dt = datetime.fromisoformat(collected.replace('+08:00', ''))
            if dt > cutoff and p.get('title') and p.get('title').strip():
                recent.append(p)
    except:
        pass

recent.sort(key=lambda x: x.get('collected_at', ''), reverse=True)

print(f'Total papers: {len(papers)}')
print(f'Recent (3 days): {len(recent)}')
print()
for i, p in enumerate(recent[:10]):
    title = p.get('title', 'N/A')[:80]
    source = p.get('source', 'N/A')
    date = p.get('collected_at', 'N/A')[:10]
    pmid = p.get('pmid', p.get('arxiv_id', 'N/A'))
    print(f'{i +1}. [{source}] {title}')
    print(f'   ID: {pmid} | Date: {date}')
    print()
