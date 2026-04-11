#!/usr/bin/env node
/**
 * scripts/detect-affected-suites.mjs
 * Detects which test suites are affected by the current changes.
 *
 * Usage:
 *   node scripts/detect-affected-suites.mjs [base_sha]
 *
 * Outputs:
 *   - GITHUB_OUTPUT style: suites=<comma-separated-suites>
 *   - Sets exit code: 0 if suites found, 1 if all/no suites
 *
 * Suite → File mapping:
 *   step-parser  → shared/step-parser.mjs, shared/step-parser.test.mjs
 *   run-seed     → shared/run-seed.mjs, shared/run-seed.test.mjs
 *   add-seed     → shared/add-seed.mjs, shared/add-seed.test.mjs
 */
import { spawn } from 'child_process';
import { stdout } from 'process';

const GH = process.platform === 'win32' ? 'gh.cmd' : 'gh';
const BASE = process.argv[2] || 'HEAD~1';
const REPO = process.env.GITHUB_REPOSITORY || 'shushuzn/workspace';

// ── Suite → files mapping ─────────────────────────────────────────────────────
const SUITE_FILES = {
  'step-parser': ['shared/step-parser.mjs', 'shared/step-parser.test.mjs'],
  'run-seed':    ['shared/run-seed.mjs', 'shared/run-seed.test.mjs'],
  'add-seed':    ['shared/add-seed.mjs', 'shared/add-seed.test.mjs']
};

const ALL_SUITES = Object.keys(SUITE_FILES);
const SUITE_FILES_FLAT = ALL_SUITES.flatMap(s => SUITE_FILES[s]);

// ── Git diff ─────────────────────────────────────────────────────────────────
function git(args) {
  return new Promise((resolve, reject) => {
    const p = spawn('git', args, { shell: true });
    let out = '';
    p.stdout.on('data', d => out += d.toString());
    p.on('close', code => resolve({ code, out }));
    p.on('error', reject);
  });
}

async function getChangedFiles(base) {
  const { out } = await git(['diff', '--name-only', base, 'HEAD']);
  return out.trim().split('\n').filter(Boolean);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const changed = await getChangedFiles(BASE);
  const changedSet = new Set(changed);

  console.error(`Changed files (${changed.length}):`);
  for (const f of changed) console.error(`  ${f}`);

  // Find affected suites
  const affected = ALL_SUITES.filter(suite =>
    SUITE_FILES[suite].some(f => changedSet.has(f))
  );

  console.error(`\nAffected suites: ${affected.length > 0 ? affected.join(', ') : '(none)'}`);

  // Also check workflow files → all suites
  const workflowChanged = changed.some(f => f.includes('.github/workflows') || f.includes('tests.yml'));
  const allSuites = workflowChanged ? ALL_SUITES.join(',') : (affected.length > 0 ? affected.join(',') : '');

  // Output for GitHub Actions (modern GITHUB_OUTPUT)
  process.stdout.write(`suites=${allSuites}\n`);

  console.error(`\nFinal suites output: ${allSuites || '(empty — no tests will run)'}`);

  // Exit code: 0 if suites found, 1 if all or none
  process.exit(affected.length === 0 || affected.length === ALL_SUITES.length ? 1 : 0);
}

main().catch(e => {
  console.error(e);
  // On error, output all suites as fallback
  process.stdout.write(`suites=${ALL_SUITES.join(',')}\n`);
  process.exit(0);
});
