#!/usr/bin/env node
/**
 * scripts/ci-fix-predictor.mjs
 * Predicts which CI failure pattern a git diff is most likely to trigger,
 * based on change-feature → failure-pattern association scoring.
 *
 * Usage:
 *   node scripts/ci-fix-predictor.mjs                    # predict from unstaged diff
 *   node scripts/ci-fix-predictor.mjs --staged          # from git staged diff
 *   node scripts/ci-fix-predictor.mjs --diff <file>    # from specific diff file
 *   node scripts/ci-fix-predictor.mjs --help           # show feature weights
 *
 * Output: ranked list of patterns with risk score, or empty (no risk detected).
 */
import { existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = join(__dirname, '..', 'ci-state.json');
const PATTERNS_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const HELP = process.argv.includes('--help');
const STAGED = process.argv.includes('--staged');
const DIFF_FILE = process.argv[process.argv.indexOf('--diff') + 1] || null;

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch { return {}; }
}

function loadPatterns() {
  if (!existsSync(PATTERNS_FILE)) return [];
  try {
    const content = readFileSync(PATTERNS_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function execGit(cmd) {
  try {
    return execSync(cmd, { cwd: join(__dirname, '..'), encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
  } catch (e) {
    return e.stdout || '';
  }
}

function getDiff() {
  if (DIFF_FILE) {
    return readFileSync(DIFF_FILE, 'utf8');
  }
  if (STAGED) {
    return execGit('git diff --cached');
  }
  return execGit('git diff');
}

// Feature extractors: each returns a map of feature-name → count
function extractFeatures(diff) {
  const lines = diff.split('\n');
  const features = {
    // File-level features
    'package_json': 0,
    'package_lock': 0,
    'workflow_yml': 0,
    'workflow_yaml': 0,
    'test_file': 0,
    'node_script': 0,
    'bash_script': 0,
    'package_json_engines': 0,
    'package_json_scripts': 0,
    'github_actions': 0,
    // Content-level features
    'node_minus_e': 0,      // node -e / node -p / node -c
    'cache_colon_npm': 0,  // cache: 'npm'
    'setup_node': 0,       // uses: actions/setup-node
    'node_version_missing': 0,
    'npm_install': 0,
    'npm_err': 0,
    'coverage_threshold': 0,
    'exit_126': 0,
    'shebang_missing': 0,
    'esmodule_import': 0,
    'gh_auth': 0,
  };

  const changedFiles = new Set();
  let inFile = null;

  for (const line of lines) {
    // diff --git a/path b/path
    const fileMatch = line.match(/^diff --git a\/(.+?) b\/(.+)/);
    if (fileMatch) {
      inFile = fileMatch[2];
      changedFiles.add(inFile);
    }

    if (!inFile) continue;

    // Package files
    if (/package\.json$/.test(inFile)) features['package_json']++;
    if (/package-lock\.json$/.test(inFile)) features['package_lock']++;
    if (/\.github\/workflows?\/.*\.ya?ml$/.test(inFile)) features['workflow_yml']++;

    // Test files
    if (/\.(test|spec)\.(js|mjs|ts)$/.test(inFile)) features['test_file']++;

    // Node/bash scripts
    if (/\.(mjs|js)$/.test(inFile) && !inFile.includes('node_modules')) {
      features['node_script']++;
    }
    if (/\.sh$/.test(inFile)) features['bash_script']++;

    // Content features (only in added lines)
    if (line.startsWith('+') && !line.startsWith('+++')) {
      const content = line.slice(1).trim();

      if (/node\s+-[epc]\s+"/.test(content) || /node\s+-[epc]\s+'/.test(content)) {
        features['node_minus_e']++;
      }
      if (/cache:\s*['"]npm['"]/.test(content)) {
        features['cache_colon_npm']++;
      }
      if (/actions\/setup-node@v\d*/.test(content)) {
        features['setup_node']++;
      }
      if (/node-version:\s*['"]?20['"]?/.test(content)) {
        // Check if missing -v4 or wrong
      }
      if (/node-version\s*:$/.test(content)) {
        features['node_version_missing']++;
      }
      if (/\.npmrc|\.nvmrc|node_version/.test(content)) {
        features['package_json_engines']++;
      }
      if (/scripts\s*:/.test(content)) {
        features['package_json_scripts']++;
      }
      if (/npm\s+install/.test(content)) {
        features['npm_install']++;
      }
      if (/npm\s+ERR!/.test(content)) {
        features['npm_err']++;
      }
      if (/coverage.*threshold|c8.*fail|Coverage.*below/.test(content)) {
        features['coverage_threshold']++;
      }
      if (/exit\s+126|error\s+126/.test(content)) {
        features['exit_126']++;
      }
      if (/^#!\s*$|^#!\s*\/usr\/bin\/env\s+node/.test(content)) {
        features['shebang_missing']++;
      }
      if (/import\s+.*\s+from\s+['"].*\.js['"]/.test(content)) {
        features['esmodule_import']++;
      }
      if (/GITHUB_TOKEN|secrets\.GITHUB/.test(content)) {
        features['gh_auth']++;
      }
    }

    // Workflow context: setup-node without node-version
    if (line.startsWith('-') && !line.startsWith('---')) {
      const content = line.slice(1).trim();
      if (/node-version:\s*['"]?\d+/.test(content)) {
        features['node_version_missing']++; // removal of node-version is concerning
      }
    }
  }

  return { features, files: changedFiles };
}

// Pattern association: which features strongly predict which pattern
const PATTERN_FEATURES = {
  'setup-node cache failure': {
    features: { 'setup_node': 3, 'cache_colon_npm': 9, 'workflow_yml': 2 },
    severity: 'P0',
  },
  'npm install failure': {
    features: { 'package_json': 3, 'package_lock': 4, 'npm_install': 2, 'npm_err': 1 },
    severity: 'P1',
  },
  'c8 coverage threshold breach': {
    features: { 'test_file': 1, 'coverage_threshold': 6 },
    severity: 'P1',
  },
  'test assertion failure': {
    features: { 'test_file': 5, 'package_json_scripts': 1 },
    severity: 'P1',
  },
  'node not found': {
    features: { 'workflow_yml': 2, 'node_version_missing': 5, 'package_json_engines': 3 },
    severity: 'P0',
  },
  'exit code 126 - permission/shebang': {
    features: { 'node_minus_e': 8, 'bash_script': 2, 'node_script': 1, 'exit_126': 3 },
    severity: 'P1',
  },
  'gh auth failure': {
    features: { 'gh_auth': 5, 'workflow_yml': 1 },
    severity: 'P0',
  },
  'ESM import error': {
    features: { 'esmodule_import': 6, 'node_script': 2 },
    severity: 'P2',
  },
};

function scorePatterns(features, patterns, state) {
  const fixHistory = state?.patterns?.fixHistory || {};
  const lastFixAttempt = state?.patterns?.lastFixAttempt || {};

  const scores = [];

  for (const pattern of patterns) {
    const pf = PATTERN_FEATURES[pattern.name];
    if (!pf) continue;

    let rawScore = 0;
    const matchedFeatures = [];

    for (const [featName, weight] of Object.entries(pf.features)) {
      const count = features[featName] || 0;
      if (count > 0) {
        rawScore += weight * Math.min(count, 3); // cap per-feature contribution
        matchedFeatures.push(`${featName}×${count}`);
      }
    }

    if (rawScore === 0) continue;

    // Confidence multiplier from history
    const conf = (pattern.confirmations != null && (pattern.confirmations + pattern.rejections) > 0)
      ? pattern.confirmations / (pattern.confirmations + pattern.rejections)
      : 0.5; // default 0.5 for unseen patterns

    // Decay multiplier from decay report
    const decayReport = state?.patterns?.decayReport?.patterns || [];
    const decayEntry = decayReport.find(p => p.name === pattern.name);
    const decayMult = decayEntry?.decayFactor ?? 1.0;

    const effConf = conf * decayMult;

    // Pattern is less relevant if it was recently applied and worked
    const lastFix = lastFixAttempt[pattern.name];
    const recentlyApplied = lastFix && (Date.now() - new Date(lastFix.timestamp)) < 7 * 24 * 60 * 60 * 1000;

    const risk = pf.severity === 'P0' ? 3 : pf.severity === 'P1' ? 2 : 1;
    const finalScore = rawScore * effConf * risk * (recentlyApplied ? 0.3 : 1.0);

    scores.push({
      name: pattern.name,
      severity: pf.severity,
      rawScore,
      confidence: effConf,
      matchedFeatures,
      fix: pattern.fix,
      hint: pattern.hint,
      risk,
      finalScore,
      recentlyApplied,
    });
  }

  return scores.sort((a, b) => b.finalScore - a.finalScore);
}

function formatReport(scores, diff) {
  if (scores.length === 0) return null;

  const top = scores[0];
  const diffLines = diff.split('\n').length;
  const files = [...(diff.match(/^diff --git a\/(.+?) b\//gm) || [])].map(m => m.replace('diff --git a/', ''));

  const lines = [];
  lines.push(`\n🔮 Fix Prediction Report\n`);
  lines.push(`Changed files: ${files.length}`);
  lines.push(`Total diff: ${diffLines} lines\n`);

  lines.push(`\n⚠️  Top risk: ${top.name} [${top.severity}]`);
  lines.push(`   Score: ${top.finalScore.toFixed(1)} | Confidence: ${(top.confidence * 100).toFixed(0)}%`);
  lines.push(`   Matched: ${top.matchedFeatures.join(', ')}`);
  if (top.recentlyApplied) lines.push(`   (recently applied — confidence reduced)`);
  lines.push(`   Fix: ${top.fix}`);
  lines.push(`   Hint: ${top.hint}`);

  if (scores.length > 1) {
    lines.push(`\nOther risks:`);
    for (const s of scores.slice(1, 4)) {
      lines.push(`  · ${s.name} [${s.severity}] score=${s.finalScore.toFixed(1)} ${s.matchedFeatures.slice(0,2).join(',')}`);
    }
  }

  const autoApply = top.finalScore >= 20 && top.severity === 'P0' && top.confidence >= 0.7;
  if (autoApply) {
    lines.push(`\n✅ Auto-fix candidate (score≥20, P0, conf≥70%)`);
    lines.push(`   Run: node scripts/ci-fix-runner.mjs run "${top.name}" --force`);
  } else if (top.finalScore >= 10) {
    lines.push(`\n💡 Pre-commit warning (score≥10)`);
    lines.push(`   Run: node scripts/ci-fix-runner.mjs dry-run "${top.name}"`);
  }

  return lines.join('\n');
}

async function main() {
  if (HELP) {
    console.log(`
ci-fix-predictor.mjs — Predict CI failure from git diff

Usage:
  node scripts/ci-fix-predictor.mjs                    # unstaged changes
  node scripts/ci-fix-predictor.mjs --staged           # staged changes
  node scripts/ci-fix-predictor.mjs --diff <file>     # from diff file
  node scripts/ci-fix-predictor.mjs --help             # this help

Feature → Pattern weights:
  cache_colon_npm → setup-node cache failure (9)
  node_minus_e     → exit code 126 (8)
  setup_node       → setup-node cache failure (3)
  node_version_missing → node not found (5)
  package_lock     → npm install failure (4)
  esmodule_import  → ESM import error (6)
  coverage_threshold → c8 coverage threshold breach (6)
  gh_auth          → gh auth failure (5)
  test_file        → test assertion failure (5)

Exit codes:
  0 = no risk detected (or report printed)
  1 = risk detected (patterns found)
  2 = no diff available
`);
    return;
  }

  const diff = getDiff();

  if (!diff || diff.trim() === '') {
    console.error('No diff found. Stage some changes or provide --diff <file>.');
    process.exit(2);
  }

  const { features } = extractFeatures(diff);
  const state = loadState();
  const patterns = loadPatterns();
  const scores = scorePatterns(features, patterns, state);

  const report = formatReport(scores, diff);

  if (!report) {
    console.log('✅ No known CI failure patterns detected in this diff.');
    process.exit(0);
  }

  console.log(report);

  // Exit 1 if high risk
  const top = scores[0];
  if (top.finalScore >= 10) {
    process.exit(1);
  }
  process.exit(0);
}

main().catch(e => { console.error(e); process.exit(1); });
