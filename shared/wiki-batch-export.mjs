#!/usr/bin/env node
/**
 * wiki-batch-export.mjs
 * Export wikipedia articles to multiple formats (HTML/MD/JSON)
 * Usage: node shared/wiki-batch-export.mjs --format=html --output=wiki-export/
 */
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'fs';
import { join, dirname, extname, resolve, isAbsolute } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const WIKI_DIR = join(__DIR, '..', 'knowledge', 'wikipedia', 'articles');

const formatIdx = process.argv.indexOf('--format');
const format = formatIdx !== -1 ? process.argv[formatIdx + 1] : 'html';
const outputIdx = process.argv.indexOf('--output');
let OUTPUT_DIR = outputIdx !== -1 && outputIdx + 1 < process.argv.length
  ? process.argv[outputIdx + 1]
  : join(__DIR, '..', 'wiki-export');

// Resolve to absolute path to handle Windows drive letters properly
if (!isAbsolute(OUTPUT_DIR)) {
  OUTPUT_DIR = resolve(OUTPUT_DIR);
}

if (!['html', 'md', 'json'].includes(format)) {
  console.error('Usage: node wiki-batch-export.mjs --format=html|md|json --output=DIR');
  process.exit(1);
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function mdToHtml(md) {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, '<a href="$1">$2</a>')
    .replace(/\[\[([^\]]+)\]\]/g, '<a href="$1">$1</a>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
}

function collectArticles(dir) {
  const articles = [];
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      articles.push(...collectArticles(full));
    } else if (entry.name.endsWith('.md')) {
      articles.push(full);
    }
  }
  return articles;
}

if (!existsSync(WIKI_DIR)) {
  console.error('[wiki-batch-export] articles directory not found:', WIKI_DIR);
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
const articles = collectArticles(WIKI_DIR);
console.log(`[wiki-batch-export] Exporting ${articles.length} articles to ${format}...`);

// Normalize WIKI_DIR for comparison (handle both / and \)
const normWikiDir = WIKI_DIR.replace(/\\/g, '/');

let exported = 0;
for (const articlePath of articles) {
  // Get relative path from WIKI_DIR
  const normPath = articlePath.replace(/\\/g, '/');
  const rel = normPath.startsWith(normWikiDir + '/')
    ? normPath.slice(normWikiDir.length + 1)
    : normPath;
  // Strip .md and use safe filename
  const name = rel.replace(/\.md$/, '').replace(/\//g, '-');
  const content = readFileSync(articlePath, 'utf8');

  let outputContent, outputExt;
  if (format === 'json') {
    outputContent = JSON.stringify({ name: rel.replace(/\.md$/, ''), content }, null, 2);
    outputExt = '.json';
  } else if (format === 'md') {
    outputContent = content;
    outputExt = '.md';
  } else {
    const htmlContent = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${escapeHtml(name)}</title></head>
<body><h1>${escapeHtml(name)}</h1><p>${mdToHtml(content)}</p></body></html>`;
    outputContent = htmlContent;
    outputExt = '.html';
  }

  const outPath = join(OUTPUT_DIR, name + outputExt);
  writeFileSync(outPath, outputContent, 'utf8');
  exported++;
}

console.log(`[wiki-batch-export] Done: ${exported} articles exported to ${OUTPUT_DIR}`);
process.exit(0);
