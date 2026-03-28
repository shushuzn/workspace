# Message Security Layer Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add message signing, authentication, and access control to the A2A Router, making agent-to-agent communication secure and trustworthy.

**Architecture:** Add `SecurityManager`, `MessageSigner`, and `AccessControl` components. Messages are signed with HMAC-SHA256, verified by the router, with optional capability-based ACL enforcement.

**Tech Stack:** Node.js (crypto built-in), SQLite for key store, existing codebase patterns

---

## Overview

```
Agent 注册 → 获取 API Key → 消息签名 → Router 验证 → 路由
                    ↓
              权限检查（capability-based ACL）
```

---

## File Structure

```
src/
├── protocols/
│   └── security/                      # NEW
│       ├── security-manager.js       # API Key 管理、签名验证
│       ├── message-signer.js         # HMAC-SHA256 签名
│       └── access-control.js        # ACL 权限检查
├── router.js                          # MODIFY: add security middleware
└── server.js                         # MODIFY: add security MCP tools
test/
├── unit/
│   ├── security-manager.test.js      # NEW
│   ├── message-signer.test.js       # NEW
│   └── access-control.test.js       # NEW
└── integration/
    └── security.test.js             # NEW
```

---

## Message Flow

### 1. Agent Registration with API Key

```javascript
// 新注册流程
{
  type: 'REGISTER',
  payload: {
    agentId: 'agent-1',
    capabilities: ['coding', 'review'],
    apiKey: 'auto-generated-or-provided'  // 可选
  }
}
```

Router 返回：
```javascript
{
  success: true,
  apiKey: 'a2a_sk_xxx',  // 如果未提供则自动生成
  expiresAt: null  // 或设置过期时间
}
```

### 2. Message Signing

发送方对每条消息签名：
```javascript
const signature = HMAC-SHA256(
  apiKey,
  message.id + message.timestamp + JSON.stringify(message.payload)
);
```

签名后消息格式：
```javascript
{
  id: 'msg-001',
  type: 'TASK',
  from: 'agent-1',
  to: 'agent-2',
  timestamp: 1743154800000,
  payload: { task: 'code review' },
  metadata: {
    signature: 'abc123...',  // 消息签名
    apiKeyId: 'a2a_sk_xxx'   // 用于验证的 key ID
  }
}
```

### 3. Router Security Check

```javascript
// 伪代码
async function securityCheck(message) {
  // 1. 验证签名
  const valid = await securityManager.verifySignature(message);
  if (!valid) {
    return { error: 'INVALID_SIGNATURE' };
  }

  // 2. 检查时间戳防重放
  if (isExpired(message.timestamp)) {
    return { error: 'EXPIRED_TIMESTAMP' };
  }

  // 3. ACL 权限检查
  const allowed = await accessControl.checkPermission(
    message.from,
    message.to
  );
  if (!allowed) {
    return { error: 'UNAUTHORIZED' };
  }

  return { success: true };
}
```

### 4. Response with Error

```javascript
// 错误响应
{
  type: 'RESPONSE',
  from: 'router',
  to: 'agent-1',
  payload: {
    success: false,
    error: 'INVALID_SIGNATURE',
    errorMessage: 'Message signature verification failed'
  }
}
```

---

## API Design

### New MCP Tools

#### a2a_create_api_key
```javascript
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
}
```

#### a2a_revoke_api_key
```javascript
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
}
```

#### a2a_set_acl
```javascript
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
}
```

#### a2a_verify_message
```javascript
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
}
```

#### a2a_list_api_keys
```javascript
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
}
```

#### a2a_rotate_api_key
```javascript
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
}
```

---

## Component Details

### MessageSigner

```javascript
export class MessageSigner {
  // 生成 Key ID（公钥标识符，用于消息中引用）
  generateKeyId() {
    return 'a2a_kid_' + crypto.randomBytes(16).toString('hex');
  }

  // 生成 API Key（密钥，用于签名）
  generateApiKey() {
    return 'a2a_sk_' + crypto.randomBytes(32).toString('hex');
  }

  // 生成签名
  sign(apiKey, message) {
    const data = message.id + message.timestamp + JSON.stringify(message.payload);
    return crypto
      .createHmac('sha256', apiKey)
      .update(data)
      .digest('hex');
  }

  // 验证签名（长度检查防止 timingSafeEqual 报错）
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

### SecurityManager

```javascript
export class SecurityManager {
  constructor(options = {}) {
    this.db = options.db;  // better-sqlite3
    this.apiKeys = new Map();  // keyId -> { agentId, key, expiresAt, revoked, lastUsed }
    this.config = options.securityConfig || {
      enabled: false,  // 默认关闭，向后兼容
      requireSignature: false,
      timestampTolerance: 300000,  // 5 min
      defaultAclPolicy: 'allow'
    };

    // 从 DB 加载已有 keys
    this.loadApiKeysFromDb();
  }

  // SQLite schema
  // CREATE TABLE IF NOT EXISTS api_keys (
  //   key_id TEXT PRIMARY KEY,
  //   agent_id TEXT NOT NULL,
  //   key_secret TEXT NOT NULL,  -- 存储加密后的密钥
  //   expires_at INTEGER,
  //   revoked INTEGER DEFAULT 0,
  //   created_at INTEGER NOT NULL
  // );
  //
  // CREATE TABLE IF NOT EXISTS seen_messages (
  //   message_id TEXT PRIMARY KEY,
  //   seen_at INTEGER NOT NULL
  // );

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
    const signer = new MessageSigner();
    const keyId = signer.generateKeyId();
    const key = signer.generateApiKey();
    const expiresAt = expiresIn > 0 ? Date.now() + expiresIn : null;

    const entry = { agentId, key, expiresAt, revoked: false, lastUsed: null };
    this.apiKeys.set(keyId, entry);

    // 持久化到 DB
    this.db.prepare(`
      INSERT OR REPLACE INTO api_keys (key_id, agent_id, key_secret, expires_at, revoked, created_at)
      VALUES (?, ?, ?, ?, 0, ?)
    `).run(keyId, agentId, key, expiresAt, Date.now());

    return { keyId, key, expiresAt };
  }

  revokeApiKey(keyId) {
    const entry = this.apiKeys.get(keyId);
    if (entry) {
      entry.revoked = true;
      this.apiKeys.delete(keyId);
      this.db.prepare('UPDATE api_keys SET revoked = 1 WHERE key_id = ?').run(keyId);
    }
  }

  verifyMessage(message) {
    if (!this.config.enabled) return { valid: true };

    const { signature, apiKeyId } = message.metadata || {};
    if (this.config.requireSignature && !signature) {
      return { valid: false, error: 'SIGNATURE_REQUIRED' };
    }

    // 如果不强制签名且无签名，则跳过验证
    if (!signature) return { valid: true };

    // 查找 API Key
    const entry = this.apiKeys.get(apiKeyId);
    if (!entry || entry.revoked) {
      return { valid: false, error: 'API_KEY_REVOKED' };
    }
    if (entry.expiresAt && entry.expiresAt < Date.now()) {
      return { valid: false, error: 'API_KEY_EXPIRED' };
    }

    // 验证 message.from 与 key 所有者匹配（防止 spoofing）
    if (entry.agentId !== message.from) {
      return { valid: false, error: 'INVALID_SIGNATURE' };
    }

    // 验证时间戳（防重放）
    const age = Date.now() - message.timestamp;
    if (age > this.config.timestampTolerance) {
      return { valid: false, error: 'EXPIRED_TIMESTAMP' };
    }

    // 验证签名
    const signer = new MessageSigner();
    if (!signer.verify(entry.key, message, signature)) {
      return { valid: false, error: 'INVALID_SIGNATURE' };
    }

    // 更新 lastUsed
    entry.lastUsed = Date.now();

    return { valid: true, agentId: entry.agentId };
  }

  // 防重放：记录已见过的 message ID
  markMessageSeen(messageId) {
    const seenAt = Date.now();
    const cutoff = seenAt - this.config.timestampTolerance;
    this.db.prepare('DELETE FROM seen_messages WHERE seen_at < ?').run(cutoff);
    this.db.prepare('INSERT OR IGNORE INTO seen_messages (message_id, seen_at) VALUES (?, ?)').run(messageId, seenAt);
  }

  isMessageSeen(messageId) {
    const row = this.db.prepare('SELECT 1 FROM seen_messages WHERE message_id = ?').get(messageId);
    return !!row;
  }
}
```

### AccessControl

```javascript
export class AccessControl {
  constructor(securityManager, options = {}) {
    this.securityManager = securityManager;
    this.acl = new Map();  // capability -> { allowed: Set, denied: Set }
    this.defaultAclPolicy = options.defaultAclPolicy || 'allow';
  }

  setRule(capability, allowedAgents = [], deniedAgents = []) {
    this.acl.set(capability, {
      allowed: new Set(allowedAgents),
      denied: new Set(deniedAgents)
    });
  }

  checkPermission(fromAgent, toTarget) {
    // toTarget 可以是 agentId 或 capability:xxx
    if (!toTarget.startsWith('capability:')) {
      // 直接发送给 Agent，直接 allow
      return true;
    }

    const capability = toTarget.replace('capability:', '');
    const rule = this.acl.get(capability);

    if (!rule) {
      // 无规则，遵循 defaultAclPolicy
      return this.defaultAclPolicy === 'allow';
    }

    // denied 优先
    if (rule.denied.has(fromAgent)) {
      return false;
    }

    // allowed 为空表示允许所有人
    if (rule.allowed.size === 0) {
      return true;
    }

    return rule.allowed.has(fromAgent);
  }
}
```

---

## Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_SIGNATURE` | 401 | Message signature verification failed |
| `EXPIRED_TIMESTAMP` | 401 | Message timestamp too old (replay attack) |
| `API_KEY_REVOKED` | 401 | API key has been revoked |
| `API_KEY_EXPIRED` | 401 | API key has expired |
| `UNAUTHORIZED` | 403 | ACL check failed |
| `SIGNATURE_REQUIRED` | 400 | Security requires signature but none provided |

---

## Configuration

```javascript
// A2ARouter options
{
  security: {
    enabled: false,                // 默认关闭，向后兼容
    requireSignature: false,       // 默认不强制签名
    timestampTolerance: 300000,    // 5 min
    defaultAclPolicy: 'allow',    // 'allow' | 'deny'
    acl: {
      'capability:admin': { allowed: ['admin-agent'] },
      'capability:coding': { allowed: [] }  // 空 = 所有人可访问
    }
  }
}
```

---

## Testing Strategy

### Unit Tests

1. **MessageSigner**
   - generates valid API keys
   - signs messages correctly
   - verifies valid signatures
   - rejects invalid signatures

2. **SecurityManager**
   - creates and stores API keys
   - revokes keys correctly
   - validates messages with valid signatures
   - rejects revoked/expired keys
   - handles missing signatures when required

3. **AccessControl**
   - allows when no rules exist (default policy)
   - respects allowed list
   - respects denied list
   - denied takes precedence over allowed
   - defaultAclPolicy applies when no rule exists

### Integration Tests

1. Full flow: register → create key → sign → send → verify
2. Security rejection: invalid signature → rejected
3. ACL enforcement: denied agent → blocked
4. Replay attack: old timestamp → rejected
5. Backward compatibility: security disabled → unsigned messages pass

---

## Backward Compatibility

- `security.enabled = false` 完全禁用安全检查，现有消息无需签名
- `security.requireSignature = false` 接受签名消息但非强制
- 向后兼容：无 metadata.signature 的消息仍可在禁用安全时通过
