#!/usr/bin/env node
/**
 * shared/add-seed.mjs
 *
 * Validates and adds a seed to ideas.md pool.
 * All seeds must pass Gate4c validation before being added.
 *
 * Usage:
 *   node shared/add-seed.mjs "seed line text"
 *   node shared/add-seed.mjs --file <path>   # read seeds from file (one per line)
 */
import { readFileSync, appendFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import { extractFirstStep, extractAllSteps, READONLY_PREFIXES, FILE_CREATION_PATTERNS, stepTypeClassification, hasFileCreation } from './step-parser.mjs';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');
const RUN_SEED = join(__DIR, 'run-seed.mjs');

// ── Removed local definitions — now imported from step-parser.mjs ──────────────

// ── Parse seed line ────────────────────────────────────────────────────────────
function parseSeed(line) {
  const headerMatch = line.match(/^- \[(\d{8})\] seed \[brainstorm\] \[score:(\d+x\d+=\d+)\] \[f:(\d+)\] \[angle:([^\]]+)\](?: \[focus:([^\]]+)\])?/);
  if (!headerMatch) return null;

  const [, date, scoreStr, feas, angle, focus] = headerMatch;
  const scoreMatch = scoreStr.match(/(\d+)x(\d+)=(\d+)/);
  const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
  const fscore = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;

  // Extract body fields
  const descMatch = line.match(/^\s*(.+?)(?:\s*\| benefit:|$)/);
  const desc = descMatch ? descMatch[1].trim() : '';

  const bodyMatch = line.match(/\| benefit:\s*(.+?)(?:\s*\| reason:|$)/s);
  const benefit_text = bodyMatch ? bodyMatch[1].trim() : '';

  const reasonMatch = line.match(/\| reason:\s*(.+?)(?:\s*\| approach:|$)/s);
  const reason = reasonMatch ? reasonMatch[1].trim() : '';

  const approachMatch = line.match(/\| approach:\s*(.+?)(?:\s*\| (?:shipped|killed|pending))?$/)
  const approach = approachMatch ? approachMatch[1].trim() : '';

  return { date, benefit, fscore, angle, focus, desc, benefit_text, reason, approach, raw: line };
}

// ── Extract script path and flag from approach ──────────────────────────────────
function extractScriptAndFlag(approach) {
  // Match "node path/to/script.mjs --flag" or "python shared/patch-script.py"
  const nodeMatch = approach.match(/node\s+(\S+\.(?:mjs|js))\s+(--[\w-]+)/);
  const pythonMatch = approach.match(/python\s+(\S+\.py)/);
  if (nodeMatch) return { type: 'node', script: nodeMatch[1], flag: nodeMatch[2] };
  if (pythonMatch) return { type: 'python', script: pythonMatch[1], flag: null };
  return null;
}

// ── Resolve target file path from patch script ─────────────────────────────────
function resolveTargetFile(scriptPath) {
  // Supported formats:
  //   // TARGET: 80-PROJECTS/.../bin/file.mjs
  //   filepath = "80-PROJECTS/.../bin/file.mjs"
  try {
    const content = readFileSync(scriptPath, 'utf-8');
    // Format 1: // TARGET: path/to/file.ext
    const targetMatch = content.match(/\/\/\s*TARGET:\s*([^\s]+)/);
    if (targetMatch) return targetMatch[1];
    // Format 2: filepath = "path/to/file.ext"
    const fpMatch = content.match(/filepath\s*=\s*["']([^"']+)["']/);
    if (fpMatch) return fpMatch[1];
  } catch (e) { /* ignore */ }
  return null;
}

// ── Pre-check: verify flag doesn't already exist ─────────────────────────────
function preCheckFeature(approach) {
  const info = extractScriptAndFlag(approach);
  if (!info || !info.flag) return { pass: true };

  const scriptPath = join(__DIR, '..', info.script);
  if (!existsSync(scriptPath)) return { pass: true }; // script doesn't exist yet

  // For patch scripts: resolve target file and grep for flag keyword directly
  const isPatchScript = info.script.includes('patch-') || info.script.includes('Patch');
  if (isPatchScript && info.type === 'node') {
    const targetFile = resolveTargetFile(scriptPath);
    if (targetFile) {
      const fullTargetPath = join(__DIR, '..', targetFile);
      if (existsSync(fullTargetPath)) {
        try {
          const targetContent = readFileSync(fullTargetPath, 'utf-8');
          // Strip common prefixes from flag: --dot → dot, --json → json
          const flagKeyword = info.flag.replace(/^--/, '');
          // Use word boundary to avoid false matches like "dotfile" matching "dot"
          const flagRe = new RegExp(`\\b${flagKeyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?=\\s|[;,\\)]|$)`, 'i');
          if (flagRe.test(targetContent)) {
            return {
              pass: false,
              error: `[PRECHECK] Flag '${info.flag}' already present in target '${targetFile}' — patch already applied`
            };
          }
        } catch (e) { /* ignore */ }
      }
    }
  }

  // For other scripts: run baseline vs flag comparison
  if (info.type !== 'node') return { pass: true };

  try {
    // Run WITHOUT flag first to get baseline output
    const baselineCmd = `node "${scriptPath}" 2>&1`;
    let baselineOutput = '';
    let baselineExit = 0;
    try {
      baselineOutput = execSync(baselineCmd, { cwd: join(__DIR, '..'), stdio: 'pipe', timeout: 5000 }).toString();
    } catch (e) {
      baselineOutput = e.stdout ? e.stdout.toString() : (e.stderr ? e.stderr.toString() : '');
      baselineExit = e.status || 1;
    }

    // Run WITH flag
    const flagCmd = `node "${scriptPath}" ${info.flag} 2>&1`;
    let flagOutput = '';
    let flagExit = 0;
    try {
      flagOutput = execSync(flagCmd, { cwd: join(__DIR, '..'), stdio: 'pipe', timeout: 5000 }).toString();
    } catch (e) {
      flagOutput = e.stdout ? e.stdout.toString() : (e.stderr ? e.stderr.toString() : '');
      flagExit = e.status || 1;
    }

    // Check for "unknown option" error patterns in flag output
    const unknownPatterns = ['unknown option', 'not recognized', 'invalid option', 'unrecognized flag', 'not a valid option'];
    const hasUnknownError = unknownPatterns.some(p => flagOutput.toLowerCase().includes(p));

    if (hasUnknownError) {
      // Flag not recognized — feature doesn't exist yet, pre-check passes
      return { pass: true };
    }

    // Compare outputs: if flag output differs from baseline, the flag actually does something
    const outputsDiffer = flagOutput !== baselineOutput || flagExit !== baselineExit;

    if (!outputsDiffer) {
      // No output change and no unknown-option error → flag exists but does nothing new
      return {
        pass: false,
        error: `[PRECHECK] Flag '${info.flag}' already exists in '${info.script}' but produces identical output — duplicate seed`
      };
    }
  } catch (e) {
    // execSync error — flag likely doesn't exist, which is what we want
  }
  return { pass: true };
}

// ── Validate approach step 1 ───────────────────────────────────────────────────
function validateApproach(approach) {
  // Extract first step using shared parser
  const parsed = extractFirstStep(approach);
  if (!parsed) {
    return { pass: false, error: 'No numbered step found in approach' };
  }
  const stepNum = parsed.stepNum;
  const firstStep = parsed.firstStep;

  // Gate 4b-adjacent: use stepTypeClassification for precise error messages
  const classification = stepTypeClassification(firstStep);

  if (classification.type === 'READONLY' && !hasFileCreation(approach)) {
    // Build specific error with the detected command
    const cmdMatch = firstStep.match(/^(\S+)/);
    const cmd = cmdMatch ? cmdMatch[1] : firstStep.slice(0, 20);
    return {
      pass: false,
      error: `[Gate 4b-adjacent] step1 '${cmd}' is read-only — no file creation in step2+. Use IMPLEMENT prefix instead: (1) python shared/patch-xxx.py (2) Edit path/to/file.mjs (3) Write path/to/file.mjs content`
    };
  }

  if (classification.dangerous) {
    const { name, alt } = classification.dangerous;
    const cmdMatch = firstStep.match(/^(\S+)/);
    const cmd = cmdMatch ? cmdMatch[1] : firstStep.slice(0, 20);
    return {
      pass: false,
      error: `[Gate 4b] step1 uses dangerous pattern '${name}' — ${alt}. Detected in: '${cmd}'`
    };
  }

  // Extract reason for consistency check
  const reasonMatch = approach.match(/\| reason:\s*(.+?)(?:\s*\| approach:|$)/s);
  const reason = reasonMatch ? reasonMatch[1].trim() : '';

  // Call run-seed validation
  try {
    const validationCmd = `node "${RUN_SEED}" --validate-approach "${approach.replace(/"/g, '\\"')}" --reason "${reason.replace(/"/g, '\\"')}"`;
    execSync(validationCmd, { cwd: join(__DIR, '..'), stdio: 'pipe' });
  } catch (e) {
    const output = e.stdout ? e.stdout.toString() : e.stderr ? e.stderr.toString() : '';
    return { pass: false, error: output.trim() };
  }

  // Pre-check: verify flag doesn't already exist
  const preCheck = preCheckFeature(approach);
  if (!preCheck.pass) return preCheck;

  return { pass: true };
}

// ── Main ─────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage:`);
  console.log(`  node shared/add-seed.mjs "<seed line>"`);
  console.log(`  node shared/add-seed.mjs --file <path>   # one seed per line`);
  console.log(`  node shared/add-seed.mjs --dry-run "<seed line>"   # validate without writing`);
  console.log(``);
  console.log(`Examples:`);
  console.log(`  node shared/add-seed.mjs "- [20260411] seed [brainstorm] [score:3x3=9] [f:3] [angle:ws-level] description | benefit: ... | reason: ... | approach: 1. node script.mjs --flag"`);
  console.log(`  node shared/add-seed.mjs --dry-run "..."    # test validation without adding to pool`);
  process.exit(0);
}

const dryRun = args.includes('--dry-run') || args.includes('-n');
if (dryRun) {
  console.log('[DRY RUN] Validation only — no changes will be written\n');
}

if (args.includes('--file')) {
  const fileIdx = args.indexOf('--file');
  const filePath = args[fileIdx + 1];
  if (!filePath) {
    console.error('[ERROR] --file requires a path argument');
    process.exit(1);
  }
  const content = readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
  console.log(`Processing ${lines.length} seed(s) from ${filePath}...`);
  let added = 0, skipped = 0;
  for (const line of lines) {
    const seed = parseSeed(line);
    if (!seed) {
      console.error(`[SKIP] Could not parse: ${line.slice(0, 60)}...`);
      skipped++;
      continue;
    }
    if (!seed.approach) {
      console.error(`[SKIP] No approach found: ${line.slice(0, 60)}...`);
      skipped++;
      continue;
    }
    const validation = validateApproach(seed.approach);
    if (!validation.pass) {
      console.error(`[FAIL] Validation failed for: ${seed.desc.slice(0, 50)}`);
      console.error(`       Error: ${validation.error}`);
      skipped++;
      continue;
    }
    // Append with pending tag (skip if dry-run)
    if (!dryRun) {
      const pendingLine = line.replace(/\s*\|\s*(shipped|killed|pending).*$/, '') + ' | pending\n';
      appendFileSync(IDEAS_PATH, pendingLine);
    }
    console.log(`[OK] ${dryRun ? '(dry-run) ' : ''}Added (pending): ${seed.desc.slice(0, 50)}`);
    added++;
  }
  console.log(`\nDone: ${added} added, ${skipped} skipped${dryRun ? ' (dry-run)' : ''}`);
  process.exit(skipped > 0 && !dryRun ? 1 : 0);
}

// Single seed mode (strip --dry-run/-n from args before joining)
const seedLine = args.filter(a => a !== '--dry-run' && a !== '-n').join(' ');
if (!seedLine) {
  console.error('[ERROR] No seed line provided. Use --help for usage.');
  process.exit(1);
}

const seed = parseSeed(seedLine);
if (!seed) {
  console.error('[ERROR] Could not parse seed line. Check format.');
  console.error('Expected format: - [YYYYMMDD] seed [brainstorm] [score:BxF] [f:N] [angle:X] description | benefit: ... | reason: ... | approach: 1. ...');
  process.exit(1);
}

console.log(`Seed: ${seed.desc}`);
console.log(`Score: ${seed.benefit}x${seed.fscore} | Angle: ${seed.angle} | Focus: ${seed.focus || 'none'}`);

// Validate approach
if (!seed.approach) {
  console.error('[ERROR] No approach found in seed line');
  process.exit(1);
}

console.log('\nValidating approach...');
const validation = validateApproach(seed.approach);
if (!validation.pass) {
  console.error(`[FAIL] Approach validation failed:`);
  console.error(`  ${validation.error}`);
  process.exit(1);
}

console.log('[PASS] Approach validation passed');

// Append to ideas.md with pending tag (skip if dry-run)
if (!dryRun) {
  const pendingLine = seedLine.replace(/\s*\|\s*(shipped|killed|pending).*$/, '') + ' | pending\n';
  appendFileSync(IDEAS_PATH, pendingLine);
  console.log(`\n[OK] Seed added with | pending tag`);
  console.log(`    → Run: node shared/run-seed.mjs --list-pending`);
  console.log(`    → Approve: node shared/run-seed.mjs --approve <lineidx>`);
} else {
  console.log(`\n[DRY RUN] Seed NOT written to pool`);
}
