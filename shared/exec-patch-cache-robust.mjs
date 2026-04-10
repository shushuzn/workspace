#!/usr/bin/env node
// Protect loadCache JSON.parse in try-catch
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

const oldBlock = `        try {
            const data = JSON.parse(readFileSync(this.cacheFile, 'utf-8'));
            const now = Date.now();
            for (const [key, entry] of Object.entries(data)) {
                if (entry.expiresAt > now) {
                    this.cache.set(key, entry);
                }
            }
            if (this.cache.size > 0) {
                console.warn(\`[cache] loaded \${this.cache.size} entries from \${this.cacheFile}\`);
            }
        }`;

const newBlock = `        try {
            const data = JSON.parse(readFileSync(this.cacheFile, 'utf-8'));
            const now = Date.now();
            for (const [key, entry] of Object.entries(data)) {
                if (entry.expiresAt > now) {
                    this.cache.set(key, entry);
                }
            }
            if (this.cache.size > 0) {
                console.warn(\`[cache] loaded \${this.cache.size} entries from \${this.cacheFile}\`);
            }
        } catch (e) {
            console.warn(\`[cache] failed to parse cache file: \${e.message}\`);
        }`;

if (!content.includes(oldBlock)) {
    console.error('[patch] loadCache JSON.parse try-catch not found');
    process.exit(1);
}

const next = content.replace(oldBlock, newBlock);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] loadCache JSON.parse now protected by try-catch');
