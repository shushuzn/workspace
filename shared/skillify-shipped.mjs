#!/usr/bin/env node
/**
 * shared/skillify-shipped.mjs
 * Auto-generates .claude/skills/[name]/SKILL.md from shipped skill-file seeds.
 * Usage:
 *   node shared/skillify-shipped.mjs              # process all shipped skill-file seeds
 *   node shared/skillify-shipped.mjs --dry-run    # preview without writing
 *   node shared/skillify-shipped.mjs --name X     # process specific skill name
 */
import { mkdirSync, writeFileSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const SKILLS_DIR = join(__DIR, '..', '.claude', 'skills');
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const nameIdx = args.indexOf('--name');
const nameFilter = nameIdx !== -1 ? args[nameIdx + 1] : null;

// ── Parse ideas.md ─────────────────────────────────────────────────────────────
const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const skillFileSeeds = [];
let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const headerMatch = line.match(/^- \[(\d{4}-\d{2}-\d{2}|\d{8})\] (?:STAGE|seed) \[([^\]]+)\]/);
  if (!headerMatch) { i++; continue; }

  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) {
    bodyLines.push(lines[j]);
    j++;
  }
  const bodyText = bodyLines.join('\n').replace(/^\s{2}/gm, '');

  const shippedMatch = line.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/);
  if (!shippedMatch) { i = j; continue; }

  const angleMatch = line.match(/\[angle:([^\]]+)\]/);
  const angle = angleMatch ? angleMatch[1] : '';

  if (angle === 'skill-file' || angle.includes('skill-file')) {
    const desc = line.replace(/^\s*/, '').split('|')[0].replace(/.*\]\s*[\w-]+\s*/, '').trim();

    const benefitMatch = bodyText.match(/\| benefit:\s*(.+?)(?:\s*\| reason:|$)/s)
      || bodyText.match(/benefit:\s*(.+?)(?:\s*\|)/s);
    const benefitText = benefitMatch ? benefitMatch[1].trim() : desc;

    const approachMatch = bodyText.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|$)/s)
      || line.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|$)/s);
    const approachText = approachMatch ? approachMatch[1].trim() : '';

    skillFileSeeds.push({ date: shippedMatch[1], desc, benefitText, approachText, lineIdx: i, bodyLines });
  }
  i = j;
}

if (skillFileSeeds.length === 0) {
  console.log('[SKILLIFY] No shipped skill-file seeds found.');
  process.exit(0);
}

console.log(`\n=== Skillify ===`);
console.log(`Found ${skillFileSeeds.length} shipped skill-file seed(s)\n`);

// ── Skillify each seed ────────────────────────────────────────────────────────
const results = [];
for (const seed of skillFileSeeds) {
  if (nameFilter && !seed.desc.toLowerCase().includes(nameFilter.toLowerCase())) continue;

  // Derive skill name from description
  const skillName = seed.desc
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .replace(/^skill-file-/, '')
    .slice(0, 64);

  if (!skillName) {
    console.log(`[SKILLIFY] Skip: could not derive skill name from "${seed.desc}"`);
    results.push({ skillName: null, status: 'skipped' });
    continue;
  }

  // Extract description (benefit text or first clause of desc)
  const description = seed.benefitText || seed.desc;

  // Format approach as skill body
  const body = seed.approachText
    .split(/\n/)
    .map(l => l.replace(/^\s*[\d一二三四五六七八九]+\.\s*/, '- ').replace(/；$/, '').trim())
    .filter(l => l.length > 0)
    .join('\n');

  const skillContent = `---
name: "${skillName.replace(/-/g, ' ')}"
description: "${description.replace(/"/g, '\\"')}"
---
# ${skillName}

## Overview
${description}

## Usage
${body || '(see approach steps in ideas.md)'}
`;

  const skillDir = join(SKILLS_DIR, skillName);
  const skillFilePath = join(skillDir, 'SKILL.md');

  if (dryRun) {
    console.log(`[DRY RUN] Would create: .claude/skills/${skillName}/SKILL.md`);
    console.log(`  desc: ${seed.desc.slice(0, 60)}`);
    console.log(`  benefit: ${description.slice(0, 60)}`);
    console.log('');
    results.push({ skillName, status: 'dry-run' });
  } else {
    mkdirSync(skillDir, { recursive: true });
    writeFileSync(skillFilePath, skillContent, 'utf-8');
    console.log(`[SKILLIFY] Created: .claude/skills/${skillName}/SKILL.md`);
    results.push({ skillName, status: 'created' });
  }
}

console.log(`\n=== Summary ===`);
console.log(`Total: ${results.length} | Created: ${results.filter(r => r.status === 'created').length} | Dry run: ${results.filter(r => r.status === 'dry-run').length}`);

// ── Export for use by run-seed.mjs ──────────────────────────────────────────
export async function skillifyOne(seed) {
  const skillName = seed.desc
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .replace(/^skill-file-/, '')
    .slice(0, 64);

  if (!skillName) throw new Error(`Cannot derive skill name from: ${seed.desc}`);

  const description = seed.benefitText || seed.desc;
  const body = (seed.approachText || '')
    .split(/\n/)
    .map(l => l.replace(/^\s*[\d一二三四五六七八九]+\.\s*/, '- ').replace(/；$/, '').trim())
    .filter(l => l.length > 0)
    .join('\n');

  const skillContent = `---
name: "${skillName.replace(/-/g, ' ')}"
description: "${description.replace(/"/g, '\\"')}"
version: 1.0.0
triggers:
  - ${seed.angle || skillName.replace(/-/g, ' ')}
---

# ${skillName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}

${description}

## Usage
${body || '(see approach steps in ideas.md)'}
`;

  const skillDir = join(SKILLS_DIR, skillName);
  mkdirSync(skillDir, { recursive: true });
  writeFileSync(join(skillDir, 'SKILL.md'), skillContent, 'utf-8');
  console.log(`[SKILLIFY] Created .claude/skills/${skillName}/SKILL.md`);
}
