// Memory Manager — hot/cold storage for time-series data with decay-based alert cooldowns

import { readFileSync, writeFileSync, mkdirSync, existsSync, renameSync, unlinkSync } from 'fs';
import { join } from 'path';
import { computeDelta } from './engine.mjs';

const MAX_HOT_RUNS = 3;
const ALERT_DECAY_TIERS = [0, 6, 12, 24]; // hours

export class MemoryManager {
  constructor(runsDir) {
    this.runsDir = runsDir;
    this.memoryDir = join(runsDir, 'memory');
    this.hotPath = join(this.memoryDir, 'hot.json');
    this.coldDir = join(this.memoryDir, 'cold');
    for (const dir of [this.memoryDir, this.coldDir]) {
      if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    }
    this.hot = this._loadHot();
  }

  _loadHot() {
    for (const path of [this.hotPath, this.hotPath + '.bak']) {
      try {
        const raw = readFileSync(path, 'utf8');
        const data = JSON.parse(raw);
        if (data && Array.isArray(data.runs) && typeof data.alertedSignals === 'object') return data;
      } catch { /* try next */ }
    }
    return { runs: [], alertedSignals: {} };
  }

  _saveHot() {
    const tmpPath = this.hotPath + '.tmp';
    const bakPath = this.hotPath + '.bak';
    try {
      writeFileSync(tmpPath, JSON.stringify(this.hot, null, 2));
      try { if (existsSync(this.hotPath)) renameSync(this.hotPath, bakPath); } catch { /* no backup */ }
      renameSync(tmpPath, this.hotPath);
    } catch (err) {
      console.error('[Memory] Failed to save:', err.message);
      try { unlinkSync(tmpPath); } catch { }
    }
  }

  addRun(synthesizedData) {
    const previous = this.getLastRun();
    const priorRuns = this.hot.runs.map(r => r.data);
    const delta = computeDelta(synthesizedData, previous, {}, priorRuns);

    this.hot.runs.unshift({
      timestamp: synthesizedData.meta?.timestamp || new Date().toISOString(),
      data: this._compactForStorage(synthesizedData),
      delta,
    });

    if (this.hot.runs.length > MAX_HOT_RUNS) {
      const archived = this.hot.runs.splice(MAX_HOT_RUNS);
      this._archiveToCold(archived);
    }

    this._saveHot();
    return delta;
  }

  getLastRun() { return this.hot.runs.length === 0 ? null : this.hot.runs[0].data; }
  getRunHistory(n = 3) { return this.hot.runs.slice(0, n); }
  getLastDelta() { return this.hot.runs.length === 0 ? null : this.hot.runs[0].delta; }
  getAlertedSignals() { return this.hot.alertedSignals || {}; }

  isSignalSuppressed(signalKey) {
    const entry = this.hot.alertedSignals[signalKey];
    if (!entry) return false;
    const now = Date.now();
    const occurrences = typeof entry === 'object' ? (entry.count || 1) : 1;
    const lastAlerted = typeof entry === 'object' ? new Date(entry.lastAlerted).getTime() : new Date(entry).getTime();
    const tierIndex = Math.min(occurrences, ALERT_DECAY_TIERS.length - 1);
    const cooldownMs = ALERT_DECAY_TIERS[tierIndex] * 60 * 60 * 1000;
    return (now - lastAlerted) < cooldownMs;
  }

  markAsAlerted(signalKey, timestamp) {
    const now = timestamp || new Date().toISOString();
    const existing = this.hot.alertedSignals[signalKey];
    if (existing && typeof existing === 'object') {
      existing.count = (existing.count || 1) + 1;
      existing.lastAlerted = now;
    } else {
      this.hot.alertedSignals[signalKey] = {
        firstSeen: typeof existing === 'string' ? existing : now,
        lastAlerted: now,
        count: typeof existing === 'string' ? 2 : 1,
      };
    }
    this._saveHot();
  }

  pruneAlertedSignals() {
    const now = Date.now();
    for (const [key, entry] of Object.entries(this.hot.alertedSignals)) {
      let lastTime, count;
      if (typeof entry === 'object') { lastTime = new Date(entry.lastAlerted).getTime(); count = entry.count || 1; }
      else { lastTime = new Date(entry).getTime(); count = 1; }
      const maxAge = count >= 2 ? 48 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
      if ((now - lastTime) > maxAge) delete this.hot.alertedSignals[key];
    }
    this._saveHot();
  }

  _compactForStorage(data) {
    return { meta: data.meta, fred: data.fred, energy: data.energy, bls: data.bls, treasury: data.treasury, gscpi: data.gscpi };
  }

  _archiveToCold(runs) {
    if (runs.length === 0) return;
    const dateKey = new Date().toISOString().split('T')[0];
    const coldPath = join(this.coldDir, `${dateKey}.json`);
    let existing = [];
    try { existing = JSON.parse(readFileSync(coldPath, 'utf8')); } catch { }
    existing.push(...runs);
    const tmpPath = coldPath + '.tmp';
    try {
      writeFileSync(tmpPath, JSON.stringify(existing, null, 2));
      renameSync(tmpPath, coldPath);
    } catch (err) {
      console.error('[Memory] Cold archive failed:', err.message);
      try { unlinkSync(tmpPath); } catch { }
    }
  }
}
