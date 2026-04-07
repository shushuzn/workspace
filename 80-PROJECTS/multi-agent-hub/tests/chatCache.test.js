import { describe, it } from 'node:test';
import assert from 'node:assert';
import { ChatCache } from '../shared/chatCache.js';

describe('ChatCache', () => {
  it('stores and retrieves', () => {
    const cache = new ChatCache(3);
    const msgs = [{ role: 'user', content: 'hello' }];
    cache.set(msgs, 0.7, 1500, 'response');
    const result = cache.get(msgs, 0.7, 1500);
    assert.strictEqual(result, 'response');
  });

  it('LRU evicts oldest entry when full', () => {
    const cache = new ChatCache(2);
    const a = [{ role: 'user', content: 'a' }];
    const b = [{ role: 'user', content: 'b' }];
    const c = [{ role: 'user', content: 'c' }];
    cache.set(a, 0.7, 1500, 'A');
    cache.set(b, 0.7, 1500, 'B');
    cache.set(c, 0.7, 1500, 'C'); // evicts a
    assert.strictEqual(cache.get(a, 0.7, 1500), null);
    assert.strictEqual(cache.get(b, 0.7, 1500), 'B');
    assert.strictEqual(cache.get(c, 0.7, 1500), 'C');
  });

  it('increments hit counter on cache hit', () => {
    const cache = new ChatCache(10);
    const msgs = [{ role: 'user', content: 'x' }];
    cache.set(msgs, 0.7, 1500, 'X');
    cache.get(msgs, 0.7, 1500);
    cache.get(msgs, 0.7, 1500);
    const stats = cache.stats();
    assert.strictEqual(stats.hits, 2);
    assert.strictEqual(stats.misses, 0);
  });

  it('increments miss counter on cache miss', () => {
    const cache = new ChatCache(10);
    const msgs = [{ role: 'user', content: 'y' }];
    const result = cache.get(msgs, 0.7, 1500);
    assert.strictEqual(result, null);
    const stats = cache.stats();
    assert.strictEqual(stats.misses, 1);
  });

  it('calculates hit rate correctly', () => {
    const cache = new ChatCache(10);
    const a = [{ role: 'user', content: 'a' }];
    const b = [{ role: 'user', content: 'b' }];
    cache.set(a, 0.7, 1500, 'A');
    cache.set(b, 0.7, 1500, 'B');
    cache.get(a, 0.7, 1500); // hit
    cache.get(a, 0.7, 1500); // hit
    cache.get(b, 0.7, 1500); // hit
    cache.get([{ role: 'user', content: 'c' }], 0.7, 1500); // miss
    const stats = cache.stats();
    assert.strictEqual(stats.hits, 3);
    assert.strictEqual(stats.misses, 1);
    assert.strictEqual(stats.hitRate, '75.0%');
  });

  it('clear resets all state', () => {
    const cache = new ChatCache(10);
    const msgs = [{ role: 'user', content: 'z' }];
    cache.set(msgs, 0.7, 1500, 'Z');
    cache.get(msgs, 0.7, 1500);
    cache.clear();
    const stats = cache.stats();
    assert.strictEqual(stats.size, 0);
    assert.strictEqual(stats.hits, 0);
    assert.strictEqual(stats.misses, 0);
  });

  it('key differs when extra fields differ (name is part of cache identity)', () => {
    const cache = new ChatCache(10);
    const withName = [{ role: 'user', content: 'hi', name: 'alice' }];
    const withoutName = [{ role: 'user', content: 'hi' }];
    cache.set(withName, 0.7, 1500, 'answer');
    const result = cache.get(withoutName, 0.7, 1500);
    // name field makes the key different — this is correct LLM behaviour
    assert.strictEqual(result, null);
  });
});
