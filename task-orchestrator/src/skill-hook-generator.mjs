#!/usr/bin/env node
/**
 * skill-hook-generator.mjs
 * Generate RED-GREEN-REFACTOR skill enforcement hooks for task-orchestrator
 */
import { writeFileSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TEMPLATE = process.argv[2] || 'red-green-refactor';

const HOOK_TEMPLATE = `
// RED-GREEN-REFACTOR checkpoint enforcement
export function onCheckpoint(phase) {
  const valid = ['PLAN', 'CODE', 'TEST', 'REFACTOR'];
  if (!valid.includes(phase)) {
    throw new Error(\`Invalid checkpoint: \${phase}\`);
  }
  // Phase order enforcement
  if (typeof global._lastPhase !== 'undefined') {
    const order = { PLAN: 0, CODE: 1, TEST: 2, REFACTOR: 3 };
    if (order[phase] <= order[global._lastPhase]) {
      throw new Error(\`Phase order violation: \${global._lastPhase} -> \${phase}\`);
    }
  }
  global._lastPhase = phase;
  console.log(\`[checkpoint] \${phase}\`);
}
`;

const OUT_DIR = join(__DIR, '..', '..', '..', '.claude', 'skills');
mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(join(OUT_DIR, 'red-green-refactor-hook.mjs'), HOOK_TEMPLATE, 'utf8');
console.log('[skill-hook-generator] Generated red-green-refactor-hook.mjs');
