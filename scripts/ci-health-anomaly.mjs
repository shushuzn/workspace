#!/usr/bin/env node
/**
 * scripts/ci-health-anomaly.mjs
 * Time-series anomaly detection on CI health scores.
 * Uses CUSUM (cumulative sum) changepoint detection + exponential smoothing.
 *
 * Usage:
 *   node scripts/ci-health-anomaly.mjs          # show anomaly status + alert
 *   node scripts/ci-health-anomaly.mjs trend   # show score with anomaly markers
 *   node scripts/ci-health-anomaly.mjs predict # predict next score + threshold breach ETA
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__dirname, '..', 'ci-health-history.jsonl');
const HEALTH_FILE = join(__dirname, '..', 'ci-health.json');

const SCORE_THRESHOLD = 60;
const DROP_THRESHOLD = 15;
const CUSUM_DRIFT = 0.5;   // CUSUM k: minimal detectable shift (per-step)
const CUSUM_THRESHOLD = 5;  // CUSUM h: decision boundary

function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  try {
    const content = readFileSync(HISTORY_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

// ── CUSUM changepoint detection ───────────────────────────────────────────────
/**
 * CUSUM: detects when a process shifts away from a target mean.
 * Returns { cusum, shifted, changePoint } where shifted=true means
 * the score has deviated significantly from the expected baseline.
 */
function cusum(scores, target = null) {
  if (scores.length < 3) return { cusum: 0, shifted: false, changePoint: null };

  const mean = target ?? scores.slice(0, Math.max(1, Math.floor(scores.length * 0.6))).reduce((a, b) => a + b, 0) / Math.max(1, Math.floor(scores.length * 0.6));
  const std = Math.sqrt(scores.slice(0, Math.max(1, Math.floor(scores.length * 0.6))).reduce((s, x) => s + (x - mean) ** 2, 0) / Math.max(1, Math.floor(scores.length * 0.6)));

  let S = 0;
  let maxS = 0;
  let changePoint = null;

  for (let i = 0; i < scores.length; i++) {
    const x = scores[i];
    const z = std > 0 ? (x - mean) / std : 0;
    // Lower-tail CUSUM: detect drops
    S = Math.max(0, S + z - CUSUM_DRIFT);
    if (S > maxS) {
      maxS = S;
      changePoint = i;
    }
  }

  return {
    cusum: maxS,
    shifted: maxS > CUSUM_THRESHOLD,
    changePoint: changePoint !== null ? changePoint : null
  };
}

// ── Exponential smoothing forecast ─────────────────────────────────────────────
function expSmooth(scores, alpha = 0.3) {
  if (scores.length === 0) return null;
  let forecast = scores[0];
  return scores.map(s => {
    forecast = alpha * s + (1 - alpha) * forecast;
    return forecast;
  });
}

function predictBreach(scores, threshold = SCORE_THRESHOLD) {
  if (scores.length < 3) return { eta: null, confidence: 0 };

  // Fit linear regression on recent window
  const window = scores.slice(-10);
  const n = window.length;
  const xMean = (n - 1) / 2;
  const yMean = window.reduce((a, b) => a + b, 0) / n;

  let num = 0, den = 0;
  for (let i = 0; i < n; i++) {
    num += (i - xMean) * (window[i] - yMean);
    den += (i - xMean) ** 2;
  }

  const slope = den !== 0 ? num / den : 0;
  const intercept = yMean - slope * xMean;

  if (slope >= 0) return { eta: null, confidence: 0, trend: 'stable/rising' };

  // ETA = (threshold - intercept) / slope
  const eta = Math.ceil((threshold - intercept) / slope);

  // Confidence based on fit quality (R²)
  let ssRes = 0, ssTot = 0;
  for (let i = 0; i < n; i++) {
    const pred = intercept + slope * i;
    ssRes += (window[i] - pred) ** 2;
    ssTot += (window[i] - yMean) ** 2;
  }
  const r2 = ssTot !== 0 ? 1 - ssRes / ssTot : 0;

  return { eta: eta > 0 ? eta : null, confidence: Math.max(0, r2), trend: 'falling' };
}

// ── Anomaly scoring ────────────────────────────────────────────────────────────
function anomalyScore(history) {
  if (history.length < 3) return { score: 0, level: 'unknown', reasons: [] };

  const scores = history.map(h => h.score);
  const { cusum: cusumVal, shifted, changePoint } = cusum(scores);

  // Recent drop
  const recent = scores.slice(-5);
  const drop = recent.length >= 2 ? recent[0] - recent[recent.length - 1] : 0;

  // Streak: consecutive below-threshold
  const belowThresh = [...scores].reverse().findIndex(s => s >= SCORE_THRESHOLD);
  const streak = belowThresh >= 0 ? belowThresh : scores.length;

  // Prediction
  const pred = predictBreach(scores);

  // Compute composite anomaly score (0-100)
  let anomScore = 0;
  const reasons = [];

  if (shifted) {
    anomScore += 40;
    reasons.push(`CUSUM shift detected at position ${changePoint} (cusum=${cusumVal.toFixed(1)})`);
  }

  if (drop >= 10) {
    anomScore += 25;
    reasons.push(`Recent drop: ${drop.toFixed(1)} points`);
  } else if (drop >= 5) {
    anomScore += 10;
    reasons.push(`Moderate drop: ${drop.toFixed(1)} points`);
  }

  if (streak <= 3 && streak < scores.length) {
    anomScore += 15;
    reasons.push(`Below-threshold streak: ${streak} consecutive runs`);
  }

  if (pred.eta !== null && pred.confidence > 0.5) {
    anomScore += 20;
    reasons.push(`Threshold breach ETA: ~${pred.eta} runs (confidence: ${(pred.confidence * 100).toFixed(0)}%)`);
  }

  let level;
  if (anomScore >= 60) level = '🔴 CRITICAL';
  else if (anomScore >= 35) level = '🟡 ATTENTION';
  else level = '🟢 HEALTHY';

  return { score: Math.min(100, anomScore), level, reasons, pred, drop, streak, shifted };
}

function printTrend(history) {
  if (history.length < 3) {
    console.log('Not enough data for trend visualization (need ≥3 runs).');
    return;
  }

  const scores = history.map(h => h.score).slice(-20);
  const min = Math.min(...scores) - 5;
  const max = Math.max(...scores) + 5;

  console.log('\n=== CI Health Trend with Anomaly Detection ===\n');

  // Score chart (ASCII)
  for (let v = Math.ceil(max); v >= Math.floor(min); v -= 5) {
    let row = v >= 100 ? `${v}|` : `${v >= 0 ? ' ' : ''}${v}|`;
    if (v === SCORE_THRESHOLD) row += ' ';
    else if (v === 60) row += ' ';
    else row += '  ';

    for (const s of scores) {
      if (s >= v && s < v + 5) row += '█';
      else if (v === SCORE_THRESHOLD && s < v) row += '─';
      else row += ' ';
    }

    if (v === SCORE_THRESHOLD) row += ` ← THRESHOLD (${SCORE_THRESHOLD})`;
    console.log(row);
  }

  const { cusum: cv, shifted } = cusum(scores);
  if (shifted) {
    console.log('\n⚠️  CUSUM: drift detected (cusum=' + cv.toFixed(1) + ')');
  }

  const pred = predictBreach(scores);
  if (pred.eta !== null) {
    console.log(`\n📉 Linear forecast: threshold breach in ~${pred.eta} runs (R²=${pred.confidence.toFixed(2)})`);
  }
  console.log();
}

async function main() {
  const history = loadHistory();
  const cmd = process.argv[2];

  if (cmd === 'trend') {
    printTrend(history);
    return;
  }

  if (cmd === 'predict') {
    const scores = history.map(h => h.score);
    const pred = predictBreach(scores);
    if (pred.eta === null) {
      console.log(`\n✅ Score trend stable/rising — no threshold breach predicted`);
    } else {
      console.log(`\n📉 Predict: threshold breach in ~${pred.eta} runs (confidence: ${(pred.confidence * 100).toFixed(0)}%)`);
    }
    return;
  }

  // Default: anomaly status
  const { score: anomScore, level, reasons, pred, drop, streak, shifted } = anomalyScore(history);

  console.log('\n=== CI Health Anomaly Detection ===\n');

  const last = history[history.length - 1];
  console.log(`${level}  Anomaly Score: ${anomScore}/100`);
  if (last) console.log(`Latest: score=${last.score} date=${last.date}`);

  if (reasons.length > 0) {
    console.log('\nAnomaly factors:');
    for (const r of reasons) console.log(`  ⚠️  ${r}`);
  }

  // Early warning
  if (drop >= 5 && drop < 10) {
    console.log(`\n⚡ EARLY WARNING: moderate drop (${drop.toFixed(1)} pts) — monitor closely`);
    console.log('  Run: node scripts/ci-health-anomaly.mjs predict  # for ETA');
  } else if (drop >= 10) {
    console.log(`\n🚨 EARLY WARNING: severe drop (${drop.toFixed(1)} pts)`);
    console.log('  Run: node scripts/ci-health-anomaly.mjs predict  # for ETA');
  }

  console.log();
  process.exit(shifted || anomScore >= 35 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
