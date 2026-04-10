#!/usr/bin/env node
// Optimize buildDependencyGraph cycle detection: single DFS instead of per-node
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Replace the per-node DFS cycle detection with a single global DFS
// Old: for (let i = 0; i < steps.length; i++) { visited.clear(); stack.clear(); hasCycle(i); }
// New: single pass using Tarjan-like algorithm with global visited and onStack sets

const oldCycleBlock = `// Detect cycles using DFS — throw on cycle
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
}`;

const newCycleBlock = `// Detect cycles using single DFS pass (Tarjan-inspired) — O(V+E)
const visited = new Set();
const onStack = new Set();
let hasGlobalCycle = false;
let cycleNode = -1;
function dfsCycle(node) {
    if (onStack.has(node)) { hasGlobalCycle = true; cycleNode = node; return; }
    if (visited.has(node)) return;
    visited.add(node);
    onStack.add(node);
    for (const dep of (deps.get(node) || new Set())) {
        dfsCycle(dep);
        if (hasGlobalCycle) return;
    }
    onStack.delete(node);
}
for (let i = 0; i < steps.length; i++) {
    if (!visited.has(i)) {
        dfsCycle(i);
        if (hasGlobalCycle) throw new Error(\`[dependency] cycle detected at step \${cycleNode}\`);
    }
}`;

if (!content.includes(oldCycleBlock)) {
    console.error('[patch] cycle detection block not found');
    process.exit(1);
}

const next = content.replace(oldCycleBlock, newCycleBlock);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] buildDependencyGraph cycle detection now uses single DFS pass');
