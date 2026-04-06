/**
 * CrossSource Federation Adapter
 * Queries multiple OSINT sources concurrently and merges results into a unified schema.
 *
 * Usage:
 *   import { CrossSourceFederation, SOURCE_IDS } from './federation-adapter.mjs';
 *   const fed = new CrossSourceFederation();
 *   const results = await fed.query({ query: 'John Doe', sources: ['telegram','news'] });
 */

export const SOURCE_IDS = [
  'telegram', 'news', 'acled', 'fred', 'energy', 'thermal', 'air', 'sdrd', 'who'
];

export const FederationStrategy = {
  ALL: 'all',
  FIRST: 'first',
  WEIGHTED: 'weighted',
  CONSENSUS: 'consensus',
};

export class CrossSourceQuery {
  constructor({
    query,
    entityType = 'general',
    sources = null,
    strategy = 'all',
    weights = {},
    timeout = 5000,
    limit = 20,
  }) {
    this.query = query;
    this.entityType = entityType;
    this.sources = sources ?? [...SOURCE_IDS];
    this.strategy = strategy;
    this.weights = weights;
    this.timeout = timeout;
    this.limit = limit;
  }
}

export class SourceResult {
  constructor({ sourceId, status, data, score, latencyMs, error }) {
    this.sourceId = sourceId;
    this.status = status;  // 'ok' | 'error' | 'timeout' | 'no_data'
    this.data = data;
    this.score = score;
    this.latencyMs = latencyMs;
    this.error = error;
  }
}

export class FederationResult {
  constructor({ query, entityType, strategy, totalSources, successfulSources, results, merged, associations, timestamp }) {
    this.query = query;
    this.entityType = entityType;
    this.strategy = strategy;
    this.totalSources = totalSources;
    this.successfulSources = successfulSources;
    this.results = results;
    this.merged = merged;
    this.associations = associations ?? [];
    this.timestamp = timestamp ?? Date.now();
  }
}

// ─── Source Adapters ────────────────────────────────────────────────────────

class SourceAdapter {
  constructor(sourceId) { this.sourceId = sourceId; }
  async query(entity, limit, timeout) {
    throw new Error('Not implemented');
  }
}

class TelegramAdapter extends SourceAdapter {
  constructor() { super('telegram'); }
  async query(entity, limit, timeout) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const res = await fetch(`http://localhost:3999/search?q=${encodeURIComponent(entity)}&limit=${limit}`, {
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (!res.ok) throw new Error(`Telegram API error: ${res.status}`);
      return await res.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error('Telegram timeout');
      throw e;
    }
  }
}

class NewsAdapter extends SourceAdapter {
  constructor() { super('news'); }
  async query(entity, limit, timeout) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const res = await fetch(`http://localhost:3998/news?q=${encodeURIComponent(entity)}&limit=${limit}`, {
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (!res.ok) throw new Error(`News API error: ${res.status}`);
      return await res.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error('News timeout');
      throw e;
    }
  }
}

class FREDAdapter extends SourceAdapter {
  constructor() { super('fred'); }
  async query(entity, limit, timeout) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const res = await fetch(
        `https://api.stlouisfed.org/fred/series/search?search_text=${encodeURIComponent(entity)}&limit=${limit}&sort_order=relevance&api_key=&file_type=json`,
        { signal: controller.signal }
      );
      clearTimeout(timer);
      if (!res.ok) throw new Error(`FRED API error: ${res.status}`);
      return await res.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error('FRED timeout');
      throw e;
    }
  }
}

class DefaultAdapter extends SourceAdapter {
  constructor(sourceId) { super(sourceId); }
  async query(entity, limit, timeout) {
    return { sourceId: this.sourceId, note: `Adapter for ${this.sourceId} not yet integrated`, query: entity };
  }
}

// ─── Federation Engine ───────────────────────────────────────────────────────

const ADAPTERS = {
  telegram: new TelegramAdapter(),
  news: new NewsAdapter(),
  acled: new DefaultAdapter('acled'),
  fred: new FREDAdapter(),
  energy: new DefaultAdapter('energy'),
  thermal: new DefaultAdapter('thermal'),
  air: new DefaultAdapter('air'),
  sdrd: new DefaultAdapter('sdrd'),
  who: new DefaultAdapter('who'),
};

export class CrossSourceFederation {
  constructor() {
    this._adapters = new Map(Object.entries(ADAPTERS));
  }

  /** Override the adapter for a specific source */
  registerAdapter(sourceId, adapter) {
    this._adapters.set(sourceId, adapter);
  }

  /** Execute a federated query across multiple sources concurrently */
  async query(req) {
    const sources = req.sources ?? [...SOURCE_IDS];
    const timeout = req.timeout ?? 5000;
    const limit = req.limit ?? 20;
    const strategy = req.strategy ?? 'all';

    const start = Date.now();
    const tasks = sources.map((sourceId) =>
      this._querySource(sourceId, req.query, limit, timeout)
    );

    let results;
    if (strategy === FederationStrategy.FIRST) {
      results = [await Promise.race(tasks)];
    } else {
      results = await Promise.allSettled(tasks).then((settled) =>
        settled.map((s, i) => {
          if (s.status === 'fulfilled') return s.value;
          return new SourceResult({ sourceId: sources[i], status: 'error', latencyMs: 0, error: String(s.reason) });
        })
      );
    }

    const successful = results.filter((r) => r.status === 'ok');
    const merged = this._mergeResults(results, req.entityType);
    const associations = this._findAssociations(successful, req.entityType);

    return new FederationResult({
      query: req.query,
      entityType: req.entityType,
      strategy,
      totalSources: sources.length,
      successfulSources: successful.length,
      results,
      merged,
      associations,
      timestamp: Date.now(),
    });
  }

  async _querySource(sourceId, query, limit, timeout) {
    const adapter = this._adapters.get(sourceId);
    if (!adapter) {
      return new SourceResult({ sourceId, status: 'error', latencyMs: 0, error: `Unknown source: ${sourceId}` });
    }
    const start = Date.now();
    try {
      const data = await adapter.query(query, limit, timeout);
      return new SourceResult({ sourceId, status: 'ok', data, score: 0.5, latencyMs: Date.now() - start });
    } catch (e) {
      return new SourceResult({
        sourceId,
        status: e.message.includes('timeout') ? 'timeout' : 'error',
        latencyMs: Date.now() - start,
        error: e.message,
      });
    }
  }

  _mergeResults(results, entityType) {
    const okResults = results.filter((r) => r.status === 'ok' && r.data);
    if (okResults.length === 0) return null;
    const allItems = [];
    for (const r of okResults) {
      if (Array.isArray(r.data)) allItems.push(...r.data);
      else if (r.data && typeof r.data === 'object') allItems.push(r.data);
    }
    return {
      items: allItems.slice(0, 100),
      count: allItems.length,
      sources: okResults.map((r) => r.sourceId),
    };
  }

  _findAssociations(results, entityType) {
    const associations = [];
    const entityMap = new Map();

    for (const r of results) {
      if (!r.data || typeof r.data !== 'object') continue;
      const data = r.data;
      const items = Array.isArray(data.items) ? data.items : [data];
      for (const item of items) {
        if (!item || typeof item !== 'object') continue;
        const name = item.name || item.title;
        if (!name || String(name).length < 2) continue;
        const key = String(name).toLowerCase();
        const existing = entityMap.get(key);
        if (existing) {
          existing.mentions = (existing.mentions ?? 1) + 1;
          associations.push({
            entityA: existing,
            entityB: existing,
            relation: `same_source:${r.sourceId}`,
            confidence: 0.6,
            source: r.sourceId,
          });
        } else {
          entityMap.set(key, {
            name: String(name),
            type: entityType ?? 'general',
            mentions: 1,
          });
        }
      }
    }
    return associations;
  }
}

// ─── REST endpoint handler ──────────────────────────────────────────────────

export async function federationHandler(req) {
  try {
    const body = await req.json();
    const fed = new CrossSourceFederation();
    const result = await fed.query(body);
    return new Response(JSON.stringify(result), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 });
  }
}
