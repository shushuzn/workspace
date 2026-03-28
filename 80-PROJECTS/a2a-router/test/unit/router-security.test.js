import Database from 'better-sqlite3';
import { A2ARouter } from '../../src/router.js';

describe('A2ARouter Security Integration', () => {
  let db;
  let router;

  beforeEach(() => {
    db = new Database(':memory:');
    router = new A2ARouter({
      securityDb: db,
      security: {
        enabled: true,
        requireSignature: true
      },
      defaultAclPolicy: 'allow'
    });
  });

  afterEach(() => {
    if (router) {
      router.close();
    }
    if (db) {
      db.close();
    }
  });

  describe('SecurityManager Initialization', () => {
    test('initializes securityManager from options', () => {
      expect(router.securityManager).toBeDefined();
      expect(typeof router.securityManager.createApiKey).toBe('function');
      expect(typeof router.securityManager.revokeApiKey).toBe('function');
      expect(typeof router.securityManager.verifyMessage).toBe('function');
      expect(typeof router.securityManager.listApiKeys).toBe('function');
      expect(typeof router.securityManager.rotateApiKey).toBe('function');
    });

    test('initializes accessControl from options', () => {
      expect(router.accessControl).toBeDefined();
      expect(typeof router.accessControl.setRule).toBe('function');
      expect(typeof router.accessControl.checkPermission).toBe('function');
    });

    test('stores securityDb from options', () => {
      expect(router.securityDb).toBe(db);
    });
  });

  describe('Security Check in routeMessage()', () => {
    test('rejects message without signature when requireSignature is true', () => {
      const message = {
        id: 'msg-1',
        type: 'TASK',
        from: 'agent-1',
        to: 'agent-2',
        timestamp: Date.now(),
        payload: { data: 'test' }
      };

      const result = router.routeMessage(message);
      expect(result.success).toBe(false);
      expect(result.error).toBe('SIGNATURE_REQUIRED');
    });

    test('accepts valid signed message', () => {
      // Register target agent first
      router.registerAgent('agent-2', ['data:process'], {});

      const { keyId, key } = router.securityManager.createApiKey('agent-1', 0);
      const message = {
        id: 'msg-2',
        type: 'TASK',
        from: 'agent-1',
        to: 'agent-2',
        timestamp: Date.now(),
        payload: { data: 'test' },
        metadata: { apiKeyId: keyId }
      };
      // Sign using HMAC-SHA256, producing 64 hex chars
      message.metadata.signature = router.securityManager.signer.sign(key, message);

      const result = router.routeMessage(message);
      expect(result.success).toBe(true);
    });
  });

  describe('Public Security Methods', () => {
    test('createApiKey() creates and returns key details', () => {
      const result = router.createApiKey('agent-1', 60000);

      expect(result.keyId).toBeDefined();
      expect(result.keyId.startsWith('a2a_kid_')).toBe(true);
      expect(result.key).toBeDefined();
      expect(result.key.startsWith('a2a_sk_')).toBe(true);
      expect(result.expiresAt).toBeGreaterThan(Date.now());
    });

    test('revokeApiKey() removes key from memory', () => {
      const { keyId } = router.createApiKey('agent-1', 0);

      // Verify key exists
      expect(router.securityManager.apiKeys.has(keyId)).toBe(true);

      router.revokeApiKey(keyId);

      // Key should be removed from memory
      expect(router.securityManager.apiKeys.has(keyId)).toBe(false);
    });

    test('rotateApiKey() rotates an existing key', () => {
      const { keyId } = router.createApiKey('agent-1', 0);

      const result = router.rotateApiKey('agent-1', keyId);

      expect(result.keyId).toBeDefined();
      expect(result.keyId).not.toBe(keyId);
    });

    test('setAclRule() sets access control rule', () => {
      const result = router.setAclRule('code:execute', ['agent-1', 'agent-2'], ['agent-3']);

      expect(result.success).toBe(true);
    });

    test('checkPermission() checks permission via access control', () => {
      router.setAclRule('code:execute', ['agent-1'], []);

      const result = router.checkPermission('agent-1', 'code:execute');

      expect(result).toBe(true);
    });
  });
});
