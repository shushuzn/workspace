export class LoadBalancer {
  constructor(router) {
    this.router = router;
  }

  getAgentLoads(capability = null) {
    const agents = [];

    for (const [agentId, agent] of this.router.agents) {
      if (capability && !Array.from(agent.capabilities).some(c => c.toLowerCase().includes(capability.toLowerCase()))) continue;

      const queueStats = this.getQueueStatsForAgent(agentId);
      const score = this.calculateScore(agent, queueStats);

      agents.push({
        id: agentId,
        capabilities: Array.from(agent.capabilities),
        status: agent.status,
        load: agent.load,
        queueSize: queueStats.size,
        avgWaitTime: queueStats.avgWaitTime,
        score
      });
    }

    return agents.sort((a, b) => b.score - a.score);
  }

  calculateScore(agent, queueStats) {
    const queueScore = Math.max(0, 100 - queueStats.size);
    const statusScore = agent.status === 'idle' ? 100 : 50;
    const loadScore = (1 - agent.load) * 100;

    return queueScore * 0.3 + statusScore * 0.2 + loadScore * 0.5;
  }

  getQueueStatsForAgent(agentId) {
    const stats = this.router.queueMonitor.getQueueStats();
    const totalSize = Object.values(stats.queues).reduce((sum, q) => sum + q.size, 0);
    const totalWait = Object.values(stats.queues).reduce((sum, q) => sum + (q.avgWaitTime * q.size), 0);
    return {
      size: totalSize,
      avgWaitTime: totalSize > 0 ? Math.round(totalWait / totalSize) : 0
    };
  }
}