/**
 * generate-license.mjs — Generates MIT LICENSE files for projects missing them
 * Run: node scripts/generate-license.mjs [--author "Your Name"] [--dry-run]
 */

import { readdirSync, writeFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const TEMPLATE_SRC = resolve('D:/OpenClaw/workspace/LICENSE');
const YEAR = new Date().getFullYear();

const args = process.argv.slice(2);
let author = 'OpenClaw';
let dryRun = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--author' && args[i + 1]) author = args[++i];
  if (args[i] === '--dry-run') dryRun = true;
}

const template = existsSync(TEMPLATE_SRC)
  ? readFileSync(TEMPLATE_SRC, 'utf8')
  : `MIT License

Copyright (c) ${YEAR} ${author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
`;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

let generated = 0;
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const licPath = join(dir, 'LICENSE');
  if (!existsSync(licPath)) {
    if (dryRun) {
      console.log(`  [dry-run] would create: ${rel}/LICENSE`);
    } else {
      const content = template.replace(/\{\{YEAR\}\}/g, String(YEAR)).replace(/\{\{AUTHOR\}\}/g, author);
      writeFileSync(licPath, content, 'utf8');
      console.log(`  + ${rel}/LICENSE`);
    }
    generated++;
  }
}

if (dryRun) {
  console.log(`\n  [dry-run] ${generated} project(s) need LICENSE (not written)\n`);
} else {
  console.log(`\n  ${generated} LICENSE file(s) generated\n`);
}
