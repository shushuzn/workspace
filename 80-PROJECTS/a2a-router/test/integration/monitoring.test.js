/**
 * A2A Router Monitoring Integration Test
 * Tests the full flow: queue stats with threshold alerts
 */

import { A2ARouter } from '../../src/router.js';

describe('Queue Monitoring Integration', () => {
  let router;

  afterEach(() => {
    router.close();
  });

  test('end-to-end: queue stats with threshold alert', () => {
    // Use low threshold (10) to trigger alert with 15 messages
    router = new A2ARouter({
      heartbeatTimeout: 60000,
      queueThresholds: { CRITICAL: 10, HIGH: 10, NORMAL: 100, LOW: 200 }
    });
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['review']);

    // Directly push messages to queue (simulates messages queued for offline agent)
    // This is the correct approach since messages are delivered directly when agent is online
    for (let i = 0; i < 15; i++) {
      router.queues.get('HIGH').push({
        message: {
          id: `msg-${i}`,
          type: 'TASK',
          priority: 'HIGH',
          from: 'alice',
          to: 'bob',
          timestamp: Date.now(),
          payload: {}
        },
        enqueuedAt: Date.now(),
        retryCount: 0
      });
    }

    const stats = router.getQueueStats();
    expect(stats.queues.HIGH.size).toBe(15);
    expect(stats.alerts.length).toBeGreaterThan(0);
    expect(stats.alerts[0].level).toBe('HIGH');
  });
});
