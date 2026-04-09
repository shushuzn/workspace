#!/usr/bin/env node
/**
 * Export annealing process to CSV via --export-csv flag
 * Usage: node index.js --export-csv "topic" --rounds 3
 */
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const INDEX_JS = join(__DIR, '..', 'index.js');

const topic = process.argv[2] || '测试讨论';
const rounds = process.argv.includes('--rounds')
  ? process.argv[process.argv.indexOf('--rounds') + 1] || '3'
  : '3';

console.log('=== Annealing CSV Export ===');
console.log('Topic:', topic);
console.log('Rounds:', rounds);
console.log('Flag: --export-csv');
console.log('\n[RUN] node index.js --export-csv --rounds', rounds, '"' + topic + '"');

const child = spawn('node', [INDEX_JS, '--export-csv', '--rounds', rounds, topic], {
  stdio: 'inherit',
  cwd: __DIR
});

child.on('exit', code => {
  console.log('\n[EXIT] Code:', code);
});
