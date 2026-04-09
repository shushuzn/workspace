#!/usr/bin/env python3
"""Check wiki entries for staleness (>30 days)"""
import json, time, os

idx_path = os.path.join(os.path.dirname(__file__), 'wiki-index.json')
try:
    data = json.load(open(idx_path, encoding='utf-8'))
    entries = data.get('entries', []) if isinstance(data, dict) else data
except:
    print('No index found')
    exit(1)

now = time.time()
old = [e for e in entries if now - e.get('mtime', 0) > 30*86400]
print('Old entries:', len(old))
for e in old[:5]:
    print(' ', e.get('title', 'no-title')[:60])
