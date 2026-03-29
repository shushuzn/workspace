import { describe, it, test, expect, beforeEach, afterEach } from 'vitest';
/**
 * Message Persistence Integration Test
 * Tests the full flow: register agents, send message, query history
 */

import { A2ARouter } from '../../src/router.js';

describe('Message Persistence Integration', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  afterEach(() => {
    if (router.messageStore) {
      router.messageStore.close();
    }
  });

  test('end-to-end: register agents, send message, query history', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['review']);

    router.routeMessage({
      id: 'e2e-1',
      type: 'TASK',
      priority: 'HIGH',
      from: 'alice',
      to: 'bob',
      timestamp: Date.now(),
      payload: { task: 'review PR' }
    });

    const history = router.queryMessages('alice', { limit: 10 });
    expect(history.some(m => m.id === 'e2e-1')).toBe(true);
  });

  test('archiveMessages() deletes old messages', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['review']);

    const oldTs = Date.now() - 100000;
    router.routeMessage({
      id: 'old-1',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'alice',
      to: 'bob',
      timestamp: oldTs,
      payload: { task: 'old task' }
    });

    // Use a cutoff AFTER the message timestamp (oldTs + 50000)
    // since archive uses timestamp < cutoff
    const cutoff = oldTs + 50000;
    const deleted = router.archiveMessages(cutoff);
    expect(deleted).toBe(1);

    const history = router.queryMessages('alice', { limit: 10 });
    expect(history.some(m => m.id === 'old-1')).toBe(false);
  });

  test('findByAgent() returns messages as sender and receiver', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['review']);
    router.registerAgent('carol', ['testing']);

    // alice -> bob
    router.routeMessage({
      id: 'msg-1',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'alice',
      to: 'bob',
      timestamp: Date.now(),
      payload: { task: 'task 1' }
    });

    // carol -> alice
    router.routeMessage({
      id: 'msg-2',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'carol',
      to: 'alice',
      timestamp: Date.now(),
      payload: { task: 'task 2' }
    });

    const aliceHistory = router.queryMessages('alice', { limit: 10 });
    expect(aliceHistory.length).toBe(2); // both msg-1 (to bob) and msg-2 (to alice)

    const bobHistory = router.queryMessages('bob', { limit: 10 });
    expect(bobHistory.length).toBe(1);
    expect(bobHistory[0].id).toBe('msg-1');
  });
});
