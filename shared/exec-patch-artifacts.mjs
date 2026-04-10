#!/usr/bin/env node
// Patch persistLogs to also write step artifacts as JSON
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

const marker = "writeFileSync(join(logsDir, `step-${i + 1}.stdout`), r.output, 'utf-8');";
const repl = "writeFileSync(join(logsDir, `step-${i + 1}.stdout`), r.output, 'utf-8');\n                if (r.artifacts && r.artifacts.length > 0) {\n                    writeFileSync(join(logsDir, `step-${i + 1}.artifacts.json`), JSON.stringify(r.artifacts, null, 2), 'utf-8');\n                }";

if (!content.includes(marker)) {
  console.error('[patch] persistLogs marker not found');
  process.exit(1);
}

const next = content.replace(marker, repl);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] persistLogs now writes step artifacts');
