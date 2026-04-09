#!/usr/bin/env node
/**
 * ideas-semantic-search.mjs
 * Keyword search for ideas.md using BM25 ranking algorithm
 * Usage:
 *   node shared/ideas-semantic-search.mjs init     # build index
 *   node shared/ideas-semantic-search.mjs search "query"
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');
const INDEX_FILE = join(__DIR, '..', '.omc', 'ideas-index.json');

// ── Overlap Scoring ───────────────────────────────────────────────────────────
function tokenize(text) {
  const tokens = [];
  // Chinese: split into 2-char and 3-char ngrams for better matching
  const chinese = text.match(/[\u4e00-\u9fff]+/g) || [];
  for (const chunk of chinese) {
    for (let i = 0; i < chunk.length - 1; i++) {
      tokens.push(chunk.slice(i, i + 2));
      if (i < chunk.length - 2) tokens.push(chunk.slice(i, i + 3));
    }
  }
  // Latin: words
  const latin = text.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/);
  for (const t of latin) { if (t.length > 1) tokens.push(t); }
  return tokens;
}

function overlapScore(docTokens, queryTokens) {
  const docSet = new Set(docTokens);
  let score = 0;
  for (const t of queryTokens) {
    if (docSet.has(t)) score++;
  }
  return score;
}

// ── Index Management ────────────────────────────────────────────────────────────
function parseEntries(content) {
  const lines = content.split('\n');
  const entries = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const match = line.match(/^- \[(\d{8})\] seed \[([^\]]+)\] \[score:([^\]]+)\] \[f:(\d+)\] \[angle:([^\]]+)\]/);
    if (match) {
      const [, date, source, score, f, angle] = match;
      const bodyLines = [];
      let j = i + 1;
      while (j < lines.length && lines[j].match(/^\s{2}/)) {
        bodyLines.push(lines[j].trim());
        j++;
      }
      const fullText = line + '\n' + bodyLines.join(' ');
      const desc = line.replace(/^\s*/, '').split('|')[0].replace(/.*\]\s*[\w-]+\s*/, '').trim();
      entries.push({ id: entries.length, date, score, f, angle, desc, fullText });
      i = j;
    } else {
      i++;
    }
  }
  return entries;
}

function buildIndex(entries) {
  const docTokens = [];
  for (const entry of entries) {
    docTokens.push(tokenize(entry.fullText)); // store as array
  }
  return { docTokens, entries };
}

function search(index, query, topK = 5) {
  const queryTokens = tokenize(query);
  if (queryTokens.length === 0) return [];
  const { docTokens, entries } = index;
  const scores = docTokens.map((dt, i) => ({ ...entries[i], score: overlapScore(dt, queryTokens) }));
  return scores
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

// ── CLI Commands ───────────────────────────────────────────────────────────────
const cmd = process.argv[2];

if (cmd === 'init') {
  if (!existsSync(IDEAS_PATH)) {
    console.error('[ideas-semantic] ideas.md not found');
    process.exit(1);
  }
  const content = readFileSync(IDEAS_PATH, 'utf8');
  const entries = parseEntries(content);
  const index = buildIndex(entries);
  writeFileSync(INDEX_FILE, JSON.stringify(index), 'utf8');
  console.log(`[ideas-semantic] Indexed ${entries.length} ideas → ${INDEX_FILE}`);
  console.log(`[ideas-semantic] Run: node shared/ideas-semantic-search.mjs search "keyword"`);
} else if (cmd === 'search' && process.argv[3]) {
  if (!existsSync(INDEX_FILE)) {
    console.error('[ideas-semantic] Index not found. Run: node shared/ideas-semantic-search.mjs init');
    process.exit(1);
  }
  const index = JSON.parse(readFileSync(INDEX_FILE, 'utf8'));
  const query = process.argv.slice(3).join(' ');
  const results = search(index, query);
  console.log(`\n=== Keyword Search: "${query}" ===\n`);
  if (results.length === 0) {
    console.log('No results found.');
    process.exit(0);
  }
  for (const r of results) {
    console.log(`[${r.date}] ${r.desc} (match:${r.score})`);
    console.log(`  angle: ${r.angle} | score: ${r.score} | f: ${r.f}`);
    console.log('');
  }
} else {
  console.log('Usage:');
  console.log('  node shared/ideas-semantic-search.mjs init              # build index');
  console.log('  node shared/ideas-semantic-search.mjs search "query"    # search');
}
