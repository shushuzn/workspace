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

function searchIndex(query) {
  if (!existsSync(INDEX_FILE)) {
    console.error('[wiki-indexer] No index. Run --rebuild first.'); process.exit(1);
  }
  const idx = JSON.parse(readFileSync(INDEX_FILE, 'utf-8'));
  const q = query.toLowerCase();
  const results = idx.entries.filter(e =>
    e.title.toLowerCase().includes(q) ||
    e.description.toLowerCase().includes(q) ||
    e.path.toLowerCase().includes(q)
  ).slice(0, 10);
  if (!results.length) { console.log('No results.'); return; }
  for (const r of results) {
    console.log(`  [${r.path}]`);
    console.log(`    ${r.title}`);
    if (r.description) console.log(`    ${r.description}`);
  }
  console.log(`\nTotal: ${results.length} / ${idx.count}`);
}

const args = process.argv.slice(2);
if (args.includes('--rebuild') || args.includes('-r')) {
  buildIndex();
} else if (args.includes('--search') || args.includes('-s')) {
  const q = args[args.indexOf('--search') + 1] || args[args.indexOf('-s') + 1];
  if (!q) { console.log('Usage: node wiki-indexer.mjs --search <query>'); process.exit(1); }
  searchIndex(q);
} else {
  console.log('Usage:');
  console.log('  node shared/wiki-indexer.mjs --rebuild   # Build/update index');
  console.log('  node shared/wiki-indexer.mjs --search <query>  # Search');
}
