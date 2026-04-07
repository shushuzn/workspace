#!/usr/bin/env node
/**
 * shared/run-seed.mjs
 *
 * Scans ideas.md pool, picks the highest-score unshipped seed,
 * executes its approach's first step, then marks it shipped.
 *
 * Usage: node run-seed.mjs [--dry-run] [--limit N]
 */
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', 'knowledge', 'wikipedia', '.omc', 'innovation', 'ideas.md');

const dryRun = process.argv.includes('--dry-run');
const limitIdx = process.argv.indexOf('--limit');
const showLimit = limitIdx !== -1 ? parseInt(process.argv[limitIdx + 1], 10) : 1;

// ── Parse ideas.md ───────────────────────────────────────────────────────────
const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const results = [];

let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const headerMatch = line.match(/^- \[(\d{8})\] seed \[brainstorm\] \[score:(\d+)x(\d+)\] \[f:(\d+)\] \[angle:([^\]]+)\]/);
  if (!headerMatch) { i++; continue; }

  const [, date, benefitS, feasS, feasEntry, angle] = headerMatch;
  const benefit = parseInt(benefitS, 10);
  const feas = parseInt(feasS, 10);
  const score = benefit * feas;

  // Collect continuation lines (indented lines following header)
  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) {
    bodyLines.push(lines[j].replace(/^\s{2}/, ''));
    j++;
  }
  const bodyText = bodyLines.join('\n');

  // Check shipped — tag can be in header line or body; also check for killed
  const shippedMatch = line.match(/\| shipped:(\d{8})/) || bodyText.match(/\| shipped:(\d{8})/);
  const killedMatch = line.match(/killed:(\d{8})/) || bodyText.match(/killed:(\d{8})/);
  const shipped = !!shippedMatch;
  const killed = !!killedMatch;

  // Extract description — try body first, then fall back to header line (no "description:" prefix)
  const descMatch = bodyText.match(/description:\s*(.+?)(?:\s*\| benefit:|$)/s);
  const desc = descMatch ? descMatch[1].trim() : line.replace(/^\s*/, '').split('|')[0].trim();

  // Extract approach (numbered steps)
  const approachMatch = bodyText.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|$)/s);
  const approachText = approachMatch ? approachMatch[1].trim() : '';

  results.push({ date, score, benefit, feas, feasEntry, angle, shipped, killed, desc, approachText, lineIdx: i, bodyLines });

  i = j;
}

const unshipped = results.filter(s => !s.shipped && !s.killed).sort((a, b) => b.score - a.score);

console.log(`\n=== Seed Runner ===`);
console.log(`Total seeds: ${results.length} | Unshipped: ${unshipped.length}`);
console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'}`);
console.log('');

if (unshipped.length === 0) {
  console.log('[OK] No unshipped seeds found.');
  process.exit(0);
}

if (showLimit > 1) {
  console.log(`Top ${showLimit} unshipped seeds:`);
  for (const s of unshipped.slice(0, showLimit)) {
    console.log(`  [score:${s.score}] f:${s.feas} angle:${s.angle} | ${s.desc.slice(0, 60)}`);
  }
  process.exit(0);
}

const top = unshipped[0];
// Default cwd; script resolution may override
let execCwd = join(__DIR, '..');
console.log(`Top seed: score:${top.score} f:${top.feas} angle:${top.angle}`);
console.log(`  ${top.desc}`);
console.log(`  approach: ${top.approachText.slice(0, 80)}...`);

// Extract first numbered step from approach
// Handle both "1. Do X" and "1. Do X；2. Do Y" (semicolon-separated compound steps)
const firstStepMatch = top.approachText.match(/(?:^|\n)\s*(\d+)\.\s+(.+?)(?:\n\s*\d+\.|$)/s);
if (!firstStepMatch) {
  console.error('[ERROR] No numbered step found in approach');
  process.exit(1);
}
const stepNum = firstStepMatch[1];
let firstStep = firstStepMatch[2].replace(/；$/, '').trim();

// If firstStep contains no path separators or shebang, it's a description —
// try to find the script name in description and build the actual command
if (!firstStep.startsWith('python ') && !firstStep.startsWith('node ') && !firstStep.startsWith('npx ') && !firstStep.startsWith('#') && !firstStep.startsWith('/') && !firstStep.match(/^[a-zA-Z]:\\/)) {
  // Extract script name (e.g. "package_videos.py 添加 --all" → "video/package_videos.py")
  const scriptMatch = top.desc.match(/(?:^|\s)([\w-]+\.(?:py|mjs|js|ts|sh))(?:[\s\[]|$)/);
  if (scriptMatch) {
    const scriptName = scriptMatch[1];
    // Map script name → {path, projectRoot}
    const scriptMeta = {
      'package_videos.py': { path: 'video/package_videos.py', project: 'wikipedia' },
      'check_script.py':   { path: 'video/check_script.py',     project: 'wikipedia' },
      'draw_scene.py':      { path: 'video/draw_scene.py',       project: 'wikipedia' },
      'generate_speech.py': { path: 'video/generate_speech.py',   project: 'wikipedia' },
      'make_video.py':      { path: 'video/make_video.py',       project: 'wikipedia' },
      'wiki.mjs':           { path: 'wiki.mjs',                  project: 'wikipedia' },
      'check-deps.mjs':     { path: 'check-deps.mjs',            project: null },
      'video-editors.mjs':  { path: 'video-editors.mjs',         project: null },
      'wiki-indexer.mjs':   { path: 'wiki-indexer.mjs',          project: null },
      'video-quality-check.mjs': { path: 'video-quality-check.mjs', project: null },
    };
    const meta = scriptMeta[scriptName];
    if (meta) {
      const flagsMatch = firstStep.match(/--?[\w-]+/g);
      const flags = flagsMatch ? flagsMatch.join(' ') : '';
      const isPython = scriptName.endsWith('.py');
      firstStep = isPython ? `python ${meta.path} ${flags}` : `node ${meta.path} ${flags}`;
      firstStep = firstStep.trim();
      if (meta.project === 'wikipedia') {
        execCwd = join(__DIR, '..', 'knowledge', 'wikipedia');
      }
    }
  }
}
console.log(`\n[ACTION] ${dryRun ? 'Would execute step ' + stepNum + ': ' : 'Executing step ' + stepNum + ': '}${firstStep}`);

if (dryRun) {
  console.log(`[DRY] Seed "${top.desc.slice(0, 60)}..." validated — would execute: ${firstStep}`);
  process.exit(0);
}

// ── Execute ──────────────────────────────────────────────────────────────────
const { execSync } = await import('child_process');

try {
  execSync(firstStep, {
    cwd: execCwd,
    stdio: 'inherit',
    timeout: 120_000,
  });
} catch (err) {
  console.error(`\n[ERROR] Command failed (exit ${err.status})`);
  console.error(`Seed NOT marked shipped.`);
  process.exit(err.status ?? 1);
}

// ── Mark shipped ─────────────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
const newLines = [...lines];

// Append "| shipped:YYYYMMDD" to the last body line of the seed
const lastBodyIdx = top.lineIdx + top.bodyLines.length;
const lastBodyLine = newLines[lastBodyIdx];
if (lastBodyLine.match(/\| shipped:/)) {
  // Already shipped (race condition check)
  console.log(`\n[SKIP] Seed already shipped.`);
  process.exit(0);
}
newLines[lastBodyIdx] = lastBodyLine.replace(/(\s*)$/, ` | shipped:${today}`);

writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');

console.log(`\n[SHIPPED] ${top.desc.slice(0, 60)}... → shipped:${today}`);
console.log(`=== Run complete ===\n`);
