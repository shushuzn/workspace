#!/usr/bin/env python3
"""Fuzzy search for wiki-indexer entries"""
import sys, json, os

q = sys.argv[1] if len(sys.argv) > 1 else ''
idx_path = os.path.join(os.path.dirname(__file__), 'wiki-index.json')
try:
    data = json.load(open(idx_path, encoding='utf-8'))
    entries = data.get('entries', []) if isinstance(data, dict) else data
except:
    print('No index found. Run: node shared/wiki-indexer.mjs --rebuild')
    sys.exit(1)

q_lower = q.lower()
res = [e for e in entries if q_lower in e.get('title', '').lower()][:10]
for e in res:
    print(e.get('title', 'no-title'))
if not res:
    print('No matches for:', q)
