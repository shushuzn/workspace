/**
 * CapabilityRegistry Unit Tests
 * TDD approach: tests first, then implementation
 */

import { CapabilityRegistry } from '../../src/protocols/capability-registry.js';
import { A2ARouter } from '../../src/router.js';

describe('CapabilityRegistry', () => {
  let router;
  let registry;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    registry = new CapabilityRegistry(router);
  });

  test('initializes with empty capabilityIndex', () => {
    expect(registry.capabilityIndex.size).toBe(0);
  });

  test('initializes with empty subscriptions', () => {
    expect(registry.subscriptions.size).toBe(0);
  });

  test('register() adds agent capabilities to index', () => {
    registry.register('agent-1', ['coding', 'review']);
    expect(registry.capabilityIndex.get('coding')).toContain('agent-1');
    expect(registry.capabilityIndex.get('review')).toContain('agent-1');
  });

  test('unregister() removes agent from index', () => {
    registry.register('agent-1', ['coding']);
    registry.unregister('agent-1');
    const set = registry.capabilityIndex.get('coding');
    expect(set && set.has('agent-1')).toBe(false);
  });

  test('match() returns scored results sorted by score', () => {
    // Register agents with capabilities that match 'code' query
    router.registerAgent('coder', ['code']);
    router.registerAgent('reviewer', ['code-review']);
    registry.register('coder', ['code']);
    registry.register('reviewer', ['code-review']);
    // Set different loads
    router.agents.get('coder').load = 0.5;
    router.agents.get('reviewer').load = 0.1;

    // Query 'code' matches both: 'code' (exact=10) and 'code-review' (prefix=5)
    const results = registry.match('code', { limit: 5 });
    // coder: exact match=10, recency=1, load=0.5 → score = 10+1-5 = 6
    // reviewer: prefix match=5, recency=1, load=0.1 → score = 5+1-1 = 5
    expect(results[0].agentId).toBe('coder'); // exact match wins
    expect(results[1].agentId).toBe('reviewer');
  });

  test('subscribe() adds subscriber and notifySubscribers() delivers message', () => {
    // Register provider agent in router
    router.registerAgent('provider', ['coding']);
    registry.register('provider', ['coding']);
    // Register subscriber agent in router
    router.registerAgent('subscriber-1', ['listening']);
    registry.subscribe('subscriber-1', ['coding']);

    let notified = null;
    router.on('message:deliver', (msg) => { notified = msg; });

    registry.notifySubscribers('coding', { type: 'capability:added', agentId: 'provider', capabilities: ['coding'] });

    expect(notified).not.toBeNull();
    expect(notified.to).toBe('subscriber-1');
  });

  test('match() respects loadThreshold as hard filter', () => {
    router.registerAgent('high-load-agent', ['coding']);
    registry.register('high-load-agent', ['coding']);
    router.agents.get('high-load-agent').load = 0.95;

    const results = registry.match('coding', { loadThreshold: 0.9, limit: 5 });
    // Agent with load 0.95 > threshold 0.9 should be excluded
    expect(results.some(m => m.agentId === 'high-load-agent')).toBe(false);
  });

  test('match() excludes agents above load threshold', () => {
    router.registerAgent('busy-agent', ['coding']);
    router.registerAgent('idle-agent', ['coding']);
    registry.register('busy-agent', ['coding']);
    registry.register('idle-agent', ['coding']);
    router.agents.get('busy-agent').load = 0.95;
    router.agents.get('idle-agent').load = 0.3;

    const results = registry.match('coding', { loadThreshold: 0.9, limit: 5 });
    expect(results.some(m => m.agentId === 'busy-agent')).toBe(false);
    expect(results.some(m => m.agentId === 'idle-agent')).toBe(true);
  });

  test('match() tie-breaking prefers lower load', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['coding']);
    registry.register('alice', ['coding']);
    registry.register('bob', ['coding']);
    router.heartbeat('alice', 'idle', 0.2, 0); // load=0.2
    router.heartbeat('bob', 'idle', 0.8, 0);    // load=0.8
    const matches = registry.match('coding', { loadThreshold: 1.0, limit: 5 });
    expect(matches[0].agentId).toBe('alice'); // lower load wins
    expect(matches[1].agentId).toBe('bob');
  });

  test('match() tie-breaking prefers recent heartbeat', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['coding']);
    registry.register('alice', ['coding']);
    registry.register('bob', ['coding']);
    router.heartbeat('alice', 'idle', 0.5, 0);
    router.heartbeat('bob', 'idle', 0.5, 0);
    const bob = router.agents.get('bob');
    bob.lastHeartbeat = Date.now() + 1000; // bob's heartbeat is more recent
    const matches = registry.match('coding', { loadThreshold: 1.0, limit: 5 });
    expect(matches[0].agentId).toBe('bob'); // more recent wins
  });
});
