#!/usr/bin/env node
// Guard result output with verbose check
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

const oldLine = `                    process.stderr.write(\`[result] success=\${result.success} artifacts=\${result.artifacts.length}\\n\`);`;
const newLine = `                    if (this.options.verbose) {\n                        process.stderr.write(\`[result] success=\${result.success} artifacts=\${result.artifacts.length}\\n\`);\n                    }`;

if (!content.includes(oldLine)) {
    console.error('[patch] result verbose line not found');
    process.exit(1);
}

const next = content.replace(oldLine, newLine);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] result output now guarded by verbose check');
