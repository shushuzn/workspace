#!/usr/bin/env node
// Patch executor.mjs runSelfAudit to trigger auto-seed when patterns >= 3
import { readFileSync, writeFileSync, appendFileSync, mkdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { execSync } from 'child_process';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
const content = readFileSync(TARGET, 'utf8');

// Find the "Append to seeds file" section and add auto-seed trigger after it
const appendMarker = 'appendFileSync(SEEDS_FILE, entry, \'utf-8\');';
if (!content.includes(appendMarker)) {
  console.error('[patch] appendFileSync marker not found');
  process.exit(1);
}

const triggerBlock = `
        // Trigger auto-seed if patterns accumulated >= 3
        if (selfReflectPatterns.length >= 3) {
            try {
                execSync('node "D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs" --ingest', {
                    stdio: 'ignore',
                    timeout: 5000
                });
            } catch { /* ignore */ }
        }`;

const next = content.replace(appendMarker, appendMarker + triggerBlock);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] runSelfAudit now triggers auto-seed when patterns >= 3');
