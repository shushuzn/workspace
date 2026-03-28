import { LoadBalancer } from '../../src/protocols/load-balancing/load-balancer.js';

describe('LoadBalancer', () => {
  let router;
  let loadBalancer;

  beforeEach(() => {
    router = {
      agents: new Map(),
      queueMonitor: { getQueueStats: () => ({ queues: { CRITICAL: { size: 0 }, HIGH: { size: 0 }, NORMAL: { size: 5 }, LOW: { size: 0 } } }) }
    };
    loadBalancer = new LoadBalancer(router);
  });

  test('initializes with router reference', () => {
    expect(loadBalancer.router).toBe(router);
  });

  test('getAgentLoads returns empty for no agents', () => {
    const result = loadBalancer.getAgentLoads();
    expect(result).toEqual([]);
  });

  test('getAgentLoads filters by capability', () => {
    router.agents.set('alice', { id: 'alice', capabilities: new Set(['coding', 'review']), status: 'idle', load: 0.3, lastHeartbeat: Date.now() });
    router.agents.set('bob', { id: 'bob', capabilities: new Set(['review']), status: 'idle', load: 0.5, lastHeartbeat: Date.now() });

    const result = loadBalancer.getAgentLoads('coding');
    expect(result.length).toBe(1);
    expect(result[0].id).toBe('alice');
  });
});