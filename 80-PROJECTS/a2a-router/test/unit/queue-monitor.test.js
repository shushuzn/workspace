/**
 * QueueMonitor Unit Tests
 * TDD approach: tests first, then implementation
 */

import { QueueMonitor } from '../../src/protocols/monitoring/queue-monitor.js';

describe('QueueMonitor', () => {
  let router;
  let monitor;

  beforeEach(() => {
    router = {
      queues: new Map([
        ['CRITICAL', []],
        ['HIGH', []],
        ['NORMAL', []],
        ['LOW', []]
      ])
    };
    monitor = new QueueMonitor(router);
  });

  test('initializes with default thresholds', () => {
    expect(monitor.thresholds.CRITICAL).toBe(10);
    expect(monitor.thresholds.HIGH).toBe(50);
    expect(monitor.thresholds.NORMAL).toBe(100);
    expect(monitor.thresholds.LOW).toBe(200);
  });

  test('initializes with custom thresholds', () => {
    const custom = new QueueMonitor(router, {
      thresholds: { CRITICAL: 5, HIGH: 20, NORMAL: 50, LOW: 100 }
    });
    expect(custom.thresholds.CRITICAL).toBe(5);
  });

  test('getQueueStats() returns zeros for empty queue', () => {
    const stats = monitor.getQueueStats();
    expect(stats.queues.CRITICAL.size).toBe(0);
    expect(stats.queues.CRITICAL.avgWaitTime).toBe(0);
    expect(stats.queues.CRITICAL.maxWaitTime).toBe(0);
    expect(stats.alerts).toEqual([]);
  });

  test('getQueueStats() calculates wait times', () => {
    const msg1 = { id: 'm1', enqueuedAt: Date.now() - 1000 };
    const msg2 = { id: 'm2', enqueuedAt: Date.now() - 500 };
    router.queues.get('HIGH').push(msg1, msg2);

    const stats = monitor.getQueueStats();
    expect(stats.queues.HIGH.size).toBe(2);
    expect(stats.queues.HIGH.avgWaitTime).toBeGreaterThan(0);
    expect(stats.queues.HIGH.maxWaitTime).toBeGreaterThanOrEqual(1000);
  });

  test('checkThresholds() returns alert when over threshold', () => {
    // Create monitor with lower threshold so 15 messages triggers alert
    const lowThresholdMonitor = new QueueMonitor(router, {
      thresholds: { CRITICAL: 10, HIGH: 10, NORMAL: 100, LOW: 200 }
    });
    // Add 15 messages to HIGH queue (threshold is 10)
    for (let i = 0; i < 15; i++) {
      router.queues.get('HIGH').push({ id: `m${i}`, enqueuedAt: Date.now() });
    }

    const alerts = lowThresholdMonitor.checkThresholds();
    expect(alerts.length).toBe(1);
    expect(alerts[0].level).toBe('HIGH');
    expect(alerts[0].queue).toBe('HIGH');
    expect(alerts[0].message).toContain('15');
  });

  test('checkThresholds() does NOT alert when size equals threshold', () => {
    const equalThresholdMonitor = new QueueMonitor(router, {
      thresholds: { CRITICAL: 10, HIGH: 10, NORMAL: 100, LOW: 200 }
    });
    // Add exactly 10 messages to HIGH queue (threshold is 10, should NOT alert)
    for (let i = 0; i < 10; i++) {
      router.queues.get('HIGH').push({ id: `m${i}`, enqueuedAt: Date.now() });
    }

    const alerts = equalThresholdMonitor.checkThresholds();
    expect(alerts.length).toBe(0);
  });
});
