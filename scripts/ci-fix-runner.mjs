#!/usr/bin/env node
/**
 * scripts/ci-fix-runner.mjs
 * Executes fix commands for high-confidence CI failure patterns.
 *
 * Usage:
 *   node scripts/ci-fix-runner.mjs list              # show available fixes
 *   node scripts/ci-fix-runner.mjs run <name>       # execute fix for pattern
 *   node scripts/ci-fix-runner.mjs dry-run <name>    # preview fix without executing
 *   node scripts/ci-fix-runner.mjs check <name>      # check if fix is applicable
 *
 * Fixes are defined in scripts/ci-failure-patterns.jsonl with confidence >= 0.8.
 */
import { spawn } from 'child_process';
import { existsSync, readFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATTERN_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const WORKFLOW_FILE = join(__dirname, '..', '.github', 'workflows', 'tests.yml');

const GH = process.platform === 'win32' ? 'gh.cmd' : 'gh';

const FIXES = {
  'setup-node cache failure': {
    check: () => {
      if (!existsSync(WORKFLOW_FILE)) return { applicable: false, reason: 'tests.yml not found' };
      const content = readFileSync(WORKFLOW_FILE, 'utf8');
      const hasCacheNpm = content.includes("cache: 'npm'") || content.includes('cache: "npm"') || content.includes('cache:\n        npm');
      return { applicable: hasCacheNpm, reason: hasCacheNpm ? 'cache: npm found in tests.yml' : 'cache: npm not found (already fixed or not present)' };
    },
    dryRun: () => [
      '1. Edit .github/workflows/tests.yml',
      '2. Find: cache: \'npm\' in setup-node action',
      '3. Remove the cache: \'npm\' line or set cache: \'\' (empty)',
      '4. Git commit and push'
    ],
    execute: async () => {
      if (!existsSync(WORKFLOW_FILE)) throw new Error('tests.yml not found');
      let content = readFileSync(WORKFLOW_FILE, 'utf8');
      // Remove cache: 'npm' line in setup-node action
      const lines = content.split('\n');
      const filtered = lines.map(line => {
        if (line.match(/^\s*cache:\s*['"]npm['"]\s*$/)) return null;
        return line;
      }).filter(l => l !== null);
      content = filtered.join('\n');
      const { writeFileSync } = await import('fs');
      writeFileSync(WORKFLOW_FILE, content);
      return 'Removed cache: npm from tests.yml. Commit and push to apply.';
    }
  },
  'npm install failure': {
    check: () => {
      if (!existsSync('./package.json')) return { applicable: false, reason: 'package.json not found' };
      const pkg = JSON.parse(readFileSync('./package.json', 'utf8'));
      return { applicable: true, reason: `engines: ${JSON.stringify(pkg.engines || 'not specified')}` };
    },
    dryRun: () => [
      '1. Check Node version in CI (setup-node@v4 with node-version)',
      '2. Verify package.json engines field matches CI Node version',
      '3. Run: npm install locally to reproduce error',
      '4. Fix version mismatch in package.json or CI workflow'
    ],
    execute: async () => {
      throw new Error('Manual fix required: npm install failure has many causes. Run: node scripts/ci-diagnose.mjs --latest');
    }
  },
  'c8 coverage threshold breach': {
    check: () => {
      if (!existsSync('./coverage-report.json')) return { applicable: false, reason: 'coverage-report.json not found' };
      const cov = JSON.parse(readFileSync('./coverage-report.json', 'utf8'));
      const failedSuites = (cov.suites || []).filter(s => s.coverage < s.threshold);
      return { applicable: failedSuites.length > 0, reason: `${failedSuites.length} suite(s) below threshold` };
    },
    dryRun: () => [
      '1. Run: node scripts/coverage-trend.mjs --report',
      '2. Identify which suite regressed',
      '3. Add tests or adjust threshold via: node scripts/coverage-autobaseline.mjs --update',
      '4. Or lower threshold if legitimate coverage change'
    ],
    execute: async () => {
      throw new Error('Manual fix: Run coverage-trend.mjs first to identify which suite regressed, then add tests or adjust threshold.');
    }
  },
  'test assertion failure': {
    check: () => {
      if (!existsSync('./test-output.txt')) return { applicable: false, reason: 'test-output.txt not found' };
      return { applicable: true, reason: 'test-output.txt available for grep' };
    },
    dryRun: () => [
      '1. Grep test-output.txt for AssertionError',
      '2. Find the failing test file and line',
      '3. Fix the assertion or test expectation',
      '4. Run tests locally to verify'
    ],
    execute: async () => {
      throw new Error('Manual fix: test assertion failures require code investigation.');
    }
  },
  'node not found': {
    check: () => {
      if (!existsSync(WORKFLOW_FILE)) return { applicable: false, reason: 'tests.yml not found' };
      const content = readFileSync(WORKFLOW_FILE, 'utf8');
      const hasNodeVersion = content.includes('node-version:');
      return { applicable: hasNodeVersion, reason: hasNodeVersion ? 'node-version found in tests.yml' : 'no node-version specified' };
    },
    dryRun: () => [
      '1. Check setup-node action in tests.yml',
      '2. Ensure node-version is set (e.g., node-version: \'20\')',
      '3. Check if using actions/setup-node@v4',
      '4. Verify actions/setup-node version compatibility'
    ],
    execute: async () => {
      throw new Error('Manual fix: node not found requires workflow inspection.');
    }
  },
  'exit code 126 - permission/shebang': {
    check: () => {
      // Check for problematic node -e / node -p patterns in scripts
      const problematic = ['node -e', 'node -p', 'node -c'];
      if (!existsSync('./scripts')) return { applicable: false, reason: 'scripts/ not found' };
      let found = false;
      try {
        const files = readdirSync('./scripts', { recursive: true });
        for (const f of files) {
          if (typeof f === 'string' && f.endsWith('.mjs')) {
            try {
              const content = readFileSync(join('./scripts', f), 'utf8');
              if (problematic.some(p => content.includes(p))) { found = true; break; }
            } catch {}
          }
        }
      } catch {}
      return { applicable: found, reason: found ? 'Found problematic node -e/p/c patterns' : 'No problematic patterns found' };
    },
    dryRun: () => [
      '1. Find scripts using node -e, node -p, or node -c',
      '2. Replace with node script.mjs pattern (pre-create the script)',
      '3. Ensure script has proper shebang: #!/usr/bin/env node',
      '4. Test locally: node scripts/your-script.mjs'
    ],
    execute: async () => {
      throw new Error('Manual fix: exit code 126 requires refactoring scripts to use node script.mjs pattern.');
    }
  },
  'gh auth failure': {
    check: () => ({ applicable: true, reason: 'Check GITHUB_TOKEN secret in repo settings' }),
    dryRun: () => [
      '1. Verify GITHUB_TOKEN secret is set in repo Settings > Secrets',
      '2. Ensure token has required permissions (actions:write for check runs)',
      '3. In workflow, use: secrets.GITHUB_TOKEN',
      '4. Check if token has expired'
    ],
    execute: async () => {
      throw new Error('Manual fix: gh auth failure requires repo secret configuration.');
    }
  },
  'ESM import error': {
    check: () => {
      if (!existsSync('./test-output.txt')) return { applicable: false, reason: 'test-output.txt not found' };
      const content = readFileSync('./test-output.txt', 'utf8');
      const hasEsmError = content.includes('ERR_REQUIRE_ESM') || content.includes('ERR_PACKAGE_PATH_NOT_EXPORTED');
      return { applicable: hasEsmError, reason: hasEsmError ? 'ESM error detected' : 'No ESM error found' };
    },
    dryRun: () => [
      '1. Identify the failing module from error message',
      '2. Check if package.json type is "module"',
      '3. Verify .mjs extensions used for ESM files',
      '4. Check import/export statements match'
    ],
    execute: async () => {
      throw new Error('Manual fix: ESM errors require module structure investigation.');
    }
  }
};

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  try {
    const content = readFileSync(PATTERN_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function run(command) {
  return new Promise((resolve) => {
    const parts = command.split(' ');
    const cmd = parts[0];
    const args = parts.slice(1);
    const p = spawn(cmd, args, { shell: true, stdio: 'pipe' });
    let out = '', err = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => err += d.toString());
    p.on('close', code => resolve({ code, out, err }));
    p.on('error', e => resolve({ code: -1, out: '', err: e.message }));
  });
}

async function main() {
  const [, , cmd, ...args] = process.argv;

  if (!cmd || cmd === 'list') {
    const patterns = loadPatterns();
    console.log('\n=== CI Fix Runner — Available Fixes ===\n');
    for (const p of patterns) {
      const fix = FIXES[p.name];
      const autoFix = p.confidence >= 0.8 && fix ? '🟢' : '🔒';
      console.log(`  ${autoFix} ${p.name}`);
      const conf = (p.confirmations != null && p.rejections != null && (p.confirmations + p.rejections) > 0)
        ? p.confirmations / (p.confirmations + p.rejections) : null;
      console.log(`     Severity: ${p.severity} | Confidence: ${conf != null ? `${(conf * 100).toFixed(0)}%` : 'N/A'}`);
      console.log(`     Fix: ${p.fix}`);
      if (fix) {
        const check = fix.check();
        console.log(`     Status: ${check.applicable ? '✅ applicable' : '⏭️  not applicable'} — ${check.reason}`);
      }
      console.log();
    }
    console.log('Run: node scripts/ci-fix-runner.mjs dry-run "<name>"  # preview');
    console.log('Run: node scripts/ci-fix-runner.mjs run "<name>"       # execute');
    return;
  }

  if (cmd === 'check') {
    const name = args.join(' ');
    const patterns = loadPatterns();
    const pattern = patterns.find(p => p.name === name);
    if (!pattern) { console.error(`Pattern not found: ${name}`); process.exit(1); }
    const fix = FIXES[name];
    if (!fix) { console.error(`No fix defined for: ${name}`); process.exit(1); }
    const check = fix.check();
    console.log(`Pattern: ${name}`);
    console.log(`Applicable: ${check.applicable ? 'YES' : 'NO'}`);
    console.log(`Reason: ${check.reason}`);
    process.exit(check.applicable ? 0 : 1);
    return;
  }

  if (cmd === 'dry-run') {
    const name = args.join(' ');
    const fix = FIXES[name];
    if (!fix) { console.error(`No fix defined for: ${name}`); process.exit(1); }
    console.log(`\n=== Dry Run: ${name} ===\n`);
    const steps = fix.dryRun();
    for (const s of steps) console.log(`  ${s}`);
    console.log();
    return;
  }

  if (cmd === 'run') {
    const name = args.join(' ');
    const patterns = loadPatterns();
    const pattern = patterns.find(p => p.name === name);
    if (!pattern) { console.error(`Pattern not found: ${name}`); process.exit(1); }
    if (pattern.confidence < 0.8) {
      console.error(`Confidence too low: ${(pattern.confidence * 100).toFixed(0)}% (need 80% for auto-fix)`);
      process.exit(1);
    }
    const fix = FIXES[name];
    if (!fix) { console.error(`No executable fix defined for: ${name}`); process.exit(1); }
    const check = fix.check();
    if (!check.applicable) {
      console.error(`Fix not applicable: ${check.reason}`);
      process.exit(1);
    }
    console.log(`\n=== Executing: ${name} ===\n`);
    try {
      const result = await fix.execute();
      console.log(result);
      console.log('\n✅ Fix executed successfully');
    } catch (e) {
      console.error(`Error: ${e.message}`);
      process.exit(1);
    }
    return;
  }

  console.log(`Unknown command: ${cmd}`);
  console.log('Usage: node scripts/ci-fix-runner.mjs [list|dry-run|run|check] [pattern-name]');
}

main().catch(e => { console.error(e); process.exit(1); });
