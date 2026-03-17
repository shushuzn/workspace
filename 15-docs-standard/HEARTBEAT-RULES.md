# Heartbeat 执行规则

**最后更新：** 2026-03-08  
**版本：** 2.0 (单步执行)

---

## 核心原则

**Heartbeat 是单步执行器，不是批处理器。**

```
❌ 错误理解：触发 → 能做多少做多少 → 做完才停
✅ 正确理解：触发 → 做一个动作 → 停止 → 等下次触发
```

---

## 每次 Heartbeat 只做一件事

| 情况 | 动作 | 输出 |
|------|------|------|
| currentArticle.status = "analyzing" | 分析当前文章 | **直接输出完整分析** + `STATUS: RUNNING`（可选） |
| queue.Count > 0 | 处理队列第一篇 | **直接输出完整分析** + `STATUS: RUNNING`（可选） |
| completed 有未整理结果 | 整理分析结果 | **直接输出整理结果** |
| discovered.Count > 0 | 搜索新文章 | **直接执行搜索** + 输出结果 |
| 以上都不满足 | 无动作 | `NO_ACTION` / `WAITING_FOR_USER: <reason>` |

**禁止：**
- ❌ 只输出 `CONTINUE: ...` 而不执行
- ❌ 一次 heartbeat 分析多篇论文
- ❌ 扩展研究范围或创建新主题

---

## 执行流程

```
1. 获取锁 (heartbeat-check.ps1 -AcquireLock)
   ↓
2. 读 heartbeat-state.json
   ↓
3. 判断下一步 (analyzing → queued → discovered → none)
   ↓
4. 执行一个动作
   ↓
5. 更新状态文件
   ↓
6. 释放锁 (heartbeat-check.ps1 -ReleaseLock)
   ↓
7. 输出结果，然后停止
```

---

## 输出规则

**只允许输出以下 8 种结果之一：**

1. `CONTINUE: analyze current article` — 继续分析当前文章（附完整分析）
2. `CONTINUE: analyze next queued article` — 处理队列下一篇
3. `CONTINUE: search for new articles` — 搜索新文章
4. `CONTINUE: consolidate completed analysis` — 整理已完成分析
5. `WAITING_FOR_USER: <reason>` — 需要用户输入
6. `WAITING_FOR_RESULT: <reason>` — 等待外部结果
7. `NO_ACTION` — 无动作
8. `DONE` — 全部完成

**禁止：**
- ❌ 添加 [Mode]/[North Star] 等额外格式
- ❌ 询问用户确认
- ❌ 提供多个选项
- ❌ 解释规则
- ❌ 输出状态表格

---

## 锁机制

`heartbeat-state.json` 中的 `heartbeatLock` 字段：

```json
{
  "heartbeatLock": {
    "acquired": false,
    "acquiredAt": null,
    "releasedAt": null,
    "actionTaken": null
  }
}
```

**用途：**
- 防止同一次 heartbeat 触发多次执行
- 追踪上次执行的动作
- 确保"单步执行"纪律

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 一次分析多篇 | 当成批处理 | 记住：一次只做一件事 |
| 输出追加 `CONTINUE: next` | 习惯性继续 | 停止是规则的一部分 |
| 询问用户"继续吗？" | 等确认 | 自主决定下一步，但不决定做多少步 |
| 不更新状态文件 | 忘记 | 行动后立即更新 |

---

## 为什么这样设计？

1. **可控** — 用户可以在任何 heartbeat 间隔中断
2. **可审查** — 每步都有明确的状态记录
3. **可恢复** — 失败后从断点继续
4. **节能** — 不过度消耗 token/时间
5. **纪律** — 培养"单步执行"的条件反射

---

## 检查清单

每次 heartbeat 前自问：

- [ ] 我是否只准备做一个动作？
- [ ] 我是否会在输出后停止？
- [ ] 我是否没有准备追加 `CONTINUE: next`？
- [ ] 我是否会在行动后更新状态文件？
- [ ] 我是否理解了"单步执行"的含义？

如果任一答案是"否"，先停下来重新阅读本文档。

---

*违反这些规则会导致 heartbeat 失去意义，退化为批处理。*
