import Database from 'better-sqlite3';
import { SecurityManager } from '../../src/protocols/security/security-manager.js';

describe('SecurityManager', () => {
  let db;
  let sm;

  beforeEach(() => {
    db = new Database(':memory:');
    sm = new SecurityManager({ db });
  });

  afterEach(() => {
    db.close();
  });

  test('creates api_keys and seen_messages tables on init', () => {
    const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
    const names = tables.map(t => t.name);
    expect(names).toContain('api_keys');
    expect(names).toContain('seen_messages');
  });

  test('createApiKey() returns keyId, secret, and expiresAt', () => {
    const result = sm.createApiKey('agent-1', 0);
    expect(result.keyId.startsWith('a2a_kid_')).toBe(true);
    expect(result.key.startsWith('a2a_sk_')).toBe(true);
    expect(result.expiresAt).toBeNull();
  });

  test('createApiKey() with expiration sets expiresAt', () => {
    const result = sm.createApiKey('agent-1', 60000);
    expect(result.expiresAt).toBeGreaterThan(Date.now());
  });

  test('createApiKey() persists to DB', () => {
    const { keyId, key } = sm.createApiKey('agent-1', 0);
    const row = db.prepare('SELECT * FROM api_keys WHERE key_id = ?').get(keyId);
    expect(row.key_id).toBe(keyId);
    expect(row.key_secret).toBe(key);
    expect(row.agent_id).toBe('agent-1');
  });

  test('revokeApiKey() marks key revoked and removes from memory', () => {
    const { keyId } = sm.createApiKey('agent-1', 0);
    sm.revokeApiKey(keyId);
    expect(sm.apiKeys.has(keyId)).toBe(false);
    const row = db.prepare('SELECT revoked FROM api_keys WHERE key_id = ?').get(keyId);
    expect(row.revoked).toBe(1);
  });

  test('verifyMessage() returns valid when security disabled', () => {
    const result = sm.verifyMessage({ id: 'msg-1', from: 'a', timestamp: Date.now() });
    expect(result.valid).toBe(true);
  });

  test('verifyMessage() returns SIGNATURE_REQUIRED when requireSignature is true', () => {
    sm = new SecurityManager({ db, securityConfig: { enabled: true, requireSignature: true } });
    const result = sm.verifyMessage({ id: 'msg-1', from: 'agent-1', timestamp: Date.now() });
    expect(result.valid).toBe(false);
    expect(result.error).toBe('SIGNATURE_REQUIRED');
  });

  test('verifyMessage() returns INVALID_SIGNATURE for bad signature', () => {
    sm = new SecurityManager({ db, securityConfig: { enabled: true, requireSignature: true } });
    const { keyId, key } = sm.createApiKey('agent-1', 0);
    const msg = { id: 'msg-1', from: 'agent-1', timestamp: Date.now(), payload: { data: 'test' }, metadata: { signature: 'a'.repeat(64), apiKeyId: keyId } };
    const result = sm.verifyMessage(msg);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('INVALID_SIGNATURE');
  });

  test('verifyMessage() returns API_KEY_EXPIRED for expired key', () => {
    sm = new SecurityManager({ db, securityConfig: { enabled: true } });
    const { keyId } = sm.createApiKey('agent-1', -1000); // already expired
    const msg = { id: 'msg-1', from: 'agent-1', timestamp: Date.now(), payload: {}, metadata: { signature: 'a'.repeat(64), apiKeyId: keyId } };
    const result = sm.verifyMessage(msg);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('API_KEY_EXPIRED');
  });

  test('verifyMessage() returns EXPIRED_TIMESTAMP for old message', () => {
    sm = new SecurityManager({ db, securityConfig: { enabled: true, timestampTolerance: 5000 } });
    const { keyId, key } = sm.createApiKey('agent-1', 0);
    const oldTs = Date.now() - 10000;
    const msg = { id: 'msg-old', from: 'agent-1', timestamp: oldTs, payload: { data: 'test' }, metadata: { apiKeyId: keyId } };
    const signer = sm.signer;
    msg.metadata.signature = signer.sign(key, msg);
    const result = sm.verifyMessage(msg);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('EXPIRED_TIMESTAMP');
  });

  test('markMessageSeen() and isMessageSeen() track message IDs', () => {
    sm.markMessageSeen('msg-1');
    expect(sm.isMessageSeen('msg-1')).toBe(true);
    expect(sm.isMessageSeen('msg-2')).toBe(false);
  });
});
