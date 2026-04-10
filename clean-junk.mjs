import { readdirSync, unlinkSync } from 'fs';
import { join } from 'path';

const junk = [
  "3'",
  "`${i",
  "console.log(JSON.stringify(a)))",
  "l.includes('argv')))",
  "p.test(r))",
  "p.test(reasonForCheck))",
  "p.test(reasonText))",
  "s.feas",
  "{,",
  "{const",
  "x.includes('seed",
];

const dirs = readdirSync('.');
for (const f of dirs) {
  for (const pat of junk) {
    if (f.includes(pat.slice(0, 8))) {
      try { unlinkSync(f); console.log('rm', f); } catch {}
      break;
    }
  }
}
console.log('Done');
