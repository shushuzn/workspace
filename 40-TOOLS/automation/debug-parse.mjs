import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
const __dirname = dirname(fileURLToPath(import.meta.url));

const raw = readFileSync(resolve(__dirname, 'AGENT-WORKFLOWS.md'), 'utf-8');

// Extract first yaml block
const start = raw.indexOf('```yaml');
const end = raw.indexOf('```', start + 1);
const block = raw.slice(start + 7, end).trim();

console.log('=== YAML BLOCK ===');
console.log(block);
console.log('\n=== LINES ===');
block.split('\n').forEach((l, i) => {
  console.log(`${i}: indent=${l.search(/\S/)} | "${l}"`);
});
