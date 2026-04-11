#!/usr/bin/env node
/**
 * scripts/ci-diagnose.mjs
 * CI failure diagnostic tool - inputs run_id, outputs structured failure report.
 *
 * Usage:
 *   node scripts/ci-diagnose.mjs [run_id]
 *   node scripts/ci-diagnose.mjs --latest
 *
 * Uses `gh run view` + `gh api` to fetch failure info and identify root cause.
 * Pattern matches common failure modes (setup-node, npm install, test failures).
 */
import { spawn } from 'child_process';
import { existsSync } from 'fs';

const GH = process.platform === 'win32' ? 'gh.cmd' : 'gh';

// ── CLI args ──────────────────────────────────────────────────────────────────
const runId = process.argv.includes('--latest') ? null : process.argv[2];
const repo = process.env.GITHUB_REPOSITORY || 'shushuzn/workspace';

// ── Run gh command ─────────────────────────────────────────────────────────────
function gh(args, { capture = true } = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(GH, args, {
      stdio: capture ? ['pipe', 'pipe', 'pipe'] : ['ignore', 'inherit', 'inherit'],
      shell: true
    });
    let out = '', err = '';
    if (capture) {
      p.stdout.on('data', d => out += d.toString());
      p.stderr.on('data', d => err += d.toString());
    }
    p.on('close', code => {
      if (capture) resolve({ code, out, err });
      else resolve({ code, out: '', err: '' });
    });
    p.on('error', reject);
  });
}

// ── Detect run_id ──────────────────────────────────────────────────────────────
async function findRunId() {
  const { out } = await gh(['run', 'list', '--json', 'databaseId,name,status,conclusion', '-L', '5', '--repo', repo]);
  try {
    const runs = JSON.parse(out);
    const latest = runs.find(r => r.status === 'in_progress' || r.status === 'completed') || runs[0];
    if (!latest) throw new Error('No runs found');
    return String(latest.databaseId);
  } catch (e) {
    console.error('Failed to find run_id:', e.message);
    console.error('Output:', out);
    process.exit(1);
  }
}

// ── Fetch run details ─────────────────────────────────────────────────────────
async function getRunDetails(id) {
  const { out } = await gh(['run', 'view', id, '--json', 'name,status,conclusion,runsOn,jobs,createdAt,url', '--repo', repo]);
  return JSON.parse(out);
}

async function getJobSteps(runId) {
  const { out } = await gh(['run', 'view', id, '--json', 'jobs', '--repo', repo, '--log']);
  // --log flag returns log URL, let's use the API instead
  return null;
}

async function getRunJobs(runId) {
  const { out } = await gh(['api', `repos/${repo}/actions/runs/${runId}/jobs`]);
  return JSON.parse(out);
}

// ── Fetch artifact ────────────────────────────────────────────────────────────
async function downloadArtifact(runId, namePattern) {
  const { out } = await gh(['api', `repos/${repo}/actions/runs/${runId}/artifacts`]);
  try {
    const data = JSON.parse(out);
    const artifact = data.artifacts?.find(a => a.name.includes(namePattern));
    if (!artifact) return null;
    const { out: logOut } = await gh(['api', artifact.archive_download_url, '--jq', '.']);
    return logOut;
  } catch { return null; }
}

// ── Pattern match common failures ─────────────────────────────────────────────
const FAILURE_PATTERNS = [
  {
    name: 'setup-node cache failure',
    pattern: /setup-node.*cache.*npm|failed to retrieve.*cache/gi,
    hint: 'setup-node@v4 cache:\'npm\' is known to fail on GitHub runners. Remove cache:\'npm\' from setup-node action.',
    severity: 'P0'
  },
  {
    name: 'npm install failure',
    pattern: /npm ERR|npm install.*failed|EBADPLATFORM/gi,
    hint: 'Check package.json compatibility and Node version match.',
    severity: 'P1'
  },
  {
    name: 'c8 coverage threshold',
    pattern: /coverage below threshold|COVERAGE FAIL|❌ Coverage/gi,
    hint: 'Coverage dropped below threshold. Check coverage-report.json for per-suite details.',
    severity: 'P1'
  },
  {
    name: 'test assertion failure',
    pattern: /AssertionError|expected \d+.*got \d+|fail.*at.*\.test\.mjs/gi,
    hint: 'Test assertion failed. Check the specific test in test-output.txt.',
    severity: 'P1'
  },
  {
    name: 'node not found',
    pattern: /node.*not found|command not found.*node/gi,
    hint: 'Node.js setup failed. Verify setup-node action version and node-version parameter.',
    severity: 'P0'
  },
  {
    name: 'exit code 126',
    pattern: /exit code 126|error 126/gi,
    hint: 'Permission denied or invalid shebang. This often happens with node -e on Windows Git Bash.',
    severity: 'P1'
  },
  {
    name: 'gh auth failure',
    pattern: /gh.*auth|AuthenticationError|GITHUB_TOKEN/gi,
    hint: 'GitHub token issue. Ensure GITHUB_TOKEN is set and has actions:write permission.',
    severity: 'P0'
  },
  {
    name: 'ESM import error',
    pattern: /ERR_PACKAGE_PATH_NOT_EXPORTED|Cannot find module|ERR_REQUIRE_ESM/gi,
    hint: 'Module resolution error. Check if target file uses ESM correctly.',
    severity: 'P2'
  }
];

function analyzeFailure(text) {
  const findings = [];
  for (const fp of FAILURE_PATTERNS) {
    if (fp.pattern.test(text)) {
      findings.push({ name: fp.name, hint: fp.hint, severity: fp.severity });
    }
  }
  return findings;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const id = runId || await findRunId();
  console.log(`\n=== CI Diagnose ===`);
  console.log(`Run: ${id}`);
  console.log(`Repo: ${repo}\n`);

  // Get run info
  const run = await getRunDetails(id);
  console.log(`Status: ${run.status} | Conclusion: ${run.conclusion || 'pending'}`);
  console.log(`Name: ${run.name}`);
  console.log(`Created: ${run.createdAt}`);
  console.log(`URL: ${run.url}\n`);

  // Get jobs
  const jobsData = await getRunJobs(id);
  const jobs = jobsData.jobs || [];

  console.log(`Jobs (${jobs.length}):`);
  for (const job of jobs) {
    const icon = job.conclusion === 'success' ? '✅' : job.conclusion === 'failure' ? '❌' : '⏳';
    console.log(`  ${icon} ${job.name} (${job.id}) - ${job.conclusion || job.status}`);
  }
  console.log();

  // Get failed job logs
  const failedJobs = jobs.filter(j => j.conclusion === 'failure');
  if (failedJobs.length === 0) {
    console.log('No failed jobs detected.');
  } else {
    for (const job of failedJobs) {
      console.log(`\n--- Failed Job: ${job.name} ---`);
      const { out: logUrlData } = await gh(['api', `repos/${repo}/actions/jobs/${job.id}/logs`]);
      try {
        const logUrl = JSON.parse(logUrlData);
        if (logUrl && logUrl.log_filegz_url) {
          // Download and parse log
          const { out: rawLogs } = await gh(['api', logUrl.log_filegz_url]);
          analyzeAndPrint(rawLogs);
        }
      } catch {
        // Fallback: try to get step details
        const stepUrl = `repos/${repo}/actions/jobs/${job.id}/steps`;
        const { out: stepsData } = await gh(['api', stepUrl]);
        try {
          const steps = JSON.parse(stepsData);
          for (const step of steps) {
            if (step.conclusion === 'failure') {
              console.log(`  Failed step: ${step.name}`);
              console.log(`    Number: ${step.number}`);
            }
          }
        } catch { /* ignore */ }
      }
    }
  }

  // Try to download and analyze test-output artifact
  const testOutputArtifact = jobsData.artifacts?.find(a => a.name.includes('test-output'));
  if (testOutputArtifact) {
    console.log(`\n--- Test Output Artifact Found ---`);
    console.log(`Name: ${testOutputArtifact.name}`);
    console.log(`Download: ${testOutputArtifact.archive_download_url}`);
  }

  // Local coverage-report check
  const localCov = existsSync('./coverage-report.json');
  if (localCov) {
    console.log(`\n--- Local coverage-report.json Found ---`);
    const { readFileSync } = await import('fs');
    try {
      const cov = JSON.parse(readFileSync('./coverage-report.json', 'utf8'));
      console.log(`Total coverage: ${cov.total}%`);
      console.log(`Pass: ${cov.pass}`);
      for (const s of (cov.suites || [])) {
        const icon = s.coverage >= s.threshold ? '✅' : '❌';
        console.log(`  ${icon} ${s.suite}: ${s.coverage}% (threshold: ${s.threshold}%)`);
      }
    } catch { /* ignore */ }
  }

  // Summary
  console.log(`\n=== Diagnostic Summary ===`);
  console.log(`Run ID: ${id}`);
  console.log(`URL: ${run.url}`);
  if (failedJobs.length > 0) {
    console.log(`Failed jobs: ${failedJobs.map(j => j.name).join(', ')}`);
  }
  console.log(`\nNext steps:`);
  console.log(`  1. gh run view ${id} --log          # Full logs`);
  console.log(`  2. gh run download ${id} --repo ${repo}  # Download artifacts`);
  console.log(`  3. Check coverage-report.json locally`);

  process.exit(failedJobs.length > 0 ? 1 : 0);
}

function analyzeAndPrint(text) {
  const findings = analyzeFailure(text);
  if (findings.length === 0) {
    // Try to extract the last few lines of error
    const lines = text.split('\n').slice(-30);
    console.log('Last 30 lines of log:');
    for (const l of lines) console.log('  ' + l.substring(0, 120));
  } else {
    console.log(`Detected ${findings.length} issue(s):`);
    for (const f of findings) {
      console.log(`  [${f.severity}] ${f.name}`);
      console.log(`    → ${f.hint}`);
    }
  }
}

main().catch(e => { console.error(e); process.exit(1); });
