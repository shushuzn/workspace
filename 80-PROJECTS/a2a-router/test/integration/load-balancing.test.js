import { A2ARouter } from '../../src/router.js';

describe('Load Balancing Integration', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('end-to-end: capability routing selects lowest load agent', () => {
    // Register agents with different loads
    router.registerAgent('agent-a', ['coding']);
    router.registerAgent('agent-b', ['coding']);
    router.registerAgent('agent-c', ['review']);

    router.heartbeat('agent-a', 'idle', 0.1, 0); // lowest load
    router.heartbeat('agent-b', 'idle', 0.9, 0); // highest load
    router.heartbeat('agent-c', 'idle', 0.2, 0);

    // Deliver a capability-based message
    const msg = {
      id: 'e2e-1',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'coordinator',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { task: 'implement feature' }
    };

    let deliveredTo = null;
    router.on('message:deliver', (message, agent) => {
      deliveredTo = agent.id;
    });

    const result = router.routeMessage(msg);
    expect(result.delivered).toBe(true);
    expect(deliveredTo).toBe('agent-a'); // lowest load selected
  });

  test('end-to-end: queues when no agents with capability', () => {
    router.registerAgent('reviewer', ['review']);

    const msg = {
      id: 'e2e-2',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'coordinator',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { task: 'implement feature' }
    };

    const result = router.routeMessage(msg);
    expect(result.queued).toBe(true);
    expect(result.reason).toBe('NO_AGENTS_FOR_CAPABILITY');
  });

  test('end-to-end: queues when only matching agent is offline', () => {
    router.registerAgent('offline-agent', ['coding']);
    router.heartbeat('offline-agent', 'idle', 0.1, 0);
    router.agents.get('offline-agent').status = 'offline';

    const msg = {
      id: 'e2e-3',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'coordinator',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { task: 'implement feature' }
    };

    const result = router.routeMessage(msg);
    expect(result.queued).toBe(true);
    expect(result.reason).toBe('AGENT_OFFLINE');
  });
});
