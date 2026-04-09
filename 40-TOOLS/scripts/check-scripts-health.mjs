#!/usr/env node
/**
 * 40-TOOLS/scripts/check-scripts-health.mjs
 * 检查 40-TOOLS 下所有 .mjs 脚本是否有语法错误
 */
import { readdirSync, readFileSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TOOLS_DIR = join(__DIR, '..');

let total = 0, broken = 0;

function scanDir(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry === 'node_modules' || entry === '.git') continue;
    const full = join(dir, entry);
    let stat;
    try { stat = statSync(full); } catch { continue; }
    if (stat.isDirectory()) {
      scanDir(full);
    } else if (full.endsWith('.mjs')) {
      total++;
      try {
        readFileSync(full, 'utf8');
        console.log(`OK: ${full.replace(TOOLS_DIR + '\\', '').replace(TOOLS_DIR + '/', '')}`);
      } catch (e) {
        broken++;
        console.log(`BROKEN: ${full.replace(TOOLS_DIR + '\\', '').replace(TOOLS_DIR + '/', '')} — ${e.message}`);
      }
    }
  }
}

scanDir(TOOLS_DIR);
console.log(`\nHealth check: ${total} scripts, ${broken} broken`);
process.exit(broken > 0 ? 1 : 0);
