import { describe, it, expect, beforeEach } from 'vitest';
import { AgentHub } from '../src/mcp-sdk/agent-hub.js';

describe('AgentHub', () => {
  let hub;

  beforeEach(() => {
    hub = new AgentHub();
  });

  it('should create an AgentHub instance', () => {
    expect(hub).toBeDefined();
    expect(typeof hub.getAgents).toBe('function');
    expect(typeof hub.dispatchTask).toBe('function');
  });

  it('should return empty array when no agents registered', () => {
    const agents = hub.getAgents();
    expect(agents).toEqual([]);
  });

  it('should return stats with zero values', () => {
    const stats = hub.getStats();
    expect(stats).toBeDefined();
    expect(typeof stats.totalAgents).toBe('number');
    expect(typeof stats.totalTasks).toBe('number');
  });

  it('should return agents by type', () => {
    const agentsByType = hub.getAgentsByType('news');
    expect(Array.isArray(agentsByType)).toBe(true);
  });

  it('should get agents with capability', () => {
    const agents = hub.getAgentsWithCapability('coding');
    expect(Array.isArray(agents)).toBe(true);
  });
});
