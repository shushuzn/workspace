/**
 * ACPGateway - Protocol gateway for ACP-A2A translation
 * Bidirectional translation between ACP JSON-RPC and A2A messages
 */

import { EventEmitter } from 'events';
import { ACPParser } from './acp-parser.js';
import { ACPAgentAdapter } from './acp-adapter.js';

export class ACPGateway extends EventEmitter {
  /**
   * @param {Object} router - A2A Router instance
   * @param {Object} options - Gateway options
   */
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

  /**
   * Handle incoming ACP message from external agent
   * @param {Object} acpMessage - ACP JSON-RPC message
   * @param {string} acpAgentId - Source ACP agent ID
   * @returns {Object} - Result of handling
   */
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

  /**
   * Convert A2A message to ACP format and send
   * @param {Object} a2aMessage - A2A internal message
   * @param {string} targetAcpAgentId - Target ACP agent ID
   * @returns {Object} - ACP message
   */
  sendToACP(a2aMessage, targetAcpAgentId) {
    return this.parser.toACP(a2aMessage, a2aMessage.originalId);
  }

  /**
   * Handle A2A message routed to an ACP agent
   * @param {Object} a2aMessage - A2A internal message
   */
  handleA2AMessage(a2aMessage) {
    if (a2aMessage.to.startsWith('acp/')) {
      const acpAgentId = a2aMessage.to.replace('acp/', '');
      this.sendToACP(a2aMessage, acpAgentId);
    }
  }

  /** Start the gateway */
  start() {
    this.options.enabled = true;
    console.log('[ACP Gateway] Started');
  }

  /** Stop the gateway */
  stop() {
    this.options.enabled = false;
    console.log('[ACP Gateway] Stopped');
  }
}
