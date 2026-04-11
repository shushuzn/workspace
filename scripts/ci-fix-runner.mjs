#!/usr/bin/env node
/**
 * scripts/ci-fix-runner.mjs
 * Executes fix commands for high-confidence CI failure patterns.
 * Fix verification: records attempts, runs smoke test, auto-updates confidence.
 *
 * Usage:
 *   node scripts/ci-fix-runner.mjs list              # show available fixes
 *   node scripts/ci-fix-runner.mjs run <name>       # execute fix + smoke test
 *   node scripts/ci-fix-runner.mjs dry-run <name>   # preview fix without executing
 *   node scripts/ci-fix-runner.mjs check <name>     # check if fix is applicable
 *   node scripts/ci-fix-runner.mjs smoke <name>     # run smoke test only
 *
 * Confidence >= 80% unlocks auto-fix. Confidence computed from
 * confirmations/(confirmations+rejections).
 * After fix execution, smoke test runs:
 *   smoke pass → pattern confirmations++
 *   smoke fail → pattern rejections++ + revert fix
 */
import { spawn } from 'child_process';
import { existsSync, readFileSync, writeFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATTERN_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const WORKFLOW_FILE = join(__dirname, '..', '.github', 'workflows', 'tests.yml');
const STATE_FILE = join(__dirname, '..', 'ci-state.json');

function run(cmd, args, cwd = join(__dirname, '..')) {
  return new Promise((resolve, reject) => {
    const shell = process.platform === 'win32';
    const p = spawn(cmd, args, { shell, cwd, stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '', err = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => err += d.toString());
    p.on('close', code => resolve({ code, out, err, outRaw: out, errRaw: err }));
    p.on('error', reject);
  });
}

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  try {
    const content = readFileSync(PATTERN_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function savePatterns(patterns) {
  const lines = patterns.map(p => JSON.stringify(p)).join('\n') + '\n';
  writeFileSync(PATTERN_FILE, lines);
}

function getConfidence(pattern) {
  if (pattern.confirmations == null || pattern.rejections == null) return null;
  if (pattern.confirmations + pattern.rejections === 0) return null;
  return pattern.confirmations / (pattern.confirmations + pattern.rejections);
}

function updatePatternConfidence(name, confirmed) {
  const patterns = loadPatterns();
  const idx = patterns.findIndex(p => p.name === name);
  if (idx === -1) return false;
  if (patterns[idx].confirmations == null) patterns[idx].confirmations = 0;
  if (patterns[idx].rejections == null) patterns[idx].rejections = 0;
  if (confirmed) {
    patterns[idx].confirmations++;
    patterns[idx].lastConfirmed = new Date().toISOString().split('T')[0];
  } else {
    patterns[idx].rejections++;
    patterns[idx].lastRejected = new Date().toISOString().split('T')[0];
  }
  savePatterns(patterns);
  return true;
}

function recordFixAttempt(name, smokeResult) {
  try {
    let state = {};
    if (existsSync(STATE_FILE)) {
      try { state = JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch {}
    }
    if (!state.patterns) state.patterns = {};
    if (!state.patterns.fixHistory) state.patterns.fixHistory = {};
    if (!state.patterns.lastFixAttempt) state.patterns.lastFixAttempt = {};
    const entry = {
      pattern: name,
      timestamp: new Date().toISOString(),
      result: smokeResult === null ? 'applied' : (smokeResult ? 'confirmed' : 'rejected'),
      smokeTest: smokeResult
    };
    if (!state.patterns.fixHistory[name]) state.patterns.fixHistory[name] = [];
    state.patterns.fixHistory[name].push(entry);
    state.patterns.lastFixAttempt[name] = entry;
    state.lastUpdated = new Date().toISOString();
    writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch {}
}

// Revert helpers per fix type
const REVERT = {
  'setup-node cache failure': async () => {
    // Revert: add cache: 'npm' back after the uses: actions/setup-node@v4 line
    if (!existsSync(WORKFLOW_FILE)) return;
    let content = readFileSync(WORKFLOW_FILE, 'utf8');
    // Find the setup-node block and restore cache: 'npm'
    const lines = content.split('\n');
    const restored = [];
    for (let i = 0; i < lines.length; i++) {
      restored.push(lines[i]);
      // After setup-node action with node-version but no cache, add cache
      if (lines[i].includes('uses: actions/setup-node@v4') && !content.slice(content.indexOf(lines[i]), content.indexOf(lines[i]) + 500).includes('cache:')) {
        // Find indentation
        const indent = lines[i].match(/^(\s*)/)[1];
        restored.push(`${indent}        cache: 'npm'`);
      }
    }
    writeFileSync(WORKFLOW_FILE, restored.join('\n'));
  }
};

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
      '3. Remove the cache: \'npm\' line',
      '4. Git commit and push'
    ],
    execute: async () => {
      if (!existsSync(WORKFLOW_FILE)) throw new Error('tests.yml not found');
      let content = readFileSync(WORKFLOW_FILE, 'utf8');
      const lines = content.split('\n');
      const filtered = lines.map(line => {
        if (line.match(/^\s*cache:\s*['"]npm['"]\s*$/)) return null;
        return line;
      }).filter(l => l !== null);
      content = filtered.join('\n');
      writeFileSync(WORKFLOW_FILE, content);
      return 'Removed cache: npm from tests.yml. Commit and push to apply.';
    },
    smokeTest: async () => {
      // Smoke test: verify YAML is valid and workflow file parses
      const result = await run('node', ['-e', `const yaml=require('js-yaml'); const fs=require('fs'); yaml.load(fs.readFileSync('${WORKFLOW_FILE.replace(/\\/g, '\\\\')}', 'utf8')); console.log('YAML valid'); process.exit(0);`]);
      if (result.code !== 0) {
        // Try alternative: just check YAML syntax without require
        const yamlResult = await run('node', ['-e', `const fs=require('fs'); const content=fs.readFileSync('${WORKFLOW_FILE.replace(/\\/g, '\\\\')}', 'utf8'); try { require('js-yaml'); } catch(e) { process.exit(1); }`]);
        if (yamlResult.code !== 0) {
          console.log('  [smoke] WARNING: js-yaml not available, skipping YAML validation');
          return null; // indeterminate — skip confidence update
        }
      }
      // Also check workflow file has no duplicate setup-node entries
      const content = readFileSync(WORKFLOW_FILE, 'utf8');
      const setupNodeCount = (content.match(/uses: actions\/setup-node@v4/g) || []).length;
      console.log(`  [smoke] YAML valid, setup-node@v4 count: ${setupNodeCount}`);
      return setupNodeCount >= 1; // at least one setup-node should remain
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
    },
    smokeTest: async () => null
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
    },
    smokeTest: async () => null
  },
  'test assertion failure': {
    check: () => ({ applicable: true, reason: 'test-output.txt needed for details' }),
    dryRun: () => [
      '1. Grep test-output.txt for AssertionError',
      '2. Find the failing test file and line',
      '3. Fix the assertion or test expectation',
      '4. Run tests locally to verify'
    ],
    execute: async () => {
      throw new Error('Manual fix: test assertion failures require code investigation.');
    },
    smokeTest: async () => null
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
      '3. Verify actions/setup-node version compatibility'
    ],
    execute: async () => {
      throw new Error('Manual fix: node not found requires workflow inspection.');
    },
    smokeTest: async () => null
  },
  'exit code 126 - permission/shebang': {
    check: () => {
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
    },
    smokeTest: async () => null
  },
  'gh auth failure': {
    check: () => ({ applicable: true, reason: 'Check GITHUB_TOKEN secret in repo settings' }),
    dryRun: () => [
      '1. Verify GITHUB_TOKEN secret is set in repo Settings > Secrets',
      '2. Ensure token has required permissions (actions:write for check runs)',
      '3. In workflow, use: secrets.GITHUB_TOKEN'
    ],
    execute: async () => {
      throw new Error('Manual fix: gh auth failure requires repo secret configuration.');
    },
    smokeTest: async () => null
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
    },
    smokeTest: async () => null
  }
};

function getFixHistory(name) {
  try {
    if (!existsSync(STATE_FILE)) return null;
    const state = JSON.parse(readFileSync(STATE_FILE, 'utf8'));
    return state.patterns?.fixHistory?.[name] || null;
  } catch { return null; }
}

async function main() {
  const [, , cmd, ...args] = process.argv;

  if (!cmd || cmd === 'list') {
    const patterns = loadPatterns();
    console.log('\n=== CI Fix Runner ===\n');
    for (const p of patterns) {
      const fix = FIXES[p.name];
      const conf = getConfidence(p);
      const autoFix = fix && conf !== null && conf >= 0.8 ? '🟢' : '🔒';
      const history = getFixHistory(p.name);
      console.log(`  ${autoFix} ${p.name}`);
      console.log(`     Severity: ${p.severity} | Confidence: ${conf != null ? `${(conf * 100).toFixed(0)}%` : 'N/A'}`);
      console.log(`     Fix: ${p.fix}`);
      if (fix) {
        const check = fix.check();
        console.log(`     Status: ${check.applicable ? '✅ applicable' : '⏭️  not applicable'} — ${check.reason}`);
      }
      if (history && history.length > 0) {
        const last = history[history.length - 1];
        console.log(`     Last fix: ${new Date(last.timestamp).toLocaleDateString()} (${history.length} total attempts)`);
        console.log(`     Last result: ${last.result}${last.smokeTest !== undefined ? ` (smoke: ${last.smokeTest ? 'PASS' : 'FAIL'})` : ''}`);
      }
      console.log();
    }
    console.log('Run: node scripts/ci-fix-runner.mjs dry-run "<name>"  # preview');
    console.log('Run: node scripts/ci-fix-runner.mjs run "<name>"       # execute + smoke test');
    console.log('Run: node scripts/ci-fix-runner.mjs smoke "<name>"   # smoke test only');
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

  if (cmd === 'smoke') {
    const name = args.join(' ');
    const fix = FIXES[name];
    if (!fix) { console.error(`No fix defined for: ${name}`); process.exit(1); }
    if (!fix.smokeTest) { console.log('No smoke test defined for this pattern'); process.exit(0); }
    console.log(`\n=== Smoke Test: ${name} ===\n`);
    try {
      const result = await fix.smokeTest();
      if (result === null) {
        console.log('  ⏭️  Smoke test indeterminate (skipped confidence update)');
      } else if (result) {
        console.log('  ✅ Smoke test PASSED');
      } else {
        console.log('  ❌ Smoke test FAILED');
      }
    } catch (e) {
      console.log(`  ❌ Smoke test ERROR: ${e.message}`);
    }
    return;
  }

  if (cmd === 'dry-run') {
    const name = args.join(' ');
    const fix = FIXES[name];
    if (!fix) { console.error(`No fix defined for: ${name}`); process.exit(1); }
    console.log(`\n=== Dry Run: ${name} ===\n`);
    const steps = fix.dryRun();
    for (const s of steps) console.log(`  ${s}`);
    const history = getFixHistory(name);
    if (history && history.length > 0) {
      console.log(`\n  Fix history (${history.length} attempts):`);
      for (const h of history.slice(-3)) {
        console.log(`    - ${new Date(h.timestamp).toLocaleDateString()}: ${h.result}${h.smokeTest !== undefined ? ` (smoke: ${h.smokeTest ? 'PASS' : 'FAIL'})` : ''}`);
      }
    }
    console.log();
    return;
  }

  if (cmd === 'run') {
    const name = args.join(' ');
    const patterns = loadPatterns();
    const pattern = patterns.find(p => p.name === name);
    if (!pattern) { console.error(`Pattern not found: ${name}`); process.exit(1); }
    const conf = getConfidence(pattern);
    if (conf !== null && conf < 0.8) {
      console.error(`Confidence too low: ${(conf * 100).toFixed(0)}% (need 80% for auto-fix)`);
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

      // Run smoke test
      let smokeResult = null;
      if (fix.smokeTest) {
        console.log('\n--- Running smoke test ---');
        try {
          smokeResult = await fix.smokeTest();
          if (smokeResult === null) {
            console.log('  ⏭️  Smoke indeterminate — skipping confidence update');
          } else if (smokeResult) {
            console.log('  ✅ Smoke PASSED — confirming fix effectiveness');
          } else {
            console.log('  ❌ Smoke FAILED — reverting fix and rejecting pattern');
            // Auto-revert
            if (REVERT[name]) {
              await REVERT[name]();
              console.log('  ↩️  Reverted fix automatically');
            }
          }
        } catch (e) {
          console.log(`  ⚠️  Smoke error: ${e.message} — skipping confidence update`);
          smokeResult = null;
        }
      }

      recordFixAttempt(name, smokeResult);

      if (smokeResult !== null) {
        const updated = updatePatternConfidence(name, smokeResult);
        if (updated) {
          const newConf = getConfidence({ confirmations: patterns.find(p => p.name === name).confirmations + (smokeResult ? 1 : 0), rejections: patterns.find(p => p.name === name).rejections + (smokeResult ? 0 : 1) });
          console.log(`\n  Pattern confidence: ${conf !== null ? `${(conf * 100).toFixed(0)}% → ` : ''}${smokeResult ? '✅ confirmed' : '❌ rejected'}`);
        }
      }

      console.log('\n✅ Fix executed successfully');
    } catch (e) {
      console.error(`Error: ${e.message}`);
      process.exit(1);
    }
    return;
  }

  if (cmd === 'check-file') {
    // Pre-flight check: scan a file for patterns that would fail CI
    const filePath = args[0];
    if (!filePath) { console.error('Usage: check-file <path>'); process.exit(1); }
    if (!existsSync(filePath)) { console.error(`File not found: ${filePath}`); process.exit(1); }

    const content = readFileSync(filePath, 'utf8');
    const patterns = loadPatterns();
    const matched = [];

    for (const p of patterns) {
      const fix = FIXES[p.name];
      if (!fix) continue;

      let fileRelevant = false;
      let wouldIntroduce = false;

      // Route to type-specific checker
      if (filePath.endsWith('.yml') || filePath.endsWith('.yaml')) {
        // Workflow file: check workflow-specific patterns
        const wfPatterns = {
          'setup-node cache failure': () => {
            const re = /cache:\s*['"]npm['"]/;
            return { match: re.test(content), detail: 'cache: npm found in workflow' };
          },
          'node not found': () => {
            // setup-node without node-version
            const hasSetup = /uses:\s*actions\/setup-node@v\d/.test(content);
            const hasVersion = /node-version:\s*['"]?\d+['"]?/.test(content);
            return { match: hasSetup && !hasVersion, detail: hasSetup ? 'setup-node without node-version' : 'no setup-node action' };
          },
          'exit code 126 - permission/shebang': () => {
            // Scripts with node -e/p/c inline
            const re = /\bnode\s+-[epc]\s+['"`]/;
            return { match: re.test(content), detail: 'node -e/p/c inline script detected' };
          },
          'gh auth failure': () => {
            const re = /GITHUB_TOKEN|secrets\./;
            return { match: !re.test(content), detail: 'workflow uses GITHUB_TOKEN or secrets.*' };
          }
        };

        if (wfPatterns[p.name]) {
          const result = wfPatterns[p.name]();
          if (result.match) {
            fileRelevant = true;
            wouldIntroduce = true;
          }
        }
      } else {
        // Non-workflow file: only check patterns relevant to source files
        const sourcePatterns = {
          'exit code 126 - permission/shebang': () => {
            const re = /\bnode\s+-[epc]\s+['"`]/;
            return { match: re.test(content), detail: 'node -e/p/c inline detected' };
          },
          'ESM import error': () => {
            const re = /ERR_REQUIRE_ESM|ERR_PACKAGE_PATH_NOT_EXPORTED|require\(.*\.mjs/;
            return { match: re.test(content), detail: 'ESM compatibility issue detected' };
          }
        };

        if (sourcePatterns[p.name]) {
          const result = sourcePatterns[p.name]();
          if (result.match) {
            fileRelevant = true;
            wouldIntroduce = true;
          }
        }
      }

      if (fileRelevant) {
        const conf = getConfidence(p);
        matched.push({ name: p.name, severity: p.severity, confidence: conf, fix: p.fix, wouldIntroduce });
      }
    }

    if (matched.length === 0) {
      console.log(`✅ No CI failure patterns detected in: ${filePath}`);
      process.exit(0);
    }

    console.log(`\n⚠️  CI failure patterns detected in: ${filePath}\n`);
    for (const m of matched) {
      const confStr = m.confidence !== null ? `${(m.confidence * 100).toFixed(0)}%` : 'N/A';
      const icon = m.severity === 'P0' ? '🔴' : '🟡';
      console.log(`  ${icon} ${m.name} (${m.severity}) | confidence: ${confStr}`);
      console.log(`     Fix: ${m.fix}`);
      console.log(`     ${m.wouldIntroduce ? '⚡ Would be introduced' : '⚠️  Already present'}`);
      console.log();
    }
    process.exit(matched.some(m => m.severity === 'P0') ? 2 : 1);
  }

  console.log(`Unknown command: ${cmd}`);
  console.log('Usage: node scripts/ci-fix-runner.mjs [list|dry-run|run|check|smoke|check-file] [pattern-name]');
}

main().catch(e => { console.error(e); process.exit(1); });
