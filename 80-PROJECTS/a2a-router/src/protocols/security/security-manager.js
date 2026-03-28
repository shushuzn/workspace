import crypto from 'crypto';
import Database from 'better-sqlite3';
import { MessageSigner } from './message-signer.js';

export class SecurityManager {
  constructor(options = {}) {
    this.db = options.db;
    this.apiKeys = new Map(); // keyId -> { agentId, key, expiresAt, revoked, lastUsed }
    this.config = options.securityConfig || {
      enabled: false,
      requireSignature: false,
      timestampTolerance: 300000,
      defaultAclPolicy: 'allow'
    };
    this.signer = new MessageSigner();

    if (this.db) {
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS api_keys (
          key_id TEXT PRIMARY KEY,
          agent_id TEXT NOT NULL,
          key_secret TEXT NOT NULL,
          expires_at INTEGER,
          revoked INTEGER DEFAULT 0,
          created_at INTEGER NOT NULL
        )
      `);
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS seen_messages (
          message_id TEXT PRIMARY KEY,
          seen_at INTEGER NOT NULL
        )
      `);
      this.loadApiKeysFromDb();
    }
  }

  loadApiKeysFromDb() {
    if (!this.db) return;
    const rows = this.db.prepare('SELECT * FROM api_keys WHERE revoked = 0').all();
    for (const row of rows) {
      this.apiKeys.set(row.key_id, {
        agentId: row.agent_id,
        key: row.key_secret,
        expiresAt: row.expires_at,
        revoked: false,
        lastUsed: null
      });
    }
  }

  createApiKey(agentId, expiresIn = 0) {
    const keyId = this.signer.generateKeyId();
    const key = this.signer.generateApiKey();
    // expiresIn > 0: future expiration, expiresIn < 0: already expired, expiresIn = 0: no expiration
    const expiresAt = expiresIn > 0 ? Date.now() + expiresIn : (expiresIn < 0 ? Date.now() - 1 : null);

    const entry = { agentId, key, expiresAt, revoked: false, lastUsed: null };
    this.apiKeys.set(keyId, entry);

    if (this.db) {
      this.db.prepare(`
        INSERT OR REPLACE INTO api_keys (key_id, agent_id, key_secret, expires_at, revoked, created_at)
        VALUES (?, ?, ?, ?, 0, ?)
      `).run(keyId, agentId, key, expiresAt, Date.now());
    }

    return { keyId, key, expiresAt };
  }

  revokeApiKey(keyId) {
    const entry = this.apiKeys.get(keyId);
    if (entry) {
      entry.revoked = true;
      this.apiKeys.delete(keyId);
      if (this.db) {
        this.db.prepare('UPDATE api_keys SET revoked = 1 WHERE key_id = ?').run(keyId);
      }
    }
  }

  verifyMessage(message) {
    if (!this.config.enabled) return { valid: true };

    const { signature, apiKeyId } = message.metadata || {};
    if (this.config.requireSignature && !signature) {
      return { valid: false, error: 'SIGNATURE_REQUIRED' };
    }

    if (!signature) return { valid: true };

    const entry = this.apiKeys.get(apiKeyId);
    if (!entry || entry.revoked) {
      return { valid: false, error: 'API_KEY_REVOKED' };
    }
    if (entry.expiresAt && entry.expiresAt < Date.now()) {
      return { valid: false, error: 'API_KEY_EXPIRED' };
    }

    // Verify message.from matches key owner (spoofing prevention)
    if (entry.agentId !== message.from) {
      return { valid: false, error: 'INVALID_SIGNATURE' };
    }

    // Check timestamp (replay prevention)
    const age = Date.now() - message.timestamp;
    if (age > this.config.timestampTolerance) {
      return { valid: false, error: 'EXPIRED_TIMESTAMP' };
    }

    // Verify signature
    if (!this.signer.verify(entry.key, message, signature)) {
      return { valid: false, error: 'INVALID_SIGNATURE' };
    }

    // Update lastUsed
    entry.lastUsed = Date.now();

    return { valid: true, agentId: entry.agentId };
  }

  markMessageSeen(messageId) {
    if (!this.db) return;
    const seenAt = Date.now();
    const cutoff = seenAt - this.config.timestampTolerance;
    this.db.prepare('DELETE FROM seen_messages WHERE seen_at < ?').run(cutoff);
    this.db.prepare('INSERT OR IGNORE INTO seen_messages (message_id, seen_at) VALUES (?, ?)').run(messageId, seenAt);
  }

  isMessageSeen(messageId) {
    if (!this.db) return false;
    const row = this.db.prepare('SELECT 1 FROM seen_messages WHERE message_id = ?').get(messageId);
    return !!row;
  }

  listApiKeys(agentId) {
    const keys = [];
    for (const [keyId, entry] of this.apiKeys) {
      if (entry.agentId === agentId) {
        keys.push({ keyId, expiresAt: entry.expiresAt, lastUsed: entry.lastUsed, revoked: false });
      }
    }
    if (this.db) {
      const rows = this.db.prepare('SELECT key_id, expires_at, last_used FROM api_keys WHERE agent_id = ? AND revoked = 0').all(agentId);
      for (const row of rows) {
        if (!keys.find(k => k.keyId === row.key_id)) {
          keys.push({ keyId: row.key_id, expiresAt: row.expires_at, lastUsed: row.last_used, revoked: false });
        }
      }
    }
    return keys;
  }

  rotateApiKey(agentId, keyId) {
    this.revokeApiKey(keyId);
    return this.createApiKey(agentId, 0);
  }
}
