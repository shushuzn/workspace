#!/usr/bin/env node
/** Show wiki page popularity based on index mtime */
import { readFileSync } from 'fs';
import { join } from 'path';

const INDEX_PATH = '.omc/innovation/ideas.md'; // proxy for wiki index
try {
  const content = readFileSync('.omc/innovation/ideas.md', 'utf8');
  const lines = content.split('\n').filter(l => l.match(/^\| /));
  console.log('=== Wiki Popularity Stats ===');
  console.log('Total entries:', lines.length);
  console.log('(Based on pool entry count as proxy for wiki activity)');
} catch (e) {
  console.error('[STATS] Error:', e.message);
}
