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
import { TaskDecomposer } from './protocols/task-decomposition/task-decomposer.js';
import { ResultAggregator } from './protocols/task-decomposition/result-aggregator.js';
import { SubtaskManager } from './protocols/task-decomposition/subtask-manager.js';
import { SecurityManager } from './protocols/security/security-manager.js';
import { AccessControl } from './protocols/security/access-control.js';
import { OrchestrationEngine } from './protocols/orchestration/orchestration-engine.js';
import { LangChainAdapter } from './protocols/orchestration/langchain-adapter.js';
import { StockAnalysisAdapter } from './protocols/mcp/stock-analysis-adapter.js';

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

    // Security database
    this.securityDb = options.securityDb; // SQLite DB for security tables
    
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

    // Initialize task decomposition components
    this.taskDecomposer = new TaskDecomposer();
    this.resultAggregator = new ResultAggregator();
    this.subtaskManager = new SubtaskManager();

    // Initialize security manager
    this.securityManager = new SecurityManager({
      db: options.securityDb,
      securityConfig: options.security || {}
    });

    // Initialize access control
    this.accessControl = new AccessControl(this.securityManager, {
      defaultAclPolicy: options.security?.defaultAclPolicy || 'allow'
    });

    // Initialize orchestration engine
    this.orchestrationEngine = new OrchestrationEngine(this);

    // Initialize LangChain adapter
    this.langchainAdapter = new LangChainAdapter();

    // Initialize Stock Analysis adapter (lazy-start on first use)
    this.stockAnalysisAdapter = null;

    // Task decomposition configuration
    this.subtaskTimeout = options.subtaskTimeout || 300000; // 5 minutes default
    this.subtaskTimeouts = new Map(); // taskId -> timeoutId
    this.subtaskStartTimes = new Map(); // subtaskId -> startTime

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
  async routeMessage(message) {
    // Validate message
    const validation = this.validateMessage(message);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    // Security check
    const securityResult = this.securityManager.verifyMessage(message);
    if (!securityResult.valid) {
      return { success: false, error: securityResult.error };
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
      return await this.handleRouterMessage(message);
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
  async handleRouterMessage(message) {
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

      case 'TASK_DECOMPOSE':
        return this.decomposeTask(message);

      case 'SUB_RESULT':
        return this.handleSubResult(message);

      case 'TASK_CANCEL':
        return this.cancelTask(message);

      case 'WORKFLOW_CREATE':
        return this.orchestrationEngine.createWorkflow(
          message.payload.workflowId,
          message.payload.definition
        );

      case 'WORKFLOW_START':
        return this.orchestrationEngine.startWorkflow(
          message.payload.workflowId,
          message.payload.context
        );

      case 'WORKFLOW_PAUSE':
        return this.orchestrationEngine.pauseWorkflow(message.payload.workflowId);

      case 'WORKFLOW_RESUME':
        return this.orchestrationEngine.resumeWorkflow(message.payload.workflowId);

      case 'WORKFLOW_CANCEL':
        return this.orchestrationEngine.cancelWorkflow(message.payload.workflowId);

      case 'WORKFLOW_STATUS':
        return { success: true, status: this.orchestrationEngine.getWorkflowStatus(message.payload.workflowId) };

      case 'WORKFLOW_LIST':
        return { success: true, workflows: this.orchestrationEngine.listWorkflows(message.payload?.filter) };

      case 'LANGCHAIN_CREATE':
        return this.langchainAdapter.createAgent(
          message.payload.agentId,
          message.payload.config
        );

      case 'LANGCHAIN_INVOKE':
        return this.langchainAdapter.invoke(
          message.payload.agentId,
          message.payload.input
        );

      case 'LANGCHAIN_STATUS':
        return this.langchainAdapter.status(message.payload.runId);

      case 'LANGCHAIN_LIST':
        return { success: true, agents: this.langchainAdapter.listAgents() };

      case 'STOCK_ANALYSIS': {
        // Lazy-start the stock analysis adapter on first use
        if (!this.stockAnalysisAdapter) {
          this.stockAnalysisAdapter = new StockAnalysisAdapter();
          try {
            await this.stockAnalysisAdapter.start();
          } catch (err) {
            return { success: false, error: 'STOCK_ADAPTER_START_FAILED', details: err.message };
          }
        }
        const { tool, input } = message.payload;
        try {
          const result = await this.stockAnalysisAdapter.call(tool, input);
          return { success: true, result };
        } catch (err) {
          return { success: false, error: 'STOCK_TOOL_CALL_FAILED', details: err.message };
        }
      }

      case 'STOCK_ANALYSIS_LIST':
        return {
          success: true,
          tools: this.stockAnalysisAdapter
            ? this.stockAnalysisAdapter.getTools()
            : []
        };

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
   * Decompose a task into subtasks
   */
  async decomposeTask(message) {
    const { taskId, description, strategy, capabilities, maxSubTasks } = message.payload;

    // ── Self-evolving orchestrator 联动 ─────────────────────────────
    if (strategy === 'self-evolve') {
      try {
        const res = await fetch('http://localhost:8080/api/v1/orchestrate/evolve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task: description }),
          signal: AbortSignal.timeout(15000),
        });
        if (res.ok) {
          const result = await res.json();
          // result.subtasks 或 result.steps 是 orchestrator 返回的子任务
          const steps = result.subtasks ?? result.steps ?? [];
          if (steps.length > 0) {
            this.subtaskManager.createParentTask(taskId, steps.length, strategy);
            steps.forEach(step => {
              this.capabilityRoute({
                id: uuidv4(),
                from: 'router',
                to: `capability:${step.capability ?? 'coding'}`,
                timestamp: Date.now(),
                parentTaskId: taskId,
                type: 'SUB_TASK',
                capability: step.capability ?? 'coding',
                description: step.description ?? step.text ?? step,
              });
            });
            console.log(`[Router] self-evolve: ${steps.length} subtasks from orchestrator`);
            return { success: true, taskId, subtaskCount: steps.length, via: 'orchestrator' };
          }
        }
      } catch (err) {
        console.warn(`[Router] orchestrator unreachable (${err.message}), falling back to simple decomposer`);
      }
    }
    // ─────────────────────────────────────────────────────────────

    const subtasks = this.taskDecomposer.decompose(description, {
      strategy,
      capabilities,
      maxSubTasks
    });

    this.subtaskManager.createParentTask(taskId, subtasks.length, strategy);

    subtasks.map(subtask => {
      const routed = this.capabilityRoute({
        ...subtask,
        id: uuidv4(),
        from: 'router',
        to: `capability:${subtask.capability}`,
        timestamp: Date.now(),
        parentTaskId: taskId,
        type: 'SUB_TASK'
      });
      return routed;
    });

    return { success: true, taskId, subtaskCount: subtasks.length, via: 'simple' };
  }

  /**
   * Handle sub-task result
   */
  handleSubResult(message) {
    const { parentTaskId, subtaskId, success, payload } = message;

    // Check if this subtask already timed out
    const existingResults = this.subtaskManager.getSubtaskResults(parentTaskId);
    const existing = existingResults.find(r => r.subtaskId === subtaskId);
    if (existing && existing.timedOut) {
      // Result arrived after timeout, skip
      return { success: true, aggregated: false, reason: 'SUBTASK_ALREADY_TIMED_OUT' };
    }

    this.subtaskManager.recordSubtaskResult(parentTaskId, subtaskId, success, payload);

    if (this.subtaskManager.isTaskComplete(parentTaskId)) {
      return this.aggregateResults(parentTaskId);
    }

    return { success: true, aggregated: false };
  }

  /**
   * Aggregate results from subtasks
   */
  aggregateResults(taskId) {
    const parentTask = this.subtaskManager.getParentTask(taskId);
    const subtaskResults = this.subtaskManager.getSubtaskResults(taskId);

    const aggregated = this.resultAggregator.aggregate(subtaskResults, {
      taskId,
      strategy: parentTask.strategy
    });

    this.subtaskManager.completeTask(taskId);

    return {
      success: true,
      aggregated: true,
      payload: aggregated
    };
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

    const validTypes = ['TASK', 'TASK_ACK', 'TASK_RESULT', 'QUERY', 'RESPONSE', 'EVENT', 'HEARTBEAT', 'REGISTER', 'UNREGISTER', 'DISCOVER', 'TASK_DECOMPOSE', 'SUB_TASK', 'SUB_RESULT', 'TASK_AGGREGATED', 'TASK_CANCEL', 'WORKFLOW_CREATE', 'WORKFLOW_START', 'WORKFLOW_PAUSE', 'WORKFLOW_RESUME', 'WORKFLOW_CANCEL', 'WORKFLOW_STATUS', 'WORKFLOW_LIST'];
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

    // Check subtask timeouts every 30 seconds
    this.maintenanceIntervals.push(setInterval(() => this.checkSubtaskTimeouts(), 30000));
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
   * Check subtask timeouts and mark timed out subtasks
   */
  checkSubtaskTimeouts() {
    const now = Date.now();
    for (const [taskId, parentTask] of this.subtaskManager.parentTasks) {
      if (parentTask.status !== 'in_progress') continue;

      const results = this.subtaskManager.subtaskResults.get(taskId);
      if (!results) continue;

      for (const [subtaskId, result] of results) {
        if (result.timedOut || result.success !== undefined) continue;
        // Check if this subtask has been waiting longer than subtaskTimeout
        const startTime = this.subtaskStartTimes.get(subtaskId);
        if (startTime && (now - startTime) > this.subtaskTimeout) {
          results.set(subtaskId, { ...result, timedOut: true, success: false, payload: { error: 'Subtask timeout' } });
          parentTask.completedCount++;
          console.log(`[Router] Subtask ${subtaskId} timed out after ${this.subtaskTimeout}ms`);
        }
      }

      // Check if all subtasks are now complete (including timed out ones)
      if (this.subtaskManager.isTaskComplete(taskId)) {
        this.aggregateResults(taskId);
      }
    }
  }

  /**
   * Cancel a parent task and clean up tracking data
   */
  cancelParentTask(taskId) {
    const parent = this.parentTasks.get(taskId);
    if (parent) {
      parent.status = 'canceled';
      parent.canceledAt = Date.now();
    }
    // Clean up tracking data
    this.subtaskResults.delete(taskId);
    // Note: Individual subtasks already sent cannot be recalled;
    // agents will handle cancellation on next heartbeat
  }

  /**
   * Handle task cancellation request
   */
  cancelTask(message) {
    const { taskId } = message.payload;
    this.subtaskManager.cancelParentTask(taskId);
    return { success: true, canceled: true };
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

  createApiKey(agentId, expiresIn) {
    return this.securityManager.createApiKey(agentId, expiresIn);
  }

  revokeApiKey(keyId) {
    return this.securityManager.revokeApiKey(keyId);
  }

  listApiKeys(agentId) {
    return this.securityManager.listApiKeys(agentId);
  }

  rotateApiKey(agentId, keyId) {
    return this.securityManager.rotateApiKey(agentId, keyId);
  }

  setAclRule(capability, allowedAgents, deniedAgents) {
    this.accessControl.setRule(capability, allowedAgents, deniedAgents);
    return { success: true };
  }

  checkPermission(fromAgent, toTarget) {
    return this.accessControl.checkPermission(fromAgent, toTarget);
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
