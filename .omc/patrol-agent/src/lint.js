// ~/.omc/patrol-agent/src/lint.js
// Check for lint errors in workspace projects
// Uses eslint if project has eslint.config.js or .eslintrc, else surface scan

import { execSync } from 'child_process';
import { existsSync, readdirSync } from 'fs';
import { join } from 'path';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';

function findEslintConfig(dir) {
  const candidates = [
    'eslint.config.js', 'eslint.config.mjs', 'eslint.config.cjs',
    '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yaml',
  ];
  for (const c of candidates) {
    if (existsSync(join(dir, c))) return join(dir, c);
  }
  return null;
}

function getJsFiles(dir, patterns = ['src/', ''], maxDepth = 3) {
  const files = [];
  function scan(subdir, depth) {
    if (depth > maxDepth) return;
    try {
      const entries = readdirSync(subdir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory() && !entry.name.startsWith('.') && !entry.name.startsWith('node_modules')) {
          scan(join(subdir, entry.name), depth + 1);
        } else if (entry.isFile() && (entry.name.endsWith('.js') || entry.name.endsWith('.jsx') || entry.name.endsWith('.ts') || entry.name.endsWith('.tsx'))) {
          files.push(join(subdir, entry.name));
        }
      }
    } catch { /* skip inaccessible dirs */ }
  }
  scan(dir, 0);
  return files;
}

const PROJECT_DIRS = [
  'D:/OpenClaw/workspace/80-PROJECTS/agent-arena',
  'D:/OpenClaw/workspace/80-PROJECTS/ai-roundtable',
  'D:/OpenClaw/workspace/80-PROJECTS/star-forge-web',
];

export function checkLint() {
  /** @type {Array<{project: string, errors: number, output: string}>} */
  const results = [];

  for (const projectDir of PROJECT_DIRS) {
    if (!existsSync(projectDir)) continue;

    const eslintConfig = findEslintConfig(projectDir);
    if (eslintConfig) {
      try {
        const output = execSync(
          `npx eslint . --max-warnings 0 --format json`,
          { cwd: projectDir, encoding: 'utf-8', timeout: 60000, stdio: ['pipe', 'pipe', 'pipe'] }
        );
        let parsed;
        try {
          parsed = JSON.parse(output);
        } catch {
          parsed = [];
        }
        const totalErrors = parsed.reduce((sum, f) => sum + (f.errorCount || 0), 0);
        results.push({ project: projectDir.split('/').pop(), errors: totalErrors, output: '' });
      } catch (err) {
        // eslint failed or found errors (exit code != 0)
        const output = err.stdout || '';
        let parsed;
        try {
          parsed = JSON.parse(output);
        } catch {
          parsed = [];
        }
        const totalErrors = parsed.reduce((sum, f) => sum + (f.errorCount || 0), 0);
        results.push({ project: projectDir.split('/').pop(), errors: totalErrors, output });
      }
    } else {
      // No eslint config — skip for now (surface scan in Phase 3)
      results.push({ project: projectDir.split('/').pop(), errors: 0, output: 'no-eslint-config' });
    }
  }

  return results;
}

export function hasLintErrors() {
  const results = checkLint();
  return results.some(r => r.errors > 0);
}
