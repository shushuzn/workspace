import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { Registry } from './registry.mjs';
import { Planner } from './planner.mjs';
import { Executor } from './executor.mjs';
const SERVER_NAME = 'task-orchestrator';
const SERVER_VERSION = '1.0.0';
function buildServer(registry) {
    const server = new Server({ name: SERVER_NAME, version: SERVER_VERSION }, { capabilities: { tools: {} } });
    const tools = [
        {
            name: 'task_parse',
            description: 'Parse a natural language prompt into a task execution plan without running it',
            inputSchema: {
                type: 'object',
                properties: {
                    prompt: { type: 'string', description: 'Natural language prompt describing the task' },
                },
                required: ['prompt'],
            },
        },
        {
            name: 'task_execute',
            description: 'Execute a task from a natural language prompt using available adapters',
            inputSchema: {
                type: 'object',
                properties: {
                    prompt: { type: 'string', description: 'Natural language prompt describing the task' },
                    outputFormat: {
                        type: 'string',
                        enum: ['text', 'json', 'yaml'],
                        description: 'Output format (default: text)',
                        default: 'text',
                    },
                },
                required: ['prompt'],
            },
        },
        {
            name: 'task_list_adapters',
            description: 'List all available adapters and their capabilities',
            inputSchema: {
                type: 'object',
                properties: {},
            },
        },
    ];
    server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools }));
    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;
        try {
            if (name === 'task_parse') {
                const planner = new Planner(registry);
                const result = planner.parse(args.prompt);
                return {
                    content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
                };
            }
            if (name === 'task_execute') {
                const planner = new Planner(registry);
                const { steps, errors, warnings } = planner.parse(args.prompt);
                if (steps.length === 0) {
                    return {
                        content: [{ type: 'text', text: `No steps generated. Errors: ${errors.join('; ')}` }],
                    };
                }
                const executor = new Executor(registry, { verbose: false });
                const results = await executor.execute(steps, { prompt: args.prompt });
                const outputFormat = args.outputFormat ?? 'text';
                if (outputFormat === 'json' || outputFormat === 'yaml') {
                    return {
                        content: [{ type: 'text', text: JSON.stringify({ steps, results, errors, warnings }, null, 2) }],
                    };
                }
                // text output
                const lines = [];
                for (let i = 0; i < steps.length; i++) {
                    const r = results[i];
                    const icon = r?.success ? '✓' : '✗';
                    lines.push(`${icon} [${i + 1}] ${steps[i].adapterId}: ${steps[i].command} → ${r?.success ? 'OK' : r?.error ?? 'unknown'}`);
                }
                return { content: [{ type: 'text', text: lines.join('\n') }] };
            }
            if (name === 'task_list_adapters') {
                const adapters = registry.list();
                const lines = adapters.map(a => `${a.id} [${a.type}]`);
                return { content: [{ type: 'text', text: lines.join('\n') }] };
            }
            throw new Error(`Unknown tool: ${name}`);
        }
        catch (err) {
            return {
                content: [{ type: 'text', text: `Error: ${err instanceof Error ? err.message : String(err)}` }],
                isError: true,
            };
        }
    });
    return server;
}
export async function runMcpServer() {
    const registry = new Registry();
    await registry.load();
    const server = buildServer(registry);
    const transport = new StdioServerTransport();
    await server.connect(transport);
    // Keep process alive — MCP server runs until client disconnects
    await new Promise(() => { });
}
