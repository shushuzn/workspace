/**
 * CapabilityRegistry - Inverted index for capability-based agent discovery
 *
 * Maintains:
 * - capabilityIndex: Map<capability, Set<agentId>> — fast lookup by capability
 * - subscriptions: Map<capability, Set<agentId>> — pub/sub subscribers
 */

export class CapabilityRegistry {
  constructor(router) {
    this.router = router;
    this.capabilityIndex = new Map(); // capability -> Set<agentId>
    this.subscriptions = new Map();    // capability -> Set<agentId>
  }

  /**
   * Register agent capabilities in the index
   */
  register(agentId, capabilities) {
    for (const cap of capabilities) {
      if (!this.capabilityIndex.has(cap)) {
        this.capabilityIndex.set(cap, new Set());
      }
      this.capabilityIndex.get(cap).add(agentId);
    }
    // Emit capability:added events
    for (const cap of capabilities) {
      this.router.emit('capability:added', { agentId, capabilities: [cap] });
      this.notifySubscribers(cap, { type: 'capability:added', agentId, capabilities: [cap] });
    }
  }

  /**
   * Unregister agent — removes from index AND subscriptions
   */
  unregister(agentId) {
    // Remove from capabilityIndex
    for (const [, agents] of this.capabilityIndex) {
      agents.delete(agentId);
    }
    // Clean up subscriptions for this agent
    for (const [, subscribers] of this.subscriptions) {
      subscribers.delete(agentId);
    }
    // Emit capability:removed for all capabilities this agent had
    // We don't track what capabilities an agent had, so emit a general event
    this.router.emit('capability:removed', { agentId });
  }

  /**
   * Update agent capabilities (diff and emit events)
   */
  updateCapabilities(agentId, newCapabilities) {
    const agent = this.router.agents.get(agentId);
    if (!agent) return;

    const oldCapabilities = Array.from(agent.capabilities);
    const added = newCapabilities.filter(c => !oldCapabilities.includes(c));
    const removed = oldCapabilities.filter(c => !newCapabilities.includes(c));

    // Update agent's capabilities set
    agent.capabilities = new Set(newCapabilities);

    // Remove from old capabilities index
    for (const cap of removed) {
      const agents = this.capabilityIndex.get(cap);
      if (agents) agents.delete(agentId);
    }

    // Add to new capabilities index
    for (const cap of added) {
      if (!this.capabilityIndex.has(cap)) {
        this.capabilityIndex.set(cap, new Set());
      }
      this.capabilityIndex.get(cap).add(agentId);
    }

    // Emit events
    if (added.length > 0) {
      this.router.emit('capability:updated', { agentId, oldCapabilities, newCapabilities: added });
      for (const cap of added) {
        this.notifySubscribers(cap, { type: 'capability:updated', agentId, capabilities: [cap] });
      }
    }
  }

  /**
   * Match agents by capability query with weighted scoring
   * Score = matchScore + recencyBonus - (load × 10)
   *
   * @param {string} query - Capability to search for
   * @param {object} options - { loadThreshold=0.9, limit=5 }
   * @returns {Array} Sorted matches [{agentId, score, capabilities, status, load}]
   */
  match(query, options = {}) {
    const { loadThreshold = 0.9, limit = 5 } = options;
    const scored = [];

    for (const [capability, agentIds] of this.capabilityIndex) {
      for (const agentId of agentIds) {
        const agent = this.router.agents.get(agentId);
        if (!agent) continue;
        if (agent.load > loadThreshold) continue; // hard filter

        let matchScore = 0;
        if (capability === query) matchScore = 10;
        else if (capability.startsWith(query)) matchScore = 5;
        else if (capability.includes(query)) matchScore = 3;
        else continue;

        // recencyBonus: +1 if heartbeat within 30s, else 0
        const now = Date.now();
        const lastSeen = agent.lastHeartbeat || agent.registeredAt || 0;
        const recencyBonus = (now - lastSeen) < 30000 ? 1 : 0;

        const score = matchScore + recencyBonus - (agent.load * 10);

        scored.push({
          agentId,
          score,
          capabilities: Array.from(agent.capabilities),
          status: agent.status,
          load: agent.load,
          lastHeartbeat: agent.lastHeartbeat
        });
      }
    }

    return scored.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      if (a.load !== b.load) return a.load - b.load;        // lower load wins
      return (b.lastHeartbeat || 0) - (a.lastHeartbeat || 0); // more recent wins
    }).slice(0, limit);
  }

  /**
   * Subscribe to capability changes
   */
  subscribe(agentId, capabilities) {
    for (const cap of capabilities) {
      if (!this.subscriptions.has(cap)) {
        this.subscriptions.set(cap, new Set());
      }
      this.subscriptions.get(cap).add(agentId);
    }
  }

  /**
   * Unsubscribe from capability changes
   */
  unsubscribe(agentId, capabilities) {
    for (const cap of capabilities) {
      const subscribers = this.subscriptions.get(cap);
      if (subscribers) {
        subscribers.delete(agentId);
      }
    }
  }

  /**
   * Notify subscribers of a capability event
   */
  notifySubscribers(capability, event) {
    const subscribers = this.subscriptions.get(capability);
    if (!subscribers) return;

    for (const subscriberId of subscribers) {
      const agent = this.router.agents.get(subscriberId);
      // Skip offline/dead subscribers silently
      if (!agent || agent.status === 'offline') continue;

      const msg = {
        id: crypto.randomUUID(),
        type: 'EVENT',
        priority: 'NORMAL',
        from: 'router',
        to: subscriberId,
        timestamp: Date.now(),
        payload: { event: { capability, ...event } }
      };
      this.router.emit('message:deliver', msg, agent);
    }
  }
}
