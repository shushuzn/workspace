/**
 * ACPParser - JSON-RPC 2.0 parser for ACP protocol
 * Translates between ACP JSON-RPC format and A2A internal format
 */

export class ACPParser {
  /**
   * Parse and validate incoming ACP message
   * @param {Object} message - ACP JSON-RPC message
   * @returns {Object} - Parsed message
   * @throws {Error} - If message is invalid
   */
  parse(message) {
    if (!message.jsonrpc) {
      throw new Error('Invalid ACP message: missing jsonrpc');
    }
    if (!message.method) {
      throw new Error('Invalid ACP message: missing method');
    }
    return message;
  }

  /**
   * Convert A2A message to ACP JSON-RPC response format
   * @param {Object} a2aMessage - A2A internal message
   * @param {string} originalId - Original ACP message ID for correlation
   * @returns {Object} - ACP JSON-RPC response
   */
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

  /**
   * Convert ACP request to A2A internal format
   * @param {Object} acpMessage - ACP JSON-RPC request
   * @param {string} fromAgentId - Source agent ID (ACP format)
   * @param {string} toAgentId - Target agent ID
   * @returns {Object} - A2A internal message
   */
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
