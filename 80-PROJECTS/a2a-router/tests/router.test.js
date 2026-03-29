import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { A2ARouter } from '../src/router.js';

describe('A2ARouter', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter();
  });

  afterEach(() => {
    router.close();
  });

  it('should create an A2ARouter instance', () => {
    expect(router).toBeDefined();
    expect(router.agents).toBeInstanceOf(Map);
    expect(router.queues).toBeInstanceOf(Map);
  });

  it('should have four priority queues initialized', () => {
    expect(router.queues.get('CRITICAL')).toEqual([]);
    expect(router.queues.get('HIGH')).toEqual([]);
    expect(router.queues.get('NORMAL')).toEqual([]);
    expect(router.queues.get('LOW')).toEqual([]);
  });

  it('should register an agent successfully', () => {
    const result = router.registerAgent('test-agent', ['coding', 'reasoning'], { version: '1.0' });
    expect(result.success).toBe(true);
    expect(result.agent.id).toBe('test-agent');
    expect(result.agent.capabilities.has('coding')).toBe(true);
  });

  it('should reject duplicate agent registration', () => {
    router.registerAgent('test-agent', ['coding']);
    const result = router.registerAgent('test-agent', ['coding']);
    expect(result.success).toBe(false);
    expect(result.error).toBe('Agent already registered');
  });

  it('should return error when unregistering non-existent agent', () => {
    const result = router.unregisterAgent('nonexistent');
    expect(result.success).toBe(false);
    expect(result.error).toBe('Agent not found');
  });

  it('should unregister an existing agent', () => {
    router.registerAgent('test-agent', ['coding']);
    const result = router.unregisterAgent('test-agent');
    expect(result.success).toBe(true);
    expect(router.agents.has('test-agent')).toBe(false);
  });

  it('should update agent heartbeat', () => {
    router.registerAgent('test-agent', ['coding']);
    const result = router.heartbeat('test-agent', 'healthy', 0.5, 2);
    expect(result.success).toBe(true);
    expect(result.agent.lastHeartbeat).toBeDefined();
    expect(result.agent.load).toBe(0.5);
  });

  it('should return error for heartbeat of unknown agent', () => {
    const result = router.heartbeat('unknown-agent');
    expect(result.success).toBe(false);
    expect(result.error).toBe('Agent not found');
  });

  it('should validate a valid message', () => {
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'agent-a',
      to: 'agent-b',
      timestamp: Date.now(),
      payload: { task: 'test' }
    };
    const result = router.validateMessage(message);
    expect(result.valid).toBe(true);
  });

  it('should reject message with missing required field', () => {
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'agent-a',
      timestamp: Date.now(),
      payload: {}
    };
    const result = router.validateMessage(message);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Missing required field');
  });

  it('should reject message with null body', () => {
    const result = router.validateMessage(null);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Message is null');
  });

  it('should reject message with invalid type', () => {
    const message = {
      id: 'msg-1',
      type: 'INVALID_TYPE',
      from: 'agent-a',
      to: 'agent-b',
      timestamp: Date.now(),
      payload: {}
    };
    const result = router.validateMessage(message);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Invalid message type');
  });

  it('should route message to registered agent directly', async () => {
    router.registerAgent('target-agent', ['coding']);
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'sender',
      to: 'target-agent',
      timestamp: Date.now(),
      payload: { data: 'test' }
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(true);
    expect(result.delivered).toBe(true);
  });

  it('should return error when routing to unknown agent', async () => {
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'sender',
      to: 'unknown-agent',
      timestamp: Date.now(),
      payload: {}
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(false);
    expect(result.error).toBe('AGENT_NOT_FOUND');
  });

  it('should enqueue message when target agent is offline', async () => {
    router.registerAgent('offline-agent', ['coding']);
    router.agents.get('offline-agent').status = 'offline';
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'sender',
      to: 'offline-agent',
      timestamp: Date.now(),
      payload: {}
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(true);
    expect(result.queued).toBe(true);
  });

  it('should broadcast to all agents except sender', () => {
    router.registerAgent('agent-a', ['coding']);
    router.registerAgent('agent-b', ['coding']);
    router.registerAgent('agent-c', ['coding']);
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'agent-a',
      to: 'broadcast',
      timestamp: Date.now(),
      payload: {}
    };
    const result = router.broadcast(message);
    expect(result.success).toBe(true);
    expect(result.broadcast).toBe(true);
    expect(result.delivered).toBe(2);
    expect(result.failed).toBe(0);
  });

  it('should route via capability when to starts with capability:', async () => {
    router.registerAgent('coder', ['coding']);
    router.registerAgent('reviewer', ['review']);
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'sender',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: {}
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(true);
    expect(result.delivered).toBe(true);
    expect(result.agent).toBe('coder');
  });

  it('should handle DISCOVER router message', async () => {
    router.registerAgent('test-agent', ['coding']);
    const message = {
      id: 'msg-1',
      type: 'DISCOVER',
      from: 'main',
      to: 'router',
      timestamp: Date.now(),
      payload: { query: 'code' }
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(true);
  });

  it('should handle QUERY stats router message', async () => {
    router.registerAgent('test-agent', ['coding']);
    const message = {
      id: 'msg-1',
      type: 'QUERY',
      from: 'main',
      to: 'router',
      timestamp: Date.now(),
      payload: { query: 'stats' }
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(true);
    expect(result.stats).toBeDefined();
  });

  it('should return UNKNOWN_ROUTER_COMMAND for unknown router message type', async () => {
    const message = {
      id: 'msg-1',
      type: 'QUERY',
      from: 'main',
      to: 'router',
      timestamp: Date.now(),
      payload: { query: 'unknown_query' }
    };
    const result = await router.routeMessage(message);
    expect(result.success).toBe(false);
    expect(result.error).toBe('UNKNOWN_QUERY');
  });
});
