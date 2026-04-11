#!/usr/bin/env python3
"""Patch audit-query.mjs to add --json output mode"""
import sys

filepath = "80-PROJECTS/task-orchestrator/bin/audit-query.mjs"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if "isJson" in content and "JSON.stringify" in content:
    print("already has --json")
    sys.exit(0)

# Add isJson after the cmd variables
old = """const cmd = process.argv.includes('--recent') ? 'recent'
  : process.argv.includes('--run') ? 'run'
  : process.argv.includes('--failed') ? 'failed'
  : process.argv.includes('--stats') ? 'stats'
  : 'recent';"""

new = """const isJson = process.argv.includes('--json');
const cmd = process.argv.includes('--recent') ? 'recent'
  : process.argv.includes('--run') ? 'run'
  : process.argv.includes('--failed') ? 'failed'
  : process.argv.includes('--stats') ? 'stats'
  : 'recent';"""

# Also patch each output branch to check isJson
# For --recent output
old_recent = """  console.log(`=== Last ${recent.length} audit entries ===`);
  for (const e of recent) {
    const dt = new Date(e.timestamp).toISOString().slice(0, 19).replace('T', ' ');
    const status = e.success ? '✓' : '✗';
    const fatal = e.fatal ? ' [FATAL]' : '';
    const cached = e.cached ? ' [CACHED]' : '';
    const duration = e.durationMs ? ` ${(e.durationMs/1000).toFixed(1)}s` : '';
    console.log(`${status} ${dt} runId=${e.runId?.slice(0,8)} seq=${e.seq} ${e.adapterId}:${e.command}${duration}${fatal}${cached}`);
    if (!e.success && e.error) console.log(`  ERROR: ${e.error.slice(0, 120)}`);
    if (e.causalityDepth > 0) console.log(`  chain depth=${e.causalityDepth} parent=${e.parentStepIdx}`);
  }"""

new_recent = """  if (isJson) {
    console.log(JSON.stringify({ cmd: 'recent', entries: recent.map(e => ({ runId: e.runId, seq: e.seq, adapterId: e.adapterId, command: e.command, success: e.success, durationMs: e.durationMs, fatal: e.fatal })) }));
  } else {
    console.log(`=== Last ${recent.length} audit entries ===`);
    for (const e of recent) {
      const dt = new Date(e.timestamp).toISOString().slice(0, 19).replace('T', ' ');
      const status = e.success ? '✓' : '✗';
      const fatal = e.fatal ? ' [FATAL]' : '';
      const cached = e.cached ? ' [CACHED]' : '';
      const duration = e.durationMs ? ` ${(e.durationMs/1000).toFixed(1)}s` : '';
      console.log(`${status} ${dt} runId=${e.runId?.slice(0,8)} seq=${e.seq} ${e.adapterId}:${e.command}${duration}${fatal}${cached}`);
      if (!e.success && e.error) console.log(`  ERROR: ${e.error.slice(0, 120)}`);
      if (e.causalityDepth > 0) console.log(`  chain depth=${e.causalityDepth} parent=${e.parentStepIdx}`);
    }
  }"""

if old in content:
    content = content.replace(old, new)
    if old_recent in content:
        content = content.replace(old_recent, new_recent)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("added --json")
else:
    print("skip: pattern not found")
