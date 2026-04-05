/**
 * prune-omc-state.mjs
 * Prunes stale OMC state files from 80-PROJECTS/.
 * Targets: last-tool-error.json, idle-notif-cooldown.json (safe to delete on sight)
 * Run: node scripts/prune-omc-state.mjs [--dry-run]
 */

import { rmSync, readdirSync } from 'fs';
import { join, resolve } from 'path';

const DRY_RUN = process.argv.includes('--dry-run');
const PRUNE_TYPES = ['last-tool-error.json', 'idle-notif-cooldown.json'];
const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');

async function main() {
  const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));
  let total = 0;

  for (const type of PRUNE_TYPES) {
    for (const dir of dirs) {
      const stateDir = join(WORKSPACE, dir, '.omc', 'state');
      const stateFile = join(stateDir, type);
      try {
        readdirSync(stateDir); // check dir exists
        if (!DRY_RUN) {
          rmSync(stateFile, { force: true });
        }
        total++;
        process.stderr.write(`${DRY_RUN ? '[dry-run] remove' : 'removed'}: ${dir}/.omc/state/${type}\n`);
      } catch {
        // state dir or file doesn't exist — skip
      }
    }
  }

  process.stderr.write(`\n${DRY_RUN ? 'dry-run: ' : ''}pruned ${total} file(s)\n`);
}

main();
