import { ResultAggregator } from '../../src/protocols/task-decomposition/result-aggregator.js';

describe('ResultAggregator', () => {
  let aggregator;

  beforeEach(() => {
    aggregator = new ResultAggregator();
  });

  test('aggregate() collects outputs from successful results', () => {
    const results = [
      { subtaskId: 'sub-1', success: true, payload: { output: 'API done' } },
      { subtaskId: 'sub-2', success: true, payload: { output: 'Review done' } }
    ];
    const aggregated = aggregator.aggregate(results, { taskId: 'task-1', strategy: 'parallel' });
    expect(aggregated.outputs).toEqual(['API done', 'Review done']);
    expect(aggregated.success).toBe(true);
  });

  test('aggregate() filters out failed results', () => {
    const results = [
      { subtaskId: 'sub-1', success: true, payload: { output: 'done' } },
      { subtaskId: 'sub-2', success: false, payload: { error: 'failed' } }
    ];
    const aggregated = aggregator.aggregate(results, { taskId: 'task-1', strategy: 'parallel' });
    expect(aggregated.outputs).toEqual(['done']);
    expect(aggregated.success).toBe(false);
  });

  test('aggregate() collects artifacts from all successful results', () => {
    const results = [
      { subtaskId: 'sub-1', success: true, payload: { artifacts: [{ type: 'file', path: 'a.js' }] } },
      { subtaskId: 'sub-2', success: true, payload: { artifacts: [{ type: 'file', path: 'b.js' }] } }
    ];
    const aggregated = aggregator.aggregate(results, { taskId: 'task-1', strategy: 'parallel' });
    expect(aggregated.artifacts).toHaveLength(2);
  });

  test('aggregate() computes correct stats', () => {
    const results = [
      { subtaskId: 'sub-1', success: true, payload: {} },
      { subtaskId: 'sub-2', success: false, payload: {} },
      { subtaskId: 'sub-3', success: true, payload: {} }
    ];
    const aggregated = aggregator.aggregate(results, { taskId: 'task-1', strategy: 'parallel' });
    expect(aggregated.stats.total).toBe(3);
    expect(aggregated.stats.succeeded).toBe(2);
    expect(aggregated.stats.failed).toBe(1);
  });

  test('generateSummary() formats output correctly', () => {
    expect(aggregator.generateSummary(['one'])).toBe('one');
    expect(aggregator.generateSummary(['a', 'b'])).toBe('Completed 2 subtasks: a, b');
    expect(aggregator.generateSummary([])).toBe('No results');
  });
});
