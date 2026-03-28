import { MCPAdapter } from './adapters/mcp-adapter';
import { A2AAdapter } from './adapters/a2a-adapter';

interface OrchestratorConfig {
    orchestratorUrl: string;
    agentId: string;
    capabilities: string[];
}

/**
 * Bridge between Go orchestrator and TypeScript agent-islands
 * This allows TypeScript agents to submit tasks to the Go orchestrator
 * and receive results back for further processing.
 */
export class AgentIslandsBridge {
    private mcpAdapter: MCPAdapter;
    private a2aAdapter: A2AAdapter;
    private config: OrchestratorConfig;

    constructor(config: OrchestratorConfig) {
        this.config = config;
        this.mcpAdapter = new MCPAdapter(config.orchestratorUrl);
        this.a2aAdapter = new A2AAdapter(config.agentId, config.capabilities);
    }

    /**
     * Submit a task to the Go orchestrator via MCP
     */
    async submitTask(task: string, options?: { maxIterations?: number; threshold?: number }) {
        // In production, this would call through the MCP adapter
        // For now, return a placeholder result
        return {
            status: 'submitted',
            task,
            options,
        };
    }

    /**
     * Register this bridge with the A2A network
     */
    async register() {
        await this.a2aAdapter.register(async (msg) => {
            console.log('Received A2A message:', msg);
        });
    }

    /**
     * Get the MCP adapter for direct tool access
     */
    getMCPAdapter(): MCPAdapter {
        return this.mcpAdapter;
    }

    /**
     * Get the A2A adapter for peer communication
     */
    getA2AAdapter(): A2AAdapter {
        return this.a2aAdapter;
    }
}
