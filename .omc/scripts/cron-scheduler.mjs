#!/usr/bin/env node
/**
 * OMC Natural Language Cron Scheduler
 * Schedules periodic tasks using natural language descriptions.
 *
 * Inspired by Hermes Agent's Cron system:
 *   - Natural language configured cron jobs (not traditional cron syntax)
 *   - Autonomous agent decides when to run periodic tasks
 *   - Supports: daily reports, weekly summaries, periodic audits, backups
 *   - Platform delivery (hooks, notifications, etc.)
 *
 * Usage:
 *   node cron-scheduler.mjs --add "自然语言描述" [--interval N]    Add a cron job
 *   node cron-scheduler.mjs --list                                    List jobs
 *   node cron-scheduler.mjs --remove id                              Remove a job
 *   node cron-scheduler.mjs --check                                   Check & fire due jobs
 *   node cron-scheduler.mjs --parse "描述"                            Parse natural lang → cron expr
 *
 * Architecture:
 *   - Jobs stored in .omc/state/cron-jobs.json
 *   - --check is called periodically (e.g., by hook or external cron)
 *   - Supports: every N minutes, hourly, daily, weekly, monthly
 *   - Next-run calculation from natural language
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'cron-jobs.json');
const CRON_STATE = resolve(STATE_DIR, 'cron-state.json');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'add') { args.add = argv[i + 1] || ''; i++; continue; }
      if (key === 'remove') { args.remove = argv[i + 1] || ''; i++; continue; }
      if (key === 'interval') { args.interval = parseInt(argv[i + 1]) || 60; i++; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readJobs() {
  if (!existsSync(STATE_FILE)) return [];
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return []; }
}

function writeJobs(jobs) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(jobs, null, 2), 'utf-8');
}

function readCronState() {
  if (!existsSync(CRON_STATE)) return { lastCheck: null, firedJobs: {} };
  try { return JSON.parse(readFileSync(CRON_STATE, 'utf-8')); }
  catch { return { lastCheck: null, firedJobs: {} }; }
}

function writeCronState(state) {
  writeFileSync(CRON_STATE, JSON.stringify(state, null, 2), 'utf-8');
}

// ── Natural language → interval parser ─────────────────────────────────────
function parseNaturalLanguage(text) {
  const lower = text.toLowerCase();
  const now = new Date();

  // Minute-level
  if (lower.includes('每分钟') || lower.includes('every minute')) {
    return { interval: 1, unit: 'minute', next: addMinutes(now, 1) };
  }
  if (lower.includes('每5分钟') || lower.match(/every\s+5\s*minutes?/)) {
    return { interval: 5, unit: 'minute', next: addMinutes(now, 5) };
  }
  if (lower.match(/每?(\d+)\s*分钟/)) {
    const mins = parseInt(lower.match(/(\d+)\s*分钟/)[1]);
    return { interval: mins, unit: 'minute', next: addMinutes(now, mins) };
  }

  // Hourly
  if (lower.includes('每小时') || lower.includes('hourly')) {
    return { interval: 60, unit: 'hour', next: addHours(now, 1) };
  }
  if (lower.match(/每?(\d+)\s*小时/)) {
    const hours = parseInt(lower.match(/(\d+)\s*小时/)[1]);
    return { interval: hours * 60, unit: 'hour', next: addHours(now, hours) };
  }

  // Daily
  if (lower.includes('每天') || lower.includes('daily')) {
    return { interval: 1440, unit: 'day', next: startOfDay(addDays(now, 1)) };
  }

  // Weekly
  if (lower.includes('每周') || lower.includes('weekly')) {
    return { interval: 10080, unit: 'week', next: startOfDay(addDays(now, 7)) };
  }

  // Morning/evening
  if (lower.includes('早上') || lower.includes('上午') || lower.includes('morning')) {
    return { interval: 1440, unit: 'day', next: setTime(startOfDay(addDays(now, 1)), 9, 0) };
  }
  if (lower.includes('晚上') || lower.includes('evening')) {
    return { interval: 1440, unit: 'day', next: setTime(startOfDay(addDays(now, 1)), 20, 0) };
  }

  // Default: daily
  return { interval: 1440, unit: 'day', next: startOfDay(addDays(now, 1)) };
}

function addMinutes(d, mins) { return new Date(d.getTime() + mins * 60000); }
function addHours(d, hours) { return addMinutes(d, hours * 60); }
function addDays(d, days) { return addMinutes(d, days * 1440); }
function startOfDay(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
function setTime(d, h, m) { d.setHours(h, m, 0, 0); return d; }

// ── Classify job type ───────────────────────────────────────────────────────
function classifyJob(text) {
  const lower = text.toLowerCase();
  if (lower.includes('报告') || lower.includes('report')) return 'report';
  if (lower.includes('总结') || lower.includes('summary')) return 'summary';
  if (lower.includes('备份') || lower.includes('backup')) return 'backup';
  if (lower.includes('审计') || lower.includes('audit')) return 'audit';
  if (lower.includes('清理') || lower.includes('cleanup')) return 'cleanup';
  if (lower.includes('同步') || lower.includes('sync')) return 'sync';
  return 'general';
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.add) {
    const parsed = parseNaturalLanguage(args.add);
    const id = `job-${Date.now()}`;
    const job = {
      id,
      description: args.add,
      type: classifyJob(args.add),
      interval: parsed.interval,
      unit: parsed.unit,
      next_run: parsed.next.toISOString(),
      created: new Date().toISOString(),
      last_run: null,
      run_count: 0,
    };

    const jobs = readJobs();
    jobs.push(job);
    writeJobs(jobs);

    console.log(`\n✅ Cron job added: ${id}`);
    console.log(`   Description: ${args.add}`);
    console.log(`   Schedule: every ${parsed.interval} ${parsed.unit}`);
    console.log(`   Next run: ${parsed.next.toLocaleString('zh-CN')}\n`);
    return;
  }

  if (args.remove) {
    const jobs = readJobs();
    const before = jobs.length;
    const filtered = jobs.filter(j => j.id !== args.remove && j.id !== String(args.remove));
    writeJobs(filtered);
    console.log(`Removed ${before - filtered.length} job(s)\n`);
    return;
  }

  if (args.list) {
    const jobs = readJobs();
    console.log(`\n📅 OMC Cron Scheduler`);
    console.log(`  Jobs: ${jobs.length}\n`);
    for (const j of jobs) {
      const next = j.next_run ? new Date(j.next_run).toLocaleString('zh-CN') : 'not set';
      const last = j.last_run ? new Date(j.last_run).toLocaleString('zh-CN') : 'never';
      console.log(`  [${j.id}] ${j.type}`);
      console.log(`    ${j.description}`);
      console.log(`    Every ${j.interval} ${j.unit} | Next: ${next} | Last: ${last} | Runs: ${j.run_count}`);
    }
    console.log();
    return;
  }

  if (args.check) {
    const jobs = readJobs();
    const now = Date.now();
    const cronState = readCronState();
    const fired = [];

    for (const job of jobs) {
      const nextTime = new Date(job.next_run).getTime();
      if (nextTime <= now) {
        console.log(`FIRE:${JSON.stringify({ id: job.id, description: job.description, type: job.type, interval: job.interval })}`);

        // Update next run
        job.last_run = new Date().toISOString();
        job.run_count++;
        job.next_run = new Date(nextTime + job.interval * 60000).toISOString();

        fired.push(job.id);
      }
    }

    writeJobs(jobs);
    cronState.lastCheck = new Date().toISOString();
    cronState.firedJobs = { ...cronState.firedJobs, [new Date().toISOString()]: fired };
    writeCronState(cronState);

    if (fired.length === 0) {
      console.log(`No jobs due (checked ${jobs.length} jobs)`);
    } else {
      console.log(`Fired ${fired.length} job(s)`);
    }
    return;
  }

  if (args.parse) {
    const parsed = parseNaturalLanguage(args.parse);
    console.log(`\n🔍 Parse: "${args.parse}"`);
    console.log(`   Interval: ${parsed.interval} ${parsed.unit}`);
    console.log(`   Next run: ${parsed.next.toLocaleString('zh-CN')}\n`);
    return;
  }

  // Default: help
  console.log(`OMC Natural Language Cron Scheduler`);
  console.log(`Usage:`);
  console.log(`  --add "自然语言描述"   Add a periodic job`);
  console.log(`  --list                List all jobs`);
  console.log(`  --remove id           Remove a job`);
  console.log(`  --check               Check and fire due jobs (call periodically)`);
  console.log(`  --parse "描述"         Parse natural language → interval`);
  console.log(`\nExamples:`);
  console.log(`  --add "每天早上生成工作报告"`);
  console.log(`  --add "每小时检查新issue"`);
  console.log(`  --add "每周生成总结"`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
