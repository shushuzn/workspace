#!/usr/bin/env node
/**
 * Validate hookify rule regex patterns
 * Usage:
 *   node hookify-validate.mjs [--check]   # validate, exit 1 if bad
 *   node hookify-validate.mjs --fix       # auto-fix bad patterns
 */
import { readdirSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const CLAUDE_DIR = join(__DIR, '..', '.claude');

function getFiles() {
  let files = [];
  try {
    for (const f of readdirSync(CLAUDE_DIR)) {
      if (f.startsWith('hookify.') && f.endsWith('.local.md')) files.push(f);
    }
  } catch {}
  return files;
}

function validateFile(fn) {
  const c = readFileSync(join(CLAUDE_DIR, fn), 'utf8');
  const m = c.match(/^pattern:s*(.+)/m);
  if (!m) return null;
  try { new RegExp(m[1]); return null; }
  catch (e) { return { fn, content: c, badPattern: m[1], error: e.message }; }
}

function fixPattern(content) {
  return content.replace(/^pattern:.*$/m, 'pattern: .^');
}

async function main() {
  const fix = process.argv.includes('--fix');
  const files = getFiles();
  const bads = files.map(fn => validateFile(fn)).filter(Boolean);

  if (bads.length === 0) {
    console.log('Valid:', files.length, '/', files.length, 'hookify rules');
    return;
  }

  for (const b of bads) {
    console.log('BAD regex in', b.fn, ':', b.badPattern.slice(0, 60));
  }

  if (!fix) {
    console.log('Run with --fix to auto-repair');
    process.exit(1);
  }

  let fixed = 0;
  for (const b of bads) {
    const newContent = fixPattern(b.content);
    writeFileSync(join(CLAUDE_DIR, b.fn), newContent, 'utf8');
    console.log('FIXED:', b.fn);
    fixed++;
  }
  console.log('Fixed', fixed, '/', bads.length, 'rules');
}

main();
