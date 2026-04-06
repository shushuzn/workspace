/**
 * generate-readme.mjs — Auto-generates README.md from package.json for projects missing it
 * Run: node scripts/generate-readme.mjs [--dry-run]
 */

import { readdirSync, readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const args = process.argv.includes('--dry-run');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

let generated = 0;
for (const dir of dirs) {
  const readmePath = join(dir, 'README.md');
  if (existsSync(readmePath)) continue;
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    const name = pkg.name || rel;
    const description = pkg.description || '';
    const version = pkg.version || '0.0.1';
    const repo = typeof pkg.repository === 'string' ? pkg.repository : pkg.repository?.url || '';

    let badges = '';
    if (repo.includes('github.com')) {
      const repoClean = repo.replace('git+https://github.com/', '').replace('.git', '');
      badges = `[![CI](https://img.shields.io/github/actions/workflow/status/${repoClean}/ci.yml?style=flat-square)](https://github.com/${repoClean}/actions)\n`;
    }

    const readme = `# ${name}

${description ? description + '\n' : ''}${badges}
## Install

\`\`\`bash
npm install
\`\`\`

## Usage

\`\`\`bash
npm run dev
\`\`\`

## License

MIT
`;
    if (!args) writeFileSync(readmePath, readme, 'utf8');
    console.log(`  + ${rel}/README.md`);
    generated++;
  } catch {}
}
console.log(`\n  ${generated} README(s) generated\n`);
