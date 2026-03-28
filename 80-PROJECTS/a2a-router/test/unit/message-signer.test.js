import { MessageSigner } from '../../src/protocols/security/message-signer.js';

describe('MessageSigner', () => {
  let signer;

  beforeEach(() => {
    signer = new MessageSigner();
  });

  test('generateKeyId() returns prefixed key ID', () => {
    const keyId = signer.generateKeyId();
    expect(keyId.startsWith('a2a_kid_')).toBe(true);
    expect(keyId.length).toBe(8 + 32); // prefix (8) + 16 bytes hex (32)
  });

  test('generateApiKey() returns prefixed secret key', () => {
    const key = signer.generateApiKey();
    expect(key.startsWith('a2a_sk_')).toBe(true);
    expect(key.length).toBe(7 + 64); // prefix (7) + 32 bytes hex (64)
  });

  test('sign() produces 64-char hex signature', () => {
    const key = signer.generateApiKey();
    const message = { id: 'msg-1', timestamp: 1743154800000, payload: { data: 'test' } };
    const sig = signer.sign(key, message);
    expect(sig.length).toBe(64);
    expect(/^[a-f0-9]+$/.test(sig)).toBe(true);
  });

  test('verify() returns true for valid signature', () => {
    const key = signer.generateApiKey();
    const message = { id: 'msg-1', timestamp: 1743154800000, payload: { data: 'test' } };
    const sig = signer.sign(key, message);
    expect(signer.verify(key, message, sig)).toBe(true);
  });

  test('verify() returns false for invalid signature', () => {
    const key = signer.generateApiKey();
    const message = { id: 'msg-1', timestamp: 1743154800000, payload: { data: 'test' } };
    expect(signer.verify(key, message, 'a'.repeat(64))).toBe(false);
  });

  test('verify() returns false for null signature', () => {
    const key = signer.generateApiKey();
    const message = { id: 'msg-1', timestamp: 1743154800000, payload: { data: 'test' } };
    expect(signer.verify(key, message, null)).toBe(false);
  });

  test('verify() returns false for wrong length signature', () => {
    const key = signer.generateApiKey();
    const message = { id: 'msg-1', timestamp: 1743154800000, payload: { data: 'test' } };
    expect(signer.verify(key, message, 'abc123')).toBe(false);
  });

  test('sign() is deterministic for same input', () => {
    const key = signer.generateApiKey();
    const message = { id: 'msg-1', timestamp: 1743154800000, payload: { data: 'test' } };
    const sig1 = signer.sign(key, message);
    const sig2 = signer.sign(key, message);
    expect(sig1).toBe(sig2);
  });
});
