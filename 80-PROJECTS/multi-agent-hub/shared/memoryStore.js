/**
 * Memory store — persists discussion summaries to a JSON file for cross-session retrieval.
 *
 * Unlike a vector DB (requires a separate service), this uses a local file store
 * keyed by topic similarity (simple TF-IDF word overlap).
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const STORE_FILE = path.join(__dirname, '..', 'memory-store.jsonl');

export class MemoryStore {
  constructor() {
    this.entries = [];
    this._loaded = false;
  }

  _ensureLoaded() {
    if (this._loaded) return;
    try {
      if (fs.existsSync(STORE_FILE)) {
        const raw = fs.readFileSync(STORE_FILE, 'utf8');
        this.entries = raw
          .trim()
          .split('\n')
          .filter(Boolean)
          .map(line => JSON.parse(line));
      }
    } catch {
      this.entries = [];
    }
    this._loaded = true;
  }

  /**
   * Save a discussion summary.
   * @param {{ topic: string, summary: string, mode: string, rounds: number, votes?: object }} entry
   */
  add(entry) {
    this._ensureLoaded();
    this.entries.push({ ...entry, storedAt: new Date().toISOString() });
    fs.appendFileSync(STORE_FILE, JSON.stringify(entry) + '\n');
  }

  /**
   * Search for relevant past discussions by topic keyword overlap.
   * @param {string} topic
   * @param {number} limit
   * @returns {{ topic: string, summary: string, storedAt: string }[]}
   */
  search(topic, limit = 5) {
    this._ensureLoaded();
    const topicWords = new Set(topic.toLowerCase().split(/\s+/));
    const scored = this.entries
      .map(e => {
        const entryWords = new Set(e.topic.toLowerCase().split(/\s+/));
        const overlap = [...topicWords].filter(w => entryWords.has(w)).length;
        return { entry: e, score: overlap };
      })
      .filter(s => s.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
    return scored.map(s => ({
      topic: s.entry.topic,
      summary: s.entry.summary,
      storedAt: s.entry.storedAt,
    }));
  }

  /** Number of entries stored. */
  get size() {
    this._ensureLoaded();
    return this.entries.length;
  }

  clear() {
    this.entries = [];
    if (fs.existsSync(STORE_FILE)) fs.unlinkSync(STORE_FILE);
  }
}
