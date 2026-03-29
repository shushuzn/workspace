import { describe, it, test, expect, beforeEach, afterEach } from 'vitest';
/**
 * ACP-A2A Integration Test
 * Tests the full flow: ACP message -> Gateway -> A2A Router -> Agent
 */

import { A2ARouter } from '../../src/router.js';
import { ACPGateway } from '../../src/protocols/acp-gateway.js';

describe('ACP-A2A Integration', () => {
  let router;
  let gateway;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    gateway = new ACPGateway(router, { enabled: true });
  });

  it('should route ACP message through gateway to A2A agent', () => {
    // Register a target A2A agent
    router.registerAgent('target-agent', ['coding']);

    // ACP agent sends request
    const acpMsg = {
      jsonrpc: '2.0',
      method: 'agent.request',
      params: {
        capabilities: ['coding'],
        targetAgent: 'target-agent',
        metadata: { priority: 'HIGH' }
      },
      id: 'acp-req-1'
    };

    let delivered = null;
    router.on('message:deliver', (msg, agent) => {
      delivered = { msg, agent };
    });

    gateway.handleACPMessage(acpMsg, 'acp-editor-1');

    expect(delivered).not.toBeNull();
    expect(delivered.msg.from).toBe('acp/acp-editor-1');
    expect(delivered.msg.to).toBe('target-agent');
    expect(delivered.msg.priority).toBe('HIGH');
  });

  it('should register ACP agent in A2A registry', () => {
    const acpMsg = {
      jsonrpc: '2.0',
      method: 'agent.request',
      params: { capabilities: ['refactor'] },
      id: '1'
    };

    gateway.handleACPMessage(acpMsg, 'new-acp-agent');

    const internalId = 'acp/new-acp-agent';
    const agent = router.agents.get(internalId);
    expect(agent).toBeDefined();
    expect(Array.from(agent.capabilities)).toEqual(['refactor']);
  });

  it('should translate priority URGENT to CRITICAL', () => {
    router.registerAgent('urgent-agent', ['task']);

    const acpMsg = {
      jsonrpc: '2.0',
      method: 'agent.request',
      params: {
        capabilities: ['task'],
        targetAgent: 'urgent-agent',
        metadata: { priority: 'URGENT' }
      },
      id: 'urgent-1'
    };

    let delivered = null;
    router.on('message:deliver', (msg) => {
      delivered = msg;
    });

    gateway.handleACPMessage(acpMsg, 'urgent-sender');

    expect(delivered.priority).toBe('CRITICAL');
  });

  it('should handle agent.request method', () => {
    router.registerAgent('test-agent', ['analyze']);

    const acpMsg = {
      jsonrpc: '2.0',
      method: 'agent.request',
      params: {
        capabilities: ['analyze'],
        targetAgent: 'test-agent',
        metadata: { priority: 'NORMAL' }
      },
      id: 'req-1'
    };

    const result = gateway.handleACPMessage(acpMsg, 'acp-client');

    expect(result.success).toBe(true);
  });

  it('should emit error on invalid ACP message', () => {
    return new Promise((resolve) => {
      gateway.on('error', (err) => {
        expect(err.message).toContain('Invalid ACP message');
        resolve();
      });

      gateway.handleACPMessage({ jsonrpc: '2.0' }, 'sender');
    });
  });
});
