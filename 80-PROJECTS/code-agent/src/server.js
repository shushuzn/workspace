#!/usr/bin/env node
/**
 * Code Agent MCP Server
 * 
 * Intelligent code analysis with Semgrep + Tree-sitter
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import CodeAgent from './agent.js';

// Create agent instance
const agent = new CodeAgent();

// Create MCP server
const server = new Server(
  {
    name: 'code-agent',
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
    name: 'code_scan_security',
    description: 'Scan file/project for security vulnerabilities using Semgrep',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File or project path to scan'
        },
        configs: {
          type: 'array',
          items: { type: 'string' },
          description: 'Semgrep config sets (e.g., p/security-audit)'
        }
      },
      required: ['path']
    }
  },
  {
    name: 'code_analyze_quality',
    description: 'Analyze code quality metrics using Tree-sitter',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File path to analyze'
        },
        content: {
          type: 'string',
          description: 'File content (optional, read from file if not provided)'
        }
      },
      required: ['path']
    }
  },
  {
    name: 'code_analyze_file',
    description: 'Full analysis of a file (security + quality)',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File path'
        },
        options: {
          type: 'object',
          properties: {
            checkSecurity: { type: 'boolean' },
            checkQuality: { type: 'boolean' },
            checkComplexity: { type: 'boolean' }
          }
        }
      },
      required: ['path']
    }
  },
  {
    name: 'code_scan_project',
    description: 'Scan entire project for issues',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Project root path'
        },
        excludePatterns: {
          type: 'array',
          items: { type: 'string' },
          description: 'Patterns to exclude (e.g., node_modules)'
        }
      },
      required: ['path']
    }
  },
  {
    name: 'code_get_metrics',
    description: 'Get code complexity and structure metrics',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File path'
        }
      },
      required: ['path']
    }
  },
  {
    name: 'code_get_findings',
    description: 'Get findings from last analysis',
    inputSchema: {
      type: 'object',
      properties: {
        severity: {
          type: 'string',
          enum: ['ERROR', 'WARNING', 'INFO'],
          description: 'Filter by severity'
        }
      }
    }
  },
  {
    name: 'code_get_status',
    description: 'Get agent status and capabilities',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'code_get_ast',
    description: 'Query AST structure by node type',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File path to analyze'
        },
        nodeType: {
          type: 'string',
          description: 'Node type to query (e.g., function_declaration, class, method_definition)'
        },
        language: {
          type: 'string',
          enum: ['javascript', 'typescript', 'python'],
          description: 'Language (auto-detected from extension if omitted)'
        }
      },
      required: ['path', 'nodeType']
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
      case 'code_scan_security': {
        const result = await agent.securityScan(args.path, args.configs);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_analyze_quality': {
        const result = await agent.qualityCheck(args.path, args.content);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_analyze_file': {
        const result = await agent.analyzeFile(args.path, args.options);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_scan_project': {
        const result = await agent.scanProject(args.path, args.excludePatterns);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_get_metrics': {
        const result = await agent.getMetrics(args.path);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_get_findings': {
        const result = agent.getFindings(args.severity);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_get_status': {
        const result = agent.getStatus();
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'code_get_ast': {
        const result = await agent.getAst(args.path, args.nodeType, args.language);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
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

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.log('[Code Agent] MCP Server started');
  console.log('[Code Agent] Tools:', TOOLS.map(t => t.name).join(', '));
}

main().catch((error) => {
  console.error('[Code Agent] Fatal error:', error);
  process.exit(1);
});