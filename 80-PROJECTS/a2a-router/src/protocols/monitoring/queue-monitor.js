/**
 * QueueMonitor - Monitors router queue stats and alerts on threshold violations
 */

export class QueueMonitor {
  constructor(router, options = {}) {
    this.router = router;
    this.thresholds = options.thresholds || {
      CRITICAL: 10,
      HIGH: 50,
      NORMAL: 100,
      LOW: 200
    };
  }

  getQueueStats() {
    const queues = {};
    const alerts = [];

    for (const [priority, queue] of this.router.queues) {
      const size = queue.length;
      let avgWaitTime = 0;
      let maxWaitTime = 0;

      if (size > 0) {
        const now = Date.now();
        const waitTimes = queue.map(msg => now - (msg.enqueuedAt || now));
        avgWaitTime = Math.round(waitTimes.reduce((a, b) => a + b, 0) / size);
        maxWaitTime = waitTimes.reduce((max, t) => t > max ? t : max, 0);
      }

      queues[priority] = { size, avgWaitTime, maxWaitTime };

      // Check threshold
      const threshold = this.thresholds[priority];
      if (size > threshold) {
        alerts.push({
          level: priority,
          queue: priority,
          message: `Queue ${priority} backlog ${size} exceeds threshold ${threshold}`,
          triggeredAt: Date.now()
        });
      }
    }

    return { queues, alerts };
  }

  checkThresholds() {
    return this.getQueueStats().alerts;
  }
}
