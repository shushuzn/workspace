/**
 * scripts/run-all-tests.mjs — Run test scripts across all 80-PROJECTS
 * Run: node scripts/run-all-tests.mjs [--json]
 *
 * Scans 80-PROJECTS for projects with a "test" script in package.json,
 * executes them concurrently (max 5 at a time), returns {project, pass, fail, duration, error} report.
 */
import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';

const execP = promisify(exec);
const __dirname = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(__dirname, '..', '80-PROJECTS');
const IS_JSON = process.argv.includes('--json');
const CONCURRENCY = 5;

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function runTest(dir, name) {
  const start = Date.now();
  try {
    const { stdout, stderr } = await execP('npm test', {
      cwd: dir,
      timeout: 120000,
      killSignal: 'SIGTERM',
    });
    return {
      project: name,
      pass: true,
      fail: false,
      duration: Date.now() - start,
      error: null,
      stdout: stdout.slice(-500),
    };
  } catch (e) {
    const duration = Date.now() - start;
    // exit code 0 with no test runner = "pass" (some projects have no tests)
    if (e.code === 0 && !e.stdout && !e.stderr) {
      return { project: name, pass: true, fail: false, duration, error: null };
    }
    return {
      project: name,
      pass: false,
      fail: true,
      duration,
      error: e.stderr?.slice(-300) || e.message?.slice(-300) || `exit ${e.code}`,
    };
  }
}

async function main() {
  const dirs = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
    .map(d => ({ path: join(ROOT, d.name), name: d.name }));

  // Find projects with test script
  const testProjects = [];
  for (const { path, name } of dirs) {
    try {
      const pkg = JSON.parse(readFileSync(join(path, 'package.json'), 'utf8'));
      if (pkg.scripts && pkg.scripts.test) {
        testProjects.push({ path, name });
      }
    } catch {
      // no package.json or unreadable
    }
  }

  if (!testProjects.length) {
    const result = { total: 0, pass: 0, fail: 0, projects: [], summary: 'No projects with test script found' };
    console.log(IS_JSON ? JSON.stringify(result, null, 2) : result.summary);
    return;
  }

  // Run concurrently with CONCURRENCY limit
  const results = [];
  for (let i = 0; i < testProjects.length; i += CONCURRENCY) {
    const batch = testProjects.slice(i, i + CONCURRENCY);
    const batchResults = await Promise.all(batch.map(({ path, name }) => runTest(path, name)));
    results.push(...batchResults);
  }

  const total = results.length;
  const pass = results.filter(r => r.pass).length;
  const fail = results.filter(r => r.fail).length;
  const totalDuration = results.reduce((s, r) => s + r.duration, 0);
  const avgDuration = Math.round(totalDuration / total);

  const report = {
    total,
    pass,
    fail,
    passRate: total > 0 ? Math.round(pass / total * 100) : 0,
    totalDuration,
    avgDuration,
    projects: results,
  };

  if (IS_JSON) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(`\n  Workspace Test Summary\n  ─────────────────────`);
    console.log(`  Total:   ${total}`);
    console.log(`  Pass:    ${pass} (${report.passRate}%)`);
    console.log(`  Fail:    ${fail}`);
    console.log(`  Avg:     ${avgDuration}ms\n`);
    for (const r of results) {
      const icon = r.pass ? '✓' : '✗';
      const dur = `${r.duration}ms`.padEnd(8);
      console.log(`  ${icon} ${dur} ${r.project}${r.error ? ` — ${r.error}` : ''}`);
    }
    console.log('');
  }
}

main().catch(e => {
  console.error('run-all-tests error:', e.message);
  process.exit(1);
});
