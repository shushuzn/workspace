export class SubtaskManager {
  constructor() {
    this.parentTasks = new Map();    // taskId -> ParentTask
    this.subtaskResults = new Map(); // taskId -> Map<subtaskId, Result>
    this.subtaskStatus = new Map(); // taskId -> Map<subtaskId, SubtaskStatus>
    this.progressCallbacks = new Map(); // taskId -> [callback]
  }

  /**
   * Progress tracking event types
   */
  static SubtaskStatus = {
    PENDING: 'pending',
    RUNNING: 'running',
    COMPLETED: 'completed',
    FAILED: 'failed',
    CANCELLED: 'cancelled'
  };

  createParentTask(taskId, expectedCount, strategy = 'parallel') {
    this.parentTasks.set(taskId, {
      taskId,
      expectedCount,
      completedCount: 0,
      failedCount: 0,
      runningCount: 0,
      status: 'in_progress',
      strategy,
      createdAt: new Date(),
      completedAt: null,
      estimatedDurationMs: null
    });
    this.subtaskResults.set(taskId, new Map());
    this.subtaskStatus.set(taskId, new Map());
  }

  /**
   * Register a progress callback for real-time updates
   * @param {string} taskId - Parent task ID
   * @param {Function} callback - (progress) => void
   */
  onProgress(taskId, callback) {
    if (!this.progressCallbacks.has(taskId)) {
      this.progressCallbacks.set(taskId, []);
    }
    this.progressCallbacks.get(taskId).push(callback);
  }

  /**
   * Emit progress update to all registered callbacks
   */
  emitProgress(taskId) {
    const callbacks = this.progressCallbacks.get(taskId);
    if (!callbacks) return;
    const progress = this.getProgress(taskId);
    callbacks.forEach(cb => {
      try { cb(progress); } catch (e) { /* ignore callback errors */ }
    });
  }

  /**
   * Get detailed progress for a parent task
   * @returns {Object} { percent, completedCount, failedCount, runningCount, expectedCount, eta, elapsed }
   */
  getProgress(taskId) {
    const parent = this.parentTasks.get(taskId);
    if (!parent) return null;

    const elapsed = Date.now() - new Date(parent.createdAt).getTime();
    const percent = parent.expectedCount > 0
      ? Math.round(((parent.completedCount + parent.failedCount) / parent.expectedCount) * 100)
      : 0;

    // Estimate ETA based on completed subtasks timing
    let eta = null;
    if (parent.completedCount > 0 && parent.completedCount < parent.expectedCount) {
      const avgTimePerTask = elapsed / (parent.completedCount + parent.failedCount);
      const remaining = parent.expectedCount - parent.completedCount - parent.failedCount;
      eta = Math.round(avgTimePerTask * remaining);
    }

    return {
      taskId,
      percent,
      completedCount: parent.completedCount,
      failedCount: parent.failedCount,
      runningCount: parent.runningCount,
      expectedCount: parent.expectedCount,
      status: parent.status,
      eta,
      elapsed,
      strategy: parent.strategy
    };
  }

  /**
   * Update subtask status to running (started execution)
   */
  startSubtask(taskId, subtaskId, metadata = {}) {
    const parent = this.parentTasks.get(taskId);
    if (!parent) return;

    const statusMap = this.subtaskStatus.get(taskId);
    if (!statusMap) return;

    const existing = statusMap.get(subtaskId);
    if (existing && existing.status === SubtaskManager.SubtaskStatus.RUNNING) return; // already running

    statusMap.set(subtaskId, {
      subtaskId,
      status: SubtaskManager.SubtaskStatus.RUNNING,
      startedAt: new Date(),
      metadata
    });
    parent.runningCount++;
    this.emitProgress(taskId);
  }

  recordSubtaskResult(taskId, subtaskId, success, payload) {
    const parent = this.parentTasks.get(taskId);
    if (!parent) return;

    // Update status tracking
    const statusMap = this.subtaskStatus.get(taskId);
    if (statusMap) {
      const current = statusMap.get(subtaskId);
      if (current) {
        if (current.status === SubtaskManager.SubtaskStatus.RUNNING) {
          parent.runningCount--;
        }
      }
      statusMap.set(subtaskId, {
        ...current,
        status: success ? SubtaskManager.SubtaskStatus.COMPLETED : SubtaskManager.SubtaskStatus.FAILED,
        completedAt: new Date(),
        payload
      });
    }

    if (success) {
      parent.completedCount++;
    } else {
      parent.failedCount++;
    }

    const results = this.subtaskResults.get(taskId);
    if (results) {
      results.set(subtaskId, { subtaskId, success, payload });
    }

    // Check if overall task is complete
    if (this.isTaskComplete(taskId)) {
      this.completeTask(taskId);
    }

    this.emitProgress(taskId);
  }

  isTaskComplete(taskId) {
    const parent = this.parentTasks.get(taskId);
    if (!parent) return false;
    return parent.completedCount >= parent.expectedCount;
  }

  getParentTask(taskId) {
    return this.parentTasks.get(taskId);
  }

  getSubtaskResults(taskId) {
    const results = this.subtaskResults.get(taskId);
    if (!results) return [];
    return Array.from(results.values());
  }

  completeTask(taskId) {
    const parent = this.parentTasks.get(taskId);
    if (!parent) return;
    parent.status = 'completed';
    parent.completedAt = new Date();
  }

  cancelParentTask(taskId) {
    const parent = this.parentTasks.get(taskId);
    if (parent) {
      parent.status = 'canceled';
      parent.canceledAt = new Date();
    }
    // Clean up tracking data
    this.subtaskResults.delete(taskId);
  }
}
