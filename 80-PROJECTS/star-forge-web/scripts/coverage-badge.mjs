/**
 * scripts/coverage-badge.mjs — Generate SVG coverage badge + update README
 * Run: node scripts/coverage-badge.mjs [--dry-run]
 *
 * Runs vitest coverage, parses coverage-final.json for %, generates SVG badge,
 * optionally updates README with the badge.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const IS_DRY = process.argv.includes('--dry-run');
const README_PATH = join(ROOT, 'README.md');

function runCoverage() {
  execSync('npx vitest run --coverage', {
    cwd: ROOT,
    encoding: 'utf8',
    maxBuffer: 100 * 1024 * 1024,
  });
  // Parse coverage/coverage-final.json — format: { "file.js": { s: {}, fnMap: {}, branchMap: {} } }
  const data = JSON.parse(readFileSync(join(ROOT, 'coverage/coverage-final.json'), 'utf8'));
  const files = Object.values(data);
  if (!files.length) return { lines: 0, statements: 0, functions: 0, branches: 0 };
  const f = files[0];
  const sKeys = Object.keys(f.s || {});
  const sVals = Object.values(f.s || {});
  const sCovered = sVals.filter(v => v > 0).length;
  const stmts = sVals.length ? Math.round((sCovered / sVals.length) * 1000) / 10 : 0;
  const fVals = Object.values(f.fnMap || {});
  const fCovered = fVals.filter(v => v.exec > 0).length;
  const funcs = fVals.length ? Math.round((fCovered / fVals.length) * 1000) / 10 : 0;
  const bChildKeys = Object.values(f.b || {}).flat();
  const bCovered = bChildKeys.filter(v => v > 0).length;
  const branches = bChildKeys.length ? Math.round((bCovered / bChildKeys.length) * 1000) / 10 : 0;
  return { lines: stmts, statements: stmts, functions: funcs, branches };
}

function pct(n) {
  return typeof n === 'number' ? n : 0;
}

function badgeColor(pct) {
  if (pct >= 90) return '#4caf50';
  if (pct >= 70) return '#ff9800';
  return '#f44336';
}

function badgeSVG({ lines, statements, functions, branches }) {
  const p = [lines, statements, functions, branches].map(pct);
  const svgColor = badgeColor(p[0]);
  const label = `Lines: ${p[0]}% | Stmts: ${p[1]}% | Funcs: ${p[2]}% | Branch: ${p[3]}%`;
  const W = Math.max(420, label.length * 7 + 40);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="24" viewBox="0 0 ${W} 24">
  <rect width="${W}" height="24" rx="4" fill="${svgColor}"/>
  <text x="12" y="17" font-family="monospace" font-size="11" fill="white" font-weight="bold">${label}</text>
</svg>`;
}

function updateReadme(readmePath, svg) {
  if (!existsSync(readmePath)) return;
  let readme = readFileSync(readmePath, 'utf8');
  const open = '<!-- COVERAGE_BADGE -->';
  const close = '<!-- /COVERAGE_BADGE -->';
  const block = `${open}\n${svg}\n${close}`;
  if (readme.includes(open)) {
    readme = readme.replace(new RegExp(`${open}[\\s\\S]*?${close}`), block);
  } else {
    readme = readme.replace(/^(# .+)$/m, `$1\n\n${block}`);
  }
  return readme;
}

const cov = runCoverage();
const svg = badgeSVG(cov);

const badgePath = join(ROOT, 'coverage-badge.svg');
if (!IS_DRY) {
  writeFileSync(badgePath, svg, 'utf8');
  console.log(`Badge → ${badgePath}`);
}

const updated = updateReadme(README_PATH, svg);
if (updated && !IS_DRY) {
  writeFileSync(README_PATH, updated, 'utf8');
  console.log(`README updated → ${README_PATH}`);
}

console.log(`\n  ── star-forge Coverage ──`);
console.log(`  Lines:  ${pct(cov.lines)}%`);
console.log(`  Stmts:  ${pct(cov.statements)}%`);
console.log(`  Funcs:  ${pct(cov.functions)}%`);
console.log(`  Branch: ${pct(cov.branches)}%`);
