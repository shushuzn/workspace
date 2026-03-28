# Task Decomposition & Aggregation Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add task decomposition and aggregation — when a main agent submits a complex task, the router decomposes it into subtasks, routes them to capable agents in parallel, and aggregates results.

**Architecture:** Add `TaskDecomposer` and `ResultAggregator` components. New `TASK_DECOMPOSE` message type triggers decomposition. Subtasks use existing `capabilityRoute()` for load-aware routing. Results collected via event subscription and aggregated on completion.

**Tech Stack:** Node.js (no deps), Jest ES modules, existing codebase patterns

---

## Overview

```
┌─────────────┐  TASK_DECOMPOSE   ┌──────────────────┐
│ Main Agent   │ ────────────────▶│ TaskDecomposer   │
└─────────────┘                  └────────┬───────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        ▼                ▼                ▼
                 ┌─────────┐     ┌─────────┐     ┌─────────┐
                 │ SubTask1│     │ SubTask2│     │ SubTask3│
                 │ (code)  │     │ (review)│     │ (test)  │
                 └────┬────┘     └────┬────┘     └────┬────┘
                      │                │                │
                      └────────────────┴────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        ▼                                 ▼
                 ┌──────────────────┐              ┌──────────────────┐
                 │ResultAggregator  │              │  capabilityRoute │
                 │                  │              │  (existing)      │
                 └────────┬─────────┘              └──────────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ TASK_AGGREGATED  │
                 │   → Main Agent   │
                 └──────────────────┘
```

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
├── router.js                         # MODIFY: add decomposeTask(), aggregateResults()
└── server.js                        # MODIFY: add a2a_decompose_task tool
test/
├── unit/
│   ├── task-decomposer.test.js    # NEW
│   └── result-aggregator.test.js  # NEW
└── integration/
    └── task-decomposition.test.js # NEW
```

---

## Message Protocol

### New Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `TASK_DECOMPOSE` | Main → Router | Contains task description, strategy, required capabilities |
| `SUB_TASK` | Router → Agent | Individual subtask with parent tracking |
| `SUB_RESULT` | Agent → Router | Subtask completion result |
| `TASK_AGGREGATED` | Router → Main | Final aggregated result |

### Message Schemas

```javascript
// TASK_DECOMPOSE
{
  type: 'TASK_DECOMPOSE',
  id: 'msg-xxx',
  from: 'main-agent',
  to: 'router',
  timestamp: Date.now(),
  payload: {
    taskId: 'task-xxx',           // unique task ID
    description: '构建用户登录系统',
    strategy: 'parallel',         // parallel | sequential
    capabilities: ['coding', 'review', 'test'],
    maxSubTasks: 5,
    metadata: {}
  }
}

// SUB_TASK
{
  type: 'SUB_TASK',
  id: 'sub-xxx',
  from: 'router',
  to: 'capability:coding',
  parentTaskId: 'task-xxx',
  payload: {
    description: '实现用户注册API',
    requirements: ['POST /api/register', 'validation', 'hash password'],
    priority: 'NORMAL'
  }
}

// SUB_RESULT
{
  type: 'SUB_RESULT',
  id: 'result-xxx',
  from: 'agent-xxx',
  to: 'router',
  parentTaskId: 'task-xxx',
  subtaskId: 'sub-xxx',
  success: true,
  payload: {
    output: 'API实现完成',
    artifacts: [{ type: 'file', path: 'src/auth/register.js' }]
  }
}

// TASK_AGGREGATED
{
  type: 'TASK_AGGREGATED',
  id: 'agg-xxx',
  from: 'router',
  to: 'main-agent',
  parentTaskId: 'task-xxx',
  success: true,
  payload: {
    outputs: ['API实现完成', '代码审查通过', '测试通过'],
    artifacts: [...],
    summary: '用户登录系统构建完成'
  }
}
```

---

## API Design

### New Router Methods

```javascript
// In A2ARouter class

/**
 * Decompose a task into subtasks and route them
 */
decomposeTask(message) {
  const { taskId, description, strategy, capabilities, maxSubTasks } = message.payload;

  // 1. Decompose task
  const subtasks = this.taskDecomposer.decompose(description, {
    strategy,
    capabilities,
    maxSubTasks
  });

  // 2. Track parent task
  this.subtaskManager.createParentTask(taskId, subtasks.length);

  // 3. Route each subtask
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

/**
 * Handle subtask result
 */
handleSubResult(message) {
  const { parentTaskId, subtaskId, success, payload } = message;

  this.subtaskManager.recordSubtaskResult(parentTaskId, subtaskId, success, payload);

  // Check if all subtasks complete
  if (this.subtaskManager.isTaskComplete(parentTaskId)) {
    return this.aggregateResults(parentTaskId);
  }

  return { success: true, aggregated: false };
}

/**
 * Aggregate all subtask results
 */
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

### New MCP Tool

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

---

## Component Details

### TaskDecomposer

```javascript
export class TaskDecomposer {
  decompose(taskDescription, options) {
    const { strategy, capabilities, maxSubTasks } = options;

    // Simple keyword-based decomposition
    const subtasks = [];

    // Parse task for action keywords
    const actions = this.extractActions(taskDescription);

    // Group actions by capability
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
    // Simple split by common delimiters
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
    return 'coding'; // default
  }
}
```

### ResultAggregator

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

### SubtaskManager

```javascript
export class SubtaskManager {
  constructor() {
    this.parentTasks = new Map();  // taskId -> ParentTask
    this.subtaskResults = new Map(); // taskId -> Map<subtaskId, Result>
  }

  createParentTask(taskId, expectedCount) {
    this.parentTasks.set(taskId, {
      taskId,
      expectedCount,
      completedCount: 0,
      status: 'in_progress',
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

---

## Event Flow

```
1. Main Agent
   └─▶ sends TASK_DECOMPOSE message

2. Router.decomposeTask()
   ├─▶ TaskDecomposer.decompose() → subtasks[]
   ├─▶ SubtaskManager.createParentTask()
   └─▶ capabilityRoute() for each subtask

3. Subtask Agents (parallel)
   └─▶ execute and send SUB_RESULT

4. Router.handleSubResult()
   ├─▶ SubtaskManager.recordSubtaskResult()
   └─▶ check isTaskComplete()
       ├─▶ false: wait for more results
       └─▶ true: aggregateResults()

5. Router.aggregateResults()
   └─▶ ResultAggregator.aggregate() → TASK_AGGREGATED

6. Main Agent
   └─▶ receives TASK_AGGREGATED with final result
```

---

## Error Handling

| Scenario | Handling |
|----------|----------|
| No agents available for capability | Enqueue subtask, wait for agent registration |
| Subtask timeout (no result) | Mark as failed after `subtaskTimeout`, continue aggregation |
| All subtasks fail | Return `TASK_AGGREGATED` with `success: false` |
| Parent task canceled | Cancel pending subtasks, cleanup |

---

## Testing Strategy

### Unit Tests

1. **TaskDecomposer**
   - decomposes task into correct number of subtasks
   - infers correct capability from action keywords
   - respects maxSubTasks limit

2. **ResultAggregator**
   - aggregates successful results
   - collects artifacts from all subtasks
   - handles partial failure

3. **SubtaskManager**
   - tracks completion status correctly
   - detects task completion at threshold

### Integration Tests

1. Full flow: TASK_DECOMPOSE → SUB_TASKs → SUB_RESULTs → TASK_AGGREGATED
2. Parallel execution: verify concurrent subtask routing
3. Failure recovery: agent goes offline mid-task
