/**
 * Router Queue Monitoring Tests
 */
import { A2ARouter } from '../../src/router.js';

describe('Router Queue Monitoring', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  afterEach(() => {
    router.close();
  });

  test('router has queueMonitor', () => {
    expect(router.queueMonitor).toBeDefined();
  });

  test('routeMessage sets enqueuedAt on queued messages', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['review']);

    // Mark bob as offline to trigger enqueue
    router.agents.get('bob').status = 'offline';

    router.routeMessage({
      id: 'enqueue-test',
      type: 'TASK',
      priority: 'HIGH',
      from: 'alice',
      to: 'bob',
      timestamp: Date.now(),
      payload: {}
    });

    const queue = router.queues.get('HIGH');
    expect(queue[0].enqueuedAt).toBeDefined();
  });
});
