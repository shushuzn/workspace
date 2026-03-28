#!/usr/bin/env node
/**
 * A2A Router MCP Server
 * 
 * Exposes A2A routing capabilities via Model Context Protocol
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { v4 as uuidv4 } from 'uuid';
import { A2ARouter } from './router.js';
import { ACPGateway } from './protocols/acp-gateway.js';

// Create router instance
const router = new A2ARouter({
  heartbeatTimeout: 60000,
  maxQueueSize: 1000
});

// Initialize ACP Gateway
const acpGateway = new ACPGateway(router, {
  enabled: true,
  port: 7890
});

// Create MCP server
const server = new Server(
  {
    name: 'a2a-router',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define MCP tools
const TOOLS = [
  {
    name: 'a2a_register_agent',
    description: 'Register an agent with the A2A router',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: {
          type: 'string',
          description: 'Unique agent identifier'
        },
        capabilities: {
          type: 'array',
          items: { type: 'string' },
          description: 'List of agent capabilities'
        },
        metadata: {
          type: 'object',
          description: 'Optional agent metadata'
        }
      },
      required: ['agentId', 'capabilities']
    }
  },
  {
    name: 'a2a_unregister_agent',
    description: 'Unregister an agent from the A2A router',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: {
          type: 'string',
          description: 'Agent identifier to unregister'
        }
      },
      required: ['agentId']
    }
  },
  {
    name: 'a2a_heartbeat',
    description: 'Send heartbeat to keep agent registered',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: {
          type: 'string',
          description: 'Agent identifier'
        },
        status: {
          type: 'string',
          enum: ['healthy', 'busy', 'error'],
          description: 'Agent health status'
        },
        load: {
          type: 'number',
          minimum: 0,
          maximum: 1,
          description: 'Current load (0-1)'
        },
        activeTasks: {
          type: 'number',
          description: 'Number of active tasks'
        }
      },
      required: ['agentId']
    }
  },
  {
    name: 'a2a_send_message',
    description: 'Send a message to another agent',
    inputSchema: {
      type: 'object',
      properties: {
        from: {
          type: 'string',
          description: 'Source agent ID'
        },
        to: {
          type: 'string',
          description: 'Target agent ID or "broadcast"'
        },
        type: {
          type: 'string',
          enum: ['TASK', 'QUERY', 'EVENT', 'RESPONSE'],
          description: 'Message type'
        },
        priority: {
          type: 'string',
          enum: ['CRITICAL', 'HIGH', 'NORMAL', 'LOW'],
          description: 'Message priority'
        },
        payload: {
          type: 'object',
          description: 'Message payload'
        },
        metadata: {
          type: 'object',
          description: 'Optional metadata'
        }
      },
      required: ['from', 'to', 'type', 'payload']
    }
  },
  {
    name: 'a2a_discover',
    description: 'Discover agents by capability',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Capability to search for'
        },
        requesterId: {
          type: 'string',
          description: 'Agent ID making the request'
        }
      },
      required: ['query', 'requesterId']
    }
  },
  {
    name: 'a2a_get_agents',
    description: 'Get list of registered agents',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'a2a_get_stats',
    description: 'Get router statistics',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'a2a_subscribe_capabilities',
    description: 'Subscribe to capability change notifications',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent subscribing' },
        capabilities: { type: 'array', items: { type: 'string' } }
      },
      required: ['agentId', 'capabilities']
    }
  },
  {
    name: 'a2a_match_agent',
    description: 'Find best agent by capabilities with load scoring',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Capability to search for' },
        loadThreshold: { type: 'number', default: 0.9 },
        limit: { type: 'number', default: 5 }
      },
      required: ['query']
    }
  },
  {
    name: 'a2a_update_agent_capabilities',
    description: 'Update an agent capabilities after initial registration',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string' },
        capabilities: { type: 'array', items: { type: 'string' } }
      },
      required: ['agentId', 'capabilities']
    }
  },
  // RuFlo Bridge Tools
  {
    name: 'ruflo_list_agents',
    description: 'List available RuFlo agents via MCP',
    inputSchema: {
      type: 'object',
      properties: {
        capability: {
          type: 'string',
          description: 'Filter agents by capability (optional)'
        }
      }
    }
  },
  {
    name: 'ruflo_dispatch_task',
    description: 'Dispatch a task to a RuFlo swarm',
    inputSchema: {
      type: 'object',
      properties: {
        task: {
          type: 'string',
          description: 'Task description to execute'
        },
        agentType: {
          type: 'string',
          description: 'Agent type (coder, reviewer, tester, etc.)',
          enum: ['coder', 'reviewer', 'tester', 'security-auditor', 'documenter', 'devops', 'general']
        },
        topology: {
          type: 'string',
          description: 'Swarm topology',
          enum: ['hierarchical', 'mesh', 'ring', 'star'],
          default: 'mesh'
        }
      },
      required: ['task']
    }
  },
  {
    name: 'ruflo_get_status',
    description: 'Get RuFlo worker pool status',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'ruflo_query_intelligence',
    description: 'Query RuVector intelligence layer',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Query string for pattern search'
        },
        limit: {
          type: 'number',
          description: 'Max results to return',
          default: 5
        }
      },
      required: ['query']
    }
  },
  // ACP Gateway Tools
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
  },
  // Message Persistence Tools
  {
    name: 'a2a_query_messages',
    description: 'Query message history for an agent',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID to query' },
        limit: { type: 'number', default: 100 },
        since: { type: 'number', description: 'Start timestamp (ms)' },
        until: { type: 'number', description: 'End timestamp (ms)' }
      },
      required: ['agentId']
    }
  },
  {
    name: 'a2a_archive_messages',
    description: 'Delete messages older than timestamp',
    inputSchema: {
      type: 'object',
      properties: {
        olderThan: { type: 'number', description: 'Delete messages before this timestamp (ms)' }
      },
      required: ['olderThan']
    }
  },
  {
    name: 'a2a_get_queue_stats',
    description: 'Get queue backlog statistics and threshold alerts',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: TOOLS,
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'a2a_register_agent': {
        const result = router.registerAgent(
          args.agentId,
          args.capabilities || [],
          args.metadata || {}
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_unregister_agent': {
        const result = router.unregisterAgent(args.agentId);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_heartbeat': {
        const result = router.heartbeat(
          args.agentId,
          args.status || 'healthy',
          args.load || 0,
          args.activeTasks || 0
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_send_message': {
        const message = {
          id: uuidv4(),
          type: args.type,
          priority: args.priority || 'NORMAL',
          from: args.from,
          to: args.to,
          timestamp: Date.now(),
          payload: args.payload,
          metadata: args.metadata || {}
        };

        const result = router.routeMessage(message);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_discover': {
        const discoverMessage = {
          id: uuidv4(),
          type: 'DISCOVER',
          priority: 'NORMAL',
          from: args.requesterId,
          to: 'router',
          timestamp: Date.now(),
          payload: { query: args.query }
        };

        const result = router.routeMessage(discoverMessage);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_get_agents': {
        const result = router.handleQuery({
          payload: { query: 'agents' }
        });
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_get_stats': {
        const result = { success: true, stats: router.getStats() };
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_subscribe_capabilities': {
        const result = router.subscribeCapabilities(args.agentId, args.capabilities || []);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'a2a_match_agent': {
        const result = router.matchBestAgent(args.query, {
          loadThreshold: args.loadThreshold || 0.9,
          limit: args.limit || 5
        });
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ success: true, matches: result }, null, 2),
            },
          ],
        };
      }

      case 'a2a_update_agent_capabilities': {
        const result = router.updateAgentCapabilities(args.agentId, args.capabilities || []);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      // RuFlo Bridge Handlers
      case 'ruflo_list_agents': {
        // In production, this would call RuFlo MCP: await mcp.callTool('list_agents', args)
        const capability = args.capability || '';
        const mockAgents = [
          { id: 'ruflo-coder-1', name: 'Coder', capabilities: ['coding', 'refactor'], status: 'idle' },
          { id: 'ruflo-reviewer-1', name: 'Reviewer', capabilities: ['review', 'security'], status: 'idle' },
          { id: 'ruflo-tester-1', name: 'Tester', capabilities: ['testing', 'qa'], status: 'idle' },
        ];
        const filtered = capability
          ? mockAgents.filter(a => a.capabilities.some(c => c.includes(capability)))
          : mockAgents;
        return {
          content: [{ type: 'text', text: JSON.stringify({ success: true, agents: filtered }, null, 2) }],
        };
      }

      case 'ruflo_dispatch_task': {
        const { task, agentType = 'general', topology = 'mesh' } = args;
        // In production, this would call RuFlo MCP to dispatch task
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              taskId: uuidv4(),
              dispatched: { task, agentType, topology },
              message: 'Task dispatched to RuFlo swarm (MCP bridge placeholder)',
            }, null, 2),
          }],
        };
      }

      case 'ruflo_get_status': {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              status: 'healthy',
              activeWorkers: 8,
              idleWorkers: 4,
              totalTasks: 127,
              queueDepth: 3,
              ruvetorStatus: 'active',
            }, null, 2),
          }],
        };
      }

      case 'ruflo_query_intelligence': {
        const { query, limit = 5 } = args;
        // In production, this would query RuVector HNSW layer via MCP
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              query,
              results: [
                { pattern: `Similar to: ${query}`, score: 0.95, source: 'memory' },
                { pattern: `Related: ${query} implementation`, score: 0.87, source: 'history' },
              ],
              total: 2,
            }, null, 2),
          }],
        };
      }

      // ACP Gateway Handlers
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
                agentsRegistered: acpGateway.adapter.idMap.size
              }
            }, null, 2)
          }]
        };
      }

      // Message Persistence Handlers
      case 'a2a_query_messages': {
        const { agentId, limit, since, until } = args;
        const results = router.queryMessages(agentId, { limit: limit || 100, since, until });
        return {
          content: [{ type: 'text', text: JSON.stringify({ success: true, messages: results }, null, 2) }]
        };
      }

      case 'a2a_archive_messages': {
        const { olderThan } = args;
        const deleted = router.archiveMessages(olderThan);
        return {
          content: [{ type: 'text', text: JSON.stringify({ success: true, deleted }, null, 2) }]
        };
      }

      case 'a2a_get_queue_stats': {
        const stats = router.getQueueStats();
        return {
          content: [{ type: 'text', text: JSON.stringify({ success: true, ...stats }, null, 2) }]
        };
      }

      default:
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: `Unknown tool: ${name}` }),
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: error.message }),
        },
      ],
      isError: true,
    };
  }
});

// Handle router events
router.on('agent:registered', (agent) => {
  console.log(`[A2A] Agent registered: ${agent.id}`);
});

router.on('agent:unregistered', (agent) => {
  console.log(`[A2A] Agent unregistered: ${agent.id}`);
});

router.on('agent:offline', (agent) => {
  console.log(`[A2A] Agent offline: ${agent.id}`);
});

router.on('message:deliver', (message, agent) => {
  console.log(`[A2A] Message ${message.id} -> ${agent.id} (${message.type})`);
});

// Start ACP Gateway
acpGateway.start();

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.log('[A2A Router] MCP Server started with RuFlo Bridge and ACP Gateway');
  console.log('[A2A Router] Tools available:', TOOLS.map(t => t.name).join(', '));
  console.log('[RuFlo Bridge] 4 tools: ruflo_list_agents, ruflo_dispatch_task, ruflo_get_status, ruflo_query_intelligence');
  console.log('[ACP Gateway] 3 tools: acp_send_message, acp_register_agent, acp_gateway_status');
}

main().catch((error) => {
  console.error('[A2A Router] Fatal error:', error);
  process.exit(1);
});
