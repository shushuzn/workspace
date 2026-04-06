/**
 * scripts/health-check.mjs — Svelte 5 API health & breaking change detector
 * Run: node scripts/health-check.mjs [--verbose]
 */
import { readdirSync, readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = __dirname;
const SRC = join(ROOT, 'src');

const JSON_MODE = process.argv.includes('--json');
const VERBOSE = process.argv.includes('--verbose');

// Known Svelte 5 deprecated/breaking API patterns
const SVELTE5_BREAKING = [
  { pattern: /on:(\w+)/, severity: 'error', msg: 'on:event directive — Svelte 5 uses onclick={handler} instead' },
  { pattern: /export\s+let\s+(\w+)/, severity: 'warn', msg: 'export let — Svelte 5 uses $props() instead' },
  { pattern: /\$:/, severity: 'warn', msg: 'Svelte 4 store reactive — Svelte 5 uses $state/$derived instead' },
  { pattern: /await\s+then/, severity: 'warn', msg: 'await then block — Svelte 5 uses {#await} differently' },
  { pattern: /createEventDispatcher/, severity: 'error', msg: 'createEventDispatcher — Svelte 5 uses callback props instead' },
  { pattern: /\.destroy\(\)/, severity: 'warn', msg: '.destroy() — Svelte 5 uses onDestroy lifecycle differently' },
  { pattern: /<svelte:component\s+this=/, severity: 'warn', msg: 'svelte:component this={} — Svelte 5 uses snippets instead' },
  { pattern: /:\s*export\s+const/, severity: 'warn', msg: 'const: export — Svelte 5 uses runes differently' },
  { pattern: /\$store\b/, severity: 'warn', msg: '$store shorthand — Svelte 5 prefers $state/$derived' },
  { pattern: /use:action\s*=\s*\{/, severity: 'warn', msg: 'use:action with object — Svelte 5 action API may differ' },
];

// Svelte 5 preferred runes
const SVELTE5_PREFERRED = [
  { pattern: /\$state\(/, msg: '$state() rune found — good' },
  { pattern: /\$derived\(/, msg: '$derived() rune found — good' },
  { pattern: /\$effect\(/, msg: '$effect() rune found — good' },
  { pattern: /\$props\(/, msg: '$props() rune found — good' },
  { pattern: /\{#snippet\b/, msg: 'snippet directive found — good' },
  { pattern: /\{#render\b/, msg: 'render directive found — good' },
];

function findFiles(dir, ext) {
  const results = [];
  if (!existsSync(dir)) return results;
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory() && entry.name !== 'node_modules') {
      results.push(...findFiles(full, ext));
    } else if (entry.name.endsWith(ext)) {
      results.push(full);
    }
  }
  return results;
}

const svelteFiles = findFiles(SRC, '.svelte');
const jsFiles = findFiles(SRC, '.js').filter(f => !f.includes('node_modules'));
const tsFiles = findFiles(SRC, '.ts').filter(f => !f.includes('node_modules'));

const results = { errors: [], warnings: [], preferred: [] };

for (const file of [...svelteFiles, ...jsFiles, ...tsFiles]) {
  const content = readFileSync(file, 'utf8');
  const rel = file.replace(ROOT, '').replace(/\\/g, '/');

  for (const rule of SVELTE5_BREAKING) {
    const matches = content.match(new RegExp(rule.pattern, 'g'));
    if (matches) {
      const entry = { file: rel, severity: rule.severity, msg: rule.msg, count: matches.length };
      if (rule.severity === 'error') results.errors.push(entry);
      else results.warnings.push(entry);
      if (VERBOSE) console.error(`  [${rule.severity}] ${rel}: ${rule.msg} (${matches.length}x)`);
    }
  }

  for (const rule of SVELTE5_PREFERRED) {
    if (rule.pattern.test(content)) {
      const entry = { file: rel, msg: rule.msg };
      results.preferred.push(entry);
    }
  }
}

const uniqueErrors = [...new Map(results.errors.map(e => [e.msg + e.file, e])).values()];
const uniqueWarnings = [...new Map(results.warnings.map(e => [e.msg + e.file, e])).values()];

if (JSON_MODE) {
  console.log(JSON.stringify({ errors: uniqueErrors, warnings: uniqueWarnings, preferred: results.preferred, summary: { error_count: uniqueErrors.length, warning_count: uniqueWarnings.length, preferred_count: results.preferred.length } }, null, 2));
} else {
  console.log(`\n  ── Svelte 5 Health Check ──`);
  console.log(`  Svelte files:  ${svelteFiles.length}`);
  console.log(`  JS/TS files:   ${jsFiles.length + tsFiles.length}`);
  if (uniqueErrors.length > 0) {
    console.log(`\n  ❌ Breaking/Error issues (${uniqueErrors.length}):`);
    for (const e of uniqueErrors) console.log(`    ${e.file}: ${e.msg}`);
  } else {
    console.log(`\n  ✅ No breaking issues found`);
  }
  if (uniqueWarnings.length > 0) {
    console.log(`\n  ⚠️  Warnings (${uniqueWarnings.length}):`);
    for (const w of uniqueWarnings) console.log(`    ${w.file}: ${w.msg}`);
  }
  if (results.preferred.length > 0) {
    console.log(`\n  👍 Svelte 5 runes usage (${results.preferred.length} files):`);
    for (const p of [...new Map(results.preferred.map(p => [p.file, p])).values()].slice(0, 5)) {
      console.log(`    ${p.file}: ${p.msg}`);
    }
    if (results.preferred.length > 5) console.log(`    ... and ${results.preferred.length - 5} more`);
  }
  console.log('');
}
