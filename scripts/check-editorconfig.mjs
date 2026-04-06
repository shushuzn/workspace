/**
 * check-editorconfig.mjs — Validates .editorconfig consistency across 80-PROJECTS/
 * Run: node scripts/check-editorconfig.mjs
 */

import { readFileSync } from 'fs';
import { readdirSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const BASELINE = resolve('D:/OpenClaw/workspace/.editorconfig');

const BASELINE_FIELDS = ['indent_size', 'indent_style', 'charset', 'end_of_line', 'insert_final_newline', 'trim_trailing_whitespace'];

function parseIni(content) {
  const result = {};
  for (const line of content.split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#') || t.startsWith('[')) continue;
    const eq = t.indexOf('=');
    if (eq < 0) continue;
    const key = t.slice(0, eq).trim();
    const val = t.slice(eq + 1).trim();
    result[key] = val;
  }
  return result;
}

function checkProject(dir) {
  const ecPath = join(dir, '.editorconfig');
  try {
    const content = readFileSync(ecPath, 'utf8');
    const parsed = parseIni(content);
    const mismatches = [];
    for (const field of BASELINE_FIELDS) {
      const baselineVal = baseline[field];
      const localVal = parsed[field];
      if (localVal !== undefined && localVal !== '' && localVal !== baselineVal) {
        mismatches.push(`${field}=${localVal} (baseline: ${baselineVal})`);
      }
    }
    return mismatches.length > 0 ? mismatches : null;
  } catch {
    return null;
  }
}

const baseline = parseIni(readFileSync(BASELINE, 'utf8'));
const baselineStr = BASELINE_FIELDS.map(f => `${f}=${baseline[f] || ''}`).join(' | ');

console.log(`\nBaseline (.editorconfig root): ${baselineStr}`);
console.log('-'.repeat(80));

const projects = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const proj of projects) {
  const mismatches = checkProject(proj);
  if (mismatches) {
    const rel = proj.replace(ROOT + '/', '');
    issues.push({ rel, mismatches });
  }
}

if (issues.length === 0) {
  console.log('  All projects match baseline');
} else {
  for (const { rel, mismatches } of issues) {
    console.log(`  ✗ ${rel}: ${mismatches.join(', ')}`);
  }
}
console.log(`\n${projects.length} projects checked, ${issues.length} with custom .editorconfig\n`);
