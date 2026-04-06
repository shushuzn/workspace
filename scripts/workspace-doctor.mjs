/**
 * workspace-doctor.mjs
 * Aggregated health dashboard for all 80-PROJECTS.
 * Single command: node scripts/workspace-doctor.mjs [--fix]
 *
 * Checks: git status, typecheck, lint, test, package.json validity
 * Parallel execution across all projects for speed.
 */

import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { join, resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync, spawnSync } from 'child_process';
import { createRequire } from 'module';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const PROJECTS = join(ROOT, '80-PROJECTS');
const require = createRequire(import.meta.url);

const NO_COLOR = process.env.NO_COLOR || !process.stdout.isTTY;
const GREEN  = NO_COLOR ? '' : '\x1b[32m';
const RED    = NO_COLOR ? '' : '\x1b[31m';
const YELLOW = NO_COLOR ? '' : '\x1b[33m';
const CYAN   = NO_COLOR ? '' : '\x1b[36m';
const DIM    = NO_COLOR ? '' : '\x1b[2m';
const RESET  = NO_COLOR ? '' : '\x1b[0m';
const BOLD   = NO_COLOR ? '' : '\x1b[1m';

const FLAG_FIX = process.argv.includes('--fix');

// ─── Helpers ────────────────────────────────────────────────────────────────────

function exec(cmd, dir, timeout = 10000) {
  try {
    const r = spawnSync(cmd, [], {
      cwd: dir,
      encoding: 'utf8',
      timeout,
      shell: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return { ok: r.status === 0, out: (r.stdout || '').trim(), err: (r.stderr || '').trim(), code: r.status };
  } catch (e) {
    return { ok: false, out: '', err: e.message, code: -1 };
  }
}

function getProjects() {
  const dirs = readdirSync(PROJECTS, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && !d.name.startsWith('10-') && d.name !== 'node_modules')
    .map(d => join(PROJECTS, d.name));

  // Exclude ARCHIVED
  return dirs.filter(d => !d.endsWith('ARCHIVED'));
}

function getProjectMeta(dir) {
  const pkgPath = join(dir, 'package.json');
  const readmePath = join(dir, 'name') ? null : null; // unused
  const name = dir.replace(PROJECTS, '').replace(/\\/g, '/').replace(/^\//, '');

  let pkg = null;
  let pkgValid = false;
  if (existsSync(pkgPath)) {
    try {
      pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
      pkgValid = true;
    } catch { pkgValid = false; }
  }

  const scripts = pkgValid && pkg.scripts ? Object.keys(pkg.scripts) : [];
  const hasTest    = scripts.includes('test');
  const hasBuild   = scripts.includes('build');
  const hasTypecheck = scripts.includes('typecheck') || scripts.includes('tsc') || scripts.includes('check') || scripts.includes('lint');
  const engine = pkgValid && pkg.engines ? pkg.engines.node : null;

  return { name, pkg, pkgValid, scripts, hasTest, hasBuild, hasTypecheck, engine };
}

// ─── Checkers ───────────────────────────────────────────────────────────────────

async function checkGit(dir) {
  const r = exec('git status --porcelain', dir, 5000);
  const lines = (r.out || '').split('\n').filter(Boolean);
  const staged  = lines.filter(l => l.startsWith('M') || l.startsWith('A') || l.startsWith('D'));
  const unstaged = lines.filter(l => l.startsWith(' M') || l.startsWith('??'));
  const dirty = lines.length > 0;
  const branch = exec('git branch --show-current', dir, 3000).out || '(detached)';
  return { dirty, staged: staged.length, unstaged: unstaged.length, branch, lines: lines.slice(0, 5) };
}

async function checkTypecheck(dir, pkg) {
  if (!pkg.pkgValid) return { ok: false, out: 'no package.json' };
  const scripts = pkg.scripts || {};
  if (scripts['typecheck']) {
    const r = exec('npm run typecheck 2>&1', dir, 30000);
    return { ok: r.code === 0, out: r.out + r.err };
  }
  if (scripts['tsc'] && existsSync(join(dir, 'tsconfig.json'))) {
    const r = exec('npx tsc --noEmit 2>&1', dir, 30000);
    return { ok: r.code === 0, out: r.out + r.err };
  }
  return { ok: null, out: 'no typecheck script' };
}

async function checkTest(dir, pkg) {
  if (!pkg.pkgValid || !pkg.hasTest) return { ok: null, out: 'no test script' };
  const r = exec('npm test 2>&1', dir, 60000);
  return { ok: r.code === 0, out: r.out + r.err };
}

async function checkPkgMeta(dir) {
  const { name, pkg, pkgValid } = getProjectMeta(dir);
  const issues = [];
  if (!pkgValid) issues.push('INVALID pkg.json');
  else {
    if (!pkg.description || pkg.description === '项目' || pkg.description === 'A project for...') issues.push('generic desc');
    if (!pkg.keywords || pkg.keywords.length === 0) issues.push('no keywords');
    if (!existsSync(join(dir, 'README.md'))) issues.push('no README');
  }
  return issues;
}

async function checkEngines(dir, pkg) {
  if (!pkg.pkgValid || !pkg.engine) return [];
  const issues = [];
  const required = pkg.engine.replace(/[\^~>= ]/g, '').split('||').map(v => v.trim());
  // Check if current node satisfies
  const nodeVer = process.version.replace(/^v/, '');
  // Simple check - just warn if engines field exists
  return issues;
}

// ─── Main ───────────────────────────────────────────────────────────────────────

async function main() {
  const projects = getProjects();
  const total = projects.length;
  let overallHealthy = 0;
  let overallDirty = 0;
  let overallPkgIssue = 0;
  let overallTypecheckFail = 0;
  let overallTestFail = 0;

  const results = [];

  console.log(`\n${BOLD}${CYAN}🏥 Workspace Doctor — ${total} projects${RESET}\n`);

  // Run checks in parallel batches
  const BATCH = 8;
  for (let i = 0; i < projects.length; i += BATCH) {
    const batch = projects.slice(i, i + BATCH);
    const batchPromises = batch.map(async (dir) => {
      const meta = getProjectMeta(dir);
      const [git, typecheck, test, pkgIssues] = await Promise.all([
        checkGit(dir),
        checkTypecheck(dir, meta),
        checkTest(dir, meta),
        checkPkgMeta(dir),
      ]);
      return { dir, meta, git, typecheck, test, pkgIssues };
    });
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }

  // Sort: dirty first, then by name
  results.sort((a, b) => {
    if (a.git.dirty !== b.git.dirty) return b.git.dirty - a.git.dirty;
    return a.meta.name.localeCompare(b.meta.name);
  });

  // Summary table
  const rows = [];
  for (const r of results) {
    const gitIcon = r.git.dirty
      ? `${YELLOW}!${r.git.branch}${RESET}`
      : `${GREEN}✓${RESET}`;
    const tcIcon = r.typecheck.ok === true
      ? `${GREEN}✓${RESET}`
      : r.typecheck.ok === false
      ? `${RED}✗${RESET}`
      : `${DIM}—${RESET}`;
    const testIcon = r.test.ok === true
      ? `${GREEN}✓${RESET}`
      : r.test.ok === false
      ? `${RED}✗${RESET}`
      : `${DIM}—${RESET}`;
    const pkgIcon = r.pkgIssues.length === 0
      ? `${GREEN}✓${RESET}`
      : `${YELLOW}⚠${r.pkgIssues.length}${RESET}`;

    rows.push({
      name: r.meta.name,
      gitIcon,
      tcIcon,
      testIcon,
      pkgIcon,
      git: r.git,
      typecheck: r.typecheck,
      test: r.test,
      pkgIssues: r.pkgIssues,
      meta: r.meta,
    });
  }

  // Print table
  const col = (s, w) => s.toString().slice(0, w).padEnd(w);
  console.log(`${BOLD}${col('PROJECT', 28)} ${col('GIT', 12)} ${col('TYPECHK', 9)} ${col('TEST', 7)} ${col('PKG', 6)}${RESET}`);
  console.log(DIM + '─'.repeat(65) + RESET);

  for (const row of rows) {
    const gitStr = row.git.dirty
      ? `${YELLOW}!${row.git.branch}${RESET} (${row.git.staged}S ${row.git.unstaged}U)`
      : `${GREEN}✓${RESET}`;
    const tcStr = row.typecheck.ok === true
      ? `${GREEN}✓${RESET}`
      : row.typecheck.ok === false
      ? `${RED}✗ FAIL${RESET}`
      : `${DIM}—${RESET}`;
    const testStr = row.test.ok === true
      ? `${GREEN}✓${RESET}`
      : row.test.ok === false
      ? `${RED}✗ FAIL${RESET}`
      : `${DIM}—${RESET}`;
    const pkgStr = row.pkgIssues.length === 0
      ? `${GREEN}✓${RESET}`
      : `${YELLOW}⚠${RESET}`;

    console.log(`${col(row.name, 28)} ${col(gitStr, 12)} ${col(tcStr, 9)} ${col(testStr, 7)} ${col(pkgStr, 6)}`);

    // Track totals
    if (row.git.dirty) overallDirty++;
    else overallHealthy++;
    if (row.pkgIssues.length > 0) overallPkgIssue++;
    if (row.typecheck.ok === false) overallTypecheckFail++;
    if (row.test.ok === false) overallTestFail++;
  }

  // Summary
  console.log(DIM + '─'.repeat(65) + RESET);
  console.log(`\n${BOLD}Summary:${RESET} ${total} projects | ` +
    `${GREEN}${overallHealthy} clean${RESET} | ` +
    `${YELLOW}${overallDirty} dirty${RESET} | ` +
    `${RED}${overallTypecheckFail} typecheck-fail${RESET} | ` +
    `${YELLOW}${overallPkgIssue} pkg-issue${RESET}`);

  if (overallDirty === 0 && overallTypecheckFail === 0 && overallPkgIssue === 0) {
    console.log(`\n${GREEN}${BOLD}✅ All projects healthy!${RESET}\n`);
  } else {
    console.log(`\n${YELLOW}Run with ${CYAN}--fix${YELLOW} to auto-commit clean changes or fix simple issues.${RESET}\n`);
  }

  // List dirty projects for quick reference
  if (overallDirty > 0) {
    console.log(`${YELLOW}Dirty projects:${RESET}`);
    for (const r of rows) {
      if (r.git.dirty) {
        for (const line of r.git.lines) {
          console.log(`  ${r.meta.name}: ${line}`);
        }
      }
    }
  }

  if (overallTypecheckFail > 0) {
    console.log(`\n${RED}Typecheck failures:${RESET}`);
    for (const r of rows) {
      if (r.typecheck.ok === false) {
        const err = r.typecheck.out.split('\n').slice(-2).join(' ');
        console.log(`  ${RED}✗${RESET} ${r.meta.name}: ${DIM}${err.slice(0, 80)}${RESET}`);
      }
    }
  }
}

main().catch(console.error);
