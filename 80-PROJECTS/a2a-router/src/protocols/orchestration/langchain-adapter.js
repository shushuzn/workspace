/**
 * LangChainAdapter - LangChain AI Agent integration
 *
 * Provides agent creation and invocation for LangChain-based AI agents.
 * Uses @langchain/langgraph for modern LangChain agentic workflows.
 *
 *   npm install @langchain/langgraph @langchain/core
 */

import { createHash } from 'crypto';
import { StateGraph, Annotation, START, END } from '@langchain/langgraph';
import { addMessages } from '@langchain/langgraph';
import { ToolMessage } from '@langchain/core/messages';
import { SqliteCheckpointSaver } from './sqlite-checkpoint-saver.js';

export class LangChainAdapter {
  /**
   * @param {Object} options
   * @param {string} [options.checkpointDb] - Path to SQLite checkpoint DB (default: ':memory:')
   * @param {boolean} [options.persist=true]  - Use SQLite persistence (false = in-memory)
   */
  constructor(options = {}) {
    this.agents = new Map();   // agentId -> { config, createdAt }
    this.runs = new Map();    // runId -> { agentId, status, result }
    this.graphs = new Map();  // agentId -> compiled graph (cached)
    this.sessions = new Map(); // agentId -> sessionId (stable thread_id)

    const dbPath = options.checkpointDb ?? (options.persist !== false ? './data/checkpoints.db' : ':memory:');
    this.checkpointer = options.persist !== false
      ? new SqliteCheckpointSaver(dbPath)
      : null;
  }

  /**
   * Create a LangChain agent
   * @param {string} agentId - Unique agent identifier
   * @param {Object} config - Agent configuration
   * @param {string} config.model - LLM model name (e.g. 'gpt-4')
   * @param {string[]} config.capabilities - Agent capabilities
   * @param {Object} config.tools - Tool definitions
   */
  async createAgent(agentId, config = {}) {
    if (this.agents.has(agentId)) {
      return { success: false, error: 'AGENT_ALREADY_EXISTS' };
    }

    this.agents.set(agentId, {
      config,
      createdAt: new Date(),
      runs: []
    });

    return { success: true, agentId };
  }

  /**
   * Build or retrieve cached compiled StateGraph for an agent.
   * Uses ReAct pattern: route (tool_call?) → tool OR end
   * @param {string} agentId
   * @returns {Promise<CompiledStateGraph>}
   */
  async _getGraph(agentId) {
    if (this.graphs.has(agentId)) {
      return this.graphs.get(agentId);
    }

    // Define the state schema using LangGraph Annotation
    const AgentState = Annotation.Root({
      messages: Annotation({
        reducer: addMessages,
        default: () => []
      })
    });

    // ── Built-in mock tools (no API key required) ────────────────────────
    const availableTools = {
      calculator: {
        description: 'Evaluate a mathematical expression',
        schema: {
          type: 'object',
          properties: {
            expression: { type: 'string', description: 'Math expression, e.g. "2 + 2 * 3"' }
          },
          required: ['expression']
        },
        fn: ({ expression }) => {
          try {
            if (!/^[\d+\-*/(). ]+$/.test(expression)) throw new Error('Invalid');
            const result = Function(`"use strict"; return (${expression})`)();
            return `[CALCULATOR] ${expression} = ${result}`;
          } catch {
            return `[CALCULATOR] Invalid expression: ${expression}`;
          }
        }
      },
      wikipedia_lookup: {
        description: 'Look up a topic on Wikipedia',
        schema: {
          type: 'object',
          properties: {
            topic: { type: 'string', description: 'Topic to look up' }
          },
          required: ['topic']
        },
        fn: ({ topic }) => `[WIKIPEDIA] "${topic}": A notable article covering key aspects and history of the subject.`
      },
      datetime_now: {
        description: 'Get current date and time',
        schema: {
          type: 'object',
          properties: {
            timezone: { type: 'string', description: 'Timezone, e.g. "Asia/Shanghai" or "UTC"' }
          }
        },
        fn: ({ timezone }) => {
          try {
            const now = timezone ? new Date().toLocaleString('en-US', { timeZone: timezone }) : new Date().toISOString();
            return `[DATETIME] Current time${timezone ? ` (${timezone})` : ' (UTC)'}: ${now}`;
          } catch {
            return `[DATETIME] Current time: ${new Date().toISOString()}`;
          }
        }
      },
      uuid_generate: {
        description: 'Generate a random UUID v4',
        schema: { type: 'object', properties: {}, required: [] },
        fn: () => `[UUID] Generated: ${globalThis.crypto.randomUUID()}`
      },
      hash_compute: {
        description: 'Compute SHA-256 hash of a string',
        schema: {
          type: 'object',
          properties: {
            text: { type: 'string', description: 'Text to hash' }
          },
          required: ['text']
        },
        fn: ({ text }) => {
          const hash = createHash('sha256').update(text).digest('hex');
          return `[HASH] SHA-256("${text.slice(0, 20)}${text.length > 20 ? '...' : ''}") = ${hash.slice(0, 16)}...`;
        }
      },
      json_format: {
        description: 'Pretty-print JSON with indentation',
        schema: {
          type: 'object',
          properties: {
            data: { type: 'string', description: 'JSON string or object to format' }
          },
          required: ['data']
        },
        fn: ({ data }) => {
          try {
            const parsed = typeof data === 'string' ? JSON.parse(data) : data;
            return `[JSON] Formatted:\n${JSON.stringify(parsed, null, 2)}`;
          } catch {
            return `[JSON] Failed to parse: ${data}`;
          }
        }
      }
    };

    // ── Node: call model (decides tool or response) ─────────────────────
    const callModelNode = (state) => {
      const lastMsg = state.messages[state.messages.length - 1];
      const content = typeof lastMsg?.content === 'string' ? lastMsg.content : '';

      // Parse mock tool calls: call_tool(name) or call_tool(name, {args})
      // e.g. call_tool(calculator) or call_tool(calculator, {"expression":"2+2"})
      const toolCallMatch = content.match(/^call_tool\(([^,]+)(?:,\s*(\{.*\}))?\)$/);
      if (toolCallMatch) {
        const toolName = toolCallMatch[1].trim();
        const tool = availableTools[toolName];
        if (tool) {
          let args = {};
          if (toolCallMatch[2]) {
            try { args = JSON.parse(toolCallMatch[2]); } catch { /* ignore bad JSON */ }
          }
          const toolResult = `[TOOL ${toolName}] ${tool.description} — args: ${JSON.stringify(args)} — result: ${tool.fn(args)}`;
          return {
            messages: [new ToolMessage({ content: toolResult, tool_call_id: toolName })]
          };
        }
      }

      // Parse request for tool
      const toolRequestMatch = content.match(/^use_tool\(([^)]+)\)$/);
      if (toolRequestMatch) {
        const toolName = toolRequestMatch[1];
        const tool = availableTools[toolName];
        if (tool) {
          return {
            messages: [{
              type: 'ai',
              content: `[TOOL_CALL] ${toolName} — schema: ${JSON.stringify(tool.schema)}`
            }]
          };
        }
      }

      // Default: simple response with tool availability hint
      return {
        messages: [{
          type: 'ai',
          content: `[LangGraph Agent ${agentId}] received: ${content}\n\nAvailable tools: ${Object.keys(availableTools).join(', ')}\n\nTo use a tool, send: use_tool(tool_name)`
        }]
      };
    };

    // ── Conditional routing: route [TOOL*] back to model, else end ───────
    const routeOrEnd = (state) => {
      const lastMsg = state.messages[state.messages.length - 1];
      if (!lastMsg) return 'callModel';
      const content = typeof lastMsg?.content === 'string' ? lastMsg.content : '';
      // [TOOL_CALL] = request to use tool, [TOOL ...] = tool result → both loop back
      if (content.startsWith('[TOOL')) return 'callModel';
      return END;
    };

    const graph = new StateGraph(AgentState)
      .addNode('callModel', callModelNode)
      .addEdge(START, 'callModel')
      .addConditionalEdges('callModel', routeOrEnd, {
        'callModel': 'callModel',
        [END]: END
      })
      .compile({ checkpointer: this.checkpointer });

    this.graphs.set(agentId, graph);
    return graph;
  }

  /**
   * Invoke a LangChain agent
   * @param {string} agentId - Agent to invoke
   * @param {Object} input - Input payload
   * @param {string} input.messages - Chat messages
   * @param {Object} context - Execution context
   * @param {string} [context.sessionId] - Optional session ID (stable conversation thread)
   */
  async invoke(agentId, input = {}, context = {}) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return { success: false, error: 'AGENT_NOT_FOUND' };
    }

    // Use provided sessionId or reuse existing, or create new one
    const sessionId = context.sessionId
      || this.sessions.get(agentId)
      || `session-${globalThis.crypto.randomUUID()}`;
    this.sessions.set(agentId, sessionId);

    const runId = `run-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const startTime = Date.now();

    try {
      const graph = await this._getGraph(agentId);

      // Normalize messages to LangGraph format
      const messages = (input.messages || []).map(msg => ({
        type: msg.role === 'user' ? 'human' : (msg.role === 'assistant' ? 'ai' : 'system'),
        content: msg.content || String(msg)
      }));

      // Execute the graph — checkpointer auto-restores prior state from thread_id
      const result = await graph.invoke(
        { messages },
        { configurable: { thread_id: sessionId } }
      );

      const lastMsg = result.messages[result.messages.length - 1];
      const output = typeof lastMsg?.content === 'string' ? lastMsg.content : String(lastMsg || '');

      const invokeResult = {
        runId,
        agentId,
        sessionId,
        output,
        model: agent.config.model || 'langgraph',
        latencyMs: Date.now() - startTime
      };

      this.runs.set(runId, {
        agentId,
        status: 'completed',
        result: invokeResult,
        completedAt: new Date()
      });

      return { success: true, ...invokeResult };
    } catch (err) {
      return {
        success: false,
        error: 'INVOCATION_FAILED',
        details: err.message,
        runId
      };
    }
  }

  /**
   * Stop a running agent execution
   * @param {string} runId - Run identifier
   */
  async stop(runId) {
    const run = this.runs.get(runId);
    if (!run) {
      return { success: false, error: 'RUN_NOT_FOUND' };
    }
    run.status = 'stopped';
    return { success: true, runId };
  }

  /**
   * Get status of an agent run
   * @param {string} runId - Run identifier
   */
  async status(runId) {
    const run = this.runs.get(runId);
    if (!run) {
      return { success: false, error: 'RUN_NOT_FOUND' };
    }
    return { success: true, runId, status: run.status };
  }

  /**
   * List all registered agents
   */
  listAgents() {
    return Array.from(this.agents.entries()).map(([id, data]) => ({
      agentId: id,
      config: data.config,
      createdAt: data.createdAt
    }));
  }
}

export default LangChainAdapter;
