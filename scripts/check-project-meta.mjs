/**
 * check-project-meta.mjs — Reports missing/broken metadata in 80-PROJECTS packages
 * Run: node scripts/check-project-meta.mjs [--json]
 */
import { readdirSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';

const ROOT = join('D:/OpenClaw/workspace/80-PROJECTS');
const JSON_MODE = process.argv.includes('--json');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

let total = 0, missingDesc = 0, missingKw = 0, missingReadme = 0, placeholderDesc = 0;
const results = [];

for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const readmePath = join(dir, 'README.md');
  const name = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  total++;

  const pkg = existsSync(pkgPath)
    ? JSON.parse(readFileSync(pkgPath, 'utf8'))
    : null;
  const readmeExists = existsSync(readmePath);

  const issues = [];
  const missing_fields = [];
  const invalid_fields = [];

  if (!pkg) {
    issues.push('NO package.json');
  } else {
    if (!pkg.description || pkg.description.trim() === '') {
      missingDesc++;
      missing_fields.push('description');
      issues.push('MISSING description');
    } else if (
      pkg.description === 'TODO' ||
      pkg.description === 'undefined' ||
      /^{{"?name"?}/.test(pkg.description) ||
      pkg.description.length < 10
    ) {
      placeholderDesc++;
      invalid_fields.push(`description: "${pkg.description}"`);
      issues.push(`PLACEHOLDER description: "${pkg.description}"`);
    }
    if (!pkg.keywords || pkg.keywords.length === 0) {
      missingKw++;
      missing_fields.push('keywords');
      issues.push('MISSING keywords');
    }
    // New: repository field
    if (!pkg.repository) {
      missing_fields.push('repository');
      issues.push('MISSING repository');
    } else if (typeof pkg.repository === 'object' && !pkg.repository.url) {
      invalid_fields.push('repository: missing url field');
      issues.push('INVALID repository: missing url field');
    } else if (typeof pkg.repository === 'string' && !pkg.repository.startsWith('git')) {
      invalid_fields.push(`repository: "${pkg.repository}"`);
      issues.push(`INVALID repository: "${pkg.repository}"`);
    }
    // New: homepage field
    if (!pkg.homepage) {
      missing_fields.push('homepage');
      issues.push('MISSING homepage');
    }
  }

  if (!readmeExists) {
    missingReadme++;
    missing_fields.push('README.md');
    issues.push('NO README.md');
  }

  if (issues.length > 0) {
    if (JSON_MODE) {
      results.push({ project: name, missing_fields, invalid_fields, issues });
    } else {
      console.log(`\n  ${name}`);
      for (const issue of issues) console.log(`    - ${issue}`);
    }
  }
}

if (JSON_MODE) {
  console.log(JSON.stringify({ total, results, summary: { missing_description: missingDesc, placeholder_desc: placeholderDesc, missing_keywords: missingKw, missing_readme: missingReadme } }, null, 2));
} else {
  console.log(`\n  ── Summary (${total} projects) ──`);
  console.log(`  Missing description:  ${missingDesc}`);
  console.log(`  Placeholder desc:     ${placeholderDesc}`);
  console.log(`  Missing keywords:     ${missingKw}`);
  console.log(`  Missing README:        ${missingReadme}`);
  console.log('');
}
