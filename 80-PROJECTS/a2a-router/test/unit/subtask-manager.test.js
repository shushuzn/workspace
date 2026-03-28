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
});
