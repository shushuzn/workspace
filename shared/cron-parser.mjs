#!/usr/bin/env node
/**
 * cron-parser.mjs
 * 解析和验证cron表达式，返回下次触发时间
 */
function parseCron(cron) {
  const parts = cron.trim().split(/\s+/);
  if (parts.length < 5) return { valid: false, error: '需要5个字段: 分 时 日 月 周' };
  const [min, hour, day, month, dow] = parts;
  const validate = (v, max) => {
    if (v === '*') return true;
    if (/^\d+$/.test(v)) return parseInt(v) <= max;
    if (v.includes('/')) { const [base, step] = v.split('/'); return (base === '*' || validate(base, max)) && /^\d+$/.test(step); }
    if (v.includes(',')) return v.split(',').every(x => validate(x, max));
    if (v.includes('-')) { const [a,b] = v.split('-').map(Number); return a <= b && b <= max; }
    return false;
  };
  if (!validate(min, 59)) return { valid: false, error: '分字段无效(0-59)' };
  if (!validate(hour, 23)) return { valid: false, error: '时字段无效(0-23)' };
  if (!validate(day, 31)) return { valid: false, error: '日字段无效(1-31)' };
  if (!validate(month, 12)) return { valid: false, error: '月字段无效(1-12)' };
  if (!validate(dow, 7)) return { valid: false, error: '周字段无效(0-7)' };
  return { valid: true };
}

function getNextRun(cron) {
  const p = parseCron(cron);
  if (!p.valid) return null;
  const parts = cron.trim().split(/\s+/);
  const [min, hour, day, month, dow] = parts;
  const now = new Date();
  const start = new Date(now);
  start.setSeconds(0);
  start.setMilliseconds(0);

  for (let offset = 1; offset < 525600; offset++) {
    const candidate = new Date(start.getTime() + offset * 60000);
    const m = candidate.getMinutes();
    const h = candidate.getHours();
    const d = candidate.getDate();
    const mo = candidate.getMonth() + 1;
    const w = candidate.getDay();

    const matchField = (f, val) => {
      if (f === '*') return true;
      if (f.includes('/')) { const [base, step] = f.split('/'); const stepNum = parseInt(step); if (base === '*') return val % stepNum === 0; }
      if (/^\d+$/.test(f)) return parseInt(f) === val;
      if (f.includes(',')) return f.split(',').some(x => matchField(x.trim(), val));
      if (f.includes('-')) { const [a,b] = f.split('-').map(Number); return val >= a && val <= b; }
      return false;
    };

    if (matchField(min, m) && matchField(hour, h) && matchField(day, d) && matchField(month, mo) && matchField(dow, w)) {
      return candidate;
    }
  }
  return null;
}

function main() {
  const tests = ['*/5 * * * *', '0 9 * * 1-5', '30 14 28 2 *', 'invalid', '* * * *'];
  for (const cron of tests) {
    const p = parseCron(cron);
    console.log(`${cron} → ${p.valid ? 'VALID' : 'INVALID: ' + p.error}`);
  }

  const next = getNextRun('*/5 * * * *');
  console.log('next */5 run:', next ? next.toISOString() : 'unknown');
}

main();
