#!/usr/bin/env node
/**
 * OMC Honcho Dialectic
 * Multi-level reasoning to extract conclusions from session interactions.
 *
 * Inspired by Hermes Agent's Honcho dialectic user modeling (plastic-labs/honcho):
 *   - Thesis → Antithesis → Synthesis reasoning
 *   - Extracts user preferences, work patterns, decision tendencies
 *   - Peer entity system (User as dialectic partner)
 *   - Synthesizes session history into actionable insights
 *
 * Usage:
 *   node honcho-dialectic.mjs                    # analyze recent sessions
 *   node honcho-dialectic.mjs --deep "query"    # deep analysis on specific topic
 *   node honcho-dialectic.mjs --report          # generate full dialectic report
 *   node honcho-dialectic.mjs --peer user|agent # set dialectic perspective
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, appendFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SESSIONS_DIR = resolve(__dirname, '../sessions');
const STATE_DIR = resolve(__dirname, '../state');
const OUTPUT_DIR = resolve(__dirname, '../memory/dialectic');
const STATE_FILE = resolve(STATE_DIR, 'honcho-dialectic-state.json');
const REPORT_FILE = resolve(OUTPUT_DIR, 'latest-report.md');
const DAYS_BACK = 14;
const MIN_SESSIONS = 3;

function parseArgs(argv) {
  const args = { peer: 'user' };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'deep') { args.deep = argv[i + 1] || ''; i++; continue; }
      if (key === 'report') { args.report = true; continue; }
      if (key === 'peer') { args.peer = argv[i + 1] || 'user'; i++; continue; }
      if (key === 'json') { args.json = true; continue; }
      args[key] = true;
    }
  }
  return args;
}

function readState() {
  if (!existsSync(STATE_FILE)) return { analyses: [], lastAnalysis: null };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { analyses: [], lastAnalysis: null }; }
}

function writeState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function readSessions(daysBack = DAYS_BACK) {
  if (!existsSync(SESSIONS_DIR)) return [];
  const cutoff = Date.now() - daysBack * 24 * 60 * 60 * 1000;
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
    } catch { /* skip */ }
  }
  return sessions;
}

// ── Dialectic Analysis ────────────────────────────────────────────────────────
function thesisFromSessions(sessions) {
  // What does the data show?
  const projects = {};
  const modes = {};
  const blockers = [];
  const victories = [];
  let totalDuration = 0;
  let count = 0;

  for (const s of sessions) {
    if (s.project) projects[s.project] = (projects[s.project] || 0) + 1;
    if (Array.isArray(s.modes_used)) {
      for (const m of s.modes_used) modes[m] = (modes[m] || 0) + 1;
    }
    if (s.blockers) blockers.push(...s.blockers);
    if (Array.isArray(s.victories)) victories.push(...s.victories);
    if (s.duration_minutes) { totalDuration += s.duration_minutes; count++; }
  }

  return {
    summary: sessions.length >= MIN_SESSIONS ? {
      session_count: sessions.length,
      avg_duration: count > 0 ? Math.round(totalDuration / count) : 0,
      top_projects: Object.entries(projects).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([p]) => p),
      top_modes: Object.entries(modes).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([m]) => m),
      total_victories: victories.length,
      common_blockers: blockers.slice(0, 3),
    } : null,
    raw: { projects, modes, blockers, victories },
  };
}

function antithesisFromThesis(thesis) {
  // What are the contradictions, gaps, assumptions?
  const gaps = [];

  if (thesis.summary) {
    if (thesis.summary.avg_duration < 10) {
      gaps.push('Short sessions suggest fragmented work or quick task turnaround');
    }
    if (thesis.summary.top_projects.length > 2) {
      gaps.push('Multi-project work may indicate context-switching overhead');
    }
    if (thesis.summary.common_blockers.length > 0) {
      gaps.push('Repeated blockers suggest systemic issues worth addressing');
    }
  } else {
    gaps.push('Insufficient session data for confident analysis');
  }

  return { gaps, assumptions: gaps.length > 0 ? gaps : ['Default assumption: user works autonomously'] };
}

function synthesisFromDialectic(thesis, antithesis, peer = 'user') {
  // Synthesize into actionable insights
  const insights = [];
  const peerLabel = peer === 'user' ? 'user' : 'agent';

  if (thesis.summary) {
    insights.push({
      type: 'pattern',
      finding: `${peerLabel} prefers working on ${thesis.summary.top_projects[0] || 'varied projects'}`,
      confidence: thesis.summary.session_count >= 5 ? 'high' : 'medium',
      evidence: `${thesis.summary.session_count} sessions, avg ${thesis.summary.avg_duration}min`,
    });

    if (thesis.summary.top_modes.length > 0) {
      insights.push({
        type: 'preference',
        finding: `${peerLabel} frequently uses: ${thesis.summary.top_modes.join(', ')}`,
        confidence: 'medium',
        evidence: `${Object.values(thesis.raw.modes).reduce((a, b) => a + b, 0)} mode activations`,
      });
    }

    if (thesis.summary.common_blockers.length > 0) {
      insights.push({
        type: 'pain_point',
        finding: `Common blockers: ${thesis.summary.common_blockers.join(', ')}`,
        confidence: 'medium',
        evidence: 'Session-end reports',
      });
    }
  }

  // Add dialectic tensions
  const tensions = antithesis.gaps.map(g => ({
    type: 'tension',
    finding: g,
    resolution: 'Needs investigation',
  }));

  return { insights, tensions, peer };
}

// ── Report generator ─────────────────────────────────────────────────────────
function buildReport(sessions, thesis, antithesis, synthesis) {
  const today = new Date().toISOString().split('T')[0];

  let report = `# Honcho Dialectic Report
> Generated: ${today} | Sessions: ${sessions.length} | Peer: ${synthesis.peer}

## Thesis (What the data shows)

`;
  if (thesis.summary) {
    report += `**Session Count**: ${thesis.summary.session_count}
**Avg Duration**: ${thesis.summary.avg_duration}min
**Top Projects**: ${thesis.summary.top_projects.join(' → ') || 'none'}
**Top Modes**: ${thesis.summary.top_modes.join(', ') || 'none'}
**Victories**: ${thesis.summary.total_victories} completed
`;
  } else {
    report += `Insufficient data (${sessions.length}/${MIN_SESSIONS} sessions needed)\n`;
  }

  report += `
## Antithesis (Contradictions and gaps)

`;
  if (antithesis.gaps.length > 0) {
    for (const g of antithesis.gaps) {
      report += `- ${g}\n`;
    }
  } else {
    report += `- No significant gaps detected\n`;
  }

  report += `
## Synthesis (Actionable insights)

### Patterns
`;
  for (const i of synthesis.insights.filter(i => i.type === 'pattern')) {
    report += `- **[${i.confidence}]** ${i.finding}\n  *Evidence*: ${i.evidence}\n`;
  }

  report += `
### Preferences
`;
  for (const i of synthesis.insights.filter(i => i.type === 'preference')) {
    report += `- **[${i.confidence}]** ${i.finding}\n  *Evidence*: ${i.evidence}\n`;
  }

  report += `
### Pain Points
`;
  for (const i of synthesis.insights.filter(i => i.type === 'pain_point')) {
    report += `- **[${i.confidence}]** ${i.finding}\n  *Evidence*: ${i.evidence}\n`;
  }

  report += `
### Tensions (requiring resolution)
`;
  for (const t of synthesis.tensions) {
    report += `- ${t.finding} → ${t.resolution}\n`;
  }

  report += `
---
*Generated by OMC Honcho Dialectic (Hermes-inspired)*
`;
  return report;
}

// ── Deep analysis on specific topic ─────────────────────────────────────────
function deepAnalysis(query, sessions) {
  const queryLower = query.toLowerCase();
  const relevant = sessions.filter(s => {
    const text = [
      s.project || '',
      s.summary || '',
      s.activities || '',
      Array.isArray(s.victories) ? s.victories.join(' ') : '',
    ].join(' ').toLowerCase();
    return text.includes(queryLower);
  });

  return {
    query,
    sessions_analyzed: sessions.length,
    relevant_sessions: relevant.length,
    findings: relevant.map(s => ({
      date: s.started_at?.split('T')[0],
      project: s.project,
      summary: s.summary,
      activities: s.activities,
    })),
  };
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.report) {
    const sessions = readSessions();
    if (sessions.length < MIN_SESSIONS) {
      console.log(`Need ≥${MIN_SESSIONS} sessions for dialectic analysis (found ${sessions.length})`);
      return;
    }

    const thesis = thesisFromSessions(sessions);
    const antithesis = antithesisFromThesis(thesis);
    const synthesis = synthesisFromDialectic(thesis, antithesis, args.peer);
    const report = buildReport(sessions, thesis, antithesis, synthesis);

    if (!existsSync(OUTPUT_DIR)) mkdirSync(OUTPUT_DIR, { recursive: true });
    writeFileSync(REPORT_FILE, report, 'utf-8');

    const state = readState();
    state.lastAnalysis = new Date().toISOString();
    state.analyses.push({ date: state.lastAnalysis, peer: args.peer, sessionCount: sessions.length });
    writeState(state);

    console.log(`\n📊 Honcho Dialectic Report`);
    console.log(`  Sessions: ${sessions.length}`);
    console.log(`  Peer: ${args.peer}`);
    console.log(`  Output: ${REPORT_FILE}\n`);
    console.log(report.slice(0, 500) + '...\n');
    return;
  }

  if (args.deep) {
    const sessions = readSessions();
    const analysis = deepAnalysis(args.deep, sessions);

    if (args.json) {
      console.log(JSON.stringify(analysis, null, 2));
    } else {
      console.log(`\n🔍 Deep Analysis: "${args.deep}"`);
      console.log(`  Relevant: ${analysis.relevant_sessions}/${analysis.sessions_analyzed} sessions`);
      for (const f of analysis.findings.slice(0, 5)) {
        console.log(`  [${f.date}] ${f.project}`);
        console.log(`    ${f.summary || f.activities || '(no summary)'}`);
      }
      console.log();
    }
    return;
  }

  // Default: quick summary
  const sessions = readSessions();
  console.log(`\n📊 Honcho Dialectic`);
  console.log(`  Sessions: ${sessions.length}/${MIN_SESSIONS} needed`);
  if (sessions.length >= MIN_SESSIONS) {
    console.log(`  Run --report for full dialectic analysis`);
    console.log(`  Run --deep "topic" for deep analysis`);
  }
  console.log();
}

main().catch(e => { console.error(e.message); process.exit(1); });
