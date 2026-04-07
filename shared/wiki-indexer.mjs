#!/usr/bin/env node
/**
 * shared/wiki-indexer.mjs
 * 扫描 workspace 下所有项目的 README.md，建立统一搜索索引
 * 用法：
 *   node shared/wiki-indexer.mjs --rebuild   # 强制重建索引
 *   node shared/wiki-indexer.mjs --search <query>  # 搜索
 */
import { readFileSync, readdirSync, existsSync, writeFileSync } from 'fs';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__DIR, '..');
const INDEX_FILE = join(__DIR, 'wiki-index.json');

function getAllReadmes(dir, depth = 2) {
  const results = [];
  if (depth < 0) return results;
  try {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist') continue;
        results.push(...getAllReadmes(join(dir, entry.name), depth - 1));
      } else if (entry.name === 'README.md') {
        results.push(join(dir, entry.name));
      }
    }
  } catch { /* skip inaccessible dirs */ }
  return results;
}

function extractInfo(readmePath) {
  try {
    const content = readFileSync(readmePath, 'utf-8').trim();
    const lines = content.split('\n');
    let title = basename(dirname(readmePath));
    let description = '';
    for (const line of lines.slice(1, 10)) {
      const stripped = line.replace(/^#+\s*/, '').trim();
      if (stripped && !stripped.startsWith('[') && stripped.length > 20) {
        description = stripped.slice(0, 120);
        break;
      }
    }
    const rel = readmePath.replace(ROOT + '\\', '').replace(ROOT + '/', '');
    return { path: rel, title, description };
  } catch {
    return null;
  }
}

function buildIndex() {
  console.log('[wiki-indexer] Scanning workspace for README.md files...');
  const readmes = getAllReadmes(ROOT);
  const entries = [];
  for (const rm of readmes) {
    const info = extractInfo(rm);
    if (info) entries.push(info);
  }
  const index = { built: new Date().toISOString(), count: entries.length, entries };
  writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2));
  console.log(`[wiki-indexer] Indexed ${entries.length} projects`);
  return index;
}

function fuzzyMatch(text, query) {
  const t = text.toLowerCase(), q = query.toLowerCase();
  // Prefix match: query at start of text (weight ×2)
  if (t.startsWith(q)) return 2 * q.length / t.length;
  // Word boundary match: query as complete word (weight ×1.5)
  const wordBoundaries = t.match(new RegExp(`\\b${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i'));
  if (wordBoundaries) return 1.5 * q.length / t.length;
  // Substring match
  if (t.includes(q)) return q.length / t.length;
  // Character overlap (original logic)
  let qi = 0, score = 0;
  for (let ci = 0; ci < t.length && qi < q.length; ci++) {
    if (t[ci] === q[qi]) { score += 1; qi++; }
  }
  return qi === q.length ? score / q.length : 0;
}

function searchIndex(query, opts = {}) {
  if (!existsSync(INDEX_FILE)) {
    console.error('[wiki-indexer] No index. Run --rebuild first.'); process.exit(1);
  }
  const idx = JSON.parse(readFileSync(INDEX_FILE, 'utf-8'));
  const limit = opts.limit || 10;
  let results;
  if (opts.fuzzy) {
    results = idx.entries
      .map(e => ({ ...e, _score: Math.max(fuzzyMatch(e.title, query), fuzzyMatch(e.description, query), fuzzyMatch(e.path, query)) }))
      .filter(e => e._score > 0)
      .sort((a, b) => b._score - a._score)
      .slice(0, limit);
  } else {
    const q = query.toLowerCase();
    results = idx.entries.filter(e =>
      e.title.toLowerCase().includes(q) ||
      e.description.toLowerCase().includes(q) ||
      e.path.toLowerCase().includes(q)
    ).slice(0, limit);
  }
  if (opts.json) {
    console.log(JSON.stringify(results.map(({_score, ...r}) => r)));
    return;
  }
  if (!results.length) { console.log('No results.'); return; }
  for (const r of results) {
    console.log(`  [${r.path}]`);
    console.log(`    ${r.title}`);
    if (r.description) console.log(`    ${r.description}`);
  }
  console.log(`\nTotal: ${results.length} / ${idx.count}`);
}

const args = process.argv.slice(2);
const get = (flag, short) => { const i = args.indexOf(flag); return i !== -1 ? args[i + 1] : short ? args.indexOf(short) !== -1 ? true : undefined : undefined; };
if (args.includes('--rebuild') || args.includes('-r')) {
  buildIndex();
} else if (args.includes('--search') || args.includes('-s')) {
  const q = get('--search') || get('-s', true);
  if (!q || q === true) { console.log('Usage: node wiki-indexer.mjs --search <query>'); process.exit(1); }
  searchIndex(q);
} else if (args.includes('--query')) {
  const q = get('--query');
  const limit = parseInt(get('--limit') || '10', 10);
  const json = args.includes('--json');
  if (!q || q === true) { console.log('Usage: node wiki-indexer.mjs --query <term> [--limit N] [--json] [--fuzzy]'); process.exit(1); }
  searchIndex(q, { json, limit, fuzzy: args.includes('--fuzzy') });
} else {
  console.log('Usage:');
  console.log('  node shared/wiki-indexer.mjs --rebuild   # Build/update index');
  console.log('  node shared/wiki-indexer.mjs --search <query>  # Human-readable search');
  console.log('  node shared/wiki-indexer.mjs --query <term> [--limit N] [--json] [--fuzzy]  # JSON search (for scripts)');
}
