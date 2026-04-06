/**
 * dependency-health-score.mjs — Computes dependency health score per project
 * Run: node scripts/dependency-health-score.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';
import { execSync } from 'child_process';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

console.log('\n  Dependency Health Scores:\n');

const results = [];
for (const dir of dirs) {
  const name = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const pkgPath = join(dir, 'package.json');

  let outdated = 0, auditCritical = 0, auditHigh = 0, missingEngines = false;
  try {
    try {
      const out = execSync('npm outdated --json --depth=0 2>nul', { cwd: dir, encoding: 'utf8', timeout: 30000 });
      const parsed = JSON.parse(out);
      outdated = Object.keys(parsed).length;
    } catch {}
    try {
      const out = execSync('npm audit --json 2>nul', { cwd: dir, encoding: 'utf8', timeout: 30000 });
      const parsed = JSON.parse(out);
      auditCritical = parsed.metadata?.vulnerabilities?.critical || 0;
      auditHigh = parsed.metadata?.vulnerabilities?.high || 0;
    } catch {}
    try {
      const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
      missingEngines = !pkg.engines?.node;
    } catch {}
  } catch {}

  let score = 100;
  score -= outdated * 3;
  score -= auditCritical * 10;
  score -= auditHigh * 5;
  if (missingEngines) score -= 10;
  score = Math.max(0, Math.min(100, score));

  const grade = score >= 80 ? 'A' : score >= 60 ? 'B' : score >= 40 ? 'C' : score >= 20 ? 'D' : 'F';
  console.log(`    [${grade}] ${String(score).padStart(3)}  outdated=${outdated} critical=${auditCritical} high=${auditHigh}  ${name}`);
  results.push({ name, score });
}

results.sort((a, b) => b.score - a.score);
console.log(`\n  Worst: ${results[results.length - 1]?.name} (${results[results.length - 1]?.score})`);
console.log(`  Best:  ${results[0]?.name} (${results[0]?.score})\n`);
