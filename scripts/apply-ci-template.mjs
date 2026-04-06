/**
 * apply-ci-template.mjs — Links workspace CI template to a project
 * Run: node scripts/apply-ci-template.mjs <project-name>
 */

import { copyFileSync, mkdirSync } from 'fs';
import { resolve, join } from 'path';

const args = process.argv.slice(2);
if (args.length < 1) {
  console.log('Usage: node scripts/apply-ci-template.mjs <project-name>');
  process.exit(1);
}

const project = args[0];
const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const templateSrc = resolve('D:/OpenClaw/workspace/80-PROJECTS/.github/workflows/template.yml');
const destDir = join(ROOT, project, '.github', 'workflows');
const destPath = join(destDir, 'ci.yml');

try {
  mkdirSync(destDir, { recursive: true });
  copyFileSync(templateSrc, destPath);
  console.log(`  ✓ ${project}/.github/workflows/ci.yml created`);
} catch (e) {
  console.error(`  ✗ Failed: ${e.message}`);
}
