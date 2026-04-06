/**
 * generate-result-md.mjs — Auto-generate Result.md from shared-types/index.ts
 *
 * Scans type exports and generates a typed Markdown table document.
 * Run: node shared-types/generate-result-md.mjs
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(__dirname, 'index.ts');
const OUTPUT = join(__dirname, 'Result.md');

const content = readFileSync(SOURCE, 'utf8');

const lines = [
  '# shared-types — Type Reference',
  '',
  '> Auto-generated — run `node generate-result-md.mjs` to update',
  '',
  '## Exports',
  '',
  '| Name | Type | Fields |',
  '|------|------|--------|',
];

// Parse top-level exports
const exportMatches = content.matchAll(/^export (?:interface|type|enum|const) (\w+)/gm);
for (const m of exportMatches) {
  const name = m[1];
  const start = m.index;
  const nextExport = [...content.slice(start + 1).matchAll(/^export /gm)][0];
  const end = nextExport ? start + 1 + nextExport.index : content.length;
  const block = content.slice(start, end).trim();

  let fields = '';
  if (block.includes('{')) {
    const fieldMatches = block.matchAll(/(\w+)(\??):\s*([^;=\n]+)/g);
    const fieldParts = [];
    for (const fm of fieldMatches) {
      fieldParts.push(`${fm[1]}: ${fm[3].trim()}`);
    }
    if (fieldParts.length) {
      fields = fieldParts.slice(0, 4).join(', ') + (fieldParts.length > 4 ? '...' : '');
    }
  }

  const isInterface = block.startsWith('export interface');
  const kind = isInterface ? 'interface' : 'type';
  lines.push(`| \`${name}\` | ${kind} | ${fields || '(complex)'} |`);
}

lines.push('');
lines.push('---');
lines.push('');
lines.push('## Full Source');
lines.push('');
lines.push('```typescript');
lines.push(content);
lines.push('```');

writeFileSync(OUTPUT, lines.join('\n'), 'utf8');
console.log(`Saved: ${OUTPUT}`);
