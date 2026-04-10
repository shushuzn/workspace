#!/usr/bin/env node
// Patch executor.mjs buildDependencyGraph to detect cycles
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

const marker = 'return deps;';
if (!content.includes(marker)) {
  console.error('[patch] return deps not found');
  process.exit(1);
}

const cycleCheck = `
// Detect cycles using DFS — throw on cycle
const visited = new Set();
const stack = new Set();
function hasCycle(node) {
    if (stack.has(node)) throw new Error(\`[dependency] cycle detected at step \${node}\`);
    if (visited.has(node)) return false;
    visited.add(node);
    stack.add(node);
    for (const dep of (deps.get(node) || new Set())) {
        if (hasCycle(dep)) return true;
    }
    stack.delete(node);
    return false;
}
for (let i = 0; i < steps.length; i++) {
    visited.clear();
    stack.clear();
    hasCycle(i);
}
`;

const next = content.replace(marker, cycleCheck + '\n        ' + marker);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] buildDependencyGraph now detects cycles');
