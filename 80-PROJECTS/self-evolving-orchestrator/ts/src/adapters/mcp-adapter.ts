import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

interface OrchestratorStatus {
  ready: boolean;
  peers: number;
  activeTasks: number;
}

interface EvolutionResult {
  finalTask: string;
  subtasks: string[];
  iterations: number;
  finalScore: number;
  converged: boolean;
}

export class MCPAdapter {
  private server: Server;
  private orchestratorUrl: string;

  constructor(orchestratorUrl: string = 'http://localhost:8080') {
    this.orchestratorUrl = orchestratorUrl;
    this.server = new Server(
      { name: 'self-evolving-orchestrator', version: '1.0.0' },
      { capabilities: { tools: {} } }
    );
    this.setupTools();
  }

  private setupTools() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'orchestrator_process',
          description: 'Submit a task for self-evolving orchestration',
          inputSchema: {
            type: 'object',
            properties: {
              task: { type: 'string', description: 'The task to orchestrate' },
              maxIterations: { type: 'number', default: 3 },
              threshold: { type: 'number', default: 0.7 },
            },
          },
        },
        {
          name: 'orchestrator_status',
          description: 'Get orchestrator status',
          inputSchema: { type: 'object', properties: {} },
        },
        {
          name: 'orchestrator_peers',
          description: 'List registered peer agents',
          inputSchema: { type: 'object', properties: {} },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'orchestrator_process':
          return await this.processTask(args.task, args.maxIterations, args.threshold);
        case 'orchestrator_status':
          return await this.getStatus();
        case 'orchestrator_peers':
          return await this.listPeers();
        default:
          return { error: `Unknown tool: ${name}` };
      }
    });
  }

  private async processTask(task: string, maxIter?: number, threshold?: number): Promise<{ content: Array<{ type: string; text: string }> }> {
    try {
      const response = await fetch(`${this.orchestratorUrl}/api/v1/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, maxIterations: maxIter, threshold }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result: EvolutionResult = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2),
        }],
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
      };
    }
  }

  private async getStatus(): Promise<{ content: Array<{ type: string; text: string }> }> {
    return {
      content: [{ type: 'text', text: JSON.stringify({ ready: true, peers: 0, activeTasks: 0 }) }],
    };
  }

  private async listPeers(): Promise<{ content: Array<{ type: string; text: string }> }> {
    return {
      content: [{ type: 'text', text: '[]' }],
    };
  }

  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MCP adapter running');
  }
}
