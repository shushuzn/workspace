import { SubtaskManager } from '../../src/protocols/task-decomposition/subtask-manager.js';

describe('SubtaskManager', () => {
  let manager;

  beforeEach(() => {
    manager = new SubtaskManager();
  });

  test('createParentTask() initializes parent task tracking', () => {
    manager.createParentTask('task-1', 3, 'parallel');
    const parent = manager.getParentTask('task-1');
    expect(parent.taskId).toBe('task-1');
    expect(parent.expectedCount).toBe(3);
    expect(parent.completedCount).toBe(0);
    expect(parent.status).toBe('in_progress');
    expect(parent.strategy).toBe('parallel');
  });

  test('recordSubtaskResult() increments completedCount', () => {
    manager.createParentTask('task-1', 3, 'parallel');
    manager.recordSubtaskResult('task-1', 'sub-1', true, { output: 'done' });
    expect(manager.getParentTask('task-1').completedCount).toBe(1);
  });

  test('isTaskComplete() returns true when completedCount >= expectedCount', () => {
    manager.createParentTask('task-1', 2, 'parallel');
    manager.recordSubtaskResult('task-1', 'sub-1', true, {});
    expect(manager.isTaskComplete('task-1')).toBe(false);
    manager.recordSubtaskResult('task-1', 'sub-2', true, {});
    expect(manager.isTaskComplete('task-1')).toBe(true);
  });

  test('getSubtaskResults() returns all recorded results', () => {
    manager.createParentTask('task-1', 2, 'parallel');
    manager.recordSubtaskResult('task-1', 'sub-1', true, { output: 'first' });
    manager.recordSubtaskResult('task-1', 'sub-2', false, { error: 'failed' });
    const results = manager.getSubtaskResults('task-1');
    expect(results).toHaveLength(2);
  });

  test('completeTask() marks parent as completed', () => {
    manager.createParentTask('task-1', 1, 'parallel');
    manager.recordSubtaskResult('task-1', 'sub-1', true, {});
    manager.completeTask('task-1');
    expect(manager.getParentTask('task-1').status).toBe('completed');
    expect(manager.getParentTask('task-1').completedAt).toBeDefined();
  });

  test('getProgress() returns correct progress structure', () => {
    manager.createParentTask('task-1', 4, 'parallel');
    manager.recordSubtaskResult('task-1', 'sub-1', true, {});
    manager.recordSubtaskResult('task-1', 'sub-2', false, { error: 'fail' });
    const progress = manager.getProgress('task-1');
    expect(progress.percent).toBe(50); // 2 of 4
    expect(progress.completedCount).toBe(1);
    expect(progress.failedCount).toBe(1);
    expect(progress.expectedCount).toBe(4);
  });

  test('startSubtask() increments runningCount', () => {
    manager.createParentTask('task-1', 3, 'parallel');
    manager.startSubtask('task-1', 'sub-1', { agentId: 'agent-a' });
    const progress = manager.getProgress('task-1');
    expect(progress.runningCount).toBe(1);
  });

  test('failedCount tracked separately from completedCount', () => {
    manager.createParentTask('task-1', 3, 'parallel');
    manager.recordSubtaskResult('task-1', 'sub-1', true, {});
    manager.recordSubtaskResult('task-1', 'sub-2', false, { error: 'failed' });
    const progress = manager.getProgress('task-1');
    expect(progress.completedCount).toBe(1);
    expect(progress.failedCount).toBe(1);
    expect(progress.percent).toBe(67); // 2 of 3
  });

  test('onProgress() callback is called on result', () => {
    manager.createParentTask('task-1', 2, 'parallel');
    const calls = [];
    manager.onProgress('task-1', (p) => calls.push(p));
    manager.recordSubtaskResult('task-1', 'sub-1', true, {});
    expect(calls).toHaveLength(1);
    expect(calls[0].completedCount).toBe(1);
  });
});
