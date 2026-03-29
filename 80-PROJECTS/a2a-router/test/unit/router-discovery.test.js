/**
 * Router Capability Discovery Integration Tests
 */

import { A2ARouter } from '../../src/router.js';

describe('Router Capability Integration', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('registerAgent() creates capabilityRegistry', () => {
    router.registerAgent('test-agent', ['coding', 'review']);
    expect(router.capabilityRegistry).toBeDefined();
  });

  test('registerAgent() updates capability registry', () => {
    router.registerAgent('test-agent', ['coding', 'review']);
    const matches = router.capabilityRegistry.match('cod', { limit: 5 });
    expect(matches.length).toBeGreaterThan(0);
  });

  test('unregisterAgent() removes from capability registry', () => {
    router.registerAgent('test-agent', ['coding']);
    router.unregisterAgent('test-agent');
    const matches = router.capabilityRegistry.match('cod', { limit: 5 });
    expect(matches.some(m => m.agentId === 'test-agent')).toBe(false);
  });

  test('matchBestAgent() returns best scored agent', () => {
    router.registerAgent('idle-coder', ['coding']);
    router.registerAgent('busy-coder', ['coding']);
    router.heartbeat('idle-coder', 'healthy', 0.1, 0);
    router.heartbeat('busy-coder', 'healthy', 0.9, 10);

    // Query 'cod' matches 'coding' via contains
    const result = router.matchBestAgent('cod', { limit: 1 });
    expect(result[0].agentId).toBe('idle-coder');
  });

  test('subscribeCapabilities() adds subscription', () => {
    router.registerAgent('subscriber', ['listening']);
    router.subscribeCapabilities('subscriber', ['coding']);
    const capSubs = router.capabilityRegistry.subscriptions.get('coding');
    expect(capSubs && capSubs.has('subscriber')).toBe(true);
  });

  test('updateAgentCapabilities() updates capabilities', () => {
    router.registerAgent('agent-1', ['coding']);
    router.updateAgentCapabilities('agent-1', ['coding', 'review']);

    const agent = router.agents.get('agent-1');
    expect(Array.from(agent.capabilities)).toContain('review');
  });
});
