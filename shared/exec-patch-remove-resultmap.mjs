#!/usr/bin/env node
// Remove dead resultMap: declared but never read (8 .set, 0 .get)
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Remove the resultMap declaration (note: arrow is → unicode, not ->)
let next = content.replace(
    '        const resultMap = new Map(); // step index \u2192 result\n',
    ''
);

// Remove all resultMap.set calls (multiline)
next = next.replace(/resultMap\.set\(stepIdx, .+\);?\n/g, '');

if (next === content) {
    console.error('[patch] resultMap dead code not found');
    process.exit(1);
}

writeFileSync(TARGET, next, 'utf8');
console.log('[patch] removed dead resultMap (8 .set calls, 0 .get)');
