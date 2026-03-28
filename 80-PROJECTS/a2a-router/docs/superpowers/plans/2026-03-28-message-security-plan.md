# Message Security Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add message signing, authentication, and access control to the A2A Router — HMAC-SHA256 signatures, API key management, capability-based ACL.

**Architecture:** Security components live in `src/protocols/security/`. SecurityManager initializes SQLite schema for api_keys + seen_messages. Security middleware hooks into router.routeMessage() after validation, before routing. Backward compatible: security disabled by default.

**Tech Stack:** Node.js crypto (built-in), better-sqlite3 (synchronous API), existing test patterns with Jest ES modules.

---

## File Structure

```
src/
├── protocols/security/                    # NEW
│   ├── message-signer.js               # HMAC-SHA256 sign/verify
│   ├── security-manager.js              # API key lifecycle + verification
│   └── access-control.js               # Capability-based ACL
├── router.js                            # MODIFY: security middleware in routeMessage()
└── server.js                            # MODIFY: 6 new MCP tools

test/
├── unit/
│   ├── message-signer.test.js          # NEW
│   ├── security-manager.test.js         # NEW
│   └── access-control.test.js         # NEW
└── integration/
    └── security.test.js                 # NEW
```

---

## Task 1: MessageSigner

**Files:**
- Create: `src/protocols/security/message-signer.js`
- Test: `test/unit/message-signer.test.js`

- [ ] **Step 1: Write failing test**

```javascript
import { MessageSigner } from '../../src/protocols/security/message-signer.js';

describe('MessageSigner', () => {
  let signer;

  beforeEach(() => {
    signer = new MessageSigner();
  });

  test('generateKeyId() returns prefixed key ID', () => {
    const keyId = signer.generateKeyId();
    expect(keyId.startsWith('a2a_kid_')).toBe(true);
    expect(keyId.length).toBe(11 + 32); // prefix + 16 bytes hex
  });

  test('generateApiKey() returns prefixed secret key', () => {
    const key = signer.generateApiKey();
    expect(key.startsWith('a2a_sk_')).toBe(true);
    expect(key.length).toBe(11 + 64); // prefix + 32 bytes hex
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- test/unit/message-signer.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```javascript
import crypto from 'crypto';

export class MessageSigner {
  generateKeyId() {
    return 'a2a_kid_' + crypto.randomBytes(16).toString('hex');
  }

  generateApiKey() {
    return 'a2a_sk_' + crypto.randomBytes(32).toString('hex');
  }

  sign(apiKey, message) {
    const data = message.id + message.timestamp + JSON.stringify(message.payload);
    return crypto.createHmac('sha256', apiKey).update(data).digest('hex');
  }

  verify(apiKey, message, signature) {
    if (!signature || signature.length !== 64) {
      return false;
    }
    const expected = this.sign(apiKey, message);
    try {
      return crypto.timingSafeEqual(
        Buffer.from(signature, 'hex'),
        Buffer.from(expected, 'hex')
      );
    } catch {
      return false;
    }
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- test/unit/message-signer.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/security/message-signer.js test/unit/message-signer.test.js
git commit -m "feat(security): add MessageSigner with HMAC-SHA256 sign/verify"
```

---

## Task 2: SecurityManager with SQLite schema

**Files:**
- Create: `src/protocols/security/security-manager.js`
- Test: `test/unit/security-manager.test.js`

- [ ] **Step 1: Write failing test**

```javascript
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
    // sign it first
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- test/unit/security-manager.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write implementation**

```javascript
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
    const expiresAt = expiresIn > 0 ? Date.now() + expiresIn : null;

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- test/unit/security-manager.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/security/security-manager.js test/unit/security-manager.test.js
git commit -m "feat(security): add SecurityManager with API key lifecycle and verification"
```

---

## Task 3: AccessControl

**Files:**
- Create: `src/protocols/security/access-control.js`
- Test: `test/unit/access-control.test.js`

- [ ] **Step 1: Write failing test**

```javascript
import { AccessControl } from '../../src/protocols/security/access-control.js';

describe('AccessControl', () => {
  let ac;

  beforeEach(() => {
    ac = new AccessControl(null, { defaultAclPolicy: 'allow' });
  });

  test('allows direct agent-to-agent by default', () => {
    expect(ac.checkPermission('agent-1', 'agent-2')).toBe(true);
  });

  test('allows when no rules exist (default policy allow)', () => {
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(true);
  });

  test('denies when no rules exist (default policy deny)', () => {
    ac = new AccessControl(null, { defaultAclPolicy: 'deny' });
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(false);
  });

  test('respects allowed list', () => {
    ac.setRule('capability:coding', ['agent-1']);
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(true);
    expect(ac.checkPermission('agent-2', 'capability:coding')).toBe(false);
  });

  test('respects denied list', () => {
    ac.setRule('capability:coding', [], ['agent-2']);
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(true);
    expect(ac.checkPermission('agent-2', 'capability:coding')).toBe(false);
  });

  test('denied takes precedence over allowed', () => {
    ac.setRule('capability:coding', ['agent-1', 'agent-2'], ['agent-1']);
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(false);
    expect(ac.checkPermission('agent-2', 'capability:coding')).toBe(true);
  });

  test('empty allowed means allow everyone', () => {
    ac.setRule('capability:coding', []);
    expect(ac.checkPermission('anyone', 'capability:coding')).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- test/unit/access-control.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write implementation**

```javascript
export class AccessControl {
  constructor(securityManager, options = {}) {
    this.securityManager = securityManager;
    this.acl = new Map(); // capability -> { allowed: Set, denied: Set }
    this.defaultAclPolicy = options.defaultAclPolicy || 'allow';
  }

  setRule(capability, allowedAgents = [], deniedAgents = []) {
    this.acl.set(capability, {
      allowed: new Set(allowedAgents),
      denied: new Set(deniedAgents)
    });
  }

  checkPermission(fromAgent, toTarget) {
    // Direct agent-to-agent: always allow
    if (!toTarget.startsWith('capability:')) {
      return true;
    }

    const capability = toTarget.replace('capability:', '');
    const rule = this.acl.get(capability);

    if (!rule) {
      return this.defaultAclPolicy === 'allow';
    }

    // Denied takes precedence
    if (rule.denied.has(fromAgent)) {
      return false;
    }

    // Empty allowed means allow everyone
    if (rule.allowed.size === 0) {
      return true;
    }

    return rule.allowed.has(fromAgent);
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- test/unit/access-control.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/security/access-control.js test/unit/access-control.test.js
git commit -m "feat(security): add AccessControl with capability-based ACL"
```

---

## Task 4: Integrate Security Middleware into Router

**Files:**
- Modify: `src/router.js` (add securityManager and accessControl, integrate into routeMessage)

- [ ] **Step 1: Add SecurityManager and AccessControl to router.js**

Add imports after existing imports (around line 9):
```javascript
import { SecurityManager } from './protocols/security/security-manager.js';
import { AccessControl } from './protocols/security/access-control.js';
```

Add in constructor after existing component initialization (around line 53):
```javascript
// Initialize security manager
this.securityManager = new SecurityManager({
  db: options.securityDb,
  securityConfig: options.security || {}
});

// Initialize access control
this.accessControl = new AccessControl(this.securityManager, {
  defaultAclPolicy: options.security?.defaultAclPolicy || 'allow'
});
```

Add securityConfig to options accepted in constructor (around line 29):
```javascript
this.heartbeatTimeout = options.heartbeatTimeout || 60000;
this.maxQueueSize = options.maxQueueSize || 1000;
this.defaultTTL = options.defaultTTL || 3600;
this.securityDb = options.securityDb; // SQLite DB for security tables
```

- [ ] **Step 2: Add security check in routeMessage() after validateMessage()**

In `routeMessage()` method, after validation (around line 135):
```javascript
// Security check
const securityResult = this.securityManager.verifyMessage(message);
if (!securityResult.valid) {
  return { success: false, error: securityResult.error };
}
```

- [ ] **Step 3: Add security methods to router**

Add these public methods after existing methods:
```javascript
createApiKey(agentId, expiresIn) {
  return this.securityManager.createApiKey(agentId, expiresIn);
}

revokeApiKey(keyId) {
  return this.securityManager.revokeApiKey(keyId);
}

listApiKeys(agentId) {
  return this.securityManager.listApiKeys(agentId);
}

rotateApiKey(agentId, keyId) {
  return this.securityManager.rotateApiKey(agentId, keyId);
}

setAclRule(capability, allowedAgents, deniedAgents) {
  this.accessControl.setRule(capability, allowedAgents, deniedAgents);
  return { success: true };
}

checkPermission(fromAgent, toTarget) {
  return this.accessControl.checkPermission(fromAgent, toTarget);
}
```

- [ ] **Step 4: Commit**

```bash
git add src/router.js
git commit -m "feat(security): integrate SecurityManager and AccessControl into router"
```

---

## Task 5: Add Security MCP Tools to Server

**Files:**
- Modify: `src/server.js`

- [ ] **Step 1: Add new tools to TOOLS array**

Add these 6 tools after the existing tools (before the closing bracket around line 386):

```javascript
// Security Tools
{
  name: 'a2a_create_api_key',
  description: 'Create API key for agent authentication',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' },
      expiresIn: { type: 'number', description: 'Expiration in ms, 0 = never' }
    },
    required: ['agentId']
  }
},
{
  name: 'a2a_revoke_api_key',
  description: 'Revoke an API key',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' },
      keyId: { type: 'string' }
    },
    required: ['agentId', 'keyId']
  }
},
{
  name: 'a2a_list_api_keys',
  description: 'List all API keys for an agent (metadata only, no secrets)',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' }
    },
    required: ['agentId']
  }
},
{
  name: 'a2a_rotate_api_key',
  description: 'Rotate an API key (revoke old, create new)',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' },
      keyId: { type: 'string' }
    },
    required: ['agentId', 'keyId']
  }
},
{
  name: 'a2a_set_acl',
  description: 'Set access control rules for capabilities',
  inputSchema: {
    type: 'object',
    properties: {
      capability: { type: 'string' },
      allowedAgents: { type: 'array', items: { type: 'string' } },
      deniedAgents: { type: 'array', items: { type: 'string' } }
    },
    required: ['capability']
  }
},
{
  name: 'a2a_verify_message',
  description: 'Verify message signature and security',
  inputSchema: {
    type: 'object',
    properties: {
      message: { type: 'object', description: 'Message to verify' }
    },
    required: ['message']
  }
},
```

- [ ] **Step 2: Add case handlers in switch statement**

Add these cases in the switch statement (before the default case around line 705):

```javascript
case 'a2a_create_api_key': {
  const result = router.createApiKey(args.agentId, args.expiresIn || 0);
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true, ...result }, null, 2) }]
  };
}

case 'a2a_revoke_api_key': {
  router.revokeApiKey(args.keyId);
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true }, null, 2) }]
  };
}

case 'a2a_list_api_keys': {
  const keys = router.listApiKeys(args.agentId);
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true, keys }, null, 2) }]
  };
}

case 'a2a_rotate_api_key': {
  const result = router.rotateApiKey(args.agentId, args.keyId);
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true, ...result }, null, 2) }]
  };
}

case 'a2a_set_acl': {
  const result = router.setAclRule(args.capability, args.allowedAgents || [], args.deniedAgents || []);
  return {
    content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
  };
}

case 'a2a_verify_message': {
  const result = router.securityManager.verifyMessage(args.message);
  return {
    content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
  };
}
```

- [ ] **Step 3: Update router initialization to pass securityDb**

Update the router initialization (around line 20):
```javascript
import Database from 'better-sqlite3';

const securityDb = new Database('./security.db');
securityDb.exec(`
  CREATE TABLE IF NOT EXISTS api_keys (
    key_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    key_secret TEXT NOT NULL,
    expires_at INTEGER,
    revoked INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL
  )
`);
securityDb.exec(`
  CREATE TABLE IF NOT EXISTS seen_messages (
    message_id TEXT PRIMARY KEY,
    seen_at INTEGER NOT NULL
  )
`);

const router = new A2ARouter({
  heartbeatTimeout: 60000,
  maxQueueSize: 1000,
  securityDb
});
```

Also add the import:
```javascript
import Database from 'better-sqlite3';
```

- [ ] **Step 4: Commit**

```bash
git add src/server.js
git commit -m "feat(security): add 6 MCP security tools and SQLite-backed security store"
```

---

## Task 6: Integration Test

**Files:**
- Create: `test/integration/security.test.js`

- [ ] **Step 1: Write integration test**

```javascript
import { A2ARouter } from '../../src/router.js';
import Database from 'better-sqlite3';

describe('Security Integration', () => {
  let router;
  let db;
  let signer;

  beforeEach(() => {
    db = new Database(':memory:');
    db.exec(`
      CREATE TABLE IF NOT EXISTS api_keys (
        key_id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        key_secret TEXT NOT NULL,
        expires_at INTEGER,
        revoked INTEGER DEFAULT 0,
        created_at INTEGER NOT NULL
      )
    `);
    db.exec(`
      CREATE TABLE IF NOT EXISTS seen_messages (
        message_id TEXT PRIMARY KEY,
        seen_at INTEGER NOT NULL
      )
    `);

    router = new A2ARouter({
      heartbeatTimeout: 60000,
      maxQueueSize: 1000,
      securityDb: db,
      security: { enabled: true, requireSignature: true, timestampTolerance: 300000 }
    });

    router.registerAgent('agent-1', ['coding']);
    router.registerAgent('agent-2', ['review']);

    signer = router.securityManager.signer;
  });

  afterEach(() => {
    db.close();
  });

  test('full flow: create key, sign, send, verify', () => {
    // Create API key for agent-1
    const { keyId, key } = router.createApiKey('agent-1', 0);
    expect(keyId).toBeDefined();
    expect(key).toBeDefined();

    // Sign a message
    const message = {
      id: 'msg-test-1',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now(),
      payload: { data: 'hello' },
      metadata: { apiKeyId: keyId }
    };
    message.metadata.signature = signer.sign(key, message);

    // Route the message
    const result = router.routeMessage(message);
    expect(result.success).toBe(true);
  });

  test('invalid signature is rejected', () => {
    const { keyId } = router.createApiKey('agent-1', 0);

    const message = {
      id: 'msg-bad-1',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now(),
      payload: { data: 'hello' },
      metadata: { apiKeyId: keyId, signature: 'a'.repeat(64) }
    };

    const result = router.routeMessage(message);
    expect(result.success).toBe(false);
    expect(result.error).toBe('INVALID_SIGNATURE');
  });

  test('ACL denies blocked agent', () => {
    router.setAclRule('capability:coding', [], ['agent-2']);

    // Create API key and sign message so it passes signature verification
    const { keyId, key } = router.createApiKey('agent-2', 0);
    const message = {
      id: 'msg-blocked-1',
      from: 'agent-2',
      to: 'capability:coding',
      timestamp: Date.now(),
      payload: { data: 'task' },
      metadata: { apiKeyId: keyId }
    };
    message.metadata.signature = signer.sign(key, message);

    const allowed = router.checkPermission('agent-2', 'capability:coding');
    expect(allowed).toBe(false);
  });

  test('security disabled allows unsigned messages', () => {
    router.securityManager.config.enabled = false;

    const message = {
      id: 'msg-no-sig-1',
      from: 'agent-1',
      to: 'agent-2',
      timestamp: Date.now(),
      payload: { data: 'hello' }
    };

    const result = router.routeMessage(message);
    expect(result.success).toBe(true);
  });
});
```

- [ ] **Step 2: Run integration test**

Run: `npm test -- test/integration/security.test.js`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add test/integration/security.test.js
git commit -m "test(security): add integration test for full security flow"
```

---

## Task 7: Run All Tests

- [ ] **Step 1: Run full test suite**

Run: `npm test`
Expected: ALL PASS

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "test: run full test suite, all passing"
```
