# executor.js 关键修复记录 (2026-03-28)

## decision.js → executor.js 接口契约

**decision.js 的 `buildPriorityQueue()` 返回的是对象，不是数组：**
```javascript
{
  P0: [],   // 数组
  P1: [],   // 数组
  P2: [],   // 数组
  P3: [],   // 数组
  _meta: { orderedIds: [] }
}
```

## 修复的 4 个 Bug

| # | 问题 | 位置 | 修复 |
|---|------|------|------|
| 1 | `priorityQueue.filter()` 对对象调用会 TypeError | `execute()` lines 168-171 | 改用 `priorityQueue.P0 \|\| []` |
| 2 | P2/P3 任务被静默丢弃 | `execute()` | 新增 `scheduleBacklog(p2, p3)` 方法 |
| 3 | `trackState()` 中同样用了 `.filter()` | lines 125-126 | 改用 `(priorityQueue.P1 \|\| []).length` |
| 4 | `executionState.completedTasks` 未定义 | line 144 | 改为 `scheduledTasks` |

## 文件路径
`C:\Users\adm\.claude\skills\auto-research\src\executor.js`
