/**
 * LangChainAdapter Unit Tests
 */

import { describe, test, expect, beforeEach } from 'vitest';
import { LangChainAdapter } from '../../src/protocols/orchestration/langchain-adapter.js';

describe('LangChainAdapter', () => {
  let adapter;

  beforeEach(() => {
    adapter = new LangChainAdapter();
  });

  describe('createAgent()', () => {
    test('creates a new agent successfully', async () => {
      const result = await adapter.createAgent('test-agent', {
        model: 'gpt-4',
        capabilities: ['coding', 'reasoning']
      });

      expect(result.success).toBe(true);
      expect(result.agentId).toBe('test-agent');
    });

    test('returns error for duplicate agent', async () => {
      await adapter.createAgent('test-agent', { model: 'gpt-4' });
      const result = await adapter.createAgent('test-agent', { model: 'gpt-4' });

      expect(result.success).toBe(false);
      expect(result.error).toBe('AGENT_ALREADY_EXISTS');
    });

    test('stores agent config', async () => {
      const config = { model: 'claude-3', capabilities: ['analysis'] };
      await adapter.createAgent('test-agent', config);

      const agents = adapter.listAgents();
      expect(agents).toHaveLength(1);
      expect(agents[0].config).toEqual(config);
    });
  });

  describe('invoke()', () => {
    test('invokes existing agent successfully', async () => {
      await adapter.createAgent('test-agent', { model: 'gpt-4' });
      const result = await adapter.invoke('test-agent', {
        messages: [{ role: 'user', content: 'Hello' }]
      });

      expect(result.success).toBe(true);
      expect(result.agentId).toBe('test-agent');
      expect(result.runId).toBeDefined();
      expect(result.output).toContain('[LangGraph Agent test-agent] received: Hello');
    });

    test('returns error for non-existent agent', async () => {
      const result = await adapter.invoke('nonexistent', {
        messages: [{ role: 'user', content: 'Hello' }]
      });

      expect(result.success).toBe(false);
      expect(result.error).toBe('AGENT_NOT_FOUND');
    });

    test('tracks run in runs map', async () => {
      await adapter.createAgent('test-agent', { model: 'gpt-4' });
      const invokeResult = await adapter.invoke('test-agent', {
        messages: [{ role: 'user', content: 'Hi' }]
      });

      const statusResult = await adapter.status(invokeResult.runId);
      expect(statusResult.success).toBe(true);
      expect(statusResult.status).toBe('completed');
    });
  });

  describe('stop()', () => {
    test('stops a running agent', async () => {
      await adapter.createAgent('test-agent', { model: 'gpt-4' });
      const invokeResult = await adapter.invoke('test-agent', {
        messages: [{ role: 'user', content: 'Hello' }]
      });

      const stopResult = await adapter.stop(invokeResult.runId);
      expect(stopResult.success).toBe(true);

      const statusResult = await adapter.status(invokeResult.runId);
      expect(statusResult.status).toBe('stopped');
    });

    test('returns error for non-existent run', async () => {
      const result = await adapter.stop('nonexistent-run');
      expect(result.success).toBe(false);
      expect(result.error).toBe('RUN_NOT_FOUND');
    });
  });

  describe('status()', () => {
    test('returns completed status for finished run', async () => {
      await adapter.createAgent('test-agent', { model: 'gpt-4' });
      const invokeResult = await adapter.invoke('test-agent', {
        messages: [{ role: 'user', content: 'Hello' }]
      });

      const status = await adapter.status(invokeResult.runId);
      expect(status.success).toBe(true);
      expect(status.status).toBe('completed');
    });

    test('returns error for non-existent run', async () => {
      const result = await adapter.status('nonexistent-run');
      expect(result.success).toBe(false);
      expect(result.error).toBe('RUN_NOT_FOUND');
    });
  });

  describe('listAgents()', () => {
    test('lists all registered agents', async () => {
      await adapter.createAgent('agent-1', { model: 'gpt-4' });
      await adapter.createAgent('agent-2', { model: 'claude-3' });

      const agents = adapter.listAgents();
      expect(agents).toHaveLength(2);
      expect(agents.map(a => a.agentId)).toContain('agent-1');
      expect(agents.map(a => a.agentId)).toContain('agent-2');
    });

    test('returns empty array when no agents', () => {
      const agents = adapter.listAgents();
      expect(agents).toHaveLength(0);
    });

    test('includes createdAt timestamp', async () => {
      await adapter.createAgent('test-agent', { model: 'gpt-4' });
      const agents = adapter.listAgents();
      expect(agents[0].createdAt).toBeInstanceOf(Date);
    });
  });
});
