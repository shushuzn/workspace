export class SubtaskManager {
  constructor() {
    this.parentTasks = new Map();    // taskId -> ParentTask
    this.subtaskResults = new Map(); // taskId -> Map<subtaskId, Result>
  }

  createParentTask(taskId, expectedCount, strategy = 'parallel') {
    this.parentTasks.set(taskId, {
      taskId,
      expectedCount,
      completedCount: 0,
      status: 'in_progress',
      strategy,
      createdAt: new Date(),
      completedAt: null
    });
    this.subtaskResults.set(taskId, new Map());
  }

  recordSubtaskResult(taskId, subtaskId, success, payload) {
    const parent = this.parentTasks.get(taskId);
    if (!parent) return;

    parent.completedCount++;

    const results = this.subtaskResults.get(taskId);
    if (results) {
      results.set(subtaskId, { subtaskId, success, payload });
    }
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
}
