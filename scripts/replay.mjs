/**
 * replay.mjs — Replay a task-orchestrator run from history
 * Run: node scripts/replay.mjs <runId> [--dry-run] [--real]
 * Reads ~/.unified-agent-cli/history.jsonl to find the run record
 */
import { readFileSync, existsSync } from 'fs';
import { join, homedir } from 'path';

const DRY = process.argv.includes('--dry-run');
const REAL = process.argv.includes('--real');
const runId = process.argv.find((a) => !a.startsWith('--') && a !== 'replay.mjs');

if (!runId) {
  console.error('Usage: node scripts/replay.mjs <runId> [--dry-run] [--real]');
  process.exit(1);
}

const histPath = join(homedir(), '.unified-agent-cli', 'history.jsonl');
if (!existsSync(histPath)) {
  console.error(`History file not found: ${histPath}`);
  process.exit(1);
}

const lines = readFileSync(histPath, 'utf8').split('\n').filter(Boolean);
let record = null;
for (const line of lines) {
  try {
    const rec = JSON.parse(line);
    if (rec.runId === runId) {
      record = rec;
      break;
    }
  } catch {
    // skip malformed lines
  }
}

if (!record) {
  console.error(`Run not found: ${runId}`);
  process.exit(1);
}

console.log(`\n  Replaying run ${runId} (${record.timestamp})`);
console.log(`  Prompt: ${record.prompt || '(none)'}`);
console.log(`  Steps: ${record.steps.length}\n`);

for (let i = 0; i < record.steps.length; i++) {
  const step = record.steps[i];
  const prevOk = step.success ? '✓' : '✗';
  console.log(`  [${i + 1}] ${prevOk} ${step.adapterId}: ${step.command} ${(step.args || []).join(' ')}`);
}

if (DRY) {
  console.log('\n  [dry-run] Run with --real to execute\n');
  process.exit(0);
}

if (!REAL) {
  console.log('\n  Run with --real to execute, or --dry-run to preview only\n');
  process.exit(0);
}

// Import Executor and replay
const { Executor } = await import('../80-PROJECTS/task-orchestrator/src/executor.js');
const { Registry } = await import('../80-PROJECTS/task-orchestrator/src/registry.js');

const registry = new Registry();
await registry.load();
const executor = new Executor(registry, { verbose: true });

const { steps, errors } = await import('../80-PROJECTS/task-orchestrator/src/planner.js').then((m) => {
  const planner = new m.Planner(registry);
  return planner.parse(record.prompt || '');
});

if (errors.length > 0) {
  console.error('\n  Parse errors:');
  for (const err of errors) console.error(`    - ${err}`);
}

console.log('\n  Executing...\n');
const results = await executor.execute(steps, { prompt: record.prompt });

const failures = results.filter((r) => !r.success);
console.log(`\n  ${results.length - failures.length}/${results.length} steps succeeded\n`);
if (failures.length > 0) {
  for (const f of failures) console.error(`  ✗ ${f.error}`);
}
