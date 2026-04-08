#!/usr/bin/env node
/**
 * OMC Honcho-Inspired User Profile Deriver
 * Analyzes recent session history → extracts user work patterns → generates memory/user-profile.md
 *
 * Inspired by Hermes Agent's Honcho dialectic user modeling:
 *   https://github.com/plastic-labs/honcho
 *
 * Usage:
 *   node honcho-derive.mjs              # derive user profile from sessions
 *   node honcho-derive.mjs --dry-run    # preview without writing
 *   node honcho-derive.mjs --force      # overwrite existing profile
 *
 * Input:  .omc/sessions/*.json (recent sessions)
 * Output: .omc/memory/user-profile.md
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SESSIONS_DIR = resolve(__dirname, '../sessions');
const PROFILE_DIR = resolve(__dirname, '../memory');
const PROFILE_FILE = resolve(PROFILE_DIR, 'user-profile.md');
const STATE_FILE = resolve(__dirname, '../state/honcho-derive-state.json');
const DAYS_BACK = 14; // analyze sessions from last 14 days
const MIN_SESSIONS = 3; // need at least 3 sessions to extract patterns

const STATE = {
  get() {
    if (!existsSync(STATE_FILE)) return { lastRun: null, sessionsAnalyzed: 0, patterns: [] };
    try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
    catch { return { lastRun: null, sessionsAnalyzed: 0, patterns: [] }; }
  },
  set(s) { writeFileSync(STATE_FILE, JSON.stringify(s, null, 2), 'utf-8'); }
};

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

// ── Extract patterns from sessions ───────────────────────────────────────────
function extractPatterns(sessions) {
  const patterns = {
    preferredProjects: [],    // projects worked on most
    workHours: [],          // approximate work times
    modesUsed: [],          // OMC modes activated
    sessionDuration: [],     // how long sessions last
    toolsUsed: [],          // tools frequently invoked
    blockers: [],           // common blockers/pause reasons
    errors: [],            // repeated errors
    victories: [],         // completed features
  };

  // Counters
  const projectCounts = {};
  const hourCounts = {};
  const modeCounts = {};
  const toolCounts = {};
  const errorSet = new Set();
  const victorySet = new Set();

  for (const session of sessions) {
    if (session.started_at) {
      const d = new Date(session.started_at);
      const hour = d.getHours();
      hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    }
    if (session.duration_minutes) {
      patterns.sessionDuration.push(session.duration_minutes);
    }
    if (session.modes_used) {
      for (const m of session.modes_used) modeCounts[m] = (modeCounts[m] || 0) + 1;
    }
    if (session.tools_used) {
      for (const t of session.tools_used) toolCounts[t] = (toolCounts[t] || 0) + 1;
    }
    if (session.ended_reason && ['clear', 'interrupted'].includes(session.ended_reason)) {
      patterns.blockers.push(session.ended_reason);
    }
    if (session.project) {
      projectCounts[session.project] = (projectCounts[session.project] || 0) + 1;
    }
    if (session.victories) {
      for (const v of session.victories) victorySet.add(v);
    }
  }

  // Top-N extraction
  patterns.preferredProjects = Object.entries(projectCounts)
    .sort((a, b) => b[1] - a[1]).slice(0, 5).map(([p]) => p);
  patterns.workHours = Object.entries(hourCounts)
    .sort((a, b) => b[1] - a[1]).slice(0, 3).map(([h]) => `${h}:00`);
  patterns.modesUsed = Object.entries(modeCounts)
    .sort((a, b) => b[1] - a[1]).slice(0, 3).map(([m]) => m);
  patterns.victories = Array.from(victorySet).slice(0, 10);
  patterns.sessionDuration = patterns.sessionDuration.length > 0
    ? [Math.min(...patterns.sessionDuration), Math.max(...patterns.sessionDuration),
       Math.round(patterns.sessionDuration.reduce((a, b) => a + b, 0) / patterns.sessionDuration.length)]
    : [];

  return patterns;
}

function readSessions() {
  if (!existsSync(SESSIONS_DIR)) return [];
  const cutoff = Date.now() - DAYS_BACK * 24 * 60 * 60 * 1000;
  const files = readdirSync(SESSIONS_DIR).filter(f => f.endsWith('.json'));
  const sessions = [];

  for (const file of files) {
    try {
      const content = readFileSync(resolve(SESSIONS_DIR, file), 'utf-8');
      const session = JSON.parse(content);
      if (!session.started_at) continue;
      const ts = new Date(session.started_at).getTime();
      if (ts < cutoff) continue;
      sessions.push(session);
    } catch { /* skip corrupt files */ }
  }

  return sessions;
}

function buildProfile(patterns, stats) {
  const today = new Date().toISOString().split('T')[0];
  const durationStr = patterns.sessionDuration.length >= 3
    ? `${patterns.sessionDuration[0]}-${patterns.sessionDuration[1]}min (avg ${patterns.sessionDuration[2]}min)`
    : 'unknown';

  return `# 用户画像（自动生成 — 来自 Honcho 风格分析）

> 由 honcho-derive.mjs 自动生成 | ${today} | 分析 ${stats.sessionCount} 个 session
> **警告**：以下内容为自动推断，需人工验证准确性

## 工作模式

- **常用项目**：${patterns.preferredProjects.length > 0 ? patterns.preferredProjects.join('、') : '需要更多数据'}
- **活跃时段**：${patterns.workHours.length > 0 ? patterns.workHours.join('、') : '需要更多数据'}
- **平均会话时长**：${durationStr}
- **常用模式**：${patterns.modesUsed.length > 0 ? patterns.modesUsed.join('、') : 'autopilot / ralph / manual'}

## 偏好与习惯

<!-- 人工填充：
- 偏好详细方案 vs 直接执行
- 喜欢即时反馈 vs 批量完成
- 对代码质量容忍度
- 典型打断场景
-->

## 已知完成项

${patterns.victories.length > 0
  ? patterns.victories.map(v => `- ${v}`).join('\n')
  : '（从 session 历史中提取）'}

## 典型错误模式

<!-- 人工填充：
- 常见失误
- 反复出现的模式
- 已知的坑
-->

## 代理行为指导

<!-- 基于历史 session 的行为洞察：
- 适合自动驾驶的程度
- 需要人工确认的边界
- 偏好什么样的任务分配
-->

---
*最后更新：${today}*
`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const dryRun = !!args['dry-run'];
  const force = !!args.force;

  console.log(`\n🧠 OMC Honcho User Profile Deriver`);
  console.log(`  Sessions: ${SESSIONS_DIR}`);
  console.log(`  Profile:  ${PROFILE_FILE}`);
  console.log(`  Days:     ${DAYS_BACK}`);

  const sessions = readSessions();
  console.log(`\n  Sessions found: ${sessions.length}`);

  if (sessions.length < MIN_SESSIONS) {
    console.log(`  ⚠️  Need ≥${MIN_SESSIONS} sessions to derive patterns.`);
    console.log(`      Found ${sessions.length}. Run more sessions first.\n`);
    return;
  }

  const patterns = extractPatterns(sessions);
  const stats = { sessionCount: sessions.length, daysBack: DAYS_BACK };
  const profile = buildProfile(patterns, stats);

  console.log(`  📊 Patterns extracted:`);
  console.log(`     Projects:  ${patterns.preferredProjects.join(', ') || 'none'}`);
  console.log(`     Work hours: ${patterns.workHours.join(', ') || 'none'}`);
  console.log(`     Modes:      ${patterns.modesUsed.join(', ') || 'none'}`);
  console.log(`     Duration:   ${patterns.sessionDuration.join('-') || 'unknown'}min`);
  console.log(`     Victories:  ${patterns.victories.length}`);

  if (existsSync(PROFILE_FILE) && !force) {
    console.log(`\n  ⚠️  Profile exists. Use --force to overwrite.`);
    return;
  }

  if (dryRun) {
    console.log(`\n  [DRY RUN] Would write profile:\n`);
    console.log(profile);
    return;
  }

  if (!existsSync(PROFILE_DIR)) mkdirSync(PROFILE_DIR, { recursive: true });
  writeFileSync(PROFILE_FILE, profile, 'utf-8');

  STATE.set({
    lastRun: new Date().toISOString(),
    sessionsAnalyzed: sessions.length,
    patterns: {
      projects: patterns.preferredProjects,
      hours: patterns.workHours,
      modes: patterns.modesUsed,
    }
  });

  console.log(`\n  ✅ Profile written → ${PROFILE_FILE}`);
  console.log(`  💡 Review and edit the "preferences" and "behavior" sections.\n`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
