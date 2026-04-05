/**
 * check-env-templates.mjs
 * Reports projects missing .env.example and generates a template.
 * Run: node scripts/check-env-templates.mjs
 */

import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { join, resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));

const TEMPLATE = `# Environment variables
# Copy to .env and fill in your values

# LLM API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

# Application
NODE_ENV=development
PORT=3000
`;

console.log(`\n${'Project'.padEnd(28)} Status`);
console.log('-'.repeat(40));

let has = 0, created = 0;

for (const dir of dirs) {
  const envPath = join(WORKSPACE, dir, '.env.example');
  try {
    readFileSync(envPath);
    console.log(`${dir.padEnd(28)} has .env.example`);
    has++;
  } catch {
    try {
      writeFileSync(envPath, TEMPLATE, 'utf8');
      console.log(`${dir.padEnd(28)} CREATED`);
      created++;
    } catch {
      console.log(`${dir.padEnd(28)} SKIP (no package?)`);
    }
  }
}

console.log(`\nhas: ${has}  created: ${created}  total: ${dirs.length}\n`);
