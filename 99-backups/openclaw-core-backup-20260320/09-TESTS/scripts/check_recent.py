#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timedelta

f = Path('40-arxiv/lig-papers-20260309-155045.json')
data = json.load(open(f, encoding='utf-8-sig'))

print('Type:', type(data))
if isinstance(data, dict):
    papers = data.get('value', [])
elif isinstance(data, list):
    papers = data
else:
    papers = []

print(f'Paper count: {len(papers)}')

# Check dates
cutoff = datetime.now() - timedelta(days=3)
recent = []
for p in papers:
    try:
        collected = p.get('collected_at', '')
        if collected:
            dt = datetime.fromisoformat(collected.replace('+08:00', ''))
            if dt > cutoff and p.get('title') and p.get('title').strip():
                recent.append(p)
    except Exception as e:
        pass

print(f'Recent (3 days): {len(recent)}')
print()
for i, p in enumerate(recent[:10]):
    title = p.get('title', 'N/A')[:70]
    source = p.get('source', 'N/A')
    date = p.get('collected_at', 'N/A')[:10]
    pmid = p.get('pmid', p.get('arxiv_id', 'N/A'))
    print(f'{i +1}. [{source}] {title}')
    print(f'   ID: {pmid} | Collected: {date}')
    print()
