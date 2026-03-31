/**
 * History Manager
 * Manages operation history with sliding window
 */

import fs from 'fs';
import path from 'path';
import { CONFIG } from '../config/default.mjs';

export class HistoryManager {
  constructor(historyFile) {
    this.historyFile = historyFile;
    this.history = this.load();
  }

  load() {
    if (!fs.existsSync(this.historyFile)) {
      return {
        epsilon: CONFIG.epsilon.init,
        streak: { success: 0, fail: 0 },
        records: []
      };
    }
    try {
      return JSON.parse(fs.readFileSync(this.historyFile, 'utf8'));
    } catch {
      return {
        epsilon: CONFIG.epsilon.init,
        streak: { success: 0, fail: 0 },
        records: []
      };
    }
  }

  save() {
    const dir = path.dirname(this.historyFile);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(this.historyFile, JSON.stringify(this.history, null, 2));
  }

  addRecord(record) {
    this.history.records.push(record);
    if (this.history.records.length > CONFIG.history.maxRecords) {
      this.history.records = this.history.records.slice(-CONFIG.history.maxRecords);
    }
  }

  updateStreak(success) {
    if (success) {
      this.history.streak.success++;
      this.history.streak.fail = 0;
    } else {
      this.history.streak.fail++;
      this.history.streak.success = 0;
    }
  }

  getSuccessRates() {
    const rates = {};
    for (const record of this.history.records) {
      if (!rates[record.opId]) {
        rates[record.opId] = { name: record.opName, success: 0, total: 0 };
      }
      rates[record.opId].total++;
      if (record.improved) rates[record.opId].success++;
    }
    return rates;
  }

  reset() {
    this.history = {
      epsilon: CONFIG.epsilon.init,
      streak: { success: 0, fail: 0 },
      records: []
    };
  }
}
