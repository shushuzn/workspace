#!/usr/bin/env node
/**
 * ci-recommend-calc.mjs
 * Shared Thompson Sampling recommendation engine.
 * Used by: ci-fix-runner.mjs (--recommend) + ci-fix-effectiveness-dashboard.mjs
 */
import { existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = join(__dirname, '..', 'ci-state.json');
const PATTERNS_FILE = join(__dirname, 'ci-failure-patterns.jsonl');

export function loadPatterns() {
  if (!existsSync(PATTERNS_FILE)) return [];
  try {
    const content = readFileSync(PATTERNS_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

export function loadFixHistory() {
  if (!existsSync(STATE_FILE)) return {};
  try {
    const state = JSON.parse(readFileSync(STATE_FILE, 'utf8'));
    return {
      fixHistory: state?.patterns?.fixHistory || {},
      lastFixAttempt: state?.patterns?.lastFixAttempt || {},
      decayReport: state?.patterns?.decayReport?.patterns || [],
    };
  } catch { return { fixHistory: {}, lastFixAttempt: {}, decayReport: [] }; }
}

/** Thompson Sampling: sample from Beta(α, β) via additive Gaussian noise */
export function sampleConfidence(pattern) {
  if (pattern.confirmations == null || pattern.rejections == null) return Math.random();
  const c = pattern.confirmations, r = pattern.rejections;
  if (c === 0 && r === 0) return Math.random();
  const alpha = c + 0.5, beta = r + 0.5; // Jeffreys prior
  const mean = alpha / (alpha + beta);
  const variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1));
  const std = Math.sqrt(variance);
  const temperature = Math.max(0.02, Math.exp(-(c + r) / 8));
  const sampled = mean + std * gaussianRandom() * temperature;
  return Math.max(0, Math.min(1, sampled));
}

function gaussianRandom() {
  const u1 = Math.random(), u2 = Math.random();
  return Math.sqrt(-2 * Math.log(u1 || 1e-10)) * Math.cos(2 * Math.PI * u2);
}

/** Compute recommendation score for a pattern */
export function calcRecommendationScore(p, fix, { fixHistory, lastFixAttempt, decayReport }) {
  const sampledConf = sampleConfidence(p);
  const decayEntry = decayReport.find(d => d.name === p.name);
  const decay = decayEntry?.decayFactor ?? 1.0;
  const effConf = sampledConf * decay;
  const riskWeight = fix.risk === 'low' ? 1.0 : fix.risk === 'medium' ? 0.6 : 0.3;
  const lastFix = lastFixAttempt[p.name];
  const daysSince = lastFix ? (Date.now() - new Date(lastFix.timestamp)) / (1000 * 60 * 60 * 24) : null;
  const recentPenalty = (daysSince !== null && daysSince < 7) ? 0.4 : 1.0;

  // Co-occurrence bonus
  let coBonus = 1.0;
  const coMatrix = {};
  for (const [pat, events] of Object.entries(fixHistory)) {
    if (!events || events.length < 2) continue;
    for (const ev of events) {
      if (ev.coPatterns) {
        for (const cop of ev.coPatterns) {
          if (!coMatrix[pat]) coMatrix[pat] = {};
          coMatrix[pat][cop] = (coMatrix[pat][cop] || 0) + 1;
        }
      }
    }
  }
  if (coMatrix[p.name]) {
    for (const [cop, count] of Object.entries(coMatrix[p.name])) {
      const copLast = lastFixAttempt[cop];
      if (copLast && (Date.now() - new Date(copLast.timestamp)) < 7 * 24 * 60 * 60 * 1000) {
        coBonus = Math.max(coBonus, 1 + 0.1 * Math.min(count, 5));
      }
    }
  }

  const check = fix.check();
  const score = effConf * riskWeight * recentPenalty * coBonus;
  return {
    name: p.name,
    fix: p.fix,
    risk: fix.risk,
    severity: p.severity,
    score,
    effConf,
    decay,
    daysSince,
    applicable: check.applicable,
  };
}

/** Top-level recommend engine — returns sorted recommendations array */
export function getRecommendations(FIXES = {}) {
  const patterns = loadPatterns();
  const { fixHistory, lastFixAttempt, decayReport } = loadFixHistory();
  const recommendations = [];
  for (const p of patterns) {
    const fix = FIXES[p.name];
    if (!fix) continue;
    const result = calcRecommendationScore(p, fix, { fixHistory, lastFixAttempt, decayReport });
    if (!result.applicable) continue;
    recommendations.push(result);
  }
  recommendations.sort((a, b) => b.score - a.score);
  return recommendations;
}
