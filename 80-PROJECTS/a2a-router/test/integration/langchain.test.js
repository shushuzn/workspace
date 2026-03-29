import { describe, it, test, expect, beforeEach, afterEach } from 'vitest';
/**
 * LangChain Adapter Integration Test
 * Tests LangChain adapter through the router's internal langchainAdapter instance.
 * Validates the full pipeline: router command -> adapter -> router response.
 */

import { A2ARouter } from '../../src/router.js';

describe('LANGCHAIN Integration', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  afterEach(() => {
    router.close();
  });

  describe('LANGCHAIN_CREATE', () => {
    it('creates a LangChain agent via langchainAdapter', async () => {
      const result = await router.langchainAdapter.createAgent('test-agent', {
        model: 'gpt-4',
        capabilities: ['coding']
      });

      expect(result.success).toBe(true);
      expect(result.agentId).toBe('test-agent');
    });

    it('returns error for duplicate agent', async () => {
      await router.langchainAdapter.createAgent('dup-agent', { model: 'gpt-4' });
      const result = await router.langchainAdapter.createAgent('dup-agent', { model: 'claude-3' });

      expect(result.success).toBe(false);
      expect(result.error).toBe('AGENT_ALREADY_EXISTS');
    });
  });

  describe('LANGCHAIN_INVOKE', () => {
    it('invokes a LangChain agent and returns mock result', async () => {
      await router.langchainAdapter.createAgent('invoke-agent', { model: 'gpt-4' });

      const result = await router.langchainAdapter.invoke('invoke-agent', {
        messages: [{ role: 'user', content: 'Hello' }]
      });

      expect(result.success).toBe(true);
      expect(result.agentId).toBe('invoke-agent');
      expect(result.runId).toBeDefined();
      expect(result.output).toContain('[LangGraph Agent invoke-agent] received: Hello');
    });

    it('returns error for non-existent agent', async () => {
      const result = await router.langchainAdapter.invoke('nonexistent', {
        messages: [{ role: 'user', content: 'Hi' }]
      });

      expect(result.success).toBe(false);
      expect(result.error).toBe('AGENT_NOT_FOUND');
    });
  });

  describe('LANGCHAIN_STATUS', () => {
    it('returns completed status for a finished run', async () => {
      await router.langchainAdapter.createAgent('status-agent', {});
      const invokeResult = await router.langchainAdapter.invoke('status-agent', {
        messages: [{ role: 'user', content: 'test' }]
      });

      const status = await router.langchainAdapter.status(invokeResult.runId);

      expect(status.success).toBe(true);
      expect(status.status).toBe('completed');
    });

    it('returns error for non-existent run', async () => {
      const result = await router.langchainAdapter.status('nonexistent-run');

      expect(result.success).toBe(false);
      expect(result.error).toBe('RUN_NOT_FOUND');
    });
  });

  describe('LANGCHAIN_LIST', () => {
    it('lists all registered LangChain agents', async () => {
      await router.langchainAdapter.createAgent('list-agent-1', { model: 'gpt-4' });
      await router.langchainAdapter.createAgent('list-agent-2', { model: 'claude-3' });

      const result = await router.langchainAdapter.listAgents();

      expect(result).toHaveLength(2);
      expect(result.map(a => a.agentId)).toContain('list-agent-1');
      expect(result.map(a => a.agentId)).toContain('list-agent-2');
    });

    it('returns empty list when no agents registered', () => {
      const result = router.langchainAdapter.listAgents();
      expect(result).toHaveLength(0);
    });
  });

  describe('stop a run', () => {
    it('stops a run and status changes to stopped', async () => {
      await router.langchainAdapter.createAgent('stop-agent', {});
      const invokeResult = await router.langchainAdapter.invoke('stop-agent', {
        messages: [{ role: 'user', content: 'stop me' }]
      });

      const stopResult = await router.langchainAdapter.stop(invokeResult.runId);
      expect(stopResult.success).toBe(true);

      const status = await router.langchainAdapter.status(invokeResult.runId);
      expect(status.status).toBe('stopped');
    });

    it('returns error when stopping non-existent run', async () => {
      const result = await router.langchainAdapter.stop('nonexistent-run');
      expect(result.success).toBe(false);
      expect(result.error).toBe('RUN_NOT_FOUND');
    });
  });
});
