import { jest } from '@jest/globals';

// Mock the router
const mockSecurityManager = {
  createApiKey: jest.fn(),
  revokeApiKey: jest.fn(),
  listApiKeys: jest.fn(),
  rotateApiKey: jest.fn(),
  setAclRule: jest.fn(),
  verifyMessage: jest.fn()
};

const mockRouter = {
  securityManager: mockSecurityManager,
  getQueueStats: jest.fn().mockReturnValue({ size: 0, maxSize: 1000 }),
  archiveMessages: jest.fn().mockReturnValue(0),
  queryMessages: jest.fn().mockReturnValue([])
};

jest.unstable_mockModule('../../src/router.js', () => ({
  A2ARouter: jest.fn(() => mockRouter)
}));

jest.unstable_mockModule('../../src/protocols/acp-gateway.js', () => ({
  ACPGateway: jest.fn()
}));

// Import after mocking
const { A2ARouter } = await import('../../src/router.js');
const { ACPGateway } = await import('../../src/protocols/acp-gateway.js');

describe('Server Security Tools', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('a2a_create_api_key', () => {
    test('creates API key for agent', async () => {
      mockSecurityManager.createApiKey.mockReturnValue({
        keyId: 'a2a_kid_123',
        key: 'a2a_sk_secret',
        expiresAt: null
      });

      const result = mockRouter.securityManager.createApiKey('agent-1', 0);

      expect(mockSecurityManager.createApiKey).toHaveBeenCalledWith('agent-1', 0);
      expect(result.keyId).toBe('a2a_kid_123');
      expect(result.key).toBe('a2a_sk_secret');
    });

    test('creates API key with expiration', async () => {
      const futureTime = Date.now() + 60000;
      mockSecurityManager.createApiKey.mockReturnValue({
        keyId: 'a2a_kid_456',
        key: 'a2a_sk_secret2',
        expiresAt: futureTime
      });

      const result = mockRouter.securityManager.createApiKey('agent-2', 60000);

      expect(result.expiresAt).toBe(futureTime);
    });
  });

  describe('a2a_revoke_api_key', () => {
    test('revokes an API key', async () => {
      mockSecurityManager.revokeApiKey.mockReturnValue({ success: true });

      const result = mockRouter.securityManager.revokeApiKey('agent-1', 'a2a_kid_123');

      expect(mockSecurityManager.revokeApiKey).toHaveBeenCalledWith('agent-1', 'a2a_kid_123');
      expect(result.success).toBe(true);
    });
  });

  describe('a2a_list_api_keys', () => {
    test('lists API keys for agent', async () => {
      mockSecurityManager.listApiKeys.mockReturnValue([
        { keyId: 'a2a_kid_123', createdAt: Date.now(), expiresAt: null, revoked: false },
        { keyId: 'a2a_kid_456', createdAt: Date.now(), expiresAt: null, revoked: false }
      ]);

      const result = mockRouter.securityManager.listApiKeys('agent-1');

      expect(mockSecurityManager.listApiKeys).toHaveBeenCalledWith('agent-1');
      expect(result).toHaveLength(2);
    });

    test('returns empty array when no keys', async () => {
      mockSecurityManager.listApiKeys.mockReturnValue([]);

      const result = mockRouter.securityManager.listApiKeys('unknown-agent');

      expect(result).toHaveLength(0);
    });
  });

  describe('a2a_rotate_api_key', () => {
    test('rotates an API key', async () => {
      mockSecurityManager.rotateApiKey.mockReturnValue({
        success: true,
        newKeyId: 'a2a_kid_new',
        newKey: 'a2a_sk_new_secret'
      });

      const result = mockRouter.securityManager.rotateApiKey('agent-1', 'a2a_kid_old');

      expect(mockSecurityManager.rotateApiKey).toHaveBeenCalledWith('agent-1', 'a2a_kid_old');
      expect(result.newKeyId).toBe('a2a_kid_new');
    });
  });

  describe('a2a_set_acl', () => {
    test('sets ACL rule for capability', async () => {
      mockSecurityManager.setAclRule.mockReturnValue({ success: true });

      const result = mockRouter.securityManager.setAclRule(
        'code-generation',
        ['agent-1', 'agent-2'],
        ['agent-3']
      );

      expect(mockSecurityManager.setAclRule).toHaveBeenCalledWith(
        'code-generation',
        ['agent-1', 'agent-2'],
        ['agent-3']
      );
      expect(result.success).toBe(true);
    });

    test('sets ACL with only allowed agents', async () => {
      mockSecurityManager.setAclRule.mockReturnValue({ success: true });

      mockRouter.securityManager.setAclRule('推理', ['agent-1'], []);

      expect(mockSecurityManager.setAclRule).toHaveBeenCalledWith('推理', ['agent-1'], []);
    });
  });

  describe('a2a_verify_message', () => {
    test('verifies valid message', async () => {
      const testMessage = {
        id: 'msg-1',
        from: 'agent-1',
        to: 'agent-2',
        timestamp: Date.now(),
        signature: 'valid_sig'
      };
      mockSecurityManager.verifyMessage.mockReturnValue({ valid: true });

      const result = mockRouter.securityManager.verifyMessage(testMessage);

      expect(mockSecurityManager.verifyMessage).toHaveBeenCalledWith(testMessage);
      expect(result.valid).toBe(true);
    });

    test('returns invalid for unsigned message when required', async () => {
      const testMessage = {
        id: 'msg-2',
        from: 'agent-1',
        to: 'agent-2',
        timestamp: Date.now()
      };
      mockSecurityManager.verifyMessage.mockReturnValue({ valid: false, error: 'SIGNATURE_REQUIRED' });

      const result = mockRouter.securityManager.verifyMessage(testMessage);

      expect(result.valid).toBe(false);
      expect(result.error).toBe('SIGNATURE_REQUIRED');
    });
  });
});
