const QUEUE_WEIGHT = 0.3;
const STATUS_WEIGHT = 0.2;
const LOAD_WEIGHT = 0.5;
const MAX_QUEUE_SIZE = 100;
const IDLE_STATUS_SCORE = 100;
const BUSY_STATUS_SCORE = 50;

export class LoadBalancer {
  constructor(router) {
    if (!router) throw new Error('router is required');
    if (!router.agents) throw new Error('router.agents is required');
    if (!router.queueMonitor) throw new Error('router.queueMonitor is required');
    this.router = router;
  }

  getAgentLoads(capability = null) {
    const agents = [];

    for (const [agentId, agent] of this.router.agents) {
      if (!agent || !agent.capabilities) continue;

      const capabilities = Array.isArray(agent.capabilities)
        ? agent.capabilities
        : Array.from(agent.capabilities);

      if (capability && !capabilities.some(c => c.toLowerCase().includes(capability.toLowerCase()))) continue;

      const queueStats = this.getQueueStatsForAgent(agentId);
      const score = this.calculateScore(agent, queueStats);

      agents.push({
        id: agentId,
        capabilities,
        status: agent.status || 'unknown',
        load: typeof agent.load === 'number' ? agent.load : 0,
        queueSize: queueStats.size,
        avgWaitTime: queueStats.avgWaitTime,
        score
      });
    }

    return agents.sort((a, b) => b.score - a.score);
  }

  calculateScore(agent, queueStats) {
    const queueScore = Math.max(0, MAX_QUEUE_SIZE - queueStats.size);
    const statusScore = agent.status === 'idle' ? IDLE_STATUS_SCORE : BUSY_STATUS_SCORE;
    const load = typeof agent.load === 'number' ? agent.load : 0;
    const loadScore = (1 - load) * MAX_QUEUE_SIZE;

    return queueScore * QUEUE_WEIGHT + statusScore * STATUS_WEIGHT + loadScore * LOAD_WEIGHT;
  }

  getQueueStatsForAgent(agentId) {
    const stats = this.router.queueMonitor.getQueueStats();
    if (!stats || !stats.queues) {
      return { size: 0, avgWaitTime: 0 };
    }
    const totalSize = Object.values(stats.queues).reduce((sum, q) => sum + q.size, 0);
    const totalWait = Object.values(stats.queues).reduce((sum, q) => sum + (q.avgWaitTime * q.size), 0);
    return {
      size: totalSize,
      avgWaitTime: totalSize > 0 ? Math.round(totalWait / totalSize) : 0
    };
  }
}