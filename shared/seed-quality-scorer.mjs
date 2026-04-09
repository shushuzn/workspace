#!/usr/bin/env node
/** Score unscored seeds in ideas.md pool */
import { readFileSync } from 'fs';

const content = readFileSync('.omc/innovation/ideas.md', 'utf8');
const lines = content.split('\n');
let unscored = 0;
for (const l of lines) {
  if (l.match(/shipped:|killed:/) || !l.match(/seed.*score:/)) continue;
  const score = l.match(/score:(\d+x\d+)/);
  if (!score) {
    console.log(l.slice(2, 80));
    unscored++;
  }
}
console.log('Unscored seeds:', unscored);
