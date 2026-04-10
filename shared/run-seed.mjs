#!/usr/bin/env node
/**
 * shared/run-seed.mjs
 *
 * Scans ideas.md pool, picks the highest-score unshipped seed,
 * executes its approach's first step, then marks it shipped.
 *
 * Usage:
 *   node run-seed.mjs [--dry-run] [--limit N] [--focus PROJECT] [--skip LINEIDX] [--warm-all]
 *   node run-seed.mjs --validate-approach "1. python wiki.mjs --rebuild"
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

const dryRun = process.argv.includes('--dry-run');
const verboseMode = process.argv.includes('--verbose');
const validateApproachIdx = process.argv.indexOf('--validate-approach');
const validateApproach = validateApproachIdx !== -1 ? process.argv[validateApproachIdx + 1] : null;
const reasonIdx = process.argv.indexOf('--reason');
const reasonText = reasonIdx !== -1 ? process.argv[reasonIdx + 1] : null;
const limitIdx = process.argv.indexOf('--limit');
const showLimit = limitIdx !== -1 ? parseInt(process.argv[limitIdx + 1], 10) : 1;
const focusIdx = process.argv.indexOf('--focus');
const focusProject = focusIdx !== -1 ? process.argv[focusIdx + 1] : null;
const skipIdxs = process.argv.includes('--skip')
  ? (() => { const i = process.argv.indexOf('--skip') + 1; return process.argv.slice(i, i + 2).map(n => parseInt(n, 10)).filter(n => !isNaN(n)); })()
  : [];
const warmAll = process.argv.includes('--warm-all');
const explainMode = process.argv.includes('--explain');
const quickMode = process.argv.includes('--quick');

// ── Gate 4c: Validate approach text without writing to pool ────────────────────
if (validateApproach !== null) {
  // Extract first step from approach text (shared logic with main flow)
  const firstStepMatch = validateApproach.match(/(?:^|\n)\s*(\d+)\.\s+(.+?)(?:\n\s*\d+\.|[；;]\d+\.|$)/s);
  if (!firstStepMatch) {
    console.error('[VALIDATE] FAIL: No numbered step found in approach');
    process.exit(1);
  }
  const stepNum = firstStepMatch[1];
  let firstStep = firstStepMatch[2].replace(/[；;]$/, '').trim();

  // Check for tool-name prefixes (Edit/Read/Grep etc.) — these require Claude Code
  const TOOL_PREFIXES = ['Edit ', 'Read ', 'Write ', 'Grep ', 'Glob ', 'Bash ', 'Search ', 'List ', 'Delete ', 'Create '];
  const isToolCommand = TOOL_PREFIXES.some(p => firstStep.startsWith(p));
  if (isToolCommand) {
    console.error(`[VALIDATE] FAIL: approach step is a tool-name command (requires Claude Code): ${firstStep}`);
    process.exit(1);
  }

  // Check for node -e/p/c inline (node --version is valid, node -e/p/c is not)
  if (/^node\s+-[epc]\s+/i.test(firstStep)) {
    console.error(`[VALIDATE] FAIL: "node -e/p/c" inline code is not allowed — Windows shell corrupts quotes/newlines: ${firstStep.slice(0, 60)}`);
    process.exit(1);
  }
  const DANGEROUS_COMMAND_BLACKLIST = [
    { pattern: /python\s+-c\s+["'][\s\S]+["']/i, name: 'python -c inline code' },
    { pattern: /node\s+-[epc]\s+/i, name: 'node -e/p/c inline' },
    { pattern: /bash\s+-c\s+["'][\s\S]+["']/i, name: 'bash -c inline code' },
  ];
  const isDangerousCommand = DANGEROUS_COMMAND_BLACKLIST.some(d => d.pattern.test(firstStep));
  if (isDangerousCommand) {
    console.error(`[Gate4b FAIL] Dangerous command pattern detected: ${firstStep.slice(0, 60)}`);
    process.exit(1);
  }
  const EXEC_PREFIXES = ['python ', 'bash ', 'sh ', 'cd ', 'mkdir ', '//', '#', '/', 'echo '];
  const isExecCommand = EXEC_PREFIXES.some(p => firstStep.startsWith(p)) || firstStep.match(/^[a-zA-Z]:\\/);
  // node allowed as "node xxx.mjs", "node xxx.js", or "node --version" etc. (built-in flags)
  const isNodeScript = firstStep.match(/^node \S+\.(mjs|js)(\s|$)/) || firstStep.match(/^node\s+--/);
  if (!isExecCommand && !isNodeScript) {
    console.error(`[VALIDATE] FAIL: approach step has no executable prefix: ${firstStep}`);
    process.exit(1);
  }

  // Check for script-name pattern that can be resolved
  const nodeScriptMatch = firstStep.match(/^node\s+(\S+\.(?:mjs|js))\b/i);
  const pythonScriptMatch = firstStep.match(/^python\s+(\S+\.(?:py))\b/i);

  if (nodeScriptMatch || pythonScriptMatch) {
    const scriptName = (nodeScriptMatch || pythonScriptMatch)[1];
    const scriptPath = join(__DIR, '..', scriptName);
    if (!existsSync(scriptPath)) {
      console.error(`[VALIDATE] FAIL: script does not exist: ${scriptPath}`);
      process.exit(1);
    }
  }

  if (!firstStep.startsWith('python ') && !firstStep.startsWith('bash ') && !firstStep.startsWith('sh ') &&
      !firstStep.startsWith('cd ') && !firstStep.startsWith('mkdir ') && !firstStep.startsWith('#') &&
      !firstStep.startsWith('/') && !firstStep.match(/^[a-zA-Z]:\\/) && !nodeScriptMatch && !pythonScriptMatch &&
      !firstStep.match(/^node\s+--/) && !firstStep.startsWith('echo ')) {
    // Script-name based step — check if scriptMeta can resolve it
    const scriptMatch = validateApproach.match(/(?:^|\s)([\w-]+\.(?:py|mjs|js|ts|sh))(?:[\s\[]|$)/);
    if (!scriptMatch) {
      console.error(`[VALIDATE] FAIL: cannot resolve script name from: ${firstStep}`);
      process.exit(1);
    }
  }

  // ── Gate 4c supplement: approach vs reason consistency check ──
  if (reasonText !== null) {
    // Patterns that signal new implementation (not just testing/validation)
    const IMPLEMENT_PATTERNS = [
      /增加/, /新增/, /集成/, /打通/, /创建/, /写入/, /编写/,
      /集成到/, /接入/, /固化为/, /生成/, /实现/, /添加/,
      /^无/, /缺失环节[：:]/,
    ];
    const IS_IMPLEMENT = IMPLEMENT_PATTERNS.some(p => p.test(reasonText));
    // Patterns that signal testing/validation only (echo is OK for these)
    const IS_TEST_PATTERNS = [
      /测试/, /验证/, /检查/, /分析/, /巡检/, /诊断/, /echo/,
      /去重分析/, /根因分析/, /反思/,
    ];
    const IS_TEST = IS_TEST_PATTERNS.some(p => p.test(reasonText));

    // echo-only approach for implement-type seeds = approach drift
    if (IS_IMPLEMENT && !IS_TEST && /^echo\s/i.test(firstStep)) {
      console.error(`[VALIDATE] FAIL: approach drift — reason describes new implementation but approach is just "echo": ${reasonText.slice(0, 60)}`);
      process.exit(1);
    }
    // purely testing approach for implement-type seeds = likely too shallow
    if (IS_IMPLEMENT && !IS_TEST) {
      const SHALLOW_PATTERNS = [
        /^node\s+\S+\.mjs\s+--\w+\s*$/,  // just runs --help/--version with no args
        /^node\s+shared\/run-seed\.mjs\s+--validate-approach/,
      ];
      if (SHALLOW_PATTERNS.some(p => p.test(firstStep))) {
        console.error(`[VALIDATE] FAIL: approach drift — reason describes new implementation but approach only runs validation: ${firstStep}`);
        process.exit(1);
      }
    }
  }

  console.log(`[VALIDATE] PASS: approach step ${stepNum} is executable — ${firstStep.slice(0, 80)}`);
  process.exit(0);
}

// ── Dry-run: validate ALL numbered steps in approach ─────────────────────────
if (dryRun) {
  // Extract all numbered steps from the full approach text
  const approachIdx = process.argv.indexOf('--dry-run');
  const approachText = approachIdx !== -1 ? process.argv[approachIdx + 1] || '' : '';
  if (!approachText) {
    console.error('[DRY-RUN] No approach text provided after --dry-run');
    process.exit(1);
  }
  const stepMatches = [...approachText.matchAll(/^\s*(\d+)\.\s+(.+)/gm)];
  if (stepMatches.length === 0) {
    console.error('[DRY-RUN] No numbered steps found in approach');
    process.exit(1);
  }
  let pass = 0, fail = 0;
  for (const m of stepMatches) {
    const stepNum = m[1], stepText = m[2].trim();
    // Reuse the same validation logic for each step
    const firstStep = stepText;
    const TOOL_PREFIXES = ['Edit ', 'Read ', 'Write ', 'Grep ', 'Glob ', 'Bash ', 'Search ', 'List ', 'Delete ', 'Create '];
    if (TOOL_PREFIXES.some(p => firstStep.startsWith(p))) {
      console.error(`[DRY-RUN] FAIL step ${stepNum}: tool-name command (requires Claude Code): ${firstStep.slice(0, 60)}`);
      fail++; continue;
    }
    if (/^node\s+-[epc]\s+/i.test(firstStep)) {
      console.error(`[DRY-RUN] FAIL step ${stepNum}: node -e/p/c not allowed`);
      fail++; continue;
    }
    const EXEC_PREFIXES = ['python ', 'bash ', 'sh ', 'cd ', 'mkdir ', '//', '#', '/', 'echo '];
    const isExecCommand = EXEC_PREFIXES.some(p => firstStep.startsWith(p)) || firstStep.match(/^[a-zA-Z]:\\/);
    const isNodeScript = firstStep.match(/^node \S+\.(mjs|js)(\s|$)/) || firstStep.match(/^node\s+--/);
    if (!isExecCommand && !isNodeScript) {
      console.error(`[DRY-RUN] FAIL step ${stepNum}: no executable prefix: ${firstStep.slice(0, 60)}`);
      fail++; continue;
    }
    // Check script path
    const nodeScriptMatch = firstStep.match(/^node\s+(\S+\.(?:mjs|js))\b/i);
    const pythonScriptMatch = firstStep.match(/^python\s+(\S+\.(?:py))\b/i);
    if (nodeScriptMatch || pythonScriptMatch) {
      const scriptName = (nodeScriptMatch || pythonScriptMatch)[1];
      const scriptPath = join(__DIR, '..', scriptName);
      if (!existsSync(scriptPath)) {
        console.error(`[DRY-RUN] FAIL step ${stepNum}: script does not exist: ${scriptPath}`);
        fail++; continue;
      }
    }
    console.log(`[DRY-RUN] PASS step ${stepNum}: ${firstStep.slice(0, 80)}`);
    pass++;
  }
  console.log(`[DRY-RUN] Summary: ${pass} passed, ${fail} failed`);
  process.exit(fail > 0 ? 1 : 0);
}

// ── Parse ideas.md ───────────────────────────────────────────────────────────
const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const results = [];

let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const headerMatch = line.match(/^- \[(\d{8})\] seed \[brainstorm\] \[score:(\d+x\d+=\d+)\] \[f:(\d+)\] \[angle:([^\]]+)\](?: \[focus:([^\]]+)\])?/);
  if (!headerMatch) { i++; continue; }

  const [, date, scoreStr, feasEntry, angle, focus] = headerMatch;
  // scoreStr format: "3x4=12"
  const scoreMatch = scoreStr.match(/(\d+)x(\d+)=(\d+)/);
  const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
  const feas = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;
  const score = scoreMatch ? parseInt(scoreMatch[3], 10) : 0;

  // Collect continuation lines (indented lines following header)
  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) {
    bodyLines.push(lines[j].replace(/^\s{2}/, ''));
    j++;
  }
  const bodyText = bodyLines.join('\n');

  // Check shipped — tag can be in header line or body; also check for killed
  const shippedMatch = line.match(/\| shipped:(\d{8})/) || bodyText.match(/\| shipped:(\d{8})/);
  const killedMatch = line.match(/killed:(\d{8})/) || bodyText.match(/killed:(\d{8})/);
  const shipped = !!shippedMatch;
  const killed = !!killedMatch;

  // Extract description — try body first, then fall back to header line (no "description:" prefix)
  const descMatch = bodyText.match(/description:\s*(.+?)(?:\s*\| benefit:|$)/s);
  const desc = descMatch ? descMatch[1].trim() : line.replace(/^\s*/, '').split('|')[0].trim();

  // Extract approach (numbered steps) — from body or fallback to header line
  const approachMatch = bodyText.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|$)/s)
    || line.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|$)/s);
  const approachText = approachMatch ? approachMatch[1].trim() : '';
  const reasonMatch = bodyText.match(/\| reason:\s*(.+?)(?:\s*\| approach:|$)/s)
    || line.match(/\| reason:\s*(.+?)(?:\s*\| approach:|$)/);
  const reason = reasonMatch ? reasonMatch[1].trim() : '';

  results.push({ date, score, benefit, feas, feasEntry, angle, focus, shipped, killed, desc, approachText, reason, lineIdx: i, bodyLines });

  i = j;
}

const angleIdx = process.argv.indexOf('--filter-angle');
const filterAngle = angleIdx !== -1 ? process.argv[angleIdx + 1] : null;

const unshipped = results
  .filter(s => !s.shipped && !s.killed)
  .filter(s => !focusProject || s.focus === focusProject)
  .filter(s => !filterAngle || s.angle === filterAngle)
  .filter(s => skipIdxs.length === 0 || !skipIdxs.includes(s.lineIdx))
  .sort((a, b) => {
    // Bonus for high-complexity seeds (f:1, f:2) to prevent them being buried by easy f:4/f:5
    const feasBonus = (s) => s.feas <= 1 ? 15 : s.feas <= 2 ? 8 : 0;
    return (b.score + feasBonus(b)) - (a.score + feasBonus(a));
  });

console.log(`\n=== Seed Runner ===`);
console.log(`Total seeds: ${results.length} | Unshipped: ${unshipped.length}${focusProject ? ` | focus: ${focusProject}` : ''}${filterAngle ? ` | angle: ${filterAngle}` : ''}`);
console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'}${quickMode ? ' (QUICK)' : ''}`);
console.log('');

if (unshipped.length === 0) {
  console.log('[OK] No unshipped seeds found.');
  console.log('  → Run: node shared/brainstorm-next-seed.mjs --auto   # generate from metacognition');
  console.log('  → Or: brainstorm new seeds manually');
  process.exit(0);
}

if (showLimit > 1) {
  console.log(`Top ${showLimit} unshipped seeds:`);
  for (const s of unshipped.slice(0, showLimit)) {
    console.log(`  [score:${s.score}] f:${s.feas} angle:${s.angle} | ${s.desc.slice(0, 60)}`);
  }
  process.exit(0);
}

if (warmAll) {
  console.log(`\n=== Warm Pool — All Candidates (${unshipped.length}) ===\n`);
  for (let i = 0; i < unshipped.length; i++) {
    const s = unshipped[i];
    console.log(`  ${String(i + 1).padStart(2)}. [score:${s.score}] f:${s.feas} [${s.angle || 'none'}]${s.focus ? ` focus:${s.focus}` : ''} ${s.desc.slice(0, 55)}`);
  }
  process.exit(0);
}

if (quickMode) {
  // Skip --quick/-skip seed itself to prevent infinite recursion
  const skipIdx = unshipped.findIndex(s =>
    s.approachText.includes('run-seed.mjs --quick') ||
    s.approachText.includes('run-seed.mjs --skip')
  );
  let top;
  if (skipIdx === 0) {
    top = unshipped.length > 1 ? unshipped[1] : unshipped[0];
  } else if (skipIdx > 0) {
    top = unshipped[skipIdx - 1];
  } else {
    top = unshipped[0];
  }
  const firstStepMatch = top.approachText.match(/(?:^|\n)\s*(\d+)\.\s+(.+?)(?:\n\s*\d+\.|[；;]\d+\.|$)/s);
  if (!firstStepMatch) { console.error('[ERROR] No numbered step'); process.exit(1); }
  const firstStep = firstStepMatch[2].replace(/[；;]$/, '').trim();
  console.log(`[QUICK] Executing: ${firstStep}`);
  const { execSync } = await import('child_process');
  try {
    execSync(firstStep, { cwd: join(__DIR, '..'), stdio: 'inherit', timeout: 120_000 });
  } catch (e) { process.exit(e.status ?? 1); }
  // mark shipped
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const lines = readFileSync(IDEAS_PATH, 'utf-8').split('\n');
  const newLines = [...lines];
  const lastBodyIdx = top.lineIdx + top.bodyLines.length;
  newLines[lastBodyIdx] = newLines[lastBodyIdx].replace(/(\s*)$/, ` | shipped:${today}`);
  writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
  console.log(`[SHIPPED] ${top.desc.slice(0, 60)}...`);
  process.exit(0);
}

const top = unshipped[0];
// Default cwd; script resolution may override
let execCwd = join(__DIR, '..');

if (explainMode) {
  console.log(`\n=== Seed Explanation ===`);
  console.log(`  description: ${top.desc}`);
  console.log(`  score: ${top.score} = Benefit(${top.benefit}) × Feasibility(${top.feas})`);
  console.log(`  angle: ${top.angle} | focus: ${top.focus || 'none'}`);
  const bodyLines = top.bodyLines.join('\n');
  const benefitMatch = bodyLines.match(/benefit:\s*(.+?)(?:\s*\| reason:|$)/s);
  const reasonMatch = bodyLines.match(/reason:\s*(.+?)(?:\s*\| approach:|$)/s);
  if (benefitMatch) console.log(`  benefit src: ${benefitMatch[1].trim().slice(0, 80)}`);
  if (reasonMatch) {
    const reason = reasonMatch[1].trim();
    // Highlight the three-part structure
    const hasResources = reason.includes('已知资源');
    const hasGap = reason.includes('缺失环节');
    const hasConnection = reason.includes('连接方式');
    console.log(`  reason structure: 已知资源=${hasResources ? '✓' : '✗'} 缺失环节=${hasGap ? '✓' : '✗'} 连接方式=${hasConnection ? '✓' : '✗'}`);
  }
  console.log(`  approach step 1: ${top.approachText.split('\n')[0].trim().slice(0, 80)}`);
  console.log(`\n=== End Explanation ===\n`);
  process.exit(0);
}

console.log(`Top seed: score:${top.score} f:${top.feas} angle:${top.angle}`);
console.log(`  ${top.desc}`);
console.log(`  approach: ${top.approachText.slice(0, 80)}...`);

// Extract first numbered step from approach
// Handle both "1. Do X" and "1. Do X；2. Do Y" (semicolon-separated compound steps)
const firstStepMatch = top.approachText.match(/(?:^|\n)\s*(\d+)\.\s+(.+?)(?:\n\s*\d+\.|[；;]\d+\.|$)/s);
if (!firstStepMatch) {
  console.error('[ERROR] No numbered step found in approach');
  process.exit(1);
}
const stepNum = firstStepMatch[1];
let firstStep = firstStepMatch[2].replace(/[；;]$/, '').trim();

// If firstStep contains no path separators or shebang, it's a description —
// try to find the script name in description and build the actual command
if (!firstStep.startsWith('python ') && !firstStep.startsWith('node ') && !firstStep.startsWith('npx ') && !firstStep.startsWith('#') && !firstStep.startsWith('/') && !firstStep.startsWith('Edit ') && !firstStep.startsWith('Read ') && !firstStep.startsWith('Write ') && !firstStep.startsWith('Create ') && !firstStep.startsWith('Delete ') && !firstStep.startsWith('Grep ') && !firstStep.startsWith('Glob ') && !firstStep.startsWith('Bash ') && !firstStep.startsWith('Search ') && !firstStep.startsWith('List ') && !firstStep.match(/^[a-zA-Z]:\\/)) {
  // Extract script name (e.g. "package_videos.py 添加 --all" → "video/package_videos.py")
  const scriptMatch = top.desc.match(/(?:^|\s)([\w-]+\.(?:py|mjs|js|ts|sh))(?:[\s\[]|$)/);
  if (scriptMatch) {
    const scriptName = scriptMatch[1];
    // Map script name → {path, projectRoot}
    const scriptMeta = {
      'package_videos.py': { path: 'video/package_videos.py', project: 'wikipedia' },
      'check_script.py':   { path: 'video/check_script.py',     project: 'wikipedia' },
      'draw_scene.py':      { path: 'video/draw_scene.py',       project: 'wikipedia' },
      'generate_speech.py': { path: 'video/generate_speech.py',   project: 'wikipedia' },
      'make_video.py':      { path: 'video/make_video.py',       project: 'wikipedia' },
      'wiki.mjs':           { path: 'wiki.mjs',                  project: 'wikipedia' },
      'check-deps.mjs':     { path: 'check-deps.mjs',            project: null },
      'video-editors.mjs':  { path: 'video-editors.mjs',         project: null },
      'wiki-indexer.mjs':   { path: 'wiki-indexer.mjs',          project: null },
      'video-quality-check.mjs': { path: 'video-quality-check.mjs', project: null },
    };
    const meta = scriptMeta[scriptName];
    if (meta) {
      const flagsMatch = firstStep.match(/--?[\w-]+/g);
      const flags = flagsMatch ? flagsMatch.join(' ') : '';
      const isPython = scriptName.endsWith('.py');
      firstStep = isPython ? `python ${meta.path} ${flags}` : `node ${meta.path} ${flags}`;
      firstStep = firstStep.trim();
      if (meta.project === 'wikipedia') {
        execCwd = join(__DIR, '..', 'knowledge', 'wikipedia');
      }
    }
  }
}
const TOOL_PREFIXES = ['Edit ', 'Read ', 'Write ', 'Grep ', 'Glob ', 'Bash ', 'Search ', 'List ', 'Delete ', 'Create '];
const isToolCommand = TOOL_PREFIXES.some(p => firstStep.startsWith(p));

if (isToolCommand) {
  // Tool-name step requires Claude Code to execute — output as next-session instruction
  console.log(`\n[TOOL STEP] Seed requires Claude Code to execute:`);
  console.log(`  ${firstStep}`);
  console.log(`\n  → Execute this step manually, then run:`);
  console.log(`    node ${join(__DIR, 'run-seed.mjs')} --skip ${top.lineIdx + 1}`);
  console.log(`  to mark shipped and continue.\n`);
  process.exit(0);
}

// Gate4c: validate approach before executing (Windows bash compatibility check)
if (firstStep.startsWith('node -')) {
  console.error(`\n[Gate4c FAIL] "node -e/p/c" inline code not allowed on Windows Git Bash:`);
  console.error(`  ${firstStep.slice(0, 80)}`);
  // Skip this seed and pick the next one
  console.error(`Skipping seed, picking next...`);
  // Mark current as killed and pick next
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const newLines = [...lines];
  const lastBodyIdx = top.lineIdx + top.bodyLines.length;
  const lastBodyLine = newLines[lastBodyIdx];
  newLines[lastBodyIdx] = lastBodyLine.replace(/(\s*)$/, ` | killed:${today} Gate4c: node -e blocked`);
  writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
  console.log(`[KILLED] ${top.desc.slice(0, 60)}...`);
  // Re-run to pick next seed
  process.exit(2); // 2 = skip and continue
}

// Gate4c consistency: echo approach + implement-type reason = kill (not shipped)
const IMPL_PATTERNS_EXEC = [/增加/, /新增/, /集成/, /打通/, /创建/, /写入/, /编写/, /集成到/, /接入/, /固化为/, /生成/, /实现/, /添加/, /^无/, /缺失环节[：:]/];
const TEST_PATTERNS_EXEC = [/测试/, /验证/, /检查/, /分析/, /巡检/, /诊断/, /去重分析/, /根因分析/, /反思/];
const reasonForCheck = top.reason || '';
const isImplReason = IMPL_PATTERNS_EXEC.some(p => p.test(reasonForCheck)) && !TEST_PATTERNS_EXEC.some(p => p.test(reasonForCheck));
if (isImplReason && /^echo\s/i.test(firstStep)) {
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const newLines = [...lines];
  const lastBodyIdx = top.lineIdx + top.bodyLines.length;
  const lastBodyLine = newLines[lastBodyIdx];
  newLines[lastBodyIdx] = lastBodyLine.replace(/(\s*)$/, ` | killed:${today} approach_drift: echo approach for implement-type seed`);
  writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
  console.log(`[KILLED] approach_drift: echo approach for implement-type seed`);
  process.exit(2);
}

console.log(`\n[ACTION] ${dryRun ? 'Would execute step ' + stepNum + ': ' : 'Executing step ' + stepNum + ': '}${firstStep}`);

if (dryRun) {
  console.log(`[DRY] Seed "${top.desc.slice(0, 60)}..." validated — would execute: ${firstStep}`);
  process.exit(0);
}

// ── Execute ──────────────────────────────────────────────────────────────────
const { execSync } = await import('child_process');

if (verboseMode) {
  console.log(`\n[VERBOSE] Executing seed step:`);
  console.log(`  cwd: ${execCwd}`);
  console.log(`  command: ${firstStep}`);
  console.log(`  timeout: 120000ms`);
  console.log('');
}

try {
  const startTime = Date.now();
  execSync(firstStep, {
    cwd: execCwd,
    stdio: 'inherit',
    timeout: 120_000,
  });
  if (verboseMode) {
    console.log(`\n[VERBOSE] Step completed in ${Date.now() - startTime}ms`);
  }
} catch (err) {
  const stderr = err.stderr ? err.stderr.toString() : '';
  const stdout = err.stdout ? err.stdout.toString() : '';
  const output = stderr + stdout;
  if (output.includes('ALREADY APPLIED')) {
    // Patch was already applied — mark shipped and continue
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const newLines = [...lines];
    const lastBodyIdx = top.lineIdx + top.bodyLines.length;
    const lastBodyLine = newLines[lastBodyIdx];
    if (!lastBodyLine.match(/\| shipped:/)) {
      newLines[lastBodyIdx] = lastBodyLine.replace(/(\s*)$/, ` | shipped:${today}`);
      writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
    }
    console.log(`\n[SHIPPED] ${top.desc.slice(0, 60)}... → shipped:${today} (ALREADY APPLIED)`);
    process.exit(0);
  }
  console.error(`\n[ERROR] Command failed (exit ${err.status})`);
  console.error(`Seed NOT marked shipped.`);
  process.exit(err.status ?? 1);
}

// ── Mark shipped ─────────────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
const newLines = [...lines];

// Append "| shipped:YYYYMMDD" to the last body line of the seed
const lastBodyIdx = top.lineIdx + top.bodyLines.length;
const lastBodyLine = newLines[lastBodyIdx];
if (lastBodyLine.match(/\| shipped:/)) {
  // Already shipped (race condition check)
  console.log(`\n[SKIP] Seed already shipped.`);
  process.exit(0);
}
newLines[lastBodyIdx] = lastBodyLine.replace(/(\s*)$/, ` | shipped:${today}`);

if (!dryRun) {
  writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
  console.log(`\n[SHIPPED] ${top.desc.slice(0, 60)}... → shipped:${today}`);
} else {
  console.log('\n[DRY RUN] Would write shipped marker (not written)');
}

// Self-critique: mandatory 3 questions after shipped
console.log('\n=== Seed Self-Critique ===');
console.log('Q1 reason准确吗？已知资源/缺失环节/连接方式与实际一致？');
console.log('Q2 approach描述好吗？步骤与实际执行路径匹配？');
console.log('Q3 score虚高了吗？f:评分与实际耗时匹配？');
console.log('→ 将答案追加到 brainstorm-metacognition.jsonl seed_critiques 字段');
console.log('');

// Auto-generate insight: write to trigger file after each shipped seed
try {
  const { writeFileSync: wf, existsSync: ex } = await import('fs');
  const { join: j2, dirname: dn2 } = await import('path');
  const { fileURLToPath: fu2 } = await import('url');
  const stateDir = dn2(fu2(import.meta.url)) + '/../.omc/state';
  const triggerFile = j2(stateDir, 'auto-insight-trigger.json');
  const trigger = {
    sessionId: String(Date.now()),
    work: { tool: 'seed-shipped', input: { seed: top.desc.slice(0, 80), score: top.score, angle: top.angle, focus: top.focus } },
    prompt: `从 seed 执行经验生成 insight：${top.desc.slice(0, 60)} | angle:${top.angle} | score:${top.score}`,
    triggeredAt: new Date().toISOString(),
  };
  wf(triggerFile, JSON.stringify(trigger, null, 2), 'utf-8');
  console.log(`[INSIGHT] Generated trigger: ${triggerFile}`);
} catch (e) {
  console.error(`[INSIGHT] Warning: could not generate trigger: ${e.message}`);
}

// Auto-skillify: if angle contains 'skill-file', generate .claude/skills/ entry
if (top.angle && top.angle.includes('skill-file')) {
  try {
    const { skillifyOne } = await import('./skillify-shipped.mjs');
    await skillifyOne(top);
  } catch (e) {
    console.error(`[SKILLIFY] Warning: could not skillify: ${e.message}`);
  }
}

console.log(`=== Run complete ===\n`);
