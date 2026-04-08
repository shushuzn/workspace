import { existsSync, readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TRAJ_DIR = resolve(__dirname, '../trajectories');
const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');
const MANIFEST_FILE = resolve(__dirname, '../state/insight-gen-manifest.json');

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

Rules:
- Look for patterns: tool usage imbalances, missing seed generation, debugging loops, workflow inefficiencies
- Title should be a short phrase (under 10 words)
- Observation must reference specific numbers/metrics from the trajectory
- Generate 1-3 insights max — quality over quantity
- If trajectory shows good productivity with seeds, note what worked
- Skip if session was too short (< 5 tool calls)

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
  const trajPath = findLatestTraj();
  if (!trajPath) { log('no trajectory found'); return; }

  const trajStat = statSync(trajPath);
  if (isTrajectoryProcessed(trajPath, trajStat.mtimeMs)) {
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
  log('generated insights:', insightLines.filter(l => l.startsWith('###')).join(', '));
}

main().catch(e => { log('error:', e.message); });
