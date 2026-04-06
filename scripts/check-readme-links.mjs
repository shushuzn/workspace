/**
 * check-readme-links.mjs — Checks README.md for broken relative links
 * Run: node scripts/check-readme-links.mjs
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const LINK_RE = /\[([^\]]+)\]\(([^)]+)\)/g;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const readmePath = join(dir, 'README.md');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const content = readFileSync(readmePath, 'utf8');
    let match;
    while ((match = LINK_RE.exec(content)) !== null) {
      const [full, text, url] = match;
      if (url.startsWith('http') || url.startsWith('mailto') || url.startsWith('#')) continue;
      const absPath = resolve(dir, url);
      if (!existsSync(absPath)) {
        issues.push({ rel, text: text.slice(0, 40), url });
      }
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All README relative links valid\n`);
} else {
  console.log(`\n  Broken README links:`);
  for (const { rel, text, url } of issues) {
    console.log(`  ✗ ${rel}: "${text}" → "${url}"`);
  }
  console.log(`\n  ${issues.length} broken link(s)\n`);
}
