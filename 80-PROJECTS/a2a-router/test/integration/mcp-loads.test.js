/**
 * a2a_get_agent_loads MCP Tool Test
 * Tests the load balancer integration via MCP tool
 */

import { A2ARouter } from '../../src/router.js';
import { LoadBalancer } from '../../src/protocols/load-balancing/load-balancer.js';

describe('a2a_get_agent_loads MCP tool', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('a2a_get_agent_loads tool is registered in TOOLS array', async () => {
    // Read server.js source and verify the tool definition exists
    const fs = await import('fs');
    const serverSource = fs.readFileSync('./src/server.js', 'utf-8');

    // Verify the tool definition exists in the TOOLS array
    expect(serverSource).toContain("name: 'a2a_get_agent_loads'");
    expect(serverSource).toContain("description: 'Get load scores for all registered agents'");

    // Verify the handler exists
    expect(serverSource).toContain("case 'a2a_get_agent_loads':");
  });

  test('LoadBalancer.getAgentLoads returns agent load data', () => {
    // Register test agents
    router.registerAgent('agent-1', ['coding', 'review']);
    router.registerAgent('agent-2', ['testing']);
    router.heartbeat('agent-1', 'idle', 0.3, 2);
    router.heartbeat('agent-2', 'busy', 0.7, 5);

    const loadBalancer = new LoadBalancer(router);
    const loads = loadBalancer.getAgentLoads();

    expect(loads.length).toBe(2);
    expect(loads.some(a => a.id === 'agent-1')).toBe(true);
    expect(loads.some(a => a.id === 'agent-2')).toBe(true);
  });

  test('LoadBalancer.getAgentLoads filters by capability', () => {
    router.registerAgent('coder-agent', ['coding', 'review']);
    router.registerAgent('tester-agent', ['testing', 'qa']);

    const loadBalancer = new LoadBalancer(router);

    const codingAgents = loadBalancer.getAgentLoads('coding');
    expect(codingAgents.length).toBe(1);
    expect(codingAgents[0].id).toBe('coder-agent');

    const testingAgents = loadBalancer.getAgentLoads('testing');
    expect(testingAgents.length).toBe(1);
    expect(testingAgents[0].id).toBe('tester-agent');
  });

  test('LoadBalancer.getAgentLoads returns score for each agent', () => {
    router.registerAgent('test-agent', ['analysis']);
    router.heartbeat('test-agent', 'idle', 0.2, 1);

    const loadBalancer = new LoadBalancer(router);
    const loads = loadBalancer.getAgentLoads();

    expect(loads.length).toBe(1);
    expect(typeof loads[0].score).toBe('number');
    expect(loads[0].score).toBeGreaterThan(0);
  });
});
