// ~/.omc/patrol-agent/src/state.js
// Loads and saves patrol-state.json with cross-platform homedir support

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import os from 'os';

// Resolve ~/.omc/patrol-state.json
function getStatePath() {
  const home = os.homedir();
  const omcDir = join(home, '.omc');
  return join(omcDir, 'patrol-state.json');
}

function ensureOmcDir() {
  const home = os.homedir();
  const omcDir = join(home, '.omc');
  if (!existsSync(omcDir)) {
    mkdirSync(omcDir, { recursive: true });
  }
  return omcDir;
}

export function loadState() {
  const statePath = getStatePath();
  try {
    if (existsSync(statePath)) {
      const raw = readFileSync(statePath, 'utf-8');
      return JSON.parse(raw);
    }
  } catch (err) {
    // Corrupt state — start fresh
  }
  // Default state
  return {
    last_patrol: null,
    loop_count: 0,
    completed_actions: [],
    skipped: [],
    research_topics: [],
    patrol_log: [],
    running: false,
  };
}

export function saveState(state) {
  const statePath = getStatePath();
  ensureOmcDir();
  try {
    writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8');
  } catch (err) {
    console.error('[patrol] Failed to save state:', err.message);
  }
}
