#!/usr/bin/env node
/**
 * Paper comparison view generator
 * Compares two papers side-by-side
 * Usage: node shared/paper-compare.mjs <paper1.md> <paper2.md>
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));

function extractFrontmatter(content) {
  const fm = content.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) return { title: 'Untitled', authors: '', abstract: '', body: content };
  const lines = fm[1].split('\n');
  const data = {};
  for (const l of lines) {
    const [k, ...v] = l.split(':');
    if (k && v.length) data[k.trim()] = v.join(':').trim();
  }
  return { ...data, body: content.replace(/^---\n[\s\S]*?\n---/, '') };
}

function generateHtml(p1, p2) {
  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Paper Comparison</title>
<style>
body { font-family: system-ui; margin: 2rem; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.card { border: 1px solid #ddd; padding: 1rem; border-radius: 8px; }
h2 { margin-top: 0; }
.meta { color: #666; font-size: 0.9em; }
.abstract { background: #f9f9f9; padding: 1rem; border-radius: 4px; }
</style></head><body>
<h1>Paper Comparison</h1>
<div class="grid">
<div class="card">
<h2>${p1.title || 'Untitled'}</h2>
<div class="meta">${p1.authors || ''}</div>
<div class="abstract"><strong>Abstract:</strong><br>${p1.abstract || 'No abstract'}</div>
<div class="body">${p1.body || ''}</div>
</div>
<div class="card">
<h2>${p2.title || 'Untitled'}</h2>
<div class="meta">${p2.authors || ''}</div>
<div class="abstract"><strong>Abstract:</strong><br>${p2.abstract || 'No abstract'}</div>
<div class="body">${p2.body || ''}</div>
</div>
</div></body></html>`;
}

const [f1, f2] = process.argv.slice(2);
if (!f1 || !f2) {
  console.error('Usage: node paper-compare.mjs <paper1.md> <paper2.md>');
  process.exit(1);
}

if (!existsSync(f1) || !existsSync(f2)) {
  console.error('Files not found');
  process.exit(1);
}

const p1 = extractFrontmatter(readFileSync(f1, 'utf8'));
const p2 = extractFrontmatter(readFileSync(f2, 'utf8'));
console.log(generateHtml(p1, p2));
