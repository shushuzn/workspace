#!/usr/bin/env node
/**
 * OMC Trajectory Collector
 * Collects and compresses agent trajectories for fine-tuning data generation.
 *
 * Inspired by Hermes Agent's Trajectory Generation:
 *   - Batch trajectory collection across tasks
 *   - Trajectory compression for efficient model fine-tuning
 *   - Structured format: task → reasoning → action → result
 *   - Supports GRPO/PRM training data formats
 *
 * Usage:
 *   node trajectory-collector.mjs --collect session-id [--task "description"]  Collect
 *   node trajectory-collector.mjs --batch path/to/*.jsonl                   Batch collect
 *   node trajectory-collector.mjs --compress trajectory.jsonl                  Compress
 *   node trajectory-collector.mjs --export --format oai|grpo|prm             Export
 *   node trajectory-collector.mjs --stats                                     Show stats
 *
 * Architecture:
 *   - Raw trajectories: .omc/state/trajectories/raw/
 *   - Compressed: .omc/state/trajectories/compressed/
 *   - Exported: .omc/state/trajectories/export/
 *   - State: .omc/state/trajectory-state.json
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'trajectory-state.json');
const RAW_DIR = resolve(STATE_DIR, 'trajectories/raw');
const COMPRESSED_DIR = resolve(STATE_DIR, 'trajectories/compressed');
const EXPORT_DIR = resolve(STATE_DIR, 'trajectories/export');
const SESSIONS_DIR = resolve(__dirname, '../sessions');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'format') { args.format = argv[++i]; continue; }
      if (key === 'task') { args.task = argv[++i]; continue; }
      if (key === 'batch') { args.batch = argv[++i]; continue; }
      if (key === 'collect') { args.collect = argv[++i]; continue; }
      if (key === 'compress') { args.compress = argv[++i]; continue; }
      if (key === 'export') { args.export = true; continue; }
      if (key === 'stats') { args.stats = true; continue; }
      if (key === 'format') { args.format = argv[++i]; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readState() {
  if (!existsSync(STATE_FILE)) return { collected: 0, compressed: 0, exported: 0 };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { collected: 0, compressed: 0, exported: 0 }; }
}

function writeState(state) {
  mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function ensureDirs() {
  [RAW_DIR, COMPRESSED_DIR, EXPORT_DIR].forEach(d => mkdirSync(d, { recursive: true }));
}

// ── Extract trajectory from session ──────────────────────────────────────────
function extractTrajectory(sessionId, taskDesc = '') {
  const sessionPath = resolve(SESSIONS_DIR, `${sessionId}.json`);
  if (!existsSync(sessionPath)) return { error: 'Session not found' };

  try {
    const content = readFileSync(sessionPath, 'utf-8');
    const session = JSON.parse(content);

    // Convert session to trajectory format
    const trajectory = {
      id: `traj-${Date.now()}`,
      session_id: sessionId,
      task: taskDesc || session.summary || session.activities || 'unknown',
      project: session.project || null,
      started_at: session.started_at,
      ended_at: session.ended_at,
      duration_minutes: session.duration_minutes,
      steps: [],
      tools_used: session.tools_used || [],
      modes_used: session.modes_used || [],
      victories: session.victories || [],
      blockers: session.blockers || [],
      quality: assessQuality(session),
    };

    // Build steps from session data
    if (session.activities) {
      const activities = Array.isArray(session.activities)
        ? session.activities
        : session.activities.split('\n').filter(Boolean);
      for (let i = 0; i < activities.length; i++) {
        trajectory.steps.push({
          step: i + 1,
          type: 'activity',
          content: activities[i],
          outcome: 'success',
        });
      }
    }

    return trajectory;
  } catch (e) {
    return { error: e.message };
  }
}

// ── Quality assessment ────────────────────────────────────────────────────────
function assessQuality(session) {
  let score = 0;
  const reasons = [];

  if (session.victories?.length > 0) { score += 2; reasons.push('victories'); }
  if (session.duration_minutes > 5) { score += 1; reasons.push('meaningful_duration'); }
  if (session.tools_used?.length > 3) { score += 1; reasons.push('tool_diversity'); }
  if (session.blockers?.length === 0) { score += 1; reasons.push('no_blockers'); }

  const quality = score >= 4 ? 'high' : score >= 2 ? 'medium' : 'low';
  return { score, quality, reasons };
}

// ── Compress trajectory ───────────────────────────────────────────────────────
function compressTrajectory(trajectory) {
  // Remove redundant information, keep essential structure
  const compressed = {
    id: trajectory.id,
    session_id: trajectory.session_id,
    task: trajectory.task,
    project: trajectory.project,
    duration_minutes: trajectory.duration_minutes,
    quality: trajectory.quality.quality,
    tool_count: trajectory.tools_used?.length || 0,
    victory_count: trajectory.victories?.length || 0,
    blocker_count: trajectory.blockers?.length || 0,
    step_count: trajectory.steps.length,
    summary: compressSteps(trajectory.steps),
    tags: buildTags(trajectory),
  };

  return compressed;
}

function compressSteps(steps) {
  if (steps.length <= 10) return steps.map(s => s.content);
  // Summarize: first 3 + ellipsis + last 2
  return [
    ...steps.slice(0, 3).map(s => s.content),
    `... [${steps.length - 5} steps omitted] ...`,
    ...steps.slice(-2).map(s => s.content),
  ];
}

function buildTags(trajectory) {
  const tags = [];
  if (trajectory.project) tags.push(`project:${trajectory.project}`);
  if (trajectory.quality?.quality) tags.push(`quality:${trajectory.quality.quality}`);
  if (trajectory.victories?.length > 0) tags.push('has_victories');
  if (trajectory.blockers?.length > 0) tags.push('has_blockers');
  return tags;
}

// ── Export formats ─────────────────────────────────────────────────────────────
function exportOAI(trajectories) {
  return trajectories.map(t => ({
    messages: [
      { role: 'system', content: `You are an AI agent. Task: ${t.task}` },
      { role: 'user', content: t.task },
      { role: 'assistant', content: t.summary?.join('\n') || 'Completed' },
    ],
    metadata: { trajectory_id: t.id, quality: t.quality },
  }));
}

function exportGRPO(trajectories) {
  return trajectories.map(t => ({
    prompt: t.task,
    trajectory: t.summary?.join(' → ') || 'Completed',
    reward: t.quality?.score || 0,
    metadata: { id: t.id, project: t.project },
  }));
}

function exportPRM(trajectories) {
  // Process Reward Model format: step-level rewards
  return trajectories.flatMap(t => {
    if (!t.steps) return [];
    return t.steps.map((step, idx) => ({
      trajectory_id: t.id,
      step: idx + 1,
      content: step.content,
      // For PRM, need actual step outcomes - use placeholder
      reward: step.outcome === 'success' ? 1 : -1,
      metadata: { task: t.task },
    }));
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  ensureDirs();

  if (args.collect) {
    const result = extractTrajectory(args.collect, args.task);
    if (result.error) {
      console.error(`Error: ${result.error}`);
      return;
    }

    const path = resolve(RAW_DIR, `${result.id}.json`);
    writeFileSync(path, JSON.stringify(result, null, 2), 'utf-8');

    const state = readState();
    state.collected++;
    writeState(state);

    console.log(`\n✅ Collected trajectory: ${result.id}`);
    console.log(`   Session: ${result.session_id}`);
    console.log(`   Task: ${result.task}`);
    console.log(`   Quality: ${result.quality.quality} (${result.quality.score}/5)`);
    console.log(`   Steps: ${result.steps.length}`);
    console.log(`   Saved: ${path}\n`);
    return;
  }

  if (args.batch) {
    // Batch collect from multiple sessions
    const glob = args.batch;
    const sessionIds = glob.match(/(\w+-\w+-\w+-\w+-\w+)/g) || [];
    let collected = 0;

    for (const id of sessionIds) {
      const result = extractTrajectory(id);
      if (!result.error) {
        const path = resolve(RAW_DIR, `${result.id}.json`);
        writeFileSync(path, JSON.stringify(result, null, 2), 'utf-8');
        collected++;
      }
    }

    const state = readState();
    state.collected += collected;
    writeState(state);

    console.log(`\n✅ Batch collected: ${collected}/${sessionIds.length} trajectories\n`);
    return;
  }

  if (args.compress) {
    const path = resolve(RAW_DIR, `${args.compress}.json`);
    if (!existsSync(path)) {
      console.error(`Trajectory not found: ${args.compress}`);
      return;
    }

    const raw = JSON.parse(readFileSync(path, 'utf-8'));
    const compressed = compressTrajectory(raw);

    const outPath = resolve(COMPRESSED_DIR, `${compressed.id}.json`);
    writeFileSync(outPath, JSON.stringify(compressed, null, 2), 'utf-8');

    const state = readState();
    state.compressed++;
    writeState(state);

    console.log(`\n✅ Compressed: ${args.compress} → ${compressed.id}`);
    console.log(`   Original: ${raw.steps.length} steps → ${compressed.step_count} steps`);
    console.log(`   Size: ${JSON.stringify(raw).length} → ${JSON.stringify(compressed).length} bytes\n`);
    return;
  }

  if (args.export) {
    const format = args.format || 'oai';
    const files = readdirSync(COMPRESSED_DIR).filter(f => f.endsWith('.json'));
    const trajectories = files.map(f => {
      try { return JSON.parse(readFileSync(resolve(COMPRESSED_DIR, f), 'utf-8')); }
      catch { return null; }
    }).filter(Boolean);

    let exported;
    switch (format) {
      case 'oai': exported = exportOAI(trajectories); break;
      case 'grpo': exported = exportGRPO(trajectories); break;
      case 'prm': exported = exportPRM(trajectories); break;
      default:
        console.error(`Unknown format: ${format}`);
        return;
    }

    const outPath = resolve(EXPORT_DIR, `${format}-${Date.now()}.json`);
    writeFileSync(outPath, JSON.stringify(exported, null, 2), 'utf-8');

    const state = readState();
    state.exported++;
    writeState(state);

    console.log(`\n✅ Exported: ${format.toUpperCase()}`);
    console.log(`   Trajectories: ${trajectories.length}`);
    console.log(`   Format: ${format}`);
    console.log(`   Saved: ${outPath}\n`);
    return;
  }

  if (args.stats) {
    const state = readState();
    const rawFiles = existsSync(RAW_DIR) ? readdirSync(RAW_DIR).filter(f => f.endsWith('.json')) : [];
    const compFiles = existsSync(COMPRESSED_DIR) ? readdirSync(COMPRESSED_DIR).filter(f => f.endsWith('.json')) : [];
    const expFiles = existsSync(EXPORT_DIR) ? readdirSync(EXPORT_DIR).filter(f => f.endsWith('.json')) : [];

    console.log(`\n📊 OMC Trajectory Collector`);
    console.log(`  Collected: ${state.collected} (raw: ${rawFiles.length})`);
    console.log(`  Compressed: ${state.exported} (compressed: ${compFiles.length})`);
    console.log(`  Exported: ${state.exported}`);
    console.log(`  Export files: ${expFiles.length}`);
    console.log();
    return;
  }

  // Default: help
  console.log(`OMC Trajectory Collector`);
  console.log(`Usage:`);
  console.log(`  --collect session-id [--task "desc"]   Collect a trajectory`);
  console.log(`  --batch "glob/pattern"                Batch collect`);
  console.log(`  --compress traj-id                    Compress trajectory`);
  console.log(`  --export --format oai|grpo|prm       Export trajectories`);
  console.log(`  --stats                              Show statistics`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
