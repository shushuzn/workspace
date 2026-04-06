import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
const __dirname = dirname(fileURLToPath(import.meta.url));

const raw = readFileSync(resolve(__dirname, 'AGENT-WORKFLOWS.md'), 'utf-8');
const start = raw.indexOf('```yaml');
const end = raw.indexOf('```', start + 1);
const block = raw.slice(start + 7, end).trim();

// Manual parse debug
const lines = block.split('\n').filter(l => l.trim() !== '');
console.log('Lines:', lines.length);
for (const [i, l] of lines.entries()) {
  console.log(`${i}: indent=${l.search(/\S/)} | "${l.trim()}"`);
}
