#!/usr/bin/env node
/**
 * Generate capability manifest for all 80-PROJECTS.
 * Output: JSON array of { name, description, keywords, path }
 */
import { readdirSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';

const ROOT = join(import.meta.dirname, '..', '80-PROJECTS');

const projects = [];

for (const dir of readdirSync(ROOT)) {
  if (dir.startsWith('.') || dir.startsWith('10-') || dir === 'ARCHIVED' || dir === 'shared-types' || dir === 'shared' || dir === 'scripts') continue;
  const pkgPath = join(ROOT, dir, 'package.json');
  if (!existsSync(pkgPath)) continue;
  let pkg;
  try {
    pkg = JSON.parse(readFileSync(pkgPath, 'utf-8'));
  } catch { continue; }
  projects.push({
    name: dir,
    description: pkg.description ?? '',
    keywords: Array.isArray(pkg.keywords) ? pkg.keywords : [],
    path: `80-PROJECTS/${dir}`,
  });
}

const outPath = join(import.meta.dirname, '..', '80-PROJECTS', '.capability-manifest.json');
import { writeFileSync } from 'fs';
writeFileSync(outPath, JSON.stringify(projects, null, 2));
console.log(`Generated ${projects.length} project capabilities -> ${outPath}`);
