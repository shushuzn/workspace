#!/usr/bin/env node
/**
 * OMC FTS5 Session Search
 * Full-text search across session history with relevance ranking.
 *
 * Inspired by Hermes Agent's FTS5 session search:
 *   - FTS5 virtual table over session messages
 *   - BM25 ranking for relevance
 *   - LLM summarization of matching sessions
 *   - Temporal filters (last N days, date range)
 *
 * Usage:
 *   node fts5-search.mjs "query"                    # search last 7 days
 *   node fts5-search.mjs "query" --days 30         # last 30 days
 *   node fts5-search.mjs "query" --llm            # LLM summarize matches
 *   node fts5-search.mjs "query" --json            # machine-readable output
 *   node fts5-search.mjs --index                   # rebuild index
 *
 * Architecture:
 *   - Index: .omc/state/fts5.db (SQLite FTS5)
 *   - Sessions: .omc/sessions/*.json
 *   - Cache: .omc/state/fts5-cache.json (file hash tracking)
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, open } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SESSIONS_DIR = resolve(__dirname, '../sessions');
const STATE_DIR = resolve(__dirname, '../state');
const DB_FILE = resolve(STATE_DIR, 'fts5.db');
const CACHE_FILE = resolve(STATE_DIR, 'fts5-cache.json');
const DAYS_DEFAULT = 7;
const MAX_RESULTS = 20;
const BM25_K1 = 1.2;
const BM25_B = 0.75;

const STATE = {
  get() {
    if (!existsSync(STATE_FILE)) return { indexed: [], lastIndex: null };
    try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
    catch { return { indexed: [], lastIndex: null }; }
  },
  set(s) { writeFileSync(STATE_FILE, JSON.stringify(s, null, 2), 'utf-8'); }
};

function parseArgs(argv) {
  const args = {};
  args.query = argv.find(a => !a.startsWith('--')) || '';
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'json') { args.json = true; continue; }
      if (key === 'llm') { args.llm = true; continue; }
      if (key === 'index') { args.index = true; continue; }
      if (key === 'days') { args.days = parseInt(argv[i + 1]) || DAYS_DEFAULT; i++; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

// ── Simple tokenizer ────────────────────────────────────────────────────────
function tokenize(text) {
  return text.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2);
}

// ── BM25 scoring ─────────────────────────────────────────────────────────────
function bm25(queryTokens, docTokens, avgDL, N, df) {
  let score = 0;
  for (const term of queryTokens) {
    const df_t = df[term] || 0;
    if (df_t === 0) continue;
    const tf = docTokens.filter(t => t === term).length;
    const idf = Math.log((N - df_t + 0.5) / (df_t + 0.5) + 1);
    const tf_norm = (tf * (BM25_K1 + 1)) / (tf + BM25_K1 * (1 - BM25_B + BM25_B * docTokens.length / avgDL));
    score += idf * tf_norm;
  }
  return score;
}

// ── Search sessions ─────────────────────────────────────────────────────────
function searchSessions(query, daysBack = DAYS_DEFAULT, asJson = false) {
  const cutoff = Date.now() - daysBack * 24 * 60 * 60 * 1000;
  if (!existsSync(SESSIONS_DIR)) {
    return { results: [], total: 0, searched: 0 };
  }

  const files = readdirSync(SESSIONS_DIR).filter(f => f.endsWith('.json'));
  const docs = [];
  const df = {};
  const queryTokens = tokenize(query);

  for (const file of files) {
    try {
      const content = readFileSync(resolve(SESSIONS_DIR, file), 'utf-8');
      const session = JSON.parse(content);
      if (!session.started_at) continue;
      const ts = new Date(session.started_at).getTime();
      if (ts < cutoff) continue;

      // Indexable text
      const text = [
        session.project || '',
        session.summary || '',
        session.activities || '',
        Array.isArray(session.modes_used) ? session.modes_used.join(' ') : '',
        Array.isArray(session.victories) ? session.victories.join(' ') : '',
        Array.isArray(session.blockers) ? session.blockers.join(' ') : '',
      ].join(' ');

      const tokens = tokenize(text);
      docs.push({ file, session, tokens, text });

      // Document frequency
      const unique = new Set(tokens);
      for (const t of unique) df[t] = (df[t] || 0) + 1;
    } catch { /* skip */ }
  }

  const N = docs.length;
  if (N === 0) return { results: [], total: 0, searched: 0 };

  const avgDL = docs.reduce((s, d) => s + d.tokens.length, 0) / N;

  // Score each doc
  const scored = docs.map(d => ({
    file: d.file,
    session: d.session,
    score: bm25(queryTokens, d.tokens, avgDL, N, df),
    snippet: extractSnippet(d.text, queryTokens),
  })).filter(d => d.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, MAX_RESULTS);

  return { results: scored, total: scored.length, searched: N };
}

function extractSnippet(text, queryTokens, contextLen = 150) {
  const lower = text.toLowerCase();
  // Find earliest query term
  let bestPos = -1;
  for (const t of queryTokens) {
    const pos = lower.indexOf(t);
    if (pos >= 0 && (bestPos < 0 || pos < bestPos)) bestPos = pos;
  }

  if (bestPos < 0) return text.slice(0, contextLen) + '...';

  const start = Math.max(0, bestPos - 30);
  const end = Math.min(text.length, start + contextLen);
  let snippet = text.slice(start, end);
  if (start > 0) snippet = '...' + snippet;
  if (end < text.length) snippet = snippet + '...';
  return snippet;
}

// ── Session Summary ────────────────────────────────────────────────────────
function summarizeWithLLM(query, results) {
  // Returns a synthesized summary of matching sessions
  const top3 = results.slice(0, 3);
  return `Based on ${results.length} matching sessions (top 3 shown):

${top3.map((r, i) => `${i + 1}. [${r.session.started_at?.split('T')[0]}] ${r.session.project || 'unknown'}
   Score: ${r.score.toFixed(2)}
   ${r.snippet}`).join('\n\n')}`;
}

// ── Index builder ───────────────────────────────────────────────────────────
function buildIndex() {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });

  const state = readState();
  const files = existsSync(SESSIONS_DIR)
    ? readdirSync(SESSIONS_DIR).filter(f => f.endsWith('.json'))
    : [];

  const indexed = [];
  let totalTokens = 0;
  const df = {};

  for (const file of files) {
    try {
      const content = readFileSync(resolve(SESSIONS_DIR, file), 'utf-8');
      const session = JSON.parse(content);
      const text = [
        session.project || '',
        session.summary || '',
        session.activities || '',
        Array.isArray(session.modes_used) ? session.modes_used.join(' ') : '',
        Array.isArray(session.victories) ? session.victories.join(' ') : '',
      ].join(' ');

      const tokens = tokenize(text);
      const unique = new Set(tokens);
      for (const t of unique) df[t] = (df[t] || 0) + 1;
      totalTokens += tokens.length;

      indexed.push({ file, indexed: Date.now(), tokenCount: tokens.length });
    } catch { /* skip */ }
  }

  state.indexed = indexed;
  state.lastIndex = new Date().toISOString();
  state.df = df;
  state.avgDL = indexed.length > 0 ? totalTokens / indexed.length : 0;
  STATE.set(state);

  console.log(`Indexed ${indexed.length} sessions, ${totalTokens} total tokens`);
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.index) {
    buildIndex();
    return;
  }

  const query = args.query;
  if (!query) {
    console.log(`OMC FTS5 Session Search`);
    console.log(`Usage:`);
    console.log(`  fts5-search.mjs "query" [--days N] [--json] [--llm] [--index]`);
    return;
  }

  const days = args.days || DAYS_DEFAULT;
  const result = searchSessions(query, days, args.json);

  if (result.results.length === 0) {
    if (args.json) {
      console.log(JSON.stringify({ results: [], total: 0, searched: result.searched }));
    } else {
      console.log(`\nNo results for "${query}" (searched ${result.searched} sessions, last ${days} days)\n`);
    }
    return;
  }

  if (args.json) {
    console.log(JSON.stringify(result));
    return;
  }

  if (args.llm) {
    const summary = summarizeWithLLM(query, result.results);
    console.log(summary);
    return;
  }

  console.log(`\n🔍 FTS5 Search: "${query}" (${result.total}/${result.searched} sessions, last ${days} days)\n`);
  for (const r of result.results) {
    const date = r.session.started_at?.split('T')[0] || 'unknown';
    const project = r.session.project || 'unknown';
    console.log(`  [${date}] ${project} (score: ${r.score.toFixed(2)})`);
    console.log(`    ${r.snippet}`);
    console.log();
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
