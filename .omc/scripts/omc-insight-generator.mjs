import { existsSync, readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TRAJ_DIR = resolve(__dirname, '../trajectories');
const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');
const MANIFEST_FILE = resolve(__dirname, '../state/insight-gen-manifest.json');
const PENDING_FILE = resolve(__dirname, '../state/pending-actions.md');

function log(...a) { console.log('[insight-gen]', ...a); }

function loadManifest() {
  if (!existsSync(MANIFEST_FILE)) return {};
  try { return JSON.parse(readFileSync(MANIFEST_FILE, 'utf-8')); } catch { return {}; }
}

function saveManifest(m) {
  try { writeFileSync(MANIFEST_FILE, JSON.stringify(m, null, 2)); } catch {}
}

function isTrajectoryProcessed(trajPath, trajMtime) {
  const m = loadManifest();
  return m[trajPath] === trajMtime;
}

function markTrajectoryProcessed(trajPath, trajMtime) {
  const m = loadManifest();
  m[trajPath] = trajMtime;
  saveManifest(m);
}

function extractPendingActionsViaAgent(rawInsights) {
  // Sub-agent: extract actionable Fix: fields from LLM-generated insights
  const prompt = `You are an OMC pending-action extractor. Read the insights below and extract only those with a concrete, executable Fix action (not "N/A").

Output format — write ONLY lines like this, nothing else:
ACTION|insight title|executable fix description

Rules:
- Only output lines where Fix: is a concrete action (not "N/A", not a tracking rule)
- If no actionable fixes found, output nothing
- Do NOT invent or infer fixes — only use what is explicitly stated

---
INSIGHTS:
${rawInsights}
---`;

  return new Promise((resolve) => {
    const proc = spawn('claude.cmd', ['--print'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: __dirname,
      shell: true,
    });

    let out = '';
    proc.stdout.on('data', d => { out += d.toString(); });
    proc.on('close', () => {
      const actionLines = out.split('\n').filter(l => l.startsWith('ACTION|'));
      if (actionLines.length === 0) { resolve([]); return; }

      const existing = existsSync(PENDING_FILE) ? readFileSync(PENDING_FILE, 'utf-8') : '';
      const newItems = [];
      for (const line of actionLines) {
        const parts = line.split('|');
        if (parts.length < 3) continue;
        const [, title, action] = parts;
        const id = `action-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
        newItems.push(`- [ ] ${title.trim()} | action: ${action.trim()} | id: ${id}`);
      }
      if (newItems.length > 0) {
        writeFileSync(PENDING_FILE, (existing ? existing + '\n' : '') + newItems.join('\n') + '\n', 'utf-8');
        log(`extracted ${newItems.length} pending actions via sub-agent`);
      }
      resolve(newItems);
    });
    proc.on('error', () => resolve([]));
    proc.stdin.write(prompt);
    proc.stdin.end();
  });
}

// Read current transcript and extract live stats + command samples for mid-session insight
function readLiveStats() {
  const sessionId = process.env.OMC_SESSION_ID;
  const transcriptPath = sessionId
    ? `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`
    : null;
  if (!transcriptPath || !existsSync(transcriptPath)) return null;
  try {
    const lines = readFileSync(transcriptPath, 'utf-8').split('\n').filter(Boolean);
    const tools = { Bash: 0, Read: 0, Write: 0, Edit: 0, Grep: 0, TaskCreate: 0, TaskUpdate: 0 };
    const bashCommands = []; // top bash commands
    let events = 0, toolCalls = 0, seeds = 0, userPrompts = 0;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        events++;
        if (entry.type === 'user' || entry.message?.role === 'user') userPrompts++;
        const content = entry.message?.content;
        if (Array.isArray(content)) {
          for (const block of content) {
            if (block.type === 'tool_use' && block.name) {
              toolCalls++;
              for (const t of Object.keys(tools)) { if (block.name.includes(t)) tools[t]++; }
              if (block.name === 'Bash' && block.input?.command) {
                bashCommands.push(block.input.command.slice(0, 80));
              }
            }
            if (block.type === 'text' && block.text?.includes('ideas.md')) seeds++;
          }
        }
        if (entry.type === 'tool_result' && entry.content?.includes('ideas.md')) seeds++;
      } catch {}
    }
    // Deduplicate bash commands, keep top 10
    const topBash = [...new Set(bashCommands)].slice(0, 10);
    return { events, toolCalls, tools, seeds, userPrompts, lines: lines.length, topBash };
  } catch { return null; }
}

function findLatestTraj() {
  if (!existsSync(TRAJ_DIR)) return null;
  let latest = null;
  let latestMtime = 0;
  const files = readdirSync(TRAJ_DIR).filter(f => f.endsWith('.md'));
  for (const f of files) {
    const p = resolve(TRAJ_DIR, f);
    const s = statSync(p);
    if (s.mtimeMs > latestMtime) { latestMtime = s.mtimeMs; latest = p; }
  }
  return latest;
}

function buildPrompt(traj) {
  return `You are an OMC self-learning insight generator. Analyze this session trajectory and generate 1-3 high-value insights.

Output format — write ONLY the insights, nothing else. Each insight as:
### N. [title]
**Observation**: [specific observation from the data]
**Rule**: [what to track/change in future sessions]
**Fix**: [concrete action to implement this fix, if directly executable; otherwise write "N/A"]

Rules:
- Look for patterns: tool usage imbalances, missing seed generation, debugging loops, workflow inefficiencies
- Title should be a short phrase (under 10 words)
- Observation must reference specific numbers/metrics from the trajectory
- Generate 1-3 insights max — quality over quantity
- If trajectory shows good productivity with seeds, note what worked
- Skip if session was too short (< 5 tool calls)
- **Fix**: Only write a concrete executable action (e.g. "Add 500ms dedup window in hook-audit-log-mcp", "Write fs.readFileSync替代Edit for complex strings"). If the insight only describes what to track/monitor without a specific fix, write "N/A" — do NOT invent a fix.

---
TRAJECTORY:
${traj}
---
`;
}

function generateInsightsClaude(traj) {
  return new Promise((resolve) => {
    const prompt = buildPrompt(traj);
    const proc = spawn('claude.cmd', ['--print'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: __dirname,
      shell: true,
    });

    let out = '', err = '';
    proc.stdout.on('data', d => { out += d.toString(); });
    proc.stderr.on('data', d => { err += d.toString(); });

    proc.on('close', (code) => {
      if (code !== 0 && err) log('claude error:', err.slice(0, 200));
      resolve(out);
    });
    proc.on('error', (e) => {
      log('spawn error:', e.message);
      resolve('');
    });

    proc.stdin.write(prompt);
    proc.stdin.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  const liveIdx = args.indexOf('--live');
  const trajArgIdx = args.indexOf('--transcript');

  // --live: mid-session analysis from current transcript (no trajectory file needed)
  if (liveIdx >= 0) {
    const stats = readLiveStats();
    if (!stats) { log('no live stats available'); return; }
    const livePrompt = `You are an OMC self-learning insight generator. Analyze this mid-session data and generate 1-3 high-value insights with concrete, executable fixes.

Output format — write ONLY the insights, nothing else. Each insight as:
### N. [title]
**Problem**: [specific bad pattern observed in the data]
**RootCause**: [why this is happening]
**Fix**: [concrete action to fix — specific file, script, or code change; write "N/A" if no executable fix]

Rules:
- Look for: tool imbalances, missing seeds, debugging loops, workflow inefficiencies, repeated bash commands that could be scripts
- Top Bash commands are shown — if a command repeats 3+ times, suggest extracting it to a script
- Generate 1-3 insights max — quality over quantity
- **Fix**: Must be a specific executable action (e.g. "Extract repeated git grep to a reusable script", "Add 500ms dedup in hook-audit-log-mcp"). If only a tracking rule, write "N/A"
- Do NOT invent fixes — only use what the data clearly points to

---
MID-SESSION DATA:
${JSON.stringify(stats, null, 2)}
---`;
    const rawOutput = await generateInsightsClaude(livePrompt);
    if (!rawOutput?.trim()) { log('no insights generated'); return; }
    log('live analysis:', stats.events, 'events,', stats.toolCalls, 'tool calls');
    const existing = existsSync(INSIGHTS_FILE) ? readFileSync(INSIGHTS_FILE, 'utf-8') : '';
    const entry = `\n## Mid-Session Live Insight\n\n${rawOutput.trim()}\n`;
    writeFileSync(INSIGHTS_FILE, existing + entry, 'utf-8');
    log('live insight appended to session-insights.md');
    // Also extract pending actions
    await extractPendingActionsViaAgent(rawOutput);
    return;
  }

  const trajPath = trajArgIdx >= 0 && args[trajArgIdx + 1]
    ? resolve(args[trajArgIdx + 1])
    : findLatestTraj();
  if (!trajPath) { log('no trajectory found'); return; }

  const trajStat = statSync(trajPath);
  const isMidSession = trajArgIdx >= 0;
  if (!isMidSession && isTrajectoryProcessed(trajPath, trajStat.mtimeMs)) {
    log('trajectory already processed');
    return;
  }

  const content = readFileSync(trajPath, 'utf-8');
  log('analyzing trajectory:', trajPath.split('/').pop());

  const rawOutput = await generateInsightsClaude(content);
  if (!rawOutput || !rawOutput.trim()) {
    log('no output from claude');
    return;
  }

  const lines = rawOutput.split('\n');
  const insightLines = [];
  let inInsight = false;

  for (const line of lines) {
    if (line.match(/^#{1,3}\s+\d+\./)) {
      inInsight = true;
    }
    if (inInsight) {
      insightLines.push(line);
      if (line.trim() === '' && insightLines.length > 5) break;
    }
  }

  if (insightLines.length < 3) {
    log('no valid insights in output, raw:', rawOutput.slice(0, 200));
    return;
  }

  const insightsMd = insightLines.join('\n').trim();
  if (!insightsMd) { log('empty insights'); return; }

  let existing = '';
  if (existsSync(INSIGHTS_FILE)) {
    existing = readFileSync(INSIGHTS_FILE, 'utf-8');
  }

  const existingNums = [...(existing.matchAll(/### (\d+)\./g))];
  const maxNum = existingNums.length > 0
    ? Math.max(...[...existingNums].map(m => parseInt(m[1])))
    : 0;

  let counter = maxNum + 1;
  let md = '';
  for (const line of insightLines) {
    if (line.match(/^#{1,3}\s+\d+\./)) {
      md += `### ${counter}. ${line.replace(/^#{1,3}\s+\d+\.\s*/, '')} [auto-generated]\n`;
      counter++;
    } else {
      md += line + '\n';
    }
  }

  writeFileSync(INSIGHTS_FILE, existing + '\n' + md + '\n', 'utf-8');
  markTrajectoryProcessed(trajPath, trajStat.mtimeMs);
  await extractPendingActionsViaAgent(rawOutput);
  log('generated insights:', insightLines.filter(l => l.startsWith('###')).join(', '));
}

main().catch(e => { log('error:', e.message); });
