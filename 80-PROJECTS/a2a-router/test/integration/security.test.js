import { A2ARouter } from '../../src/router.js';
import { MessageSigner } from '../../src/protocols/security/message-signer.js';
import Database from 'better-sqlite3';

describe('Security Integration', () => {
  let router;
  let db;
  let signer;

  beforeEach(() => {
    db = new Database(':memory:');
    router = new A2ARouter({
      securityDb: db,
      security: {
        enabled: true,
        requireSignature: true,
        timestampTolerance: 300000,
        defaultAclPolicy: 'deny'
      }
    });
    signer = new MessageSigner();
  });

  afterEach(() => {
    router.close();
    db.close();
  });

  test('Full flow: register → create key → sign → send → verify', () => {
    // Register source and target agents
    router.registerAgent('agent-1', ['coding']);
    router.registerAgent('agent-2', ['review']);

    // Create API key
    const { keyId, key } = router.createApiKey('agent-1');
    expect(keyId).toBeDefined();
    expect(key.startsWith('a2a_sk_')).toBe(true);

    // Create signed message
    const message = {
      id: 'msg-1',
      type: 'TASK',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now(),
      payload: { data: 'test' }
    };
    const signature = signer.sign(key, message);
    message.metadata = { signature, apiKeyId: keyId };

    // Route message (should succeed)
    const result = router.routeMessage(message);
    expect(result.success).toBe(true);
  });

  test('Invalid signature rejected', () => {
    router.registerAgent('agent-1', ['coding']);
    const { keyId, key } = router.createApiKey('agent-1');

    const message = {
      id: 'msg-2',
      type: 'TASK',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now(),
      payload: { data: 'test' },
      metadata: { signature: 'invalid', apiKeyId: keyId }
    };

    const result = router.routeMessage(message);
    expect(result.success).toBe(false);
    expect(result.error).toBe('INVALID_SIGNATURE');
  });

  test('ACL denied blocks message', () => {
    router.registerAgent('agent-1', ['coding']);
    router.registerAgent('agent-2', ['review']);

    // Set ACL to deny agent-1 access to capability:review
    router.setAclRule('review', [], ['agent-1']);

    // ACL check should return false
    const allowed = router.checkPermission('agent-1', 'capability:review');
    expect(allowed).toBe(false);
  });

  test('Expired timestamp rejected', () => {
    router.registerAgent('agent-1', ['coding']);
    const { keyId, key } = router.createApiKey('agent-1');

    const message = {
      id: 'msg-3',
      type: 'TASK',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now() - 600000, // 10 min ago
      payload: { data: 'test' },
      metadata: { apiKeyId: keyId }
    };
    const signature = signer.sign(key, message);
    message.metadata.signature = signature;

    const result = router.routeMessage(message);
    expect(result.success).toBe(false);
    expect(result.error).toBe('EXPIRED_TIMESTAMP');
  });

  test('Security disabled allows unsigned messages', () => {
    const router2 = new A2ARouter({
      securityDb: db,
      security: { enabled: false }
    });

    router2.registerAgent('agent-1', ['coding']);
    router2.registerAgent('agent-2', ['review']);

    const message = {
      id: 'msg-4',
      type: 'TASK',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now(),
      payload: { data: 'test' }
      // No metadata.signature
    };

    const result = router2.routeMessage(message);
    expect(result.success).toBe(true);

    router2.close();
  });
});
