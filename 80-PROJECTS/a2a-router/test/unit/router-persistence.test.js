import { A2ARouter } from '../../src/router.js';

describe('Router Persistence Integration', () => {
  let router;

  afterEach(() => {
    if (router) {
      router.close();
    }
  });

  test('router initializes with messageStore', () => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    expect(router.messageStore).toBeDefined();
    expect(router.messageStore.getDatabase).toBeDefined();
  });

  test('routeMessage() saves message to store before delivery', () => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    router.registerAgent('sender', ['coding']);
    router.registerAgent('receiver', ['coding']);
    const msg = {
      id: 'persisted-1',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'sender',
      to: 'receiver',
      timestamp: Date.now(),
      payload: { data: 'test' }
    };
    const result = router.routeMessage(msg);
    expect(result.success).toBe(true);
    const stored = router.messageStore.findById('persisted-1');
    expect(stored).toBeDefined();
    expect(stored.id).toBe('persisted-1');
  });

  test('queryMessages() returns messages for agent', () => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    router.registerAgent('agent-a', ['coding']);
    router.registerAgent('agent-b', ['coding']);

    router.routeMessage({
      id: 'qry-1',
      type: 'TASK',
      priority: 'NORMAL',
      from: 'agent-a',
      to: 'agent-b',
      timestamp: Date.now(),
      payload: { data: 'test1' }
    });

    const messages = router.queryMessages('agent-a');
    expect(messages.length).toBeGreaterThan(0);
  });

  test('archiveMessages() removes old messages', () => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    router.registerAgent('a', ['coding']);
    router.registerAgent('b', ['coding']);

    // Save an old message
    const oldTs = Date.now() - 200000;
    router.messageStore.save({
      id: 'old-msg',
      from: 'a',
      to: 'b',
      type: 'TASK',
      priority: 'NORMAL',
      payload: '{}',
      timestamp: oldTs
    });

    // Archive messages older than 100 seconds
    const deleted = router.archiveMessages(Date.now() - 100000);
    expect(deleted).toBe(1);

    // Old message should be gone
    const result = router.messageStore.findById('old-msg');
    expect(result).toBeUndefined();
  });

  test('close() shuts down messageStore gracefully', () => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    expect(() => router.close()).not.toThrow();
  });
});
