# ACP Gateway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate Agent Client Protocol (ACP) support into a2a-router via protocol adapter layer, enabling ACP agents to communicate with existing A2A agents.

**Architecture:** ACP Gateway acts as a translation layer between ACP JSON-RPC 2.0 messages and A2A internal message format. Three new components (ACPGateway, ACPParser, ACPAgentAdapter) are created in `src/protocols/`. The gateway is injected into the existing router and can be enabled via config.

**Tech Stack:** Node.js (ES Modules), JSON-RPC 2.0, existing A2ARouter class

---

## File Structure

```
80-PROJECTS/a2a-router/
├── src/
│   ├── router.js              (EXISTING - no changes needed)
│   ├── server.js             (EXISTING - add ACP tool handlers)
│   └── protocols/             (NEW - ACP protocol layer)
│       ├── acp-gateway.js   (NEW - main gateway class)
│       ├── acp-parser.js     (NEW - JSON-RPC parsing)
│       └── acp-adapter.js    (NEW - agent registration bridge)
└── test/
    ├── acp-parser.test.js         (NEW)
    ├── acp-gateway.test.js       (NEW)
    └── integration/
        └── acp-a2a.test.js       (NEW)
```

---

## Task 1: Create ACPParser

**Files:**
- Create: `80-PROJECTS/a2a-router/src/protocols/acp-parser.js`
- Test: `80-PROJECTS/a2a-router/test/acp-parser.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
// test/acp-parser.test.js
import { ACPParser } from '../src/protocols/acp-parser.js';

describe('ACPParser', () => {
  const parser = new ACPParser();

  describe('parse()', () => {
    it('should parse valid ACP agent.request message', () => {
      const acpMessage = {
        jsonrpc: '2.0',
        method: 'agent.request',
        params: {
          capabilities: ['code-completion'],
          metadata: { priority: 'HIGH' }
        },
        id: 'msg-123'
      };
      const result = parser.parse(acpMessage);
      expect(result).toEqual({
        jsonrpc: '2.0',
        method: 'agent.request',
        params: {
          capabilities: ['code-completion'],
          metadata: { priority: 'HIGH' }
        },
        id: 'msg-123'
      });
    });

    it('should throw on missing jsonrpc field', () => {
      const invalid = { method: 'agent.request', params: {}, id: '1' };
      expect(() => parser.parse(invalid)).toThrow('Invalid ACP message: missing jsonrpc');
    });

    it('should throw on missing method field', () => {
      const invalid = { jsonrpc: '2.0', params: {}, id: '1' };
      expect(() => parser.parse(invalid)).toThrow('Invalid ACP message: missing method');
    });
  });

  describe('toACP()', () => {
    it('should convert A2A message to ACP response format', () => {
      const a2aMessage = {
        id: 42,
        type: 'TASK_RESULT',
        payload: { result: 'completed' }
      };
      const result = parser.toACP(a2aMessage, 'msg-123');
      expect(result).toEqual({
        jsonrpc: '2.0',
        result: { type: 'TASK_RESULT', payload: { result: 'completed' } },
        id: 'msg-123'
      });
    });
  });

  describe('toA2A()', () => {
    it('should convert ACP request to A2A internal format', () => {
      const acpRequest = {
        jsonrpc: '2.0',
        method: 'agent.request',
        params: {
          capabilities: ['coding'],
          metadata: { priority: 'HIGH' }
        },
        id: 'acp-456'
      };
      const result = parser.toA2A(acpRequest, 'acp-sender-1', 'target-agent');
      expect(result).toEqual({
        id: expect.any(String),
        type: 'TASK',
        priority: 'HIGH',
        from: 'acp-sender-1',
        to: 'target-agent',
        timestamp: expect.any(Number),
        payload: {
          capabilities: ['coding'],
          originalMethod: 'agent.request',
          originalId: 'acp-456'
        }
      });
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/acp-parser.test.js`
Expected: FAIL with "Cannot find module '../src/protocols/acp-parser.js'"

- [ ] **Step 3: Write minimal implementation**

```javascript
// src/protocols/acp-parser.js
export class ACPParser {
  parse(message) {
    if (!message.jsonrpc) {
      throw new Error('Invalid ACP message: missing jsonrpc');
    }
    if (!message.method) {
      throw new Error('Invalid ACP message: missing method');
    }
    return message;
  }

  toACP(a2aMessage, originalId) {
    return {
      jsonrpc: '2.0',
      result: {
        type: a2aMessage.type,
        payload: a2aMessage.payload
      },
      id: originalId
    };
  }

  toA2A(acpMessage, fromAgentId, toAgentId) {
    const priorityMap = {
      'URGENT': 'CRITICAL',
      'HIGH': 'HIGH',
      'NORMAL': 'NORMAL',
      'LOW': 'LOW'
    };

    return {
      id: crypto.randomUUID(),
      type: 'TASK',
      priority: priorityMap[acpMessage.params?.metadata?.priority] || 'NORMAL',
      from: fromAgentId,
      to: toAgentId,
      timestamp: Date.now(),
      payload: {
        capabilities: acpMessage.params?.capabilities || [],
        originalMethod: acpMessage.method,
        originalId: acpMessage.id
      }
    };
  }
}

export default new ACPParser();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/acp-parser.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 80-PROJECTS/a2a-router/src/protocols/acp-parser.js 80-PROJECTS/a2a-router/test/acp-parser.test.js
git commit -m "feat(a2a-router): add ACPParser for JSON-RPC 2.0 translation"
```

---

## Task 2: Create ACPAgentAdapter

**Files:**
- Create: `80-PROJECTS/a2a-router/src/protocols/acp-adapter.js`
- Test: `80-PROJECTS/a2a-router/test/acp-adapter.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
// test/acp-adapter.test.js
import { ACPAgentAdapter } from '../src/protocols/acp-adapter.js';

describe('ACPAgentAdapter', () => {
  const mockRouter = {
    registerAgent: jest.fn().mockReturnValue({ success: true }),
    heartbeat: jest.fn().mockReturnValue({ success: true })
  };
  const adapter = new ACPAgentAdapter(mockRouter);

  describe('registerACPAgent()', () => {
    it('should register ACP agent with A2A router', () => {
      const acpAgent = {
        id: 'acp-editor-1',
        capabilities: ['code-completion', 'refactor'],
        metadata: { name: 'VS Code Agent' }
      };
      const result = adapter.registerACPAgent(acpAgent);
      expect(mockRouter.registerAgent).toHaveBeenCalledWith(
        'acp/acp-editor-1',
        ['code-completion', 'refactor'],
        { originalId: 'acp-editor-1', name: 'VS Code Agent', protocol: 'ACP' }
      );
      expect(result.internalId).toBe('acp/acp-editor-1');
    });

    it('should handle ACP capabilities array to Set conversion', () => {
      const acpAgent = { id: 'test', capabilities: ['a', 'b'] };
      adapter.registerACPAgent(acpAgent);
      const call = mockRouter.registerAgent.mock.calls[0];
      expect(call[1]).toEqual(['a', 'b']);
    });
  });

  describe('toACPHeartbeat()', () => {
    it('should translate A2A heartbeat to ACP format', () => {
      const result = adapter.toACPHeartbeat('acp/agent-1', 'healthy', 0.3, 2);
      expect(result).toEqual({
        jsonrpc: '2.0',
        method: 'agent.heartbeat',
        params: {
          agentId: 'agent-1',
          status: 'healthy',
          load: 0.3,
          activeTasks: 2
        },
        id: expect.any(String)
      });
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/acp-adapter.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```javascript
// src/protocols/acp-adapter.js
export class ACPAgentAdapter {
  constructor(router) {
    this.router = router;
    this.idMap = new Map(); // ACP ID -> Internal ID
  }

  registerACPAgent(acpAgent) {
    const internalId = `acp/${acpAgent.id}`;
    this.idMap.set(acpAgent.id, internalId);

    this.router.registerAgent(
      internalId,
      acpAgent.capabilities || [],
      {
        originalId: acpAgent.id,
        ...acpAgent.metadata,
        protocol: 'ACP'
      }
    );

    return { success: true, internalId };
  }

  toACPHeartbeat(agentId, status, load, activeTasks) {
    // Strip 'acp/' prefix for ACP protocol
    const acpId = agentId.replace('acp/', '');
    return {
      jsonrpc: '2.0',
      method: 'agent.heartbeat',
      params: {
        agentId: acpId,
        status,
        load,
        activeTasks
      },
      id: crypto.randomUUID()
    };
  }

  getInternalId(acpId) {
    return this.idMap.get(acpId) || acpId;
  }
}

export default new ACPAgentAdapter();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/acp-adapter.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 80-PROJECTS/a2a-router/src/protocols/acp-adapter.js 80-PROJECTS/a2a-router/test/acp-adapter.test.js
git commit -m "feat(a2a-router): add ACPAgentAdapter for ACP-A2A agent bridging"
```

---

## Task 3: Create ACPGateway

**Files:**
- Create: `80-PROJECTS/a2a-router/src/protocols/acp-gateway.js`
- Test: `80-PROJECTS/a2a-router/test/acp-gateway.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
// test/acp-gateway.test.js
import { ACPGateway } from '../src/protocols/acp-gateway.js';

describe('ACPGateway', () => {
  const mockRouter = {
    routeMessage: jest.fn().mockReturnValue({ success: true }),
    registerAgent: jest.fn().mockReturnValue({ success: true }),
    on: jest.fn()
  };
  const gateway = new ACPGateway(mockRouter);

  describe('handleACPMessage()', () => {
    it('should route ACP request to A2A agent', () => {
      const acpMsg = {
        jsonrpc: '2.0',
        method: 'agent.request',
        params: {
          capabilities: ['coding'],
          targetAgent: 'a2a-agent-1',
          metadata: { priority: 'HIGH' }
        },
        id: 'msg-1'
      };

      gateway.handleACPMessage(acpMsg, 'acp-sender-1');

      expect(mockRouter.routeMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'TASK',
          priority: 'HIGH',
          from: 'acp/acp-sender-1',
          to: 'a2a-agent-1'
        })
      );
    });

    it('should emit error on invalid message', (done) => {
      gateway.on('error', (err) => {
        expect(err.message).toContain('Invalid ACP message');
        done();
      });

      gateway.handleACPMessage({ jsonrpc: '2.0' }, 'sender');
    });
  });

  describe('sendToACP()', () => {
    it('should convert A2A response to ACP format', () => {
      const a2aMsg = {
        id: 'int-42',
        type: 'TASK_RESULT',
        payload: { result: 'done' }
      };

      const result = gateway.sendToACP(a2aMsg, 'acp-receiver-1');

      expect(result).toEqual({
        jsonrpc: '2.0',
        result: { type: 'TASK_RESULT', payload: { result: 'done' } },
        id: 'int-42'
      });
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/acp-gateway.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```javascript
// src/protocols/acp-gateway.js
import { EventEmitter } from 'events';
import { ACPParser } from './acp-parser.js';
import { ACPAgentAdapter } from './acp-adapter.js';

export class ACPGateway extends EventEmitter {
  constructor(router, options = {}) {
    super();
    this.router = router;
    this.parser = new ACPParser();
    this.adapter = new ACPAgentAdapter(router);
    this.options = {
      enabled: true,
      ...options
    };

    // Listen for A2A events to convert to ACP
    this.router.on('message:deliver', (msg) => {
      this.handleA2AMessage(msg);
    });
  }

  handleACPMessage(acpMessage, acpAgentId) {
    try {
      const parsed = this.parser.parse(acpMessage);

      if (parsed.method === 'agent.request') {
        const internalMsg = this.parser.toA2A(
          parsed,
          `acp/${acpAgentId}`,
          parsed.params.targetAgent || 'router'
        );

        // Register ACP agent if not already
        this.adapter.registerACPAgent({
          id: acpAgentId,
          capabilities: parsed.params.capabilities || []
        });

        this.router.routeMessage(internalMsg);
      }

      return { success: true };
    } catch (err) {
      this.emit('error', err);
      return { success: false, error: err.message };
    }
  }

  sendToACP(a2aMessage, targetAcpAgentId) {
    return this.parser.toACP(a2aMessage, a2aMessage.originalId);
  }

  handleA2AMessage(a2aMessage) {
    // Extract ACP agent ID from internal ID
    if (a2aMessage.to.startsWith('acp/')) {
      const acpAgentId = a2aMessage.to.replace('acp/', '');
      this.sendToACP(a2aMessage, acpAgentId);
    }
  }

  start() {
    this.options.enabled = true;
    console.log('[ACP Gateway] Started');
  }

  stop() {
    this.options.enabled = false;
    console.log('[ACP Gateway] Stopped');
  }
}

export default new ACPGateway();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/acp-gateway.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 80-PROJECTS/a2a-router/src/protocols/acp-gateway.js 80-PROJECTS/a2a-router/test/acp-gateway.test.js
git commit -m "feat(a2a-router): add ACPGateway for ACP-A2A protocol translation"
```

---

## Task 4: Add ACP Tools to MCP Server

**Files:**
- Modify: `80-PROJECTS/a2a-router/src/server.js:1-30` (add imports and ACP gateway init)

- [ ] **Step 1: Add ACP gateway initialization and ACP tools**

Add to server.js after the router initialization:

```javascript
// Import ACP Gateway
import { ACPGateway } from './protocols/acp-gateway.js';

// Initialize ACP Gateway
const acpGateway = new ACPGateway(router, {
  enabled: true,
  port: 7890
});
```

Add these tools to the TOOLS array in server.js:

```javascript
// ACP Tools
{
  name: 'acp_send_message',
  description: 'Send message via ACP protocol (for ACP-native agents)',
  inputSchema: {
    type: 'object',
    properties: {
      method: {
        type: 'string',
        enum: ['agent.request', 'agent.notify', 'agent.cancel'],
        description: 'ACP method to invoke'
      },
      capabilities: {
        type: 'array',
        items: { type: 'string' },
        description: 'Requested capabilities'
      },
      targetAgent: {
        type: 'string',
        description: 'Target A2A agent ID (optional)'
      },
      priority: {
        type: 'string',
        enum: ['URGENT', 'HIGH', 'NORMAL', 'LOW'],
        default: 'NORMAL'
      },
      agentId: {
        type: 'string',
        description: 'Source ACP agent ID'
      }
    },
    required: ['method', 'agentId']
  }
},
{
  name: 'acp_register_agent',
  description: 'Register an ACP-native agent with the A2A router',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string', description: 'ACP agent ID' },
      capabilities: { type: 'array', items: { type: 'string' } },
      metadata: { type: 'object' }
    },
    required: ['agentId', 'capabilities']
  }
},
{
  name: 'acp_gateway_status',
  description: 'Get ACP Gateway status',
  inputSchema: {
    type: 'object',
    properties: {}
  }
}
```

Add handlers in the switch statement:

```javascript
case 'acp_send_message': {
  const acpMsg = {
    jsonrpc: '2.0',
    method: args.method,
    params: {
      capabilities: args.capabilities || [],
      targetAgent: args.targetAgent,
      metadata: { priority: args.priority || 'NORMAL' }
    },
    id: uuidv4()
  };
  const result = acpGateway.handleACPMessage(acpMsg, args.agentId);
  return {
    content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
  };
}

case 'acp_register_agent': {
  const result = acpGateway.adapter.registerACPAgent({
    id: args.agentId,
    capabilities: args.capabilities || [],
    metadata: args.metadata || {}
  });
  return {
    content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
  };
}

case 'acp_gateway_status': {
  return {
    content: [{
      type: 'text',
      text: JSON.stringify({
        enabled: acpGateway.options.enabled,
        stats: {
          messagesTranslated: 0,
          agentsRegistered: acpGateway.adapter.idMap.size
        }
      }, null, 2)
    }]
  };
}
```

- [ ] **Step 2: Test the server starts without errors**

Run: `cd 80-PROJECTS/a2a-router && node src/server.js &` (then Ctrl+C after 2 seconds)
Expected: No import errors, see "[A2A Router] MCP Server started"

- [ ] **Step 3: Commit**

```bash
git add 80-PROJECTS/a2a-router/src/server.js
git commit -m "feat(a2a-router): add ACP gateway tools to MCP server"
```

---

## Task 5: Integration Test

**Files:**
- Create: `80-PROJECTS/a2a-router/test/integration/acp-a2a.test.js`

- [ ] **Step 1: Write integration test**

```javascript
// test/integration/acp-a2a.test.js
import { A2ARouter } from '../src/router.js';
import { ACPGateway } from '../src/protocols/acp-gateway.js';

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

    const internalId = `acp/new-acp-agent`;
    const agent = router.agents.get(internalId);
    expect(agent).toBeDefined();
    expect(Array.from(agent.capabilities)).toEqual(['refactor']);
  });
});
```

- [ ] **Step 2: Run integration test**

Run: `cd 80-PROJECTS/a2a-router && node --experimental-vm-modules node_modules/.bin/jest test/integration/acp-a2a.test.js`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add 80-PROJECTS/a2a-router/test/integration/acp-a2a.test.js
git commit -m "test(a2a-router): add ACP-A2A integration test"
```

---

## Summary

| Task | Files | Status |
|------|-------|--------|
| 1. ACPParser | acp-parser.js + test | Pending |
| 2. ACPAgentAdapter | acp-adapter.js + test | Pending |
| 3. ACPGateway | acp-gateway.js + test | Pending |
| 4. MCP Server | server.js (modify) | Pending |
| 5. Integration | acp-a2a.test.js | Pending |

**After all tasks complete**, the ACP Gateway will:
- ✅ Parse ACP JSON-RPC 2.0 messages
- ✅ Register ACP agents in A2A registry with prefixed IDs
- ✅ Route ACP requests to A2A agents
- ✅ Convert A2A responses back to ACP format
- ✅ Be accessible via 3 new MCP tools (acp_send_message, acp_register_agent, acp_gateway_status)
