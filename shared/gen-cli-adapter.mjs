#!/usr/bin/env node
/**
 * Generate task-orchestrator adapter from CLI-Anything registry entry.
 * Usage: node gen-cli-adapter.mjs <cli-name>
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const REGISTRY = join(__DIR, '..', '80-PROJECTS', 'CLI-Anything', 'registry.json');
const OUT_DIR = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'adapters');

const name = process.argv[2];
if (!name) {
  console.log('Usage: node gen-cli-adapter.mjs <cli-name>');
  const registry = JSON.parse(readFileSync(REGISTRY, 'utf8'));
  const clis = registry.clis || [];
  console.log('Available CLIs:', clis.map(c => c.name).join(', '));
  process.exit(1);
}

const registry = JSON.parse(readFileSync(REGISTRY, 'utf8'));
const cli = (registry.clis || []).find(c => c.name === name);
if (!cli) {
  console.error(`[gen-cli-adapter] CLI not found: ${name}`);
  process.exit(1);
}

mkdirSync(OUT_DIR, { recursive: true });
const adapterId = `cli-anything-${name}`;
const filePath = join(OUT_DIR, `${adapterId}.mjs`);

const content = `import { execSync } from 'child_process';

/**
 * ${cli.display_name} adapter
 * ${cli.description}
 */
export const ${adapterId.replace(/-/g, '_')} = {
  adapterId: '${adapterId}',
  adapterType: 'cli-anything',
  async execute({ command, args = [], timeoutMs = 30000 }) {
    const cmd = '${name} ' + [command, ...args].join(' ');
    const output = execSync(cmd, { timeout: timeoutMs, encoding: 'utf8', windowsHide: true });
    return { success: true, output, artifacts: [] };
  }
};
`;

writeFileSync(filePath, content, 'utf8');
console.log(`[gen-cli-adapter] Generated: ${filePath}`);
