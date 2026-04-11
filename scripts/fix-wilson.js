#!/usr/bin/env node
const fs = require('fs');
let c = fs.readFileSync(process.argv[2], 'utf8');

const old = `function confToPercent(conf) {
  if (conf === null) return 'N/A';
  if (typeof conf === 'object') {
    return \`\${(conf.center * 100).toFixed(0)}% [\${(conf.lower * 100).toFixed(0)}%–\${(conf.upper * 100).toFixed(0)}%]\`;
  }
  return \`\${(conf * 100).toFixed(0)}%\`;
}`;

const nu = `function confToPercent(conf) {
  if (conf === null) return 'N/A';
  if (typeof conf === 'object') {
    if (isNaN(conf.center)) return 'ERROR';
    return (conf.center * 100).toFixed(0) + '% [' + (conf.lower * 100).toFixed(0) + '%-' + (conf.upper * 100).toFixed(0) + '%]';
  }
  if (isNaN(conf)) return 'ERROR';
  return (conf * 100).toFixed(0) + '%';
}`;

if (!c.includes(old)) {
  // Try alternate quote style
  const idx = c.indexOf('function confToPercent');
  const end = c.indexOf('}', idx);
  const current = c.slice(idx, end + 1);
  console.log('Current function:');
  console.log(current);
  process.exit(1);
}
c = c.replace(old, nu);
fs.writeFileSync(process.argv[2], c);
console.log('done');
