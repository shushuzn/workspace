import { A2ARouter } from '../../src/router.js';

describe('Capability Routing', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('capabilityRoute() routes to best matching agent', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['coding']);
    router.heartbeat('alice', 'idle', 0.2, 0); // lower load
    router.heartbeat('bob', 'idle', 0.8, 0);    // higher load

    const msg = {
      id: 'test-1',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'tester',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { task: 'build feature' }
    };

    const result = router.routeMessage(msg);
    expect(result.delivered).toBe(true);
    expect(result.agent).toBe('alice'); // lower load wins
  });

  test('capabilityRoute() queues when no agents match', () => {
    router.registerAgent('alice', ['review']); // no coding capability

    const msg = {
      id: 'test-2',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'tester',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { task: 'build feature' }
    };

    const result = router.routeMessage(msg);
    expect(result.queued).toBe(true);
    expect(result.reason).toBe('NO_AGENTS_FOR_CAPABILITY');
  });

  test('capabilityRoute() queues when matching agent offline', () => {
    router.registerAgent('alice', ['coding']);
    router.agents.get('alice').status = 'offline';

    const msg = {
      id: 'test-3',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'tester',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { task: 'build feature' }
    };

    const result = router.routeMessage(msg);
    expect(result.queued).toBe(true);
    expect(result.reason).toBe('AGENT_OFFLINE');
  });
});
