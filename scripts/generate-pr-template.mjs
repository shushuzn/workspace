/**
 * generate-pr-template.mjs — Generates PULL_REQUEST_TEMPLATE.md for projects missing it
 * Run: node scripts/generate-pr-template.mjs [--dry-run]
 */

import { readdirSync, existsSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const args = process.argv.includes('--dry-run');

const TEMPLATE = `## Summary
<!-- Brief description of changes -->

## Type
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Documentation
- [ ] Other

## Test Plan
<!-- How was this tested? -->

## Checklist
- [ ] Tests pass
- [ ] Lint passes
- [ ] Documentation updated (if needed)
`;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

let generated = 0;
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const ghDir = join(dir, '.github');
  const prPath = join(ghDir, 'PULL_REQUEST_TEMPLATE.md');
  if (!existsSync(prPath)) {
    if (!args) {
      if (!existsSync(ghDir)) mkdirSync(ghDir, { recursive: true });
      writeFileSync(prPath, TEMPLATE, 'utf8');
    }
    console.log(`  + ${rel}/.github/PULL_REQUEST_TEMPLATE.md`);
    generated++;
  }
}
console.log(`\n  ${generated} PR template(s) generated\n`);
