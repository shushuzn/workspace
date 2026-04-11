#!/usr/bin/env node
/**
 * scripts/ci.mjs
 * CI Command Center — unified entry point for all CI tools.
 *
 * Usage:
 *   node scripts/ci.mjs diagnose [--run-id=<id>|--latest]
 *   node scripts/ci.mjs trend [--suite=<name>]
 *   node scripts/ci.mjs health [--badge|--summary]
 *   node scripts/ci.mjs predict [--alert]
 *   node scripts/ci.mjs regression
 *   node scripts/ci.mjs patterns [confirm|reject <name>] [--notes=<text>]
 *   node scripts/ci.mjs chronicle append <run_id> [key=value ...]
 *   node scripts/ci.mjs chronicle report
 *   node scripts/ci.mjs autobaseline [--update]
 *   node scripts/ci.mjs all          # run full suite
 *   node scripts/ci.mjs help
 */
import { spawn } from 'child_process';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_DIR = join(__dirname);

const GH = process.platform === 'win32' ? 'gh.cmd' : 'gh';
const REPO = process.env.GITHUB_REPOSITORY || 'shushuzn/workspace';

const COMMANDS = {
  diagnose:     { script: 'ci-diagnose.mjs',           args: (a) => [] },
  trend:        { script: 'coverage-trend.mjs',          args: (a) => ['--report'] },
  health:       { script: 'ci-health.mjs',               args: (a) => a.includes('--badge') ? ['--badge'] : a.includes('--summary') ? ['--summary'] : [] },
  predict:      { script: 'ci-fix-predictor.mjs',           args: (a) => a },
  burnalert:   { script: 'coverage-burndown.mjs',       args: (a) => a.includes('--alert') ? ['--alert'] : [] },
  regression:    { script: 'coverage-regression.mjs',      args: () => [] },
  autobaseline:  { script: 'coverage-autobaseline.mjs', args: (a) => a.includes('--update') ? ['--update'] : [] },
  patterns:     { script: 'ci-pattern-feedback.mjs',     args: (a) => a.slice(1) },
  chronicle:    { script: 'ci-debug-chronicle.mjs',     args: (a) => a.slice(1) },
  state:        { script: 'ci-state.mjs',               args: (a) => a.slice(1) },
  fix:          { script: 'ci-fix-runner.mjs',         args: (a) => a.slice(1) },
  fixlog:       { script: 'ci-fix-log.mjs',             args: (a) => a.slice(1) },
  fixreport:    { script: 'ci-fix-effectiveness-dashboard.mjs', args: (a) => a },
  decay:        { script: 'ci-pattern-health-decay.mjs',       args: (a) => a },
  predict:      { script: 'ci-fix-predictor.mjs',           args: (a) => a },
  recommend:   { script: 'ci-fix-runner.mjs',            args: (a) => ['recommend', ...a] },
  phealth:      { script: 'ci-pattern-health.mjs',     args: (a) => a.slice(1) },
  hreport:      { script: 'ci-health-report.mjs',    args: (a) => a.slice(1) },
  pgraph:      { script: 'ci-pattern-graph.mjs',  args: (a) => a.slice(1) },
  deploy:     { script: 'ci-deploy-dashboard.mjs', args: (a) => a.slice(1) },
  autoissue:  { script: 'ci-auto-issue.mjs',     args: (a) => a.slice(1) },
  all:          { script: null, args: () => [] },  // special
};

function run(script, args) {
  return new Promise((resolve, reject) => {
    const node = process.platform === 'win32' ? 'node.exe' : 'node';
    const p = spawn(node, [join(SCRIPTS_DIR, script), ...args], {
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: true
    });
    let out = '', err = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => err += d.toString());
    p.on('close', code => {
      if (out) process.stdout.write(out);
      if (err && !err.includes('DeprecationWarning')) process.stderr.write(err);
      resolve({ code, out, err });
    });
    p.on('error', reject);
  });
}

async function runAll() {
  console.log('\n=== CI Command Center — Full Suite ===\n');

  const suite = [
    { name: 'Health Score',    script: 'ci-health.mjs',              args: ['--summary'] },
    { name: 'Coverage Trend', script: 'coverage-trend.mjs',          args: ['--report'] },
    { name: 'Burndown',       script: 'coverage-burndown.mjs',        args: [] },
    { name: 'Regression',     script: 'coverage-regression.mjs',       args: [] },
    { name: 'Chronicle',     script: 'ci-debug-chronicle.mjs',      args: ['report'] },
    { name: 'Patterns',       script: 'ci-pattern-feedback.mjs',      args: ['report'] },
  ];

  let allPassed = true;
  for (const step of suite) {
    const label = `  ${step.name.padEnd(16)}`;
    process.stdout.write(`${label} ... `);
    const result = await run(step.script, step.args);
    const icon = result.code === 0 ? '✅' : '⚠️ ';
    console.log(icon);
    if (result.code !== 0) allPassed = false;
  }

  console.log();
  console.log(allPassed ? '✅ All checks passed' : '⚠️  Some checks need attention');
}

function printHelp() {
  console.log(`
=== CI Command Center ===

Usage: node scripts/ci.mjs <command> [options]

Commands:
  diagnose [--run-id=<id>|--latest]    Diagnose CI failure (GitHub API)
  trend [--suite=<name>]               Show coverage trend report
  health [--badge|--summary]           Show CI health score
  predict [--staged|--diff <f>]         Predict CI failure from git diff
  recommend                           Bayesian fix priority recommendation
  burnalert [--alert]                 Predict coverage threshold breach
  regression                            Analyze coverage regression root cause
  autobaseline [--update]               Recommend/sync coverage thresholds
  patterns [confirm|reject <name>]     Manage pattern confidence
  chronicle append <run_id> [...]       Record debug session
  chronicle report                      Show debug history stats
  state [get|set|init|dump]           CI state store
  fix [list|dry-run|run|check <name>]  Run fix for failure pattern
  fixreport [--output <path>]              Generate fix effectiveness HTML dashboard
  decay [--apply|--stale]                  Pattern health decay analysis
  predict [--staged|--diff <f>]           Predict CI failure from git diff
  phealth [alert|trend <name>]          Pattern health dashboard
  hreport [--output <path>]              Generate HTML health report
  all                                   Run full diagnostic suite

Examples:
  node scripts/ci.mjs diagnose --latest
  node scripts/ci.mjs health --summary
  node scripts/ci.mjs predict --staged
  node scripts/ci.mjs patterns confirm "setup-node cache failure" --notes="removed cache:npm works"
  node scripts/ci.mjs chronicle append 123 pattern=setup-node-cache-fix resolved=true
`);
}

async function main() {
  const [, , cmd, ...args] = process.argv;

  if (!cmd || cmd === 'help' || cmd === '--help') {
    printHelp();
    return;
  }

  if (cmd === 'all') {
    await runAll();
    return;
  }

  const command = COMMANDS[cmd];
  if (!command) {
    console.error(`Unknown command: ${cmd}`);
    console.error("Run: node scripts/ci.mjs help");
    process.exit(1);
  }

  const { script, args: argFn } = command;
  const finalArgs = argFn(args);

  const result = await run(script, finalArgs);
  process.exit(result.code || 0);
}

main().catch(e => { console.error(e); process.exit(1); });
