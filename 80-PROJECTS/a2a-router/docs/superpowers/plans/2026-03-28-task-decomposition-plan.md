# Task Decomposition & Aggregation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add task decomposition and aggregation — when a main agent submits a complex task, the router decomposes it into subtasks, routes them to capable agents in parallel, and aggregates results.

**Architecture:** Three new components (TaskDecomposer, ResultAggregator, SubtaskManager) in `src/protocols/task-decomposition/`. Router gets `decomposeTask()`, `handleSubResult()`, `aggregateResults()` methods. New message types (TASK_DECOMPOSE, SUB_TASK, SUB_RESULT, TASK_AGGREGATED) extend the protocol. Subtasks use existing `capabilityRoute()` for load-aware routing.

**Tech Stack:** Node.js (no deps), Jest ES modules, existing codebase patterns

---

## File Structure

```
src/
├── protocols/
│   ├── task-decomposition/           # NEW
│   │   ├── task-decomposer.js      # decompose() method
│   │   ├── result-aggregator.js   # aggregate() method
│   │   └── subtask-manager.js     # track subtask lifecycle
│   └── capability-registry.js     # EXISTING
├── router.js                         # MODIFY: add new methods, update validateMessage
└── server.js                        # MODIFY: add a2a_decompose_task tool
test/
├── unit/
│   ├── task-decomposer.test.js    # NEW
│   ├── result-aggregator.test.js  # NEW
│   └── subtask-manager.test.js    # NEW
└── integration/
    └── task-decomposition.test.js # NEW
```

---

## Task 1: SubtaskManager

**Files:**
- Create: `src/protocols/task-decomposition/subtask-manager.js`
- Test: `test/unit/subtask-manager.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- test/unit/subtask-manager.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```javascript
export class SubtaskManager {
  constructor() {
    this.parentTasks = new Map();
    this.subtaskResults = new Map();
  }

  createParentTask(taskId, expectedCount, strategy = 'parallel') {
    this.parentTasks.set(taskId, {
      taskId,
      expectedCount,
      completedCount: 0,
      status: 'in_progress',
      strategy,
      createdAt: Date.now()
    });
    this.subtaskResults.set(taskId, new Map());
  }

  recordSubtaskResult(taskId, subtaskId, success, payload) {
    const results = this.subtaskResults.get(taskId);
    results.set(subtaskId, { subtaskId, success, payload });
    this.parentTasks.get(taskId).completedCount++;
  }

  isTaskComplete(taskId) {
    const parent = this.parentTasks.get(taskId);
    return parent.completedCount >= parent.expectedCount;
  }

  getParentTask(taskId) {
    return this.parentTasks.get(taskId);
  }

  getSubtaskResults(taskId) {
    return Array.from(this.subtaskResults.get(taskId).values());
  }

  completeTask(taskId) {
    const parent = this.parentTasks.get(taskId);
    parent.status = 'completed';
    parent.completedAt = Date.now();
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- test/unit/subtask-manager.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/task-decomposition/subtask-manager.js test/unit/subtask-manager.test.js
git commit -m "feat: add SubtaskManager for tracking parent task lifecycle

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 2: TaskDecomposer

**Files:**
- Create: `src/protocols/task-decomposition/task-decomposer.js`
- Test: `test/unit/task-decomposer.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
import { TaskDecomposer } from '../../src/protocols/task-decomposition/task-decomposer.js';

describe('TaskDecomposer', () => {
  let decomposer;

  beforeEach(() => {
    decomposer = new TaskDecomposer();
  });

  test('decompose() splits by common delimiters', () => {
    const subtasks = decomposer.decompose('实现登录. 实现注册, 测试功能', {
      strategy: 'parallel',
      capabilities: ['coding', 'test'],
      maxSubTasks: 5
    });
    expect(subtasks.length).toBe(3);
  });

  test('decompose() respects maxSubTasks limit', () => {
    const subtasks = decomposer.decompose('a,b,c,d,e,f,g', {
      strategy: 'parallel',
      capabilities: ['coding'],
      maxSubTasks: 3
    });
    expect(subtasks.length).toBe(3);
  });

  test('inferCapability() detects coding keywords', () => {
    expect(decomposer.inferCapability('实现登录功能')).toBe('coding');
    expect(decomposer.inferCapability('build user API')).toBe('coding');
    expect(decomposer.inferCapability('create file')).toBe('coding');
  });

  test('inferCapability() detects review keywords', () => {
    expect(decomposer.inferCapability('审查代码')).toBe('review');
    expect(decomposer.inferCapability('check security')).toBe('review');
  });

  test('inferCapability() detects test keywords', () => {
    expect(decomposer.inferCapability('测试功能')).toBe('test');
    expect(decomposer.inferCapability('run tests')).toBe('test');
  });

  test('inferCapability() defaults to coding', () => {
    expect(decomposer.inferCapability('do something')).toBe('coding');
  });

  test('extractActions() handles mixed delimiters', () => {
    const actions = decomposer.extractActions('实现登录;实现注册\n测试功能');
    expect(actions).toHaveLength(3);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- test/unit/task-decomposer.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```javascript
export class TaskDecomposer {
  decompose(taskDescription, options) {
    const { strategy, capabilities, maxSubTasks } = options;
    const subtasks = [];
    const actions = this.extractActions(taskDescription);

    for (const action of actions) {
      const capability = this.inferCapability(action);
      subtasks.push({
        capability,
        description: action,
        priority: 'NORMAL'
      });
    }

    return subtasks.slice(0, maxSubTasks);
  }

  extractActions(description) {
    return description
      .split(/[,，.。;；\n]/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }

  inferCapability(action) {
    const coding = ['实现', '构建', '开发', '编写', 'create', 'implement', 'build'];
    const review = ['审查', '检查', 'review', 'check'];
    const test = ['测试', 'test'];

    const lower = action.toLowerCase();
    if (coding.some(k => lower.includes(k))) return 'coding';
    if (review.some(k => lower.includes(k))) return 'review';
    if (test.some(k => lower.includes(k))) return 'test';
    return 'coding';
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- test/unit/task-decomposer.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/task-decomposition/task-decomposer.js test/unit/task-decomposer.test.js
git commit -m "feat: add TaskDecomposer for splitting tasks into subtasks

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 3: ResultAggregator

**Files:**
- Create: `src/protocols/task-decomposition/result-aggregator.js`
- Test: `test/unit/result-aggregator.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- test/unit/result-aggregator.test.js`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```javascript
export class ResultAggregator {
  aggregate(subtaskResults, options) {
    const { taskId, strategy } = options;

    const outputs = subtaskResults
      .filter(r => r.success)
      .map(r => r.payload.output);

    const artifacts = subtaskResults
      .filter(r => r.success && r.payload.artifacts)
      .flatMap(r => r.payload.artifacts);

    const failedCount = subtaskResults.filter(r => !r.success).length;

    return {
      taskId,
      outputs,
      artifacts,
      summary: this.generateSummary(outputs),
      success: failedCount === 0,
      stats: {
        total: subtaskResults.length,
        succeeded: outputs.length,
        failed: failedCount
      }
    };
  }

  generateSummary(outputs) {
    if (outputs.length === 0) return 'No results';
    if (outputs.length === 1) return outputs[0];
    return `Completed ${outputs.length} subtasks: ${outputs.join(', ')}`;
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- test/unit/result-aggregator.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/task-decomposition/result-aggregator.js test/unit/result-aggregator.test.js
git commit -m "feat: add ResultAggregator for combining subtask results

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 4: Router Integration

**Files:**
- Modify: `src/router.js` (add imports, constructor init, new methods, update validateMessage)

- [ ] **Step 1: Add imports and initialize components in constructor**

```javascript
import { TaskDecomposer } from './protocols/task-decomposition/task-decomposer.js';
import { ResultAggregator } from './protocols/task-decomposition/result-aggregator.js';
import { SubtaskManager } from './protocols/task-decomposition/subtask-manager.js';
```

Add in constructor after `this.queueMonitor` initialization:

```javascript
// Initialize task decomposition components
this.taskDecomposer = new TaskDecomposer();
this.resultAggregator = new ResultAggregator();
this.subtaskManager = new SubtaskManager();
```

- [ ] **Step 2: Add new message types to validateMessage()**

In `validateMessage()`, add to validTypes array:

```javascript
const validTypes = ['TASK', 'TASK_ACK', 'TASK_RESULT', 'QUERY', 'RESPONSE', 'EVENT', 'HEARTBEAT', 'REGISTER', 'UNREGISTER', 'DISCOVER', 'TASK_DECOMPOSE', 'SUB_TASK', 'SUB_RESULT', 'TASK_AGGREGATED'];
```

- [ ] **Step 3: Add decomposeTask() method**

```javascript
decomposeTask(message) {
  const { taskId, description, strategy, capabilities, maxSubTasks } = message.payload;

  const subtasks = this.taskDecomposer.decompose(description, {
    strategy,
    capabilities,
    maxSubTasks
  });

  this.subtaskManager.createParentTask(taskId, subtasks.length, strategy);

  const results = subtasks.map(subtask => {
    const routed = this.capabilityRoute({
      ...subtask,
      parentTaskId: taskId,
      type: 'SUB_TASK'
    });
    return routed;
  });

  return { success: true, taskId, subtaskCount: subtasks.length };
}
```

- [ ] **Step 4: Add handleSubResult() method**

```javascript
handleSubResult(message) {
  const { parentTaskId, subtaskId, success, payload } = message;

  this.subtaskManager.recordSubtaskResult(parentTaskId, subtaskId, success, payload);

  if (this.subtaskManager.isTaskComplete(parentTaskId)) {
    return this.aggregateResults(parentTaskId);
  }

  return { success: true, aggregated: false };
}
```

- [ ] **Step 5: Add aggregateResults() method**

```javascript
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
```

- [ ] **Step 6: Handle TASK_DECOMPOSE in handleRouterMessage()**

In `handleRouterMessage()` switch, add:

```javascript
case 'TASK_DECOMPOSE':
  return this.decomposeTask(message);
```

- [ ] **Step 7: Handle SUB_RESULT in handleRouterMessage()**

In `handleRouterMessage()` switch, add:

```javascript
case 'SUB_RESULT':
  return this.handleSubResult(message);
```

Also remove the SUB_RESULT pre-check from `routeMessage()` if it was added in error.

- [ ] **Step 8: Run tests to verify nothing is broken**

Run: `npm test`
Expected: All tests pass

- [ ] **Step 9: Commit**

```bash
git add src/router.js
git commit -m "feat: integrate TaskDecomposer, ResultAggregator, SubtaskManager into router

Adds decomposeTask(), handleSubResult(), aggregateResults() methods.
Adds new message types to validation.
Handles TASK_DECOMPOSE and SUB_RESULT message routing.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 5: Integration Test

**Files:**
- Create: `test/integration/task-decomposition.test.js`

- [ ] **Step 1: Write integration test**

```javascript
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
```

- [ ] **Step 2: Run test to verify it passes**

Run: `npm test -- test/integration/task-decomposition.test.js`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add test/integration/task-decomposition.test.js
git commit -m "test: add integration test for task decomposition flow

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 6: MCP Tool (Optional - server.js)

**Files:**
- Modify: `src/server.js` (add a2a_decompose_task tool)

Note: This task depends on server.js existing with MCP tool structure. If server.js doesn't have MCP tools yet, skip this task.

- [ ] **Step 1: Add MCP tool definition**

Add to server's tool definitions:

```javascript
{
  name: 'a2a_decompose_task',
  description: 'Decompose a complex task into subtasks for parallel execution',
  inputSchema: {
    type: 'object',
    properties: {
      task: {
        type: 'string',
        description: 'Task description'
      },
      strategy: {
        type: 'string',
        enum: ['parallel', 'sequential'],
        default: 'parallel'
      },
      capabilities: {
        type: 'array',
        items: { type: 'string' },
        description: 'Required capabilities for subtasks'
      },
      maxSubTasks: {
        type: 'number',
        default: 5
      }
    },
    required: ['task', 'capabilities']
  }
}
```

- [ ] **Step 2: Commit (if server.js exists)**

```bash
git add src/server.js
git commit -m "feat: add a2a_decompose_task MCP tool

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 7: Timeout Handling (Error Handling)

**Files:**
- Modify: `src/router.js` (add subtaskTimeout config and timeout checker)

- [ ] **Step 1: Add subtaskTimeout to constructor**

In the router constructor, add:

```javascript
// Task decomposition configuration
this.subtaskTimeout = options.subtaskTimeout || 300000; // 5 minutes default
this.subtaskTimeouts = new Map(); // taskId -> timeoutId
this.subtaskStartTimes = new Map(); // subtaskId -> startTime
```

- [ ] **Step 2: Add timeout checker in startMaintenance()**

Add to the maintenance interval setup:

```javascript
// Check subtask timeouts every 30 seconds
this.maintenanceIntervals.push(setInterval(() => this.checkSubtaskTimeouts(), 30000));
```

- [ ] **Step 3: Add checkSubtaskTimeouts() method**

```javascript
checkSubtaskTimeouts() {
  const now = Date.now();
  for (const [taskId, parentTask] of this.parentTasks) {
    if (parentTask.status !== 'in_progress') continue;

    const results = this.subtaskResults.get(taskId);
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
    if (this.isTaskComplete(taskId)) {
      this.aggregateResults(taskId);
    }
  }
}
```

- [ ] **Step 4: Modify recordSubtaskResult to detect timeouts**

Update `recordSubtaskResult` in SubtaskManager to accept a timestamp:

```javascript
recordSubtaskResult(taskId, subtaskId, success, payload, receivedAt = Date.now()) {
  const results = this.subtaskResults.get(taskId);
  results.set(subtaskId, { subtaskId, success, payload, receivedAt });
  this.parentTasks.get(taskId).completedCount++;
}
```

- [ ] **Step 5: Add timeout flag to failed subtasks**

In `handleSubResult()`, if a result comes in after timeout, mark it appropriately:

```javascript
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
```

- [ ] **Step 6: Add TASK_CANCEL message type to validTypes**

In `validateMessage()`, add `'TASK_CANCEL'` to validTypes.

- [ ] **Step 7: Add cancelParentTask() for parent task canceled scenario**

Add to SubtaskManager:

```javascript
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
```

In A2ARouter, add handler:

```javascript
cancelTask(message) {
  const { taskId } = message.payload;
  this.subtaskManager.cancelParentTask(taskId);
  return { success: true, canceled: true };
}
```

And add to handleRouterMessage switch:

```javascript
case 'TASK_CANCEL':
  return this.cancelTask(message);
```

- [ ] **Step 8: Commit**

```bash
git add src/router.js
git commit -m "feat: add subtask timeout handling for task decomposition

Adds subtaskTimeout configuration (default 5 minutes).
Adds checkSubtaskTimeouts() to detect and handle hung subtasks.
Adds cancelParentTask() for graceful task cancellation.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Summary

| Task | Files | Status |
|------|-------|--------|
| 1 | SubtaskManager | ⬜ |
| 2 | TaskDecomposer | ⬜ |
| 3 | ResultAggregator | ⬜ |
| 4 | Router Integration | ⬜ |
| 5 | Integration Test | ⬜ |
| 6 | MCP Tool (optional) | ⬜ |
| 7 | Timeout Handling | ⬜ |
