/**
 * LRU Chat Cache — avoids repeating identical LLM calls within a session.
 *
 * Cache key: SHA-256 hash of JSON-stringified { messages, temperature, maxTokens }.
 * Only caches successful responses (non-error strings).
 */

import { createHash } from 'crypto';

export class ChatCache {
  /**
   * @param {number} maxSize - Max entries to keep (default 100)
   */
  constructor(maxSize = 100) {
    this.maxSize = maxSize;
    this.cache = new Map(); // key → { value, hits }
    this.hits = 0;
    this.misses = 0;
  }

  _key(messages, temperature, maxTokens) {
    // Strip volatile fields that don't affect model output
    const stable = messages.map(m => ({
      role: m.role,
      content: m.content,
      ...(m.name ? { name: m.name } : {}),
    }));
    const raw = JSON.stringify({ messages: stable, temperature, maxTokens });
    return createHash('sha256').update(raw, 'utf8').digest('hex');
  }

  get(messages, temperature, maxTokens) {
    const k = this._key(messages, temperature, maxTokens);
    const entry = this.cache.get(k);
    if (!entry) {
      this.misses++;
      return null;
    }
    // Move to end (most recently used)
    this.cache.delete(k);
    this.cache.set(k, { value: entry.value, hits: entry.hits + 1 });
    this.hits++;
    return entry.value;
  }

  set(messages, temperature, maxTokens, value) {
    const k = this._key(messages, temperature, maxTokens);
    if (this.cache.has(k)) {
      this.cache.delete(k);
    } else if (this.cache.size >= this.maxSize) {
      // Evict least recently used (first key in insertion order)
      const oldest = this.cache.keys().next().value;
      this.cache.delete(oldest);
    }
    this.cache.set(k, { value, hits: 0 });
  }

  stats() {
    const total = this.hits + this.misses;
    return {
      size: this.cache.size,
      hits: this.hits,
      misses: this.misses,
      hitRate: total > 0 ? ((this.hits / total) * 100).toFixed(1) + '%' : '0%',
    };
  }

  clear() {
    this.cache.clear();
    this.hits = 0;
    this.misses = 0;
  }
}
