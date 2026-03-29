/**
 * StockAnalysisAdapter - Connects to stock-analysis-mcp Python server
 * and exposes its tools as a capability.
 */

import { PythonMCPClient } from './python-mcp-client.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export class StockAnalysisAdapter {
  constructor(options = {}) {
    this.client = null;
    this.tools = new Map();
    this.ready = false;
    this.projectRoot = options.projectRoot
      || path.resolve(__dirname, '../../../..');
  }

  /** Start the Python MCP server and handshakes */
  async start() {
    if (this.client) return;

    const serverPath = path.resolve(
      this.projectRoot,
      '80-PROJECTS/stock-analysis-mcp-test/src'
    );

    this.client = new PythonMCPClient({
      command: 'python',
      args: ['-c', 'import src.server'],
      cwd: serverPath
    });

    this.client.on('error', (err) => {
      console.error('[StockAnalysisAdapter] Python stderr:', err);
    });

    try {
      await this.client.start();
      this.tools = await this.client._listTools();
      this.ready = true;
    } catch (err) {
      console.error('[StockAnalysisAdapter] Failed to start Python MCP server:', err.message);
      throw err;
    }
  }

  /** Stop the subprocess */
  stop() {
    if (this.client) {
      this.client.stop();
      this.client = null;
      this.ready = false;
    }
  }

  /**
   * Call a stock analysis tool.
   * @param {string} toolName - e.g. 'get_quote', 'calc_macd'
   * @param {Object} input - Tool arguments
   */
  async call(toolName, input = {}) {
    if (!this.client || !this.ready) {
      throw new Error('StockAnalysisAdapter not started');
    }
    const result = await this.client.callTool(toolName, input);
    return result;
  }

  /** Returns the list of available tools */
  getTools() {
    return this.client ? this.client.tools : [];
  }
}

export default StockAnalysisAdapter;
