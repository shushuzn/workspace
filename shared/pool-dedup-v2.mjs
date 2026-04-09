#!/usr/bin/env node
/** Find duplicate seeds in pool by description similarity */
import { readFileSync } from 'fs';

const content = readFileSync('.omc/innovation/ideas.md', 'utf8');
const lines = content.split('\n');
const seeds = [];
for (const line of lines) {
  if (!line.match(/^- \[/)) continue;
  const desc = line.replace(/^\s*/, '').split('|')[0].replace(/.*\]/, '').trim();
  seeds.push(desc);
}
const seen = new Set();
const dupes = [];
for (const s of seeds) {
  const norm = s.toLowerCase().replace(/[^a-z0-9]/g, '');
  if (seen.has(norm)) dupes.push(s);
  else seen.add(norm);
}
if (dupes.length) {
  console.log('Duplicates found:', dupes.length);
  dupes.forEach(d => console.log(' ', d.slice(0, 60)));
} else {
  console.log('No duplicates found');
}
