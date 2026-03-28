/**
 * A2A Router Core
 * 
 * Message routing, agent registry, and queue management
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { CapabilityRegistry } from './protocols/capability-registry.js';
import { MessageStore } from './protocols/persistence/message-store.js';
import { QueueMonitor } from './protocols/monitoring/queue-monitor.js';

export class A2ARouter extends EventEmitter {
  constructor(options = {}) {
    super();
    this.agents = new Map();        // agentId -> AgentInfo
    this.queues = new Map();        // priority -> Queue
    this.messages = new Map();      // messageId -> Message
    this.stats = {
      messagesRouted: 0,
      messagesDropped: 0,
      agentsRegistered: 0
    };
    
    // Configuration
    this.heartbeatTimeout = options.heartbeatTimeout || 60000; // 60s
    this.maxQueueSize = options.maxQueueSize || 1000;
    this.defaultTTL = options.defaultTTL || 3600; // 1 hour
    
    // Initialize priority queues
    this.queues.set('CRITICAL', []);
    this.queues.set('HIGH', []);
    this.queues.set('NORMAL', []);
    this.queues.set('LOW', []);

    // Initialize capability registry
    this.capabilityRegistry = new CapabilityRegistry(this);

    // Initialize message store for persistence
    this.messageStore = new MessageStore(options.dbPath || ':memory:');

    // Initialize queue monitor for backlog monitoring
    this.queueMonitor = new QueueMonitor(this, {
      thresholds: options.queueThresholds || undefined
    });

    // Track maintenance interval IDs for cleanup
    this.maintenanceIntervals = [];

    // Start maintenance loop
    this.startMaintenance();
  }

  /**
   * Register an agent
   */
  registerAgent(agentId, capabilities = [], metadata = {}) {
    if (this.agents.has(agentId)) {
      return { success: false, error: 'Agent already registered' };
    }

    const agent = {
      id: agentId,
      capabilities: new Set(capabilities),
      metadata,
      status: 'idle',
      load: 0,
      lastHeartbeat: Date.now(),
      registeredAt: Date.now()
    };

    this.agents.set(agentId, agent);
    this.stats.agentsRegistered++;
    this.capabilityRegistry.register(agentId, capabilities);

    this.emit('agent:registered', agent);
    console.log(`[Router] Agent registered: ${agentId} (${capabilities.join(', ')})`);
    
    return { success: true, agent };
  }

  /**
   * Unregister an agent
   */
  unregisterAgent(agentId) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return { success: false, error: 'Agent not found' };
    }

    this.agents.delete(agentId);
    this.capabilityRegistry.unregister(agentId);
    this.emit('agent:unregistered', agent);
    console.log(`[Router] Agent unregistered: ${agentId}`);
    
    return { success: true };
  }

  /**
   * Update agent heartbeat
   */
  heartbeat(agentId, status = 'healthy', load = 0, activeTasks = 0) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return { success: false, error: 'Agent not found' };
    }

    agent.lastHeartbeat = Date.now();
    agent.status = load > 0.8 ? 'busy' : 'idle';
    agent.load = load;
    agent.activeTasks = activeTasks;

    return { success: true, agent };
  }

  /**
   * Route a message
   */
  routeMessage(message) {
    // Validate message
    const validation = this.validateMessage(message);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    // Persist message to store
    if (this.messageStore) {
      const persistResult = this.messageStore.save(message);
      if (!persistResult.success) {
        console.error('[Router] Failed to persist message:', persistResult.error);
      }
    }

    // Store message in memory
    message._receivedAt = Date.now();
    this.messages.set(message.id, message);

    // Determine routing strategy
    if (message.to === 'broadcast') {
      return this.broadcast(message);
    } else if (message.to === 'router') {
      return this.handleRouterMessage(message);
    } else if (message.to.startsWith('capability:')) {
      return this.capabilityRoute(message);
    } else {
      return this.directRoute(message);
    }
  }

  /**
   * Direct routing to specific agent
   */
  directRoute(message) {
    const targetAgent = this.agents.get(message.to);
    
    if (!targetAgent) {
      this.stats.messagesDropped++;
      return {
        success: false,
        error: 'AGENT_NOT_FOUND',
        errorMessage: `Target agent '${message.to}' not found`
      };
    }

    if (targetAgent.status === 'offline') {
      // Queue for later delivery
      this.enqueue(message);
      return {
        success: true,
        queued: true,
        message: `Agent '${message.to}' is offline, message queued`
      };
    }

    // Deliver message
    this.deliver(message, targetAgent);
    
    return {
      success: true,
      delivered: true,
      agent: targetAgent.id
    };
  }

  /**
   * Route message by capability requirement
   */
  capabilityRoute(message) {
    const capability = message.to.replace('capability:', '');

    // Find best agent by capability using existing match()
    const matches = this.capabilityRegistry.match(capability, {
      loadThreshold: 1.0,
      limit: 10
    });

    if (matches.length === 0) {
      this.enqueue(message);
      return { success: true, queued: true, reason: 'NO_AGENTS_FOR_CAPABILITY' };
    }

    // Select agent with best score (matches are already sorted)
    const best = matches[0];
    const agent = this.agents.get(best.agentId);

    if (!agent || agent.status === 'offline') {
      this.enqueue(message);
      return { success: true, queued: true, reason: 'AGENT_OFFLINE' };
    }

    // Deliver message
    this.deliver(message, agent);

    return {
      success: true,
      delivered: true,
      agent: best.agentId
    };
  }

  /**
   * Broadcast to all agents
   */
  broadcast(message) {
    const delivered = [];
    const failed = [];

    for (const [agentId, agent] of this.agents) {
      // Don't send to sender
      if (agentId === message.from) continue;

      const result = this.deliver({ ...message, _broadcast: true }, agent);
      if (result.success) {
        delivered.push(agentId);
      } else {
        failed.push({ agentId, error: result.error });
      }
    }

    this.stats.messagesRouted += delivered.length;

    return {
      success: true,
      broadcast: true,
      delivered: delivered.length,
      deliveredTo: delivered,
      failed: failed.length,
      failedAgents: failed
    };
  }

  /**
   * Handle messages to router itself
   */
  handleRouterMessage(message) {
    switch (message.type) {
      case 'REGISTER':
        return this.registerAgent(
          message.payload.agentId,
          message.payload.capabilities,
          message.payload.metadata
        );
      
      case 'UNREGISTER':
        return this.unregisterAgent(message.from);
      
      case 'HEARTBEAT':
        return this.heartbeat(
          message.from,
          message.payload.status,
          message.payload.load,
          message.payload.activeTasks
        );
      
      case 'DISCOVER':
        return this.handleDiscovery(message);
      
      case 'QUERY':
        return this.handleQuery(message);
      
      default:
        return { success: false, error: 'UNKNOWN_ROUTER_COMMAND' };
    }
  }

  /**
   * Handle capability discovery
   */
  handleDiscovery(message) {
    const query = message.payload.query;
    const matches = [];

    for (const [agentId, agent] of this.agents) {
      // Check if agent has matching capability
      const hasCapability = Array.from(agent.capabilities).some(cap => 
        cap.toLowerCase().includes(query.toLowerCase())
      );

      if (hasCapability) {
        matches.push({
          agentId: agent.id,
          capabilities: Array.from(agent.capabilities),
          status: agent.status,
          load: agent.load
        });
      }
    }

    // Send response back to requester
    const response = {
      id: uuidv4(),
      type: 'RESPONSE',
      priority: 'NORMAL',
      from: 'router',
      to: message.from,
      timestamp: Date.now(),
      payload: { capabilities: matches },
      metadata: {
        correlationId: message.metadata?.correlationId,
        inResponseTo: message.id
      }
    };

    this.routeMessage(response);

    return { success: true, matches: matches.length };
  }

  /**
   * Handle query messages
   */
  handleQuery(message) {
    switch (message.payload.query) {
      case 'agents':
        return {
          success: true,
          agents: Array.from(this.agents.values()).map(a => ({
            id: a.id,
            capabilities: Array.from(a.capabilities),
            status: a.status,
            load: a.load
          }))
        };
      
      case 'stats':
        return {
          success: true,
          stats: this.stats
        };
      
      case 'queues':
        return {
          success: true,
          queues: {
            CRITICAL: this.queues.get('CRITICAL').length,
            HIGH: this.queues.get('HIGH').length,
            NORMAL: this.queues.get('NORMAL').length,
            LOW: this.queues.get('LOW').length
          }
        };
      
      default:
        return { success: false, error: 'UNKNOWN_QUERY' };
    }
  }

  /**
   * Deliver message to agent
   */
  deliver(message, agent) {
    // In real implementation, this would send via MCP or HTTP
    // For now, emit event for the transport layer to handle
    this.emit('message:deliver', message, agent);
    this.stats.messagesRouted++;
    
    return { success: true };
  }

  /**
   * Enqueue message for later delivery
   */
  enqueue(message) {
    const priority = message.priority || 'NORMAL';
    const queue = this.queues.get(priority);

    if (queue.length >= this.maxQueueSize) {
      console.warn(`[Router] Queue ${priority} full, dropping message ${message.id}`);
      this.stats.messagesDropped++;
      return false;
    }

    // Set enqueuedAt timestamp on message before enqueueing
    message.enqueuedAt = Date.now();

    queue.push({
      message,
      enqueuedAt: message.enqueuedAt,
      retryCount: 0
    });

    // Check thresholds after enqueue
    const alerts = this.queueMonitor.checkThresholds();
    if (alerts.length > 0) {
      this.emit('queue:threshold', alerts);
    }

    return true;
  }

  /**
   * Process queues and retry failed deliveries
   */
  processQueues() {
    const now = Date.now();

    for (const [priority, queue] of this.queues) {
      const toProcess = [];
      const toKeep = [];

      for (const item of queue) {
        const ttl = item.message.metadata?.ttl || this.defaultTTL;
        const age = (now - item.enqueuedAt) / 1000;

        // Check TTL
        if (age > ttl) {
          console.log(`[Router] Message ${item.message.id} expired, dropping`);
          this.stats.messagesDropped++;
          continue;
        }

        // Try to deliver
        const agent = this.agents.get(item.message.to);
        if (agent && agent.status !== 'offline') {
          toProcess.push(item);
        } else {
          toKeep.push(item);
        }
      }

      // Update queue
      this.queues.set(priority, toKeep);

      // Process deliverable messages
      for (const item of toProcess) {
        const agent = this.agents.get(item.message.to);
        this.deliver(item.message, agent);
      }
    }
  }

  /**
   * Validate message format
   */
  validateMessage(message) {
    if (!message) {
      return { valid: false, error: 'Message is null' };
    }

    const required = ['id', 'type', 'from', 'to', 'timestamp', 'payload'];
    for (const field of required) {
      if (!(field in message)) {
        return { valid: false, error: `Missing required field: ${field}` };
      }
    }

    const validTypes = ['TASK', 'TASK_ACK', 'TASK_RESULT', 'QUERY', 'RESPONSE', 'EVENT', 'HEARTBEAT', 'REGISTER', 'UNREGISTER', 'DISCOVER'];
    if (!validTypes.includes(message.type)) {
      return { valid: false, error: `Invalid message type: ${message.type}` };
    }

    return { valid: true };
  }

  /**
   * Start maintenance loop
   */
  startMaintenance() {
    // Process queues every 5 seconds
    this.maintenanceIntervals.push(setInterval(() => this.processQueues(), 5000));

    // Check agent health every 10 seconds
    this.maintenanceIntervals.push(setInterval(() => this.checkAgentHealth(), 10000));
  }

  /**
   * Check agent health and mark offline agents
   */
  checkAgentHealth() {
    const now = Date.now();
    const offlineThreshold = this.heartbeatTimeout;

    for (const [agentId, agent] of this.agents) {
      const lastSeen = now - agent.lastHeartbeat;
      
      if (lastSeen > offlineThreshold && agent.status !== 'offline') {
        console.log(`[Router] Agent ${agentId} marked offline (last seen ${Math.round(lastSeen / 1000)}s ago)`);
        agent.status = 'offline';
        this.emit('agent:offline', agent);
      }
    }
  }

  /**
   * Find best agents by capability with weighted scoring
   */
  matchBestAgent(query, constraints) {
    return this.capabilityRegistry.match(query, constraints);
  }

  /**
   * Subscribe to capability change notifications
   */
  subscribeCapabilities(agentId, capabilities) {
    this.capabilityRegistry.subscribe(agentId, capabilities);
    return { success: true };
  }

  /**
   * Unsubscribe from capability change notifications
   */
  unsubscribeCapabilities(agentId, capabilities) {
    this.capabilityRegistry.unsubscribe(agentId, capabilities);
    return { success: true };
  }

  /**
   * Update agent capabilities after initial registration
   */
  updateAgentCapabilities(agentId, capabilities) {
    this.capabilityRegistry.updateCapabilities(agentId, capabilities);
    return { success: true };
  }

  /**
   * Get router statistics
   */
  getStats() {
    return {
      ...this.stats,
      agentsOnline: Array.from(this.agents.values()).filter(a => a.status !== 'offline').length,
      agentsTotal: this.agents.size,
      queueSizes: {
        CRITICAL: this.queues.get('CRITICAL').length,
        HIGH: this.queues.get('HIGH').length,
        NORMAL: this.queues.get('NORMAL').length,
        LOW: this.queues.get('LOW').length
      }
    };
  }

  /**
   * Get queue statistics from queue monitor
   * @returns {Object} Queue statistics including sizes and threshold status
   */
  getQueueStats() {
    return this.queueMonitor.getQueueStats();
  }

  /**
   * Query messages for an agent
   */
  queryMessages(agentId, options = {}) {
    return this.messageStore.findByAgent(agentId, options);
  }

  /**
   * Archive messages older than timestamp
   */
  archiveMessages(olderThan) {
    return this.messageStore.archive(olderThan);
  }

  /**
   * Close router and cleanup resources
   */
  close() {
    // Clear maintenance intervals
    this.maintenanceIntervals.forEach(clearInterval);
    this.maintenanceIntervals = [];

    if (this.messageStore) {
      this.messageStore.close();
    }
  }
}

export default A2ARouter;
