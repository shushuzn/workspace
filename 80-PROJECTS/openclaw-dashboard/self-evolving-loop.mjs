/**
 * Entry point - redirects to modular architecture
 * Previous monolithic self-evolving-loop.mjs
 */
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const entry = path.join(__dirname, 'src', 'index.mjs');

const child = spawn('node', [entry, ...process.argv.slice(2)], {
  cwd: process.cwd(),
  stdio: 'inherit'
});

child.on('exit', code => process.exit(code));
