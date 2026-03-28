/**
 * ACPAgentAdapter - Bridge between ACP agents and A2A router
 * Handles agent registration and ID mapping
 */

export class ACPAgentAdapter {
  constructor(router) {
    this.router = router;
    /** @type {Map<string, string>} ACP ID -> Internal ID */
    this.idMap = new Map();
  }

  /**
   * Register an ACP agent with the A2A router
   * @param {Object} acpAgent - ACP agent info
   * @param {string} acpAgent.id - ACP agent ID
   * @param {string[]} acpAgent.capabilities - Agent capabilities
   * @param {Object} acpAgent.metadata - Optional metadata
   * @returns {Object} - Registration result with internal ID
   */
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

  /**
   * Translate A2A heartbeat to ACP heartbeat format
   * @param {string} agentId - Internal agent ID
   * @param {string} status - Agent status
   * @param {number} load - Current load (0-1)
   * @param {number} activeTasks - Number of active tasks
   * @returns {Object} - ACP heartbeat message
   */
  toACPHeartbeat(agentId, status, load, activeTasks) {
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

  /**
   * Get internal ID from ACP ID
   * @param {string} acpId - ACP agent ID
   * @returns {string} - Internal agent ID
   */
  getInternalId(acpId) {
    return this.idMap.get(acpId) || acpId;
  }
}

export default new ACPAgentAdapter();
