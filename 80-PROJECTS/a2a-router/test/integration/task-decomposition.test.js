import { A2ARouter } from '../../src/router.js';
import { v4 as uuidv4 } from 'uuid';

describe('Task Decomposition Integration', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    router.registerAgent('coder', ['coding'], {});
    router.registerAgent('reviewer', ['review'], {});
  });

  afterEach(() => {
    router.close();
  });

  test('full flow: TASK_DECOMPOSE → SUB_TASKs → SUB_RESULTs → TASK_AGGREGATED', () => {
    const taskId = uuidv4();
    const decomposeMsg = {
      id: uuidv4(),
      type: 'TASK_DECOMPOSE',
      from: 'main-agent',
      to: 'router',
      timestamp: Date.now(),
      payload: {
        taskId,
        description: '实现登录功能. 审查代码',
        strategy: 'parallel',
        capabilities: ['coding', 'review'],
        maxSubTasks: 5
      }
    };

    const result = router.routeMessage(decomposeMsg);
    expect(result.success).toBe(true);
    expect(result.subtaskCount).toBe(2);

    // Simulate receiving SUB_RESULT messages
    const subResult1 = {
      type: 'SUB_RESULT',
      from: 'agent-1',
      to: 'router',
      parentTaskId: taskId,
      subtaskId: 'sub-1',
      success: true,
      payload: { output: 'Login implemented' }
    };

    const subResult2 = {
      type: 'SUB_RESULT',
      from: 'agent-2',
      to: 'router',
      parentTaskId: taskId,
      subtaskId: 'sub-2',
      success: true,
      payload: { output: 'Code reviewed' }
    };

    // Handle first result
    const aggResult1 = router.handleSubResult(subResult1);
    expect(aggResult1.aggregated).toBe(false);

    // Handle second result - should trigger aggregation
    const aggResult2 = router.handleSubResult(subResult2);
    expect(aggResult2.aggregated).toBe(true);
    expect(aggResult2.payload.outputs).toContain('Login implemented');
    expect(aggResult2.payload.outputs).toContain('Code reviewed');
    expect(aggResult2.payload.success).toBe(true);
  });
});
