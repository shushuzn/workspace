#!/usr/bin/env node
/**
 * persist-chain-artifacts.mjs
 * 将 task-orchestrator executor 的 step artifacts 写入 shared/chain-artifacts.json
 * 供 opencli 等 downstream 工具读取并执行后续操作
 */
import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SHARED_DIR = resolve(__dirname, '..');

// Read artifacts from stdin (pipeline from executor)
process.stdin.setEncoding('utf-8');
let data = '';
process.stdin.on('data', chunk => { data += chunk; });
process.stdin.on('end', () => {
  try {
    const artifacts = JSON.parse(data);
    const outPath = resolve(SHARED_DIR, 'shared', 'chain-artifacts.json');
    writeFileSync(outPath, JSON.stringify(artifacts, null, 2), 'utf-8');
    console.log(`[persist-artifacts] wrote ${artifacts.length} step artifacts to ${outPath}`);
  } catch (e) {
    console.error('[persist-artifacts] ERROR:', e.message);
    process.exit(1);
  }
});
